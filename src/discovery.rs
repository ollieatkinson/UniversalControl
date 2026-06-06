use std::{
    collections::BTreeSet,
    io,
    process::{Command, Stdio},
    thread,
    time::{Duration, Instant},
};

use anyhow::{Context, Result, bail};
use mdns_sd::{ServiceDaemon, ServiceEvent, ServiceInfo};

const COMPANION_LINK_SERVICE: &str = "_companion-link._tcp.local.";
const DNS_SD_SERVICE: &str = "_companion-link._tcp";

#[derive(Clone, Copy, Debug)]
pub enum DiscoveryBackend {
    Auto,
    System,
    RustMdns,
}

pub struct AdvertiseOptions {
    pub seconds: u64,
    pub service_type: String,
    pub instance: String,
    pub hostname: Option<String>,
    pub port: u16,
    pub txt: Vec<String>,
    pub allow_apple_service: bool,
    pub include_apple_p2p: bool,
}

pub fn browse_companion_link(
    seconds: u64,
    backend: DiscoveryBackend,
    include_apple_p2p: bool,
) -> Result<()> {
    let seconds = seconds.max(1);

    match backend {
        DiscoveryBackend::Auto if has_dns_sd() => browse_with_dns_sd(seconds),
        DiscoveryBackend::Auto => browse_with_rust_mdns(seconds, include_apple_p2p),
        DiscoveryBackend::System => browse_with_dns_sd(seconds),
        DiscoveryBackend::RustMdns => browse_with_rust_mdns(seconds, include_apple_p2p),
    }
}

pub fn advertise_mdns(options: AdvertiseOptions) -> Result<()> {
    let seconds = options.seconds.max(1);
    let service_type = normalize_service_type(&options.service_type)?;
    let hostname_source = match options.hostname.as_deref() {
        Some(hostname) => hostname.to_string(),
        None => default_hostname()?,
    };
    let hostname = normalize_hostname(&hostname_source)?;

    if is_apple_service_type(&service_type) && !options.allow_apple_service {
        bail!(
            "refusing to advertise Apple service type {service_type}; rerun with --allow-apple-service for a controlled native-compatibility experiment"
        );
    }

    let txt = parse_txt_properties(&options.txt)?;
    let mdns = ServiceDaemon::new().context("failed to create mDNS daemon")?;

    if options.include_apple_p2p {
        mdns.include_apple_p2p(true)
            .context("failed to include Apple peer-to-peer interfaces")?;
    }

    let service = ServiceInfo::new(
        &service_type,
        &options.instance,
        &hostname,
        "",
        options.port,
        txt.as_slice(),
    )
    .context("failed to create mDNS service info")?
    .enable_addr_auto();
    let fullname = service.get_fullname().to_string();

    println!(
        "Advertising {fullname} at {hostname}:{} for {seconds}s",
        options.port
    );
    println!(
        "Review output before sharing: hostnames, service names, and TXT values may be stable identifiers."
    );

    mdns.register(service)
        .context("failed to register mDNS service")?;
    thread::sleep(Duration::from_secs(seconds));

    if let Ok(unregister_events) = mdns.unregister(&fullname) {
        while unregister_events
            .recv_timeout(Duration::from_millis(250))
            .is_ok()
        {}
    }

    mdns.shutdown().context("failed to shut down mDNS daemon")?;
    Ok(())
}

fn browse_with_dns_sd(seconds: u64) -> Result<()> {
    println!("Browsing {DNS_SD_SERVICE}.local with system dns-sd for {seconds}s");
    println!(
        "Review output before sharing: hostnames and instance names may be stable identifiers."
    );

    let mut child = Command::new("dns-sd")
        .args(["-B", DNS_SD_SERVICE, "local"])
        .stdin(Stdio::null())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .spawn()
        .context("failed to start dns-sd; install Bonjour or use --backend rust-mdns")?;

    thread::sleep(Duration::from_secs(seconds));

    match child.try_wait()? {
        Some(status) if status.success() => Ok(()),
        Some(status) => bail!("dns-sd exited with status {status}"),
        None => {
            child.kill().context("failed to stop dns-sd")?;
            match child.wait() {
                Ok(_) => Ok(()),
                Err(error) if error.kind() == io::ErrorKind::InvalidInput => Ok(()),
                Err(error) => Err(error).context("failed to wait for dns-sd"),
            }
        }
    }
}

