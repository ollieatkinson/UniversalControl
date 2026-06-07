#!/usr/bin/env python3
"""Create a commit-safe summary from a macOS mDNS watcher artifact directory."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


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
        description="Summarize artifacts from scripts/mac/watch-mdns-service.sh without leaking identifiers."
    )
    parser.add_argument("artifact_dir", type=Path, help="Artifact directory under artifacts/")
    parser.add_argument(
        "--expected-instance",
        help="Optional expected instance name. The value is used only for yes/no matching and is not printed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown summary to this path instead of stdout.",
    )
    args = parser.parse_args()

    artifact_dir = args.artifact_dir
    if not artifact_dir.is_dir():
        parser.error(f"artifact directory not found: {artifact_dir}")

    summary = render_summary(artifact_dir, args.expected_instance)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def render_summary(artifact_dir: Path, expected_instance: str | None) -> str:
    metadata = parse_readme(read_file(artifact_dir / "README.txt"))
    browse_events = parse_browse(read_file(artifact_dir / "dns-sd-browse.txt"))
    resolve_events = parse_resolve(read_file(artifact_dir / "dns-sd-resolve.txt"))
    log_counts = summarize_logs(read_file(artifact_dir / "unified-log.txt"))
    launchd = {
        "ensemble_before": parse_launchctl(read_file(artifact_dir / "launchctl-ensemble-before.txt")),
        "ensemble_after": parse_launchctl(read_file(artifact_dir / "launchctl-ensemble-after.txt")),
        "rapportd_before": parse_launchctl(read_file(artifact_dir / "launchctl-rapportd-before.txt")),
        "rapportd_after": parse_launchctl(read_file(artifact_dir / "launchctl-rapportd-after.txt")),
    }

    lines = [
        "# Redacted macOS mDNS Watch Summary",
        "",
        "## Source",
        "",
        f"- Artifact: `{artifact_dir.name}`",
        f"- Created: {metadata.get('created', 'unknown')}",
        f"- Duration: {metadata.get('duration', 'unknown')}",
        f"- Service: `{metadata.get('service', 'unknown')}`",
        f"- Configured instance: {redact_string(metadata.get('instance', ''))}",
        "- Raw output: not included",
        "",
        "## DNS-SD Browse",
        "",
    ]

    if browse_events:
        seen_instances = [event.instance for event in browse_events if event.action.lower() == "add"]
        removed_instances = [event.instance for event in browse_events if event.action.lower() != "add"]
        lines.extend(
            [
                f"- Add events: {len(seen_instances)}",
                f"- Remove events: {len(removed_instances)}",
                f"- Service types: {format_set(event.service_type for event in browse_events)}",
                f"- Instance lengths: {format_set(str(len(instance)) for instance in seen_instances)}",
                f"- Interface count: {len({event.interface for event in browse_events})}",
            ]
        )
        if expected_instance is not None:
            lines.append(f"- Expected instance seen: {format_bool(expected_instance in seen_instances)}")
    else:
        seen_instances = []
        lines.append("- Events: none observed")
        if expected_instance is not None:
            lines.append("- Expected instance seen: no")

    lines.extend(["", "## DNS-SD Resolve", ""])
    if resolve_events:
        txt_keys = sorted({key for event in resolve_events for key, _ in event.txt})
        txt_classes = Counter(
            f"{key}:{classify_txt_value(value)}" for event in resolve_events for key, value in event.txt
        )
        lines.extend(
            [
                f"- Resolve events: {len(resolve_events)}",
                f"- Ports: {format_set(event.port for event in resolve_events)}",
                f"- Host lengths: {format_set(str(len(event.host)) for event in resolve_events)}",
                f"- Fullname lengths: {format_set(str(len(event.fullname)) for event in resolve_events)}",
                f"- Interface count: {len({event.interface for event in resolve_events})}",
                f"- TXT keys: {format_set(txt_keys)}",
                f"- TXT value classes: {format_counter(txt_classes)}",
            ]
        )
    else:
        lines.append("- Events: none observed or resolve was skipped")

    lines.extend(["", "## Unified Log", ""])
    lines.extend(
        [
            f"- Total captured lines: {log_counts['total']}",
            f"- UniversalControl lines: {log_counts['UniversalControl']}",
            f"- rapportd lines: {log_counts['rapportd']}",
            f"- mDNSResponder lines: {log_counts['mDNSResponder']}",
            f"- nearbyd lines: {log_counts['nearbyd']}",
            f"- wifip2pd lines: {log_counts['wifip2pd']}",
            f"- Candidate/matching keyword lines: {log_counts['candidate_keywords']}",
            f"- Error/rejection keyword lines: {log_counts['error_keywords']}",
            f"- UniversalControl/rapportd candidate keyword lines: {log_counts['native_candidate_keywords']}",
            f"- UniversalControl/rapportd error/rejection keyword lines: {log_counts['native_error_keywords']}",
            f"- Native stream keyword lines: {log_counts['native_stream_keywords']}",
            f"- Native target/input keyword lines: {log_counts['native_target_keywords']}",
            f"- Native sync/layout keyword lines: {log_counts['native_sync_layout_keywords']}",
            f"- Proximity/ranging keyword lines: {log_counts['proximity_keywords']}",
            f"- Native/proximity-process proximity keyword lines: {log_counts['native_proximity_keywords']}",
            f"- Wi-Fi peer-to-peer/AWDL keyword lines: {log_counts['p2p_transport_keywords']}",
            f"- Native/transport-process Wi-Fi P2P keyword lines: {log_counts['native_p2p_transport_keywords']}",
            "- Raw log lines: not included",
        ]
    )

    lines.extend(["", "## Launchd", ""])
    lines.extend(
        [
            f"- UniversalControl before: {format_launchd(launchd['ensemble_before'])}",
            f"- UniversalControl after: {format_launchd(launchd['ensemble_after'])}",
            f"- rapportd before: {format_launchd(launchd['rapportd_before'])}",
            f"- rapportd after: {format_launchd(launchd['rapportd_after'])}",
        ]
    )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- macOS browse saw expected Windows service: {browse_interpretation(seen_instances, expected_instance)}",
            f"- macOS resolve succeeded: {format_bool(bool(resolve_events))}",
            f"- Native Universal Control candidate reaction: {candidate_reaction(log_counts)}",
            f"- Proximity or Wi-Fi P2P side-channel signal: {side_channel_reaction(log_counts)}",
            "- Notes:",
            "  - Fill this section manually from the redacted counts and local raw artifacts.",
            "  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, or log lines.",
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
        elif line.startswith("Duration: "):
            metadata["duration"] = line.removeprefix("Duration: ").strip()
        elif line.startswith("Service: "):
            metadata["service"] = line.removeprefix("Service: ").strip()
        elif line.startswith("Instance: "):
            metadata["instance"] = line.removeprefix("Instance: ").strip()
    return metadata


def parse_browse(text: str) -> list[BrowseEvent]:
    events: list[BrowseEvent] = []
    pattern = re.compile(
        r"^\d{1,2}:\d{2}:\d{2}\.\d+\s+"
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


def parse_resolve(text: str) -> list[ResolveEvent]:
    events: list[ResolveEvent] = []
    current: ResolveEvent | None = None
    reached_pattern = re.compile(
        r"^\d{1,2}:\d{2}:\d{2}\.\d+\s+"
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

        if current and line.startswith(" "):
            for key, value in parse_txt_tokens(line.strip()):
                current.txt.append((key, value))
    return events


def parse_txt_tokens(line: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    for token in line.split():
        if "=" in token:
            key, value = token.split("=", 1)
            if key:
                tokens.append((key, value))
    return tokens


def summarize_logs(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    candidate_pattern = re.compile(r"candidate|matching|companion|_companion-link|clink|p2p", re.I)
    error_pattern = re.compile(r"reject|den(?:y|ied)|fail(?:ed|ure)?|(?<!no)error|invalid|refus", re.I)
    stream_pattern = re.compile(r"RPStreamServer|P2PStream|P2PDirectLink|Accept Stream|Prepare Stream", re.I)
    proximity_pattern = re.compile(
        r"nearby|proximity|ranging|NISession|NINearby|Bluetooth|\bBLE\b|\bUWB\b",
        re.I,
    )
    p2p_transport_pattern = re.compile(
        r"AWDL|WiFiP2P|wifip2p|peer[- ]to[- ]peer|P2PDirectLink|P2PStream",
        re.I,
    )
    target_pattern = re.compile(
        r"FocusMove|FocusReset|TargetBegin|TargetConnect|TargetReady|TargetEvent|"
        r"TargetReply|Target Reply|Keyboard Reports|Pointing Reports|HID accumulation",
        re.I,
    )
    sync_layout_pattern = re.compile(
        r"Initial Sync|Create Message|Send Message|Receive Message|Received Message|"
        r"Remote Display Layout|Remote Source Device|Remote Connected Devices|"
        r"Remote Synced Devices|Reset Remote|Connected Devices Clock",
        re.I,
    )
    for line in text.splitlines():
        if not line or line.startswith("$ ") or line.startswith("Filtering ") or line.startswith("Timestamp "):
            continue
        counts["total"] += 1
        is_native_process = "UniversalControl" in line or "rapportd" in line
        is_proximity_process = is_native_process or "nearbyd" in line
        is_p2p_transport_process = is_native_process or "wifip2pd" in line
        for process in (
            "UniversalControl",
            "rapportd",
            "mDNSResponder",
            "nearbyd",
            "wifip2pd",
        ):
            if process in line:
                counts[process] += 1
        if candidate_pattern.search(line):
            counts["candidate_keywords"] += 1
            if is_native_process:
                counts["native_candidate_keywords"] += 1
        if error_pattern.search(line):
            counts["error_keywords"] += 1
            if is_native_process:
                counts["native_error_keywords"] += 1
        if stream_pattern.search(line) and is_native_process:
            counts["native_stream_keywords"] += 1
        if target_pattern.search(line) and is_native_process:
            counts["native_target_keywords"] += 1
        if sync_layout_pattern.search(line) and is_native_process:
            counts["native_sync_layout_keywords"] += 1
        if proximity_pattern.search(line):
            counts["proximity_keywords"] += 1
            if is_proximity_process:
                counts["native_proximity_keywords"] += 1
        if p2p_transport_pattern.search(line):
            counts["p2p_transport_keywords"] += 1
            if is_p2p_transport_process:
                counts["native_p2p_transport_keywords"] += 1
    return counts


def parse_launchctl(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("state = "):
            result["state"] = stripped.removeprefix("state = ").strip()
        elif stripped.startswith("runs = "):
            result["runs"] = stripped.removeprefix("runs = ").strip()
    return result


def browse_interpretation(seen_instances: list[str], expected_instance: str | None) -> str:
    if expected_instance is not None:
        return format_bool(expected_instance in seen_instances)
    if seen_instances:
        return "yes"
    return "no"


def candidate_reaction(log_counts: Counter[str]) -> str:
    deeper_signal = (
        log_counts["native_stream_keywords"]
        or log_counts["native_target_keywords"]
        or log_counts["native_sync_layout_keywords"]
    )
    if deeper_signal:
        return "stream, target, or sync/layout signal in redacted counts; inspect raw local artifacts"
    if log_counts["native_candidate_keywords"] or log_counts["native_error_keywords"]:
        return "possible signal in redacted counts; inspect raw local artifacts"
    if log_counts["UniversalControl"] or log_counts["rapportd"]:
        return "process logs present, no candidate/rejection keywords counted"
    return "no UniversalControl or rapportd lines counted"


def side_channel_reaction(log_counts: Counter[str]) -> str:
    if log_counts["native_proximity_keywords"] or log_counts["native_p2p_transport_keywords"]:
        return "possible proximity or Wi-Fi peer-to-peer signal in redacted counts"
    if log_counts["proximity_keywords"] or log_counts["p2p_transport_keywords"]:
        return "only generic proximity or Wi-Fi peer-to-peer keywords counted"
    if log_counts["nearbyd"] or log_counts["wifip2pd"]:
        return "nearbyd or wifip2pd logs present without counted protocol keywords"
    return "no nearbyd or wifip2pd lines counted"


def format_launchd(value: dict[str, str]) -> str:
    if not value:
        return "missing"
    return f"state={value.get('state', 'unknown')} runs={value.get('runs', 'unknown')}"


def redact_string(value: str) -> str:
    return f"<redacted len={len(value)}>"


def classify_txt_value(value: str) -> str:
    if value == "":
        return "empty"
    text = value.strip()
    if not text:
        return "whitespace"
    if text.lower() in {"true", "false"}:
        return "boolean"
    if text.isdigit():
        return "integer"
    if re.fullmatch(r"0x[0-9A-Fa-f]+", text):
        return "hex-prefixed"
    if re.fullmatch(r"\d+(?:\.\d+)+", text):
        return "version"
    if re.fullmatch(r"[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}", text) or re.fullmatch(
        r"[0-9A-Fa-f]{2}(?:-[0-9A-Fa-f]{2}){5}", text
    ):
        return "mac-like"
    if re.fullmatch(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}", text):
        return "uuid-like"
    if len(text) >= 2 and len(text) % 2 == 0 and re.fullmatch(r"[0-9A-Fa-f]+", text):
        return "hex"
    if all((character.isprintable() and character.isascii()) for character in text):
        return "text"
    return "utf8"


def format_set(values) -> str:
    unique = sorted({str(value) for value in values if str(value)})
    if not unique:
        return "none"
    return ", ".join(f"`{value}`" for value in unique)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
