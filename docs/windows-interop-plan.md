# Windows Interop Plan

## Target

Let a Windows PC and a Mac share one keyboard and mouse while keeping the Mac side on native Apple Universal Control if feasible:

- push pointer across display edges
- transfer keyboard focus with pointer focus
- preserve normal keyboard shortcuts as far as possible
- support high-rate pointer movement, clicks, scroll, and key events
- leave room for drag and clipboard once input transport is stable

## Reality Check

The native Apple feature is not just "send mouse events over TCP." Public requirements and local evidence point to a Continuity stack that combines proximity, Apple Account identity, Rapport/CompanionLink, peer-to-peer Wi-Fi/AWDL, private HID dispatch, and private window-server integration.

The project should keep native macOS compatibility as the lead strategy until evidence proves it cannot work. A separate Mac agent is not the target architecture; it is the fallback if Apple's native trust/session path cannot admit Windows.

The native/fallback decision is tracked in
[native-feasibility.md](native-feasibility.md). In short, native remains open
while Windows can advance through observable Rapport/CompanionLink and
`com.apple.universalcontrol` gates without Apple-private identity material. It
closes only when captures show the remaining path depends on Apple Account,
iCloud Keychain, private certificates, protected entitlements, or non-negotiated
Apple-only keys.

## Track A: Native Compatibility Investigation

Purpose: learn whether a Windows peer can be accepted by macOS Universal Control without Apple-private secrets or entitlements.

Work items:

1. Use `cargo run -- discover-companion-link --backend rust-mdns --seconds 30
   --redact` on Windows for passive DNS-SD browsing of
   `_companion-link._tcp`, then summarize it with
   `scripts/windows/summarize-companion-link-discovery-output.py`.
2. Parse and log TXT records without assigning meanings prematurely.
3. Compare the Rust mDNS backend with `--backend system` if Bonjour's `dns-sd.exe` is installed.
4. Use `cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe` to prove macOS can see and resolve a Windows-advertised service.
5. Run the minimal controlled `_companion-link._tcp` candidate experiment in [native-candidate-experiments.md](native-candidate-experiments.md) using `--allow-apple-service` only while macOS logs are captured.
6. Observe whether macOS `rapportd` or `UniversalControl` logs react to a Windows advertisement.
7. Attempt a minimal TCP connection to the advertised `rapportd` listener only after logging what Apple peers do first.
8. Continue native work while the session advances with observable, reproducible messages.
9. Stop only if authentication requires Apple Account/iCloud Keychain material, private Apple signatures, or entitlement-protected peer claims that Windows cannot possess.

Success evidence:

- macOS logs show the Windows peer as a candidate Universal Control device.
- A reproducible handshake trace reaches a Universal Control-specific message exchange.
- At least one input/control message can be decoded or generated without relying on Apple secrets.

Main risk:

- Rapport/CompanionLink refuses non-Apple-trusted peers before Universal Control-specific messages are exposed.

## Track B: Project-Owned Mac/Windows Bridge Fallback

Purpose: deliver the requested Mac plus Windows keyboard/mouse sharing only if native Universal Control authentication is closed.

Architecture:

- Mac agent:
  - captures local input near configured screen edges
  - owns display topology and focus state
  - sends normalized HID-like events to Windows
  - receives events when Windows is the source and injects them into macOS using public APIs where possible
- Windows agent:
  - captures low-level mouse/keyboard events
  - injects input through `SendInput`
  - participates in discovery and pairing
  - maintains display-edge topology
- Shared protocol:
  - mDNS/DNS-SD discovery
  - explicit pairing with project-owned public keys
  - encrypted event stream over TCP or QUIC
  - event schema based on HID usages, not platform-specific virtual key codes

Fallback entry criteria:

- Apple-to-Apple captures identify a native handshake that cannot be completed without Apple-private identity material.
- macOS logs show Windows discovery but reject the peer before `com.apple.universalcontrol` negotiation.
- The accepted data plane is encrypted with keys not negotiated on the wire and not available to Windows.
- Native Universal Control requires remote attestations or platform claims that would be dishonest or unsafe to spoof.

Why this track remains useful if needed:

- It gets the Windows/Mac user experience working without pretending Windows is an Apple-account device.
- It can still use the reverse-engineered discovery, topology, and HID mapping ideas from Universal Control.
- It creates a test harness for latency, event mapping, and focus transitions.

## Windows Agent Responsibilities

Native discovery:

- browse `_companion-link._tcp` for Apple observations
- record whether advertising `_companion-link._tcp` changes macOS logs, but do not ship that as the primary bridge service until its semantics are understood

Fallback discovery:

- advertise the project-specific `_anykbflow._tcp.local.` service only for the bridge track
- keep `_anykbflow._tcp.local.` separate from `_companion-link._tcp.local.` so bridge testing does not masquerade as native Universal Control

Input capture:

- low-level mouse hook
- low-level keyboard hook
- raw input where high-resolution mouse data is needed
- suppress local delivery only while focus is remote

Input injection:

- use `SendInput` for keyboard, mouse, scroll, and button events
- preserve physical/logical key distinction in the event schema
- handle keyboard layout explicitly

Security:

- generate a per-device identity key
- require explicit pairing confirmation on both machines
- encrypt sessions
- reject unauthenticated event injection

Diagnostics:

- write Markdown status reports into `docs/windows-inbox/`
- include packet/log summaries and implementation state
- redact hostnames, local IPs, stable Bluetooth addresses, and account identifiers

## First Milestone

Build enough discovery and instrumentation to answer these questions:

1. Can Windows see the Mac's `_companion-link._tcp` advertisement?
2. Can macOS see a Windows advertisement?
3. Does macOS Universal Control react to a Windows peer at the discovery layer?
4. During a real Apple-to-Apple Universal Control session, which stream carries input?
5. Is the input stream decodable without Apple-private key material?

Do not start full native-protocol implementation until those questions have evidence.
