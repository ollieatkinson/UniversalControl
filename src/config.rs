use std::{fs, net::SocketAddr, path::Path};

use anyhow::{Context, Result, bail};
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub node_name: String,
    pub role: Role,
    pub listen_addr: Option<SocketAddr>,
    pub peer_addr: Option<SocketAddr>,
    pub layout: Layout,
}

#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Role {
    InputOwner,
    Receiver,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Layout {
    pub local_width: f64,
    pub local_height: f64,
    pub remote_width: f64,
    pub remote_height: f64,
    pub remote_edge: Edge,
}

#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Edge {
    Left,
    Right,
    Top,
    Bottom,
}

impl Config {
    pub fn load(path: &Path) -> Result<Self> {
        let body = fs::read_to_string(path)
            .with_context(|| format!("failed to read config {}", path.display()))?;
        let config: Self = toml::from_str(&body)
            .with_context(|| format!("failed to parse config {}", path.display()))?;
        config.validate()?;
        Ok(config)
    }

    fn validate(&self) -> Result<()> {
        if self.node_name.trim().is_empty() {
            bail!("node_name must not be empty");
        }

        match self.role {
            Role::InputOwner if self.listen_addr.is_none() => {
                bail!("input_owner role requires listen_addr");
            }
            Role::Receiver => {}
            _ => {}
        }

        if self.layout.local_width <= 0.0
            || self.layout.local_height <= 0.0
            || self.layout.remote_width <= 0.0
            || self.layout.remote_height <= 0.0
        {
            bail!("layout dimensions must be positive");
        }

        Ok(())
    }
}
