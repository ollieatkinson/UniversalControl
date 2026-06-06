# 2026-06-06 Windows Bridge Discovery Observation

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2
- Firewall profile: Private

## Repo State

- Branch: `trunk`
- Base commit before this change: `ab97841 Add mDNS discovery probes and Windows report`
- Uncommitted changes at note time: AnyKBFlow bridge mDNS auto-discovery

## What Changed

- The input-owner role now advertises `_anykbflow._tcp.local.` after successfully binding its TCP listener.
- The receiver role can omit `peer_addr`; it browses `_anykbflow._tcp.local.` and connects to the first resolved input owner.
- Manual `peer_addr` remains supported and bypasses discovery.

## Commands Run

```sh
cargo fmt
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- --config configs/input-owner.example.toml
cargo run -- --config configs/receiver.example.toml
```

## Observations

- The input-owner role advertised `windows-desk._anykbflow._tcp.local.` on port `24800`.
- The receiver role, with `peer_addr` omitted, discovered that service and connected successfully.
- The advertised WSL address was redacted from this note.
- Because this was run on Linux/WSL, native capture/injection was stubbed; this test proves discovery and TCP connection only, not real keyboard/mouse transfer.

## Evidence Files

- No raw output committed because it included a local WSL address.

## Questions For Mac Side

- Does macOS resolve `_anykbflow._tcp.local.` when the Windows/input-owner daemon is running?
- Can the macOS receiver connect with `peer_addr` omitted?
- Does macOS require firewall prompts or extra permissions for the receiver role beyond Accessibility/Input Monitoring needed by native input probes?

