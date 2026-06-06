use std::time::Duration;

use anyhow::Result;
use tokio::time;
use tracing::{debug, info, warn};

use crate::{
    config::{Config, Role},
    network,
    platform::{self, PlatformCommand},
    protocol::PeerMessage,
    router::InputRouter,
};

pub async fn run(config: Config) -> Result<()> {
    network::ensure_receiver_has_peer(&config)?;
    info!("starting {} as {:?}", config.node_name, config.role);

    let capture = config.role == Role::InputOwner;
    let (mut captured_rx, platform_tx) = platform::spawn(capture)?;
    let mut peer = network::connect(&config).await?;

    match config.role {
        Role::InputOwner => run_input_owner(config, &mut captured_rx, &peer.outbound).await,
        Role::Receiver => run_receiver(&mut peer.inbound, &peer.outbound, platform_tx).await,
    }
}

async fn run_input_owner(
    config: Config,
    captured_rx: &mut tokio::sync::mpsc::Receiver<platform::CaptureEvent>,
    outbound: &tokio::sync::mpsc::Sender<PeerMessage>,
) -> Result<()> {
    let mut router = InputRouter::new(config.layout);
    let mut heartbeat = time::interval(Duration::from_secs(5));

    loop {
        tokio::select! {
            captured = captured_rx.recv() => {
                let Some(captured) = captured else {
                    warn!("input capture channel closed");
                    return Ok(());
                };

                let decision = router.handle_captured(captured.event);
                if captured.suppress.send(decision.suppress_local).is_err() {
                    warn!("capture suppress response channel closed");
                }

                for message in decision.messages {
                    debug!("sending routed message: {:?}", message);
                    network::send(outbound, message).await?;
                }
            }
            _ = heartbeat.tick() => {
                network::send(outbound, PeerMessage::Heartbeat).await?;
            }
        }
    }
}

async fn run_receiver(
    inbound: &mut tokio::sync::mpsc::Receiver<PeerMessage>,
    outbound: &tokio::sync::mpsc::Sender<PeerMessage>,
    platform_tx: tokio::sync::mpsc::Sender<PlatformCommand>,
) -> Result<()> {
    let mut heartbeat = time::interval(Duration::from_secs(5));

    loop {
        tokio::select! {
            message = inbound.recv() => {
                let Some(message) = message else {
                    warn!("peer connection closed");
                    return Ok(());
                };

                match message {
                    PeerMessage::Hello { node_name } => {
                        info!("input owner identified as {}", node_name);
                    }
                    PeerMessage::Active { remote_active } => {
                        info!("remote_active={}", remote_active);
                    }
                    PeerMessage::Input { event } => {
                        platform_tx.send(PlatformCommand::Inject(event)).await?;
                    }
                    PeerMessage::Heartbeat => {}
                }
            }
            _ = heartbeat.tick() => {
                network::send(outbound, PeerMessage::Heartbeat).await?;
            }
        }
    }
}
