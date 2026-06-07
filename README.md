# UniversalControl

Reverse-engineering notes, tooling, and prototypes for making a Windows machine participate in the Mac Universal Control-style keyboard, mouse, drag, and clipboard experience.

The repository is currently in the evidence-gathering phase. The primary target is native macOS Universal Control compatibility: keep the Mac side running Apple's `UniversalControl.app` and make Windows participate if the protocol allows it. A project-owned Mac/Windows bridge is a fallback only if native Rapport/CompanionLink authentication proves impossible from Windows.

## Tracks

### Native Universal Control

This is the preferred path. The Mac should stay on Apple's native Universal Control stack, and Windows should try to become visible to macOS discovery and session setup.

Start with:

- [docs/native-feasibility.md](docs/native-feasibility.md)
- [docs/research-log.md](docs/research-log.md)
- [docs/protocol-hypothesis.md](docs/protocol-hypothesis.md)
- [docs/native-compatibility-checklist.md](docs/native-compatibility-checklist.md)
- [docs/capture-plan.md](docs/capture-plan.md)
- [docs/native-candidate-experiments.md](docs/native-candidate-experiments.md)
- [scripts/mac/uc-probe.sh](scripts/mac/uc-probe.sh)

### AnyKBFlow Prototype

`anykbflow` is an early Rust software KVM prototype for sharing a Keychron keyboard and mouse between macOS and Windows without relying on Logitech Flow or Bluetooth profile switching.

It has a TCP JSON-lines peer protocol, edge-crossing router, and a macOS/Windows native input backend based on `rdev` grab/simulate. Linux builds use a no-op backend so the shared code can be checked in this workspace.

See [docs/prototype.md](docs/prototype.md) for setup and current limitations.

## Native mDNS Probes

Run this on macOS or Windows to browse for Apple's native Rapport/CompanionLink service:

```sh
cargo run -- discover-companion-link --seconds 10
```

Useful variants:

```sh
cargo run -- discover-companion-link --backend system --seconds 10
cargo run -- discover-companion-link --backend rust-mdns --seconds 10
python scripts/windows/capture-companion-link-discovery.py
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact > artifacts/windows-companion-link-discovery.txt 2>&1
scripts/windows/summarize-companion-link-discovery-output.py artifacts/windows-companion-link-discovery.txt
```

`auto` uses the system `dns-sd` command when available, otherwise it uses the pure Rust mDNS backend. With `--redact`, `auto` uses the Rust backend because system `dns-sd` output is pass-through and cannot be sanitized. The Windows capture wrapper uses the redacted Rust backend by default, writes a summary, and compares it with the local macOS baseline. It refuses `--backend system` unless `--allow-unredacted-system` is passed. Review unredacted output before sharing because hostnames, addresses, instance names, and TXT values can be stable identifiers.

Run this on Windows to advertise a benign probe service while the Mac watches with `dns-sd`:

```sh
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
```

On the Mac:

```sh
./scripts/mac/watch-mdns-service.sh --duration 60
dns-sd -B _anykbflow-probe._tcp local
dns-sd -L "AnyKBFlow Probe" _anykbflow-probe._tcp local
```

For the coordinated native-admission run, prefer the Mac wrapper that prints the
matching Windows command and writes a redacted Mac summary after capture:

```sh
./scripts/mac/capture-native-admission.sh --mode benign
./scripts/mac/capture-native-admission.sh --mode companion-link
./scripts/mac/capture-native-admission.sh --mode shape
```

On Windows, use the matching wrapper to print the Mac command, capture the raw
Windows transcript under ignored `artifacts/`, and write a redacted Windows
summary:

```sh
python scripts/windows/capture-native-admission.py --mode benign
python scripts/windows/capture-native-admission.py --mode companion-link
python scripts/windows/capture-native-admission.py --mode shape
```

