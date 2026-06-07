# 2026-06-06 Windows Reconnect Smoke Observation

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `9c8d7f1 Add bridge heartbeats and keepalive smoke note`
- Uncommitted changes at note time: bridge reconnect loop

## What Changed

- The daemon now runs peer sessions in a reconnect loop.
- After a session ends or fails, the input-owner role listens again.
- After a session ends or fails, the receiver role re-runs manual connect or mDNS discovery.
- The `_anyuniversalcontrol._tcp.local.` advertisement is guarded so it is registered once per process rather than on every reconnect.

## Commands Run

```sh
cargo fmt
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- --config configs/input-owner.example.toml
timeout 4 cargo run -- --config configs/receiver.example.toml
timeout 4 cargo run -- --config configs/receiver.example.toml
```

## Observations

- First receiver discovered `_anyuniversalcontrol._tcp.local.`, connected, and was stopped by `timeout`.
- Input-owner detected the broken peer on heartbeat and returned to `waiting for receiver`.
- Second receiver discovered the same service and connected successfully.
- Input-owner again detected the second broken peer and returned to `waiting for receiver`.
- This proves repeated local reconnect in WSL with the stub backend.

## Evidence Files

- No raw logs committed because they included a local WSL address.

## Questions For Mac Side

- Does the macOS receiver reconnect after its process is restarted while the Windows input-owner remains running?
- Does the Windows receiver reconnect after the macOS input-owner is restarted?
- Do stuck modifiers or remote-active focus state need explicit cleanup messages after reconnect on the native backends?

