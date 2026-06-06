# macOS Handoff

Please pull this repo and test the native backend on macOS.

## Checks Needed

1. Build:

   ```sh
   cargo check
   ```

2. Probe passive capture:

   ```sh
   cargo run -- probe listen --count 20
   ```

3. Probe grab without suppression:

   ```sh
   cargo run -- probe grab --count 20
   ```

4. Probe grab with suppression:

   ```sh
   cargo run -- probe grab --count 20 --suppress
   ```

5. Probe injection:

   ```sh
   cargo run -- probe inject --key KeyA
   ```

6. Run as receiver with the Windows machine as input owner:

   ```sh
   cargo run -- --config configs/receiver.example.toml
   ```

7. Run as input owner with the Windows machine as receiver:

   ```sh
   cargo run -- --config configs/input-owner.example.toml
   ```

8. Record whether `rdev::grab` captures Keychron events.
9. Record whether returning `None` from the grab callback suppresses local keyboard and mouse delivery.
10. Record whether `rdev::simulate` injects into normal apps.
11. Record required macOS permissions and whether logout/restart was needed.
12. Record modifier behavior for Command, Option, Control, and Fn/function row.
13. Check whether Secure Input breaks capture in Terminal, password fields, browsers, and IDEs.

## Notes To Push Back

Add a dated note under `docs/mac-spikes/` with:

- macOS version.
- Keychron model and connection mode.
- Keyboard layout.
- Whether the Keychron is paired to one or both machines.
- Logs from both roles.
- Any changed code or mapping patches.
