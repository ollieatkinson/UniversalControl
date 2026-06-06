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

Edit `peer_addr`, screen sizes, and `remote_edge` before running.

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
- The native input backend is based on `rdev` and should be treated as a spike layer, not the final platform code.
- Key mapping uses physical `rdev` key names. This should be replaced with platform scancode mapping once the Mac and Windows spike data is available.
- The Linux backend is intentionally no-op so the shared daemon can be checked in this workspace.

## Next Engineering Steps

1. Run the input-owner role on Windows and receiver role on macOS.
2. Confirm capture, suppression, and injection behavior with Accessibility enabled on macOS.
3. Reverse the roles and test macOS as input owner.
4. Replace `rdev` mapping with explicit platform scancodes if modifiers/layouts are wrong.
5. Add reconnect and heartbeat handling.
6. Add TLS pairing once basic control is stable.
