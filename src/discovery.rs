use std::{
    collections::{BTreeSet, HashMap},
    io,
    net::{IpAddr, SocketAddr, UdpSocket},
    process::{Command, Stdio},
    sync::atomic::{AtomicBool, Ordering},
    thread,
    time::{Duration, Instant},
};

use anyhow::{Context, Result, bail};
use mdns_sd::{ResolvedService, ServiceDaemon, ServiceEvent, ServiceInfo};

const COMPANION_LINK_SERVICE: &str = "_companion-link._tcp.local.";
const DNS_SD_SERVICE: &str = "_companion-link._tcp";
const ANYKBFLOW_SERVICE: &str = "_anykbflow._tcp.local.";
static BRIDGE_ADVERTISED: AtomicBool = AtomicBool::new(false);

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
    pub addr: Option<String>,
    pub port: u16,
    pub txt: Vec<String>,
    pub allow_apple_service: bool,
    pub include_apple_p2p: bool,
}

pub fn browse_companion_link(
    seconds: u64,
    backend: DiscoveryBackend,
    redact: bool,
    include_apple_p2p: bool,
) -> Result<()> {
    let seconds = seconds.max(1);

    match backend {
        DiscoveryBackend::Auto if has_dns_sd() && !redact => browse_with_dns_sd(seconds),
        DiscoveryBackend::Auto => {
            browse(COMPANION_LINK_SERVICE, seconds, redact, include_apple_p2p)
        }
        DiscoveryBackend::System if redact => {
            bail!(
                "--redact is only supported by the Rust mDNS backend; rerun with --backend rust-mdns"
            )
        }
        DiscoveryBackend::System => browse_with_dns_sd(seconds),
        DiscoveryBackend::RustMdns => {
            browse(COMPANION_LINK_SERVICE, seconds, redact, include_apple_p2p)
        }
    }
}

