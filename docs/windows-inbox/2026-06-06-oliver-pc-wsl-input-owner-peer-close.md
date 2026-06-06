# 2026-06-06 Windows Input Owner Peer Close Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `9490e42 Release receiver state when focus returns local`

## What Changed

- The input-owner session loop now reads inbound peer messages.
- If the receiver-side connection closes, the input owner ends the current session immediately.
- The next reconnect starts with a fresh `InputRouter`, so stale remote-active state is not carried across receiver disconnects.
- Inbound receiver `Hello` and heartbeat messages are accepted; unexpected receiver input messages are logged.

## Why This Matters

Before this change, the input owner could keep its router in remote-active mode until an outbound send or heartbeat noticed the broken connection. During that window, native capture could keep suppressing local input after the receiver had already gone away.

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
```

## Local Runtime Observation

WSL uses the stub backend, so this was unit-tested and cross-target checked, but not native-runtime tested.

## Questions For Mac Side

- During a two-machine run with the pointer remote, if the receiver process is killed, does the input-owner machine regain normal local input promptly?
- Does the input owner relisten and accept a restarted receiver without needing a daemon restart?
- Does the fresh router state avoid immediate remote suppression after reconnect until the pointer crosses the configured edge again?
