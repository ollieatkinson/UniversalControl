# Research Log

## 2026-06-06

### Repository State

The local checkout and remote repository had no commits or branches when this work started. There were no existing Windows-machine notes in the worktree.

### Public Apple Requirements

Apple's Universal Control support page says the feature requires:

- at least one Mac
- macOS Monterey 12.4 or later for Mac participants
- iPadOS 15.4 or later for iPad participants
- the same Apple Account with two-factor authentication
- Bluetooth, Wi-Fi, and Handoff enabled
- nearby devices, up to 10 meters, with 1 meter recommended for troubleshooting
- no cellular tethering from iPad and no Internet Sharing from Mac

Source: <https://support.apple.com/en-us/102459>

Interpretation for Windows: a Windows peer probably cannot satisfy the same
Apple Account plus iCloud Keychain trust requirement by ordinary mDNS shape
alone. That does not prove native Universal Control interop is impossible, and
it does not rule out using a legitimate Windows Apple identity source such as
iCloud for Windows or a future CLI login. It defines the main feasibility gate:
can a Windows peer enter the required Rapport/CompanionLink trust/session path
through supported Apple Account material on Windows, public protocol
negotiation, or both, without extracting protected secrets or making false
platform claims?

### Public Continuity Security Model

Apple's Handoff security guide says Handoff-capable devices signed into iCloud establish a BLE pairing out-of-band using APNs, store a symmetric AES-256 key in Keychain, protect BLE advertisements with AES-GCM and replay protection, and can move larger payloads over Apple peer-to-peer Wi-Fi using TLS with trust derived from an iCloud Keychain identity.

Source: <https://support.apple.com/en-ie/guide/security/secf78dbe639/web>

Interpretation for Windows: if Universal Control inherits this Continuity trust machinery, direct Windows participation must reproduce or replace the identity layer. Replacing it is feasible for our own bridge; reproducing Apple's private iCloud trust is not a good first target.

### Published Reverse-Engineering Work

Stute et al., "Disrupting Continuity of Apple's Wireless Ecosystem Security", documents a structured method for Continuity reverse engineering using binary, system, network, and persistent-data vantage points. It maps Handoff and Universal Clipboard to BLE, AWDL, and Wi-Fi, and identifies relevant macOS components including `sharingd`, `bluetoothd`, `wirelessproxd`, `mDNSResponder`, `rapportd`, `useractivityd`, CoreBluetooth, Rapport, and CoreUtils.

Source: <https://www.usenix.org/system/files/sec21-stute.pdf>

Important scope note: that paper analyzes Handoff, Universal Clipboard, and Wi-Fi Password Sharing, not macOS Universal Control. Its Continuity-stack findings are useful starting points, but Universal Control-specific behavior must be proven separately.

### Local macOS Evidence

Host:

- macOS 26.5.1, build 25F80
- Darwin 25.5.0 arm64

Universal Control component:

- path: `/System/Library/CoreServices/UniversalControl.app/Contents/MacOS/UniversalControl`
- bundle identifier: `com.apple.universalcontrol`
- bundle version: `174.4.1`
- launchd label: `com.apple.ensemble`
- launchd plist: `/System/Library/LaunchAgents/com.apple.ensemble.plist`

Relevant running processes observed:

- `UniversalControl`
- `rapportd`
- `sharingd`
- `nearbyd`
- `useractivityd`
- `bluetoothd`
- `mDNSResponder`

Entitlements observed on `UniversalControl.app` include:

- `com.apple.CompanionLink`
- `com.apple.hid.manager.user-access-device`
- `com.apple.private.hid.client.admin`
- `com.apple.private.hid.client.event-dispatch`
- `com.apple.private.nearbyinteraction.device-presence`
- `com.apple.private.nearbyinteraction.privileged`
- `com.apple.private.skylight.universal-control`
- `com.apple.wifi.peer_traffic_registration`
- `com.apple.wifip2pd`
- Mach lookup exceptions for `com.apple.CompanionLink`, `com.apple.nearbyd.xpc.nearbyinteraction`, and `com.apple.wifip2pd`

Launchd event triggers observed for `com.apple.ensemble`:

- `com.apple.universalcontrol.discovery`
  - stream: `com.apple.rapport.matching`
  - monitor: `com.apple.rapportd`
  - descriptor type: `discovery`
  - service type: `_companion-link._tcp`
- `com.apple.universalcontrol.server`
  - stream: `com.apple.rapport.matching`
  - monitor: `com.apple.rapportd`
  - descriptor type: `server`
  - service type: `com.apple.universalcontrol`

Bonjour observations:

- `_companion-link._tcp.local` had a local instance for this Mac.
- The instance resolved to the dynamic `rapportd` TCP listener.
- TXT keys included Rapport-looking fields such as `rpVr`, `rpFl`, `rpHN`, `rpHA`, `rpAD`, `rpHI`, and `rpBA`.
- `_universalcontrol._tcp.local` had no local browse results during a short sample.

String evidence from the Universal Control binary includes:

