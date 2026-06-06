mod app;
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
            include_apple_p2p,
        } => discovery::browse_companion_link(seconds, backend.into(), include_apple_p2p),
        Command::AdvertiseMdns {
            seconds,
            service_type,
            instance,
            hostname,
            port,
            txt,
            allow_apple_service,
            include_apple_p2p,
        } => discovery::advertise_mdns(discovery::AdvertiseOptions {
            seconds,
            service_type,
            instance,
            hostname,
            port,
            txt,
            allow_apple_service,
            include_apple_p2p,
        }),
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
