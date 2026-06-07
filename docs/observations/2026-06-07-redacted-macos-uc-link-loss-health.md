# Redacted macOS Universal Control Probe Summary

## Source

- Artifact: `mac-uc-probe-20260607T081119Z`
- Created: 20260607T081119Z
- Raw output: not included

## Host

- Product: macOS
- Version: 26.5.1
- Build: 25F80
- Architecture: arm64
- Hostname, local addresses, and hardware addresses: not included

## Universal Control Bundle

- Bundle identifier: `com.apple.universalcontrol`
- Bundle version: `174.4.1`
- Short version: `1.0`
- Launchd label: `com.apple.ensemble`
- Minimum macOS: `26.5`
- Entitlement keys: `com.apple.CompanionLink`, `com.apple.developer.device-information.user-assigned-device-name`, `com.apple.developer.ubiquity-kvstore-identifier`, `com.apple.hid.manager.user-access-device`, `com.apple.nearbyinteraction.background`, `com.apple.private.biome.client-identifier`, `com.apple.private.biome.writer`, `com.apple.private.hid.client.admin`, `com.apple.private.hid.client.event-dispatch`, `com.apple.private.nearbyinteraction.device-presence`, `com.apple.private.nearbyinteraction.privileged`, `com.apple.private.skylight.universal-control`, `com.apple.private.tcc.allow`, `com.apple.private.usernotifications.bundle-identifiers`, `com.apple.security.exception.mach-lookup.global-name`, `com.apple.wifi.peer_traffic_registration`, `com.apple.wifip2pd`
- Entitlement count: 17

## Launchd

- UniversalControl: state=active runs=1 path=`/System/Library/LaunchAgents/com.apple.ensemble.plist` program=`/System/Library/CoreServices/UniversalControl.app/Contents/MacOS/UniversalControl` triggers=`com.apple.universalcontrol.discovery`=1, `com.apple.universalcontrol.server`=1 event_streams=`com.apple.rapport.matching`=3 service_types=`_companion-link._tcp`=1, `com.apple.universalcontrol`=1 descriptor_types=`discovery`=1, `server`=1
- rapportd: state=active runs=1 path=`/System/Library/LaunchAgents/com.apple.rapportd-user.plist` program=`/usr/libexec/rapportd`

## Processes

- Observed process names: `UniversalControl`=1, `bluetoothd`=1, `mDNSResponder`=2, `nearbyd`=1, `rapportd`=1, `sharingd`=1, `useractivityd`=1

## Network Interfaces

- Hardware port count: 7
- Device identifiers: `bridge0`, `en0`, `en1`, `en2`, `en3`, `en4`, `en6`
- Wi-Fi port present: yes
- Hardware addresses: not included

## Continuity Health

- Wi-Fi device: `en0`
- Wi-Fi power: on
- Wi-Fi interface active: yes
- awdl0 present: yes
- awdl0 active: yes
- Firewall global state: disabled
- Firewall block-all state: disabled
- Firewall stealth mode: disabled
- Local addresses and hardware addresses: not included

## DNS-SD

### _companion-link._tcp Browse

- Add events: 3
- Remove events: 0
- Service types: `_companion-link._tcp.`
- Instance lengths: `20`
- Interface count: 2

### _companion-link._tcp Self Resolve

- Resolve events: 2
- Ports: `61833`
- Host lengths: `26`
- Fullname lengths: `54`
- Interface count: 1
- TXT keys: `rpAD`, `rpBA`, `rpFl`, `rpHA`, `rpHI`, `rpHN`, `rpMac`, `rpVr`
- TXT value classes: `rpAD:hex:12`=2, `rpBA:mac-like`=2, `rpFl:hex-prefixed:7`=2, `rpHA:hex:12`=2, `rpHI:hex:12`=2, `rpHN:hex:12`=2, `rpMac:hex:1`=2, `rpVr:number`=2

### _universalcontrol._tcp Browse

- Events: none observed

## Network Sockets

### rapportd

- Entries: 7
- rapportd entries: 7
- UniversalControl entries: 0
- TCP entries: 5
- UDP entries: 2
- TCP states: `ESTABLISHED`=3, `LISTEN`=2
- TCP listener ports: `61833`=2
- Known Apple ports seen: `3722`=2
- Raw endpoints and dynamic addresses: not included