fn browse_with_rust_mdns(seconds: u64, include_apple_p2p: bool) -> Result<()> {
    let browse_duration = Duration::from_secs(seconds);
    let mdns = ServiceDaemon::new().context("failed to create mDNS daemon")?;

    if include_apple_p2p {
        mdns.include_apple_p2p(true)
            .context("failed to include Apple peer-to-peer interfaces")?;
    }

    let receiver = mdns
        .browse(COMPANION_LINK_SERVICE)
        .context("failed to browse _companion-link._tcp.local.")?;
    let started = Instant::now();
    let deadline = started + browse_duration;

    println!("Browsing {COMPANION_LINK_SERVICE} with Rust mDNS for {seconds}s");
    println!(
        "Review output before sharing: hostnames, addresses, and TXT values may be stable identifiers."
    );

    while let Some(remaining) = deadline.checked_duration_since(Instant::now()) {
        match receiver.recv_timeout(remaining.min(Duration::from_millis(250))) {
            Ok(ServiceEvent::SearchStarted(service_type)) => {
                println!(
                    "[{:>6.2?}] search_started {service_type}",
                    started.elapsed()
                );
            }
            Ok(ServiceEvent::ServiceFound(service_type, fullname)) => {
                println!(
                    "[{:>6.2?}] service_found service_type={service_type} fullname={fullname}",
                    started.elapsed()
                );
            }
            Ok(ServiceEvent::ServiceResolved(info)) => {
                let addresses = info
                    .get_addresses()
                    .iter()
                    .map(ToString::to_string)
                    .collect::<BTreeSet<_>>()
                    .into_iter()
                    .collect::<Vec<_>>()
                    .join(",");
                let txt = info
                    .get_properties()
                    .iter()
                    .map(ToString::to_string)
                    .collect::<Vec<_>>()
                    .join(" ");

                println!(
                    "[{:>6.2?}] service_resolved fullname={} host={} port={} addresses=[{}] txt=[{}]",
                    started.elapsed(),
                    info.get_fullname(),
                    info.get_hostname(),
                    info.get_port(),
                    addresses,
                    txt
                );
            }
            Ok(ServiceEvent::ServiceRemoved(service_type, fullname)) => {
                println!(
                    "[{:>6.2?}] service_removed service_type={service_type} fullname={fullname}",
                    started.elapsed()
                );
            }
            Ok(ServiceEvent::SearchStopped(service_type)) => {
                println!(
                    "[{:>6.2?}] search_stopped {service_type}",
                    started.elapsed()
                );
            }
            Ok(other) => {
                println!("[{:>6.2?}] event {other:?}", started.elapsed());
            }
            Err(_) => {}
        }
    }

    mdns.stop_browse(COMPANION_LINK_SERVICE)
        .context("failed to stop companion-link browse")?;
    mdns.shutdown().context("failed to shut down mDNS daemon")?;
    Ok(())
}

fn normalize_service_type(value: &str) -> Result<String> {
    let trimmed = value.trim();
    if trimmed.is_empty() {
        bail!("service type must not be empty");
    }

    let service_type = trim_local_suffix(trimmed);
    if !service_type.starts_with('_')
        || !(service_type.ends_with("._tcp") || service_type.ends_with("._udp"))
    {
        bail!("service type must look like _name._tcp or _name._udp");
    }

    Ok(format!("{service_type}.local."))
}

fn normalize_hostname(value: &str) -> Result<String> {
    let trimmed = value.trim();
    if trimmed.is_empty() {
        bail!("hostname must not be empty");
    }

    Ok(format!("{}.local.", trim_local_suffix(trimmed)))
}

fn default_hostname() -> Result<String> {
    if let Ok(computer_name) = std::env::var("COMPUTERNAME")
        && !computer_name.trim().is_empty()
    {
        return Ok(computer_name);
    }

    if let Ok(hostname) = std::env::var("HOSTNAME")
        && !hostname.trim().is_empty()
    {
        return Ok(hostname);
    }

    let output = Command::new("hostname")
        .stdin(Stdio::null())
        .output()
        .context("failed to run hostname; pass --hostname explicitly")?;
    if !output.status.success() {
        bail!("hostname command failed; pass --hostname explicitly");
    }

    let hostname = String::from_utf8(output.stdout)
        .context("hostname output was not UTF-8")?
        .trim()
        .to_string();
    if hostname.is_empty() {
        bail!("hostname command returned an empty value; pass --hostname explicitly");
    }
    Ok(hostname)
}

fn trim_local_suffix(value: &str) -> &str {
    let without_dot = value.trim_end_matches('.');
    without_dot.strip_suffix(".local").unwrap_or(without_dot)
}

fn is_apple_service_type(service_type: &str) -> bool {
    service_type.eq_ignore_ascii_case("_companion-link._tcp.local.")
        || service_type.eq_ignore_ascii_case("_universalcontrol._tcp.local.")
}

fn parse_txt_properties(values: &[String]) -> Result<Vec<(String, String)>> {
    let mut properties = Vec::with_capacity(values.len());

    for value in values {
        let (key, val) = value
            .split_once('=')
            .with_context(|| format!("TXT property must be key=value: {value}"))?;
        let key = key.trim();
        if key.is_empty() {
            bail!("TXT property key must not be empty");
        }
        properties.push((key.to_string(), val.to_string()));
    }

    Ok(properties)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_service_type_suffixes() {
        assert_eq!(
            normalize_service_type("_anykbflow-probe._tcp").unwrap(),
            "_anykbflow-probe._tcp.local."
        );
        assert_eq!(
            normalize_service_type("_anykbflow-probe._tcp.local").unwrap(),
            "_anykbflow-probe._tcp.local."
        );
        assert_eq!(
            normalize_service_type("_anykbflow-probe._tcp.local.").unwrap(),
            "_anykbflow-probe._tcp.local."
        );
    }

    #[test]
    fn rejects_invalid_service_type() {
        assert!(normalize_service_type("anykbflow").is_err());
        assert!(normalize_service_type("_anykbflow-probe._http").is_err());
    }

    #[test]
    fn normalizes_hostname_suffixes() {
        assert_eq!(
            normalize_hostname("anykbflow-probe").unwrap(),
            "anykbflow-probe.local."
        );
        assert_eq!(
            normalize_hostname("anykbflow-probe.local.").unwrap(),
            "anykbflow-probe.local."
        );
    }

    #[test]
    fn uses_explicit_hostname_when_provided() {
        assert_eq!(
            normalize_hostname("windows-peer.local").unwrap(),
            "windows-peer.local."
        );
    }

    #[test]
    fn parses_txt_properties() {
        let values = vec!["phase=visibility".to_string(), "role=probe".to_string()];
        let properties = parse_txt_properties(&values).unwrap();

        assert_eq!(
            properties,
            vec![
                ("phase".to_string(), "visibility".to_string()),
                ("role".to_string(), "probe".to_string()),
            ]
        );
    }
}

fn has_dns_sd() -> bool {
    Command::new("dns-sd")
        .arg("-help")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .is_ok()
}
