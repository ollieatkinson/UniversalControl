# Redacted CompanionLink Discovery Comparison

## Source

- Before label: `local-macos-rust-mdns`
- Before file: `/home/oliver/src/github.com/ollieatkinson/AnyUniversalControl/docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md`
- After label: `windows-passive`
- After file: `/home/oliver/src/github.com/ollieatkinson/AnyUniversalControl/docs/windows-inbox/2026-06-07-redacted-companion-link-discovery.md`
- Ignored source metadata: yes

## Summary

- Changed fields: 11
- Added fields: 0
- Removed fields: 0

## Evidence Highlights

- `Command Result / AnyUniversalControl command executed`: same
  - local-macos-rust-mdns: yes
  - windows-passive: yes
- `Command Result / Redaction enabled line`: same
  - local-macos-rust-mdns: yes
  - windows-passive: yes
- `Command Result / Error lines`: same
  - local-macos-rust-mdns: 0
  - windows-passive: 0
- `Discovery Events / Search started lines`: changed
  - local-macos-rust-mdns: 4
  - windows-passive: 5
- `Discovery Events / Service found lines`: changed
  - local-macos-rust-mdns: 1
  - windows-passive: 0
- `Discovery Events / Service resolved lines`: changed
  - local-macos-rust-mdns: 1
  - windows-passive: 0
- `Discovery Events / Service removed lines`: same
  - local-macos-rust-mdns: 0
  - windows-passive: 0
- `Resolved Service Shape / Service types`: changed
  - local-macos-rust-mdns: `_companion-link._tcp.local.`=1
  - windows-passive: none
- `Resolved Service Shape / Ports`: changed
  - local-macos-rust-mdns: `61833`=1
  - windows-passive: none
- `Resolved Service Shape / Fullname lengths`: changed
  - local-macos-rust-mdns: `50`=1
  - windows-passive: none
- `Resolved Service Shape / Host lengths`: changed
  - local-macos-rust-mdns: `26`=1
  - windows-passive: none
- `Resolved Service Shape / Address counts`: changed
  - local-macos-rust-mdns: `2`=1
  - windows-passive: none
- `Resolved Service Shape / TXT keys`: changed
  - local-macos-rust-mdns: `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
  - windows-passive: none
- `Resolved Service Shape / TXT value length/classes`: changed
  - local-macos-rust-mdns: `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1
  - windows-passive: none
- `Interpretation / CompanionLink service resolved`: changed
  - local-macos-rust-mdns: yes
  - windows-passive: no
- `Interpretation / Output appears redacted`: same
  - local-macos-rust-mdns: yes
  - windows-passive: yes

## Changed Fields

- `Discovery Events / Search started lines`
  - local-macos-rust-mdns: 4
  - windows-passive: 5
- `Discovery Events / Service found lines`
  - local-macos-rust-mdns: 1
  - windows-passive: 0
- `Discovery Events / Service resolved lines`
  - local-macos-rust-mdns: 1
  - windows-passive: 0
- `Interpretation / CompanionLink service resolved`
  - local-macos-rust-mdns: yes
  - windows-passive: no
- `Resolved Service Shape / Address counts`
  - local-macos-rust-mdns: `2`=1
  - windows-passive: none
- `Resolved Service Shape / Fullname lengths`
  - local-macos-rust-mdns: `50`=1
  - windows-passive: none
- `Resolved Service Shape / Host lengths`
  - local-macos-rust-mdns: `26`=1
  - windows-passive: none
- `Resolved Service Shape / Ports`
  - local-macos-rust-mdns: `61833`=1
  - windows-passive: none
- `Resolved Service Shape / Service types`
  - local-macos-rust-mdns: `_companion-link._tcp.local.`=1
  - windows-passive: none
- `Resolved Service Shape / TXT keys`
  - local-macos-rust-mdns: `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
  - windows-passive: none
- `Resolved Service Shape / TXT value length/classes`
  - local-macos-rust-mdns: `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1
  - windows-passive: none

## Added Fields

- none

## Removed Fields

- none

## Notes

- This comparison is safe to commit only when both inputs are redacted summaries.
- Use this for local macOS Rust mDNS baseline versus Windows passive browse summaries.
- Matching DNS-SD shape is visibility evidence, not native Universal Control admission.
- Re-run with `--include-source` only when transcript paths are relevant.