- `CompanionLink`
- `CompanionLinkClient`
- `CompanionLinkServer`
- `P2PDirectLink`
- `P2PBrowser`
- `P2PStream`
- `P2PMessage`
- `AWDL`
- `OPACKCoding`
- `EnsembleHID`
- `HIDReportAccumulator`
- `PointerController`
- `EventController`
- `PasteboardController`
- `DragSourceCoordinator`
- `DragSinkCoordinator`
- log messages for `CLink Activated`, `P2PDirectLink Activated`, focus movement, target readiness, keyboard readiness, pointer movement, and local keyboard report removal

### Working Hypothesis After First Pass

Universal Control is probably an "Ensemble" application layered over Rapport/CompanionLink for discovery and session setup, NearbyInteraction/proximity for eligibility, Wi-Fi peer-to-peer/AWDL for low-latency paths, OPACK-like messages for structured control, and HID reports for input transport.

The next proof step is a paired-device capture while a second Mac or iPad is actively linked. Without a paired Apple peer, we can see the local advertisement and launchd triggers but not the Universal Control session messages.

### Repo-Native Discovery Probe

Added a read-only Rust CLI probe:

```sh
cargo run -- discover-companion-link --seconds 10
```

Backends:

- `auto`: use system `dns-sd` when available, otherwise the Rust mDNS backend.
- `system`: call `dns-sd -B _companion-link._tcp local`.
- `rust-mdns`: use the `mdns-sd` crate to browse `_companion-link._tcp.local.` and print found/resolved/removed events.

Local validation on macOS:

- `--backend system` saw this Mac's `_companion-link._tcp` advertisement.
- `--backend rust-mdns` resolved this Mac's `_companion-link._tcp` service and printed the dynamic Rapport port plus `rp*` TXT keys.
- Raw output was not committed because it includes local hostnames and stable-looking TXT values.

Added redacted discovery output:

```sh
cargo run -- discover-companion-link --backend rust-mdns --seconds 30 --redact
```

This mode is intended for Windows-machine notes that can be committed. It preserves event type, service type, port, TXT key names, TXT value length/class, and address count, while hiding hostnames, addresses, instance names, and TXT values. Redaction is only available on the Rust mDNS backend; system `dns-sd` output remains raw pass-through output.

### Repo-Native Advertisement Probe

Added a bounded mDNS advertiser:

```sh
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
```

Defaults:

- service type: `_anykbflow-probe._tcp.local.`
- instance: `AnyKBFlow Probe`
- hostname: the local machine hostname, unless `--hostname` is supplied
- port: `49152`

The command rejects Apple-owned service types such as `_companion-link._tcp` unless `--allow-apple-service` is supplied. That guard keeps routine visibility checks separate from controlled native-compatibility experiments.

Local validation on macOS:

- `dns-sd -B _anykbflow-probe._tcp local` saw the advertised `AnyKBFlow Probe` service.
- `dns-sd -L "AnyKBFlow Probe" _anykbflow-probe._tcp local` resolved the hostname, port, and TXT values.
- Because this validation ran on one Mac, the resolver reported the loopback interface; Windows-to-Mac visibility still needs a Windows-machine report.

### macOS mDNS Watcher

Added a bounded Mac-side watcher:

```sh
./scripts/mac/watch-mdns-service.sh --duration 60
```

It writes an ignored artifact directory containing:

- `dns-sd -B` output for the selected service type
- `dns-sd -L` output for the selected instance
- unified logs for `UniversalControl`, `rapportd`, and `mDNSResponder`
- launchd state snapshots for `com.apple.ensemble` and `com.apple.rapportd`

This is intended to run while Windows advertises `_anykbflow-probe._tcp` or a controlled `_companion-link._tcp` experiment. Raw output is not committed because it can contain hostnames, addresses, TXT values, and local interface identifiers.

Added a native-specific wrapper:

```sh
./scripts/mac/watch-companion-link-candidate.sh --duration 90 --instance "AnyKBFlow Native Probe"
```

It wraps the generic watcher with service type `_companion-link._tcp` so a
Windows-controlled candidate advertisement can be observed together with
`rapportd`, `UniversalControl`, and `mDNSResponder` logs. This is the next
candidate-admission smoke test after basic Windows-to-macOS mDNS visibility is
proven.

Added a watcher summarizer:

```sh
./scripts/mac/summarize-mdns-watch-artifact.py artifacts/mac-mdns-watch-YYYYMMDDTHHMMSSZ
```

It emits commit-safe Markdown from ignored watcher artifacts. The summary
preserves service type, browse/resolve counts, expected-instance match,
published port, TXT key names, TXT value classes, launchd state, and native
process log counts, but omits raw hostnames, addresses, instance names, TXT
values, interface identifiers, and unified-log lines.

Added a baseline macOS probe summarizer:

```sh
./scripts/mac/summarize-uc-probe-artifact.py artifacts/mac-uc-probe-YYYYMMDDTHHMMSSZ
```

It emits commit-safe Markdown from ignored `uc-probe.sh` artifacts. The summary
preserves OS/build, Universal Control bundle metadata, entitlement key names,
launchd Rapport matching triggers, DNS-SD browse/resolve counts, `rp*` TXT key
names and value classes, rapportd socket shape, binary-string hint counts, and
redacted Rapport event/message IDs. It omits raw hostnames, addresses, hardware
addresses, Bluetooth IDs, TXT values, defaults values, and unified-log lines. A
generated summary from the first local probe lives in
`docs/observations/2026-06-06-redacted-macos-uc-probe.md`.

Added a redacted-summary comparer:

