# Prototype

`anykbflow` is currently a two-node software KVM prototype. It does not switch the Keychron Bluetooth profile. One machine owns the physical keyboard/mouse and forwards events to the other machine when the pointer crosses the configured edge.

## Roles

- `input_owner`: the machine with the physical keyboard/mouse attached. It captures local events, detects edge crossing, suppresses local delivery while the remote machine is active, and sends events to the receiver.
- `receiver`: the other machine. It connects to the input owner and injects received events.

Either macOS or Windows can be the `input_owner`.

## Run

Before starting the daemon, run preflight on each machine:

```sh
cargo run -- --config configs/input-owner.example.toml preflight
cargo run -- --config configs/receiver.example.toml preflight
```

Preflight validates the config, prints the role, peer mode, configured display
sizes, detected primary display size when available, effective local display,
and warnings such as unreachable loopback peer addresses or missing native
display detection. Fix warnings before a full two-machine run unless they are
expected for WSL or another stub backend.

On the machine with the keyboard/mouse:

```sh
cargo run -- --config configs/input-owner.example.toml
```

On the other machine:

```sh
cargo run -- --config configs/receiver.example.toml
```

Edit `local_width`, `local_height`, and `remote_edge` before running. Native macOS/Windows builds detect the primary display with the same display path used by `probe displays`; Linux/WSL and detection failures fall back to configured dimensions. The input owner uses detected local dimensions for edge routing, and the peer `Hello` message includes each side's detected primary display size so the input owner updates remote routing dimensions from the receiver after connection. The configured `remote_width` and `remote_height` remain fallback values until the receiver hello arrives. The input owner advertises `_anykbflow._tcp.local.` and the receiver discovers it automatically when `peer_addr` is omitted. Add `peer_addr = "host:24800"` to the receiver config to bypass discovery.

The peer protocol sends periodic heartbeat messages in both directions. If a peer disconnects, both roles re-enter their connection loop after a short delay: the input owner listens again and the receiver re-discovers or reconnects. The input owner listens for inbound peer closure so a disconnected receiver resets the session and starts the next connection with fresh routing state. The receiver releases common modifier keys and mouse buttons when a session starts, when focus returns local, and when a connection fails; it also releases any keys or buttons it injected and still considers pressed.

## Native Probes

Use these before the full two-machine run to verify the platform input layer.

Run a deterministic bridge routing smoke test without native input capture:

```sh
cargo run -- --config configs/input-owner.example.toml probe bridge-smoke
```

This loads the input-owner config, prints the same input-owner `Hello` shape used
by the peer protocol, simulates an edge crossing and `KeyA` press/release,
prints the JSON peer messages, and prints the receiver-side injection effect.
Native macOS/Windows builds use detected primary display size for local edge
routing and `Hello.local_display`; Linux/WSL falls back to the config.

Run a loopback TCP protocol smoke test:

```sh
cargo run -- --config configs/input-owner.example.toml probe bridge-network-smoke
```

This creates an in-process input owner and receiver over `127.0.0.1`, exchanges
peer `Hello` messages using the real JSON-lines network tasks, then sends
`Active`, mouse move, and `KeyA` press/release messages from owner to receiver.
Native macOS/Windows builds use detected primary display size in loopback
`Hello` messages; Linux/WSL falls back to the config.

Print display geometry for layout calibration:

```sh
cargo run -- probe displays
```

Use the primary display `width`/`height` values to fill `local_width`/`local_height` on each machine. Record negative `x`/`y` origins in notes because they prove how the OS represents displays positioned left or above the primary display.

Print observed events without suppressing them:

```sh
cargo run -- probe listen --count 20
cargo run -- probe listen-events --count 20
```

Grab events but allow them through:

```sh
cargo run -- probe grab --count 20
cargo run -- probe grab-events --count 20
```

Grab and suppress events:

```sh
cargo run -- probe grab --count 20 --suppress
cargo run -- probe grab-events --count 20 --suppress
```

Inject one key press/release:

```sh
cargo run -- probe inject --key KeyA
```

Inject pointer, button, and wheel events:

```sh
cargo run -- probe inject-mouse --x 200 --y 200
cargo run -- probe inject-button --button Left
cargo run -- probe inject-wheel --delta-y 3
```

Run pointer, button, and wheel injection only with a controlled foreground target
open. `inject-button` clicks at the current pointer location, and `inject-wheel`
scrolls the current focus target.

Valid key names are the `rdev::Key` debug names, such as `KeyA`, `MetaLeft`, `ControlLeft`, `Alt`, `Space`, and `Return`.
Valid button names are `Left`, `Right`, and `Middle`.
Unsupported key or button names fail explicitly instead of being replayed as an
`Unknown(0)` input. Treat that failure as a mapping gap to record from native
macOS or Windows spike data.

