# Redacted CompanionLink Discovery Comparison

## Source

- Before label: `before`
- Before file: `docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md`
- After label: `after`
- After file: `docs/windows-inbox/2026-06-07-20260607T102817Z-redacted-native-windows-companion-link-discovery.md`
- Ignored source metadata: yes

## Summary

- Changed fields: 10
- Added fields: 0
- Removed fields: 0

## Evidence Highlights

- `Command Result / AnyUniversalControl command executed`: same
  - before: yes
  - after: yes
- `Command Result / Redaction enabled line`: same
  - before: yes
  - after: yes
- `Command Result / Error lines`: same
  - before: 0
  - after: 0
- `Discovery Events / Search started lines`: changed
  - before: 4
  - after: 5
- `Discovery Events / Service found lines`: changed
  - before: 1
  - after: 2
- `Discovery Events / Service resolved lines`: changed
  - before: 1
  - after: 2
- `Discovery Events / Service removed lines`: same
  - before: 0
  - after: 0
- `Resolved Service Shape / Service types`: changed
  - before: `_companion-link._tcp.local.`=1
  - after: `_companion-link._tcp.local.`=2
- `Resolved Service Shape / Ports`: changed
  - before: `61833`=1
  - after: `49152`=1, `61833`=1
- `Resolved Service Shape / Fullname lengths`: changed
  - before: `50`=1
  - after: `50`=1, `55`=1
- `Resolved Service Shape / Host lengths`: changed
  - before: `26`=1
  - after: `26`=2
- `Resolved Service Shape / Address counts`: changed
  - before: `2`=1
  - after: `2`=2
- `Resolved Service Shape / TXT keys`: changed
  - before: `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
  - after: `probe`, `role`, `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
- `Resolved Service Shape / TXT value length/classes`: changed
  - before: `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1
  - after: `probe:text:11`=1, `role:text:21`=1, `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1
- `Interpretation / CompanionLink service resolved`: same
  - before: yes
  - after: yes
- `Interpretation / Output appears redacted`: same
  - before: yes
  - after: yes

## Changed Fields

- `Discovery Events / Search started lines`
  - before: 4
  - after: 5
- `Discovery Events / Service found lines`
  - before: 1
  - after: 2
- `Discovery Events / Service resolved lines`
  - before: 1
  - after: 2
- `Resolved Service Shape / Address counts`
  - before: `2`=1
  - after: `2`=2
- `Resolved Service Shape / Fullname lengths`
  - before: `50`=1
  - after: `50`=1, `55`=1
- `Resolved Service Shape / Host lengths`
  - before: `26`=1
  - after: `26`=2
- `Resolved Service Shape / Ports`
  - before: `61833`=1
  - after: `49152`=1, `61833`=1
- `Resolved Service Shape / Service types`
  - before: `_companion-link._tcp.local.`=1
  - after: `_companion-link._tcp.local.`=2
- `Resolved Service Shape / TXT keys`
  - before: `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
  - after: `probe`, `role`, `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
- `Resolved Service Shape / TXT value length/classes`
  - before: `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1
  - after: `probe:text:11`=1, `role:text:21`=1, `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1

## Added Fields

- none

## Removed Fields

- none

## Notes

- This comparison is safe to commit only when both inputs are redacted summaries.
- Use this for local macOS Rust mDNS baseline versus Windows passive browse summaries.
- Matching DNS-SD shape is visibility evidence, not native Universal Control admission.
- Re-run with `--include-source` only when transcript paths are relevant.