```sh
./scripts/mac/compare-uc-probe-summaries.py docs/observations/before.md docs/observations/after.md
```

It compares commit-safe baseline probe summaries and reports added, removed, and
changed fields while ignoring source artifact name and timestamp by default.
This is meant for Universal Control disabled/enabled/active-peer state
comparisons without exposing the raw probe artifacts.

Added a paired-session capture wrapper:

```sh
./scripts/mac/capture-uc-session.sh --duration 120
./scripts/mac/summarize-uc-session-artifact.py artifacts/mac-uc-session-YYYYMMDDTHHMMSSZ
```

It captures CompanionLink and Universal Control DNS-SD browsing, unified logs,
launchd snapshots, and `lsof` network snapshots during a real Apple-to-Apple
Universal Control edge-push session. Passing `--tcpdump` additionally records
raw packet captures on `en0` and `awdl0` when present. Raw session artifacts stay
under `artifacts/`; only redacted summaries should be committed. The summarizer
preserves service counts, native process keyword counts, launchd state, network
snapshot counts, and packet-capture file sizes, but omits raw hostnames,
addresses, instance names, interface identifiers, packet payloads, and
unified-log lines.

### Windows Bridge Progress Versus Native Gap

Windows-side notes now show the separate AnyKBFlow bridge track can advertise
`_anykbflow._tcp.local.`, discover that service from the receiver role, keep a
TCP JSON-lines session alive with heartbeats, and reconnect after receiver
process restarts under WSL. The receiver also tracks injected key/button state
and releases those inputs when the peer disconnects, plus releases common
latch-prone modifiers/buttons at receiver session start and when planned focus
return marks the receiver inactive. The input owner now also resets routing
state when the receiver connection closes. Those cleanup paths have not yet been
runtime-tested with native macOS/Windows input injection. Bridge display geometry
now prefers runtime primary-display detection on native macOS/Windows: peer
`Hello` messages carry each side's detected display size, the input owner
replaces configured remote-dimension fallbacks after the receiver hello, and
local edge routing uses the input owner's detected display before falling back to
config. WSL still uses the stub fallback, so native Windows-terminal output is
needed. A repo-native display geometry probe is also available as
`cargo run -- probe displays`. The first macOS run returned `displays: 0`
through `display-info` because CoreGraphics active-display enumeration was empty
while the built-in display was still online but asleep. The probe now falls back
to CoreGraphics online-display enumeration on macOS and produced a redacted
single-display observation in
`docs/observations/2026-06-06-local-macos-display-probe.md`. It still needs
native Windows output, external-monitor macOS output, and comparison with
`probe listen` mouse coordinates during live edge routing.

Mac-side `probe bridge-smoke` now also prints the input-owner `Hello` generated
by the real peer-protocol helper. A local macOS run in
`docs/observations/2026-06-06-local-macos-bridge-smoke.md` used detected
`1710x1112` display geometry for both local edge routing and
`Hello.local_display`, overriding the stale `2560x1440` example-config fallback.
It emitted the expected `active=true`, remote mouse move, and `KeyA`
press/release messages. The same observation also records a successful
`probe bridge-network-smoke` run over loopback TCP using the real JSON-lines peer
tasks. Because both loopback endpoints ran on one Mac, both hello messages used
the same detected Mac display geometry; this validates the native hello path and
transport shape on macOS, not remote Windows geometry. This does not close any
native Universal Control admission gate.

Those bridge observations are useful fallback progress, but they do not prove
native Universal Control compatibility. The native-first gaps remain:

- Windows still needs a redacted Rust mDNS browse proving whether it can resolve
  the Mac's `_companion-link._tcp` advertisement on the real network.
- macOS still needs to resolve a Windows-advertised benign probe on the real
  network.
- macOS still needs a controlled `_companion-link._tcp` candidate run to show
  whether `rapportd` or `UniversalControl` ignores, accepts, or rejects a
  Windows-owned candidate.

### Normalized Event Replay Probe

Added `cargo run -- probe replay-events --path <jsonl> --delay-ms <ms>`.
The command reads the same normalized `InputEvent` JSONL emitted by
`probe listen-events` and `probe grab-events`, then feeds each event through the
platform injector used by the receiver role. This is the next bridge between
passive capture and the full two-machine daemon: capture a short sequence on one
machine, copy or commit a redacted sample, and replay it on the other with a
controlled foreground target.

This still does not prove native Universal Control compatibility. It proves the
fallback software-KVM event shape is internally replayable across macOS and
Windows once native capture/injection permissions are working.

### Native macOS Priority

The preferred Mac-side architecture is to leave Apple's `UniversalControl.app` in control. The Windows side should first try to become visible to native macOS discovery and session setup. A Mac-side bridge should be treated as a fallback only after captures prove one of these hard blockers:

- macOS rejects the Windows peer before Universal Control-specific messages are exchanged.
- Authentication requires Apple Account, IDS, iCloud Keychain, or
  entitlement-protected material unavailable through supported Windows Apple
  software or APIs.
- The accepted peer path requires Apple-private HID or proximity claims that cannot be represented externally.
- Native Universal Control messages can be observed but not generated without protected keys or signatures.

### Private Framework Inspection Note

