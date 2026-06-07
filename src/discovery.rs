use std::{
    collections::{BTreeSet, HashMap},
    io::{self, Read},
    net::{IpAddr, SocketAddr, TcpListener, UdpSocket},
    process::{Command, Stdio},
    sync::{
        Arc,
        atomic::{AtomicBool, AtomicUsize, Ordering},
    },
    thread,
    time::{Duration, Instant},
};

use anyhow::{Context, Result, bail};
use mdns_sd::{ResolvedService, ServiceDaemon, ServiceEvent, ServiceInfo};

const COMPANION_LINK_SERVICE: &str = "_companion-link._tcp.local.";
const DNS_SD_SERVICE: &str = "_companion-link._tcp";
const ANYKBFLOW_SERVICE: &str = "_anykbflow._tcp.local.";
const TCP_OBSERVER_READ_LIMIT: usize = 16;
const TCP_OBSERVER_READ_CHUNK_BYTES: usize = 4096;
const COMPANION_LINK_SHAPE_TXT: [(&str, &str); 8] = [
    ("rpAD", "000000000001"),
    ("rpBA", "02:00:00:00:00:01"),
    ("rpFl", "0xabcde"),
    ("rpHA", "000000000002"),
    ("rpHI", "000000000003"),
    ("rpHN", "000000000004"),
    ("rpMac", "0"),
    ("rpVr", "174"),
];
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
    pub observe_tcp: bool,
    pub observe_framing: bool,
}

pub fn companion_link_shape_txt() -> Vec<String> {
    COMPANION_LINK_SHAPE_TXT
        .iter()
        .map(|(key, value)| format!("{key}={value}"))
        .collect()
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
    if options.observe_framing && !options.observe_tcp {
        bail!("--observe-framing requires --observe-tcp");
    }

    let observe_addr = if options.observe_tcp {
        Some(observe_tcp_addr(
            options.addr.as_deref(),
            options.port,
            &hostname,
        )?)
    } else {
        None
    };
    let tcp_observer = observe_addr
        .map(|addr| spawn_tcp_observer(addr, Duration::from_secs(seconds), options.observe_framing))
        .transpose()?;
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

    if let Some(observer) = tcp_observer {
        observer.stop.store(true, Ordering::SeqCst);
        observer
            .handle
            .join()
            .map_err(|_| anyhow::anyhow!("TCP observer thread panicked"))?;
        println!(
            "TCP observer summary: accepted_connections={}",
            observer.accepted.load(Ordering::SeqCst)
        );
    }

    if let Ok(unregister_events) = mdns.unregister(&fullname) {
        while unregister_events
            .recv_timeout(Duration::from_millis(250))
            .is_ok()
        {}
    }

    mdns.shutdown().context("failed to shut down mDNS daemon")?;
    Ok(())
}

struct TcpObserver {
    stop: Arc<AtomicBool>,
    accepted: Arc<AtomicUsize>,
    handle: thread::JoinHandle<()>,
}

fn observe_tcp_addr(addr: Option<&str>, port: u16, hostname: &str) -> Result<SocketAddr> {
    let ip = match addr {
        Some(value) => value.parse::<IpAddr>().with_context(|| {
            format!("--addr must be an IP address when --observe-tcp is used: {value}")
        })?,
        None => IpAddr::from([0, 0, 0, 0]),
    };
    if ip.is_multicast() {
        bail!("cannot observe TCP on multicast address {ip}");
    }
    if hostname.eq_ignore_ascii_case("localhost.local.") && addr.is_none() {
        bail!("pass --addr explicitly when observing TCP with localhost hostname");
    }
    Ok(SocketAddr::new(ip, port))
}

fn spawn_tcp_observer(
    addr: SocketAddr,
    duration: Duration,
    observe_framing: bool,
) -> Result<TcpObserver> {
    let listener = TcpListener::bind(addr)
        .with_context(|| format!("failed to bind TCP observer on advertised address {addr}"))?;
    listener
        .set_nonblocking(true)
        .context("failed to set TCP observer nonblocking mode")?;

    let stop = Arc::new(AtomicBool::new(false));
    let accepted = Arc::new(AtomicUsize::new(0));
    let thread_stop = Arc::clone(&stop);
    let thread_accepted = Arc::clone(&accepted);
    let handle = thread::spawn(move || {
        run_tcp_observer(
            listener,
            addr,
            duration,
            observe_framing,
            thread_stop,
            thread_accepted,
        )
    });

    Ok(TcpObserver {
        stop,
        accepted,
        handle,
    })
}

