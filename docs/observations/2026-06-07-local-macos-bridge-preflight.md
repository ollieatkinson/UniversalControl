# 2026-06-07 Local macOS Bridge Preflight

## Machine

- Host role: macOS-side fallback bridge preflight host
- Prior display observation: `docs/observations/2026-06-06-local-macos-display-probe.md`
- Node names: example-config values only
- Display names: redacted

## Repo State

- Branch: `trunk`
- Base before local macOS observation: `0f1e697 Add mDNS watch summary comparer`

## Commands Run

```sh
cargo run -- probe displays
cargo run -- --config configs/input-owner.example.toml preflight
cargo run -- --config configs/receiver.example.toml preflight
```

## Observation

`probe displays` still reports one built-in display through the macOS
CoreGraphics online fallback:

```text
displays: 1
display_source: coregraphics-online-fallback
primary=true builtin=true x=0 y=0 width=1710 height=1112 scale=2.00
virtual_bounds: x=0 y=0 width=1710 height=1112
```

Input-owner preflight:

```text
preflight_status=ok
role=InputOwner
capture_enabled=true
configured_local_display=2560x1440
configured_remote_display=1728x1117
remote_edge=Right
detected_primary_display=1710x1112
effective_local_display=1710x1112
listen_addr=0.0.0.0:24800
advertises_service=_anykbflow._tcp.local.
peer_mode=listen
warnings=0
```

Receiver preflight:

```text
preflight_status=ok
role=Receiver
capture_enabled=false
configured_local_display=1728x1117
configured_remote_display=2560x1440
remote_edge=Left
detected_primary_display=1710x1112
effective_local_display=1710x1112
peer_addr=none
peer_mode=mdns_discovery
discovers_service=_anykbflow._tcp.local.
warnings=0
```

## Interpretation

- Native macOS preflight sees the same `1710x1112` primary display geometry as
  `probe displays`.
- Both example configs contain stale fallback dimensions, but preflight reports
  `effective_local_display=1710x1112`, matching the native display probe.
- Receiver preflight uses `peer_mode=mdns_discovery` when `peer_addr` is omitted.
- Neither example config emitted preflight warnings on this Mac.
- This answers the Mac-side preflight questions in
  `docs/windows-inbox/2026-06-07-oliver-pc-wsl-bridge-preflight.md`.

## Native Universal Control Gap

This is fallback bridge evidence only. It does not prove native macOS
`UniversalControl.app` admission for Windows. The native-first gaps remain the
Windows passive `_companion-link._tcp` browse, Windows-to-macOS benign mDNS
visibility, controlled minimal CompanionLink candidate capture, and shape-only
candidate comparison with Windows TCP observer output.