`Rapport.framework`, `CompanionServices.framework`, and `Ensemble.framework` are present as private frameworks. On this macOS 26.5.1 installation their framework executable symlinks are unresolved on the normal system path because the binaries are supplied through the dyld shared cache.

The relevant cache path found locally is:

```text
/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e
```

Later symbol or string inspection of private frameworks should use dyld shared cache tooling rather than assuming the framework symlink points to a standalone Mach-O file.

## 2026-06-07

### Native Feasibility Position

Added `docs/native-feasibility.md` to make the native-first decision explicit.
The Mac side should stay on Apple's `UniversalControl.app` while Windows can
advance through observable Rapport/CompanionLink and
`com.apple.universalcontrol` gates, including a legitimate Windows Apple Account
identity path if required.

Checked Apple's current Universal Control support page and Handoff security
guide on 2026-06-07:

- Universal Control still lists same Apple Account with two-factor
  authentication, Bluetooth, Wi-Fi, and Handoff as requirements.
- Handoff security still describes iCloud-mediated BLE pairing,
  Keychain-stored symmetric keys, protected advertisements, and larger
  peer-to-peer Wi-Fi transfers whose TLS trust derives from an iCloud Keychain
  identity.

Sources:

- <https://support.apple.com/en-us/102459>
- <https://support.apple.com/guide/security-pdf/handoff-security-secf78dbe639/web>

Interpretation for Windows: native Universal Control is not disproven, but it
is high risk. The immediate proof gates are a native Windows Apple
Account/iCloud environment report, Windows passive browsing of the Mac
`_companion-link._tcp` advertisement, macOS visibility of a benign Windows mDNS
probe, a controlled Windows `_companion-link._tcp` candidate run with macOS
`rapportd`/`UniversalControl` logs, and Apple-to-Apple baseline captures before
any deeper Windows native handshake attempt.

### Windows Apple Account Environment Probe

Added `scripts/windows/capture-apple-account-environment.py` so the Windows
machine can report whether a legitimate Apple Account path is locally plausible
before native admission is declared blocked. The probe is meant to run from a
native Windows terminal and writes:

- a sanitized JSON transcript under ignored `artifacts/`
- a redacted Markdown summary under `docs/windows-inbox/`

It records supported-software and account-surface shape only: iCloud, Apple,
and Bonjour product/package names, Apple service/process names, known
executable candidate presence without paths, account-related registry surface
presence and value-name classes without values, Apple-related Credential
Manager target counts without target names, and Apple-related certificate counts
without subjects.

The summary deliberately omits Apple Account identifiers, credential target
names, registry values, certificate subjects, install paths, hostnames,
usernames, and IP addresses. A human still needs to confirm locally that the
Windows Apple software is signed in to the same Apple Account as the Mac.

### Shape-Only CompanionLink Candidate

Added `cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment`.
It advertises `_companion-link._tcp` with deterministic placeholder `rp*` TXT
values matching the redacted local macOS baseline key/value classes:

- `rpAD`, `rpHA`, `rpHI`, `rpHN`: hex length 12
- `rpBA`: MAC-like placeholder
- `rpFl`: `0x`-prefixed hex, seven TXT bytes with five hex digits
- `rpMac`: hex length 1
- `rpVr`: number

This is a controlled DNS-SD shape experiment, not a native Universal Control
implementation. It does not copy Apple identifiers or account material and does
not speak Rapport. `--observe-tcp` can be added to advertise commands to open a
bounded TCP listener on the advertised port and log connection attempts plus
length/timing-only read metadata. The next evidence needed is a Mac-side watcher
summary comparing this shape-only candidate against the minimal
`probe=visibility` candidate, along with the Windows TCP observer summary, to
see whether `rapportd` or `UniversalControl` ignores it, attempts a connection,
or logs a concrete rejection reason.

### Native Admission Capture Wrapper

Added `scripts/mac/capture-native-admission.sh` for the immediate
Windows-to-macOS native admission checks:

```sh
./scripts/mac/capture-native-admission.sh --mode benign
./scripts/mac/capture-native-admission.sh --mode companion-link
./scripts/mac/capture-native-admission.sh --mode shape
```

The wrapper prints the matching Windows advertisement command, runs the correct
macOS watcher, stores raw artifacts under ignored `artifacts/`, and writes a
redacted `docs/observations/` summary through
`scripts/mac/summarize-mdns-watch-artifact.py`. It does not replace the raw
watcher scripts; it just removes the manual artifact-directory lookup during
coordinated LAN runs.

### Bridge Preflight

Added `cargo run -- --config <path> preflight` for the project-owned fallback
bridge. It validates config and prints the role, capture mode, configured
display dimensions, detected primary display when available, effective local
display, peer/listen mode, service name, and warnings before a daemon run.

This does not advance native Universal Control admission, but it improves the
fallback two-machine prototype path by making stale dimensions, missing native
display detection, loopback listen addresses, and receiver loopback peer
addresses visible before starting global input capture.

### mDNS Watch Summary Comparer

Added `scripts/mac/compare-mdns-watch-summaries.py` to compare two redacted
watcher summaries. The intended first use is minimal CompanionLink candidate
versus shape-only CompanionLink candidate, preserving the Mac-side browse,
resolve, TXT-shape, native log count, and interpretation differences without
committing raw DNS-SD or unified-log output.

### Windows Native Admission Output Summary