### UniversalControl

- Entries: none observed

## UniversalControl Binary Strings

- Filtered string lines: 658
- Hint categories: `AWDL`=3, `CompanionLink`=35, `Drag`=40, `EnsembleHID`=161, `Keyboard`=42, `Nearby`=17, `OPACK`=5, `P2P`=77, `Pasteboard`=33, `Pointer`=76, `WiFiP2P`=1
- Raw strings: not included

## Defaults

- Top-level key names: `ExtensionsPreferences.ShareMenu.displayOrder`, `ExtensionsPreferences.ShareMenu.userHasOrdered`, `familySyncedName`, `frPruneLastSecs`, `oneTimeDateRequestedResetCompleted`, `pdFriendSyncStart`
- Top-level key count: 6
- Values: not included

## Universal Control ByHost Preferences

- Preference files: 1
- Preference byte sizes: `3039`=1
- Top-level key names: `Configuration`, `ConfigurationID`, `HasShownControlNotification`
- Has configuration blob: yes
- Has configuration ID: yes
- Has shown control notification: yes
- Raw configuration blob and identifiers: not included

## Display Cache Shape

- WindowServer display config entries: 4
- WindowServer current display entries: 5
- WindowServer linked display flags: `false`=10
- WindowServer nonzero-origin entries: 2
- Spaces monitor records: 2
- Spaces collapsed display records: 1
- Display UUIDs, names, and raw layout values: not included

## Recent Unified Logs

- Total captured lines: 200
- UniversalControl lines: 2
- rapportd lines: 198
- Proximity keyword lines: 69
- BLE keyword lines: 78
- CompanionLink keyword lines: 94
- P2P keyword lines: 77
- Input keyword lines: 11
- Error/fault keyword lines: 19
- Rapport event IDs: `_systemInfoUpdate`
- Rapport message IDs: `Completed`, `SystemInfo`
- Raw log lines: not included

## Continuity Health Logs

- Total captured lines: 200
- UniversalControl lines: 0
- rapportd lines: 77
- sharingd lines: 118
- useractivityd lines: 0
- Handoff keyword lines: 31
- CompanionLink keyword lines: 81
- BLE/nearby keyword lines: 133
- Wi-Fi P2P/AWDL keyword lines: 40
- Display/Sidecar keyword lines: 29
- Preference/disabled keyword lines: 6
- Error/rejection keyword lines: 22
- Raw log lines: not included

## Interpretation

- CompanionLink browse observed: yes
- CompanionLink self resolve observed: yes
- Universal Control DNS-SD browse observed: no
- rapportd network presence: network sockets observed
- UniversalControl network presence: none observed
- Continuity transport health: Wi-Fi interface and AWDL look available; firewall block-all is not enabled
- Universal Control preference cache: Universal Control ByHost configuration cache present
- Display cache link-loss signal: display cache contains collapsed or nonzero-origin records; inspect if Displays UI is stale
- Native proximity/log signal: native process logs include redacted Rapport event/message IDs
- Link-loss health-log signal: Rapport/Sharing continuity lines present without UniversalControl lines
- Notes:
  - Captured after the operator reported the Universal Control mouse-link option disappeared or could no longer be used.
  - Local transport prerequisites looked healthy: Wi-Fi, the Wi-Fi interface, AWDL, and firewall block-all state were not the obvious failure.
  - Rapport/CompanionLink discovery remained active: `_companion-link._tcp` browse and self-resolve worked, and `rapportd` kept its listener.
  - The suspicious local signals were display/cache state and engagement state: no UniversalControl network sockets, a Universal Control ByHost configuration cache, collapsed/nonzero-origin display-cache records, and a broader continuity log window with Rapport/Sharing activity but no UniversalControl lines.
  - Recovery should prefer restarting/toggling Universal Control and, if needed, moving only the ByHost `com.apple.universalcontrol.*.plist` aside before touching wider display preferences.
  - Do not paste raw hostnames, addresses, TXT values, Bluetooth IDs, hardware addresses, or unified-log lines.
