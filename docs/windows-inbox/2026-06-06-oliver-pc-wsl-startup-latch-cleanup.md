# 2026-06-06 Windows Startup Latch Cleanup Observation

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `0566e7d Release injected keys on receiver disconnect`
- Uncommitted changes at note time: receiver session-start latch cleanup

## What Changed

- Receiver sessions now inject releases for common modifiers and mouse buttons at session start.
- This covers a crash/restart case where tracked pressed-key state was lost before disconnect cleanup could run.
- The startup cleanup is limited to common latch-prone keys/buttons:
  - Shift, Control, Alt, Meta, AltGr, Function
  - Left, Right, Middle mouse buttons

## Commands Run

```sh
cargo fmt
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
```

## Observations

- Unit coverage now verifies the startup release sequence.
- This was not runtime-tested with native input because WSL uses the stub backend.
- Native testing should confirm that sending release events for unpressed modifiers/buttons is harmless on macOS and Windows.

## Evidence Files

- No raw logs committed.

## Questions For Mac Side

- Does the macOS native backend tolerate release events for unpressed Command/Option/Control/Shift keys?
- Should the Function/Fn release be kept, or does the Keychron/macOS path never expose it usefully?
- Are there other latch-prone keys on the Keychron model that should be included in startup cleanup?