Added `scripts/windows/summarize-native-admission-output.py` to turn the Windows
side of coordinated native-admission runs into commit-safe Markdown. It reads
the ignored transcript from commands such as
`advertise-companion-link-shape --observe-tcp` and preserves service type, port,
observer status, accepted connection count, first-read byte counts, and
first-read hex lengths from older transcripts while redacting peer addresses,
hostnames, and payload bytes.

This pairs with the Mac-side `capture-native-admission.sh` summary so one
commit can contain both sides of the same admission attempt without raw network
identifiers.

Added `scripts/windows/compare-native-admission-summaries.py` to compare two
redacted Windows native-admission summaries. The intended first use is minimal
CompanionLink candidate versus shape-only CompanionLink candidate, preserving
the Windows-side advertised service/port, TCP observer status, accepted
connection counts, connection outcomes, first-read byte counts, and first-read
hex lengths without raw peer addresses or payload bytes.

Expanded the `--observe-tcp` admission observer from a single first-read sample
to a bounded multi-read transcript. It still avoids committing raw payloads:
the Windows summarizer preserves accepted connection counts, read counts, byte
counts, read durations, hex-string lengths, read-limit status, and peer-close
status. This is the next useful evidence if macOS resolves a Windows
`_companion-link._tcp` candidate and attempts the advertised port.

After the Apple-to-Apple AWDL payload-length fingerprints were added, hardened
the Windows TCP observer for comparable native-admission evidence:

- increased the read buffer from 256 bytes to 4096 bytes so 621 and 1428 byte
  Apple-session-sized reads are not clipped by the observer
- increased the bounded read limit from 8 to 16 reads
- stopped printing payload hex in new observer output
- added first-read elapsed time and per-read length-only lines
- taught `scripts/windows/summarize-native-admission-output.py` to preserve read
  byte counts, per-connection read byte sequences, inter-read gap buckets, and
  small/large Apple AWDL length-family hit counts
- kept the summarizer backward-compatible with older local transcripts that
  included hex prefixes, preserving only hex-string lengths in committed
  summaries

This makes the Windows admission report comparable with the Apple AWDL
length/gap fingerprints without storing TCP payload bytes in terminal output or
git.

Added `scripts/windows/capture-native-admission.py` to mirror the Mac-side
native-admission wrapper. It prints the matching macOS watcher command, runs
the selected Windows advertisement mode, stores the raw transcript under ignored
`artifacts/`, and writes a redacted Windows summary under `docs/windows-inbox/`.
This removes manual shell redirection from the coordinated benign, minimal
CompanionLink, and shape-only admission runs.

### Local macOS Bridge Preflight

Recorded `docs/observations/2026-06-07-local-macos-bridge-preflight.md` after
running `probe displays` plus input-owner and receiver `preflight` on native
macOS. The preflight path detected `1710x1112`, matched `probe displays`, used
that as the effective local display for both stale example configs, selected
`peer_mode=mdns_discovery` for the receiver config with no `peer_addr`, and
reported zero warnings. This answers the Windows bridge-preflight note, but it
does not advance native Universal Control admission.

### Native Admission Pair Report

Added `scripts/compare-native-admission-pair.py` to combine a redacted macOS
watcher summary with a redacted Windows native-admission output summary. The
paired report highlights DNS-SD visibility, resolve success, native macOS log
signals, Windows TCP observer connection evidence, and a coarse admission tier
such as `not_visible`, `browse_only`, `resolved_no_tcp_attempt`, or
`resolved_with_tcp_attempt`.

This is intended to be the final committed artifact for each Windows admission
attempt, alongside the individual Mac and Windows redacted summaries.

### Unknown Input Mapping Guard

Changed native replay and injection mapping so unsupported normalized key or
mouse button names fail with explicit errors instead of silently mapping to
`rdev::Key::Unknown(0)` or `rdev::Button::Unknown(0)`. This keeps bridge and
replay tests from hiding layout or platform-specific key gaps. If native macOS
or Windows captures produce an unsupported name, commit the exact redacted
failure context and add the intended mapping deliberately.

Added `cargo run -- probe replay-events --path <file> --dry-run` so native
macOS and Windows spike files can be parsed and mapped without sending
synthetic input. Use this before full replay when validating Keychron captures
or new platform-specific key names.

### Refreshed macOS Universal Control Probe

Recorded `docs/observations/2026-06-07-redacted-macos-uc-probe.md` and
`docs/observations/2026-06-07-redacted-macos-uc-probe-compare.md` from a fresh
read-only `scripts/mac/uc-probe.sh` artifact. The CompanionLink DNS-SD baseline
stayed stable: `_companion-link._tcp` browse/resolve was observed, the listener
port remained `61833`, and the redacted TXT key/value classes still matched the
shape-only Windows advertiser. The comparison against the 2026-06-06 probe only
changed recent unified-log counters and parsed Rapport event/message IDs.

Fixed `scripts/mac/summarize-uc-probe-artifact.py` to parse normal `dns-sd`
timestamp lines with leading whitespace. Without that, a valid browse/resolve
capture could be summarized incorrectly as `Events: none observed`.

### Redacted Rust CompanionLink Discovery Baseline

