use std::{sync::mpsc as std_mpsc, thread, time::Duration};

use anyhow::Result;
use rdev::{Button, Event, EventType, Key};
use tokio::sync::mpsc;
use tracing::{info, warn};

use crate::protocol::InputEvent;

#[derive(Debug)]
pub struct CaptureEvent {
    pub event: InputEvent,
    pub suppress: std_mpsc::SyncSender<bool>,
}

#[derive(Debug)]
pub enum PlatformCommand {
    Inject(InputEvent),
}

pub fn spawn(
    capture: bool,
) -> Result<(mpsc::Receiver<CaptureEvent>, mpsc::Sender<PlatformCommand>)> {
    let (capture_tx, capture_rx) = mpsc::channel::<CaptureEvent>(256);
    let (command_tx, mut command_rx) = mpsc::channel::<PlatformCommand>(256);

    if capture {
        let tx = capture_tx.clone();
        thread::spawn(move || {
            info!("starting native input grab loop");
            let result = rdev::grab(move |event: Event| {
                let Some(input) = from_rdev_event(&event) else {
                    return Some(event);
                };

                let (suppress_tx, suppress_rx) = std_mpsc::sync_channel(1);
                let capture = CaptureEvent {
                    event: input,
                    suppress: suppress_tx,
                };

                if tx.blocking_send(capture).is_err() {
                    return Some(event);
                }

                match suppress_rx.recv_timeout(Duration::from_millis(20)) {
                    Ok(true) => None,
                    Ok(false) => Some(event),
                    Err(_) => Some(event),
                }
            });

            if let Err(error) = result {
                warn!("native input grab loop exited: {:?}", error);
            }
        });
    }

    tokio::spawn(async move {
        while let Some(command) = command_rx.recv().await {
            match command {
                PlatformCommand::Inject(event) => {
                    if let Err(error) = inject(event) {
                        warn!("failed to inject input event: {:?}", error);
                    }
                }
            }
        }
    });

    Ok((capture_rx, command_tx))
}

fn from_rdev_event(event: &Event) -> Option<InputEvent> {
    match event.event_type {
        EventType::KeyPress(key) => Some(InputEvent::KeyPress {
            key: format!("{key:?}"),
            text: event.name.clone(),
        }),
        EventType::KeyRelease(key) => Some(InputEvent::KeyRelease {
            key: format!("{key:?}"),
        }),
        EventType::ButtonPress(button) => Some(InputEvent::ButtonPress {
            button: format!("{button:?}"),
        }),
        EventType::ButtonRelease(button) => Some(InputEvent::ButtonRelease {
            button: format!("{button:?}"),
        }),
        EventType::MouseMove { x, y } => Some(InputEvent::MouseMove { x, y }),
        EventType::Wheel { delta_x, delta_y } => Some(InputEvent::Wheel { delta_x, delta_y }),
    }
}

fn inject(event: InputEvent) -> Result<()> {
    let event_type = match event {
        InputEvent::KeyPress { key, .. } => EventType::KeyPress(parse_key(&key)),
        InputEvent::KeyRelease { key } => EventType::KeyRelease(parse_key(&key)),
        InputEvent::ButtonPress { button } => EventType::ButtonPress(parse_button(&button)),
        InputEvent::ButtonRelease { button } => EventType::ButtonRelease(parse_button(&button)),
        InputEvent::MouseMove { x, y } => EventType::MouseMove { x, y },
        InputEvent::Wheel { delta_x, delta_y } => EventType::Wheel { delta_x, delta_y },
    };

    rdev::simulate(&event_type).map_err(|error| anyhow::anyhow!("{error}"))
}

fn parse_button(value: &str) -> Button {
    match value {
        "Left" => Button::Left,
        "Right" => Button::Right,
        "Middle" => Button::Middle,
        _ => Button::Unknown(0),
    }
}

