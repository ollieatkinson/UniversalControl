mod app;
mod bridge_smoke;
mod config;
mod discovery;
mod network;
mod platform;
mod protocol;
mod router;

use std::path::PathBuf;

use anyhow::Result;
use clap::{Parser, Subcommand, ValueEnum};
use tracing_subscriber::EnvFilter;

#[derive(Debug, Parser)]
#[command(author, version, about)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,

    #[arg(short, long, default_value = "anykbflow.toml", global = true)]
    config: PathBuf,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Run the AnyKBFlow software KVM daemon.
    Run,
    /// Browse for Apple's native Rapport/CompanionLink mDNS service.
    DiscoverCompanionLink {
        /// Browse duration in seconds.
        #[arg(long, default_value_t = 10)]
        seconds: u64,
        /// Discovery backend to use.
        #[arg(long, value_enum, default_value_t = DiscoveryBackend::Auto)]
        backend: DiscoveryBackend,
        /// Redact hostnames, addresses, instance names, and TXT values.
        #[arg(long)]
        redact: bool,
        /// Include Apple peer-to-peer interfaces such as awdl on macOS.
        #[arg(long)]
        include_apple_p2p: bool,
    },
    /// Advertise a bounded mDNS test service for visibility checks.
    AdvertiseMdns {
        /// Advertise duration in seconds.
        #[arg(long, default_value_t = 30)]
        seconds: u64,
        /// DNS-SD service type, with or without the .local. suffix.
        #[arg(long, default_value = "_anykbflow-probe._tcp")]
        service_type: String,
        /// Instance name to publish.
        #[arg(long, default_value = "AnyKBFlow Probe")]
        instance: String,
        /// Hostname to publish, with or without the .local. suffix. Defaults to this machine's hostname.
        #[arg(long)]
        hostname: Option<String>,
        /// Explicit IP address to publish. If omitted, local interface addresses are selected automatically.
        #[arg(long)]
        addr: Option<String>,
        /// TCP port to publish in the SRV record.
        #[arg(long, default_value_t = 49152)]
        port: u16,
        /// TXT property as key=value. Repeat for multiple properties.
        #[arg(long = "txt")]
        txt: Vec<String>,
        /// Allow advertising Apple-owned service types such as _companion-link._tcp.
        #[arg(long)]
        allow_apple_service: bool,
        /// Include Apple peer-to-peer interfaces such as awdl on macOS.
        #[arg(long)]
        include_apple_p2p: bool,
        /// Open a bounded TCP listener on the advertised port and log connection attempts.
        #[arg(long)]
        observe_tcp: bool,
    },
    /// Advertise a shape-only CompanionLink candidate with placeholder TXT values.
    AdvertiseCompanionLinkShape {
        /// Advertise duration in seconds.
        #[arg(long, default_value_t = 60)]
        seconds: u64,
        /// Instance name to publish.
        #[arg(long, default_value = "AnyKBFlow Native Shape Probe")]
        instance: String,
        /// Hostname to publish, with or without the .local. suffix.
        #[arg(long, default_value = "anykbflow-native-shape-probe")]
        hostname: String,
        /// Explicit IP address to publish. If omitted, local interface addresses are selected automatically.
        #[arg(long)]
        addr: Option<String>,
        /// TCP port to publish in the SRV record. The macOS baseline observed 61833.
        #[arg(long, default_value_t = 61833)]
        port: u16,
        /// Include Apple peer-to-peer interfaces such as awdl on macOS.
        #[arg(long)]
        include_apple_p2p: bool,
        /// Open a bounded TCP listener on the advertised port and log connection attempts.
        #[arg(long)]
        observe_tcp: bool,
        /// Required guard for the native-compatibility shape experiment.
        #[arg(long)]
        acknowledge_shape_experiment: bool,
    },
    /// Browse or advertise arbitrary mDNS services for interop probes.
    Discovery {
        #[command(subcommand)]
        command: DiscoveryCommand,
    },
    /// Run native input capture/injection probes.
    Probe {
        #[command(subcommand)]
        command: ProbeCommand,
    },
}

