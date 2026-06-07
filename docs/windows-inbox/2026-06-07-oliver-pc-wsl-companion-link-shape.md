# 2026-06-07 Windows CompanionLink Shape Probe Note

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2

## Repo State

- Branch: `trunk`
- Base commit before this change: `309f8f2 Add UC probe summary comparer`

## What Changed

- Added a guarded shape-only CompanionLink advertisement:
  - `cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment --seconds 60`
- Added `--observe-tcp` for advertisement probes that need to record whether
  macOS attempts to connect to the published SRV port.
- The command publishes `_companion-link._tcp` with placeholder `rp*` TXT values
  matching the redacted macOS baseline key/value classes from
  `docs/observations/2026-06-06-redacted-macos-uc-probe.md`.
- It does not copy real Apple TXT values, identifiers, certificates, hostnames,
  account material, or pairing material.
- It does not run a Rapport listener; this is DNS-SD shape evidence only.

## Why This Matters

The minimal native candidate can show whether macOS sees a Windows-owned
`_companion-link._tcp` service at all. The shape-only candidate is the next
controlled step: it tests whether `rapportd` or `UniversalControl` reacts
differently when the service has the same redacted TXT key/value-class structure
as the local macOS CompanionLink advertisement.

## Commands To Run

On macOS first:

```sh
./scripts/mac/watch-companion-link-candidate.sh --duration 90 --instance "AnyKBFlow Native Shape Probe"
./scripts/mac/summarize-mdns-watch-artifact.py artifacts/mac-mdns-watch-YYYYMMDDTHHMMSSZ \
  --expected-instance "AnyKBFlow Native Shape Probe" \
  --output docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md
```

On Windows while the watcher is running:

```powershell
cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment --observe-tcp --seconds 60
```

## Local Runtime Observation

This was implemented from WSL and cross-target checked. It still needs to run
from a native Windows terminal on the real LAN while the Mac watcher captures
DNS-SD and unified-log output.

The TCP observer prints:

- each accepted peer address
- whether the peer closed, timed out, or sent immediate bytes
- a short first-read hex prefix when immediate bytes are sent
- final `accepted_connections=<n>` summary

## Questions For Mac Side

- Does `dns-sd -B` see `AnyKBFlow Native Shape Probe`?
- Does `dns-sd -L` resolve the published port and all eight `rp*` TXT keys?
- Do `rapportd` or `UniversalControl` logs change compared with the minimal
  `probe=visibility` candidate?
- Does the Windows TCP observer record any attempted connection to the
  advertised port?