fn run_tcp_observer(
    listener: TcpListener,
    addr: SocketAddr,
    duration: Duration,
    observe_framing: bool,
    stop: Arc<AtomicBool>,
    accepted: Arc<AtomicUsize>,
) {
    println!(
        "TCP observer listening on {addr} for {}s",
        duration.as_secs().max(1)
    );
    if observe_framing {
        println!("TCP observer framing probe enabled: yes");
    }
    let deadline = Instant::now() + duration;
    while !stop.load(Ordering::SeqCst) && Instant::now() < deadline {
        match listener.accept() {
            Ok((mut stream, peer)) => {
                let index = accepted.fetch_add(1, Ordering::SeqCst) + 1;
                println!("TCP observer accepted connection #{index} from {peer}");
                if let Err(error) = stream.set_read_timeout(Some(Duration::from_millis(250))) {
                    eprintln!("TCP observer failed to set read timeout for {peer}: {error}");
                    continue;
                }

                observe_tcp_connection(&mut stream, index, observe_framing);
            }
            Err(error) if error.kind() == io::ErrorKind::WouldBlock => {
                thread::sleep(Duration::from_millis(50));
            }
            Err(error) => {
                eprintln!("TCP observer accept error: {error}");
                thread::sleep(Duration::from_millis(250));
            }
        }
    }
}

fn observe_tcp_connection(stream: &mut impl Read, index: usize, observe_framing: bool) {
    let started = Instant::now();
    let mut buffer = [0u8; TCP_OBSERVER_READ_CHUNK_BYTES];
    let mut reads = 0usize;
    let mut total_bytes = 0usize;
    let mut closed_by_peer = false;

    for read_index in 1..=TCP_OBSERVER_READ_LIMIT {
        match stream.read(&mut buffer) {
            Ok(0) => {
                if reads == 0 {
                    println!("TCP observer connection #{index} closed without data");
                } else {
                    closed_by_peer = true;
                }
                break;
            }
            Ok(bytes) => {
                reads += 1;
                total_bytes += bytes;
                if read_index == 1 {
                    println!(
                        "TCP observer connection #{index} first_read_elapsed_ms={} first_read_bytes={bytes}",
                        started.elapsed().as_millis()
                    );
                } else {
                    println!(
                        "TCP observer connection #{index} read #{read_index} elapsed_ms={} bytes={bytes}",
                        started.elapsed().as_millis()
                    );
                }
                if observe_framing {
                    println!(
                        "TCP observer connection #{index} read #{read_index} framing {}",
                        frame_shape_summary(&buffer[..bytes])
                    );
                }
            }
            Err(error)
                if matches!(
                    error.kind(),
                    io::ErrorKind::WouldBlock | io::ErrorKind::TimedOut
                ) =>
            {
                if reads == 0 {
                    println!("TCP observer connection #{index} produced no data before timeout");
                }
                break;
            }
            Err(error) => {
                eprintln!("TCP observer read error on connection #{index}: {error}");
                break;
            }
        }
    }

    if reads > 0 {
        println!(
            "TCP observer connection #{index} summary reads={reads} total_bytes={total_bytes} duration_ms={} read_limit_reached={} closed_by_peer={closed_by_peer}",
            started.elapsed().as_millis(),
            reads >= TCP_OBSERVER_READ_LIMIT
        );
    }
}

fn frame_shape_summary(bytes: &[u8]) -> String {
    let byte_classes = byte_class_counts(bytes);
    let length_prefix_candidates = length_prefix_candidates(bytes);
    let (tls_record_like, tls_record_len_match) = tls_record_shape(bytes);

    format!(
        "first_byte_class={} ascii_ratio={} high_ratio={} zero_ratio={} control_ratio={} entropy_bucket={} byte_diversity_bucket={} length_prefix_candidates={} tls_record_like={} tls_record_len_match={}",
        first_byte_class(bytes),
        ratio_bucket(byte_classes.ascii, bytes.len()),
        ratio_bucket(byte_classes.high, bytes.len()),
        ratio_bucket(byte_classes.zero, bytes.len()),
        ratio_bucket(byte_classes.control, bytes.len()),
        entropy_bucket(bytes),
        byte_diversity_bucket(bytes),
        format_candidates(&length_prefix_candidates),
        format_bool(tls_record_like),
        format_bool(tls_record_len_match),
    )
}

