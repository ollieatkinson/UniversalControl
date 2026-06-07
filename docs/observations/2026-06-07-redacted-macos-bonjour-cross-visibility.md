# Redacted macOS Bonjour Cross-Visibility Note

## Source

- Capture method: manual bounded `dns-sd -R` plus `dns-sd -B`
- Raw terminal output: not committed
- Date: 2026-06-07
- Service type: `_companion-link._tcp.local.`
- Local advertised instance: project-owned, name omitted
- Local advertised port: 49152
- Local advertised TXT count: 2

## Result

- Capture windows: 2
- Duration per window: 10 minutes
- Local registration became active: yes
- macOS browse saw the project-owned local advertisement: yes
- macOS browse saw the native local CompanionLink advertisement: yes
- macOS browse saw a Windows project-owned `_companion-link` advertisement: no
- Windows remote instance name, hostnames, addresses, TXT values, and interface identifiers: not included

## Interpretation

- macOS Bonjour advertisement was working locally during the test.
- No Windows `_companion-link._tcp.local.` advertisement crossed to the Mac during either window.
- This does not prove Windows Bonjour is blocked, because Windows was still installing `dns-sd` during the test.
- Next evidence should come from native Windows Bonjour, not WSL:
  - browse: `dns-sd -B _companion-link._tcp local`
  - advertise: `dns-sd -R "AnyKBFlow Windows Bonjour Probe" _companion-link._tcp local 49153 probe=windows-bonjour role=windows-native-visibility`
  - then compare whether Windows sees the Mac probe and whether macOS sees the Windows probe.

Do not paste raw Bonjour instance names, hostnames, addresses, TXT values, or interface identifiers into committed notes.
