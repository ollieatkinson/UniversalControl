# 2026-06-07 Local Input Replay Validation

## Source

- Windows prompt: `docs/windows-inbox/2026-06-07-oliver-pc-wsl-unknown-input-mapping.md`
- Local branch: `trunk`
- Purpose: make unsupported normalized input names visible without native
  injection or raw event review.

## Result

- `probe replay-events --dry-run` now validates normalized key/button mapping
  through shared code before any native injection path.
- Dry-run validation works on the stub WSL/Linux backend. Non-dry-run replay
  still requires the native macOS or Windows backend.
- The replayable key/button whitelist is unit-tested against the native `rdev`
  parser on macOS/Windows.
- `scripts/capture-input-events.py --dry-run-replay` appends a redacted
  `Replay Dry Run` section to the capture summary, including exact unsupported
  normalized key/button names.

## Smoke Checks

Supported event dry-run:

```sh
cargo run -- probe replay-events --dry-run --path <supported-jsonl>
```

Result:

- status: passed
- validated events: 5
- covered key/button names: `KeyA`, `Left`

Unsupported key dry-run:

```sh
cargo run -- probe replay-events --dry-run --path <unsupported-key-jsonl>
```

Result:

- status: failed
- error: `unsupported key name: AudioVolumeUp`

Unsupported button dry-run:

```sh
cargo run -- probe replay-events --dry-run --path <unsupported-button-jsonl>
```

Result:

- status: failed
- error: `unsupported mouse button name: Unknown(0)`

## Current Answer To Windows

The current mapper explicitly supports `Function`, `MetaLeft`, `MetaRight`,
left/right Control and Shift, `Alt`, `AltGr`, arrows, F1-F12, alphanumeric
keys, common punctuation, and common keypad keys. It does not yet support media
keys such as `AudioVolumeUp`.

Actual Keychron Fn/function-row behavior still needs a native macOS or Windows
`listen-events` or `grab-events` capture. Use:

```sh
python scripts/capture-input-events.py --mode listen --count 20 \
  --route-config configs/input-owner.example.toml \
  --expect-activation \
  --min-forwarded-inputs 1 \
  --dry-run-replay
```

Commit only the redacted summary. Keep the JSONL and replay transcript under
ignored `artifacts/`.
