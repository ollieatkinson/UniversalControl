use anyhow::{Result, bail};

use crate::{
    config::{Config, Edge, Role},
    platform,
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
