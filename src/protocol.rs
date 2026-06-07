use serde::{Deserialize, Serialize};

use crate::config::Role;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum PeerMessage {
    Hello {
        node_name: String,
        role: Role,
        local_display: DisplayGeometry,
        #[serde(skip_serializing_if = "Option::is_none")]
        auth: Option<HelloAuth>,
    },
    Active {
        remote_active: bool,
    },
    Input {
        event: InputEvent,
    },
    Heartbeat,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct HelloAuth {
    pub nonce: String,
    pub proof: String,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub struct DisplayGeometry {
    pub width: f64,
    pub height: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum InputEvent {
    KeyPress { key: String, text: Option<String> },
    KeyRelease { key: String },
    ButtonPress { button: String },
    ButtonRelease { button: String },
    MouseMove { x: f64, y: f64 },
    Wheel { delta_x: i64, delta_y: i64 },
}
