use std::time::Duration;

use anyhow::{Context, Result};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{TcpListener, TcpStream},
    sync::mpsc,
};
use tracing::{debug, info, warn};

use crate::{
    config::{Config, Role},
    discovery, platform,
    protocol::{DisplayGeometry, PeerMessage},
};

pub struct Peer {
    pub inbound: mpsc::Receiver<PeerMessage>,
    pub outbound: mpsc::Sender<PeerMessage>,
}

pub async fn connect(config: &Config) -> Result<Peer> {
    let stream = match config.role {
        Role::InputOwner => {
            let listen_addr = config
                .listen_addr
                .context("input_owner role requires listen_addr")?;
            let listener = TcpListener::bind(listen_addr)
                .await
                .with_context(|| format!("failed to bind {listen_addr}"))?;
            discovery::spawn_bridge_advertisement(&config.node_name, listen_addr)?;
            info!("waiting for receiver on {}", listen_addr);
            let (stream, remote_addr) = listener.accept().await?;
            info!("receiver connected from {}", remote_addr);
            stream
        }
        Role::Receiver => {
            let peer_addr = match config.peer_addr {
                Some(peer_addr) => peer_addr,
                None => discovery::discover_bridge_peer(Duration::from_secs(30))
                    .context("failed to discover AnyKBFlow input owner")?,
            };
            loop {
                match TcpStream::connect(peer_addr).await {
                    Ok(stream) => {
                        info!("connected to input owner at {}", peer_addr);
                        break stream;
                    }
                    Err(error) => {
                        warn!("failed to connect to {}: {}", peer_addr, error);
                        tokio::time::sleep(Duration::from_secs(2)).await;
                    }
                }
            }
        }
    };

    let (read_half, mut write_half) = stream.into_split();
    let (outbound_tx, mut outbound_rx) = mpsc::channel::<PeerMessage>(256);
    let (inbound_tx, inbound_rx) = mpsc::channel::<PeerMessage>(256);

    let hello = hello_message(config);
    outbound_tx.send(hello).await?;

    tokio::spawn(async move {
        while let Some(message) = outbound_rx.recv().await {
            match serde_json::to_string(&message) {
                Ok(line) => {
                    if let Err(error) = write_half.write_all(line.as_bytes()).await {
                        warn!("failed to write peer message: {}", error);
                        break;
                    }
                    if let Err(error) = write_half.write_all(b"\n").await {
                        warn!("failed to write peer message delimiter: {}", error);
                        break;
                    }
                }
                Err(error) => warn!("failed to encode peer message: {}", error),
            }
        }
    });

    tokio::spawn(async move {
        let mut lines = BufReader::new(read_half).lines();
        loop {
            match lines.next_line().await {
                Ok(Some(line)) => match serde_json::from_str::<PeerMessage>(&line) {
                    Ok(message) => {
                        debug!("received peer message: {:?}", message);
                        if inbound_tx.send(message).await.is_err() {
                            break;
                        }
                    }
                    Err(error) => warn!("failed to decode peer message: {}", error),
                },
                Ok(None) => {
                    warn!("peer connection closed");
                    break;
                }
                Err(error) => {
                    warn!("failed to read peer message: {}", error);
                    break;
                }
            }
        }
    });

    Ok(Peer {
        inbound: inbound_rx,
        outbound: outbound_tx,
    })
}

fn hello_message(config: &Config) -> PeerMessage {
    let detected_display = match platform::primary_display_geometry() {
        Ok(display) => display,
        Err(error) => {
            warn!("failed to detect primary display geometry for hello: {error}");
            None
        }
    };

    PeerMessage::Hello {
        node_name: config.node_name.clone(),
        role: config.role,
        local_display: hello_display_geometry(config, detected_display),
    }
}

fn hello_display_geometry(config: &Config, detected: Option<DisplayGeometry>) -> DisplayGeometry {
    detected.unwrap_or(DisplayGeometry {
        width: config.layout.local_width,
        height: config.layout.local_height,
    })
}

pub async fn send(outbound: &mpsc::Sender<PeerMessage>, message: PeerMessage) -> Result<()> {
    outbound
        .send(message)
        .await
        .map_err(|_| anyhow::anyhow!("peer writer task is closed"))
}

pub fn ensure_receiver_has_peer(config: &Config) -> Result<()> {
    if config.role == Role::Receiver && config.peer_addr.is_none() {
        warn!("receiver peer_addr omitted; using mDNS discovery");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{Edge, Layout};

    fn config() -> Config {
        Config {
            node_name: "node-test".to_string(),
            role: Role::InputOwner,
            listen_addr: "127.0.0.1:24800".parse().ok(),
            peer_addr: None,
            layout: Layout {
                local_width: 100.0,
                local_height: 50.0,
                remote_width: 80.0,
                remote_height: 40.0,
                remote_edge: Edge::Right,
            },
        }
    }

    #[test]
    fn hello_geometry_uses_detected_display_when_available() {
        let geometry = hello_display_geometry(
            &config(),
            Some(DisplayGeometry {
                width: 300.0,
                height: 200.0,
            }),
        );

        assert_eq!(
            geometry,
            DisplayGeometry {
                width: 300.0,
                height: 200.0
            }
        );
    }

    #[test]
    fn hello_geometry_falls_back_to_config() {
        let geometry = hello_display_geometry(&config(), None);

        assert_eq!(
            geometry,
            DisplayGeometry {
                width: 100.0,
                height: 50.0
            }
        );
    }
}