Added `scripts/windows/summarize-companion-link-discovery-output.py` to turn
`discover-companion-link --backend rust-mdns --redact` transcripts into
commit-safe Markdown summaries. It preserves search/found/resolved counts,
service type, port, redacted host/fullname lengths, address counts, and TXT
key/value length classes.

Added `scripts/windows/capture-companion-link-discovery.py` as the matching
Windows passive-browse wrapper. It runs the redacted Rust mDNS browse, stores
the transcript under ignored `artifacts/`, and writes the redacted summary under
`docs/windows-inbox/`. The wrapper refuses the system backend unless explicitly
acknowledged because `dns-sd` output is not automatically redacted.

Recorded `docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md`
from `cargo run -- discover-companion-link --backend rust-mdns --seconds 10
--redact`. The local Rust mDNS backend resolved `_companion-link._tcp.local.`
on port `61833`, preserved address count and redacted TXT key/value
length/classes, and confirmed the exact output shape Windows should produce for
the passive browse gate.

That run also exposed that `rpFl` is `0x`-prefixed in the Rust redacted output.
Updated the shape-only CompanionLink advertiser to use a non-sensitive
`0x`-prefixed placeholder and taught the Rust redactor to classify this as
`hex-prefixed` instead of generic text.

Updated the Mac-side UC probe and mDNS watcher summarizers to use the same
`hex-prefixed` class for `0x...` TXT values. Regenerated the 2026-06-06 and
2026-06-07 redacted macOS UC probe summaries from their raw artifacts so the
baseline, Rust mDNS discovery output, and shape-only Windows advertiser all
preserve the same `rpFl` wire shape.

Added `scripts/windows/compare-companion-link-discovery-summaries.py` so the
Windows passive browse summary can be compared directly against
`docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md`. The
comparison highlights service resolution, port, address count, TXT keys, and
TXT value length/classes while ignoring source transcript paths by default.

Added `scripts/windows/capture-display-probe.py` and
`scripts/windows/summarize-display-probe-output.py` for native Windows display
geometry capture. The summary redacts display names while preserving primary and
built-in flags, logical bounds, scale, rotation, refresh rate, physical size,
negative origins, and virtual bounds so bridge configs can be calibrated without
committing monitor names.

Added `scripts/windows/capture-companion-link-discovery.py` to make the passive
Windows browse gate one command. It runs
`discover-companion-link --backend rust-mdns --redact`, stores the raw transcript
under ignored `artifacts/`, writes a redacted discovery summary, and compares it
against the local macOS Rust mDNS baseline.

Added `scripts/capture-input-events.py` and `scripts/summarize-input-events.py`
for native macOS/Windows Keychron and mouse capture evidence. The capture
wrapper writes replayable normalized `InputEvent` JSONL under ignored
`artifacts/`, while the summary preserves event kinds, key/button names, text
length classes, pointer bounds, wheel deltas, and key press/release balance
without committing typed text values.

Added `cargo run -- --config <input-owner.toml> probe route-events --path <jsonl>`
to dry-run captured normalized input through the real edge router without native
hooks or network. The default report redacts key text and shows local
suppression, remote activation/deactivation, and forwarded input counts so the
macOS and Windows machines can prove a captured pointer path will switch peers
before running the full bridge daemon.

### UniversalControl String Surface

Added `scripts/mac/summarize-universalcontrol-strings.py` and recorded
`docs/observations/2026-06-07-redacted-universalcontrol-string-surface.md` from
the installed native Universal Control binary. The summary strips Apple build
roots down to source-relative paths and preserves only stable identifiers,
type/source hints, NearbyInteraction selectors, and prioritized log templates.

The current string surface strengthens the native-first capture plan: it names
`RapportStreamServer`, `P2PStream`, `P2PMessage`, `SyncController`,
`EventReport`, `EnsembleHIDController`, and `OPACKCoding`, plus log templates
for `RPStreamServer`, `P2PStream`, `Initial Sync`, send/receive messages,
remote display/source devices, `FocusMove`, `TargetBegin`, `TargetConnect`,
`TargetReady`, `TargetEvent`, `TargetReply`, and rejection/reset paths.

Updated `scripts/mac/summarize-mdns-watch-artifact.py` so future Windows native
admission captures count native stream, target/input, and sync/layout keyword
lines in addition to generic candidate/rejection counts. That makes a
controlled Windows advertisement more informative if it reaches deeper than
DNS-SD browse/resolve.

Extended `probe route-events` with `--expect-activation`,
`--expect-deactivation`, and `--min-forwarded-inputs`. The capture/replay handoff
can now fail fast when a native Keychron/mouse capture does not cross the
configured edge, does not return local when expected, or would forward too few
events to be useful for the two-machine bridge run.

Extended the Mac mDNS watcher to capture `nearbyd` and `wifip2pd` alongside
`UniversalControl`, `rapportd`, and `mDNSResponder`. The redacted watcher
summary now preserves process counts plus proximity/ranging and AWDL/Wi-Fi P2P
keyword counts. These are side-channel signals only, but they matter because
Apple's public requirements and the UniversalControl string surface both point
at NearbyInteraction and peer-to-peer Wi-Fi as likely native admission gates.

Extended `scripts/capture-input-events.py` with `--route-config`,
`--route-transcript`, and the same route expectation flags. Native macOS/Windows
testers can now capture Keychron/mouse JSONL, write the redacted input summary,
and fail the route gate in one command before attempting replay or the full
daemon.

