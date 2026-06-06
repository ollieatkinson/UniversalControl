# Native Candidate Experiments

These experiments keep the Mac side on Apple's native `UniversalControl.app`.
They are intended to prove or disprove whether a Windows peer can reach native
Rapport/CompanionLink candidate handling before the project falls back to the
separate AnyKBFlow bridge.

## Current Evidence Gap

Windows bridge discovery, heartbeats, reconnects, receiver-side injected
key/button release cleanup, startup common-latch cleanup, planned focus-return
cleanup, input-owner peer-close route reset, and a native display geometry probe
are in place, but native Universal Control discovery is still not proven:

- Windows has not yet proven it can resolve the Mac's `_companion-link._tcp`
  advertisement with the Rust mDNS backend.
- macOS has not yet proven it can see a Windows-advertised service on the real
  LAN path.
- macOS has not yet been observed reacting to a Windows `_companion-link._tcp`
  candidate in `rapportd` or `UniversalControl` logs.
- `cargo run -- probe displays` now has a local macOS single-display observation,
  but still needs native Windows output, external-monitor macOS output, and mouse
  coordinate comparison.

## Experiment 1: Passive Windows Browse

On Windows:

```powershell
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact
```

Commit the redacted output in a Windows note. The important signal is whether
Windows sees a `service_resolved` event, the dynamic port, TXT key names, TXT
value length/class, and address count.

## Experiment 2: Benign Windows Advertisement

On Windows:

```powershell
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
```

On macOS at the same time:

```sh
./scripts/mac/watch-mdns-service.sh --duration 90
./scripts/mac/summarize-mdns-watch-artifact.py artifacts/mac-mdns-watch-YYYYMMDDTHHMMSSZ \
  --expected-instance "AnyKBFlow Probe" \
  --output docs/observations/YYYY-MM-DD-redacted-benign-mdns-watch.md
```

This proves basic Windows-to-macOS mDNS visibility without pretending to be an
Apple service. Raw Mac artifacts stay under `artifacts/` until redacted.

## Experiment 3: Minimal CompanionLink Candidate

This is a controlled log-reaction experiment. It deliberately uses a project
probe TXT shape rather than pretending to know Apple's `rp*` fields.

On macOS first:

```sh
./scripts/mac/watch-companion-link-candidate.sh \
  --duration 90 \
  --instance "AnyKBFlow Native Probe"
./scripts/mac/summarize-mdns-watch-artifact.py artifacts/mac-mdns-watch-YYYYMMDDTHHMMSSZ \
  --expected-instance "AnyKBFlow Native Probe" \
  --output docs/observations/YYYY-MM-DD-redacted-companion-link-candidate.md
```

On Windows while the macOS watcher is running:

```powershell
cargo run -- advertise-mdns `
  --service-type _companion-link._tcp `
  --instance "AnyKBFlow Native Probe" `
  --hostname anykbflow-native-probe `
  --port 49152 `
  --txt probe=visibility `
  --txt role=windows-native-candidate `
  --allow-apple-service `
  --seconds 60
```

Expected evidence:

- macOS `dns-sd -B` sees `AnyKBFlow Native Probe`.
- macOS `dns-sd -L` resolves the Windows host, port, and TXT keys.
- `rapportd` and `UniversalControl` logs either ignore the service or record a
  concrete discovery/rejection reason.
- The committed observation is generated from the watcher artifact summary, not
  from raw `dns-sd` or unified-log output.

Do not treat a successful browse/resolve as native admission. Native admission
requires `rapportd` or `UniversalControl` evidence that the peer became a
candidate or was rejected for a known reason.

## Experiment 4: Apple Peer TXT Shape

Only run this when a real Mac or iPad Universal Control peer is available.

1. Capture an Apple-to-Apple `_companion-link._tcp` resolve while Universal
   Control is enabled.
2. Redact values but preserve TXT key names, value length/class, service type,
   port, and address count.
3. Compare that shape with the local Mac's self-advertisement and the minimal
   Windows candidate above.
4. Only after that, consider a Windows `_companion-link._tcp` advertisement that
   uses a structurally similar non-sensitive TXT shape.

This experiment is about protocol shape, not bypassing account identity or
private trust. Stop if logs show rejection that depends on Apple Account,
iCloud Keychain, private certificates, or platform attestation.
