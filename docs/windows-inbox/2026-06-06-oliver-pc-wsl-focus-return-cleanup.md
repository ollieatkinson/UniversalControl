# 2026-06-06 Windows Focus Return Cleanup Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `68c2336 Add native display geometry probe`

## What Changed

- Receiver-side cleanup now runs when the input owner sends `remote_active=false`.
- Cleanup also runs on peer connection close and heartbeat failure.
- Cleanup releases:
  - any tracked keys/buttons injected during the active remote session
  - common latch-prone modifiers and mouse buttons

## Why This Matters

Previously, a planned pointer return from remote to local only logged `remote_active=false`. If the remote side had seen a held modifier or mouse button and the release was lost during focus transfer, the receiver could remain latched until the next reconnect/startup cleanup.

This change makes planned focus return use the same cleanup class as broken sessions.

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

- During a macOS receiver run, does returning the pointer to the local machine release Command/Option/Control/Shift if one was held while remote?
- Are duplicate release events for unpressed buttons/modifiers harmless on macOS native injection?
- During a forced disconnect while a key/button is held, does the receiver recover without stuck state?
