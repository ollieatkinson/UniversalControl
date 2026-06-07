# Native Candidate Experiments

These experiments keep the Mac side on Apple's native `UniversalControl.app`.
They are intended to prove or disprove whether a Windows peer can reach native
Rapport/CompanionLink candidate handling before the project falls back to the
separate AnyKBFlow bridge.

## Current Evidence Gap

Windows bridge discovery, heartbeats, reconnects, receiver-side injected
key/button release cleanup, startup common-latch cleanup, planned focus-return
cleanup, input-owner peer-close route reset, runtime native display geometry in
peer `Hello` messages, local edge routing from detected display size, and a
macOS display probe fallback are in place, but native Universal Control
discovery is still not proven:

- Windows has not yet proven it can resolve the Mac's `_companion-link._tcp`
  advertisement with the Rust mDNS backend.
- macOS has not yet proven it can see a Windows-advertised service on the real
  LAN path.
- macOS has not yet been observed reacting to a Windows `_companion-link._tcp`
  candidate in `rapportd` or `UniversalControl` logs.
- `cargo run -- probe displays` now has a local macOS single-display observation,
  and the bridge smoke probes confirm macOS native display detection feeds local
  routing, input-owner `Hello`, and loopback JSON-lines transport; this still
  needs native Windows-terminal output, external-monitor macOS output, and mouse
  coordinate comparison against a live two-machine run.

## Experiment 1: Passive Windows Browse

On Windows:

```powershell
python scripts/windows/capture-companion-link-discovery.py
```

Manual equivalent:

```powershell
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact *> artifacts/windows-companion-link-discovery.txt
python scripts/windows/summarize-companion-link-discovery-output.py `
  artifacts/windows-companion-link-discovery.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-companion-link-discovery.md
```

Commit the redacted summary in a Windows note. The important signal is whether
Windows sees a `service_resolved` event, the dynamic port, TXT key names, TXT
value length/class, and address count.

Compare the Windows summary against the local macOS Rust mDNS baseline:

```sh
python scripts/windows/compare-companion-link-discovery-summaries.py \
  docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md \
  docs/windows-inbox/YYYY-MM-DD-redacted-companion-link-discovery.md \
  --before-label local-macos-rust-mdns \
  --after-label windows-passive \
  --output docs/windows-inbox/YYYY-MM-DD-redacted-companion-link-discovery-compare.md
```

## Experiment 2: Benign Windows Advertisement

On Windows:

```powershell
python scripts/windows/capture-native-admission.py --mode benign
```

Manual equivalent:

```powershell
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
```

On macOS at the same time:

```sh
./scripts/mac/capture-native-admission.sh --mode benign
```

Manual equivalent:

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
./scripts/mac/capture-native-admission.sh --mode companion-link
```

Manual equivalent:

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
python scripts/windows/capture-native-admission.py --mode companion-link
```

Manual equivalent:

```powershell
cargo run -- advertise-mdns `
  --service-type _companion-link._tcp `
  --instance "AnyKBFlow Native Probe" `
  --hostname anykbflow-native-probe `
  --port 49152 `
  --txt probe=visibility `
  --txt role=windows-native-candidate `
  --allow-apple-service `
  --observe-tcp `
  --seconds 60
```

Expected evidence:

- macOS `dns-sd -B` sees `AnyKBFlow Native Probe`.
- macOS `dns-sd -L` resolves the Windows host, port, and TXT keys.
- `rapportd` and `UniversalControl` logs either ignore the service or record a
  concrete discovery/rejection reason.
- The redacted Mac watcher summary reports whether native stream, target/input,
  or sync/layout keyword counters changed. Nonzero counts for `RPStreamServer`,
  `P2PStream`, `TargetBegin`, `TargetConnect`, `TargetReply`, `Initial Sync`,
  or `Remote Display Layout` are stronger than generic browse/resolve.
- The same summary reports `nearbyd` and `wifip2pd` activity plus
  proximity/ranging and AWDL/Wi-Fi P2P keyword counts. Those counts help
  distinguish an eligibility/transport side-channel reaction from plain
  DNS-SD visibility.
- The Windows TCP observer records whether anything connects to the advertised
  port and, if data is sent immediately, bounded read counts, byte counts, and
  hex lengths without raw payload bytes.
- `scripts/windows/summarize-native-admission-output.py` creates the commit-safe
  Windows summary from the ignored command transcript.
- The committed observation is generated from the watcher artifact summary, not
  from raw `dns-sd` or unified-log output.

Do not treat a successful browse/resolve as native admission. Native admission
requires `rapportd` or `UniversalControl` evidence that the peer became a
candidate or was rejected for a known reason.

## Experiment 4: Shape-Only CompanionLink Candidate

