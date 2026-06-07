# Redacted CompanionLink Discovery Summary

## Source

- Transcript file: `artifacts/windows-native-companion-link-discovery-20260607T102817Z.txt`
- Raw output: not included

## Command Result

- Cargo finished lines: 1
- AnyKBFlow command executed: yes
- Redaction enabled line: yes
- Error lines: 0

## Discovery Events

- Search started lines: 5
- Service found lines: 2
- Service resolved lines: 2
- Service removed lines: 0
- Other event lines: 0

## Resolved Service Shape

- Service types: `_companion-link._tcp.local.`=2
- Ports: `49152`=1, `61833`=1
- Fullname lengths: `50`=1, `55`=1
- Host lengths: `26`=2
- Address counts: `2`=2
- TXT keys: `probe`, `role`, `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
- TXT value length/classes: `probe:text:11`=1, `role:text:21`=1, `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1

## Interpretation

- CompanionLink service resolved: yes
- Output appears redacted: yes
- Notes:
  - This summary is commit-safe only when the input command used `--redact`.
  - Do not commit unredacted hostnames, addresses, instance names, or TXT values.
