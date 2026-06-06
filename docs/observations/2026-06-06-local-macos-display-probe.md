# 2026-06-06 Local macOS Display Probe

## Machine

- Host role: macOS-side native/runtime probe host
- Prior OS inventory: see `docs/observations/2026-06-06-local-macos-inventory.md`
- Display names: redacted

## Repo State

- Branch: `trunk`
- Base before local fix: `68c2336 Add native display geometry probe`

## Commands Run

```sh
cargo run -- probe displays
system_profiler SPDisplaysDataType -json
```

## Observation

The first macOS run of `cargo run -- probe displays` returned `displays: 0`
because the `display-info` crate path used `CGGetActiveDisplayList`.
`system_profiler` still reported one built-in internal display as online but
asleep, so the probe now falls back to CoreGraphics online-display enumeration
when the active-display list is empty on macOS.

Redacted probe result after the fallback:

```text
displays: 1
display_source: coregraphics-online-fallback
index=0 primary=true builtin=true name=<redacted len=9> friendly_name=<redacted len=16>
x=0 y=0 width=1710 height=1112 scale=2.00 rotation=0 hz=60.00 width_mm=290 height_mm=188
virtual_bounds: x=0 y=0 width=1710 height=1112
```

## Interpretation

- The local Mac has one display in this run.
- No negative display origin was observed because no external monitor was attached.
- The bridge config can use `local_width=1710` and `local_height=1112` for this Mac when it is the input-owner side, subject to confirming `probe listen` mouse coordinates use the same logical coordinate space.
- The macOS display probe must prefer active displays when available, but the online-display fallback is needed when displays are online but asleep.

## Follow-Up

- Run `cargo run -- probe displays` from a native Windows terminal and commit a redacted Windows geometry observation.
- Re-run this probe on macOS with an external display placed left or above the built-in display to verify negative `x` or `y` origins.
- Compare these bounds with `probe listen` mouse move coordinates before relying on them for edge crossing.
