# Capture Plan

The goal is to produce evidence that can drive an implementation, not just collect noisy traces. Every capture should record the machine state, exact commands, participants, and user action being performed.

Use [native-feasibility.md](native-feasibility.md) for the current native-first
pass gates and fallback decision threshold. Captures should advance or close
those gates directly.

## Capture Safety

- Do not commit raw packet captures, Keychain output, Apple Account identifiers, or unredacted local device IDs.
- Prefer summaries and redacted excerpts in `docs/observations/`.
- Store raw captures under `artifacts/` or another ignored path.
- Label whether the peer was a Mac, iPad, or Windows machine.

## Baseline macOS Probe

Run:

```sh
./scripts/mac/uc-probe.sh
./scripts/mac/summarize-uc-probe-artifact.py artifacts/mac-uc-probe-YYYYMMDDTHHMMSSZ \
  --output docs/observations/YYYY-MM-DD-redacted-macos-uc-probe.md
./scripts/mac/summarize-universalcontrol-strings.py \
  --output docs/observations/YYYY-MM-DD-redacted-universalcontrol-string-surface.md
```

Compare two redacted baseline states:

```sh
./scripts/mac/compare-uc-probe-summaries.py \
  docs/observations/YYYY-MM-DD-redacted-macos-uc-probe-before.md \
  docs/observations/YYYY-MM-DD-redacted-macos-uc-probe-after.md \
  --before-label before \
  --after-label after \
  --output docs/observations/YYYY-MM-DD-redacted-macos-uc-probe-compare.md
```

Expected output:

- OS version and network interfaces
- relevant process list
- Universal Control bundle metadata
- entitlements
- launchd state for `com.apple.ensemble`
- launchd state for `com.apple.rapportd`
- `rapportd` listener ports
- short DNS-SD browse for `_companion-link._tcp`
- DNS-SD resolve for the local `_companion-link._tcp` instance
- short DNS-SD browse for `_universalcontrol._tcp`
- filtered strings from `UniversalControl`
- `scripts/mac/summarize-uc-probe-artifact.py` creates the commit-safe Markdown summary from the ignored artifact folder.
- `scripts/mac/summarize-universalcontrol-strings.py` extracts source-relative
  module names, stable identifiers, NearbyInteraction selectors, and prioritized
  log templates from the installed native binary without committing raw strings
  or Apple build-root paths.

The summary preserves bundle metadata, entitlement key names, launchd trigger
service types, process counts, DNS-SD browse/resolve counts, `rp*` TXT key names
and value classes, protocol-relevant ports, socket counts, binary-string hint
categories, and native log event/message IDs. It omits raw hostnames, addresses,
hardware addresses, Bluetooth IDs, TXT values, defaults values, and unified-log
lines.

The string-surface summary provides concrete terms for later unified-log
searches. Current high-value terms include stream states (`RPStreamServer`,
`P2PStream`, `P2PDirectLink`), target states (`TargetBegin`,
`TargetConnect`, `TargetReady`, `TargetEvent`, `TargetReply`), sync/layout
states (`Initial Sync`, `Remote Display Layout`, `Remote Source Device`), and
rejection states (`Target Reply: Reject`, `Reset Remote`).

The comparer only reads redacted summaries. Use it to compare Universal Control
disabled, enabled with no peer, and active Apple-peer states without committing
raw artifact directories.

## Paired Mac Or iPad Session Capture

Use this when an Apple peer is available and Universal Control can actually connect.

Record:

- source Mac model and OS
- target Mac or iPad model and OS
- whether both are on the same Wi-Fi network
- whether AWDL is present
- Universal Control settings on both machines
- exact user actions:
  - idle before connection
  - push through edge
  - pointer movement on target
  - key press on target
  - scroll on target
  - drag start and cancel
  - copy/paste if enabled

Recommended command:

```sh
./scripts/mac/capture-uc-session.sh --duration 120
./scripts/mac/summarize-uc-session-artifact.py artifacts/mac-uc-session-YYYYMMDDTHHMMSSZ \
  --output docs/observations/YYYY-MM-DD-redacted-uc-session.md
```

Add packet capture when ready to collect raw network evidence:

```sh
./scripts/mac/capture-uc-session.sh --duration 120 --tcpdump
```

