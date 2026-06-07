#!/usr/bin/env python3
"""Create a commit-safe summary from a macOS Universal Control probe artifact."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


NATIVE_PROCESSES = (
    "UniversalControl",
    "rapportd",
    "sharingd",
    "nearbyd",
    "useractivityd",
    "bluetoothd",
    "mDNSResponder",
)

STRING_HINTS = {
    "CompanionLink": re.compile(r"CompanionLink|Companion", re.I),
    "EnsembleHID": re.compile(r"EnsembleHID|HIDReport|HID", re.I),
    "P2P": re.compile(r"P2P|DirectLink|DirectMessage", re.I),
    "OPACK": re.compile(r"OPACK", re.I),
    "AWDL": re.compile(r"AWDL", re.I),
    "WiFiP2P": re.compile(r"WiFiP2P|wifip2p", re.I),
    "Pointer": re.compile(r"Pointer|Cursor|Mouse", re.I),
    "Keyboard": re.compile(r"Keyboard|Key", re.I),
    "Drag": re.compile(r"Drag", re.I),
    "Pasteboard": re.compile(r"Pasteboard|Clipboard", re.I),
    "Nearby": re.compile(r"Nearby|Proximity|Ranging", re.I),
}


@dataclass
class BrowseEvent:
    action: str
    flags: str
    interface: str
    domain: str
    service_type: str
    instance: str


@dataclass
class ResolveEvent:
    fullname: str
    host: str
    port: str
    interface: str
    txt: list[tuple[str, str]]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize artifacts from scripts/mac/uc-probe.sh without leaking identifiers."
    )
    parser.add_argument("artifact_dir", type=Path, help="Artifact directory under artifacts/")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown summary to this path instead of stdout.",
    )
    args = parser.parse_args()

    if not args.artifact_dir.is_dir():
        parser.error(f"artifact directory not found: {args.artifact_dir}")

    summary = render_summary(args.artifact_dir)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def render_summary(artifact_dir: Path) -> str:
    metadata = parse_readme(read_file(artifact_dir / "README.txt"))
    os_info = parse_sw_vers(read_file(artifact_dir / "os.txt"))
    arch = parse_uname_arch(read_file(artifact_dir / "uname.txt"))
    bundle_info = parse_plist_pairs(read_file(artifact_dir / "universalcontrol-info-plist.txt"))
    entitlements = parse_entitlement_keys(read_file(artifact_dir / "universalcontrol-entitlements.txt"))
    launchd_ensemble = parse_launchctl(read_file(artifact_dir / "launchctl-ensemble.txt"))
    launchd_rapportd = parse_launchctl(read_file(artifact_dir / "launchctl-rapportd.txt"))
    processes = summarize_processes(read_file(artifact_dir / "processes.txt"))
    network_hardware = summarize_network_hardware(read_file(artifact_dir / "network-hardware.txt"))
    continuity_health = summarize_continuity_health(read_file(artifact_dir / "continuity-health.txt"))
    companion_browse = parse_browse(read_file(artifact_dir / "companion-link-browse.txt"))
    universalcontrol_browse = parse_browse(read_file(artifact_dir / "universalcontrol-browse.txt"))
    companion_resolve = parse_resolve(read_file(artifact_dir / "companion-link-resolve-self.txt"))
    lsof_rapportd = summarize_lsof(read_file(artifact_dir / "lsof-rapportd.txt"))
    lsof_universalcontrol = summarize_lsof(read_file(artifact_dir / "lsof-universalcontrol.txt"))
    strings = summarize_strings(read_file(artifact_dir / "universalcontrol-strings.txt"))
    defaults = summarize_defaults(read_file(artifact_dir / "defaults-rapport-sharing.txt"))
    uc_byhost_preferences = summarize_uc_byhost_preferences(read_file(artifact_dir / "universalcontrol-byhost-preferences.txt"))
    display_cache = summarize_display_cache(read_file(artifact_dir / "display-cache-shape.txt"))
    logs = summarize_logs(read_file(artifact_dir / "recent-uc-logs.txt"))
    health_logs = summarize_health_logs(read_file(artifact_dir / "continuity-health-logs.txt"))

    lines = [
        "# Redacted macOS Universal Control Probe Summary",
        "",
        "## Source",
        "",
        f"- Artifact: `{artifact_dir.name}`",
        f"- Created: {metadata.get('created', 'unknown')}",
        "- Raw output: not included",
        "",
        "## Host",
        "",
        f"- Product: {os_info.get('ProductName', 'unknown')}",
        f"- Version: {os_info.get('ProductVersion', 'unknown')}",
        f"- Build: {os_info.get('BuildVersion', 'unknown')}",
        f"- Architecture: {arch}",
        "- Hostname, local addresses, and hardware addresses: not included",
        "",
        "## Universal Control Bundle",
        "",
        f"- Bundle identifier: `{bundle_info.get('CFBundleIdentifier', 'unknown')}`",
        f"- Bundle version: `{bundle_info.get('CFBundleVersion', 'unknown')}`",
        f"- Short version: `{bundle_info.get('CFBundleShortVersionString', 'unknown')}`",
        f"- Launchd label: `{bundle_info.get('LSLaunchDLabel', 'unknown')}`",
        f"- Minimum macOS: `{bundle_info.get('LSMinimumSystemVersion', 'unknown')}`",
        f"- Entitlement keys: {format_set(entitlements)}",
        f"- Entitlement count: {len(entitlements)}",
        "",
        "## Launchd",
        "",
        f"- UniversalControl: {format_launchd(launchd_ensemble)}",
        f"- rapportd: {format_launchd(launchd_rapportd)}",
        "",
        "## Processes",
        "",
        f"- Observed process names: {format_counter(processes)}",
        "",
        "## Network Interfaces",
        "",
        f"- Hardware port count: {network_hardware['port_count']}",
        f"- Device identifiers: {format_set(network_hardware['devices'])}",
        f"- Wi-Fi port present: {format_bool(network_hardware['wifi_present'])}",
        "- Hardware addresses: not included",
        "",
        "## Continuity Health",
        "",
        f"- Wi-Fi device: {format_code_or_unknown(continuity_health.get('wifi_device', 'unknown'))}",
        f"- Wi-Fi power: {continuity_health.get('wifi_power', 'unknown')}",
        f"- Wi-Fi interface active: {format_bool(continuity_health['wifi_active'])}",
        f"- awdl0 present: {format_bool(continuity_health['awdl_present'])}",
        f"- awdl0 active: {format_bool(continuity_health['awdl_active'])}",
        f"- Firewall global state: {continuity_health.get('firewall_global', 'unknown')}",
        f"- Firewall block-all state: {continuity_health.get('firewall_block_all', 'unknown')}",
        f"- Firewall stealth mode: {continuity_health.get('firewall_stealth', 'unknown')}",
        "- Local addresses and hardware addresses: not included",
        "",
        "## DNS-SD",
        "",
        "### _companion-link._tcp Browse",
        "",
    ]
    lines.extend(render_browse_summary(companion_browse))
    lines.extend(["", "### _companion-link._tcp Self Resolve", ""])
    lines.extend(render_resolve_summary(companion_resolve))
    lines.extend(["", "### _universalcontrol._tcp Browse", ""])
    lines.extend(render_browse_summary(universalcontrol_browse))

    lines.extend(["", "## Network Sockets", ""])
    lines.extend(["### rapportd", ""])
    lines.extend(render_lsof_summary(lsof_rapportd))
    lines.extend(["", "### UniversalControl", ""])
    lines.extend(render_lsof_summary(lsof_universalcontrol))

    lines.extend(["", "## UniversalControl Binary Strings", ""])
    lines.extend(
        [
            f"- Filtered string lines: {strings['total']}",
            f"- Hint categories: {format_counter(strings['hints'])}",
            "- Raw strings: not included",
        ]
    )

    lines.extend(["", "## Defaults", ""])
    lines.extend(
        [
            f"- Top-level key names: {format_set(defaults['keys'])}",
            f"- Top-level key count: {len(defaults['keys'])}",
            "- Values: not included",
        ]
    )

    lines.extend(["", "## Universal Control ByHost Preferences", ""])
    lines.extend(
        [
            f"- Preference files: {uc_byhost_preferences['files']}",
            f"- Preference byte sizes: {format_counter(uc_byhost_preferences['byte_sizes'])}",
            f"- Top-level key names: {format_set(uc_byhost_preferences['keys'])}",
            f"- Has configuration blob: {format_bool(uc_byhost_preferences['has_configuration'])}",
            f"- Has configuration ID: {format_bool(uc_byhost_preferences['has_configuration_id'])}",
            f"- Has shown control notification: {format_bool(uc_byhost_preferences['has_shown_control_notification'])}",
            "- Raw configuration blob and identifiers: not included",
        ]
    )

    lines.extend(["", "## Display Cache Shape", ""])
    lines.extend(
        [
            f"- WindowServer display config entries: {display_cache['windowserver_config_entries']}",
            f"- WindowServer current display entries: {display_cache['windowserver_current_info_entries']}",
            f"- WindowServer linked display flags: {format_counter(display_cache['link_flags'])}",
            f"- WindowServer nonzero-origin entries: {display_cache['nonzero_origin_entries']}",
            f"- Spaces monitor records: {display_cache['spaces_monitor_records']}",
            f"- Spaces collapsed display records: {display_cache['spaces_collapsed_records']}",
            "- Display UUIDs, names, and raw layout values: not included",
        ]
    )

    lines.extend(["", "## Recent Unified Logs", ""])
    lines.extend(
        [
            f"- Total captured lines: {log_count(logs, 'total')}",
            f"- UniversalControl lines: {log_count(logs, 'UniversalControl')}",
            f"- rapportd lines: {log_count(logs, 'rapportd')}",
            f"- Proximity keyword lines: {log_count(logs, 'proximity_keywords')}",
            f"- BLE keyword lines: {log_count(logs, 'ble_keywords')}",
            f"- CompanionLink keyword lines: {log_count(logs, 'companion_keywords')}",
            f"- P2P keyword lines: {log_count(logs, 'p2p_keywords')}",
            f"- Input keyword lines: {log_count(logs, 'input_keywords')}",
            f"- Error/fault keyword lines: {log_count(logs, 'error_keywords')}",
            f"- Rapport event IDs: {format_set(logs['event_ids'])}",
            f"- Rapport message IDs: {format_set(logs['message_ids'])}",
            "- Raw log lines: not included",
        ]
    )

    lines.extend(["", "## Continuity Health Logs", ""])
    lines.extend(
        [
            f"- Total captured lines: {health_logs['total']}",
            f"- UniversalControl lines: {health_logs['UniversalControl']}",
            f"- rapportd lines: {health_logs['rapportd']}",
            f"- sharingd lines: {health_logs['sharingd']}",
            f"- useractivityd lines: {health_logs['useractivityd']}",
            f"- Handoff keyword lines: {health_logs['handoff_keywords']}",
            f"- CompanionLink keyword lines: {health_logs['companion_keywords']}",
            f"- BLE/nearby keyword lines: {health_logs['nearby_ble_keywords']}",
            f"- Wi-Fi P2P/AWDL keyword lines: {health_logs['p2p_keywords']}",
            f"- Display/Sidecar keyword lines: {health_logs['display_keywords']}",
            f"- Preference/disabled keyword lines: {health_logs['preference_keywords']}",
            f"- Error/rejection keyword lines: {health_logs['error_keywords']}",
            "- Raw log lines: not included",
        ]
    )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- CompanionLink browse observed: {format_bool(bool(companion_browse))}",
            f"- CompanionLink self resolve observed: {format_bool(bool(companion_resolve))}",
            f"- Universal Control DNS-SD browse observed: {format_bool(bool(universalcontrol_browse))}",
            f"- rapportd network presence: {network_presence(lsof_rapportd)}",
            f"- UniversalControl network presence: {network_presence(lsof_universalcontrol)}",
            f"- Continuity transport health: {continuity_transport_health(continuity_health)}",
            f"- Universal Control preference cache: {preference_cache_signal(uc_byhost_preferences)}",
            f"- Display cache link-loss signal: {display_cache_signal(display_cache)}",
            f"- Native proximity/log signal: {native_log_signal(logs)}",
            f"- Link-loss health-log signal: {health_log_signal(health_logs)}",
            "- Notes:",
            "  - Fill this section manually after comparing against the local raw artifact.",
            "  - Do not paste raw hostnames, addresses, TXT values, Bluetooth IDs, hardware addresses, or unified-log lines.",
            "",
        ]
    )
    return "\n".join(lines)


def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_readme(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("Created: "):
            metadata["created"] = line.removeprefix("Created: ").strip()
    return metadata


def parse_sw_vers(text: str) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in {"ProductName", "ProductVersion", "BuildVersion"}:
            info[key] = value.strip()
    return info


def parse_uname_arch(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("$ ") or not line.strip():
            continue
        return line.split()[-1] if line.split() else "unknown"
    return "unknown"


def parse_plist_pairs(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    pattern = re.compile(r'^\s*"(?P<key>[^"]+)"\s+=>\s+"(?P<value>[^"]*)"')
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            pairs[match.group("key")] = match.group("value")
    return pairs


def parse_entitlement_keys(text: str) -> list[str]:
    keys: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[Key] "):
            key = stripped.removeprefix("[Key] ").strip()
            if key:
                keys.append(key)
    return sorted(set(keys))


def parse_launchctl(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    trigger_names: Counter[str] = Counter()
    event_streams: Counter[str] = Counter()
    service_types: Counter[str] = Counter()
    descriptor_types: Counter[str] = Counter()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("state = "):
            result["state"] = stripped.removeprefix("state = ").strip()
        elif stripped.startswith("runs = "):
            result["runs"] = stripped.removeprefix("runs = ").strip()
        elif stripped.startswith("path = "):
            result["path"] = stripped.removeprefix("path = ").strip()
        elif stripped.startswith("program = "):
            result["program"] = stripped.removeprefix("program = ").strip()
        elif stripped.startswith("com.apple.universalcontrol.") and stripped.endswith("=> {"):
            trigger_names[stripped.split()[0]] += 1
        elif "com.apple.rapport.matching" in stripped:
            event_streams["com.apple.rapport.matching"] += 1
        descriptor_match = re.search(r'"type"\s+=>\s+"([^"]+)"', stripped)
        if descriptor_match:
            descriptor_types[descriptor_match.group(1)] += 1
        service_match = re.search(r'"serviceType"\s+=>\s+"([^"]+)"', stripped)
        if service_match:
            service_types[service_match.group(1)] += 1
    result["triggers"] = format_counter(trigger_names)
    result["event_streams"] = format_counter(event_streams)
    result["service_types"] = format_counter(service_types)
    result["descriptor_types"] = format_counter(descriptor_types)
    return result


def format_launchd(value: dict[str, str]) -> str:
    if not value:
        return "missing"
    parts = [
        f"state={value.get('state', 'unknown')}",
        f"runs={value.get('runs', 'unknown')}",
    ]
    if value.get("path"):
        parts.append(f"path=`{value['path']}`")
    if value.get("program"):
        parts.append(f"program=`{value['program']}`")
    if value.get("triggers") and value["triggers"] != "none":
        parts.append(f"triggers={value['triggers']}")
    if value.get("event_streams") and value["event_streams"] != "none":
        parts.append(f"event_streams={value['event_streams']}")
    if value.get("service_types") and value["service_types"] != "none":
        parts.append(f"service_types={value['service_types']}")
    if value.get("descriptor_types") and value["descriptor_types"] != "none":
        parts.append(f"descriptor_types={value['descriptor_types']}")
    return " ".join(parts)


def summarize_processes(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        if line.startswith("$ ") or not line.strip():
            continue
        for process in NATIVE_PROCESSES:
            if process in line:
                counts[process] += 1
    return counts


def summarize_network_hardware(text: str) -> dict[str, object]:
    port_count = 0
    devices: set[str] = set()
    wifi_present = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Hardware Port: "):
            port_count += 1
            if "wi-fi" in stripped.lower() or "wifi" in stripped.lower():
                wifi_present = True
        elif stripped.startswith("Device: "):
            devices.add(stripped.removeprefix("Device: ").strip())
    return {"port_count": port_count, "devices": devices, "wifi_present": wifi_present}


def summarize_continuity_health(text: str) -> dict[str, object]:
    result: dict[str, object] = {
        "wifi_device": "unknown",
        "wifi_power": "unknown",
        "wifi_active": False,
        "awdl_present": False,
        "awdl_active": False,
        "firewall_global": "unknown",
        "firewall_block_all": "unknown",
        "firewall_stealth": "unknown",
    }
    section = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "--- awdl0 ---":
            section = "awdl0"
            continue
        if stripped == "--- en0 ---":
            section = "wifi"
            result["wifi_device"] = "en0"
            continue
        if stripped.startswith("--- wifi-device:") and stripped.endswith(" ---"):
            section = "wifi"
            result["wifi_device"] = stripped.removeprefix("--- wifi-device:").removesuffix(" ---")
            continue
        if stripped == "--- firewall ---":
            section = "firewall"
            continue
        if stripped.startswith("wifi_device="):
            result["wifi_device"] = stripped.split("=", 1)[-1].strip()
        if stripped.startswith("Wi-Fi Power"):
            result["wifi_power"] = stripped.split(":", 1)[-1].strip().lower()
        if stripped.startswith("awdl0:"):
            result["awdl_present"] = True
        if stripped == "status: active" and section == "awdl0":
            result["awdl_active"] = True
        if stripped == "status: active" and section == "wifi":
            result["wifi_active"] = True
        if section == "firewall":
            if "Firewall is" in stripped:
                result["firewall_global"] = firewall_state(stripped)
            elif "block all state" in stripped:
                result["firewall_block_all"] = firewall_state(stripped)
            elif "stealth mode" in stripped:
                result["firewall_stealth"] = firewall_state(stripped)
    return result


def firewall_state(text: str) -> str:
    lowered = text.lower()
    if "disabled" in lowered or "off" in lowered:
        return "disabled"
    if "enabled" in lowered or "on" in lowered:
        return "enabled"
    return "unknown"


def parse_browse(text: str) -> list[BrowseEvent]:
    events: list[BrowseEvent] = []
    pattern = re.compile(
        r"^\s*\d{1,2}:\d{2}:\d{2}\.\d+\s+"
        r"(?P<action>Add|Rmv)\s+"
        r"(?P<flags>\d+)\s+"
        r"(?P<interface>\d+)\s+"
        r"(?P<domain>\S+)\s+"
        r"(?P<service_type>\S+)\s+"
        r"(?P<instance>.+?)\s*$"
    )
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            events.append(BrowseEvent(**match.groupdict()))
    return events


def render_browse_summary(events: list[BrowseEvent]) -> list[str]:
    if not events:
        return ["- Events: none observed"]
    added = [event for event in events if event.action.lower() == "add"]
    removed = [event for event in events if event.action.lower() != "add"]
    return [
        f"- Add events: {len(added)}",
        f"- Remove events: {len(removed)}",
        f"- Service types: {format_set(event.service_type for event in events)}",
        f"- Instance lengths: {format_set(str(len(event.instance)) for event in added)}",
        f"- Interface count: {len({event.interface for event in events})}",
    ]


def parse_resolve(text: str) -> list[ResolveEvent]:
    events: list[ResolveEvent] = []
    current: ResolveEvent | None = None
    reached_pattern = re.compile(
        r"^\s*\d{1,2}:\d{2}:\d{2}\.\d+\s+"
        r"(?P<fullname>.+?)\s+can be reached at\s+"
        r"(?P<host>.+?):(?P<port>\d+)\s+"
        r"\(interface\s+(?P<interface>\d+)\)"
    )
    for line in text.splitlines():
        match = reached_pattern.match(line)
        if match:
            current = ResolveEvent(**match.groupdict(), txt=[])
            events.append(current)
            continue

        if current is not None and line.startswith(" "):
            current.txt.extend(parse_txt_line(line))
    return events


def parse_txt_line(line: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for token in line.strip().split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key:
            result.append((key, value))
    return result


def render_resolve_summary(events: list[ResolveEvent]) -> list[str]:
    if not events:
        return ["- Events: none observed"]
    txt_keys = sorted({key for event in events for key, _ in event.txt})
    txt_classes = Counter(
        f"{key}:{classify_txt_value(value)}" for event in events for key, value in event.txt
    )
    return [
        f"- Resolve events: {len(events)}",
        f"- Ports: {format_set(event.port for event in events)}",
        f"- Host lengths: {format_set(str(len(event.host)) for event in events)}",
        f"- Fullname lengths: {format_set(str(len(event.fullname)) for event in events)}",
        f"- Interface count: {len({event.interface for event in events})}",
        f"- TXT keys: {format_set(txt_keys)}",
        f"- TXT value classes: {format_counter(txt_classes)}",
    ]


def classify_txt_value(value: str) -> str:
    if re.fullmatch(r"0x[0-9a-fA-F]+", value):
        return f"hex-prefixed:{len(value)}"
    if re.fullmatch(r"[0-9a-fA-F]+", value):
        return f"hex:{len(value)}"
    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return "number"
    if re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", value):
        return "mac-like"
    return f"text:{len(value)}"


def summarize_lsof(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    listen_ports: Counter[str] = Counter()
    known_ports: Counter[str] = Counter()
    for line in text.splitlines():
        if not line or line.startswith("$ ") or line.startswith("COMMAND"):
            continue
        if not (line.startswith("rapportd") or line.startswith("UniversalControl")):
            continue
        counts["total"] += 1
        if line.startswith("rapportd"):
            counts["rapportd"] += 1
        if line.startswith("UniversalControl"):
            counts["UniversalControl"] += 1
        if " TCP " in line:
            counts["tcp"] += 1
        if " UDP " in line:
            counts["udp"] += 1
        state_match = re.search(r"\(([^)]+)\)\s*$", line)
        if state_match:
            counts[f"state:{state_match.group(1)}"] += 1
        listen_match = re.search(r"[:.](\d+)\s+\(LISTEN\)", line)
        if listen_match:
            listen_ports[listen_match.group(1)] += 1
        for port in ("3722", "5353"):
            if f":{port}" in line or f".{port}" in line:
                known_ports[port] += 1
    for key, value in listen_ports.items():
        counts[f"listen_port:{key}"] = value
    for key, value in known_ports.items():
        counts[f"known_port:{key}"] = value
    return counts


def render_lsof_summary(counts: Counter[str]) -> list[str]:
    if not counts["total"]:
        return ["- Entries: none observed"]
    state_counts = Counter({key.removeprefix("state:"): value for key, value in counts.items() if key.startswith("state:")})
    listen_ports = Counter(
        {key.removeprefix("listen_port:"): value for key, value in counts.items() if key.startswith("listen_port:")}
    )
    known_ports = Counter(
        {key.removeprefix("known_port:"): value for key, value in counts.items() if key.startswith("known_port:")}
    )
    return [
        f"- Entries: {counts['total']}",
        f"- rapportd entries: {counts['rapportd']}",
        f"- UniversalControl entries: {counts['UniversalControl']}",
        f"- TCP entries: {counts['tcp']}",
        f"- UDP entries: {counts['udp']}",
        f"- TCP states: {format_counter(state_counts)}",
        f"- TCP listener ports: {format_counter(listen_ports)}",
        f"- Known Apple ports seen: {format_counter(known_ports)}",
        "- Raw endpoints and dynamic addresses: not included",
    ]


def summarize_strings(text: str) -> dict[str, object]:
    hints: Counter[str] = Counter()
    total = 0
    for line in text.splitlines():
        if line.startswith("$ ") or not line.strip():
            continue
        total += 1
        for label, pattern in STRING_HINTS.items():
            if pattern.search(line):
                hints[label] += 1
    return {"total": total, "hints": hints}


def summarize_defaults(text: str) -> dict[str, object]:
    keys: set[str] = set()
    pattern = re.compile(r'^\s*"?([A-Za-z0-9_.-]+)"?\s+=')
    for line in text.splitlines():
        if line.startswith("$ "):
            continue
        match = pattern.match(line)
        if match:
            keys.add(match.group(1))
    return {"keys": keys}


def summarize_uc_byhost_preferences(text: str) -> dict[str, object]:
    files = 0
    byte_sizes: Counter[str] = Counter()
    keys: set[str] = set()
    has_configuration = False
    has_configuration_id = False
    has_shown_control_notification = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("plist="):
            files += 1
        elif stripped.startswith("bytes="):
            match = re.search(r"bytes=(\d+)", stripped)
            if match:
                byte_sizes[match.group(1)] += 1
        key_match = re.match(r'(\s*)"?([A-Za-z0-9_.-]+)"?\s+=>', line)
        if key_match and len(key_match.group(1)) <= 2:
            key = key_match.group(2)
            keys.add(key)
            if key == "Configuration":
                has_configuration = True
            elif key == "ConfigurationID":
                has_configuration_id = True
            elif key == "HasShownControlNotification":
                has_shown_control_notification = True
    return {
        "files": files,
        "byte_sizes": byte_sizes,
        "keys": keys,
        "has_configuration": has_configuration,
        "has_configuration_id": has_configuration_id,
        "has_shown_control_notification": has_shown_control_notification,
    }


def summarize_display_cache(text: str) -> dict[str, object]:
    counts: Counter[str] = Counter()
    link_flags: Counter[str] = Counter()
    for line in text.splitlines():
        stripped = line.strip()
        if '"ConfigVersion"' in stripped or stripped.startswith("ConfigVersion = "):
            counts["windowserver_config_entries"] += 1
        if '"CurrentInfo"' in stripped or stripped.startswith("CurrentInfo = "):
            counts["windowserver_current_info_entries"] += 1
        if '"IsLink" => true' in stripped or "IsLink = 1" in stripped:
            link_flags["true"] += 1
        if '"IsLink" => false' in stripped or "IsLink = 0" in stripped:
            link_flags["false"] += 1
        origin_match = re.match(r'"?Origin[XY]"?\s+(?:=>|=)\s+(-?\d+)', stripped)
        if origin_match and int(origin_match.group(1)) != 0:
            counts["nonzero_origin_entries"] += 1
        if '"Display Identifier"' in stripped or stripped.startswith('"Display Identifier" = '):
            counts["spaces_monitor_records"] += 1
        if "Collapsed Space" in stripped:
            counts["spaces_collapsed_records"] += 1
    return {
        "windowserver_config_entries": counts["windowserver_config_entries"],
        "windowserver_current_info_entries": counts["windowserver_current_info_entries"],
        "link_flags": link_flags,
        "nonzero_origin_entries": counts["nonzero_origin_entries"],
        "spaces_monitor_records": counts["spaces_monitor_records"],
        "spaces_collapsed_records": counts["spaces_collapsed_records"],
    }


def summarize_logs(text: str) -> dict[str, object]:
    counts: Counter[str] = Counter()
    event_ids: set[str] = set()
    message_ids: set[str] = set()
    patterns = {
        "proximity_keywords": re.compile(r"nearby|prox|ranging|region", re.I),
        "ble_keywords": re.compile(r"\bBLE\b|bluetooth|PairedBT", re.I),
        "companion_keywords": re.compile(r"companion|clink|CLink", re.I),
        "p2p_keywords": re.compile(r"p2p|WiFiP2P|AWDL", re.I),
        "input_keywords": re.compile(r"hid|keyboard|key|pointer|mouse|scroll|drag|pasteboard|event", re.I),
        "error_keywords": re.compile(r"reject|den(?:y|ied)|fail(?:ed|ure)?|(?<!no)error|fault|invalid|timeout", re.I),
    }
    for line in text.splitlines():
        if not line or line.startswith("$ "):
            continue
        counts["total"] += 1
        if "UniversalControl" in line:
            counts["UniversalControl"] += 1
        if "rapportd" in line:
            counts["rapportd"] += 1
        for key, pattern in patterns.items():
            if pattern.search(line):
                counts[key] += 1
        event_match = re.search(r"event ID '([^']+)'", line)
        if event_match:
            event_ids.add(event_match.group(1))
        message_match = re.search(r"msgID '([^']+)'", line)
        if message_match:
            message_ids.add(message_match.group(1))
    return {**counts, "event_ids": event_ids, "message_ids": message_ids}


def summarize_health_logs(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    patterns = {
        "handoff_keywords": re.compile(r"handoff|continuity|activity", re.I),
        "companion_keywords": re.compile(r"companion|clink|rapport", re.I),
        "nearby_ble_keywords": re.compile(r"nearby|BLE|bluetooth|rssi|paired", re.I),
        "p2p_keywords": re.compile(r"p2p|WiFiP2P|AWDL", re.I),
        "display_keywords": re.compile(r"display|sidecar|universal", re.I),
        "preference_keywords": re.compile(r"preference|prefs|disabled|enabled", re.I),
        "error_keywords": re.compile(r"reject|den(?:y|ied)|fail(?:ed|ure)?|(?<!no)error|fault|invalid|timeout", re.I),
    }
    for line in text.splitlines():
        if not line or line.startswith("$ "):
            continue
        counts["total"] += 1
        for process in ("UniversalControl", "rapportd", "sharingd", "useractivityd"):
            if process in line:
                counts[process] += 1
        for key, pattern in patterns.items():
            if pattern.search(line):
                counts[key] += 1
    return counts


def network_presence(counts: Counter[str]) -> str:
    if not counts["total"]:
        return "none observed"
    if counts["tcp"] or counts["udp"]:
        return "network sockets observed"
    return "process present without network sockets in artifact"


def continuity_transport_health(health: dict[str, object]) -> str:
    wifi_on = health.get("wifi_power") == "on"
    wifi_active = bool(health.get("wifi_active"))
    awdl_active = bool(health.get("awdl_active"))
    block_all = health.get("firewall_block_all") == "enabled"
    if wifi_on and wifi_active and awdl_active and not block_all:
        return "Wi-Fi interface and AWDL look available; firewall block-all is not enabled"
    missing: list[str] = []
    if not wifi_on:
        missing.append("Wi-Fi power")
    if not wifi_active:
        missing.append("Wi-Fi interface active status")
    if not awdl_active:
        missing.append("AWDL active status")
    if block_all:
        missing.append("firewall block-all disabled state")
    return "possible prerequisite issue: " + ", ".join(missing)


def preference_cache_signal(preferences: dict[str, object]) -> str:
    if not preferences["files"]:
        return "no Universal Control ByHost preference file found"
    if preferences["has_configuration"]:
        return "Universal Control ByHost configuration cache present"
    return "Universal Control preference file present without configuration blob"


def display_cache_signal(cache: dict[str, object]) -> str:
    collapsed = int(cache["spaces_collapsed_records"])
    nonzero_origins = int(cache["nonzero_origin_entries"])
    if collapsed or nonzero_origins:
        return "display cache contains collapsed or nonzero-origin records; inspect if Displays UI is stale"
    if int(cache["windowserver_current_info_entries"]):
        return "display cache present without obvious collapsed/nonzero-origin signal"
    return "display cache shape not observed"


def native_log_signal(logs: dict[str, object]) -> str:
    if log_count(logs, "UniversalControl") or log_count(logs, "rapportd"):
        if logs.get("event_ids") or logs.get("message_ids"):
            return "native process logs include redacted Rapport event/message IDs"
        return "native process logs present without parsed event/message IDs"
    return "no native process log lines counted"


def health_log_signal(logs: Counter[str]) -> str:
    if logs["UniversalControl"]:
        return "UniversalControl health-log lines present"
    if logs["rapportd"] or logs["sharingd"]:
        return "Rapport/Sharing continuity lines present without UniversalControl lines"
    return "no continuity health-log lines counted"


def log_count(logs: dict[str, object], key: str) -> int:
    return int(logs.get(key, 0))


def format_set(values) -> str:
    unique = sorted({str(value) for value in values if str(value)})
    if not unique:
        return "none"
    return ", ".join(f"`{value}`" for value in unique)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_code_or_unknown(value: object) -> str:
    text = str(value)
    if not text or text == "unknown":
        return "unknown"
    return f"`{text}`"


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
