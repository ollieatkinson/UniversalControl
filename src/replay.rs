use std::{
    fs::File,
    io::{BufRead, BufReader},
    path::Path,
};

use anyhow::Result;

use crate::protocol::InputEvent;

pub const REPLAYABLE_MOUSE_BUTTON_NAMES: &[&str] = &["Left", "Right", "Middle"];

pub const REPLAYABLE_KEY_NAMES: &[&str] = &[
    "Alt",
    "AltGr",
    "Backspace",
    "CapsLock",
    "ControlLeft",
    "ControlRight",
    "Delete",
    "DownArrow",
    "End",
    "Escape",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
    "Home",
    "LeftArrow",
    "MetaLeft",
    "MetaRight",
    "PageDown",
    "PageUp",
    "Return",
    "RightArrow",
    "ShiftLeft",
    "ShiftRight",
    "Space",
    "Tab",
    "UpArrow",
    "PrintScreen",
    "ScrollLock",
    "Pause",
    "NumLock",
    "BackQuote",
    "Num1",
    "Num2",
    "Num3",
    "Num4",
    "Num5",
    "Num6",
    "Num7",
    "Num8",
    "Num9",
    "Num0",
    "Minus",
    "Equal",
    "KeyQ",
    "KeyW",
    "KeyE",
    "KeyR",
    "KeyT",
    "KeyY",
    "KeyU",
    "KeyI",
    "KeyO",
    "KeyP",
    "LeftBracket",
    "RightBracket",
    "KeyA",
    "KeyS",
    "KeyD",
    "KeyF",
    "KeyG",
    "KeyH",
    "KeyJ",
    "KeyK",
    "KeyL",
    "SemiColon",
    "Quote",
    "BackSlash",
    "IntlBackslash",
    "KeyZ",
    "KeyX",
    "KeyC",
    "KeyV",
    "KeyB",
    "KeyN",
    "KeyM",
    "Comma",
    "Dot",
    "Slash",
    "Insert",
    "KpReturn",
    "KpMinus",
    "KpPlus",
    "KpMultiply",
    "KpDivide",
    "Kp0",
    "Kp1",
    "Kp2",
    "Kp3",
    "Kp4",
    "Kp5",
    "Kp6",
    "Kp7",
    "Kp8",
    "Kp9",
    "KpDelete",
    "Function",
];

pub fn replay_events_dry_run(path: &Path) -> Result<usize> {
    let mut validated = 0usize;
    for (line_number, event) in read_input_events_jsonl(path)? {
        print_input_event(&event);
        validate_replayable_input_event(&event)
            .map_err(|error| anyhow::anyhow!("{}:{line_number}: {error}", path.display()))?;
        validated += 1;
    }
    Ok(validated)
}

pub fn read_input_events_jsonl(path: &Path) -> Result<Vec<(usize, InputEvent)>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut events = Vec::new();

    for (index, line) in reader.lines().enumerate() {
        let line_number = index + 1;
        let line = line?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let event: InputEvent = serde_json::from_str(trimmed)
            .map_err(|error| anyhow::anyhow!("{}:{line_number}: {error}", path.display()))?;
        events.push((line_number, event));
    }

    Ok(events)
}

pub fn validate_replayable_input_event(event: &InputEvent) -> Result<()> {
    match event {
        InputEvent::KeyPress { key, .. } | InputEvent::KeyRelease { key } => validate_key_name(key),
        InputEvent::ButtonPress { button } | InputEvent::ButtonRelease { button } => {
            validate_mouse_button_name(button)
        }
        InputEvent::MouseMove { .. } | InputEvent::Wheel { .. } => Ok(()),
    }
}

pub fn validate_key_name(value: &str) -> Result<()> {
    if REPLAYABLE_KEY_NAMES.contains(&value) {
        Ok(())
    } else {
        anyhow::bail!("unsupported key name: {value}")
    }
}

pub fn validate_mouse_button_name(value: &str) -> Result<()> {
    if REPLAYABLE_MOUSE_BUTTON_NAMES.contains(&value) {
        Ok(())
    } else {
        anyhow::bail!("unsupported mouse button name: {value}")
    }
}

pub fn print_input_event(event: &InputEvent) {
    match serde_json::to_string(event) {
        Ok(line) => println!("{line}"),
        Err(error) => eprintln!("failed to encode input event: {error}"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_supported_key_button_and_pointer_events() {
        let events = [
            InputEvent::KeyPress {
                key: "KeyA".to_string(),
                text: Some("a".to_string()),
            },
            InputEvent::KeyRelease {
                key: "Function".to_string(),
            },
            InputEvent::ButtonPress {
                button: "Left".to_string(),
            },
            InputEvent::ButtonRelease {
                button: "Middle".to_string(),
            },
            InputEvent::MouseMove { x: 1.0, y: 2.0 },
            InputEvent::Wheel {
                delta_x: 0,
                delta_y: -1,
            },
        ];

        for event in events {
            validate_replayable_input_event(&event).unwrap();
        }
    }

    #[test]
    fn rejects_unsupported_key_and_button_names() {
        let key_error = validate_replayable_input_event(&InputEvent::KeyRelease {
            key: "AudioVolumeUp".to_string(),
        })
        .unwrap_err()
        .to_string();
        assert_eq!(key_error, "unsupported key name: AudioVolumeUp");

        let button_error = validate_replayable_input_event(&InputEvent::ButtonPress {
            button: "Unknown(0)".to_string(),
        })
        .unwrap_err()
        .to_string();
        assert_eq!(button_error, "unsupported mouse button name: Unknown(0)");
    }
}
