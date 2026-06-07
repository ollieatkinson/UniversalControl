# 2026-06-07 Native Windows CompanionLink TCP Check

## Context

- Request: macOS advertised `_companion-link._tcp.local`; Windows should check visibility and try to message it.
- Pull status before the check: both `AnyKBFlow` and sibling `UniversalControl` were already up to date.
- Windows host role: Windows-side development/prototype host, commands launched from WSL with native Windows PowerShell interop where noted.

## Discovery Results

- WSL/Linux Rust mDNS did not see the Mac advertisement during a 45 second browse:
  - Summary: `docs/windows-inbox/2026-06-07-20260607T102226Z-redacted-companion-link-discovery.md`
  - Comparison: `docs/windows-inbox/2026-06-07-20260607T102226Z-redacted-companion-link-discovery-compare.md`
- Bonjour `dns-sd.exe` was not available on Windows PATH or in the standard Bonjour/Common Files locations checked from PowerShell.
- PowerShell `Resolve-DnsName _companion-link._tcp.local PTR` returned a normal DNS failure; this is not strong mDNS evidence.
- Native Windows Rust mDNS did resolve `_companion-link._tcp.local` when run through Windows Cargo:
  - Summary: `docs/windows-inbox/2026-06-07-20260607T102817Z-redacted-native-windows-companion-link-discovery.md`
  - Comparison: `docs/windows-inbox/2026-06-07-20260607T102817Z-redacted-native-windows-companion-link-discovery-compare.md`
- The native Windows browse saw two resolved services:
  - one Apple/Rapport-shaped service with `rp*` TXT keys
  - one controlled probe-shaped service with `probe` and `role` TXT keys

## TCP Check

- A local-only unredacted native Windows browse was used to extract the controlled probe endpoint. The unredacted endpoint was not committed.
- The controlled probe address was not one of the local Windows IPv4 addresses.
- TCP connect to the controlled probe's advertised port `49152` failed with connection refused.
- TCP connect to the same controlled probe host on the hinted port `49153` also failed with connection refused.
- No TCP payload was delivered.
- The Apple/Rapport-shaped `_companion-link` service was not probed with arbitrary bytes.

## Interpretation

- Native Windows discovery can see the Mac-side `_companion-link._tcp.local` advertisement when the Rust mDNS browser runs as a Windows process.
- WSL mDNS remains insufficient for this LAN discovery path.
- The controlled service is visible, but the Mac-side listener was not accepting TCP on the advertised port or on `49153` during this check.
- Next coordinated run should make the Mac advertiser bind a TCP observer on the same port it publishes, then keep it running while Windows repeats the native browse and hello.
