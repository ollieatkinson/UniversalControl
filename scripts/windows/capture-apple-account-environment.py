#!/usr/bin/env python3
"""Capture a redacted Windows Apple Account/iCloud environment summary."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


POWERSHELL_PROBE = r"""
$ErrorActionPreference = "SilentlyContinue"

function Redact-Label($Value) {
    if ($null -eq $Value) { return "" }
    $Text = [string]$Value
    $Text = $Text -replace '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '<redacted-email>'
    $Text = $Text -replace '\\Users\\[^\\]+', '\Users\<redacted-user>'
    return $Text
}

function Classify-Path($Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return "missing" }
    $Text = [string]$Path
    if ($Text -match '(?i)\\WindowsApps\\') { return "windowsapps" }
    if ($Text -match '(?i)\\Program Files \(x86\)\\') { return "program_files_x86" }
    if ($Text -match '(?i)\\Program Files\\') { return "program_files" }
    if ($Text -match '(?i)\\Users\\') { return "user_profile" }
    return "other"
}

function Add-Count($Map, $Key) {
    if (-not $Map.ContainsKey($Key)) { $Map[$Key] = 0 }
    $Map[$Key] += 1
}

function Convert-CountMap($Map) {
    $Items = @()
    foreach ($Key in ($Map.Keys | Sort-Object)) {
        $Items += [PSCustomObject]@{
            class = $Key
            count = $Map[$Key]
        }
    }
    return $Items
}

function Get-NameClasses($Name) {
    $Classes = New-Object System.Collections.Generic.List[string]
    $Text = [string]$Name
    if ($Text -match '(?i)apple|icloud|mobileme|itunes') { $Classes.Add("apple_hint") }
    if ($Text -match '(?i)account|appleid|apple_id|dsid|user|email|identity') { $Classes.Add("account_hint") }
    if ($Text -match '(?i)credential|token|auth|secret|key|cert|password|cookie') { $Classes.Add("credential_hint") }
    if ($Text -match '(?i)sync|drive|photo|contact|calendar|bookmark|mail|handoff|continuity') { $Classes.Add("sync_hint") }
    if ($Text -match '(?i)path|folder|directory|cache') { $Classes.Add("path_hint") }
    if ($Classes.Count -eq 0) { $Classes.Add("other") }
    return $Classes
}

function Get-RegistrySurface($Label, $Path) {
    $Exists = Test-Path -LiteralPath $Path
    if (-not $Exists) {
        return [PSCustomObject]@{
            label = $Label
            exists = $false
            value_name_count = 0
            value_name_classes = @()
            subkey_count = 0
        }
    }

    $ValueNames = @()
    $SubkeyCount = 0
    try {
        $Item = Get-Item -LiteralPath $Path
        if ($null -ne $Item) { $ValueNames = @($Item.GetValueNames()) }
    } catch {}
    try {
        $SubkeyCount = @(Get-ChildItem -LiteralPath $Path).Count
    } catch {}

    $Classes = @{}
    foreach ($Name in $ValueNames) {
        foreach ($Class in (Get-NameClasses $Name)) {
            Add-Count $Classes $Class
        }
    }

    return [PSCustomObject]@{
        label = $Label
        exists = $true
        value_name_count = $ValueNames.Count
        value_name_classes = @(Convert-CountMap $Classes)
        subkey_count = $SubkeyCount
    }
}

function Get-InstalledProducts {
    $Paths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    $Products = @()
    foreach ($Path in $Paths) {
        $Items = @(Get-ItemProperty -Path $Path | Where-Object {
            $_.DisplayName -match '(?i)apple|icloud|bonjour'
        })
        foreach ($Item in $Items) {
            $Products += [PSCustomObject]@{
                display_name = Redact-Label $Item.DisplayName
                version = Redact-Label $Item.DisplayVersion
                publisher_class = if ($Item.Publisher -match '(?i)apple') { "apple" } elseif ($Item.Publisher) { "other" } else { "missing" }
                install_location_class = Classify-Path $Item.InstallLocation
            }
        }
    }
    return $Products
}

function Get-AppxPackages {
    $Packages = @()
    $Items = @(Get-AppxPackage | Where-Object {
        $_.Name -match '(?i)apple|icloud|bonjour' -or $_.Publisher -match '(?i)apple'
    })
    foreach ($Item in $Items) {
        $Packages += [PSCustomObject]@{
            name = Redact-Label $Item.Name
            version = Redact-Label $Item.Version
            install_location_class = Classify-Path $Item.InstallLocation
        }
    }
    return $Packages
}

