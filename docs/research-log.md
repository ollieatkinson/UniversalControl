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