#[derive(Default)]
struct ByteClassCounts {
    ascii: usize,
    control: usize,
    high: usize,
    zero: usize,
}

fn byte_class_counts(bytes: &[u8]) -> ByteClassCounts {
    let mut counts = ByteClassCounts::default();
    for byte in bytes {
        match *byte {
            0 => counts.zero += 1,
            0x20..=0x7e | b'\n' | b'\r' | b'\t' => counts.ascii += 1,
            0x01..=0x1f | 0x7f => counts.control += 1,
            _ => counts.high += 1,
        }
    }
    counts
}

fn first_byte_class(bytes: &[u8]) -> &'static str {
    match bytes.first().copied() {
        None => "none",
        Some(0) => "zero",
        Some(0x20..=0x7e) => "ascii",
        Some(b'\n' | b'\r' | b'\t') => "ascii-whitespace",
        Some(0x01..=0x1f | 0x7f) => "control",
        Some(_) => "high",
    }
}

fn ratio_bucket(count: usize, total: usize) -> &'static str {
    if total == 0 || count == 0 {
        return "0pct";
    }
    if count == total {
        return "100pct";
    }

    let percent = count * 100 / total;
    match percent {
        0..=9 => "1-9pct",
        10..=49 => "10-49pct",
        50..=89 => "50-89pct",
        _ => "90-99pct",
    }
}

fn entropy_bucket(bytes: &[u8]) -> &'static str {
    if bytes.is_empty() {
        return "empty";
    }

    let mut counts = [0usize; 256];
    for byte in bytes {
        counts[*byte as usize] += 1;
    }

    let total = bytes.len() as f64;
    let mut entropy = 0.0f64;
    for count in counts {
        if count == 0 {
            continue;
        }
        let probability = count as f64 / total;
        entropy -= probability * probability.log2();
    }

    if entropy < 2.0 {
        "0-2bits"
    } else if entropy < 4.0 {
        "2-4bits"
    } else if entropy < 6.0 {
        "4-6bits"
    } else if entropy < 7.0 {
        "6-7bits"
    } else {
        "7-8bits"
    }
}

fn byte_diversity_bucket(bytes: &[u8]) -> &'static str {
    if bytes.is_empty() {
        return "empty";
    }

    let mut seen = [false; 256];
    let mut unique = 0usize;
    for byte in bytes {
        let index = *byte as usize;
        if !seen[index] {
            seen[index] = true;
            unique += 1;
        }
    }

    match unique {
        1 => "1",
        2..=4 => "2-4",
        5..=16 => "5-16",
        17..=64 => "17-64",
        65..=128 => "65-128",
        _ => "129-256",
    }
}

fn length_prefix_candidates(bytes: &[u8]) -> Vec<&'static str> {
    let mut candidates = Vec::new();
    if bytes.len() >= 2 {
        let be16 = u16::from_be_bytes([bytes[0], bytes[1]]) as usize;
        let le16 = u16::from_le_bytes([bytes[0], bytes[1]]) as usize;
        push_length_matches(&mut candidates, "be16", be16, 2, bytes.len());
        push_length_matches(&mut candidates, "le16", le16, 2, bytes.len());
    }
    if bytes.len() >= 4 {
        let be32 = u32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]) as usize;
        let le32 = u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]) as usize;
        push_length_matches(&mut candidates, "be32", be32, 4, bytes.len());
        push_length_matches(&mut candidates, "le32", le32, 4, bytes.len());
    }
    candidates
}

fn push_length_matches(
    candidates: &mut Vec<&'static str>,
    endian: &'static str,
    value: usize,
    prefix_bytes: usize,
    total_bytes: usize,
) {
    let payload_match = value
        .checked_add(prefix_bytes)
        .is_some_and(|total| total == total_bytes);
    match (endian, value == total_bytes, payload_match) {
        ("be16", true, _) => candidates.push("be16_total"),
        ("be16", _, true) => candidates.push("be16_payload"),
        ("le16", true, _) => candidates.push("le16_total"),
        ("le16", _, true) => candidates.push("le16_payload"),
        ("be32", true, _) => candidates.push("be32_total"),
        ("be32", _, true) => candidates.push("be32_payload"),
        ("le32", true, _) => candidates.push("le32_total"),
        ("le32", _, true) => candidates.push("le32_payload"),
        _ => {}
    }
}

