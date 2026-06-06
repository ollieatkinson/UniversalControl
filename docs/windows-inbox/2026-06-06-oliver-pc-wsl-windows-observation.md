# 2026-06-06 Windows Observation

## Machine

- Windows version: Windows 11 Pro
- Build: 26200
- Host role: Windows-side development/prototype host
- Shell context: Debian 12 under WSL2 on `microsoft-standard-WSL2`
- Network adapters: not committed; local adapter names and addresses are treated as local identifiers
- Active adapter: redacted
- Firewall profile: Private

## Repo State

- Branch: `trunk`
- Commit when this note was started: `5eeb447 Add native input probe commands`
- Uncommitted changes at note time: mDNS discovery CLI and this report

## What Changed

- Added `anykbflow discovery browse` for DNS-SD/mDNS service browsing.
- Added `anykbflow discovery advertise` for publishing a controlled test service from Windows.
- Added native input probe commands in `5eeb447`:
  - `probe listen`
  - `probe grab`
  - `probe grab --suppress`
  - `probe inject`

## Commands Run

```sh
git fetch origin --prune
git log --oneline --decorate --graph --all -8
cargo fmt
cargo test
cargo check
cargo check --target x86_64-apple-darwin
cargo check --target x86_64-pc-windows-msvc
cargo run -- probe listen --count 1
```

```powershell
[System.Environment]::OSVersion.VersionString
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber
Get-NetConnectionProfile | Select-Object Name, NetworkCategory, IPv4Connectivity, IPv6Connectivity
Get-Command Resolve-DnsName -ErrorAction SilentlyContinue
Get-Command dns-sd -ErrorAction SilentlyContinue
Resolve-DnsName -Name _companion-link._tcp.local -Type PTR -DnsOnly -ErrorAction Stop
```

## Observations

- The Mac side pushed `2f1102b Bootstrap native Universal Control investigation`; this Windows work was rebased on top of the merged `origin/trunk`.
- This machine has Windows PowerShell available from WSL2.
- `dns-sd` is not currently available in the Windows PATH.
- PowerShell `Resolve-DnsName -DnsOnly` did not resolve `_companion-link._tcp.local`; this is not strong evidence about mDNS visibility because `-DnsOnly` bypasses multicast DNS behavior.
- `anykbflow` now has its own cross-platform mDNS commands, so the next Windows check should use the Rust binary rather than relying on OS tools.
- Local Rust checks passed for Linux, macOS target, and Windows target after the discovery CLI was added.
- The current Windows prototype is source-controlled in this repo on `trunk`.
- The implementation language/runtime is Rust 1.94.0 for the shared daemon and probes.

## Evidence Files

- No raw captures committed.
- No unredacted TXT records, addresses, or local host identifiers committed.

## First Requested Windows Report Answers

1. Does Windows see this Mac's `_companion-link._tcp.local` advertisement?
   - Not proven yet. The only command tried was `Resolve-DnsName -DnsOnly`, which returned `DNS_ERROR_RCODE_NAME_ERROR` and is not a valid multicast browse.

2. Which TXT keys and port are visible?
   - Not proven yet. Run:

     ```powershell
     cargo run -- discovery browse --service _companion-link._tcp.local. --seconds 30
     ```

3. Can Windows advertise an mDNS service visible to macOS?
   - Not proven yet. The repo now has the command needed to test it:

     ```powershell
     cargo run -- discovery advertise --service _anykbflow-test._tcp.local. --instance anykbflow-windows --host anykbflow.local. --addr <redacted-lan-ip> --port 24800 --txt role=windows --txt probe=phase1 --seconds 60
     ```

4. Is the Windows prototype currently source-controlled somewhere outside this empty initial repo?
   - No separate Windows prototype was found. The current prototype is now in this repo on `trunk`.

5. What language/runtime is the current Windows implementation using?
   - Rust. The current Windows-native target check is `x86_64-pc-windows-msvc`.

## Questions For Mac Side

- When Windows advertises `_anykbflow-test._tcp.local.`, does macOS `dns-sd -B _anykbflow-test._tcp local` see it?
- Do `rapportd` or `UniversalControl` logs react to the test service at all?
- Can the Mac side capture a real Apple-to-Apple Universal Control `_companion-link._tcp` TXT record shape so the Windows advertiser can mimic only non-sensitive structural fields?