function Get-AppleServices {
    $Services = @()
    $Items = @(Get-Service | Where-Object {
        $_.Name -match '(?i)apple|icloud|bonjour|mdns' -or $_.DisplayName -match '(?i)apple|icloud|bonjour|mdns'
    })
    foreach ($Item in $Items) {
        $Services += [PSCustomObject]@{
            name = Redact-Label $Item.Name
            display_name = Redact-Label $Item.DisplayName
            status = [string]$Item.Status
            start_type = if ($null -ne $Item.StartType) { [string]$Item.StartType } else { "unknown" }
        }
    }
    return $Services
}

function Get-AppleProcesses {
    $Processes = @()
    $Items = @(Get-Process | Where-Object {
        $_.Name -match '(?i)apple|icloud|bonjour|mdns'
    } | Group-Object -Property Name)
    foreach ($Item in $Items) {
        $Processes += [PSCustomObject]@{
            name = Redact-Label $Item.Name
            count = $Item.Count
        }
    }
    return $Processes
}

function Get-ExecutableCandidates {
    $ProgramFiles = $env:ProgramFiles
    $ProgramFilesX86 = ${env:ProgramFiles(x86)}
    $LocalAppData = $env:LOCALAPPDATA
    $Candidates = @(
        @{ label = "legacy_icloud_exe"; path = Join-CandidatePath $ProgramFilesX86 "Common Files\Apple\Internet Services\iCloud.exe" },
        @{ label = "legacy_icloud_services_exe"; path = Join-CandidatePath $ProgramFilesX86 "Common Files\Apple\Internet Services\iCloudServices.exe" },
        @{ label = "bonjour_mdnsresponder_exe_x86"; path = Join-CandidatePath $ProgramFilesX86 "Bonjour\mDNSResponder.exe" },
        @{ label = "bonjour_mdnsresponder_exe"; path = Join-CandidatePath $ProgramFiles "Bonjour\mDNSResponder.exe" },
        @{ label = "windowsapps_icloud_alias"; path = Join-CandidatePath $LocalAppData "Microsoft\WindowsApps\iCloud.exe" }
    )
    $Results = @()
    foreach ($Candidate in $Candidates) {
        $CandidatePath = $Candidate.path
        $Exists = $false
        if (-not [string]::IsNullOrWhiteSpace($CandidatePath)) {
            $Exists = Test-Path -LiteralPath $CandidatePath
        }
        $Results += [PSCustomObject]@{
            label = $Candidate.label
            exists = $Exists
            path_class = Classify-Path $CandidatePath
        }
    }
    return $Results
}

function Join-CandidatePath($Root, $Child) {
    if ([string]::IsNullOrWhiteSpace($Root)) { return "" }
    return Join-Path $Root $Child
}

function Get-CredentialTargetSummary {
    $Classes = @{}
    $Count = 0
    $Lines = @()
    try { $Lines = @(cmdkey /list) } catch {}
    foreach ($Line in $Lines) {
        if ($Line -match '^\s*Target:\s*(.+)$') {
            $Target = $Matches[1]
            if ($Target -match '(?i)apple|icloud|mobileme|itunes|bonjour') {
                $Count += 1
                foreach ($Class in (Get-NameClasses $Target)) {
                    Add-Count $Classes $Class
                }
            }
        }
    }
    return [PSCustomObject]@{
        apple_related_count = $Count
        target_name_classes = @(Convert-CountMap $Classes)
    }
}

function Get-AppleCertificateSummary {
    $Stores = @(
        @{ label = "current_user_my"; path = "Cert:\CurrentUser\My" },
        @{ label = "current_user_root"; path = "Cert:\CurrentUser\Root" },
        @{ label = "local_machine_my"; path = "Cert:\LocalMachine\My" },
        @{ label = "local_machine_root"; path = "Cert:\LocalMachine\Root" }
    )
    $Results = @()
    foreach ($Store in $Stores) {
        $Certs = @()
        try {
            $Certs = @(Get-ChildItem -Path $Store.path | Where-Object {
                $_.Subject -match '(?i)apple|icloud|mobileme' -or $_.Issuer -match '(?i)apple|icloud|mobileme'
            })
        } catch {}
        $Results += [PSCustomObject]@{
            store = $Store.label
            apple_related_count = $Certs.Count
            with_private_key_count = @($Certs | Where-Object { $_.HasPrivateKey }).Count
        }
    }
    return $Results
}

