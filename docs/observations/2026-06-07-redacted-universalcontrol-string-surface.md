# Redacted UniversalControl String Surface Summary

## Source

- Binary: `/System/Library/CoreServices/UniversalControl.app/Contents/MacOS/UniversalControl`
- Program lines: `@(#)PROGRAM:UniversalControl  PROJECT:Ensemble-174.4.1`
- Total unique strings: 4393
- Relevant strings matched: 1319
- Raw binary strings: not included
- Redaction: Apple build roots are reduced to source-relative paths; private log placeholders are kept only as templates.

## Source-Relative Files

- Source-relative file count: 34
- Top-level groups: `Agent`=1, `CompanionLink`=1, `EnsembleAgent`=25, `EnsembleHID`=1, `Glue`=5, `HIDUtils`=1

- `Agent/main_macOS.swift`
- `CompanionLink/RapportStreamServer.swift`
- `EnsembleAgent/Agent.swift`
- `EnsembleAgent/ConnectionController.swift`
- `EnsembleAgent/ConnectionCoordinator.swift`
- `EnsembleAgent/DisplaySleepAssertionController_macOS.swift`
- `EnsembleAgent/DragController.swift`
- `EnsembleAgent/DragPlatformProvider_macOS.swift`
- `EnsembleAgent/DragSinkCoordinator.swift`
- `EnsembleAgent/DragSourceCoordinator.swift`
- `EnsembleAgent/EnsembleHIDController.swift`
- `EnsembleAgent/EventController.swift`
- `EnsembleAgent/EventReport.swift`
- `EnsembleAgent/P2PBrowser.swift`
- `EnsembleAgent/P2PController.swift`
- `EnsembleAgent/P2PDirectLink.swift`
- `EnsembleAgent/P2PLink.swift`
- `EnsembleAgent/P2PMessage.swift`
- `EnsembleAgent/P2PPeerCoordinator.swift`
- `EnsembleAgent/P2PStream.swift`
- `EnsembleAgent/PasteboardController.swift`
- `EnsembleAgent/PasteboardController_macOS.swift`
- `EnsembleAgent/PasteboardDataSession.swift`
- `EnsembleAgent/PowerManagement_macOS.swift`
- `EnsembleAgent/SyncContext.swift`
- `EnsembleAgent/SyncController.swift`
- `EnsembleAgent/SyncCoordinator.swift`
- `EnsembleHID/HIDCapsLock.swift`
- `Glue/Archive.swift`
- `Glue/CFPasteboard.swift`
- `Glue/OPACKCoding.swift`
- `Glue/ProcessInfo.swift`
- `Glue/SFSymbol.swift`
- `HIDUtils/HIDServiceProperties.swift`

## Stable Identifiers

- Identifier count: 28

- `com.apple.NSFilePromiseItemMetaData`
- `com.apple.UIKit.private.drag-suggested-name`
- `com.apple.ec.UniversalControl.unavailableDisconnect`
- `com.apple.ensemble.dragserver`
- `com.apple.pasteboard.NSFilePromiseID`
- `com.apple.pasteboard.promised-file-content-type`
- `com.apple.pasteboard.promised-file-name`
- `com.apple.pasteboard.promised-file-url`
- `com.apple.pasteboard.promised-suggested-file-name`
- `com.apple.rapport.matching`
- `com.apple.sharing.EnhancedDiscovery`
- `com.apple.uikit.private.drag-item`
- `com.apple.universalcontrol`
- `com.apple.universalcontrol.`
- `com.apple.universalcontrol.available`
- `com.apple.universalcontrol.connected`
- `com.apple.universalcontrol.hid-activity`
- `com.apple.universalcontrol.inputstate`
- `com.apple.universalcontrol.notifications.displays-preferences`
- `com.apple.universalcontrol.p2p-peer-coordinator`
- `com.apple.universalcontrol.shield`
- `com.apple.universalcontrol.transfer-destination`
- `com.apple.universalcontrol.transfer-source`
- `com.apple.universalcontrol.ui`
- `com.apple.universalcontrol.virtual-service`
- `com.apple.universalcontrol.virtual-service-pool`
- `com.apple.universalcontrol.virtual-service-pool.services`
- `universalcontrol.enabled`

## Runtime Type Hints

- Type hint count: 141

- `CompanionLinkClient`
- `CompanionLinkServer`
- `CompanionLinkSession`
- `RapportStreamServer`
- `RapportStreamSession`
- `P2PBrowser`
- `P2PController`
- `P2PDirectLink`
- `P2PLink`
- `P2PMessage`
- `P2PPeerCoordinator`
- `P2PStream`
- `SyncController`
- `SyncCoordinator`
- `SyncMessage`
- `EnsembleHIDController`
- `DisplayControllerProtocol`
- `PointerControllerProtocol`
- `PasteboardControllerRepresentationProviderProtocol`
- `PasteboardDataSession`
- `DragSourceCoordinator`
- `DragSinkCoordinator`
- `SecureLayerHost`
- `UniversalControlVirtualService`
- `CompanionLinkDelegate`
- `CompanionLinkDevice`
- `CompanionLinkServerDelegate`
- `CompanionLinkSessionDelegate`
- `DisplayController_macOS`
- `DisplaySleepAssertionController`
- `DisplaysNotification`
- `DisplaysNotificationCenter`
- ... 109 more

