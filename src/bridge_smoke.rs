use std::{net::SocketAddr, time::Duration};

use anyhow::{Context, Result, bail};
use tokio::{
    net::{TcpListener, TcpStream},
    time,
};

use crate::{
    config::{Config, Edge, Layout, Role},
    network, platform,
    protocol::{DisplayGeometry, InputEvent, PeerMessage},
    router::InputRouter,
};

pub fn run(config: Config) -> Result<()> {
    if config.role != Role::InputOwner {
        bail!("bridge smoke requires an input_owner config");
    }

    let local_display = detected_display_or_config(
        DisplayGeometry {
            width: config.layout.local_width,
            height: config.layout.local_height,
        },
        "local input-owner",
    );
    let remote_display = DisplayGeometry {
        width: config.layout.remote_width,
        height: config.layout.remote_height,
    };

    let mut router = InputRouter::new(config.layout.clone());
    router.set_local_display(local_display.width, local_display.height);
    router.set_remote_display(remote_display.width, remote_display.height);

    println!("bridge_smoke: input_owner={}", config.node_name);
    println!(
        "local_display={}x{} remote_display={}x{} remote_edge={:?}",
        local_display.width,
        local_display.height,
        remote_display.width,
        remote_display.height,
        config.layout.remote_edge
    );

    let receiver_hello = PeerMessage::Hello {
        node_name: "smoke-receiver".to_string(),
        role: Role::Receiver,
        local_display: remote_display,
    };
    print_peer_message("receiver->owner", &receiver_hello)?;

    let script = [
        (
            "local-before-edge",
            InputEvent::MouseMove {
                x: local_display.width / 2.0,
                y: local_display.height / 2.0,
            },
        ),
        (
            "cross-edge",
            cross_edge_event(config.layout.remote_edge, local_display),
        ),
        (
            "remote-key-press",
            InputEvent::KeyPress {
                key: "KeyA".to_string(),
                text: Some("a".to_string()),
            },
        ),
        (
            "remote-key-release",
            InputEvent::KeyRelease {
                key: "KeyA".to_string(),
            },
        ),
    ];

    for (label, event) in script {
        let decision = router.handle_captured(event);
        println!("{label}: suppress_local={}", decision.suppress_local);
        for message in decision.messages {
            print_peer_message("owner->receiver", &message)?;
            print_receiver_effect(&message);
        }
    }

    Ok(())
}

pub async fn run_network(config: Config) -> Result<()> {
    if config.role != Role::InputOwner {
        bail!("bridge network smoke requires an input_owner config");
    }

    let listener = TcpListener::bind("127.0.0.1:0")
        .await
        .context("failed to bind loopback smoke listener")?;
    let listen_addr = listener.local_addr()?;
    let owner_config = loopback_owner_config(&config, listen_addr);
    let receiver_config = loopback_receiver_config(&config, listen_addr);

    println!("bridge_network_smoke: listen_addr={listen_addr}");

    let owner_task = tokio::spawn(async move {
        let (stream, remote_addr) = listener.accept().await?;
        println!("bridge_network_smoke: owner accepted {remote_addr}");
        network::peer_from_stream(&owner_config, stream).await
    });

    let receiver_stream = TcpStream::connect(listen_addr)
        .await
        .context("failed to connect loopback receiver")?;
    let mut receiver = network::peer_from_stream(&receiver_config, receiver_stream).await?;
    let mut owner = owner_task.await.context("owner task panicked")??;

    let owner_hello = recv_with_timeout(&mut receiver.inbound, "owner hello").await?;
    print_peer_message("owner->receiver", &owner_hello)?;
    let receiver_hello = recv_with_timeout(&mut owner.inbound, "receiver hello").await?;
    print_peer_message("receiver->owner", &receiver_hello)?;

    network::send(
        &owner.outbound,
        PeerMessage::Active {
            remote_active: true,
        },
    )
    .await?;
    network::send(
        &owner.outbound,
        PeerMessage::Input {
            event: InputEvent::MouseMove { x: 1.0, y: 2.0 },
        },
    )
    .await?;
    network::send(
        &owner.outbound,
        PeerMessage::Input {
            event: InputEvent::KeyPress {
                key: "KeyA".to_string(),
                text: Some("a".to_string()),
            },
        },
    )
    .await?;
    network::send(
        &owner.outbound,
        PeerMessage::Input {
            event: InputEvent::KeyRelease {
                key: "KeyA".to_string(),
            },
        },
    )
    .await?;

    for label in ["active", "mouse move", "key press", "key release"] {
        let message = recv_with_timeout(&mut receiver.inbound, label).await?;
        print_peer_message("owner->receiver", &message)?;
        print_receiver_effect(&message);
    }

    Ok(())
}