What it captures:

- `dns-sd -B _companion-link._tcp local`
- `dns-sd -B _universalcontrol._tcp local`
- unified logs for `UniversalControl`, `rapportd`, `mDNSResponder`, `nearbyd`, and `wifip2pd`
- launchd snapshots for `com.apple.ensemble` and `com.apple.rapportd`
- `lsof` network snapshots for `rapportd` and `UniversalControl`
- optional `tcpdump` packet captures on `en0` plus `awdl0` when present
- `scripts/mac/summarize-uc-session-artifact.py` creates the commit-safe Markdown summary from the ignored artifact folder.

Notes:

- `--tcpdump` requires admin privileges and writes raw `.pcap` files that must not be committed.
- `awdl0` may not exist or may not show traffic until peer-to-peer Wi-Fi is active.
- Keep captures scoped to the experiment window.
- Commit only redacted summaries under `docs/observations/`.

## Windows Observation Capture

On Windows, capture both discovery and transport candidates.

Record:

- Windows version and build
- network adapters and active interface
- display geometry from `cargo run -- probe displays`
- whether Apple Bonjour is installed
- whether the Windows implementation is advertising anything
- local firewall state for inbound UDP 5353, UDP 3722, and the chosen TCP port

Wireshark display filters:

```text
mdns || udp.port == 5353 || udp.port == 3722 || tcp.port == 61833
```

PowerShell discovery commands to add or verify:

```powershell
Get-NetAdapter
Get-NetFirewallProfile
Resolve-DnsName -Type PTR _companion-link._tcp.local
```

Repo-native discovery command:

```powershell
python scripts/windows/capture-companion-link-discovery.py
```

Manual equivalent:

```powershell
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
```

Repo-native display geometry command:

```powershell
python scripts/windows/capture-display-probe.py
```

Manual equivalent:

```powershell
cargo run -- probe displays
```

Record the primary display bounds and any negative display origins. The wrapper
redacts display names while preserving name lengths, bounds, scale, primary
flags, and virtual bounds. These values calibrate `local_width`, `local_height`,
`remote_width`, `remote_height`, and `remote_edge` before a bridge run.

If Bonjour's `dns-sd.exe` is installed and available on `PATH`, also compare:

```powershell
cargo run -- discover-companion-link --backend system --seconds 30
```

The Rust `--redact` output is commit-safe for normal notes: it preserves event type, service type, port, TXT key names, TXT value length/class, and address count, but hides hostnames, addresses, instance names, and TXT values. The wrapper refuses `--backend system` unless `--allow-unredacted-system` is supplied. Treat system `dns-sd` output as raw until manually sanitized.

Expected Windows deliverable:

- a redacted Markdown note under `docs/windows-inbox/`
- any source patches for discovery/advertising under the implementation tree once it exists

## Windows-To-Mac Advertisement Check

Preferred macOS wrapper:

```sh
./scripts/mac/capture-native-admission.sh --mode benign
```

On Windows:

```powershell
cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe
```

On macOS, while the Windows command is running:

```sh
./scripts/mac/watch-mdns-service.sh --duration 60
dns-sd -B _anykbflow-probe._tcp local
dns-sd -L "AnyKBFlow Probe" _anykbflow-probe._tcp local
```

Expected evidence:

- macOS browse sees `AnyKBFlow Probe`.
- macOS resolve shows the Windows hostname, published port, and TXT values.
- The watcher writes a timestamped ignored artifact folder under `artifacts/`
  containing browse, resolve, and filtered unified logs for
  `UniversalControl`, `rapportd`, `mDNSResponder`, `nearbyd`, and `wifip2pd`.
- `scripts/mac/summarize-mdns-watch-artifact.py` creates the commit-safe Markdown summary from the ignored artifact folder.
- If browse succeeds but resolve fails, record the redacted interface count and local firewall state.
- If neither succeeds, record Windows network profile, firewall state, and whether UDP 5353 multicast is allowed.

Controlled Apple-service experiments must be separated from this benign check.
Only use `--service-type _companion-link._tcp --allow-apple-service` while
macOS `rapportd` and `UniversalControl` logs are being captured. Start with the
minimal project probe below; do not mimic Apple `rp*` TXT fields until a real
Apple-peer TXT shape has been captured and redacted.

