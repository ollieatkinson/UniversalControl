use std::{collections::HashSet, time::Duration};

use anyhow::Result;
use tokio::time;
use tracing::{debug, info, warn};

use crate::{
    config::{Config, Role},
    network,
    platform::{self, PlatformCommand},
    protocol::{DisplayGeometry, InputEvent, PeerMessage},
    router::InputRouter,
};

pub async fn run(config: Config) -> Result<()> {
    network::ensure_receiver_has_peer(&config)?;
    info!("starting {} as {:?}", config.node_name, config.role);

    let capture = config.role == Role::InputOwner;
    let (mut captured_rx, platform_tx) = platform::spawn(capture)?;

    loop {
        let mut peer = network::connect(&config).await?;
        let session_result = match config.role {
            Role::InputOwner => {
                run_input_owner(&config, &mut captured_rx, &mut peer.inbound, &peer.outbound).await
            }
            Role::Receiver => {
                run_receiver(&mut peer.inbound, &peer.outbound, platform_tx.clone()).await
            }
        };

        match session_result {
            Ok(()) => info!("peer session ended; reconnecting"),
            Err(error) => warn!("peer session failed: {error}; reconnecting"),
        }
        time::sleep(Duration::from_secs(2)).await;
    }
}

async fn run_input_owner(
    config: &Config,
    captured_rx: &mut tokio::sync::mpsc::Receiver<platform::CaptureEvent>,
    inbound: &mut tokio::sync::mpsc::Receiver<PeerMessage>,
    outbound: &tokio::sync::mpsc::Sender<PeerMessage>,
) -> Result<()> {
    let mut router = InputRouter::new(config.layout.clone());
    if let Some(local_display) = primary_display_geometry_for_router() {
        info!(
            "using detected input-owner local display {}x{} for edge routing",
            local_display.width, local_display.height
        );
        router.set_local_display(local_display.width, local_display.height);
    }
    let mut heartbeat = time::interval(Duration::from_secs(5));

    loop {
        tokio::select! {
            biased;

            message = inbound.recv() => {
                let Some(message) = message else {
                    warn!("peer connection closed");
                    return Ok(());
                };

                match message {
                    PeerMessage::Hello {
                        node_name,
                        role,
                        local_display,
                    } => {
                        info!(
                            "peer identified as {} ({:?}) local_display={}x{}",
                            node_name, role, local_display.width, local_display.height
                        );
                        if role == Role::Receiver {
                            router.set_remote_display(local_display.width, local_display.height);
                        } else {
                            warn!("expected receiver peer, got {:?}", role);
                        }
                    }
                    PeerMessage::Heartbeat => {}
                    PeerMessage::Active { remote_active } => {
                        debug!("receiver reported remote_active={remote_active}");
                    }
                    PeerMessage::Input { event } => {
                        warn!("receiver sent unexpected input event: {:?}", event);
                    }
                }
            }
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

fn primary_display_geometry_for_router() -> Option<DisplayGeometry> {
    match platform::primary_display_geometry() {
        Ok(display) => display,
        Err(error) => {
            warn!("failed to detect primary display geometry for router: {error}");
            None
        }
    }
}

async fn run_receiver(
    inbound: &mut tokio::sync::mpsc::Receiver<PeerMessage>,
    outbound: &tokio::sync::mpsc::Sender<PeerMessage>,
    platform_tx: tokio::sync::mpsc::Sender<PlatformCommand>,
) -> Result<()> {
    let mut heartbeat = time::interval(Duration::from_secs(5));
    let mut pressed_keys = HashSet::new();
    let mut pressed_buttons = HashSet::new();

    release_common_latches(&platform_tx).await;

    loop {
        tokio::select! {
            message = inbound.recv() => {
                let Some(message) = message else {
                    warn!("peer connection closed");
                    release_remote_state(&platform_tx, &mut pressed_keys, &mut pressed_buttons)
                        .await;
                    return Ok(());
                };

                match message {
                    PeerMessage::Hello {
                        node_name,
                        role,
                        local_display,
                    } => {
                        info!(
                            "peer identified as {} ({:?}) local_display={}x{}",
                            node_name, role, local_display.width, local_display.height
                        );
                        if role != Role::InputOwner {
                            warn!("expected input owner peer, got {:?}", role);
                        }
                    }
                    PeerMessage::Active { remote_active } => {
                        info!("remote_active={}", remote_active);
                        if !remote_active {
                            release_remote_state(
                                &platform_tx,
                                &mut pressed_keys,
                                &mut pressed_buttons,
                            )
                            .await;
                        }
                    }
                    PeerMessage::Input { event } => {
                        track_pressed(&event, &mut pressed_keys, &mut pressed_buttons);
                        platform_tx.send(PlatformCommand::Inject(event)).await?;
                    }
                    PeerMessage::Heartbeat => {}
                }
            }
            _ = heartbeat.tick() => {
                if let Err(error) = network::send(outbound, PeerMessage::Heartbeat).await {
                    warn!("heartbeat failed: {error}");
                    release_remote_state(&platform_tx, &mut pressed_keys, &mut pressed_buttons)
                        .await;
                    return Err(error);
                }
            }
        }
    }
}

async fn release_remote_state(
    platform_tx: &tokio::sync::mpsc::Sender<PlatformCommand>,
    pressed_keys: &mut HashSet<String>,
    pressed_buttons: &mut HashSet<String>,
) {
    release_pressed(platform_tx, pressed_keys, pressed_buttons).await;
    release_common_latches(platform_tx).await;
}

async fn release_common_latches(platform_tx: &tokio::sync::mpsc::Sender<PlatformCommand>) {
    for key in [
        "ShiftLeft",
        "ShiftRight",
        "ControlLeft",
        "ControlRight",
        "Alt",
        "AltGr",
        "MetaLeft",
        "MetaRight",
        "Function",
    ] {
        if platform_tx
            .send(PlatformCommand::Inject(InputEvent::KeyRelease {
                key: key.to_string(),
            }))
            .await
            .is_err()
        {
            warn!("platform command channel closed while releasing common keys");
            return;
        }
    }

    for button in ["Left", "Right", "Middle"] {
        if platform_tx
            .send(PlatformCommand::Inject(InputEvent::ButtonRelease {
                button: button.to_string(),
            }))
            .await
            .is_err()
        {
            warn!("platform command channel closed while releasing common buttons");
            return;
        }
    }
}

fn track_pressed(
    event: &InputEvent,
    pressed_keys: &mut HashSet<String>,
    pressed_buttons: &mut HashSet<String>,
) {
    match event {
        InputEvent::KeyPress { key, .. } => {
            pressed_keys.insert(key.clone());
        }
        InputEvent::KeyRelease { key } => {
            pressed_keys.remove(key);
        }
        InputEvent::ButtonPress { button } => {
            pressed_buttons.insert(button.clone());
        }
        InputEvent::ButtonRelease { button } => {
            pressed_buttons.remove(button);
        }
        InputEvent::MouseMove { .. } | InputEvent::Wheel { .. } => {}
    }
}

async fn release_pressed(
    platform_tx: &tokio::sync::mpsc::Sender<PlatformCommand>,
    pressed_keys: &mut HashSet<String>,
    pressed_buttons: &mut HashSet<String>,
) {
    for key in pressed_keys.drain() {
        if platform_tx
            .send(PlatformCommand::Inject(InputEvent::KeyRelease { key }))
            .await
            .is_err()
        {
            warn!("platform command channel closed while releasing keys");
            return;
        }
    }

    for button in pressed_buttons.drain() {
        if platform_tx
            .send(PlatformCommand::Inject(InputEvent::ButtonRelease {
                button,
            }))
            .await
            .is_err()
        {
            warn!("platform command channel closed while releasing buttons");
            return;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{Edge, Layout};
    use crate::protocol::DisplayGeometry;

    fn display(width: f64, height: f64) -> DisplayGeometry {
        DisplayGeometry { width, height }
    }

    fn input_owner_config() -> Config {
        Config {
            node_name: "owner-test".to_string(),
            role: Role::InputOwner,
            listen_addr: None,
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
    fn tracks_pressed_keys_and_buttons() {
        let mut keys = HashSet::new();
        let mut buttons = HashSet::new();

        track_pressed(
            &InputEvent::KeyPress {
                key: "ControlLeft".to_string(),
                text: None,
            },
            &mut keys,
            &mut buttons,
        );
        track_pressed(
            &InputEvent::ButtonPress {
                button: "Left".to_string(),
            },
            &mut keys,
            &mut buttons,
        );

        assert!(keys.contains("ControlLeft"));
        assert!(buttons.contains("Left"));

        track_pressed(
            &InputEvent::KeyRelease {
                key: "ControlLeft".to_string(),
            },
            &mut keys,
            &mut buttons,
        );
        track_pressed(
            &InputEvent::ButtonRelease {
                button: "Left".to_string(),
            },
            &mut keys,
            &mut buttons,
        );

        assert!(keys.is_empty());
        assert!(buttons.is_empty());
    }

    #[tokio::test]
    async fn releases_common_latches_on_session_start() {
        let (tx, mut rx) = tokio::sync::mpsc::channel(16);

        release_common_latches(&tx).await;
        drop(tx);

        let mut key_releases = Vec::new();
        let mut button_releases = Vec::new();
        while let Some(command) = rx.recv().await {
            match command {
                PlatformCommand::Inject(InputEvent::KeyRelease { key }) => key_releases.push(key),
                PlatformCommand::Inject(InputEvent::ButtonRelease { button }) => {
                    button_releases.push(button);
                }
                other => panic!("unexpected release cleanup command: {other:?}"),
            }
        }

        assert_eq!(
            key_releases,
            vec![
                "ShiftLeft",
                "ShiftRight",
                "ControlLeft",
                "ControlRight",
                "Alt",
                "AltGr",
                "MetaLeft",
                "MetaRight",
                "Function",
            ]
        );
        assert_eq!(button_releases, vec!["Left", "Right", "Middle"]);
    }

    #[tokio::test]
    async fn release_remote_state_releases_tracked_and_common_latches() {
        let (tx, mut rx) = tokio::sync::mpsc::channel(32);
        let mut keys = HashSet::from(["KeyA".to_string()]);
        let mut buttons = HashSet::from(["Left".to_string()]);

        release_remote_state(&tx, &mut keys, &mut buttons).await;
        drop(tx);

        let mut key_releases = Vec::new();
        let mut button_releases = Vec::new();
        while let Some(command) = rx.recv().await {
            match command {
                PlatformCommand::Inject(InputEvent::KeyRelease { key }) => key_releases.push(key),
                PlatformCommand::Inject(InputEvent::ButtonRelease { button }) => {
                    button_releases.push(button);
                }
                other => panic!("unexpected cleanup command: {other:?}"),
            }
        }

        assert!(keys.is_empty());
        assert!(buttons.is_empty());
        assert!(key_releases.contains(&"KeyA".to_string()));
        assert!(key_releases.contains(&"ShiftLeft".to_string()));
        assert!(key_releases.contains(&"MetaLeft".to_string()));
        assert!(button_releases.contains(&"Left".to_string()));
        assert!(button_releases.contains(&"Right".to_string()));
        assert!(button_releases.contains(&"Middle".to_string()));
    }

    #[tokio::test]
    async fn input_owner_ends_session_when_peer_inbound_closes() {
        let config = input_owner_config();
        let (_capture_tx, mut captured_rx) = tokio::sync::mpsc::channel(1);
        let (inbound_tx, mut inbound_rx) = tokio::sync::mpsc::channel(1);
        let (outbound_tx, _outbound_rx) = tokio::sync::mpsc::channel(1);

        drop(inbound_tx);

        tokio::time::timeout(
            Duration::from_millis(100),
            run_input_owner(&config, &mut captured_rx, &mut inbound_rx, &outbound_tx),
        )
        .await
        .expect("input owner did not notice peer closure")
        .expect("input owner peer closure should not be an error");
    }

    #[tokio::test]
    async fn input_owner_uses_receiver_display_from_hello() {
        let config = input_owner_config();
        let (capture_tx, mut captured_rx) = tokio::sync::mpsc::channel(2);
        let (inbound_tx, mut inbound_rx) = tokio::sync::mpsc::channel(2);
        let (outbound_tx, mut outbound_rx) = tokio::sync::mpsc::channel(4);

        let owner = tokio::spawn(async move {
            run_input_owner(&config, &mut captured_rx, &mut inbound_rx, &outbound_tx).await
        });

        inbound_tx
            .send(PeerMessage::Hello {
                node_name: "receiver-test".to_string(),
                role: Role::Receiver,
                local_display: display(300.0, 200.0),
            })
            .await
            .unwrap();

        let (suppress_tx, suppress_rx) = std::sync::mpsc::sync_channel(1);
        capture_tx
            .send(platform::CaptureEvent {
                event: InputEvent::MouseMove { x: 99.0, y: 49.0 },
                suppress: suppress_tx,
            })
            .await
            .unwrap();

        let mut saw_active = false;
        let mut saw_scaled_move = false;
        for _ in 0..4 {
            let message = tokio::time::timeout(Duration::from_millis(100), outbound_rx.recv())
                .await
                .unwrap()
                .unwrap();
            match message {
                PeerMessage::Active {
                    remote_active: true,
                } => saw_active = true,
                PeerMessage::Input {
                    event: InputEvent::MouseMove { x: 1.0, y },
                } if (y - 199.0).abs() < f64::EPSILON => saw_scaled_move = true,
                PeerMessage::Heartbeat => {}
                other => panic!("unexpected routed message: {other:?}"),
            }

            if saw_active && saw_scaled_move {
                break;
            }
        }

        assert!(saw_active);
        assert!(saw_scaled_move);
        assert!(suppress_rx.try_recv().unwrap());

        drop(capture_tx);
        drop(inbound_tx);
        owner
            .await
            .expect("input owner task panicked")
            .expect("input owner should stop cleanly when channels close");
    }
}