$Os = $null
try { $Os = Get-CimInstance Win32_OperatingSystem } catch {}
$RegistrySurfaces = @(
    Get-RegistrySurface "hkcu_apple_internet_services" "HKCU:\Software\Apple Inc.\Internet Services"
    Get-RegistrySurface "hkcu_apple_icloud" "HKCU:\Software\Apple Inc.\iCloud"
    Get-RegistrySurface "hkcu_apple_accounts" "HKCU:\Software\Apple Inc.\Accounts"
    Get-RegistrySurface "hkcu_mobileme_accounts" "HKCU:\Software\Apple Computer, Inc.\MobileMe Accounts"
    Get-RegistrySurface "hklm_apple_internet_services" "HKLM:\Software\Apple Inc.\Internet Services"
    Get-RegistrySurface "hklm_wow6432_apple_internet_services" "HKLM:\Software\WOW6432Node\Apple Inc.\Internet Services"
)

$Result = [ordered]@{
    schema = "apple_account_environment_v1"
    captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    host = [ordered]@{
        os_caption = if ($null -ne $Os) { Redact-Label $Os.Caption } else { "unknown" }
        os_build = if ($null -ne $Os) { Redact-Label $Os.BuildNumber } else { "unknown" }
        powershell_version = $PSVersionTable.PSVersion.ToString()
        powershell_edition = if ($PSVersionTable.PSEdition) { $PSVersionTable.PSEdition } else { "Desktop" }
    }
    installed_products = @(Get-InstalledProducts)
    appx_packages = @(Get-AppxPackages)
    services = @(Get-AppleServices)
    processes = @(Get-AppleProcesses)
    executable_candidates = @(Get-ExecutableCandidates)
    registry_surfaces = @($RegistrySurfaces)
    credential_manager = Get-CredentialTargetSummary
    certificates = @(Get-AppleCertificateSummary)
    redaction = [ordered]@{
        account_identifiers_included = $false
        credential_target_names_included = $false
        registry_values_included = $false
        certificate_subjects_included = $false
        install_paths_included = $false
        hostnames_usernames_or_addresses_included = $false
    }
}