#[derive(Debug, Subcommand)]
enum DiscoveryCommand {
    /// Browse an arbitrary DNS-SD service with the Rust mDNS backend.
    Browse {
        #[arg(long, default_value = "_companion-link._tcp.local.")]
        service: String,
        #[arg(long, default_value_t = 10)]
        seconds: u64,
        /// Redact hostnames, addresses, instance names, and TXT values.
        #[arg(long)]
        redact: bool,
        /// Include Apple peer-to-peer interfaces such as awdl on macOS.
        #[arg(long)]
        include_apple_p2p: bool,
    },
    /// Advertise an arbitrary DNS-SD service with the Rust mDNS backend.
    Advertise {
        #[arg(long, default_value = "_anykbflow-probe._tcp")]
        service: String,
        #[arg(long, default_value = "AnyKBFlow Probe")]
        instance: String,
        /// Hostname to publish. Defaults to this machine's hostname.
        #[arg(long)]
        host: Option<String>,
        /// Explicit IP address to publish. If omitted, local interface addresses are selected automatically.
        #[arg(long)]
        addr: Option<String>,
        #[arg(long, default_value_t = 49152)]
        port: u16,
        #[arg(long = "txt")]
        txt: Vec<String>,
        #[arg(long, default_value_t = 30)]
        seconds: u64,
        /// Allow advertising Apple-owned service types such as _companion-link._tcp.
        #[arg(long)]
        allow_apple_service: bool,
        /// Include Apple peer-to-peer interfaces such as awdl on macOS.
        #[arg(long)]
        include_apple_p2p: bool,
        /// Open a bounded TCP listener on the advertised port and log connection attempts.
        #[arg(long)]
        observe_tcp: bool,
    },
}

#[derive(Debug, Subcommand)]
enum ProbeCommand {
    /// Exercise JSON peer messages over a loopback TCP connection.
    BridgeNetworkSmoke,
    /// Simulate edge routing and receiver injection without native input.
    BridgeSmoke,
    /// Print native display geometry for layout calibration.
    Displays,
    /// Print observed native input events without suppressing them.
    Listen {
        #[arg(short, long, default_value_t = 10)]
        count: usize,
    },
    /// Print normalized AnyKBFlow input events without suppressing them.
    ListenEvents {
        #[arg(long, default_value_t = 10)]
        count: usize,
    },
    /// Grab native input events, optionally suppressing local delivery.
    Grab {
        #[arg(short, long, default_value_t = 10)]
        count: usize,

        #[arg(long)]
        suppress: bool,
    },
    /// Grab normalized AnyKBFlow input events, optionally suppressing local delivery.
    GrabEvents {
        #[arg(long, default_value_t = 10)]
        count: usize,

        #[arg(long)]
        suppress: bool,
    },
    /// Replay normalized AnyKBFlow input events from a JSONL file.
    ReplayEvents {
        #[arg(long)]
        path: PathBuf,

        #[arg(long, default_value_t = 20)]
        delay_ms: u64,
    },
    /// Inject a single key press/release.
    Inject {
        #[arg(long, default_value = "KeyA")]
        key: String,
    },
    /// Inject a single absolute mouse move.
    InjectMouse {
        #[arg(long)]
        x: f64,
        #[arg(long)]
        y: f64,
    },
    /// Inject a single mouse button press/release.
    InjectButton {
        #[arg(long, default_value = "Left")]
        button: String,
    },
    /// Inject a single wheel event.
    InjectWheel {
        #[arg(long, default_value_t = 0)]
        delta_x: i64,
        #[arg(long, default_value_t = 1)]
        delta_y: i64,
    },
}