## NearbyInteraction Selectors

- Selector count: 13

- `session:didDiscoverNearbyObject:`
- `session:didFailWithError:`
- `session:didGenerateShareableConfigurationData:forObject:`
- `session:didInvalidateWithError:`
- `session:didProcessBluetoothHostTimeSyncWithResponse:error:`
- `session:didReceiveRangingAuthRecommendation:forObject:`
- `session:didRemoveNearbyObjects:withReason:`
- `session:didUpdateAlgorithmConvergence:forObject:`
- `session:didUpdateAlgorithmState:forObject:`
- `session:didUpdateDLTDOAMeasurements:`
- `session:didUpdateHomeDeviceUWBRangingAvailability:`
- `session:didUpdateLocalMotionState:`
- `session:didUpdateNearbyObjects:`

## Log Template Categories

### CompanionLink And Rapport

- Template count: 15

- `%{public}s: RPStreamServer Activated`
- `%{public}s: Accept Stream: %{public}s`
- `%{public}s: P2PStream Activated (Connection Ready)`
- `%{public}s: P2PStream Connection Ready`
- `%{public}s: P2PStream Canceled`
- `%{public}s: Accepting P2PStream %{public}s`
- `%{public}s: Activating P2PStream %{public}s`
- `%{public}s: Activating RPStreamServer`
- ... 7 more

### Display And Device Layout

- Template count: 63

- `%{public}s: Device Found SF <%{public}s>, Md %{public}s, SV %{public}s, AL %{public}s`
- `%{public}s: Ineligible Device Found Md %{public}s, SV %{public}s`
- `%{public}s: Remote Display Layout: [%{public}s]`
- `%{public}s: Remote Source Device: %{public}s`
- `%{public}s: Remote Connected Devices: [%{public}s]`
- `%{public}s: Local Device Change: %{public}s`
- `%{public}s Connected Devices Clock: %s -> %s`
- `%{public}s: No main display on local device`
- ... 55 more

### Drag And Pasteboard

- Template count: 45

- `%{public}s: TargetReady drag=%{public}s, keyboard=%{public}s`
- `%{public}s: preparing drag session`
- `%{public}s: skipping drag session`
- `%{public}s: Pasteboard Data Session already deactivated`
- `%{public}s: pasteboard stream cancelled`
- `%{public}s: creating promise target: %{public}s`
- `%{public}s: setting promise target on pasteboard: %{public}s`
- `%{public}s: promise target already created`
- ... 37 more

### Focus And Target Input

- Template count: 44

- `%{public}s: FocusMove pointer=%{bool}d keyFocus=%{bool}d device=%{public}s source=%{public}s`
- `%{public}s: TargetBegin`
- `%{public}s: TargetConnect`
- `%{public}s: TargetReady drag=%{public}s, keyboard=%{public}s`
- `%{public}s: TargetEvent device=%{public}s service=0x%llx reportID=0x%hhx`
- `%{public}s: TargetReply status=%hhu`
- `%{public}s: Target Reply: Reject due to %{public}s`
- `%llx: Removed Local Keyboard Reports`
- ... 36 more

### Message Synchronization

- Template count: 59

- `%{public}s: Initial Sync`
- `%{public}s: Create Message (Barrier)`
- `%{public}s: Send Message: %{public}s`
- `%{public}s: Receive Message: %{public}s`
- `%{public}s: Received Message from IDS %{public}s: %{public}s`
- `%{public}s: Merge message: %{public}s -> %{public}s`
- `%{public}s: Ignore past message: %{public}s`
- `%{public}s: Synchronization Failed: No Message Sender`
- ... 51 more

### Peer-To-Peer Links

- Template count: 9

- `%{public}s: P2PDirectLink Activated`
- `%{public}s: Preparing P2PStream %{public}s`
- `%{public}s: P2PStream Activated (Connection Ready)`
- `%{public}s: P2PStream Connection Ready`
- `%{public}s: P2PStream Canceled`
- `%{public}s: Accepting P2PStream %{public}s`
- `%{public}s: Activating P2PStream %{public}s`
- `%{public}s: P2PStream Activated`
- ... 1 more

### Rejections And Errors

- Template count: 24

- `%{public}s: Target Reply: Reject due to %{public}s`
- `%{public}s: Reset Remote (no connected devices, mismatched signature)`
- `%{public}s: Reset Remote (no device data, mismatched signature)`
- `%{public}s: unexpected TargetReady in idle state, rejecting`
- `%{public}s: timeout during HID accumulation waiting phase`
- `: TargetReply Failure`
- `%{public}s: Synchronization Failed: No Message Sender`
- `%llx: Failed to find existing local device`
- ... 16 more

## Interpretation

- The native app exposes a CompanionLink/Rapport stream server surface, plus P2P stream/message coordination and OPACK-adjacent glue.
- Target-state log templates name `TargetBegin`, `TargetConnect`, `TargetReady`, `TargetEvent`, `TargetReply`, and rejection paths; future native-admission captures should search for those terms.
- Display layout, synced devices, source devices, pointer focus, keyboard readiness, drag, and pasteboard all appear in the same UniversalControl binary, so an accepted peer likely enters one coordinated control plane before input transport.
