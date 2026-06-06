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
3. What happens when running `cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact`?
4. If Bonjour is installed, what happens with `cargo run -- discover-companion-link --backend system --seconds 30`?
5. What happens when Windows runs `cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe`?
6. Does macOS see the Windows service with `dns-sd -B _anykbflow-probe._tcp local`?
7. Does macOS resolve the Windows service with `dns-sd -L "AnyKBFlow Probe" _anykbflow-probe._tcp local`?
8. Is the Windows prototype currently source-controlled somewhere outside this repo?
9. What language/runtime is the current Windows implementation using?

The Mac-side watcher for questions 6 and 7 is:

```sh
./scripts/mac/watch-mdns-service.sh --duration 60
```

Useful commands from this repo:

```powershell
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact
cargo run -- discover-companion-link --backend system --seconds 30
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
cargo run -- discovery advertise --service _anykbflow-probe._tcp.local. --instance "AnyKBFlow Probe" --addr <redacted-lan-ip> --port 49152 --txt phase=visibility --txt role=windows-probe --seconds 60
```

The redacted Rust mDNS output should preserve event type, service type, port, TXT key names, TXT value length/class, and address count. Do not commit unredacted `dns-sd` or `--backend system` output unless it has been manually reviewed and sanitized.
