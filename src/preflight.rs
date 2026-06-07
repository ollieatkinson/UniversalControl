use std::net::IpAddr;

use anyhow::Result;

use crate::{
    config::{Config, Role},
    platform,
    protocol::DisplayGeometry,
};

pub fn run(config: &Config) -> Result<()> {
    let detected_display = platform::primary_display_geometry()?;
    let effective_display = detected_display.unwrap_or(DisplayGeometry {
        width: config.layout.local_width,
        height: config.layout.local_height,
    });

    println!("preflight_status=ok");
    println!("node_name={}", config.node_name);
    println!("role={:?}", config.role);
    println!("capture_enabled={}", config.role == Role::InputOwner);
    println!(
        "configured_local_display={}x{}",
        config.layout.local_width, config.layout.local_height
    );
    println!(
        "configured_remote_display={}x{}",
        config.layout.remote_width, config.layout.remote_height
    );
    println!("remote_edge={:?}", config.layout.remote_edge);
    println!(
        "detected_primary_display={}",
        format_display(detected_display)
    );
    println!(
        "effective_local_display={}x{}",
        effective_display.width, effective_display.height
    );
    print_network(config);
    print_warnings(config, detected_display);
    Ok(())
}

fn print_network(config: &Config) {
    match config.role {
        Role::InputOwner => {
            println!("listen_addr={}", format_option(config.listen_addr));
            println!("advertises_service=_anykbflow._tcp.local.");
            println!("peer_mode=listen");
        }
        Role::Receiver => {
            println!("peer_addr={}", format_option(config.peer_addr));
            if config.peer_addr.is_some() {
                println!("peer_mode=manual_connect");
            } else {
                println!("peer_mode=mdns_discovery");
                println!("discovers_service=_anykbflow._tcp.local.");
            }
        }
    }
}

fn print_warnings(config: &Config, detected_display: Option<DisplayGeometry>) {
    let mut warnings = Vec::new();

    if detected_display.is_none() {
        warnings.push(
            "native primary display was not detected; configured layout dimensions will be used"
                .to_string(),
        );
    }

    if let Some(listen_addr) = config.listen_addr
        && config.role == Role::InputOwner
        && is_loopback_or_unspecified_v6(listen_addr.ip())
    {
        warnings.push(format!(
            "input_owner listen_addr {listen_addr} may not be reachable from the other machine"
        ));
    }

    if let Some(peer_addr) = config.peer_addr
        && config.role == Role::Receiver
        && peer_addr.ip().is_loopback()
    {
        warnings.push(format!(
            "receiver peer_addr {peer_addr} only works when the input owner is on the same machine"
        ));
    }

    println!("warnings={}", warnings.len());
    for warning in warnings {
        println!("warning={warning}");
    }
}

fn format_display(display: Option<DisplayGeometry>) -> String {
    match display {
        Some(display) => format!("{}x{}", display.width, display.height),
        None => "none".to_string(),
    }
}

fn format_option<T: std::fmt::Display>(value: Option<T>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "none".to_string())
}

fn is_loopback_or_unspecified_v6(ip: IpAddr) -> bool {
    ip.is_loopback() || matches!(ip, IpAddr::V6(addr) if addr.is_unspecified())
}

#[cfg(test)]
mod tests {
    use std::net::IpAddr;

    use super::{format_display, is_loopback_or_unspecified_v6};
    use crate::protocol::DisplayGeometry;

    #[test]
    fn formats_missing_display() {
        assert_eq!(format_display(None), "none");
    }

    #[test]
    fn formats_detected_display() {
        assert_eq!(
            format_display(Some(DisplayGeometry {
                width: 1710.0,
                height: 1112.0
            })),
            "1710x1112"
        );
    }

    #[test]
    fn flags_loopback_and_unspecified_v6() {
        assert!(is_loopback_or_unspecified_v6(IpAddr::from([127, 0, 0, 1])));
        assert!(is_loopback_or_unspecified_v6(IpAddr::from([0u16; 8])));
        assert!(!is_loopback_or_unspecified_v6(IpAddr::from([0, 0, 0, 0])));
    }
}
