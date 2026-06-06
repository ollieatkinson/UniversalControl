#[cfg(any(target_os = "macos", target_os = "windows"))]
mod native;
#[cfg(not(any(target_os = "macos", target_os = "windows")))]
mod stub;

#[cfg(any(target_os = "macos", target_os = "windows"))]
pub use native::{CaptureEvent, PlatformCommand, spawn};
#[cfg(not(any(target_os = "macos", target_os = "windows")))]
pub use stub::{CaptureEvent, PlatformCommand, spawn};