fn tls_record_shape(bytes: &[u8]) -> (bool, bool) {
    if bytes.len() < 5 {
        return (false, false);
    }

    let content_type = matches!(bytes[0], 0x14..=0x18);
    let version = bytes[1] == 0x03 && bytes[2] <= 0x04;
    let payload_len = u16::from_be_bytes([bytes[3], bytes[4]]) as usize;
    let record_like = content_type && version;
    (record_like, record_like && payload_len + 5 == bytes.len())
}

fn format_candidates(candidates: &[&str]) -> String {
    if candidates.is_empty() {
        return "none".to_string();
    }
    candidates.join("|")
}

fn format_bool(value: bool) -> &'static str {
    if value { "yes" } else { "no" }
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
    if let Some(hex) = text.strip_prefix("0x").or_else(|| text.strip_prefix("0X"))
        && !hex.is_empty()
        && hex.chars().all(|character| character.is_ascii_hexdigit())
    {
        return "hex-prefixed";
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
    fn companion_link_shape_txt_matches_redacted_baseline_classes() {
        let txt = companion_link_shape_txt();
        let properties = parse_txt_properties(&txt).unwrap();

        assert_eq!(
            properties.keys().cloned().collect::<BTreeSet<_>>(),
            BTreeSet::from([
                "rpAD".to_string(),
                "rpBA".to_string(),
                "rpFl".to_string(),
                "rpHA".to_string(),
                "rpHI".to_string(),
                "rpHN".to_string(),
                "rpMac".to_string(),
                "rpVr".to_string(),
            ])
        );
        assert!(properties["rpAD"].chars().all(|ch| ch.is_ascii_hexdigit()));
        assert_eq!(properties["rpAD"].len(), 12);
        assert_eq!(properties["rpBA"], "02:00:00:00:00:01");
        assert!(properties["rpFl"].starts_with("0x"));
        assert_eq!(properties["rpFl"].len(), 7);
        assert!(
            properties["rpFl"]
                .trim_start_matches("0x")
                .chars()
                .all(|ch| ch.is_ascii_hexdigit())
        );
        assert!(properties["rpHA"].chars().all(|ch| ch.is_ascii_hexdigit()));
        assert_eq!(properties["rpHA"].len(), 12);
        assert!(properties["rpHI"].chars().all(|ch| ch.is_ascii_hexdigit()));
        assert_eq!(properties["rpHI"].len(), 12);
        assert!(properties["rpHN"].chars().all(|ch| ch.is_ascii_hexdigit()));
        assert_eq!(properties["rpHN"].len(), 12);
        assert!(properties["rpMac"].chars().all(|ch| ch.is_ascii_hexdigit()));
        assert_eq!(properties["rpMac"].len(), 1);
        assert!(properties["rpVr"].chars().all(|ch| ch.is_ascii_digit()));
    }

    #[test]
    fn tcp_observer_defaults_to_unspecified_bind_address() {
        assert_eq!(
            observe_tcp_addr(None, 61833, "anykbflow-native-shape-probe.local.").unwrap(),
            SocketAddr::new(IpAddr::from([0, 0, 0, 0]), 61833)
        );
    }

    #[test]
    fn tcp_observer_rejects_multicast_advertise_address() {
        assert!(observe_tcp_addr(Some("224.0.0.251"), 5353, "probe.local.").is_err());
    }

    #[test]
    fn frame_shape_detects_length_prefixes_without_payload_values() {
        let bytes = [0x00, 0x05, 0xaa, 0xbb, 0xcc, 0xdd, 0xee];

        let summary = frame_shape_summary(&bytes);

        assert!(summary.contains("first_byte_class=zero"));
        assert!(summary.contains("entropy_bucket=2-4bits"));
        assert!(summary.contains("byte_diversity_bucket=5-16"));
        assert!(summary.contains("length_prefix_candidates=be16_payload"));
        assert!(summary.contains("tls_record_like=no"));
    }

    #[test]
    fn frame_shape_detects_tls_record_shape() {
        let bytes = [0x16, 0x03, 0x03, 0x00, 0x02, 0xaa, 0xbb];

        let summary = frame_shape_summary(&bytes);

        assert!(summary.contains("first_byte_class=control"));
        assert!(summary.contains("byte_diversity_bucket=5-16"));
        assert!(summary.contains("tls_record_like=yes"));
        assert!(summary.contains("tls_record_len_match=yes"));
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
            classify_txt_value(Some(b"0x20040".as_slice())),
            "hex-prefixed"
        );
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
