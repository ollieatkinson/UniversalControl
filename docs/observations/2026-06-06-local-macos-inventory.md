# 2026-06-06 Local macOS Inventory

This is a redacted summary of the first local inventory. Raw command output was not committed because Bonjour TXT values and network addresses can be stable identifiers.

## Host

- macOS 26.5.1
- build 25F80
- Darwin 25.5.0
- architecture arm64

## Universal Control Bundle

- `/System/Library/CoreServices/UniversalControl.app`
- bundle identifier: `com.apple.universalcontrol`
- executable: `UniversalControl`
- bundle version: `174.4.1`
- launchd label from Info.plist: `com.apple.ensemble`

## Running Components

Observed running at the same time:

- `UniversalControl`
- `rapportd`
- `sharingd`
- `nearbyd`
- `useractivityd`
- `bluetoothd`
- `mDNSResponder`

## Launchd Evidence

`com.apple.ensemble` is a GUI LaunchAgent running:

- program: `/System/Library/CoreServices/UniversalControl.app/Contents/MacOS/UniversalControl`
- path: `/System/Library/LaunchAgents/com.apple.ensemble.plist`

Event triggers:

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

## Entitlement Evidence

The Universal Control app is entitled for:

- CompanionLink
- user-access HID devices
- private HID administration
- private HID event dispatch
- NearbyInteraction background/device-presence/privileged access
- Skylight Universal Control
- Wi-Fi peer traffic registration
- Wi-Fi peer-to-peer daemon access

This strongly suggests Universal Control is not implementable as a normal third-party macOS app using only public event APIs if the goal is native integration.

## Bonjour Evidence

Short DNS-SD samples showed:

- local `_companion-link._tcp` advertisement present
- resolved target is the local host at the current dynamic `rapportd` TCP listener
- TXT record contains `rp*` keys consistent with Rapport metadata
- no local `_universalcontrol._tcp` advertisement in the short sample

## Binary String Evidence

Filtered strings from `UniversalControl` included:

- `CompanionLinkClient`
- `CompanionLinkServer`
- `P2PBrowser`
- `P2PDirectLink`
- `P2PStream`
- `P2PMessage`
- `OPACKCoding`
- `AWDL`
- `EnsembleHID`
- `HIDReportAccumulator`
- `PointerController`
- `PasteboardController`
- `DragSourceCoordinator`
- `DragSinkCoordinator`

## Next Local Inventory Step

Repeat this inventory with:

- Universal Control disabled
- Universal Control enabled but no peer
- active Mac-to-Mac Universal Control peer
- active Mac-to-iPad Universal Control peer

Then diff the `rapportd` ports, DNS-SD records, and Universal Control logs.
