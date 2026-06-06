# Capture Plan

The goal is to produce evidence that can drive an implementation, not just collect noisy traces. Every capture should record the machine state, exact commands, participants, and user action being performed.

## Capture Safety

- Do not commit raw packet captures, Keychain output, Apple Account identifiers, or unredacted local device IDs.
- Prefer summaries and redacted excerpts in `docs/observations/`.
- Store raw captures under `artifacts/` or another ignored path.
- Label whether the peer was a Mac, iPad, or Windows machine.

## Baseline macOS Probe

Run:

```sh
./scripts/mac/uc-probe.sh
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

Suggested commands:

```sh
./scripts/mac/uc-probe.sh
log stream --style compact --predicate 'process == "UniversalControl" || process == "rapportd"' > artifacts/uc-session.log
dns-sd -B _companion-link._tcp local > artifacts/companion-link-browse.log
sudo tcpdump -i en0 -w artifacts/uc-en0.pcap 'udp port 5353 or udp port 3722 or tcp'
sudo tcpdump -i awdl0 -w artifacts/uc-awdl0.pcap
```

Notes:

- `tcpdump` requires admin privileges.
- `awdl0` may not exist or may not show traffic until peer-to-peer Wi-Fi is active.
- Keep `log stream` and packet captures scoped to the experiment window.

## Windows Observation Capture

On Windows, capture both discovery and transport candidates.

Record:

- Windows version and build
- network adapters and active interface
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
cargo run -- discover-companion-link --backend rust-mdns --seconds 30
```

If Bonjour's `dns-sd.exe` is installed and available on `PATH`, also compare:

```powershell
cargo run -- discover-companion-link --backend system --seconds 30
```

Expected Windows deliverable:

- a redacted Markdown note under `docs/windows-inbox/`
- any source patches for discovery/advertising under the implementation tree once it exists

## First Experiments

1. Compare `_companion-link._tcp` TXT records while Universal Control is disabled and enabled.
2. Compare records while Handoff is disabled and enabled.
3. Browse on `en0` versus `awdl0` during a live edge-push connection.
4. Capture `rapportd` TCP connection setup during a live session.
5. Identify whether `com.apple.universalcontrol` appears as a cleartext Rapport message, a DNS-SD subtype, or only as a launchd/Rapport-internal match.
6. Capture one pointer movement and one key press, then isolate which stream changes at that moment.
