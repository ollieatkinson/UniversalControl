# Redacted macOS Universal Control Probe Comparison

## Source

- Before label: `2026-06-06`
- Before file: `docs/observations/2026-06-06-redacted-macos-uc-probe.md`
- After label: `2026-06-07`
- After file: `docs/observations/2026-06-07-redacted-macos-uc-probe.md`
- Ignored source metadata: yes

## Summary

- Changed fields: 11
- Added fields: 0
- Removed fields: 0

## Changed Fields

- `Interpretation / Native proximity/log signal`
  - 2026-06-06: native process logs include redacted Rapport event/message IDs
  - 2026-06-07: native process logs present without parsed event/message IDs
- `Recent Unified Logs / BLE keyword lines`
  - 2026-06-06: 81
  - 2026-06-07: 147
- `Recent Unified Logs / CompanionLink keyword lines`
  - 2026-06-06: 79
  - 2026-06-07: 34
- `Recent Unified Logs / Error/fault keyword lines`
  - 2026-06-06: 15
  - 2026-06-07: 9
- `Recent Unified Logs / Input keyword lines`
  - 2026-06-06: 24
  - 2026-06-07: 0
- `Recent Unified Logs / P2P keyword lines`
  - 2026-06-06: 68
  - 2026-06-07: 131
- `Recent Unified Logs / Proximity keyword lines`
  - 2026-06-06: 75
  - 2026-06-07: 132
- `Recent Unified Logs / Rapport event IDs`
  - 2026-06-06: `_systemInfoUpdate`
  - 2026-06-07: none
- `Recent Unified Logs / Rapport message IDs`
  - 2026-06-06: `SystemInfo`
  - 2026-06-07: none
- `Recent Unified Logs / UniversalControl lines`
  - 2026-06-06: 13
  - 2026-06-07: 6
- `Recent Unified Logs / rapportd lines`
  - 2026-06-06: 187
  - 2026-06-07: 194

## Added Fields

- none

## Removed Fields

- none

## Notes

- This comparison is safe to commit only when both inputs are redacted summaries.
- Re-run with `--include-source` only when artifact timestamps and names are relevant.
