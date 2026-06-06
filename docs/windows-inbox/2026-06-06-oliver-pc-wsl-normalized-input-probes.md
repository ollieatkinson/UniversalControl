# 2026-06-06 Windows Normalized Input Probe Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `b7e696b Add pointer injection probes`

## What Changed

- Added native normalized capture probes:
  - `cargo run -- probe listen-events --count 20`
  - `cargo run -- probe grab-events --count 20`
  - `cargo run -- probe grab-events --count 20 --suppress`
- These print serialized `InputEvent` JSON, not raw `rdev::Event` debug output.

## Why This Matters

The bridge sends normalized `InputEvent` messages over the JSON-lines protocol. Raw `rdev` output is useful for backend debugging, but the two-machine run needs to know whether the mapped protocol events are correct:

- key names
- text payloads
- button names
- pointer coordinates
- wheel deltas

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- probe listen-events --count 1
cargo run -- probe grab-events --count 1
```

## Local Runtime Observation

WSL uses the stub backend, so the new normalized probes log native-only warnings locally. This change was cross-target checked for macOS and Windows but still needs native runtime testing.

## Questions For Mac Side

- Do `listen-events` and `grab-events` print JSON for Keychron key down/up events?
- Do Command, Option, Control, Shift, Fn/function row, and arrow keys map to useful `key` names?
- Does `text` appear only where expected for printable keys?
- Do mouse move coordinates match `probe displays` logical coordinates?
- Do wheel deltas have the expected sign and magnitude on macOS?