fn loopback_owner_config(config: &Config, listen_addr: SocketAddr) -> Config {
    Config {
        node_name: format!("{}-smoke-owner", config.node_name),
        role: Role::InputOwner,
        listen_addr: Some(listen_addr),
        peer_addr: None,
        layout: config.layout.clone(),
    }
}

fn loopback_receiver_config(config: &Config, peer_addr: SocketAddr) -> Config {
    Config {
        node_name: "smoke-receiver".to_string(),
        role: Role::Receiver,
        listen_addr: None,
        peer_addr: Some(peer_addr),
        layout: Layout {
            local_width: config.layout.remote_width,
            local_height: config.layout.remote_height,
            remote_width: config.layout.local_width,
            remote_height: config.layout.local_height,
            remote_edge: opposite_edge(config.layout.remote_edge),
        },
    }
}

fn opposite_edge(edge: Edge) -> Edge {
    match edge {
        Edge::Left => Edge::Right,
        Edge::Right => Edge::Left,
        Edge::Top => Edge::Bottom,
        Edge::Bottom => Edge::Top,
    }
}

async fn recv_with_timeout(
    inbound: &mut tokio::sync::mpsc::Receiver<PeerMessage>,
    label: &str,
) -> Result<PeerMessage> {
    time::timeout(Duration::from_secs(2), inbound.recv())
        .await
        .with_context(|| format!("timed out waiting for {label}"))?
        .with_context(|| format!("peer inbound closed while waiting for {label}"))
}

fn cross_edge_event(edge: Edge, local_display: DisplayGeometry) -> InputEvent {
    let middle_x = local_display.width / 2.0;
    let middle_y = local_display.height / 2.0;

    match edge {
        Edge::Right => InputEvent::MouseMove {
            x: local_display.width - 1.0,
            y: middle_y,
        },
        Edge::Left => InputEvent::MouseMove {
            x: 0.0,
            y: middle_y,
        },
        Edge::Top => InputEvent::MouseMove {
            x: middle_x,
            y: 0.0,
        },
        Edge::Bottom => InputEvent::MouseMove {
            x: middle_x,
            y: local_display.height - 1.0,
        },
    }
}

fn detected_display_or_config(fallback: DisplayGeometry, label: &str) -> DisplayGeometry {
    match platform::primary_display_geometry() {
        Ok(Some(display)) => {
            println!(
                "{label}: using detected primary display {}x{}",
                display.width, display.height
            );
            display
        }
        Ok(None) => {
            println!(
                "{label}: using config fallback display {}x{}",
                fallback.width, fallback.height
            );
            fallback
        }
        Err(error) => {
            println!(
                "{label}: failed to detect primary display ({error}); using config fallback {}x{}",
                fallback.width, fallback.height
            );
            fallback
        }
    }
}

fn print_peer_message(direction: &str, message: &PeerMessage) -> Result<()> {
    println!("{direction}: {}", serde_json::to_string(message)?);
    Ok(())
}

fn print_receiver_effect(message: &PeerMessage) {
    match message {
        PeerMessage::Input { event } => println!("receiver inject: {event:?}"),
        PeerMessage::Active { remote_active } => println!("receiver active: {remote_active}"),
        PeerMessage::Hello { .. } | PeerMessage::Heartbeat => {}
    }
}
