# 2026-06-06 Windows Heartbeat Smoke Observation

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `1c336cd Add AnyUniversalControl mDNS peer discovery`
- Uncommitted changes at note time: heartbeat and stub keepalive

## What Changed

- Added periodic `Heartbeat` messages in both directions over the existing JSON-lines peer protocol.
- Kept the non-native stub capture channel open so Linux/WSL smoke tests do not immediately terminate the input-owner daemon.

## Commands Run

```sh
cargo fmt
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- --config configs/input-owner.example.toml
timeout 8 cargo run -- --config configs/receiver.example.toml
```

## Observations

- The receiver discovered `_anyuniversalcontrol._tcp.local.` and connected to the input owner.
- The receiver stayed connected until the `timeout 8` wrapper stopped it.
- The input owner observed the peer close and logged a broken pipe on the next heartbeat write.
- This proves local discovery, TCP connection, idle-session survival, and dead-peer write detection in WSL.
- This does not prove native macOS/Windows input capture or injection.

## Evidence Files

- No raw logs committed because they included a local WSL address.

## Questions For Mac Side

- Does the macOS receiver stay connected with `peer_addr` omitted when the Windows input-owner daemon is running?
- When the macOS receiver is stopped, does the Windows side detect the broken connection on heartbeat?
- Once native input permissions are granted, do heartbeats continue while no mouse/keyboard events are being forwarded?

