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

Interpretation for Windows: a Windows peer cannot satisfy the same Apple Account plus iCloud Keychain trust requirement by normal OS participation. That does not prove native Universal Control interop is impossible, but it defines the main feasibility gate: can a Windows peer enter the required Rapport/CompanionLink trust/session path without Apple-private account material?

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
- Authentication requires Apple Account, IDS, iCloud Keychain, or entitlement-protected material unavailable to Windows.
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
`com.apple.universalcontrol` gates without Apple-private identity material.

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
is high risk. The immediate proof gates are still Windows passive browsing of
the Mac `_companion-link._tcp` advertisement, macOS visibility of a benign
Windows mDNS probe, a controlled Windows `_companion-link._tcp` candidate run
with macOS `rapportd`/`UniversalControl` logs, and Apple-to-Apple baseline
captures before any deeper Windows native handshake attempt.

### Shape-Only CompanionLink Candidate

Added `cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment`.
It advertises `_companion-link._tcp` with deterministic placeholder `rp*` TXT
values matching the redacted local macOS baseline key/value classes:

- `rpAD`, `rpHA`, `rpHI`, `rpHN`: hex length 12
- `rpBA`: MAC-like placeholder
- `rpFl`: hex length 5
- `rpMac`: hex length 1
- `rpVr`: number

This is a controlled DNS-SD shape experiment, not a native Universal Control
implementation. It does not copy Apple identifiers or account material and does
not speak Rapport. `--observe-tcp` can be added to advertise commands to open a
bounded TCP listener on the advertised port and log connection attempts plus a
short first-read hex prefix. The next evidence needed is a Mac-side watcher
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
first-read hex lengths while redacting peer addresses, hostnames, and payload
bytes.

This pairs with the Mac-side `capture-native-admission.sh` summary so one
commit can contain both sides of the same admission attempt without raw network
identifiers.

### Local macOS Bridge Preflight

Recorded `docs/observations/2026-06-07-local-macos-bridge-preflight.md` after
running `probe displays` plus input-owner and receiver `preflight` on native
macOS. The preflight path detected `1710x1112`, matched `probe displays`, used
that as the effective local display for both stale example configs, selected
`peer_mode=mdns_discovery` for the receiver config with no `peer_addr`, and
reported zero warnings. This answers the Windows bridge-preflight note, but it
does not advance native Universal Control admission.
