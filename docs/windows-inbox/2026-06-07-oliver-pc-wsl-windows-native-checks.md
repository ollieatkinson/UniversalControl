# 2026-06-07 Windows Native Checks

## Machine

- Windows version: see `2026-06-07-redacted-apple-account-environment.md`
- Host role: Windows-side native admission and fallback bridge candidate
- Shell used: WSL2 with Windows PowerShell interop for Apple Account probe
- Native terminal caveat: display geometry and native input probes still need a native Windows terminal, not WSL

## Repo State

- Branch: `trunk`
- Base commit before report commit: `c6c26e6`
- Uncommitted changes at note time: generated redacted Windows summaries

## Commands Run

```powershell
python scripts/windows/capture-apple-account-environment.py --powershell powershell.exe --transcript artifacts/windows-apple-account-environment-wsl.json --output docs/windows-inbox/2026-06-07-redacted-apple-account-environment.md
python scripts/windows/capture-companion-link-discovery.py --seconds 30
cargo run -- discover-companion-link --backend system --seconds 30
python scripts/windows/capture-display-probe.py
python scripts/windows/capture-native-admission.py --mode benign --seconds 15 --no-prompt
```

## Observations

- Apple Account environment probe completed successfully through Windows PowerShell.
- Native Apple Account path status: `apple_account_surface_present`.
- Installed Apple/iCloud software was detected, including an iCloud Appx package and Apple Mobile Device Support.
- Apple Mobile Device service was running.
- Account-related registry/certificate surfaces were present, but no Apple Account identifier was written.
- Manual same-account confirmation is still required: confirm locally that the Windows Apple software is signed in to the same Apple Account as the Mac.
- Rust mDNS passive CompanionLink discovery ran for 30 seconds but did not find or resolve the Mac `_companion-link._tcp.local.` service from this environment.
- System Bonjour discovery could not run from WSL because `dns-sd` was not found. This does not prove native Windows Bonjour is unavailable; rerun from a native Windows terminal if Bonjour tools are installed there.
- Display probe ran against the WSL stub backend, so native Windows display geometry is still missing.
- Benign `_anyuniversalcontrol-probe._tcp.local.` advertisement ran for 15 seconds and wrote a redacted summary. No TCP observer was enabled for benign mode, and no macOS visibility confirmation was captured in this run.

## Evidence Files

- `docs/windows-inbox/2026-06-07-redacted-apple-account-environment.md`
- `docs/windows-inbox/2026-06-07-redacted-companion-link-discovery.md`
- `docs/windows-inbox/2026-06-07-redacted-companion-link-discovery-compare.md`
- `docs/windows-inbox/2026-06-07-redacted-display-probe.md`
- `docs/windows-inbox/2026-06-07-redacted-native-admission-benign.md`

## Questions For Mac Side

- Was the Mac awake, on the same LAN, and advertising `_companion-link._tcp.local.` during the Windows passive browse?
- Can macOS see the benign Windows `_anyuniversalcontrol-probe._tcp.local.` advertisement from the 15 second run, or should we rerun while `scripts/mac/capture-native-admission.sh --mode benign` is active?
- Can the Mac-side watcher be started for coordinated `companion-link` and `shape` native-admission runs?
- After native Windows terminal access is available, rerun `python scripts/windows/capture-display-probe.py` so bridge geometry is not based on WSL stub output.