The advertiser refuses Apple-owned service types such as `_companion-link._tcp` unless `--allow-apple-service` is supplied for a controlled native-compatibility experiment.

After a benign visibility check and a minimal `_companion-link._tcp` candidate
check, this guarded command advertises a shape-only CompanionLink candidate with
non-sensitive placeholder `rp*` TXT values matching the redacted macOS baseline
key/value classes:

```sh
cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment
```

Run it only while the Mac-side CompanionLink watcher is capturing `rapportd` and
`UniversalControl` logs; `capture-native-admission.sh --mode shape` starts that
watcher and writes the redacted summary.

The fallback bridge advertises `_anykbflow._tcp.local.` for project-owned peer discovery. Native Apple compatibility experiments continue to use `_companion-link._tcp.local.` and are tracked separately.

## Current Findings

- macOS Universal Control is implemented by `/System/Library/CoreServices/UniversalControl.app`, bundle identifier `com.apple.universalcontrol`.
- On macOS 26.5.1, the app is launched as `com.apple.ensemble`.
- Launchd starts it from Rapport matching events for:
  - discovery of `_companion-link._tcp`
  - a server match for `com.apple.universalcontrol`
- The app has private entitlements for `com.apple.CompanionLink`, HID event dispatch, NearbyInteraction, Skylight Universal Control, and Wi-Fi peer-to-peer services.
- Local Bonjour browsing shows this Mac advertises `_companion-link._tcp` through `rapportd`, not a dedicated `_universalcontrol._tcp` service.

Those facts make Rapport/CompanionLink the first interop surface to understand. See [docs/protocol-hypothesis.md](docs/protocol-hypothesis.md).

## Repo Layout

