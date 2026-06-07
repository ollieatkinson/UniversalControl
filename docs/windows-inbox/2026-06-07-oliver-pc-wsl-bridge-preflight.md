# 2026-06-07 Windows Bridge Preflight Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `c30b93b Observe TCP attempts during candidate ads`

## What Changed

- Added:
  - `cargo run -- --config configs/input-owner.example.toml preflight`
  - `cargo run -- --config configs/receiver.example.toml preflight`
- Preflight prints:
  - role and capture mode
  - configured local and remote display dimensions
  - detected primary display when available
  - effective local display used by bridge routing and hello fallback
  - listen or peer mode
  - warnings for missing native display detection and loopback-only addresses

## Why This Matters

The fallback bridge uses global capture and injection. A bad config can suppress
local input or fail to connect before useful evidence is collected. Preflight
gives both machines a cheap sanity check before running the daemon.

## Commands Run Locally

```sh
cargo run -- --config configs/input-owner.example.toml preflight
cargo run -- --config configs/receiver.example.toml preflight
```

## Local Runtime Observation

WSL uses the stub backend, so preflight correctly reports no detected primary
display and falls back to configured display dimensions. Native Windows and
macOS should report detected primary display geometry unless platform display
enumeration fails.

## Questions For Mac Side

- Does preflight on native macOS report `detected_primary_display=1710x1112` or the current `probe displays` dimensions?
- Does receiver preflight use `peer_mode=mdns_discovery` when `peer_addr` is omitted?
- Are there any warnings other than expected permission or display-detection notes?