fn parse_key(value: &str) -> Key {
    match value {
        "Alt" => Key::Alt,
        "AltGr" => Key::AltGr,
        "Backspace" => Key::Backspace,
        "CapsLock" => Key::CapsLock,
        "ControlLeft" => Key::ControlLeft,
        "ControlRight" => Key::ControlRight,
        "Delete" => Key::Delete,
        "DownArrow" => Key::DownArrow,
        "End" => Key::End,
        "Escape" => Key::Escape,
        "F1" => Key::F1,
        "F2" => Key::F2,
        "F3" => Key::F3,
        "F4" => Key::F4,
        "F5" => Key::F5,
        "F6" => Key::F6,
        "F7" => Key::F7,
        "F8" => Key::F8,
        "F9" => Key::F9,
        "F10" => Key::F10,
        "F11" => Key::F11,
        "F12" => Key::F12,
        "Home" => Key::Home,
        "LeftArrow" => Key::LeftArrow,
        "MetaLeft" => Key::MetaLeft,
        "MetaRight" => Key::MetaRight,
        "PageDown" => Key::PageDown,
        "PageUp" => Key::PageUp,
        "Return" => Key::Return,
        "RightArrow" => Key::RightArrow,
        "ShiftLeft" => Key::ShiftLeft,
        "ShiftRight" => Key::ShiftRight,
        "Space" => Key::Space,
        "Tab" => Key::Tab,
        "UpArrow" => Key::UpArrow,
        "PrintScreen" => Key::PrintScreen,
        "ScrollLock" => Key::ScrollLock,
        "Pause" => Key::Pause,
        "NumLock" => Key::NumLock,
        "BackQuote" => Key::BackQuote,
        "Num1" => Key::Num1,
        "Num2" => Key::Num2,
        "Num3" => Key::Num3,
        "Num4" => Key::Num4,
        "Num5" => Key::Num5,
        "Num6" => Key::Num6,
        "Num7" => Key::Num7,
        "Num8" => Key::Num8,
        "Num9" => Key::Num9,
        "Num0" => Key::Num0,
        "Minus" => Key::Minus,
        "Equal" => Key::Equal,
        "KeyQ" => Key::KeyQ,
        "KeyW" => Key::KeyW,
        "KeyE" => Key::KeyE,
        "KeyR" => Key::KeyR,
        "KeyT" => Key::KeyT,
        "KeyY" => Key::KeyY,
        "KeyU" => Key::KeyU,
        "KeyI" => Key::KeyI,
        "KeyO" => Key::KeyO,
        "KeyP" => Key::KeyP,
        "LeftBracket" => Key::LeftBracket,
        "RightBracket" => Key::RightBracket,
        "KeyA" => Key::KeyA,
        "KeyS" => Key::KeyS,
        "KeyD" => Key::KeyD,
        "KeyF" => Key::KeyF,
        "KeyG" => Key::KeyG,
        "KeyH" => Key::KeyH,
        "KeyJ" => Key::KeyJ,
        "KeyK" => Key::KeyK,
        "KeyL" => Key::KeyL,
        "SemiColon" => Key::SemiColon,
        "Quote" => Key::Quote,
        "BackSlash" => Key::BackSlash,
        "IntlBackslash" => Key::IntlBackslash,
        "KeyZ" => Key::KeyZ,
        "KeyX" => Key::KeyX,
        "KeyC" => Key::KeyC,
        "KeyV" => Key::KeyV,
        "KeyB" => Key::KeyB,
        "KeyN" => Key::KeyN,
        "KeyM" => Key::KeyM,
        "Comma" => Key::Comma,
        "Dot" => Key::Dot,
        "Slash" => Key::Slash,
        "Insert" => Key::Insert,
        "KpReturn" => Key::KpReturn,
        "KpMinus" => Key::KpMinus,
        "KpPlus" => Key::KpPlus,
        "KpMultiply" => Key::KpMultiply,
        "KpDivide" => Key::KpDivide,
        "Kp0" => Key::Kp0,
        "Kp1" => Key::Kp1,
        "Kp2" => Key::Kp2,
        "Kp3" => Key::Kp3,
        "Kp4" => Key::Kp4,
        "Kp5" => Key::Kp5,
        "Kp6" => Key::Kp6,
        "Kp7" => Key::Kp7,
        "Kp8" => Key::Kp8,
        "Kp9" => Key::Kp9,
        "KpDelete" => Key::KpDelete,
        "Function" => Key::Function,
        _ => Key::Unknown(0),
    }
}
