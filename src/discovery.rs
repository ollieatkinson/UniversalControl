use std::{
    collections::{BTreeSet, HashMap},
    io,
    process::{Command, Stdio},
    thread,
    time::{Duration, Instant},
};

use anyhow::{Context, Result, bail};
use mdns_sd::{ResolvedService, ServiceDaemon, ServiceEvent, ServiceInfo};

const COMPANION_LINK_SERVICE: &str = "_companion-link._tcp.local.";
const DNS_SD_SERVICE: &str = "_companion-link._tcp";

#[derive(Clone, Copy, Debug)]
pub enum DiscoveryBackend {
    Auto,
    System,
    RustMdns,
}

pub fn browse_companion_link(
    seconds: u64,
    backend: DiscoveryBackend,
    include_apple_p2p: bool,
) -> Result<()> {
    let seconds = seconds.max(1);

    match backend {
        DiscoveryBackend::Auto if has_dns_sd() => browse_with_dns_sd(seconds),
        DiscoveryBackend::Auto => {
            browse_service(COMPANION_LINK_SERVICE, seconds, include_apple_p2p)
        }
        DiscoveryBackend::System => browse_with_dns_sd(seconds),
        DiscoveryBackend::RustMdns => {
            browse_service(COMPANION_LINK_SERVICE, seconds, include_apple_p2p)
        }
    }
}

pub fn browse(service: &str, seconds: u64) -> Result<()> {
    browse_service(&normalize_service(service), seconds.max(1), false)
}

pub fn advertise(
    service: &str,
    instance: &str,
    host: &str,
    addr: &str,
    port: u16,
    txt: &[String],
    seconds: u64,
) -> Result<()> {
    let service = normalize_service(service);
    let properties = parse_txt(txt)?;
    let mdns = ServiceDaemon::new().context("failed to create mDNS daemon")?;
    let service_info = ServiceInfo::new(&service, instance, host, addr, port, Some(properties))
        .with_context(|| format!("failed to build service info for {service}"))?;
    let fullname = service_info.get_fullname().to_string();

    mdns.register(service_info)
        .with_context(|| format!("failed to advertise {fullname}"))?;
    println!("advertising {fullname} at {host} {addr}:{port} for {seconds}s");
    println!(
        "Review output before sharing: hostnames, addresses, and TXT values may be stable identifiers."
    );
    thread::sleep(Duration::from_secs(seconds.max(1)));
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

fn browse_service(service: &str, seconds: u64, include_apple_p2p: bool) -> Result<()> {
    let service = normalize_service(service);
    let browse_duration = Duration::from_secs(seconds.max(1));
    let mdns = ServiceDaemon::new().context("failed to create mDNS daemon")?;

    if include_apple_p2p {
        mdns.include_apple_p2p(true)
            .context("failed to include Apple peer-to-peer interfaces")?;
    }

    let receiver = mdns
        .browse(&service)
        .with_context(|| format!("failed to browse {service}"))?;
    let started = Instant::now();
    let deadline = started + browse_duration;

    println!("Browsing {service} with Rust mDNS for {}s", seconds.max(1));
    println!(
        "Review output before sharing: hostnames, addresses, and TXT values may be stable identifiers."
    );

    while let Some(remaining) = deadline.checked_duration_since(Instant::now()) {
        match receiver.recv_timeout(remaining.min(Duration::from_millis(250))) {
            Ok(event) => print_event(started, event),
            Err(_) => {}
        }
    }

    mdns.stop_browse(&service)
        .with_context(|| format!("failed to stop browsing {service}"))?;
    mdns.shutdown().context("failed to shut down mDNS daemon")?;
    Ok(())
}

fn print_event(started: Instant, event: ServiceEvent) {
    match event {
        ServiceEvent::SearchStarted(service_type) => {
            println!(
                "[{:>6.2?}] search_started {service_type}",
                started.elapsed()
            );
        }
        ServiceEvent::ServiceFound(service_type, fullname) => {
            println!(
                "[{:>6.2?}] service_found service_type={service_type} fullname={fullname}",
                started.elapsed()
            );
        }
        ServiceEvent::ServiceResolved(info) => print_resolved(started, &info),
        ServiceEvent::ServiceRemoved(service_type, fullname) => {
            println!(
                "[{:>6.2?}] service_removed service_type={service_type} fullname={fullname}",
                started.elapsed()
            );
        }
        ServiceEvent::SearchStopped(service_type) => {
            println!(
                "[{:>6.2?}] search_stopped {service_type}",
                started.elapsed()
            );
        }
        other => {
            println!("[{:>6.2?}] event {other:?}", started.elapsed());
        }
    }
}

fn print_resolved(started: Instant, info: &ResolvedService) {
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
        .map(|property| format!("{}={}", property.key(), property.val_str()))
        .collect::<Vec<_>>()
        .join(" ");

    println!(
        "[{:>6.2?}] service_resolved fullname={} type={} host={} port={} addresses=[{}] txt=[{}]",
        started.elapsed(),
        info.get_fullname(),
        info.ty_domain,
        info.get_hostname(),
        info.get_port(),
        addresses,
        txt
    );
}

fn normalize_service(service: &str) -> String {
    let service = service.trim();
    if service.ends_with('.') {
        service.to_string()
    } else {
        format!("{service}.")
    }
}

fn parse_txt(values: &[String]) -> Result<HashMap<String, String>> {
    let mut parsed = HashMap::new();
    for value in values {
        let Some((key, val)) = value.split_once('=') else {
            bail!("TXT values must be key=value, got {value:?}");
        };
        parsed.insert(key.to_string(), val.to_string());
    }
    Ok(parsed)
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
