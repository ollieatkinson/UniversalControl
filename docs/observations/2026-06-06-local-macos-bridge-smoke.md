# 2026-06-06 Local macOS Bridge Smoke

## Machine

- Host role: macOS-side runtime probe host
- Prior display observation: `docs/observations/2026-06-06-local-macos-display-probe.md`
- Node names: example-config values only

## Repo State

- Branch: `trunk`
- Base before local macOS observation: `869ff8f Add loopback bridge network smoke probe`

## Commands Run

```sh
cargo run -- probe displays
cargo run -- --config configs/input-owner.example.toml probe bridge-smoke
cargo run -- --config configs/input-owner.example.toml probe bridge-network-smoke
```

## Observation

`probe displays` reported the same single built-in display geometry as the prior
macOS observation:

```text
displays: 1
display_source: coregraphics-online-fallback
width=1710 height=1112 scale=2.00
virtual_bounds: x=0 y=0 width=1710 height=1112
```

The input-owner example config still contains stale local fallback dimensions:

```text
local_width=2560
local_height=1440
```

`probe bridge-smoke` used the detected macOS display size instead of those
fallback dimensions. Redacted excerpt:

```text
local input-owner: using detected primary display 1710x1112
local_display=1710x1112 remote_display=1728x1117 remote_edge=Right
owner->receiver: {"type":"hello","role":"input_owner","local_display":{"width":1710.0,"height":1112.0}}
receiver->owner: {"type":"hello","role":"receiver","local_display":{"width":1728.0,"height":1117.0}}
cross-edge: suppress_local=true
owner->receiver: {"type":"active","remote_active":true}
owner->receiver: {"type":"input","event":{"kind":"mouse_move","x":1.0,"y":558.5022502250224}}
owner->receiver: {"type":"input","event":{"kind":"key_press","key":"KeyA","text":"a"}}
owner->receiver: {"type":"input","event":{"kind":"key_release","key":"KeyA"}}
```

`probe bridge-network-smoke` also passed over loopback TCP using the real
JSON-lines peer reader/writer tasks. Redacted excerpt:

```text
bridge_network_smoke: listen_addr=127.0.0.1:<ephemeral>
bridge_network_smoke: owner accepted 127.0.0.1:<ephemeral>
owner->receiver: {"type":"hello","role":"input_owner","local_display":{"width":1710.0,"height":1112.0}}
receiver->owner: {"type":"hello","role":"receiver","local_display":{"width":1710.0,"height":1112.0}}
owner->receiver: {"type":"active","remote_active":true}
owner->receiver: {"type":"input","event":{"kind":"mouse_move","x":1.0,"y":2.0}}
owner->receiver: {"type":"input","event":{"kind":"key_press","key":"KeyA","text":"a"}}
owner->receiver: {"type":"input","event":{"kind":"key_release","key":"KeyA"}}
```

No firewall prompt appeared during the loopback run.

## Interpretation

- The macOS bridge-smoke path used native primary-display detection for local
  edge routing.
- The input-owner `Hello` message also used `1710x1112`, matching
  `probe displays` and overriding stale config fallback dimensions.
- The deterministic route produced `active=true`, a remote mouse move within
  the receiver display bounds, and `KeyA` press/release input messages.
- The loopback network smoke exchanged both hello directions plus active, mouse,
  and key messages over the real JSON-lines transport.
- Because both loopback endpoints ran on this Mac, both network-smoke hello
  messages used the same detected `1710x1112` display. That validates the native
  hello path on macOS, not a remote Windows display size.
- This validates shared bridge routing/protocol shape on macOS, but it does not
  prove native Apple Universal Control compatibility.

## Native Universal Control Gap

The preferred target remains native `UniversalControl.app` on macOS. This bridge
smoke only answers the software-KVM fallback's runtime topology question. The
native-first gaps are unchanged: Windows still needs to resolve this Mac's
`_companion-link._tcp` service, macOS still needs to observe a Windows-advertised
benign probe on the real LAN, and macOS still needs a controlled Windows-owned
`_companion-link._tcp` candidate run under `rapportd` and `UniversalControl`
logging.
