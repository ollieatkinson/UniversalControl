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

- Windows now reports an Apple Account/iCloud surface worth testing:
  `docs/windows-inbox/2026-06-07-redacted-apple-account-environment.md` has
  `apple_account_surface_present`. Manual same-Apple-Account confirmation is
  still required and must not be written to git as an account identifier.
- Windows WSL/Rust mDNS did not resolve the Mac's `_companion-link._tcp`
  advertisement in
  `docs/windows-inbox/2026-06-07-redacted-companion-link-discovery.md`, but a
  native Windows Rust mDNS run did resolve both the Mac Apple/Rapport-shaped
  service and the Mac project-owned Bonjour probe in
  `docs/windows-inbox/2026-06-07-20260607T102817Z-redacted-native-windows-companion-link-discovery.md`.
- The first native Windows TCP check reached the Mac probe's resolved endpoint
  shape, but TCP connect failed with connection refused because the Mac Bonjour
  probe was only registered with `dns-sd -R` and had no listener; see
  `docs/windows-inbox/2026-06-07-native-windows-companion-link-tcp-check.md`.
- macOS has not yet proven it can see a Windows-advertised service on the real
  LAN path. A manual macOS Bonjour watch advertised a project-owned
  `_companion-link._tcp` probe and saw no Windows `_companion-link` instance;
  see `docs/observations/2026-06-07-redacted-macos-bonjour-cross-visibility.md`.
- macOS has not yet been observed reacting to a Windows `_companion-link._tcp`
  candidate in `rapportd` or `UniversalControl` logs.
- `cargo run -- probe displays` now has a local macOS single-display observation,
  and the bridge smoke probes confirm macOS native display detection feeds local
  routing, input-owner `Hello`, and loopback JSON-lines transport; this still
  needs native Windows-terminal output, external-monitor macOS output, and mouse
  coordinate comparison against a live two-machine run.

## Experiment 0: Windows Apple Account Environment

Run this from a native Windows terminal, not WSL, before deciding whether the
same-Apple-Account trust gate is blocked:

```powershell
python scripts/windows/capture-apple-account-environment.py
```

The wrapper writes a sanitized JSON transcript under ignored `artifacts/` and a
redacted Markdown summary under `docs/windows-inbox/`. It records only
environment shape:

- iCloud, Apple, and Bonjour installed product/package names and versions
- Apple/iCloud/Bonjour service and process names
- presence of known iCloud/Bonjour executable candidates without paths
- presence and value-name classes for Apple account-related registry keys
- count and class of Apple-related Credential Manager targets without target
  names
- count of Apple-related certificates by store, including private-key counts,
  without certificate subjects

It deliberately does not include Apple Account identifiers, credential target
names, registry values, certificate subjects, install paths, hostnames,
usernames, or IP addresses.

Interpretation:

- `apple_account_surface_present`: supported Apple software plus local account
  or credential clues exist. Manually confirm the Windows Apple software is
  signed in to the same Apple Account as the Mac, then keep native trust work
  open.
- `installed_but_no_account_surface_detected`: iCloud/Apple software exists,
  but the probe did not find account-state clues. Open the Apple UI locally and
  sign in before treating this as a native blocker.
- `apple_software_missing`: install iCloud for Windows or the relevant Apple
  Windows app before using identity absence as evidence against native
  Universal Control.

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

## Experiment 1A: Mac-To-Windows Bonjour Visibility

Use this when Windows has native Bonjour `dns-sd` installed and we need to
separate LAN/mDNS visibility from Rapport or Universal Control admission.

On macOS:

```sh
./scripts/mac/capture-bonjour-visibility.sh \
  --duration 300 \
  --observe-tcp \
  --observe-framing \
  --expected-remote-instance "AnyKBFlow Windows Bonjour Probe"
```

On Windows, browse first:

```powershell
dns-sd -B _companion-link._tcp local
```

Then advertise a project-owned probe:

```powershell
dns-sd -R "AnyKBFlow Windows Bonjour Probe" _companion-link._tcp local 49153 probe=windows-bonjour role=windows-native-visibility
```

Then connect to the exact Mac-controlled instance from native Windows:

```powershell
cargo run -- discovery connect `
  --service _companion-link._tcp.local. `
  --instance "AnyKBFlow Mac Bonjour Probe" `
  --allow-apple-service
```

Expected evidence:

- Windows browse sees the Mac's project-owned probe while the macOS script is
  running.
- macOS browse sees the Windows project-owned probe while the Windows
  `dns-sd -R` command is running.
- The Windows connect command reports `TCP probe connect result: success`.
- `scripts/mac/summarize-bonjour-visibility-artifact.py` writes a commit-safe
  summary preserving only counts, yes/no expected-instance matching, and the
  Mac TCP observer's peer classes plus length/timing/framing buckets.
- If either direction fails, record native Windows firewall state, network
  profile, Bonjour service state, and whether Bonjour is bound to the real LAN
  interface rather than WSL/NAT.

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
  proximity/ranging and AWDL/Wi-Fi P2P keyword counts after removing native
  process names from the matched text. Those counts help distinguish an
  eligibility/transport side-channel reaction from plain DNS-SD visibility.
- The Windows TCP observer records whether anything connects to the advertised
  port and, if data is sent immediately, bounded read counts, byte counts,
  read-length sequences, and timing buckets without raw payload bytes.
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

The wrapper writes a raw transcript under ignored `artifacts/`, a redacted
summary under `docs/windows-inbox/`, and a redacted AWDL comparison under
`docs/observations/`. Use `--skip-awdl-compare` only when the summary must be
generated without the committed Apple reconnect baseline.

Manual equivalent:

```powershell
cargo run -- advertise-companion-link-shape `
  --acknowledge-shape-experiment `
  --observe-tcp `
  --seconds 60
```

