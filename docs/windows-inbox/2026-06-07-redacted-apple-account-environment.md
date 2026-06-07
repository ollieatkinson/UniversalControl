# Redacted Windows Apple Account Environment Summary

## Source

- Sanitized transcript file: `artifacts/windows-apple-account-environment-wsl.json`
- Raw PowerShell stderr: not included
- Account identifiers: not included
- Registry values, credential target names, certificate subjects, install paths, hostnames, usernames, and IP addresses: not included

## Command Result

- Schema: `apple_account_environment_v1`
- Probe completed: yes
- Command return code: 0
- PowerShell stderr lines: 0
- OS caption: `Microsoft Windows 11 Pro`
- OS build: `26200`
- PowerShell edition: `Desktop`
- PowerShell version: `5.1.26100.8457`

## Supported Apple Software

- Installed Apple/iCloud/Bonjour products: `iCloud Outlook` version `15.5.0.23`, `Apple Mobile Device Support` version `19.0.1.27`
- Appx Apple/iCloud packages: `AppleInc.iCloud` version `15.8.118.0`
- Apple/iCloud/Bonjour services: `Apple Mobile Device Service` status `Running` start `Automatic`
- Apple/iCloud/Bonjour processes: `AppleMobileDeviceService`=1
- Executable candidate labels present: none

## Same-Account Trust Clues

- Apple-related registry surfaces present: `hkcu_apple_internet_services` values `1` classes `other`=1 subkeys `1`, `hklm_apple_internet_services` values `3` classes `other`=3 subkeys `1`, `hklm_wow6432_apple_internet_services` values `1` classes `other`=1 subkeys `0`
- Apple-related Credential Manager targets: 0
- Credential target-name classes: none
- Apple-related certificates by store: `current_user_my` count `1` private_key `0`

## Interpretation

- Native Apple Account path status: `apple_account_surface_present`
- Meaning:
  - `apple_account_surface_present` means Windows appears to have supported Apple software plus local account or credential surfaces worth testing.
  - `installed_but_no_account_surface_detected` means iCloud/Apple software exists but this probe did not find account-state clues.
  - `apple_software_missing` means install or sign in to supported Apple software before treating native trust as blocked.
- Manual check still required: confirm the Windows Apple software is signed in to the same Apple Account as the Mac. This summary deliberately does not record the account identifier.
