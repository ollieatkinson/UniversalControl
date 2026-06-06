use std::{
    collections::BTreeSet,
    io,
    process::{Command, Stdio},
    thread,
    time::{Duration, Instant},
};

use anyhow::{Context, Result, bail};
use mdns_sd::{ServiceDaemon, ServiceEvent};

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
        DiscoveryBackend::Auto => browse_with_rust_mdns(seconds, include_apple_p2p),
        DiscoveryBackend::System => browse_with_dns_sd(seconds),
        DiscoveryBackend::RustMdns => browse_with_rust_mdns(seconds, include_apple_p2p),
    }
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

fn has_dns_sd() -> bool {
    Command::new("dns-sd")
        .arg("-help")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .is_ok()
}