pub fn browse(service: &str, seconds: u64, redact: bool, include_apple_p2p: bool) -> Result<()> {
    let service = normalize_service_type(service)?;
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
    if redact {
        println!(
            "Redaction enabled: hostnames, addresses, instance names, and TXT values will be summarized."
        );
    } else {
        println!(
            "Review output before sharing: hostnames, addresses, and TXT values may be stable identifiers."
        );
    }

    while let Some(remaining) = deadline.checked_duration_since(Instant::now()) {
        if let Ok(event) = receiver.recv_timeout(remaining.min(Duration::from_millis(250))) {
            print_event(started, event, redact);
        }
    }

    mdns.stop_browse(&service)
        .with_context(|| format!("failed to stop browsing {service}"))?;
    mdns.shutdown().context("failed to shut down mDNS daemon")?;
    Ok(())
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
        options.addr.as_deref().unwrap_or(""),
        options.port,
        Some(txt),
    )
    .context("failed to create mDNS service info")?;
    let service = if options.addr.is_none() {
        service.enable_addr_auto()
    } else {
        service
    };
    let fullname = service.get_fullname().to_string();

    println!(
        "Advertising {fullname} at {hostname}:{} for {seconds}s",
        options.port
    );
    println!(
        "Review output before sharing: hostnames, addresses, service names, and TXT values may be stable identifiers."
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

pub fn spawn_bridge_advertisement(node_name: &str, listen_addr: SocketAddr) -> Result<()> {
    if BRIDGE_ADVERTISED.swap(true, Ordering::SeqCst) {
        return Ok(());
    }

    let instance = sanitize_instance_name(node_name);
    let host = format!("{instance}.local.");
    let port = listen_addr.port();
    let advertise_addr = advertise_ip_for(listen_addr);
    let properties = HashMap::from([
        ("role".to_string(), "input_owner".to_string()),
        ("protocol".to_string(), "json-lines-v1".to_string()),
    ]);
    let mdns = ServiceDaemon::new().context("failed to create mDNS daemon")?;
    let service_info = ServiceInfo::new(
        ANYKBFLOW_SERVICE,
        &instance,
        &host,
        advertise_addr,
        port,
        Some(properties),
    )
    .context("failed to build AnyKBFlow service info")?;
    let fullname = service_info.get_fullname().to_string();

    mdns.register(service_info)
        .with_context(|| format!("failed to advertise {fullname}"))?;
    println!("advertising {fullname} at {advertise_addr}:{port}");

    thread::spawn(move || {
        let _mdns = mdns;
        loop {
            thread::park();
        }
    });

    Ok(())
}

pub fn discover_bridge_peer(timeout: Duration) -> Result<SocketAddr> {
    let mdns = ServiceDaemon::new().context("failed to create mDNS daemon")?;
    let receiver = mdns
        .browse(ANYKBFLOW_SERVICE)
        .context("failed to browse AnyKBFlow service")?;
    let started = Instant::now();
    let deadline = started + timeout;

    println!(
        "discovering {ANYKBFLOW_SERVICE} for {}s",
        timeout.as_secs().max(1)
    );

    while let Some(remaining) = deadline.checked_duration_since(Instant::now()) {
        match receiver.recv_timeout(remaining.min(Duration::from_millis(250))) {
            Ok(ServiceEvent::ServiceResolved(info)) => {
                if let Some(addr) = socket_addr_from_resolved(&info) {
                    println!("discovered {} at {}", info.get_fullname(), addr);
                    mdns.stop_browse(ANYKBFLOW_SERVICE)
                        .context("failed to stop AnyKBFlow browse")?;
                    mdns.shutdown().context("failed to shut down mDNS daemon")?;
                    return Ok(addr);
                }
            }
            Ok(event) => print_event(started, event, false),
            Err(_) => {}
        }
    }

    mdns.stop_browse(ANYKBFLOW_SERVICE)
        .context("failed to stop AnyKBFlow browse")?;
    mdns.shutdown().context("failed to shut down mDNS daemon")?;
    bail!("no AnyKBFlow input owner discovered");
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

fn print_event(started: Instant, event: ServiceEvent, redact: bool) {
    match event {
        ServiceEvent::SearchStarted(service_type) => {
            let service_type = format_service_event_subject(&service_type, redact);
            println!(
                "[{:>6.2?}] search_started {service_type}",
                started.elapsed()
            );
        }
        ServiceEvent::ServiceFound(service_type, fullname) => {
            let service_type = format_service_event_subject(&service_type, redact);
            let fullname = format_identifier(&fullname, redact);
            println!(
                "[{:>6.2?}] service_found service_type={service_type} fullname={fullname}",
                started.elapsed()
            );
        }
        ServiceEvent::ServiceResolved(info) => print_resolved(started, &info, redact),
        ServiceEvent::ServiceRemoved(service_type, fullname) => {
            let service_type = format_service_event_subject(&service_type, redact);
            let fullname = format_identifier(&fullname, redact);
            println!(
                "[{:>6.2?}] service_removed service_type={service_type} fullname={fullname}",
                started.elapsed()
            );
        }
        ServiceEvent::SearchStopped(service_type) => {
            let service_type = format_service_event_subject(&service_type, redact);
            println!(
                "[{:>6.2?}] search_stopped {service_type}",
                started.elapsed()
            );
        }
        other => {
            if redact {
                println!(
                    "[{:>6.2?}] event kind={}",
                    started.elapsed(),
                    service_event_kind(&other)
                );
            } else {
                println!("[{:>6.2?}] event {other:?}", started.elapsed());
            }
        }
    }
}

fn print_resolved(started: Instant, info: &ResolvedService, redact: bool) {
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
        .map(|property| {
            format_txt_property(property.key(), property.val(), property.val_str(), redact)
        })
        .collect::<Vec<_>>()
        .join(" ");
    let fullname = format_identifier(info.get_fullname(), redact);
    let hostname = format_identifier(info.get_hostname(), redact);
    let addresses = if redact {
        format!("<redacted count={}>", info.get_addresses().len())
    } else {
        addresses
    };

    println!(
        "[{:>6.2?}] service_resolved fullname={} type={} host={} port={} addresses=[{}] txt=[{}]",
        started.elapsed(),
        fullname,
        info.ty_domain,
        hostname,
        info.get_port(),
        addresses,
        txt
    );
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

fn parse_txt_properties(values: &[String]) -> Result<HashMap<String, String>> {
    let mut properties = HashMap::with_capacity(values.len());

    for value in values {
        let (key, val) = value
            .split_once('=')
            .with_context(|| format!("TXT property must be key=value: {value}"))?;
        let key = key.trim();
        if key.is_empty() {
            bail!("TXT property key must not be empty");
        }
        properties.insert(key.to_string(), val.to_string());
    }

    Ok(properties)
}

fn format_identifier(value: &str, redact: bool) -> String {
    if redact {
        format!("<redacted len={}>", value.len())
    } else {
        value.to_string()
    }
}

fn format_service_event_subject(value: &str, redact: bool) -> String {
    if redact {
        value
            .split_whitespace()
            .next()
            .unwrap_or("<unknown-service>")
            .to_string()
    } else {
        value.to_string()
    }
}

fn format_txt_property(key: &str, val: Option<&[u8]>, val_str: &str, redact: bool) -> String {
    if redact {
        format!(
            "{key}=<redacted len={} class={}>",
            val.map_or(0, |bytes| bytes.len()),
            classify_txt_value(val)
        )
    } else {
        format!("{key}={val_str}")
    }
}

fn classify_txt_value(val: Option<&[u8]>) -> &'static str {
    let Some(bytes) = val else {
        return "flag";
    };
    if bytes.is_empty() {
        return "empty";
    }

    let Ok(text) = std::str::from_utf8(bytes) else {
        return "binary";
    };
    let text = text.trim();
    if text.is_empty() {
        return "whitespace";
    }
    if text.eq_ignore_ascii_case("true") || text.eq_ignore_ascii_case("false") {
        return "boolean";
    }
    if text.chars().all(|character| character.is_ascii_digit()) {
        return "integer";
    }
    if looks_like_version(text) {
        return "version";
    }
    if looks_like_mac_address(text) {
        return "mac-like";
    }
    if looks_like_uuid(text) {
        return "uuid-like";
    }
    if text.len() >= 2
        && text.len() % 2 == 0
        && text.chars().all(|character| character.is_ascii_hexdigit())
    {
        return "hex";
    }
    if text
        .chars()
        .all(|character| character.is_ascii_graphic() || character == ' ')
    {
        return "text";
    }

    "utf8"
}

fn looks_like_version(value: &str) -> bool {
    let mut parts = value.split('.');
    let Some(first) = parts.next() else {
        return false;
    };
    !first.is_empty()
        && first.chars().all(|character| character.is_ascii_digit())
        && parts.clone().next().is_some()
        && parts.all(|part| {
            !part.is_empty() && part.chars().all(|character| character.is_ascii_digit())
        })
}

fn looks_like_mac_address(value: &str) -> bool {
    let separator = if value.contains(':') {
        ':'
    } else if value.contains('-') {
        '-'
    } else {
        return false;
    };
    let parts = value.split(separator).collect::<Vec<_>>();
    parts.len() == 6
        && parts.iter().all(|part| {
            part.len() == 2 && part.chars().all(|character| character.is_ascii_hexdigit())
        })
}

fn looks_like_uuid(value: &str) -> bool {
    let parts = value.split('-').collect::<Vec<_>>();
    let expected_lengths = [8, 4, 4, 4, 12];
    parts.len() == expected_lengths.len()
        && parts
            .iter()
            .zip(expected_lengths)
            .all(|(part, expected_len)| {
                part.len() == expected_len
                    && part.chars().all(|character| character.is_ascii_hexdigit())
            })
}

fn service_event_kind(event: &ServiceEvent) -> &'static str {
    match event {
        ServiceEvent::SearchStarted(_) => "search_started",
        ServiceEvent::ServiceFound(_, _) => "service_found",
        ServiceEvent::ServiceResolved(_) => "service_resolved",
        ServiceEvent::ServiceRemoved(_, _) => "service_removed",
        ServiceEvent::SearchStopped(_) => "search_stopped",
        _ => "other",
    }
}

fn socket_addr_from_resolved(info: &ResolvedService) -> Option<SocketAddr> {
    let mut addrs: Vec<IpAddr> = info
        .get_addresses()
        .iter()
        .map(|addr| addr.to_ip_addr())
        .collect();
    addrs.sort_by_key(|addr| {
        (
            addr.is_loopback(),
            !addr.is_ipv4(),
            addr.is_unspecified(),
            addr.to_string(),
        )
    });
    addrs
        .into_iter()
        .find(|addr| !addr.is_unspecified())
        .map(|addr| SocketAddr::new(addr, info.get_port()))
}

fn sanitize_instance_name(value: &str) -> String {
    let mut name = value
        .chars()
        .map(|ch| {
            if ch.is_ascii_alphanumeric() || ch == '-' || ch == '_' {
                ch
            } else {
                '-'
            }
        })
        .collect::<String>();
    if name.is_empty() {
        name = "anykbflow".to_string();
    }
    name.truncate(48);
    name
}

fn advertise_ip_for(listen_addr: SocketAddr) -> IpAddr {
    if !listen_addr.ip().is_unspecified() {
        return listen_addr.ip();
    }

    UdpSocket::bind((IpAddr::from([0, 0, 0, 0]), 0))
        .and_then(|socket| {
            socket.connect((IpAddr::from([8, 8, 8, 8]), 80))?;
            socket.local_addr()
        })
        .map(|addr| addr.ip())
        .unwrap_or_else(|_| IpAddr::from([127, 0, 0, 1]))
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

#[cfg(test)]
mod tests {
    use std::{
        net::{IpAddr, Ipv4Addr},
        str::FromStr,
    };

    use mdns_sd::ServiceInfo;

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

        assert_eq!(properties.get("phase"), Some(&"visibility".to_string()));
        assert_eq!(properties.get("role"), Some(&"probe".to_string()));
    }

    #[test]
    fn sanitize_instance_name_keeps_dns_sd_friendly_name() {
        assert_eq!(sanitize_instance_name("Windows Desk"), "Windows-Desk");
        assert_eq!(sanitize_instance_name(""), "anykbflow");
    }

    #[test]
    fn socket_addr_prefers_non_loopback_ipv4() {
        let service = ServiceInfo::new(
            ANYKBFLOW_SERVICE,
            "desk",
            "desk.local.",
            &[
                IpAddr::V4(Ipv4Addr::LOCALHOST),
                IpAddr::from_str("192.0.2.10").unwrap(),
            ][..],
            24800,
            None,
        )
        .unwrap();
        let resolved = service.as_resolved_service();

        let addr = socket_addr_from_resolved(&resolved).unwrap();

        assert_eq!(addr.ip(), IpAddr::from_str("192.0.2.10").unwrap());
        assert_eq!(addr.port(), 24800);
    }

    #[test]
    fn advertise_ip_uses_explicit_bind_address() {
        let ip = IpAddr::from_str("192.0.2.44").unwrap();

        let advertised = advertise_ip_for(SocketAddr::new(ip, 24800));

        assert_eq!(advertised, ip);
    }

    #[test]
    fn classifies_txt_values_for_redaction() {
        assert_eq!(classify_txt_value(None), "flag");
        assert_eq!(classify_txt_value(Some(b"".as_slice())), "empty");
        assert_eq!(classify_txt_value(Some(b"true".as_slice())), "boolean");
        assert_eq!(classify_txt_value(Some(b"1234".as_slice())), "integer");
        assert_eq!(classify_txt_value(Some(b"1.2.3".as_slice())), "version");
        assert_eq!(
            classify_txt_value(Some(b"00:11:22:33:44:55".as_slice())),
            "mac-like"
        );
        assert_eq!(
            classify_txt_value(Some(b"550e8400-e29b-41d4-a716-446655440000".as_slice())),
            "uuid-like"
        );
        assert_eq!(classify_txt_value(Some(b"deadbeef".as_slice())), "hex");
        assert_eq!(classify_txt_value(Some(&[0xff, 0x00])), "binary");
    }

    #[test]
    fn formats_txt_properties_without_leaking_values_when_redacted() {
        assert_eq!(
            format_txt_property("rpVr", Some(b"174.4.1".as_slice()), "174.4.1", true),
            "rpVr=<redacted len=7 class=version>"
        );
        assert_eq!(
            format_txt_property("role", Some(b"probe".as_slice()), "probe", false),
            "role=probe"
        );
    }

    #[test]
    fn redacts_search_event_interface_details() {
        assert_eq!(
            format_service_event_subject(
                "_companion-link._tcp.local. on 2 interfaces [en0 (12), lo0 (1)]",
                true
            ),
            "_companion-link._tcp.local."
        );
        assert_eq!(
            format_service_event_subject(
                "_companion-link._tcp.local. on 2 interfaces [en0 (12), lo0 (1)]",
                false
            ),
            "_companion-link._tcp.local. on 2 interfaces [en0 (12), lo0 (1)]"
        );
    }
}
