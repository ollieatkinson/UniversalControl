# Implementation Requirements

This document explains what we need before this can become a working Mac plus
Windows keyboard and mouse system.

The preferred outcome is still native macOS Universal Control: the Mac keeps
using Apple's `UniversalControl.app`, and Windows becomes an accepted peer. The
fallback outcome is a project-owned bridge with a Mac agent and a Windows agent.
Both can produce a similar user experience, but they need different evidence and
different code.

## Target Experience

The minimum useful implementation must provide:

- pointer transition across configured display edges
- keyboard focus following pointer focus
- pointer movement, buttons, wheel/trackpad scrolling, and keyboard events
- correct modifier and button release when a session starts, ends, or reconnects
- display geometry exchange so edge routing works with real monitor layouts
- explicit recovery when one side closes, sleeps, changes displays, or loses the
  network

Drag, pasteboard, file transfer, and tablet-like gestures should come after the
input path is stable.

## Native Universal Control Path

To keep the Mac fully native, Windows must satisfy the same visible stages that
an Apple peer satisfies.

### 1. Discovery

We need Windows to:

- browse and resolve the Mac's `_companion-link._tcp.local.` service
- capture the dynamic `rapportd` port and redacted `rp*` TXT key/value shape
- advertise a controlled Windows candidate that macOS can browse and resolve
- prove whether macOS `rapportd` or `UniversalControl` reacts to that candidate

Current tooling covers this with the Windows capture wrappers and the Mac
native-admission watchers. Passing ordinary mDNS visibility is not enough;
native admission needs `rapportd` or `UniversalControl` reaction.

### 2. Eligibility And Trust

This is the highest-risk layer.

Apple's public requirements point at same Apple Account, Handoff, Bluetooth,
Wi-Fi, and Continuity trust. Local evidence points at Rapport/CompanionLink,
NearbyInteraction, AWDL/Wi-Fi P2P, and private HID/Skylight entitlements.

For native Windows admission, we need one of these to be true:

- the required trust is negotiated during the observed session and Windows can
  honestly participate
- Windows can use a legitimate Apple Account identity path, such as iCloud for
  Windows or a future CLI login, if Universal Control requires same-account
  Continuity trust
- Windows can reach a Universal Control service route before same-account trust
  is required
- the missing fields are ordinary protocol fields, not protected Apple identity
  claims

Native should be considered closed only if the remaining path requires
extracting protected Apple Account or iCloud Keychain secrets, private
certificates unavailable through supported Windows Apple software, private
entitlements, or misleading platform attestation.

### 3. Rapport/CompanionLink Session

After discovery, we need to identify:

- who opens the first TCP or peer-to-peer connection
- frame boundaries and length encoding
- encryption or authentication handshake stages
- whether OPACK or an OPACK-adjacent format carries structured messages
- how `com.apple.universalcontrol` is selected inside the session
- what macOS logs when a peer is accepted, rejected, or ignored

This requires Apple-to-Apple active session captures and a Windows attempt that
can be compared against that baseline.

### 4. Universal Control Control Plane

Before input can work, the peer probably has to negotiate:

- source and target roles
- display bounds, scale, arrangement, and edge relationships
- input ownership and focus transfer
- keyboard readiness and target readiness
- capability flags for pointer, keyboard, drag, and pasteboard
- reconnect and collision behavior

The key milestone is reaching log or packet evidence for Universal
Control-specific states such as stream activation, initial sync, remote display
layout, remote source device, target begin/connect/ready, or target reply.

### 5. Input Data Plane

The native path is implementable only if we can decode and generate the input
stream without Apple-only keys. We need to isolate:

- pointer deltas or absolute coordinates
- button down/up and wheel/scroll units
- keyboard usage codes, modifier state, Caps Lock, Fn/globe, and layout effects
- event ordering, acknowledgements, timestamps, and sequence numbers
- release cleanup when a peer disconnects
- how focus returns from target to source

A single decoded pointer move and one decoded key press would be enough to start
a real native prototype. A synthetic event accepted or rejected for a known
reason would be stronger.

## Fallback Bridge Path

If native admission closes, the bridge implementation needs these components.

### Mac Agent

The Mac agent would:

- observe display geometry and configured edges
- capture local input when the pointer crosses into Windows
- inject received Windows-originated events using available public APIs
- release held keys/buttons on session start, session end, and peer close
- expose explicit pairing and local trust prompts

This gives up the requirement that the Mac remains purely native Universal
Control, but keeps the user-facing workflow deliverable.

### Windows Agent

The Windows agent would:

- use low-level keyboard and mouse hooks or Raw Input for capture
- use `SendInput` for injection
- preserve physical key identity separately from text
- handle display geometry, DPI scale, and virtual desktop offsets
- suppress local delivery only while focus is remote

Most of the existing AnyKBFlow prototype work belongs here.

### Shared Protocol

The bridge protocol should provide:

- project-owned DNS-SD discovery, separate from `_companion-link._tcp`
- explicit pairing with per-device public keys; until that exists, use the
  optional shared-secret `Hello` proof for real bridge tests
- encrypted transport over TCP or QUIC
- JSON-lines only for early diagnostics, then a compact framed protocol if
  latency or event rate demands it
- HID-usage-oriented events instead of platform-specific virtual keys
- heartbeat, reconnect, peer-close, and release-cleanup semantics

The bridge should not pretend to be an Apple device. It can borrow ideas from
Universal Control's topology and input model without copying Apple identity.
The current shared-secret proof is only a bridge hardening step, not the final
security model, because it authenticates `Hello` but does not encrypt event
traffic or prevent replay by an observer who can capture the plaintext session.

## Decision Gates

Stay on native while the evidence keeps advancing:

1. Windows resolves the Mac's `_companion-link._tcp` advertisement.
2. macOS resolves a Windows advertisement on the real LAN.
3. macOS logs show candidate, matching, connection, or rejection behavior for a
   Windows `_companion-link._tcp` candidate.
4. A Windows attempt reaches a reproducible Rapport/CompanionLink handshake.
5. The session reaches a `com.apple.universalcontrol` message or route.
6. Universal Control input/control messages can be decoded with keys negotiated
   during the session.

Switch to the bridge only when evidence shows the next native gate depends on
Apple-private identity material not available through a legitimate Windows Apple
Account path, or on non-negotiated Apple-only keys.

## What We Need Next

The immediate implementation blockers are evidence blockers, not code volume:

1. Restore or work around the local Universal Control link option enough to keep
   collecting Apple-to-Apple active session baselines.
2. Run the Windows passive CompanionLink browse and benign advertisement
   captures on the real LAN.
3. Run the minimal and shape-only CompanionLink candidate captures with Mac logs
   active.
4. If macOS connects to the Windows candidate, build the smallest TCP framing
   probe that records frame shapes without logging raw payloads.
5. Compare any Windows reaction against the Apple-to-Apple session baseline.
6. Decide whether to continue native session work or promote the bridge into the
   primary implementation track.

Until gate 3 or 4 moves, the right implementation work is instrumentation,
redaction, comparison, and small probes. After a native handshake appears, the
right work becomes framing, message labeling, and input-event decoding. If the
handshake is blocked by Apple-private trust, the right work becomes hardening the
AnyKBFlow bridge into the production path.
