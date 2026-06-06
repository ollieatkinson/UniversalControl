# macOS Handoff

Please pull this repo and test the native backend on macOS.

## Checks Needed

1. Build:

   ```sh
   cargo check
   ```

2. Run as receiver with the Windows machine as input owner:

   ```sh
   cargo run -- --config configs/receiver.example.toml
   ```

3. Run as input owner with the Windows machine as receiver:

   ```sh
   cargo run -- --config configs/input-owner.example.toml
   ```

4. Record whether `rdev::grab` captures Keychron events.
5. Record whether returning `None` from the grab callback suppresses local keyboard and mouse delivery.
6. Record whether `rdev::simulate` injects into normal apps.
7. Record required macOS permissions and whether logout/restart was needed.
8. Record modifier behavior for Command, Option, Control, and Fn/function row.
9. Check whether Secure Input breaks capture in Terminal, password fields, browsers, and IDEs.

## Notes To Push Back

Add a dated note under `docs/mac-spikes/` with:

- macOS version.
- Keychron model and connection mode.
- Keyboard layout.
- Whether the Keychron is paired to one or both machines.
- Logs from both roles.
- Any changed code or mapping patches.

