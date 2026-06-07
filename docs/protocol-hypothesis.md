# Protocol Hypothesis

This file separates observed facts from working inferences. It should be updated whenever captures disprove or refine a layer.

## Layer Model

### 1. Eligibility And Proximity

Observed:

- Apple requires same Apple Account, two-factor authentication, Bluetooth, Wi-Fi, and Handoff.
- `UniversalControl.app` has NearbyInteraction and Wi-Fi peer-to-peer private entitlements.

Inferred:

- Bluetooth and NearbyInteraction likely gate whether a device is considered physically nearby.
- The same-Apple-Account requirement likely contributes long-term identity material used by Rapport/CompanionLink or adjacent Continuity services.

Open questions:

- Does Universal Control require BLE advertisements before a Rapport session is considered eligible?
- Are proximity checks only used to surface candidates, or are they enforced during active input streaming?

### 2. Discovery

Observed:

- `com.apple.ensemble` is launched by Rapport matching events.
- Discovery trigger service type is `_companion-link._tcp`.
- Server trigger service type is `com.apple.universalcontrol`.
- Local DNS-SD browsing finds `_companion-link._tcp`, and resolving it points at the current `rapportd` listener.
- No `_universalcontrol._tcp` service was found in a short local browse.

Inferred:

- Windows should first implement DNS-SD observation for `_companion-link._tcp` and record all TXT keys without assuming their semantics.
- A direct Windows peer may need to speak the Rapport/CompanionLink application protocol to the dynamic `rapportd` listener before Universal Control will consider it.

Open questions:

- Is `com.apple.universalcontrol` exposed only inside Rapport matching, or can it be surfaced through a public network-visible message?
- Which TXT keys are stable identity, feature flags, protocol versions, transport addresses, or link-local hints?
- Does the service appear on AWDL-only interfaces during active Universal Control?

### 3. Authentication And Trust

Observed:

- Apple documents Handoff trust as iCloud-mediated BLE pairing plus Keychain-stored symmetric keys.
- Apple documents larger Handoff payloads as TLS over Apple peer-to-peer Wi-Fi with identity from iCloud Keychain.
- `UniversalControl.app` is entitled for CompanionLink and private HID dispatch.

Inferred:

- Native Universal Control likely depends on Apple-private trust material that a Windows process will not possess.
- If direct admission fails at authentication, the project should keep collecting rejection evidence until the native compatibility checklist justifies the bridge fallback.

Open questions:

- Does Universal Control use the same Pair-Verify-like handshake described for Handoff/Universal Clipboard, or a newer Rapport-specific variant?
- Are messages encrypted end-to-end above TCP/AWDL, or is TLS/Noise-like protection delegated to Rapport?

### 4. Control Plane

Observed:

- String evidence includes `CompanionLinkClient`, `CompanionLinkServer`, `P2PBrowser`, `P2PDirectLink`, `P2PMessage`, `P2PStream`, and `OPACKCoding`.
- The redacted string-surface summary at `docs/observations/2026-06-07-redacted-universalcontrol-string-surface.md` exposes source-relative modules including `CompanionLink/RapportStreamServer.swift`, `EnsembleAgent/P2PStream.swift`, `EnsembleAgent/P2PMessage.swift`, `EnsembleAgent/SyncController.swift`, `EnsembleAgent/EventReport.swift`, `EnsembleAgent/EnsembleHIDController.swift`, and `Glue/OPACKCoding.swift`.
- Stable identifiers include `com.apple.universalcontrol`, `com.apple.universalcontrol.virtual-service`, `com.apple.universalcontrol.p2p-peer-coordinator`, `com.apple.universalcontrol.hid-activity`, `com.apple.universalcontrol.inputstate`, and `com.apple.rapport.matching`.
- Log templates name stream and sync states such as `RPStreamServer Activated`, `P2PStream Activated (Connection Ready)`, `Initial Sync`, `Send Message`, `Receive Message`, `Remote Display Layout`, and `Remote Source Device`.
- Launchd registers the Universal Control service under Rapport matching.

Inferred:

- The control plane probably negotiates device capabilities, display layout, focus movement, keyboard availability, drag state, pasteboard state, and direct P2P link selection.
- OPACK or an OPACK-adjacent encoding is likely used for at least some structured messages.
- A Windows peer that reaches native admission should create log evidence in the stream, sync/message, or remote display-layout families before any input report is usable.

Open questions:

- What are the message types, IDs, and required feature flags?
- Which side is authoritative for display geometry and edge crossing?
- Is drag/pasteboard multiplexed over the same P2P stream as input, or separate streams?

### 5. Data Plane

Observed:

- Universal Control has private HID entitlements and strings for HID report accumulation, local keyboard report removal, pointer focus movement, and target keyboard readiness.
- Native log templates name `FocusMove`, `TargetBegin`, `TargetConnect`, `TargetReady`, `TargetEvent`, `TargetReply`, and `Target Reply: Reject`.
- `rapportd` listens on a dynamic TCP port and UDP 3722 locally.

Inferred:

- Input probably travels as serialized HID reports or higher-level input events after a control-plane focus transfer.
- macOS injects or dispatches events through private HID and Skylight privileges that third-party apps do not normally have.
- `TargetReply` status/rejection logs are likely the best redacted indicator that a candidate reached input-target negotiation but failed eligibility, collision handling, keyboard readiness, drag readiness, or HID accumulation.

Open questions:

- Are pointer deltas, absolute coordinates, scroll, and keyboard events encoded as raw HID reports or logical event dictionaries?
- How are keyboard layout, modifiers, Fn/globe keys, dead keys, IME state, and Caps Lock synchronized?
- Does the target create a virtual HID device, or does Universal Control dispatch directly into the window server/HID system?

## Interop Consequences

Direct Windows participation in Apple's native Universal Control session has three hard requirements:

1. Discover Apple peers the same way macOS does.
2. Authenticate in a way accepted by Rapport/CompanionLink and Universal Control.
3. Emit or consume the correct HID/control messages at session latency.

Requirement 1 is approachable now. Requirement 2 is the main risk because
Apple's public requirements imply account-linked trust; Windows may need to use
a legitimate Apple Account identity path such as iCloud for Windows or a future
CLI login if that material is required. Requirement 3 is approachable only after
paired captures reveal the message envelope.

The pragmatic architecture is therefore native-first with an explicit fallback:

1. Reverse engineer native discovery and session negotiation far enough to prove whether Windows can be accepted by macOS `UniversalControl.app`.
2. Build a Windows plus Mac bridge only if native authentication/session admission blocks direct interop.

## Native Feasibility Gates

Native Mac-side compatibility remains viable only if these gates can be passed:

1. Windows can advertise or respond in a way that causes macOS Rapport/Universal Control to consider it a candidate.
2. The session can progress beyond discovery either before account trust is
   required or using supported Apple Account/iCloud identity material available
   to Windows.
3. The Windows peer can negotiate the `com.apple.universalcontrol` service role.
4. The input/control data plane can be decoded and generated with keys negotiated during that session, not keys only Apple devices possess.
5. The Mac does not require private local entitlements from the remote peer that can only exist on Apple platforms.

The first gate is testable immediately with DNS-SD and macOS logs. Gates 2 through 4 require a real Apple-to-Apple capture for comparison.
