# Native Feasibility Position

The preferred architecture is still native macOS Universal Control: leave
Apple's `/System/Library/CoreServices/UniversalControl.app` and `rapportd` in
control on the Mac, and make Windows participate only if it can be accepted by
that native stack.

The fallback bridge exists to keep the project deliverable, but it should not be
treated as the target until native admission is disproved with evidence.

## Current Answer

It is not proven impossible yet. It is high risk.

Apple's current Universal Control support requirements still say participating
devices must use the same Apple Account with two-factor authentication, plus
Bluetooth, Wi-Fi, and Handoff. Apple's Handoff security guide describes
iCloud-mediated BLE pairing, Keychain-stored symmetric keys, protected
advertisements, and larger peer-to-peer Wi-Fi payloads whose TLS trust derives
from an iCloud Keychain identity.

Sources checked on 2026-06-07:

- <https://support.apple.com/en-us/102459>
- <https://support.apple.com/guide/security-pdf/handoff-security-secf78dbe639/web>

That evidence does not prove Universal Control itself is closed to Windows, but
it defines the main question: can a Windows peer reach the native
Rapport/CompanionLink and `com.apple.universalcontrol` session path using either
public protocol negotiation or a legitimate Apple Account identity source on
Windows, such as iCloud for Windows or a future CLI login, without extracting
protected secrets or making false platform claims?

## Keep-Native Pass Gates

Native macOS compatibility remains viable while the captures keep advancing
through these gates:

1. Windows can see and resolve the Mac's `_companion-link._tcp` advertisement.
2. macOS can see and resolve a Windows-advertised benign probe on the real LAN.
3. macOS `rapportd` or `UniversalControl` reacts to a Windows
   `_companion-link._tcp` candidate with a candidate, matching, or explicit
   rejection log instead of only generic DNS-SD visibility.
4. A Windows attempt reaches a reproducible Rapport/CompanionLink handshake
   stage comparable to an Apple peer.
5. The session reaches a `com.apple.universalcontrol` service message or route.
6. Universal Control input/control messages can be decoded and generated using
   keys negotiated during that session.

Gates 1 through 3 are the immediate LAN/discovery experiments. Gates 4 through
6 require Apple-to-Apple baseline captures so Windows behavior can be compared
against a real peer rather than guessed from local self-advertisement.

## Native-Closed Evidence

Switching the Mac side to a project-owned bridge should require at least one
clear native blocker:

- macOS rejects the Windows peer before any Universal Control-specific message
  exchange because the peer lacks Apple Account, IDS, iCloud Keychain, private
  certificate, or private entitlement material, and that material is not exposed
  through supported Windows Apple software or APIs.
- The only accepted route requires misleading platform attestation or claiming
  Apple-private identity that Windows does not honestly possess.
- The input/control data plane remains encrypted with keys that are not
  negotiated on the observed session and are only available to Apple-trusted
  devices.
- Apple-to-Apple captures show required BLE, AWDL, or Rapport messages that
  depend on protected Continuity secrets unavailable to Windows through a
  legitimate Apple Account/iCloud for Windows path.
- Matching observable DNS-SD/TXT/service shape never causes macOS to admit the
  Windows peer beyond discovery, and logs identify this as an identity or trust
  rejection rather than a malformed-probe bug.

Do not count a failed minimal probe as final proof by itself. A failure becomes
decision-grade only after comparing with a real Apple peer's service shape and
session behavior.

## Immediate Evidence Order

Run the next native checks in this order:

1. Windows passive browse:
   `scripts/windows/capture-companion-link-discovery.py`, which runs
   `discover-companion-link --backend rust-mdns --redact`, summarizes it with
   `scripts/windows/summarize-companion-link-discovery-output.py`, and compares
   it with `scripts/windows/compare-companion-link-discovery-summaries.py`.
2. Benign Windows-to-macOS visibility:
   `cargo run -- advertise-mdns --seconds 60 --txt phase=visibility --txt role=windows-probe`
   while macOS runs
   `scripts/mac/capture-native-admission.sh --mode benign`.
3. Controlled CompanionLink candidate:
   `scripts/mac/capture-native-admission.sh --mode companion-link` on macOS
   while Windows runs the printed
   `advertise-mdns --service-type _companion-link._tcp --allow-apple-service`
   command.
4. Shape-only CompanionLink candidate:
   `scripts/mac/capture-native-admission.sh --mode shape` on macOS while
   Windows runs the printed `advertise-companion-link-shape` command.
5. Apple peer TXT and state comparison using `scripts/mac/uc-probe.sh`,
   `scripts/mac/summarize-uc-probe-artifact.py`, and
   `scripts/mac/compare-uc-probe-summaries.py`.
6. Apple-to-Apple active session capture using
   `scripts/mac/capture-uc-session.sh` and
   `scripts/mac/summarize-uc-session-artifact.py`.

Only after these observations should the Windows side attempt native session
framing beyond discovery.
