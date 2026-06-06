use std::{
    process,
    sync::{
        Arc,
        atomic::{AtomicUsize, Ordering},
        mpsc as std_mpsc,
    },
    thread,
    time::Duration,
};

use anyhow::Result;
use display_info::DisplayInfo;
#[cfg(target_os = "macos")]
use objc2_core_graphics::{
    CGDirectDisplayID, CGDisplayBounds, CGDisplayCopyDisplayMode, CGDisplayIsBuiltin,
    CGDisplayIsMain, CGDisplayMode, CGDisplayPixelsWide, CGDisplayRotation, CGDisplayScreenSize,
    CGError, CGGetOnlineDisplayList,
};
use rdev::{Button, Event, EventType, Key};
use tokio::sync::mpsc;
use tracing::{info, warn};

use crate::protocol::{DisplayGeometry, InputEvent};

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

pub fn probe_listen(count: usize) -> Result<()> {
    let remaining = Arc::new(AtomicUsize::new(count.max(1)));
    let remaining_events = Arc::clone(&remaining);

    eprintln!("listening for {} native input events", count.max(1));
    rdev::listen(move |event: Event| {
        eprintln!("{event:?}");
        if remaining_events.fetch_sub(1, Ordering::SeqCst) <= 1 {
            process::exit(0);
        }
    })
    .map_err(|error| anyhow::anyhow!("{error:?}"))
}

pub fn probe_displays() -> Result<()> {
    let (displays, source) = display_infos()?;

    println!("displays: {}", displays.len());
    println!("display_source: {source}");
    println!(
        "| index | primary | builtin | name | friendly_name | x | y | width | height | scale | rotation | hz | width_mm | height_mm |"
    );
    println!(
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    );

    for (index, display) in displays.iter().enumerate() {
        println!(
            "| {index} | {} | {} | {} | {} | {} | {} | {} | {} | {:.2} | {:.0} | {:.2} | {} | {} |",
            display.is_primary,
            display.is_builtin,
            markdown_cell(&display.name),
            markdown_cell(&display.friendly_name),
            display.x,
            display.y,
            display.width,
            display.height,
            display.scale_factor,
            display.rotation,
            display.frequency,
            display.width_mm,
            display.height_mm,
        );
    }

    if let Some((min_x, min_y, max_x, max_y)) = virtual_bounds(&displays) {
        println!();
        println!(
            "virtual_bounds: x={} y={} width={} height={}",
            min_x,
            min_y,
            max_x - min_x,
            max_y - min_y
        );
    }

    Ok(())
}

pub fn primary_display_geometry() -> Result<Option<DisplayGeometry>> {
    let (displays, _source) = display_infos()?;
    Ok(primary_display(&displays).map(|display| DisplayGeometry {
        width: display.width as f64,
        height: display.height as f64,
    }))
}

fn display_infos() -> Result<(Vec<DisplayInfo>, &'static str)> {
    let displays =
        DisplayInfo::all().map_err(|error| anyhow::anyhow!("failed to list displays: {error}"))?;

    #[cfg(target_os = "macos")]
    if displays.is_empty() {
        let online_displays = macos_online_displays()?;
        return Ok((online_displays, "coregraphics-online-fallback"));
    }

    Ok((displays, "display-info"))
}

fn primary_display(displays: &[DisplayInfo]) -> Option<&DisplayInfo> {
    displays
        .iter()
        .find(|display| display.is_primary)
        .or_else(|| displays.first())
}

#[cfg(target_os = "macos")]
fn macos_online_displays() -> Result<Vec<DisplayInfo>> {
    let max_displays: u32 = 16;
    let mut display_ids: Vec<CGDirectDisplayID> = vec![0; max_displays as usize];
    let mut display_count: u32 = 0;
    let error = unsafe {
        CGGetOnlineDisplayList(max_displays, display_ids.as_mut_ptr(), &mut display_count)
    };

    if error != CGError::Success {
        anyhow::bail!("CGGetOnlineDisplayList failed: {error:?}");
    }

    display_ids.truncate(display_count as usize);
    display_ids
        .into_iter()
        .map(macos_display_info)
        .collect::<Result<Vec<_>>>()
}

