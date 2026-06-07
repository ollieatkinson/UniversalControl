use std::{
    fs::File,
    io::{BufRead, BufReader},
    net::SocketAddr,
    path::Path,
    time::Duration,
};

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

    print_peer_message("owner->receiver", &network::hello_message(&config))?;

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

pub fn run_route_events(config: Config, path: &Path, raw: bool) -> Result<()> {
    if config.role != Role::InputOwner {
        bail!("route-events requires an input_owner config");
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
    let events = read_input_events_jsonl(path)?;
    let mut router = InputRouter::new(config.layout.clone());
    router.set_local_display(local_display.width, local_display.height);
    router.set_remote_display(remote_display.width, remote_display.height);

    let mut suppressed = 0usize;
    let mut unsuppressed = 0usize;
    let mut active_true = 0usize;
    let mut active_false = 0usize;
    let mut forwarded_inputs = 0usize;

    println!("route_events: input_owner={}", config.node_name);
    println!("source={}", path.display());
    println!("raw_output={raw}");
    println!(
        "local_display={}x{} remote_display={}x{} remote_edge={:?}",
        local_display.width,
        local_display.height,
        remote_display.width,
        remote_display.height,
        config.layout.remote_edge
    );
    print_peer_message("owner->receiver", &network::hello_message(&config))?;
    print_peer_message(
        "receiver->owner",
        &PeerMessage::Hello {
            node_name: "route-events-receiver".to_string(),
            role: Role::Receiver,
            local_display: remote_display,
        },
    )?;

    for (line_number, event) in events {
        let event_summary = describe_event(&event);
        let decision = router.handle_captured(event);
        if decision.suppress_local {
            suppressed += 1;
        } else {
            unsuppressed += 1;
        }

        println!(
            "input line {line_number}: event={event_summary} suppress_local={}",
            decision.suppress_local
        );
        for message in decision.messages {
            match &message {
                PeerMessage::Active {
                    remote_active: true,
                } => active_true += 1,
                PeerMessage::Active {
                    remote_active: false,
                } => active_false += 1,
                PeerMessage::Input { .. } => forwarded_inputs += 1,
                PeerMessage::Hello { .. } | PeerMessage::Heartbeat => {}
            }

            if raw {
                print_peer_message("owner->receiver", &message)?;
                print_receiver_effect(&message);
            } else {
                println!("owner->receiver: {}", describe_peer_message(&message));
                print_receiver_effect_redacted(&message);
            }
        }
    }

    println!("summary:");
    println!("  suppressed_events={suppressed}");
    println!("  unsuppressed_events={unsuppressed}");
    println!("  remote_activations={active_true}");
    println!("  remote_deactivations={active_false}");
    println!("  forwarded_inputs={forwarded_inputs}");

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

fn read_input_events_jsonl(path: &Path) -> Result<Vec<(usize, InputEvent)>> {
    let file = File::open(path).with_context(|| format!("failed to open {}", path.display()))?;
    let reader = BufReader::new(file);
    let mut events = Vec::new();

    for (index, line) in reader.lines().enumerate() {
        let line = line?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let event: InputEvent = serde_json::from_str(trimmed)
            .map_err(|error| anyhow::anyhow!("{}:{}: {error}", path.display(), index + 1))?;
        events.push((index + 1, event));
    }

    Ok(events)
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

fn print_receiver_effect_redacted(message: &PeerMessage) {
    match message {
        PeerMessage::Input { event } => println!("receiver inject: {}", describe_event(event)),
        PeerMessage::Active { remote_active } => println!("receiver active: {remote_active}"),
        PeerMessage::Hello { .. } | PeerMessage::Heartbeat => {}
    }
}

fn describe_peer_message(message: &PeerMessage) -> String {
    match message {
        PeerMessage::Hello {
            node_name,
            role,
            local_display,
        } => format!(
            "hello node={node_name} role={role:?} local_display={}x{}",
            local_display.width, local_display.height
        ),
        PeerMessage::Active { remote_active } => format!("active remote_active={remote_active}"),
        PeerMessage::Input { event } => format!("input {}", describe_event(event)),
        PeerMessage::Heartbeat => "heartbeat".to_string(),
    }
}

fn describe_event(event: &InputEvent) -> String {
    match event {
        InputEvent::KeyPress { key, text } => {
            format!(
                "key_press key={key} text_class={}",
                text_class(text.as_deref())
            )
        }
        InputEvent::KeyRelease { key } => format!("key_release key={key}"),
        InputEvent::ButtonPress { button } => format!("button_press button={button}"),
        InputEvent::ButtonRelease { button } => format!("button_release button={button}"),
        InputEvent::MouseMove { x, y } => format!("mouse_move x={x:.2} y={y:.2}"),
        InputEvent::Wheel { delta_x, delta_y } => {
            format!("wheel delta_x={delta_x} delta_y={delta_y}")
        }
    }
}

fn text_class(value: Option<&str>) -> String {
    match value {
        None => "none".to_string(),
        Some("") => "empty".to_string(),
        Some(value)
            if value.is_ascii() && value.chars().all(|character| !character.is_control()) =>
        {
            format!("printable_len_{}", value.len())
        }
        Some(value) => format!("non_ascii_or_control_len_{}", value.chars().count()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        fs,
        time::{SystemTime, UNIX_EPOCH},
    };

    #[test]
    fn reads_input_events_jsonl_comments_and_blank_lines() {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "anykbflow-route-events-{}-{nonce}.jsonl",
            std::process::id()
        ));
        fs::write(
            &path,
            "\n# comment\n{\"kind\":\"mouse_move\",\"x\":99.0,\"y\":25.0}\n{\"kind\":\"key_press\",\"key\":\"KeyA\",\"text\":\"a\"}\n",
        )
        .unwrap();

        let events = read_input_events_jsonl(&path).unwrap();
        fs::remove_file(&path).unwrap();

        assert_eq!(events.len(), 2);
        assert_eq!(events[0].0, 3);
        assert!(matches!(
            events[0].1,
            InputEvent::MouseMove { x: 99.0, y: 25.0 }
        ));
        assert!(matches!(
            events[1].1,
            InputEvent::KeyPress {
                ref key,
                text: Some(_)
            } if key == "KeyA"
        ));
    }

    #[test]
    fn redacts_key_press_text_in_event_summary() {
        let event = InputEvent::KeyPress {
            key: "KeyA".to_string(),
            text: Some("a".to_string()),
        };

        assert_eq!(
            describe_event(&event),
            "key_press key=KeyA text_class=printable_len_1"
        );
    }
}
