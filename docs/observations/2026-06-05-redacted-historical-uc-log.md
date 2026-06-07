# Redacted Historical Universal Control Log Summary

## Source

- Window start: 2026-06-05 00:00:00
- Window end: 2026-06-06 00:00:00
- Processes counted: `UniversalControl`, `rapportd`, `nearbyd`, `wifip2pd`
- `log show --info`: no
- `log show --debug`: no
- Raw unified-log lines: not included
- Hostnames, addresses, device names, and payloads: not included
- Context: Operator reported Apple-to-Apple Universal Control use with a Mac Pro during this date.

## Process Counts

- Total counted lines: 183573
- UniversalControl lines: 110394
- rapportd lines: 75264
- nearbyd lines: 0
- wifip2pd lines: 80
- mDNSResponder lines: 0

## Signal Families

- Discovery keyword lines: 2740
- Session/control keyword lines: 172299
- Input/action keyword lines: 101507
- Error/rejection keyword lines: 13179
- UniversalControl/rapportd discovery keyword lines: 2740
- UniversalControl/rapportd session/control keyword lines: 172257
- UniversalControl/rapportd input/action keyword lines: 101475
- UniversalControl/rapportd error/rejection keyword lines: 13099
- Native stream keyword lines: 2531
- Native target/input keyword lines: 0
- Native sync/layout keyword lines: 0
- Proximity/ranging keyword lines: 28460
- Native/proximity-process proximity keyword lines: 28460
- Wi-Fi peer-to-peer/AWDL keyword lines: 32206
- Native/transport-process Wi-Fi P2P keyword lines: 32094

## Interpretation

- Native session signal: stream or sync/layout signal in redacted counts; inspect raw local logs for a narrow window
- Target/input negotiation signal: generic input/action keywords counted without target-state templates
- Proximity or Wi-Fi P2P side-channel signal: possible proximity or Wi-Fi peer-to-peer signal in redacted counts
- Notes:
  - This is a historical log count, not a labeled action trace.
  - Use it to decide whether old logs are worth narrower follow-up windows.
  - A fresh `capture-uc-session.sh --duration 120` run is still the stronger Apple-to-Apple baseline.
