# 2026-06-06 Windows Peer Display Hello Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `bdb7a6c Reset input owner session on peer close`
- Integrated before commit: `ccb54ea Add macOS probe redaction and display fallback`

## What Changed

- `PeerMessage::Hello` now carries:
  - `node_name`
  - `role`
  - `local_display.width`
  - `local_display.height`
- The network layer fills `local_display` from the local config's `layout.local_width` and `layout.local_height`.
- The input-owner session accepts the receiver hello and updates its remote routing dimensions from the receiver's local display size.
- The configured `remote_width` and `remote_height` remain fallback values until receiver hello is received.

## Why This Matters

The two-machine bridge run previously required the receiver's display dimensions to be copied into the input-owner config before starting. That is easy to get wrong and blocks fast iteration with the Mac machine.

This change moves toward Universal Control-style dynamic topology: each peer announces its own local display size, and the input owner uses the receiver's announcement to route edge crossing and remote pointer coordinates.

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

- Does the input-owner log show the receiver role and local display size immediately after connection?
- With deliberately wrong `remote_width`/`remote_height` fallback values on the input-owner config, does the receiver hello correct the routed pointer coordinates?
- Do the `probe displays` primary width/height values match the `Hello.local_display` values in logs?
- For the latest Mac observation, does `local_display=1710x1112` match the receiver config used for the bridge run?
