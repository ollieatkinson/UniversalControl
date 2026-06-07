# AnyUniversalControl / Universal Control Spike

Date: 2026-06-06

## Goal

Make a Keychron keyboard usable across a macOS machine and a Windows machine with the same feel as Logitech Flow or macOS Universal Control: when the mouse crosses to the other computer, keyboard focus follows automatically.

The linked repository was checked before writing this:

- `https://github.com/ollieatkinson/UniversalControl.git`
- Local clone: `/home/oliver/src/github.com/ollieatkinson/UniversalControl`
- Current state on 2026-06-06: repository exists but is empty.

## Short Answer

The right solution is not to switch the Keychron's Bluetooth profile automatically. The practical solution is a software KVM: keep the keyboard connected to one "server" machine, capture keyboard and mouse events there, and inject those events into the other "client" machine while the cursor is on that client.

This is the same class of solution as Universal Control, Synergy, Barrier, Input Leap, Mousehop, and Deskflow.

For an immediate working setup, try Input Leap first. It already supports Windows 10/11 and macOS 10.12+, and its latest GitHub release found during this spike was `v3.0.3` from 2025-06-13.

## Why Logitech Flow Fails Here

Logitech Flow is tied to Logitech's Flow-supported devices. Logitech's own Flow wording is that a "Flow-supported keyboard" can follow the mouse. A Keychron keyboard is outside that device ecosystem, so Flow has no supported way to command it to follow the Logitech mouse.

Keychron Bluetooth profile switching is done by keyboard firmware shortcuts such as `fn + 1`, `fn + 2`, and `fn + 3`. The `fn` key is normally consumed inside the keyboard firmware and is not delivered to the operating system as a normal key event. That means a Mac or Windows app usually cannot synthesize "press fn+2" into the physical keyboard to make it change Bluetooth hosts.

Conclusion: do not depend on hardware Bluetooth switching unless we later confirm a specific Keychron model exposes a vendor HID command for host switching. Assume it does not.

## Can We Backport Universal Control?

No, not literally. Apple's Universal Control protocol and service implementation are proprietary and not exposed as a public Windows-compatible API.

What we can build is a Windows/macOS software KVM with similar behavior:

1. Detect when the pointer crosses a configured screen edge.
2. Keep pointer and keyboard focus state in a small peer-to-peer daemon.
3. Capture local input while this machine is the active input owner.
4. Forward input events over the LAN.
5. Inject those events on the active target machine.

This avoids Bluetooth profile switching entirely. The Keychron can stay paired to one machine.

## Existing Solution To Try First

### Input Leap

Input Leap is the most direct open-source candidate to test before writing new code. It is a maintained software KVM that shares one keyboard and mouse between computers over the network. Install it on both machines, set the machine with the Keychron attached as the server, configure the screen layout, and disable Logitech Flow to avoid two tools fighting over the pointer.

Expected result:

- Keychron remains connected to the server machine.
- Mouse crosses to the other machine.
- Keyboard input is forwarded to the other machine.
- No Keychron Bluetooth switching is required.

Things to validate:

- macOS permissions: Accessibility and Input Monitoring.
- Keyboard layout fidelity for the exact Keychron model.
- Modifier mapping: Command/Control/Option/Alt, Windows key, function row behavior.
- Wake/login-screen behavior. Most user-space tools cannot work reliably at locked login screens.
- UAC/elevated-window behavior on Windows. `SendInput` is blocked when trying to inject into a higher-integrity target.

### Mousehop / Deskflow / Synergy / AcrossKM

These are also in the same solution class. Mousehop and AcrossKM appear particularly relevant for macOS/Windows. If Input Leap fails on the Mac/Windows pair, compare these before starting a custom implementation.

## Custom Build Direction

If we build `AnyUniversalControl`, do it as a software KVM, not as a Keychron Bluetooth switcher.

Recommended stack:

- Rust core daemon for cross-platform networking and shared state.
- Small native platform modules for input capture/injection.
- Optional Tauri or lightweight tray UI later; start headless with a config file.
- TCP/TLS or QUIC for event transport.
- mDNS discovery, plus manual IP fallback.
- Pairing by displayed fingerprint or short auth code.

### Core Components

1. `anyuniversalcontrold`
   - Runs on both macOS and Windows.
   - Maintains peer connection, active screen, screen geometry, and input routing state.

2. Platform input layer
   - macOS capture/injection module.
   - Windows capture/injection module.
   - Converts native events into a shared protocol and back.

3. Boundary router
   - Knows virtual screen layout.
   - Detects pointer escape at configured edges.
   - Switches active target.
   - Handles return crossing.

4. Event protocol
   - Keyboard down/up with physical key identity.
   - Modifier state.
   - Mouse move, button down/up, wheel.
   - Optional clipboard messages after MVP.

5. Permissions/bootstrap
   - macOS prompt and diagnostics for Accessibility/Input Monitoring.
   - Windows elevation warning when injection will be limited by UIPI.

## macOS API Notes

Public APIs are enough for a Universal Control-like user-space MVP:

