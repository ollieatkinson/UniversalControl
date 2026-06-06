# 2026-06-06 Windows Bridge Smoke Command Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `392acf5 Use native display size for local routing`

## What Changed

- Added `cargo run -- --config configs/input-owner.example.toml probe bridge-smoke`.
- The command loads an input-owner config and simulates:
  - a local pointer move before the configured edge
  - a pointer move across the configured edge
  - `KeyA` press/release while remote is active
- It prints:
  - local/remote display sizes used by the router
  - receiver hello JSON
  - owner-to-receiver JSON peer messages
  - receiver-side injection effects for forwarded input

## Why This Matters

This gives both machines a deterministic bridge check that does not depend on native input permissions, Accessibility, Input Monitoring, or Windows low-level hook behavior. It verifies the shared protocol/routing shape before we debug platform-specific capture and injection.

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- --config configs/input-owner.example.toml probe bridge-smoke
```

## Local Runtime Observation

WSL uses the stub display backend, so the smoke command falls back to config dimensions locally. It still proves the JSON protocol and router behavior.

Observed local output included:

```text
local input-owner: using config fallback display 2560x1440
local_display=2560x1440 remote_display=1728x1117 remote_edge=Right
receiver->owner: {"type":"hello",...}
owner->receiver: {"type":"active","remote_active":true}
owner->receiver: {"type":"input","event":{"kind":"mouse_move","x":1.0,"y":558.3877692842251}}
owner->receiver: {"type":"input","event":{"kind":"key_press","key":"KeyA","text":"a"}}
owner->receiver: {"type":"input","event":{"kind":"key_release","key":"KeyA"}}
```

## Questions For Mac Side

- Does `cargo run -- --config configs/input-owner.example.toml probe bridge-smoke` use the native detected Mac display size instead of config fallback?
- Do the printed `owner->receiver` JSON messages include `active=true`, a remote mouse move, `KeyA` press, and `KeyA` release?
- Does the remote mouse coordinate match the expected receiver display dimensions from `probe displays`?
