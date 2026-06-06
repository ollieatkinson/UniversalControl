# Prototype

`anykbflow` is currently a two-node software KVM prototype. It does not switch the Keychron Bluetooth profile. One machine owns the physical keyboard/mouse and forwards events to the other machine when the pointer crosses the configured edge.

## Roles

- `input_owner`: the machine with the physical keyboard/mouse attached. It captures local events, detects edge crossing, suppresses local delivery while the remote machine is active, and sends events to the receiver.
- `receiver`: the other machine. It connects to the input owner and injects received events.

Either macOS or Windows can be the `input_owner`.

## Run

On the machine with the keyboard/mouse:

```sh
cargo run -- --config configs/input-owner.example.toml
```

On the other machine:

```sh
cargo run -- --config configs/receiver.example.toml
```

Edit screen sizes and `remote_edge` before running. The input owner advertises `_anykbflow._tcp.local.` and the receiver discovers it automatically when `peer_addr` is omitted. Add `peer_addr = "host:24800"` to the receiver config to bypass discovery.

The peer protocol sends periodic heartbeat messages in both directions. If a peer disconnects, both roles re-enter their connection loop after a short delay: the input owner listens again and the receiver re-discovers or reconnects. The input owner listens for inbound peer closure so a disconnected receiver resets the session and starts the next connection with fresh routing state. The receiver releases common modifier keys and mouse buttons when a session starts, when focus returns local, and when a connection fails; it also releases any keys or buttons it injected and still considers pressed.

## Native Probes

Use these before the full two-machine run to verify the platform input layer.

Print display geometry for layout calibration:

```sh
cargo run -- probe displays
```

Use the primary display `width`/`height` values to fill `local_width`/`local_height` on the input-owner machine and `remote_width`/`remote_height` for the receiver. Record negative `x`/`y` origins in notes because they prove how the OS represents displays positioned left or above the primary display.

Print observed events without suppressing them:

```sh
cargo run -- probe listen --count 20
```

Grab events but allow them through:

```sh
cargo run -- probe grab --count 20
```

Grab and suppress events:

```sh
cargo run -- probe grab --count 20 --suppress
```

Inject one key press/release:

```sh
cargo run -- probe inject --key KeyA
```

Valid key names are the `rdev::Key` debug names, such as `KeyA`, `MetaLeft`, `ControlLeft`, `Alt`, `Space`, and `Return`.

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

- Peer setup is manual. The input owner listens; the receiver connects.
- No encryption or pairing yet.
- No clipboard sync yet.
- Reconnect is basic: the roles re-enter their connection loops, the input owner resets routing state on peer close, and receiver-side common latches plus tracked injected keys/buttons are released. Native runtime validation is still needed.
- The native input backend is based on `rdev` and should be treated as a spike layer, not the final platform code.
- Key mapping uses physical `rdev` key names. This should be replaced with platform scancode mapping once the Mac and Windows spike data is available.
- The Linux backend is intentionally no-op so the shared daemon can be checked in this workspace.

## Next Engineering Steps

1. Run `cargo run -- probe displays` on both macOS and Windows and commit redacted geometry summaries.
2. Run the input-owner role on Windows and receiver role on macOS.
3. Confirm capture, suppression, and injection behavior with Accessibility enabled on macOS.
4. Reverse the roles and test macOS as input owner.
5. Replace `rdev` mapping with explicit platform scancodes if modifiers/layouts are wrong.
6. Validate input-owner route reset and receiver focus/modifier cleanup on native macOS and Windows backends during planned return-to-local and forced disconnect.
7. Add TLS pairing once basic control is stable.
