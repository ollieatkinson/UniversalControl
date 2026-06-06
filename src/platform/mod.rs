#[cfg(any(target_os = "macos", target_os = "windows"))]
mod native;
#[cfg(not(any(target_os = "macos", target_os = "windows")))]
mod stub;

#[cfg(any(target_os = "macos", target_os = "windows"))]
pub use native::{
    CaptureEvent, PlatformCommand, primary_display_geometry, probe_displays, probe_grab,
    probe_inject_button, probe_inject_key, probe_inject_mouse, probe_inject_wheel, probe_listen,
    spawn,
};
#[cfg(not(any(target_os = "macos", target_os = "windows")))]
pub use stub::{
    CaptureEvent, PlatformCommand, primary_display_geometry, probe_displays, probe_grab,
    probe_inject_button, probe_inject_key, probe_inject_mouse, probe_inject_wheel, probe_listen,
    spawn,
};