The `*-events` probes print normalized `InputEvent` JSON in the same shape sent over the bridge protocol.

Replay normalized events into the local injector:

```sh
mkdir -p artifacts
python scripts/capture-input-events.py --mode listen --count 20 --jsonl artifacts/input-events.jsonl
cargo run -- --config configs/input-owner.example.toml probe route-events --path artifacts/input-events.jsonl
cargo run -- probe replay-events --path artifacts/input-events.jsonl --dry-run
cargo run -- probe replay-events --path artifacts/input-events.jsonl --delay-ms 50
```

Use this with a controlled foreground target. The replay file is JSONL: one
serialized `InputEvent` per line. Blank lines and lines starting with `#` are
ignored, so short annotations can be added while preserving replayability.
The capture wrapper writes a JSONL artifact under `artifacts/` and a redacted
summary that omits typed text values. Run `route-events` with the input-owner
config to feed the captured events through the real edge router without native
hooks or network; default output redacts key text and reports local suppression,
remote activation/deactivation, and forwarded input counts. Run
`replay-events --dry-run` first to parse the JSONL file and validate native
key/button mapping without injecting synthetic input. The full replay then
validates the capture-to-injection path before a two-machine daemon run.

## Discovery Probes

Browse for Apple's CompanionLink service:

```sh
cargo run -- discovery browse --service _companion-link._tcp.local. --seconds 15 --redact
```

Advertise a controlled test service from Windows so macOS can check whether it appears in `dns-sd` and unified logs:

```sh
cargo run -- discovery advertise \
  --service _anykbflow-probe._tcp.local. \
  --instance "AnyKBFlow Probe" \
  --addr 192.0.2.10 \
  --port 49152 \
  --txt phase=visibility \
  --txt role=windows-probe \
  --seconds 60
```

Use the real LAN address for `--addr` during a two-machine test if automatic address selection does not produce a resolvable service. Do not commit unredacted stable addresses or TXT values.

The same default advertisement is available through the shorter alias:

```sh
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
```

The software-KVM fallback uses its own service:

```sh
_anykbflow._tcp.local.
```

This is deliberately separate from Apple's `_companion-link._tcp.local.` so bridge discovery does not pretend to be native Universal Control.

## macOS Permissions

The native backend uses global event grab/injection. macOS needs Accessibility permission for the terminal/app running `anykbflow`. If events are not captured or injected, add the launcher app under:

`System Settings -> Privacy & Security -> Accessibility`

Input Monitoring may also be required depending on macOS version and launch context.

## Windows Notes

The native backend uses global low-level hooks and synthetic input. Injection into elevated apps or the secure desktop can be blocked by Windows integrity levels. Running the daemon elevated may improve UAC/elevated-window behavior, but login-screen control is not expected from this user-space prototype.

## Current Limitations

- Peer setup is partly manual. The input owner listens; the receiver connects or discovers it with mDNS.
- No encryption or pairing yet.
- No clipboard sync yet.
- Reconnect is basic: the roles re-enter their connection loops, the input owner resets routing state on peer close, and receiver-side common latches plus tracked injected keys/buttons are released. Local and remote display dimensions prefer detected primary display geometry, but native runtime validation is still needed.
- The native input backend is based on `rdev` and should be treated as a spike layer, not the final platform code.
- Normalized event replay is a probe, not a security boundary. Do not replay untrusted event files.
- Key mapping uses physical `rdev` key names and rejects unknown names. This should be replaced with platform scancode mapping once the Mac and Windows spike data is available.
- The Linux backend is intentionally no-op so the shared daemon can be checked in this workspace.

## Next Engineering Steps

1. Run `preflight` on both machines with the intended configs.
2. Run `probe bridge-smoke` and `probe bridge-network-smoke` on both machines.
3. Run `cargo run -- probe displays` on macOS and `python scripts/windows/capture-display-probe.py` on Windows, then commit redacted geometry summaries.
4. Capture a short `listen-events` or `grab-events` JSONL file with `scripts/capture-input-events.py`, route it locally with `probe route-events`, and replay it on the other machine with `probe replay-events`.
5. Run the input-owner role on Windows and receiver role on macOS.
6. Confirm input-owner edge detection and receiver hello use the same primary display dimensions as `probe displays`.
7. Reverse the roles and test macOS as input owner.
8. Replace `rdev` mapping with explicit platform scancodes if modifiers/layouts are wrong.
9. Validate input-owner route reset and receiver focus/modifier cleanup on native macOS and Windows backends during planned return-to-local and forced disconnect.
10. Add TLS pairing once basic control is stable.
