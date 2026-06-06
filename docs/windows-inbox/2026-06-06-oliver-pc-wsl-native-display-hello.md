# 2026-06-06 Windows Native Display Hello Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `0c0a959 Exchange display size in peer hello`
- Integrated before commit: `72b1e1c Add paired Universal Control session capture`

## What Changed

- `PeerMessage::Hello.local_display` now prefers native primary display detection.
- macOS/Windows native builds use the same display enumeration path as `cargo run -- probe displays`.
- Linux/WSL and native detection failures fall back to configured `layout.local_width` and `layout.local_height`.
- The input owner still uses the receiver's hello to update remote routing dimensions.

## Why This Matters

The previous peer display hello reduced manual config copying, but the hello still came from config. That meant a stale receiver config could advertise the wrong screen size even after `probe displays` had the correct native value.

This change moves one step closer to Universal Control-style dynamic topology: each peer announces the display size it actually detects at runtime.

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
```

## Local Runtime Observation

WSL uses the stub backend, so this was unit-tested and cross-target checked. In WSL, hello display geometry still falls back to config.

## Questions For Mac Side

- In a native macOS run, does the hello log show `local_display=1710x1112` from the latest redacted display observation?
- If the receiver config deliberately uses stale `local_width`/`local_height`, does the native display detection override those stale config values in hello?
- On native Windows, does hello match `cargo run -- probe displays` once run from a Windows terminal rather than WSL?
