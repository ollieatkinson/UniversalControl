# Windows Agent Documentation Contract

The Windows machine should write investigation notes here:

```text
docs/windows-inbox/YYYY-MM-DD-machine-name-topic.md
```

Use Markdown. Keep raw captures out of git unless they are explicitly redacted and small.

## Required Sections

Each note should include:

```md
# YYYY-MM-DD Windows Observation

## Machine

- Windows version:
- Build:
- Host role:
- Network adapters:
- Active adapter:
- Firewall profile:

## Repo State

- Branch:
- Commit:
- Uncommitted changes:

## What Changed

- ...

## Commands Run

```powershell
...
```

## Observations

- ...

## Evidence Files

- `artifacts/...`

## Questions For Mac Side

- ...
```

## Redaction Rules

Redact before committing:

- Apple Account identifiers
- local IP addresses if not needed
- stable Bluetooth addresses
- stable Bonjour TXT identifiers
- packet payloads containing clipboard or keyboard data
- private keys or pairing material

## First Requested Windows Report

The next Windows report should answer:

1. Does Windows see this Mac's `_companion-link._tcp.local` advertisement?
2. Which TXT keys and port are visible?
3. What happens when running `cargo run -- discover-companion-link --backend rust-mdns --seconds 30`?
4. If Bonjour is installed, what happens with `cargo run -- discover-companion-link --backend system --seconds 30`?
5. Can Windows advertise an mDNS service visible to macOS?
6. Is the Windows prototype currently source-controlled somewhere outside this repo?
7. What language/runtime is the current Windows implementation using?
