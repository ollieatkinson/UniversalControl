use anyhow::Result;
use tokio::sync::mpsc;
use tracing::{info, warn};

use crate::protocol::InputEvent;

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
    let (_capture_tx, capture_rx) = mpsc::channel(256);
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

    Ok((capture_rx, command_tx))
}

pub fn probe_listen(_count: usize) -> Result<()> {
    warn!("probe listen is only available on macOS and Windows");
    Ok(())
}

pub fn probe_grab(_count: usize, _suppress: bool) -> Result<()> {
    warn!("probe grab is only available on macOS and Windows");
    Ok(())
}

pub fn probe_inject_key(_key: &str) -> Result<()> {
    warn!("probe inject is only available on macOS and Windows");
    Ok(())
}
