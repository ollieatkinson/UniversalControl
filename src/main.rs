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
    },
    /// Advertise an arbitrary DNS-SD service with the Rust mDNS backend.
    Advertise {
        #[arg(long, default_value = "_anykbflow-test._tcp.local.")]
        service: String,

        #[arg(long, default_value = "anykbflow-windows")]
        instance: String,

        #[arg(long, default_value = "anykbflow.local.")]
        host: String,

        #[arg(long, default_value = "127.0.0.1")]
        addr: String,

        #[arg(long, default_value_t = 24800)]
        port: u16,

        #[arg(long = "txt")]
        txt: Vec<String>,

        #[arg(long, default_value_t = 30)]
        seconds: u64,
    },
}

#[derive(Debug, Subcommand)]
enum ProbeCommand {
    /// Print observed native input events without suppressing them.
    Listen {
        #[arg(short, long, default_value_t = 10)]
        count: usize,
    },
    /// Grab native input events, optionally suppressing local delivery.
    Grab {
        #[arg(short, long, default_value_t = 10)]
        count: usize,

        #[arg(long)]
        suppress: bool,
    },
    /// Inject a single key press/release.
    Inject {
        #[arg(long, default_value = "KeyA")]
        key: String,
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
        Command::Discovery { command } => match command {
            DiscoveryCommand::Browse { service, seconds } => discovery::browse(&service, seconds),
            DiscoveryCommand::Advertise {
                service,
                instance,
                host,
                addr,
                port,
                txt,
                seconds,
            } => discovery::advertise(&service, &instance, &host, &addr, port, &txt, seconds),
        },
        Command::Probe { command } => match command {
            ProbeCommand::Listen { count } => platform::probe_listen(count),
            ProbeCommand::Grab { count, suppress } => platform::probe_grab(count, suppress),
            ProbeCommand::Inject { key } => platform::probe_inject_key(&key),
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
