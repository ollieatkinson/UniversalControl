# 2026-06-06 Windows Native Local Routing Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `66ed778 Use native display size in peer hello`

## What Changed

- The input-owner router now prefers native primary display geometry for local edge detection.
- macOS/Windows native builds use the same display enumeration path as `cargo run -- probe displays`.
- Linux/WSL and native detection failures still fall back to configured `layout.local_width` and `layout.local_height`.
- The previous receiver hello behavior remains: remote dimensions are updated from the receiver's detected display size after connection.

## Why This Matters

The previous change made remote dimensions dynamic, but local edge detection still depended on input-owner config. A stale `local_width` or `local_height` could keep edge crossing from activating, or activate too early.

This change makes both sides of the bridge topology prefer runtime display evidence:

- local input-owner edge detection uses the input owner's detected primary display
- remote pointer mapping uses the receiver's detected primary display from hello

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
```

## Local Runtime Observation

WSL uses the stub backend, so this was unit-tested and cross-target checked. In WSL, local routing still falls back to config.

## Questions For Mac Side

- With macOS as input owner, does edge crossing occur at the display width reported by `cargo run -- probe displays`, even if config `local_width` is deliberately stale?
- With Windows as input owner, does native Windows display detection match `probe displays` once run from a native Windows terminal?
- Do local edge activation and receiver hello dimensions both match the latest redacted display observations?