Hardened the fallback bridge session handshake so each role rejects an unexpected
peer role in the initial `Hello` instead of only logging a warning. This reduces
the chance that a misconfigured two-machine run suppresses local input or
injects into the wrong side while still lacking transport authentication.

Updated the Apple-to-Apple Universal Control session summarizer to report the
same focused native signal families as the Windows admission watcher: stream,
target/input, sync/layout, proximity/ranging, and AWDL/Wi-Fi P2P. This keeps the
real Apple-peer baseline comparable with controlled Windows candidate runs.

### TCPDump-Backed Universal Control Session Summary

Processed `artifacts/mac-uc-session-20260607T072939Z` into
`docs/observations/2026-06-07-redacted-uc-session.md`. The raw artifact stays
ignored because it contains unified logs and packet captures.

The redacted summary preserved no DNS-SD browse rows for `_companion-link._tcp`
or `_universalcontrol._tcp`, but the active-session log counters did show native
UniversalControl/Rapport target/input, sync/layout, proximity/ranging, and
Wi-Fi peer-to-peer signal families. The pcap metadata decoded cleanly: 29,534
packet lines, split between an AWDL-class capture and a primary-network
capture, with TCP-heavy transport counts and protocol-relevant hits for ports
3722 and 5353.

The first version of `capture-uc-session.sh` left `dns-sd`, `log stream`, and
`tcpdump` descendants running after printing `Wrote`, so this artifact should be
treated as a useful active-session signal shape rather than an exact 120 second
window. The script now tears down descendant process trees with interrupt and
terminate signals, using a non-interactive `sudo kill` fallback for root-owned
tcpdump descendants.

### Historical Universal Control Log Window

Added `scripts/mac/summarize-historical-uc-log.py` so retained macOS unified-log
windows can be counted without writing raw log lines to disk. It is useful when
an Apple-to-Apple Universal Control session already happened but the matching
`capture-uc-session.sh` run was not started in time.

Recorded `docs/observations/2026-06-05-redacted-historical-uc-log.md` for a
reported Apple-to-Apple session window. It counted UniversalControl, Rapport,
NearbyInteraction, and Wi-Fi peer-to-peer signal families without committing
hostnames, addresses, device names, or raw log messages. The result is only a
coarse historical signal: it found native stream plus proximity/Wi-Fi P2P
families, but it is not a labeled action trace and cannot replace the fresh
120 second edge-push capture.

Updated both historical and session log counting to remove native process names
before matching signal keywords. This prevents `UniversalControl` process names
from inflating generic `control` counters and makes the specific stream,
target/input, sync/layout, proximity, and Wi-Fi P2P counters the stronger
evidence to compare against Windows native-admission attempts.

### Native Admission Gate Hardening

Updated the Mac mDNS watcher summarizer to remove native process names before
matching candidate, proximity, and Wi-Fi P2P keywords. This keeps
`nearbyd`/`wifip2pd` process presence from being counted as side-channel
protocol evidence by itself, aligning Windows-admission watcher summaries with
the stricter Apple session and historical-log summaries.

Updated `scripts/compare-native-admission-pair.py` to surface the focused Mac
watcher counters in the paired report and to classify a resolved service with
stream, target/input, sync/layout, candidate, or rejection log signal as
`resolved_with_native_log_signal` when no TCP observer connection is seen. If
both a TCP attempt and focused native-log signal appear, the pair report now
uses `resolved_with_tcp_attempt_and_native_log_signal`.

### Apple Session Baseline Comparator

Added `scripts/mac/compare-native-signal-baseline.py` to compare a redacted Mac
watcher summary from a Windows native-admission candidate against the real
Apple-to-Apple Universal Control session summary. It preserves only aggregate
signal-family counts and reports whether the candidate overlaps baseline
stream, target/input, sync/layout, proximity, or Wi-Fi P2P families.

This closes a review gap in the coordinated Windows experiments: the paired
Mac/Windows report can show visibility, resolve, TCP observer behavior, and
native-log signal, while the baseline comparison answers whether the Mac-side
candidate signal resembles the focused families seen during a real Apple peer
session. Side-channel-only overlap stays below stream, target/input, and
sync/layout overlap when deciding whether to inspect raw local artifacts or
build a richer Windows listener.

### Local Universal Control Link-Loss Health

After the operator reported that the Universal Control mouse-link option
disappeared or stopped working, extended `scripts/mac/uc-probe.sh` and its
summarizer with redacted continuity-health checks. The probe now records Wi-Fi,
the detected Wi-Fi interface, AWDL, firewall block-all state, Universal Control
ByHost preference-cache shape, display-cache shape, and broader
Rapport/Sharing/UserActivity health-log counts without committing local
addresses, hardware addresses, display UUIDs, configuration blobs, or raw log
lines.

Recorded `docs/observations/2026-06-07-redacted-macos-uc-link-loss-health.md`
from the affected Mac. The local transport and Rapport/CompanionLink surfaces
looked healthy: Wi-Fi, the Wi-Fi interface, and AWDL were active, firewall
block-all was not enabled, `_companion-link._tcp` browse/self-resolve worked,
and `rapportd` kept its listener. The suspicious signals were local
session/display state: no UniversalControl network sockets, an existing
Universal Control ByHost configuration cache, collapsed/nonzero-origin
display-cache records, and a broader continuity log window with Rapport/Sharing
activity but no UniversalControl lines.

