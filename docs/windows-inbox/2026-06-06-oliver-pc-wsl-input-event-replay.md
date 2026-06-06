# 2026-06-06 Windows Input Event Replay Probe Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `c1dadca Add normalized input event probes`

## What Changed

- Added normalized event replay:
  - `cargo run -- probe replay-events --path artifacts/input-events.jsonl --delay-ms 50`
- Replay accepts the JSONL emitted by:
  - `cargo run -- probe listen-events --count 20`
  - `cargo run -- probe grab-events --count 20`
  - `cargo run -- probe grab-events --count 20 --suppress`
- Blank lines and lines starting with `#` are ignored.

## Why This Matters

The daemon already sends normalized `InputEvent` messages over the peer
protocol. Replay proves those captured events can drive the receiver-side
injector without needing a live network session. It lets macOS and Windows test
the hard capture and injection mapping in isolation before the full bridge run.

## Commands To Run Natively

Capture:

```sh
mkdir -p artifacts
cargo run -- probe listen-events --count 20 > artifacts/input-events.jsonl
```

Replay:

```sh
cargo run -- probe replay-events --path artifacts/input-events.jsonl --delay-ms 50
```

Only run replay with a controlled foreground target. Keyboard, click, pointer,
and wheel events are injected into the active desktop session.

## Local Runtime Observation

WSL uses the stub backend, so local replay only verifies CLI wiring and logs a
native-only warning. This change was cross-target checked for macOS and Windows
but still needs native runtime testing.

## Questions For Mac Side

- Does replaying a macOS-captured JSONL file reproduce key, pointer, button, and wheel events in a normal app?
- Does replaying a Windows-captured JSONL file on macOS expose any key name or modifier mapping gaps?
- Does replay require the same Accessibility/Input Monitoring permissions as the one-shot inject probes?
- Are pointer coordinates in replay aligned with `probe displays` and the later bridge router?