- `CGEventTapCreate` can observe/filter low-level keyboard and mouse events.
- `CGEventPost` can synthesize events.
- `CGEventCreateKeyboardEvent` can create keyboard events.
- Accessibility/Input Monitoring permissions are required for useful capture and injection on modern macOS.

Likely limitations:

- Secure Input can prevent keyboard capture in some apps.
- Login screen/control of locked system is not realistic without deeper system integration.
- Event taps can be disabled by macOS if the callback stalls; forwarding must be non-blocking.
- Need careful mapping between physical key codes and the target keyboard layout.

## Windows API Notes

Public APIs are enough for a user-space MVP:

- `SetWindowsHookEx` with `WH_KEYBOARD_LL` and `WH_MOUSE_LL` can observe low-level keyboard/mouse events.
- Returning a non-zero value from the hook can suppress local delivery.
- `SendInput` can inject keyboard and mouse input.
- `SetCursorPos` can place the cursor when a peer becomes active.

Likely limitations:

- `SendInput` cannot inject into higher-integrity processes because of UIPI. Running the daemon elevated improves this but does not solve secure desktop/login screens.
- Games and anti-cheat-protected apps may reject or flag synthetic input.
- Raw Input may be useful for more robust device-specific handling, but low-level hooks are the simpler first spike.

## MVP Proposal

Build the smallest useful version in this order:

1. Two-machine manual config:
   - `server = mac` or `server = windows`
   - peer IP/port
   - remote screen edge
   - remote screen size

2. Mouse-only crossing:
   - Capture local mouse movement.
   - When the pointer exits the configured edge, switch active target.
   - Inject mouse movement on the peer.
   - Support crossing back.

3. Keyboard forwarding:
   - Capture key down/up on the input-owner machine.
   - Suppress local key delivery while remote is active.
   - Inject key down/up on the peer.
   - Preserve modifier state.

4. Stabilize:
   - reconnect behavior
   - heartbeat
   - cursor position restoration
   - stuck modifier cleanup
   - permission diagnostics

5. Optional:
   - clipboard
   - tray UI
   - encrypted pairing
   - screen auto-discovery
   - per-app exclusions

## Flow Integration Option

Trying to piggyback on Logitech Flow is less attractive than replacing it.

Reasons:

- Flow does not expose a public "active machine changed" API.
- If Flow owns mouse transfer, our app must infer focus from side effects such as local cursor position or process behavior.
- Two independent tools may both capture/suppress/inject pointer events.
- Keyboard forwarding still needs the same OS-level capture/injection stack as a full software KVM.

If Flow integration is still desired, the Mac spike should observe what happens to local cursor coordinates and event stream when Flow transfers to Windows. If the local cursor reliably parks at a screen edge while Flow is remote, we can infer the active peer. If not, replace Flow.

## What We Need From The Mac Spike

Please push notes/results into this repo's `docs/` folder or the linked `UniversalControl` repo once available.

Minimum Mac checks:

1. Confirm whether a simple `CGEventTapCreate` process can capture Keychron key down/up events.
2. Confirm whether the same process can suppress local key events.
3. Confirm whether `CGEventPost` can inject events into normal apps.
4. Record the permissions macOS asks for and whether a restart/logout is needed.
5. Test Command/Option/Control mapping when injecting to Windows.
6. With Logitech Flow enabled, record whether local mouse events continue while the pointer is controlling Windows.
7. With Logitech Flow enabled, record where the macOS cursor position remains while remote control is active.
8. Check whether Secure Input breaks capture in Terminal, password fields, browsers, and IDEs.

Useful details to include:

- macOS version.
- Keychron model and connection mode: Bluetooth, USB, or 2.4GHz dongle.
- Keyboard layout.
- Whether the Keychron is paired to both machines or only one.
- Logitech mouse model and Flow/Options+ version.

## Decision

Use this order of attack:

1. Try Input Leap with Flow disabled.
2. If Input Leap works well, use it instead of building custom software.
3. If Input Leap is close but flawed, inspect whether configuration or a small wrapper solves the problem.
4. If it fails materially, build `AnyUniversalControl` as a Rust-based software KVM.
5. Do not spend time on automatic Keychron Bluetooth switching unless a model-specific vendor command is discovered.

## Sources Checked

- Logitech Flow: `https://www.logitech.com/en-us/product/options/page/flow-multi-device-control`
- Logitech Flow support note: `https://prosupport.logi.com/hc/en-us/articles/360053616653-Logitech-Flow`
- Input Leap: `https://github.com/input-leap/input-leap`
- Input Leap command-line/wiki: `https://github.com/input-leap/input-leap/wiki/Command-Line`
- Keychron Bluetooth setup: `https://keychronsupport.zendesk.com/hc/en-us/articles/360044087014-How-to-connect-the-keyboard-via-Bluetooth`
- Keychron QMK shortcut tables: `https://www.keychron.com/blogs/news/keychron-qmk-keyboard-shortcuts-table-100-96-80-75`
- Apple Quartz Event Services: `https://developer.apple.com/documentation/coregraphics/quartz-event-services`
- Microsoft `SendInput`: `https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput`