$Result | ConvertTo-Json -Depth 8 -Compress
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture a redacted Windows Apple Account/iCloud environment report "
            "for native Universal Control eligibility work."
        )
    )
    parser.add_argument("--transcript", type=Path, help="Sanitized JSON transcript path.")
    parser.add_argument("--output", type=Path, help="Redacted Markdown summary path.")
    parser.add_argument("--powershell", help="PowerShell executable to use.")
    parser.add_argument(
        "--summary-from-transcript",
        type=Path,
        help="Render a Markdown summary from an existing sanitized JSON transcript.",
    )
    parser.add_argument(
        "--print-script-only",
        action="store_true",
        help="Print the embedded PowerShell probe and exit.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    day = now.strftime("%Y-%m-%d")
    transcript = resolve_path(
        repo_root,
        args.transcript,
        repo_root / "artifacts" / f"windows-apple-account-environment-{stamp}.json",
    )
    output = resolve_path(
        repo_root,
        args.output,
        repo_root
        / "docs"
        / "windows-inbox"
        / f"{day}-redacted-apple-account-environment.md",
    )
    if output.exists() and args.output is None:
        output = (
            repo_root
            / "docs"
            / "windows-inbox"
            / f"{day}-{stamp}-redacted-apple-account-environment.md"
        )

    if args.print_script_only:
        print(POWERSHELL_PROBE)
        return 0

    if args.summary_from_transcript:
        summary_input = resolve_path(repo_root, args.summary_from_transcript, args.summary_from_transcript)
        data = load_probe_json(summary_input)
        summary = render_summary(summary_input, data)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(summary, encoding="utf-8")
        print(f"Wrote redacted summary: {output}")
        return 0

    powershell = args.powershell or find_powershell()
    if not powershell:
        print("PowerShell was not found. Run this from native Windows or pass --powershell.", file=sys.stderr)
        return 127

    print("Windows Apple Account/iCloud environment capture")
    print(f"Sanitized JSON transcript: {transcript}")
    print(f"Redacted summary output: {output}")
    print(f"PowerShell executable: {powershell}")
    print()

    transcript.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = run_powershell_probe(powershell)
    transcript.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output.write_text(render_summary(transcript, data), encoding="utf-8")
    print(f"Wrote sanitized JSON transcript: {transcript}")
    print(f"Wrote redacted summary: {output}")
    return int(data.get("command_return_code", 0) or 0)


def resolve_path(repo_root: Path, value: Path | None, default: Path) -> Path:
    if value is None:
        return default
    if value.is_absolute():
        return value
    return repo_root / value


def find_powershell() -> str | None:
    for name in ("pwsh", "powershell"):
        path = shutil.which(name)
        if path:
            return path
    return None


def run_powershell_probe(powershell: str) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as script:
        script.write(POWERSHELL_PROBE)
        script_path = Path(script.name)
    try:
        completed = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    finally:
        try:
            script_path.unlink()
        except OSError:
            pass

    try:
        data = json.loads(completed.stdout)
        if not isinstance(data, dict):
            raise ValueError("probe JSON root was not an object")
    except (json.JSONDecodeError, ValueError):
        data = {
            "schema": "apple_account_environment_v1",
            "capture_error": "PowerShell probe did not emit valid JSON",
        }
    data["command_return_code"] = completed.returncode
    data["stderr_line_count"] = len([line for line in completed.stderr.splitlines() if line.strip()])
    return data


def load_probe_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def render_summary(path: Path, data: dict[str, Any]) -> str:
    installed_products = list_of_dicts(data.get("installed_products"))
    appx_packages = list_of_dicts(data.get("appx_packages"))
    services = list_of_dicts(data.get("services"))
    processes = list_of_dicts(data.get("processes"))
    executables = list_of_dicts(data.get("executable_candidates"))
    registry = list_of_dicts(data.get("registry_surfaces"))
    certificates = list_of_dicts(data.get("certificates"))
    credential_manager = dict_or_empty(data.get("credential_manager"))
    host = dict_or_empty(data.get("host"))

    evidence_status = classify_evidence(
        installed_products,
        appx_packages,
        services,
        processes,
        executables,
        registry,
        certificates,
        credential_manager,
        bool(data.get("capture_error")),
    )

    lines = [
        "# Redacted Windows Apple Account Environment Summary",
        "",
        "## Source",
        "",
        f"- Sanitized transcript file: `{display_path(path)}`",
        "- Raw PowerShell stderr: not included",
        "- Account identifiers: not included",
        "- Registry values, credential target names, certificate subjects, install paths, hostnames, usernames, and IP addresses: not included",
        "",
        "## Command Result",
        "",
        f"- Schema: `{data.get('schema', 'unknown')}`",
        f"- Probe completed: {format_bool(not data.get('capture_error'))}",
        f"- Command return code: {data.get('command_return_code', 'unknown')}",
        f"- PowerShell stderr lines: {data.get('stderr_line_count', 'unknown')}",
        f"- OS caption: `{host.get('os_caption', 'unknown')}`",
        f"- OS build: `{host.get('os_build', 'unknown')}`",
        f"- PowerShell edition: `{host.get('powershell_edition', 'unknown')}`",
        f"- PowerShell version: `{host.get('powershell_version', 'unknown')}`",
        "",
        "## Supported Apple Software",
        "",
        f"- Installed Apple/iCloud/Bonjour products: {format_named_items(installed_products, 'display_name', include_version=True)}",
        f"- Appx Apple/iCloud packages: {format_named_items(appx_packages, 'name', include_version=True)}",
        f"- Apple/iCloud/Bonjour services: {format_services(services)}",
        f"- Apple/iCloud/Bonjour processes: {format_processes(processes)}",
        f"- Executable candidate labels present: {format_present_executables(executables)}",
        "",
        "## Same-Account Trust Clues",
        "",
        f"- Apple-related registry surfaces present: {format_registry(registry)}",
        f"- Apple-related Credential Manager targets: {credential_manager.get('apple_related_count', 0)}",
        f"- Credential target-name classes: {format_count_classes(credential_manager.get('target_name_classes'))}",
        f"- Apple-related certificates by store: {format_certificates(certificates)}",
        "",
        "## Interpretation",
        "",
        f"- Native Apple Account path status: `{evidence_status}`",
        "- Meaning:",
        "  - `apple_account_surface_present` means Windows appears to have supported Apple software plus local account or credential surfaces worth testing.",
        "  - `installed_but_no_account_surface_detected` means iCloud/Apple software exists but this probe did not find account-state clues.",
        "  - `apple_software_missing` means install or sign in to supported Apple software before treating native trust as blocked.",
        "- Manual check still required: confirm the Windows Apple software is signed in to the same Apple Account as the Mac. This summary deliberately does not record the account identifier.",
        "",
    ]
    return "\n".join(lines)


def classify_evidence(
    installed_products: list[dict[str, Any]],
    appx_packages: list[dict[str, Any]],
    services: list[dict[str, Any]],
    processes: list[dict[str, Any]],
    executables: list[dict[str, Any]],
    registry: list[dict[str, Any]],
    certificates: list[dict[str, Any]],
    credential_manager: dict[str, Any],
    capture_error: bool,
) -> str:
    if capture_error:
        return "unknown_capture_failed"

    names = " ".join(
        str(item.get(key, ""))
        for collection, key in (
            (installed_products, "display_name"),
            (appx_packages, "name"),
            (services, "name"),
            (services, "display_name"),
            (processes, "name"),
        )
        for item in collection
    ).lower()
    icloud_present = "icloud" in names or any(
        item.get("exists") and "icloud" in str(item.get("label", "")).lower()
        for item in executables
    )
    apple_software_present = bool(installed_products or appx_packages or services or processes)
    apple_software_present = apple_software_present or any(item.get("exists") for item in executables)
    account_surface_present = any(item.get("exists") for item in registry)
    account_surface_present = account_surface_present or int(credential_manager.get("apple_related_count", 0) or 0) > 0
    account_surface_present = account_surface_present or any(
        int(item.get("with_private_key_count", 0) or 0) > 0 for item in certificates
    )

    if icloud_present and account_surface_present:
        return "apple_account_surface_present"
    if icloud_present:
        return "installed_but_no_account_surface_detected"
    if apple_software_present:
        return "apple_software_present_no_icloud"
    return "apple_software_missing"


def list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def display_path(path: Path) -> str:
    parts = path.parts
    for marker in ("artifacts", "docs"):
        if marker in parts:
            return "/".join(parts[parts.index(marker) :])
    return path.name


def format_named_items(items: list[dict[str, Any]], key: str, *, include_version: bool) -> str:
    if not items:
        return "none"
    rendered: list[str] = []
    seen: set[str] = set()
    for item in items:
        name = str(item.get(key, "")).strip() or "unknown"
        version = str(item.get("version", "")).strip()
        text = f"`{name}`"
        if include_version and version:
            text = f"{text} version `{version}`"
        if text not in seen:
            seen.add(text)
            rendered.append(text)
    return ", ".join(rendered[:12]) + ("; truncated" if len(rendered) > 12 else "")


def format_services(items: list[dict[str, Any]]) -> str:
    if not items:
        return "none"
    rendered = []
    for item in items[:12]:
        name = item.get("name", "unknown")
        status = item.get("status", "unknown")
        start_type = item.get("start_type", "unknown")
        rendered.append(f"`{name}` status `{status}` start `{start_type}`")
    return ", ".join(rendered) + ("; truncated" if len(items) > 12 else "")


def format_processes(items: list[dict[str, Any]]) -> str:
    if not items:
        return "none"
    return ", ".join(f"`{item.get('name', 'unknown')}`={item.get('count', 0)}" for item in items)


def format_present_executables(items: list[dict[str, Any]]) -> str:
    present = [f"`{item.get('label', 'unknown')}`" for item in items if item.get("exists")]
    return ", ".join(present) if present else "none"


def format_registry(items: list[dict[str, Any]]) -> str:
    present = [item for item in items if item.get("exists")]
    if not present:
        return "none"
    return ", ".join(
        f"`{item.get('label', 'unknown')}` values `{item.get('value_name_count', 0)}` classes {format_count_classes(item.get('value_name_classes'))} subkeys `{item.get('subkey_count', 0)}`"
        for item in present
    )


def format_certificates(items: list[dict[str, Any]]) -> str:
    relevant = [
        item
        for item in items
        if int(item.get("apple_related_count", 0) or 0) > 0
        or int(item.get("with_private_key_count", 0) or 0) > 0
    ]
    if not relevant:
        return "none"
    return ", ".join(
        f"`{item.get('store', 'unknown')}` count `{item.get('apple_related_count', 0)}` private_key `{item.get('with_private_key_count', 0)}`"
        for item in relevant
    )


def format_count_classes(value: Any) -> str:
    items = list_of_dicts(value)
    if not items:
        return "none"
    return ", ".join(f"`{item.get('class', 'unknown')}`={item.get('count', 0)}" for item in items)


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
