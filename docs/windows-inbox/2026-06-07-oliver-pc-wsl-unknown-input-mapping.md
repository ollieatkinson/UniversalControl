# 2026-06-07 Windows Unknown Input Mapping Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `f8a3176 Add native admission pair report`

## What Changed

Native key and mouse-button replay now rejects unsupported normalized names
with explicit errors:

- `unsupported key name: <name>`
- `unsupported mouse button name: <name>`

Previously an unsupported name was converted to `Unknown(0)`, which could hide
real mapping gaps during bridge or replay tests.

## Local Runtime Observation

WSL uses the stub backend, so this note records the code-path change rather
than a native Windows injection result. Native macOS and Windows runs should
record any unsupported-name error exactly and treat it as input mapping data to
fix deliberately.

## Questions For Mac Side

- Do Keychron modifier, Fn, or function-row captures produce any unsupported key names during `listen-events` or `grab-events` replay?
- If replay fails, what exact normalized event JSON line produced the unsupported-name error?
