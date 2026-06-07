use anyhow::Result;
use std::path::Path;
use tokio::sync::mpsc;
use tracing::{info, warn};

use crate::{
    protocol::{DisplayGeometry, InputEvent},
    replay,
};

#[derive(Debug)]
pub struct CaptureEvent {
    pub event: InputEvent,
    pub suppress: std::sync::mpsc::SyncSender<bool>,
}

#[derive(Debug)]
pub enum PlatformCommand {
    Inject(InputEvent),
}

pub fn spawn(
    capture: bool,
) -> Result<(mpsc::Receiver<CaptureEvent>, mpsc::Sender<PlatformCommand>)> {
    let (capture_tx, capture_rx) = mpsc::channel(256);
    let (command_tx, mut command_rx) = mpsc::channel(256);

    if capture {
        warn!("native capture is not available on this target; macOS/Windows use rdev backend");
    } else {
        info!("running with injection-only no-op platform backend");
    }

    tokio::spawn(async move {
        while let Some(command) = command_rx.recv().await {
            match command {
                PlatformCommand::Inject(event) => {
                    info!("stub injection ignored: {:?}", event);
                }
            }
        }
    });

    tokio::spawn(async move {
        let _capture_tx = capture_tx;
        std::future::pending::<()>().await;
    });

    Ok((capture_rx, command_tx))
}

pub fn probe_listen(_count: usize) -> Result<()> {
    warn!("probe listen is only available on macOS and Windows");
    Ok(())
}

pub fn probe_listen_events(_count: usize) -> Result<()> {
    warn!("probe listen-events is only available on macOS and Windows");
    Ok(())
}

pub fn probe_displays() -> Result<()> {
    warn!("probe displays is only available on macOS and Windows");
    Ok(())
}

pub fn primary_display_geometry() -> Result<Option<DisplayGeometry>> {
    Ok(None)
}

pub fn probe_grab(_count: usize, _suppress: bool) -> Result<()> {
    warn!("probe grab is only available on macOS and Windows");
    Ok(())
}

pub fn probe_grab_events(_count: usize, _suppress: bool) -> Result<()> {
    warn!("probe grab-events is only available on macOS and Windows");
    Ok(())
}

pub fn probe_replay_events(path: &Path, _delay_ms: u64, dry_run: bool) -> Result<()> {
    if !dry_run {
        anyhow::bail!(
            "probe replay-events injection is only available on macOS and Windows; use --dry-run to validate JSONL mapping on this target"
        );
    }

    warn!(
        "probe replay-events --dry-run is validating JSONL only; native injection is unavailable on this target"
    );
    let validated = replay::replay_events_dry_run(path)?;
    eprintln!("validated {validated} normalized input events");
    Ok(())
}

pub fn probe_inject_key(_key: &str) -> Result<()> {
    warn!("probe inject is only available on macOS and Windows");
    Ok(())
}

pub fn probe_inject_mouse(_x: f64, _y: f64) -> Result<()> {
    warn!("probe inject-mouse is only available on macOS and Windows");
    Ok(())
}

pub fn probe_inject_button(_button: &str) -> Result<()> {
    warn!("probe inject-button is only available on macOS and Windows");
    Ok(())
}

pub fn probe_inject_wheel(_delta_x: i64, _delta_y: i64) -> Result<()> {
    warn!("probe inject-wheel is only available on macOS and Windows");
    Ok(())
}
