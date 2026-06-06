# 2026-06-06 Windows Display Probe Implementation Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `7ab4792 Clarify Swift versus Rust choice`

## What Changed

- Added `cargo run -- probe displays`.
- Native macOS/Windows builds use `display-info` to print display geometry.
- Linux/WSL keeps a no-op stub so the shared checkout still builds and tests.
- Probe output includes:
  - display index
  - primary/built-in flags
  - display names
  - `x`, `y`, `width`, `height`
  - scale factor, rotation, refresh rate
  - physical size in millimeters when available
  - aggregate virtual bounds

## Why This Matters

The bridge router currently needs manual `local_width`, `local_height`, `remote_width`, `remote_height`, and `remote_edge` config. This probe gives both machines a repo-native way to capture the OS coordinate system before a two-machine run.

Negative display origins are especially important because they prove how the OS represents displays positioned left or above the primary display.

## Commands Run

```sh
cargo fmt --check
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
```

## Local Runtime Observation

WSL uses the stub backend, so `cargo run -- probe displays` cannot enumerate Windows displays from this shell. The command needs to be run from a native Windows terminal and from macOS.

## Questions For Mac Side

- Please run `cargo run -- probe displays` on macOS and commit a redacted observation under `docs/observations/`.
- Does the primary display size match the coordinate values reported by `probe listen` mouse move events?
- If an external monitor is attached, do displays left/above the primary appear with negative `x` or `y` origins?
