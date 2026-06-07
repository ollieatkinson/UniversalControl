# Redacted CompanionLink Discovery Summary

## Source

- Transcript file: `artifacts/macos-rust-mdns-companion-link-2026-06-07.txt`
- Raw output: not included

## Command Result

- Cargo finished lines: 1
- AnyKBFlow command executed: yes
- Redaction enabled line: yes
- Error lines: 0

## Discovery Events

- Search started lines: 4
- Service found lines: 1
- Service resolved lines: 1
- Service removed lines: 0
- Other event lines: 0

## Resolved Service Shape

- Service types: `_companion-link._tcp.local.`=1
- Ports: `61833`=1
- Fullname lengths: `50`=1
- Host lengths: `26`=1
- Address counts: `2`=1
- TXT keys: `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
- TXT value length/classes: `rpAD:hex:12`=1, `rpBA:mac-like:17`=1, `rpFl:hex-prefixed:7`=1, `rpHA:hex:12`=1, `rpHI:hex:12`=1, `rpHN:hex:12`=1, `rpMac:integer:1`=1, `rpVr:version:5`=1

## Interpretation

- CompanionLink service resolved: yes
- Output appears redacted: yes
- Notes:
  - This summary is commit-safe only when the input command used `--redact`.
  - Do not commit unredacted hostnames, addresses, instance names, or TXT values.
