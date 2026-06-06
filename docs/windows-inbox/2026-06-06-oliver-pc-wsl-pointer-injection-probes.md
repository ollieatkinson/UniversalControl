# 2026-06-06 Windows Pointer Injection Probe Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `869ff8f Add loopback bridge network smoke probe`

## What Changed

- Added native probe commands:
  - `cargo run -- probe inject-mouse --x 200 --y 200`
  - `cargo run -- probe inject-button --button Left`
  - `cargo run -- probe inject-wheel --delta-y 3`
- Existing key probe remains:
  - `cargo run -- probe inject --key KeyA`

## Why This Matters

The receiver side of the bridge must inject more than keys. Before a full two-machine run, each native platform should prove that pointer movement, mouse buttons, and wheel events can be synthesized in normal apps.

## Commands Run

```sh
cargo fmt --check
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- probe inject-mouse --x 200 --y 200
cargo run -- probe inject-button --button Left
cargo run -- probe inject-wheel --delta-y 3
```

## Local Runtime Observation

WSL uses the stub backend, so the new injection probes log native-only warnings locally. This change was cross-target checked for macOS and Windows but still needs native runtime testing.

## Questions For Mac Side

- Do `inject-mouse`, `inject-button`, and `inject-wheel` work after Accessibility/Input Monitoring permissions are granted?
- Does macOS require a logout/restart before pointer or wheel injection works?
- Are injected clicks blocked in any normal apps, secure input fields, or elevated/system prompts?