This uses the local macOS baseline in
`docs/observations/2026-06-06-redacted-macos-uc-probe.md`, not real TXT values.
The Windows advertisement publishes `_companion-link._tcp` with placeholder
values that match the observed key set and value classes:

- `rpAD`, `rpHA`, `rpHI`, `rpHN`: hex length 12
- `rpBA`: MAC-like placeholder
- `rpFl`: `0x`-prefixed hex, seven TXT bytes with five hex digits
- `rpMac`: hex length 1
- `rpVr`: number

On macOS first:

```sh
./scripts/mac/capture-native-admission.sh --mode shape
```

Manual equivalent:

```sh
./scripts/mac/watch-companion-link-candidate.sh \
  --duration 90 \
  --instance "AnyKBFlow Native Shape Probe"
./scripts/mac/summarize-mdns-watch-artifact.py artifacts/mac-mdns-watch-YYYYMMDDTHHMMSSZ \
  --expected-instance "AnyKBFlow Native Shape Probe" \
  --output docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md
```

On Windows while the macOS watcher is running:

```powershell
python scripts/windows/capture-native-admission.py --mode shape
```

Manual equivalent:

```powershell
cargo run -- advertise-companion-link-shape `
  --acknowledge-shape-experiment `
  --observe-tcp `
  --seconds 60
```

The wrapper writes a raw transcript under ignored `artifacts/` and a redacted
summary under `docs/windows-inbox/`. Manual capture plus summary:

```powershell
cargo run -- advertise-companion-link-shape `
  --acknowledge-shape-experiment `
  --observe-tcp `
  --seconds 60 *> artifacts/windows-native-admission-shape.txt
python scripts/windows/summarize-native-admission-output.py `
  artifacts/windows-native-admission-shape.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md
```

Pair the redacted Mac and Windows summaries:

```sh
./scripts/compare-native-admission-pair.py \
  docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md \
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md \
  --label shape \
  --output docs/observations/YYYY-MM-DD-redacted-native-admission-shape-pair.md
```

The Windows summary preserves accepted connection counts, per-connection read
counts, total byte counts, first-read byte counts, hex-string lengths,
read-limit status, and peer-close-after-data status without committing raw peer
addresses or payload bytes.

This command intentionally does not copy identifiers, certificates, account
material, hostnames, or real `rp*` values from an Apple device. With
`--observe-tcp`, it opens a bounded listener on the advertised port only to log
connection attempts and bounded read-shape metadata. It does not speak Rapport.
Use any accepted connection as evidence to build a real framing probe next, not
as Universal Control admission.

After the minimal and shape-only summaries are committed or staged locally,
compare their redacted Mac-side effects:

```sh
./scripts/mac/compare-mdns-watch-summaries.py \
  docs/observations/YYYY-MM-DD-redacted-companion-link-candidate.md \
  docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md \
  --before-label minimal \
  --after-label shape \
  --output docs/observations/YYYY-MM-DD-redacted-companion-link-candidate-compare.md
```

Compare their redacted Windows-side TCP observer behavior:

```powershell
python scripts/windows/compare-native-admission-summaries.py `
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-companion-link.md `
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md `
  --before-label minimal `
  --after-label shape `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-compare.md
```

## Experiment 5: Apple Peer TXT Shape

Only run this when a real Mac or iPad Universal Control peer is available.

1. Capture an Apple-to-Apple `_companion-link._tcp` resolve while Universal
   Control is enabled.
2. Redact values but preserve TXT key names, value length/class, service type,
   port, and address count.
3. Compare that shape with the local Mac's self-advertisement and the minimal
   Windows candidate above using `scripts/mac/compare-uc-probe-summaries.py`
   when both sides have redacted baseline summaries.
4. Only after that, consider a Windows `_companion-link._tcp` advertisement that
   uses a structurally similar non-sensitive TXT shape.

This experiment is about protocol shape, not bypassing account identity or
private trust. Stop if logs show rejection that depends on Apple Account,
iCloud Keychain, private certificates, or platform attestation.

## Experiment 6: Apple-To-Apple Session Trace

Only run this when Universal Control can actually transfer focus to a Mac or
iPad target.

On the source Mac:

```sh
./scripts/mac/capture-uc-session.sh --duration 120
./scripts/mac/summarize-uc-session-artifact.py artifacts/mac-uc-session-YYYYMMDDTHHMMSSZ \
  --output docs/observations/YYYY-MM-DD-redacted-uc-session.md
```

When packet capture is required and you are ready to handle raw `.pcap` files:

```sh
./scripts/mac/capture-uc-session.sh --duration 120 --tcpdump
```

Use the action timeline written in the artifact README: idle, edge push, pointer
movement, one harmless key press, one scroll, return to local, then idle. The
goal is to label which logs and network streams change at each action before
attempting any Windows native handshake.