#[cfg(target_os = "macos")]
fn macos_display_info(id: CGDirectDisplayID) -> Result<DisplayInfo> {
    let bounds = CGDisplayBounds(id);
    let width = bounds.size.width.max(0.0) as u32;
    let height = bounds.size.height.max(0.0) as u32;
    let display_mode = CGDisplayCopyDisplayMode(id);
    let mode_pixel_width = CGDisplayMode::pixel_width(display_mode.as_deref());
    let pixel_width = if mode_pixel_width == 0 {
        CGDisplayPixelsWide(id)
    } else {
        mode_pixel_width
    };
    let scale_factor = if width == 0 {
        1.0
    } else {
        pixel_width as f32 / width as f32
    };
    let frequency = CGDisplayMode::refresh_rate(display_mode.as_deref()) as f32;
    let size_mm = CGDisplayScreenSize(id);

    Ok(DisplayInfo {
        id,
        name: format!("Display {id}"),
        friendly_name: format!("Online Display {id}"),
        raw_handle: id,
        x: bounds.origin.x as i32,
        y: bounds.origin.y as i32,
        width,
        height,
        width_mm: size_mm.width as i32,
        height_mm: size_mm.height as i32,
        rotation: CGDisplayRotation(id) as f32,
        frequency,
        scale_factor,
        is_primary: CGDisplayIsMain(id),
        is_builtin: CGDisplayIsBuiltin(id),
    })
}

pub fn probe_grab(count: usize, suppress: bool) -> Result<()> {
    let remaining = Arc::new(AtomicUsize::new(count.max(1)));
    let remaining_events = Arc::clone(&remaining);

    eprintln!(
        "grabbing {} native input events; suppress={}",
        count.max(1),
        suppress
    );
    rdev::grab(move |event: Event| {
        eprintln!("{event:?}");
        if remaining_events.fetch_sub(1, Ordering::SeqCst) <= 1 {
            process::exit(0);
        }

        if suppress { None } else { Some(event) }
    })
    .map_err(|error| anyhow::anyhow!("{error:?}"))
}

fn markdown_cell(value: &str) -> String {
    value.replace('|', "\\|")
}

fn virtual_bounds(displays: &[DisplayInfo]) -> Option<(i32, i32, i32, i32)> {
    let first = displays.first()?;
    let mut min_x = first.x;
    let mut min_y = first.y;
    let mut max_x = first.x + first.width as i32;
    let mut max_y = first.y + first.height as i32;

    for display in &displays[1..] {
        min_x = min_x.min(display.x);
        min_y = min_y.min(display.y);
        max_x = max_x.max(display.x + display.width as i32);
        max_y = max_y.max(display.y + display.height as i32);
    }

    Some((min_x, min_y, max_x, max_y))
}

pub fn probe_inject_key(key: &str) -> Result<()> {
    let key = parse_key(key);
    eprintln!("injecting {key:?} press/release");
    rdev::simulate(&EventType::KeyPress(key)).map_err(|error| anyhow::anyhow!("{error}"))?;
    thread::sleep(Duration::from_millis(50));
    rdev::simulate(&EventType::KeyRelease(key)).map_err(|error| anyhow::anyhow!("{error}"))?;
    Ok(())
}

pub fn probe_inject_mouse(x: f64, y: f64) -> Result<()> {
    eprintln!("injecting mouse move to x={x} y={y}");
    rdev::simulate(&EventType::MouseMove { x, y }).map_err(|error| anyhow::anyhow!("{error}"))
}

pub fn probe_inject_button(button: &str) -> Result<()> {
    let button = parse_button(button);
    eprintln!("injecting {button:?} button press/release");
    rdev::simulate(&EventType::ButtonPress(button)).map_err(|error| anyhow::anyhow!("{error}"))?;
    thread::sleep(Duration::from_millis(50));
    rdev::simulate(&EventType::ButtonRelease(button))
        .map_err(|error| anyhow::anyhow!("{error}"))?;
    Ok(())
}

pub fn probe_inject_wheel(delta_x: i64, delta_y: i64) -> Result<()> {
    eprintln!("injecting wheel delta_x={delta_x} delta_y={delta_y}");
    rdev::simulate(&EventType::Wheel { delta_x, delta_y })
        .map_err(|error| anyhow::anyhow!("{error}"))
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