## Controlled CompanionLink Candidate Check

Use this only after the benign Windows advertisement check has established that
macOS can see Windows mDNS services on the current network.

Preferred macOS wrapper:

```sh
./scripts/mac/capture-native-admission.sh --mode companion-link
```

On macOS first:

```sh
./scripts/mac/watch-companion-link-candidate.sh --duration 90 --instance "AnyKBFlow Native Probe"
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
  --observe-tcp `
  --seconds 60
```

Capture the Windows output to an ignored transcript and summarize it before
committing:

```powershell
cargo run -- advertise-mdns ... *> artifacts/windows-native-admission-companion-link.txt
python scripts/windows/summarize-native-admission-output.py `
  artifacts/windows-native-admission-companion-link.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-companion-link.md
```

This minimal candidate deliberately does not copy Apple `rp*` TXT fields. It is
only meant to answer whether `rapportd` or `UniversalControl` reacts to a
Windows-owned `_companion-link._tcp` service at all. `--observe-tcp` records
whether macOS attempts the advertised port; it is not a Rapport implementation.
Preserve raw artifacts under `artifacts/`, then commit only redacted summaries.
The redacted Mac summary also reports `nearbyd` and `wifip2pd` line counts plus
proximity/ranging and AWDL/Wi-Fi peer-to-peer keyword counts. Treat those as
side-channel evidence that a Windows candidate affected native eligibility or
transport selection, not as admission by themselves.

## Shape-Only CompanionLink Candidate Check

Use this only after the minimal candidate check. It publishes the redacted
macOS-baseline TXT key/value-class shape with deterministic placeholder values,
not real Apple identifiers.

Preferred macOS wrapper:

```sh
./scripts/mac/capture-native-admission.sh --mode shape
```

On macOS first:

```sh
./scripts/mac/watch-companion-link-candidate.sh --duration 90 --instance "AnyKBFlow Native Shape Probe"
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
cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment --observe-tcp --seconds 60
```

The wrapper captures and summarizes the Windows output. Manual capture plus
summary:

```powershell
cargo run -- advertise-companion-link-shape --acknowledge-shape-experiment --observe-tcp --seconds 60 *> artifacts/windows-native-admission-shape.txt
python scripts/windows/summarize-native-admission-output.py `
  artifacts/windows-native-admission-shape.txt `
  --output docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md
```

Expected evidence:

- macOS browse/resolve sees `AnyKBFlow Native Shape Probe`.
- The committed watcher summary preserves port, TXT key names, TXT value
  classes, and native-process log counts.
- Compare the minimal and shape-only watcher summaries with
  `scripts/mac/compare-mdns-watch-summaries.py`.
- Compare the minimal and shape-only Windows summaries with
  `scripts/windows/compare-native-admission-summaries.py`.
- `rapportd` or `UniversalControl` either ignores the service, attempts a
  connection, or logs a concrete rejection reason.
- Windows summary includes whether the TCP observer accepted any connections,
  per-connection read counts, total byte counts, first-read byte counts,
  first-read hex lengths, additional-read hex lengths, read-limit status, and
  peer-close-after-data status without raw peer addresses or payload bytes.
- The paired report combines the Mac and Windows summaries:

  ```sh
  ./scripts/compare-native-admission-pair.py \
    docs/observations/YYYY-MM-DD-redacted-companion-link-shape-candidate.md \
    docs/windows-inbox/YYYY-MM-DD-redacted-native-admission-shape.md \
    --label shape \
    --output docs/observations/YYYY-MM-DD-redacted-native-admission-shape-pair.md
  ```

- Treat any connection attempt as a signal to inspect the bounded read summary
  and build a real listener next, not as Universal Control admission.

## First Experiments

1. Compare `_companion-link._tcp` TXT records while Universal Control is disabled and enabled.
2. Compare records while Handoff is disabled and enabled.
3. Browse on `en0` versus `awdl0` during a live edge-push connection.
4. Capture `rapportd` TCP connection setup during a live session.
5. Identify whether `com.apple.universalcontrol` appears as a cleartext Rapport message, a DNS-SD subtype, or only as a launchd/Rapport-internal match.
6. Capture one pointer movement and one key press, then isolate which stream changes at that moment.
