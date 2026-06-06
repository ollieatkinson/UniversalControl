# 2026-06-06 Windows Bridge Network Smoke Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `d5ad580 Add bridge routing smoke probe`
- Integrated before commit: `8d622a1 Add Universal Control session summarizer`

## What Changed

- Added `cargo run -- --config configs/input-owner.example.toml probe bridge-network-smoke`.
- The command creates a loopback input owner and receiver over `127.0.0.1`.
- It uses the real JSON-lines peer reader/writer tasks.
- It verifies:
  - owner hello reaches receiver
  - receiver hello reaches owner
  - owner-to-receiver `Active` reaches receiver
  - owner-to-receiver mouse move reaches receiver
  - owner-to-receiver `KeyA` press/release reaches receiver

## Why This Matters

The previous `bridge-smoke` command proved router output. This command proves the transport path that the real daemon uses after TCP connection setup. It is still platform-permission independent, so it can run before debugging native capture or injection.

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- --config configs/input-owner.example.toml probe bridge-network-smoke
```

## Local Runtime Observation

The local WSL run exchanged hello, active, mouse move, and key press/release messages over loopback TCP. WSL still uses config fallback for display geometry.

Observed local output included:

```text
bridge_network_smoke: listen_addr=127.0.0.1:<ephemeral>
bridge_network_smoke: owner accepted 127.0.0.1:<ephemeral>
owner->receiver: {"type":"hello","node_name":"windows-desk-smoke-owner","role":"input_owner","local_display":{"width":2560.0,"height":1440.0}}
receiver->owner: {"type":"hello","node_name":"smoke-receiver","role":"receiver","local_display":{"width":1728.0,"height":1117.0}}
owner->receiver: {"type":"active","remote_active":true}
owner->receiver: {"type":"input","event":{"kind":"mouse_move","x":1.0,"y":2.0}}
owner->receiver: {"type":"input","event":{"kind":"key_press","key":"KeyA","text":"a"}}
owner->receiver: {"type":"input","event":{"kind":"key_release","key":"KeyA"}}
```

## Questions For Mac Side

- Does `probe bridge-network-smoke` pass on macOS with the native detected display geometry in hello?
- Does the loopback output show both hello directions and all four owner-to-receiver messages?
- If macOS firewall prompts appear for loopback, record the prompt behavior before running the real two-machine daemon.
