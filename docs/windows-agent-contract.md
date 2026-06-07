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
3. What happens when running `python scripts/windows/capture-companion-link-discovery.py`?
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

Mac-side bridge preflight follow-up from
`docs/windows-inbox/2026-06-07-oliver-pc-wsl-bridge-preflight.md` is answered in
`docs/observations/2026-06-07-local-macos-bridge-preflight.md`: native macOS
preflight reports `detected_primary_display=1710x1112`, both example configs use
that detected size as `effective_local_display`, receiver preflight uses
`peer_mode=mdns_discovery` when `peer_addr` is omitted, and both preflights
reported `warnings=0`. This validates fallback bridge assumptions only; native
admission remains the priority.

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

Preferred capture command:

```powershell
python scripts/capture-input-events.py --mode listen --count 20
python scripts/capture-input-events.py --mode grab --count 20
```

Use `--mode grab-suppress` only after the non-suppressing capture has the
expected event shape. The wrapper writes replayable JSONL under `artifacts/` and
a redacted summary under `docs/windows-inbox/` without typed text values.

Mac-side normalized event replay from
`docs/windows-inbox/2026-06-06-oliver-pc-wsl-input-event-replay.md` is also
pending a controlled foreground target. Replay injects the captured JSONL into
the active desktop session, so use a disposable text field/window first and
record whether key, pointer, button, and wheel events reproduce safely.

The preferred Mac-side watcher for questions 6 and 7 is:

```sh
./scripts/mac/capture-native-admission.sh --mode benign
```

For question 10, use:

```sh
./scripts/mac/capture-native-admission.sh --mode companion-link
```

For the shape-only follow-up, use:

```sh
./scripts/mac/capture-native-admission.sh --mode shape
```

Useful commands from this repo:

```powershell
python scripts/windows/capture-companion-link-discovery.py
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact *> artifacts/windows-companion-link-discovery.txt
python scripts/windows/summarize-companion-link-discovery-output.py `
  artifacts/windows-companion-link-discovery.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-companion-link-discovery.md
python scripts/windows/compare-companion-link-discovery-summaries.py `
  docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md `
  docs/windows-inbox/YYYY-MM-DD-redacted-companion-link-discovery.md `
  --before-label local-macos-rust-mdns `
  --after-label windows-passive `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-companion-link-discovery-compare.md
cargo run -- discover-companion-link --backend system --seconds 30
python scripts/windows/capture-display-probe.py
python scripts/windows/capture-native-admission.py --mode benign
python scripts/windows/capture-native-admission.py --mode companion-link
python scripts/windows/capture-native-admission.py --mode shape
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
cargo run -- discovery advertise --service _anykbflow-probe._tcp.local. --instance "AnyKBFlow Probe" --addr <redacted-lan-ip> --port 49152 --txt phase=visibility --txt role=windows-probe --seconds 60
cargo run -- advertise-mdns --service-type _companion-link._tcp --instance "AnyKBFlow Native Probe" --hostname anykbflow-native-probe --port 49152 --txt probe=visibility --txt role=windows-native-candidate --allow-apple-service --observe-tcp --seconds 60
cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment --observe-tcp --seconds 60
```

For passive CompanionLink discovery, prefer
`scripts/windows/capture-companion-link-discovery.py` because it captures the
raw browse output to an ignored transcript, writes the redacted summary, and
compares it against the local macOS Rust mDNS baseline in one step.

Use `capture-native-admission.py --mode shape` only while
`capture-native-admission.sh --mode shape` is running on the Mac. Commit the
redacted Windows summary, not the raw TCP observer transcript.

For passive CompanionLink discovery, prefer
`scripts/windows/capture-companion-link-discovery.py`; it captures the redacted
Rust mDNS transcript under ignored `artifacts/` and writes the commit-safe
summary under `docs/windows-inbox/`.

For native Windows display geometry, prefer
`scripts/windows/capture-display-probe.py`; it captures `probe displays`,
redacts display names, and preserves routing-relevant bounds under
`docs/windows-inbox/`.

For native-admission runs, prefer `scripts/windows/capture-native-admission.py`
because it captures the full Windows output to an ignored file under
`artifacts/`, then writes only the redacted summary. Manual equivalent for any
command using `--observe-tcp`:

```powershell
cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment --observe-tcp --seconds 60 *> artifacts/windows-native-admission-shape.txt
python scripts/windows/summarize-native-admission-output.py `
  artifacts/windows-native-admission-shape.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md
```

When both minimal and shape-only Windows summaries exist, compare them:

```powershell
python scripts/windows/compare-native-admission-summaries.py `
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-companion-link.md `
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md `
  --before-label minimal `
  --after-label shape `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-compare.md
```

After the Mac-side redacted summary exists, create a paired report:

```powershell
python scripts/compare-native-admission-pair.py `
  docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md `
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md `
  --label shape `
  --output docs/observations/YYYY-MM-DD-redacted-native-admission-shape-pair.md
```

The redacted Rust mDNS summary should preserve event type, service type, port,
TXT key names, TXT value length/class, and address count. Do not commit
unredacted `dns-sd` or `--backend system` output unless it has been manually
reviewed and sanitized.
