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