Manual capture plus summary, if bypassing the wrapper:

```powershell
cargo run -- advertise-companion-link-shape `
  --acknowledge-shape-experiment `
  --observe-tcp `
  --seconds 60 *> artifacts/windows-native-admission-shape.txt
python scripts/windows/summarize-native-admission-output.py `
  artifacts/windows-native-admission-shape.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md
```

After a run accepts a TCP connection, rerun the same coordinated shape capture
with non-payload framing hypotheses enabled:

```powershell
python scripts/windows/capture-native-admission.py --mode shape --framing-probe
```

Manual equivalent:

```powershell
cargo run -- advertise-companion-link-shape `
  --acknowledge-shape-experiment `
  --observe-tcp `
  --observe-framing `
  --seconds 60
```

Pair the redacted Mac and Windows summaries:

```sh
./scripts/compare-native-admission-pair.py \
  docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md \
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md \
  --label shape \
  --output docs/observations/YYYY-MM-DD-redacted-native-admission-shape-pair.md
```

The wrapper runs this AWDL comparison automatically for `shape` and
`companion-link` modes. Manual comparison command:

```sh
./scripts/compare-native-admission-awdl-baseline.py \
  docs/observations/2026-06-07-redacted-uc-session-reconnect.md \
  docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md \
  --baseline-label apple-reconnect-awdl \
  --windows-label shape \
  --output docs/observations/YYYY-MM-DD-redacted-native-admission-awdl-compare.md
```

Compare the Mac-side watcher summary against the real Apple-to-Apple session
signal-family baseline:

```sh
./scripts/mac/compare-native-signal-baseline.py \
  docs/observations/2026-06-07-redacted-uc-session.md \
  docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md \
  --baseline-label apple-session \
  --candidate-label shape \
  --output docs/observations/YYYY-MM-DD-redacted-native-signal-baseline-shape.md
```

The Windows summary preserves accepted connection counts, per-connection read
counts, total byte counts, first-read byte counts, read byte counts, read byte
sequences, inter-read gap buckets, safe redacted peer classes, Apple AWDL
length-family hits, read-limit status, and peer-close-after-data status without
committing raw peer addresses or payload bytes. It may also summarize
hex-string lengths from older transcripts, but current observer output is
length/timing only.

With `--framing-probe`, the Windows summary additionally preserves
first-byte-class buckets, entropy buckets, byte-diversity buckets,
length-prefix candidate counts, TLS-record-like counts, and compact framing
samples. These are byte-class and length hypotheses, not payload decoding.

This command intentionally does not copy identifiers, certificates, account
material, hostnames, or real `rp*` values from an Apple device. With
`--observe-tcp`, it opens a bounded listener on the advertised port only to log
connection attempts and bounded read-shape metadata. It does not speak Rapport.
Use any accepted connection as evidence to rerun with `--framing-probe`, not as
Universal Control admission.

If the paired report says `resolved_with_native_log_signal`, inspect the local
raw Mac watcher artifact before changing the Windows candidate shape. That tier
means the redacted Mac summary saw focused stream, target/input, sync/layout, or
candidate/rejection signal; it does not mean the Windows peer joined native
Universal Control.

If the baseline comparison says `resolved_with_session_like_signal`, prioritize
the raw Mac artifact window for local inspection before changing TXT shape or
TCP behavior. If it says only `resolved_with_side_channel_signal`, keep it
separate from stream/target/sync evidence and compare against the Apple session
side-channel counts before escalating.

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
private trust. Stop only if logs show rejection that depends on Apple Account,
iCloud Keychain, private certificates, or platform attestation that Windows
cannot satisfy through supported Apple software such as iCloud for Windows or a
future Apple Account CLI login.

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

For already-retained old sessions, use the historical log summarizer before
digging through raw local logs:

```sh
./scripts/mac/summarize-historical-uc-log.py \
  --start "YYYY-MM-DD HH:MM:SS" \
  --end "YYYY-MM-DD HH:MM:SS" \
  --context "commit-safe operator note" \
  --output docs/observations/YYYY-MM-DD-redacted-historical-uc-log.md
```

Use the action timeline written in the artifact README: idle, edge push, pointer
movement, one harmless key press, one scroll, return to local, then idle. The
goal is to label which logs and network streams change at each action before
attempting any Windows native handshake. The paired summary reports focused
native stream, target/input, sync/layout, proximity/ranging, and AWDL/Wi-Fi P2P
counters so the Windows admission runs can be compared against the signal
families a real Apple peer produces. The packet summary also preserves 250 ms
burst buckets and phase-window burst fingerprints so accepted Windows reads can
be compared against Apple reconnect and TargetConnect-adjacent structure
without payload bytes. Phase-window burst hints are only +/-2s correlations
around redacted log phase offsets; they are not decoded Universal Control
messages.

Historical summaries are count-only and can identify promising native
`UniversalControl`, `rapportd`, proximity, or Wi-Fi peer-to-peer windows, but
they are not a substitute for the labeled action trace above.