#[derive(Clone, Debug, ValueEnum)]
enum DiscoveryBackend {
    Auto,
    System,
    RustMdns,
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("anykbflow=info")),
        )
        .init();

    let cli = Cli::parse();

    match cli.command.unwrap_or(Command::Run) {
        Command::Run => {
            let config = config::Config::load(&cli.config)?;
            app::run(config).await
        }
        Command::DiscoverCompanionLink {
            seconds,
            backend,
            redact,
            include_apple_p2p,
        } => discovery::browse_companion_link(seconds, backend.into(), redact, include_apple_p2p),
        Command::AdvertiseMdns {
            seconds,
            service_type,
            instance,
            hostname,
            addr,
            port,
            txt,
            allow_apple_service,
            include_apple_p2p,
            observe_tcp,
        } => discovery::advertise_mdns(discovery::AdvertiseOptions {
            seconds,
            service_type,
            instance,
            hostname,
            addr,
            port,
            txt,
            allow_apple_service,
            include_apple_p2p,
            observe_tcp,
        }),
        Command::AdvertiseCompanionLinkShape {
            seconds,
            instance,
            hostname,
            addr,
            port,
            include_apple_p2p,
            observe_tcp,
            acknowledge_shape_experiment,
        } => {
            if !acknowledge_shape_experiment {
                anyhow::bail!(
                    "refusing to advertise a CompanionLink-shaped candidate without --acknowledge-shape-experiment"
                );
            }

            discovery::advertise_mdns(discovery::AdvertiseOptions {
                seconds,
                service_type: "_companion-link._tcp".to_string(),
                instance,
                hostname: Some(hostname),
                addr,
                port,
                txt: discovery::companion_link_shape_txt(),
                allow_apple_service: true,
                include_apple_p2p,
                observe_tcp,
            })
        }
        Command::Discovery { command } => match command {
            DiscoveryCommand::Browse {
                service,
                seconds,
                redact,
                include_apple_p2p,
            } => discovery::browse(&service, seconds, redact, include_apple_p2p),
            DiscoveryCommand::Advertise {
                service,
                instance,
                host,
                addr,
                port,
                txt,
                seconds,
                allow_apple_service,
                include_apple_p2p,
                observe_tcp,
            } => discovery::advertise_mdns(discovery::AdvertiseOptions {
                seconds,
                service_type: service,
                instance,
                hostname: host,
                addr,
                port,
                txt,
                allow_apple_service,
                include_apple_p2p,
                observe_tcp,
            }),
        },
        Command::Probe { command } => match command {
            ProbeCommand::BridgeNetworkSmoke => {
                let config = config::Config::load(&cli.config)?;
                bridge_smoke::run_network(config).await
            }
            ProbeCommand::BridgeSmoke => {
                let config = config::Config::load(&cli.config)?;
                bridge_smoke::run(config)
            }
            ProbeCommand::Displays => platform::probe_displays(),
            ProbeCommand::Listen { count } => platform::probe_listen(count),
            ProbeCommand::ListenEvents { count } => platform::probe_listen_events(count),
            ProbeCommand::Grab { count, suppress } => platform::probe_grab(count, suppress),
            ProbeCommand::GrabEvents { count, suppress } => {
                platform::probe_grab_events(count, suppress)
            }
            ProbeCommand::ReplayEvents { path, delay_ms } => {
                platform::probe_replay_events(&path, delay_ms)
            }
            ProbeCommand::Inject { key } => platform::probe_inject_key(&key),
            ProbeCommand::InjectMouse { x, y } => platform::probe_inject_mouse(x, y),
            ProbeCommand::InjectButton { button } => platform::probe_inject_button(&button),
            ProbeCommand::InjectWheel { delta_x, delta_y } => {
                platform::probe_inject_wheel(delta_x, delta_y)
            }
        },
    }
}

impl From<DiscoveryBackend> for discovery::DiscoveryBackend {
    fn from(value: DiscoveryBackend) -> Self {
        match value {
            DiscoveryBackend::Auto => Self::Auto,
            DiscoveryBackend::System => Self::System,
            DiscoveryBackend::RustMdns => Self::RustMdns,
        }
    }
}
