# UniversalControl

Reverse-engineering notes, tooling, and prototypes for making a Windows machine participate in the Mac Universal Control-style keyboard, mouse, drag, and clipboard experience.

The repository is currently in the evidence-gathering phase. The primary target is native macOS Universal Control compatibility: keep the Mac side running Apple's `UniversalControl.app` and make Windows participate if the protocol allows it. A project-owned Mac/Windows bridge is a fallback only if native Rapport/CompanionLink authentication proves impossible from Windows.

## Tracks

### Native Universal Control

This is the preferred path. The Mac should stay on Apple's native Universal Control stack, and Windows should try to become visible to macOS discovery and session setup.

Start with:

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
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact
```

`auto` uses the system `dns-sd` command when available, otherwise it uses the pure Rust mDNS backend. With `--redact`, `auto` uses the Rust backend because system `dns-sd` output is pass-through and cannot be sanitized. Review unredacted output before sharing because hostnames, addresses, instance names, and TXT values can be stable identifiers.

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

The advertiser refuses Apple-owned service types such as `_companion-link._tcp` unless `--allow-apple-service` is supplied for a controlled native-compatibility experiment.

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
- [docs/protocol-hypothesis.md](docs/protocol-hypothesis.md): current model of discovery, trust, control, and HID data flow.
- [docs/native-compatibility-checklist.md](docs/native-compatibility-checklist.md): gates for keeping the Mac side on native Universal Control.
- [docs/capture-plan.md](docs/capture-plan.md): repeatable experiments for macOS and Windows captures.
- [docs/native-candidate-experiments.md](docs/native-candidate-experiments.md): immediate native discovery and candidate-admission experiments.
- [docs/windows-interop-plan.md](docs/windows-interop-plan.md): native-first Windows peer strategy and fallback bridge criteria.
- [docs/windows-agent-contract.md](docs/windows-agent-contract.md): where the Windows machine should write observations.
- [scripts/mac/uc-probe.sh](scripts/mac/uc-probe.sh): read-only macOS probe for Universal Control/Rapport surfaces.
- [scripts/mac/capture-uc-session.sh](scripts/mac/capture-uc-session.sh): paired Apple-to-Apple Universal Control session capture wrapper.
- [scripts/mac/watch-mdns-service.sh](scripts/mac/watch-mdns-service.sh): bounded mDNS plus log watcher for Windows advertisement checks.
- [scripts/mac/watch-companion-link-candidate.sh](scripts/mac/watch-companion-link-candidate.sh): native-focused watcher for controlled `_companion-link._tcp` candidate checks.
- [scripts/mac/summarize-mdns-watch-artifact.py](scripts/mac/summarize-mdns-watch-artifact.py): redacts watcher artifacts into commit-safe Markdown summaries.
- [scripts/mac/summarize-uc-session-artifact.py](scripts/mac/summarize-uc-session-artifact.py): redacts paired-session artifacts into commit-safe Markdown summaries.

## Running The macOS Probe

```sh
./scripts/mac/uc-probe.sh
```

The script writes timestamped output under `artifacts/`, which is intentionally ignored by git because the output can contain device names, local addresses, and stable identifiers.

## Ground Rules

- Work from observable behavior, public documentation, and local system evidence.
- Keep Apple-account secrets, Keychain material, packet captures, and device identifiers out of git unless explicitly redacted.
- Treat Apple-private authentication as a compatibility constraint, not something to bypass.
- Prefer native macOS Universal Control compatibility until evidence shows Windows cannot satisfy the trust/session requirements safely or legally.
- Keep the clean-room Windows/Mac bridge as the fallback, not the default.