- [docs/research-log.md](docs/research-log.md): dated evidence and source notes.
- [docs/native-feasibility.md](docs/native-feasibility.md): native-first decision gates and fallback evidence threshold.
- [docs/protocol-hypothesis.md](docs/protocol-hypothesis.md): current model of discovery, trust, control, and HID data flow.
- [docs/native-compatibility-checklist.md](docs/native-compatibility-checklist.md): gates for keeping the Mac side on native Universal Control.
- [docs/capture-plan.md](docs/capture-plan.md): repeatable experiments for macOS and Windows captures.
- [docs/native-candidate-experiments.md](docs/native-candidate-experiments.md): immediate native discovery and candidate-admission experiments.
- [docs/windows-interop-plan.md](docs/windows-interop-plan.md): native-first Windows peer strategy and fallback bridge criteria.
- [docs/windows-agent-contract.md](docs/windows-agent-contract.md): where the Windows machine should write observations.
- [docs/language-choice.md](docs/language-choice.md): why the shared core stays Rust and where Swift may fit as a macOS helper.
- [scripts/mac/uc-probe.sh](scripts/mac/uc-probe.sh): read-only macOS probe for Universal Control/Rapport surfaces.
- [scripts/mac/capture-uc-session.sh](scripts/mac/capture-uc-session.sh): paired Apple-to-Apple Universal Control session capture wrapper.
- [scripts/mac/capture-native-admission.sh](scripts/mac/capture-native-admission.sh): coordinated Mac watcher plus redacted summary wrapper for Windows native-admission probes.
- [scripts/mac/watch-mdns-service.sh](scripts/mac/watch-mdns-service.sh): bounded mDNS plus native log watcher for Windows advertisement checks.
- [scripts/mac/watch-companion-link-candidate.sh](scripts/mac/watch-companion-link-candidate.sh): native-focused watcher for controlled `_companion-link._tcp` candidate checks.
- [scripts/mac/summarize-uc-probe-artifact.py](scripts/mac/summarize-uc-probe-artifact.py): redacts baseline macOS probe artifacts into commit-safe Markdown summaries.
- [scripts/mac/summarize-universalcontrol-strings.py](scripts/mac/summarize-universalcontrol-strings.py): extracts a commit-safe UniversalControl string-surface summary for native protocol search terms.
- [scripts/mac/compare-uc-probe-summaries.py](scripts/mac/compare-uc-probe-summaries.py): compares two redacted baseline probe summaries.
- [scripts/mac/summarize-mdns-watch-artifact.py](scripts/mac/summarize-mdns-watch-artifact.py): redacts watcher artifacts into commit-safe Markdown summaries.
- [scripts/mac/compare-mdns-watch-summaries.py](scripts/mac/compare-mdns-watch-summaries.py): compares two redacted watcher summaries, especially minimal versus shape-only CompanionLink candidates.
- [scripts/mac/summarize-uc-session-artifact.py](scripts/mac/summarize-uc-session-artifact.py): redacts paired-session artifacts into commit-safe Markdown summaries.
- [scripts/capture-input-events.py](scripts/capture-input-events.py): captures normalized input events from native macOS/Windows probes, writes a redacted summary, and can route-gate the capture against an input-owner config.
- [scripts/summarize-input-events.py](scripts/summarize-input-events.py): summarizes normalized `InputEvent` JSONL without including typed text values.
- [scripts/compare-native-admission-pair.py](scripts/compare-native-admission-pair.py): pairs redacted Mac watcher and Windows TCP-observer summaries into one admission report.
- [scripts/windows/capture-companion-link-discovery.py](scripts/windows/capture-companion-link-discovery.py): captures Windows passive CompanionLink discovery, writes a redacted summary, and compares it with the local baseline.
- [scripts/windows/summarize-companion-link-discovery-output.py](scripts/windows/summarize-companion-link-discovery-output.py): redacts `discover-companion-link --redact` output into commit-safe Markdown.
- [scripts/windows/compare-companion-link-discovery-summaries.py](scripts/windows/compare-companion-link-discovery-summaries.py): compares two redacted CompanionLink discovery summaries.
- [scripts/windows/capture-display-probe.py](scripts/windows/capture-display-probe.py): captures native Windows display geometry and writes a redacted bridge-calibration summary.
- [scripts/windows/summarize-display-probe-output.py](scripts/windows/summarize-display-probe-output.py): redacts display probe names while preserving bounds, scale, and virtual layout.
- [scripts/windows/capture-native-admission.py](scripts/windows/capture-native-admission.py): coordinated Windows advertiser plus redacted summary wrapper for native-admission probes.
- [scripts/windows/summarize-native-admission-output.py](scripts/windows/summarize-native-admission-output.py): redacts Windows native-admission command output into commit-safe Markdown.
- [scripts/windows/compare-native-admission-summaries.py](scripts/windows/compare-native-admission-summaries.py): compares two redacted Windows native-admission summaries.

## Running The macOS Probe

```sh
./scripts/mac/uc-probe.sh
./scripts/mac/summarize-uc-probe-artifact.py artifacts/mac-uc-probe-YYYYMMDDTHHMMSSZ \
  --output docs/observations/YYYY-MM-DD-redacted-macos-uc-probe.md
./scripts/mac/compare-uc-probe-summaries.py docs/observations/before.md docs/observations/after.md \
  --before-label before --after-label after \
  --output docs/observations/YYYY-MM-DD-redacted-macos-uc-probe-compare.md
```

The script writes timestamped output under `artifacts/`, which is intentionally ignored by git because the output can contain device names, local addresses, and stable identifiers.
Only commit the redacted summary.

## Ground Rules

- Work from observable behavior, public documentation, and local system evidence.
- Keep Apple-account secrets, Keychain material, packet captures, and device identifiers out of git unless explicitly redacted.
- Treat Apple-private authentication as a compatibility constraint, not something to bypass.
- Prefer native macOS Universal Control compatibility until evidence shows Windows cannot satisfy the trust/session requirements safely or legally.
- Keep the clean-room Windows/Mac bridge as the fallback, not the default.