Recovery should therefore start with restarting/toggling Universal Control and,
if needed, moving only the ByHost `com.apple.universalcontrol.*.plist` aside
before touching wider display preferences.

### Apple Session Flow Shape

Extended `scripts/mac/summarize-uc-session-artifact.py` to decode local pcap
files into redacted TCP flow shapes. The summary now preserves endpoint classes,
port classes, packet counts, payload byte counts, payload-packet counts, max
payload size, flag classes, relative timing, and mDNS service mentions while
omitting endpoints, dynamic ports, and payload bytes.

Regenerated
`docs/observations/2026-06-07-redacted-uc-session.md` from the tcpdump-backed
Apple-to-Apple session. The strongest implementation clue is a dominant AWDL
IPv6 link-local dynamic-port TCP flow that starts near the beginning of the
active window, carries most AWDL payload bytes, and lasts through most of the
capture. Native Windows admission attempts should be compared against this
AWDL high-port flow shape before spending effort on generic primary-network
HTTPS traffic.

Extended the same summarizer again to preserve direction-neutral
payload-length fingerprints for the top TCP flows: per-direction payload
packet/byte counts, top payload lengths, the first 24 nonzero payload lengths,
and inter-payload gap buckets. Direction labels are arbitrary within a flow, and
the summary still omits raw endpoints, dynamic ports, and payload bytes.

Regenerated both 2026-06-07 Apple-to-Apple session summaries. The reconnect
baseline now shows two AWDL IPv6 link-local dynamic-port TCP flows with distinct
length signatures:

- a high-rate small-message flow dominated by repeated 122/93 byte payloads in
  one direction, with smaller 55/82/140/174 byte responses
- a lower-rate larger-message flow with repeated 621 and 1428 byte payloads in
  both directions

Those length fingerprints are now the best non-payload comparison target for a
future Windows native-admission listener. A Windows TCP attempt that only looks
like generic HTTPS or mDNS noise should not be treated as Universal Control data
path progress; an attempt that starts to resemble the AWDL length/gap pattern is
worth a targeted framing probe.

### Bridge Hello Authentication

Added optional shared-secret authentication for the AnyKBFlow bridge `Hello`
message. When `[auth].shared_secret` is configured on both peers, each side
sends a nonce-backed HMAC-SHA256 proof over its hello identity, role, and display
geometry. The receiver verifies the proof before accepting the peer role or
injecting routed input. This does not encrypt event traffic and is not final
interactive pairing; it rejects peers that cannot produce the configured proof
but is not replay-proof against an observer who can capture the plaintext
session.

### Reconnect-Capable Apple Session Baseline

Captured `artifacts/mac-uc-session-20260607T083028Z` after native Universal
Control was working again. The operator connected, disconnected, reconnected,
and performed short benign text-entry actions on both machines before and after
the reconnect. Added
`docs/observations/2026-06-07-redacted-uc-session-reconnect.md` as the
commit-safe summary; it intentionally describes the typed action by class rather
than storing the literal text.

This artifact is now the best Apple-to-Apple baseline for Windows native
admission comparison because it contains both steady-state input and the
disconnect/reconnect state-machine path. Redacted phase counters show
disconnect events, connected-link empty transitions, a later reconnect signal,
target ready/accept events, pointer focus moves, keyboard focus moves, and
remote pointing/keyboard report resets. Packet shape again points at AWDL IPv6
link-local dynamic-port TCP as the native session data path.

### Windows Admission AWDL Read-Shape Comparator

Added `scripts/compare-native-admission-awdl-baseline.py` to compare a redacted
Windows native-admission TCP observer summary with the Apple-to-Apple AWDL
payload length/gap baseline. The comparator reads only commit-safe Markdown
summaries, ignores endpoint direction, and reports overlap tiers such as
`no_tcp_attempt`, `small_length_overlap`,
`small_and_large_length_overlap`, or
`session_like_length_and_gap_overlap`.

This makes the next Windows run stricter. A connection from macOS to the
advertised Windows port is still only visibility/admission pressure. The result
becomes interesting only when the Windows read lengths and inter-read gaps start
to resemble the reconnect AWDL baseline, and even then it must be paired with
native macOS log signal plus legitimate same Apple Account/iCloud evidence from
supported Windows Apple software before building a richer listener.

The Windows native-admission summarizer now also preserves safe redacted peer
classes such as link-local versus private address class and dynamic versus
registered port class. It still omits raw peer addresses, hostnames, payload
bytes, account identifiers, credential material, and TXT values.

### Opt-In Native Admission Framing Probe

Added `--observe-framing` to the Rust TCP observer and
`--framing-probe` to `scripts/windows/capture-native-admission.py`. This is the
next step after a normal native-admission run accepts a TCP connection: rerun
the coordinated capture and collect byte-class buckets, length-prefix candidate
matches, TLS-record-like counts, and compact framing samples for each bounded
read.

The probe still does not log raw payload bytes, hex prefixes, peer addresses, or
decoded message values. Its output is only a frame-shape hypothesis layer above
the existing read length/timing observer, intended to decide whether to build a
real parser/listener and what framing family to try first.
