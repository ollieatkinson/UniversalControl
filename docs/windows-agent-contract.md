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
- display names if they include user, room, or asset names
- packet payloads containing clipboard or keyboard data
- private keys or pairing material

## First Requested Windows Report

The next native-focused Windows report should answer:

1. Does Windows see this Mac's `_companion-link._tcp.local` advertisement?
2. Which TXT keys and port are visible?
3. What happens when running `cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact`?
4. If Bonjour is installed, what happens with `cargo run -- discover-companion-link --backend system --seconds 30`?
5. What happens when Windows runs `cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe`?
6. Does macOS see the Windows service with `dns-sd -B _anykbflow-probe._tcp local`?
7. Does macOS resolve the Windows service with `dns-sd -L "AnyKBFlow Probe" _anykbflow-probe._tcp local`?
8. Is the Windows prototype currently source-controlled somewhere outside this repo?
9. What language/runtime is the current Windows implementation using?
10. After macOS confirms the benign probe is visible, what happens when Windows advertises the minimal `_companion-link._tcp` native candidate below while the Mac runs `scripts/mac/watch-companion-link-candidate.sh`?
11. What does `cargo run -- probe displays` report from a native Windows terminal, with display names redacted but bounds, scale, primary flag, and negative origins preserved?

Mac-side bridge-smoke and bridge-network-smoke follow-up from the 2026-06-06
Windows notes is answered in
`docs/observations/2026-06-06-local-macos-bridge-smoke.md`: native macOS display
detection feeds bridge local routing, input-owner `Hello.local_display`, and the
loopback JSON-lines transport. The remaining Windows priority is still native
discovery and candidate admission, not more bridge smoke output.

Mac-side pointer injection probes from
`docs/windows-inbox/2026-06-06-oliver-pc-wsl-pointer-injection-probes.md` are
still pending a controlled foreground target. Do not run `inject-button` or
`inject-wheel` against an arbitrary desktop state; those probes click or scroll
the current session and only validate the fallback bridge injection path.

Mac-side normalized input probes from
`docs/windows-inbox/2026-06-06-oliver-pc-wsl-normalized-input-probes.md` are
pending a manual Keychron/mouse action sequence. Use `listen-events` first, then
`grab-events` without suppression, and record redacted JSON for: printable key
down/up, Command/Option/Control/Shift, arrow key, mouse move, button click, and
wheel scroll. Only use `grab-events --suppress` after the non-suppressing probe
matches the expected protocol events.

Mac-side normalized event replay from
`docs/windows-inbox/2026-06-06-oliver-pc-wsl-input-event-replay.md` is also
pending a controlled foreground target. Replay injects the captured JSONL into
the active desktop session, so use a disposable text field/window first and
record whether key, pointer, button, and wheel events reproduce safely.

The Mac-side watcher for questions 6 and 7 is:

```sh
./scripts/mac/watch-mdns-service.sh --duration 60
```

Useful commands from this repo:

```powershell
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact
cargo run -- discover-companion-link --backend system --seconds 30
cargo run -- probe displays
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
cargo run -- discovery advertise --service _anykbflow-probe._tcp.local. --instance "AnyKBFlow Probe" --addr <redacted-lan-ip> --port 49152 --txt phase=visibility --txt role=windows-probe --seconds 60
cargo run -- advertise-mdns --service-type _companion-link._tcp --instance "AnyKBFlow Native Probe" --hostname anykbflow-native-probe --port 49152 --txt probe=visibility --txt role=windows-native-candidate --allow-apple-service --seconds 60
```

The redacted Rust mDNS output should preserve event type, service type, port, TXT key names, TXT value length/class, and address count. Do not commit unredacted `dns-sd` or `--backend system` output unless it has been manually reviewed and sanitized.
