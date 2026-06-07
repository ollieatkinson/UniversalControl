#!/usr/bin/env python3
"""Create a commit-safe summary from a macOS Bonjour visibility artifact."""

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


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize artifacts from scripts/mac/capture-bonjour-visibility.sh "
            "without leaking Bonjour instance names or TXT values."
        )
    )
    parser.add_argument("artifact_dir", type=Path, help="Artifact directory under artifacts/")
    parser.add_argument(
        "--expected-remote-instance",
        help="Optional remote instance name. Used only for yes/no matching and not printed.",
    )
    parser.add_argument("--output", type=Path, help="Write Markdown summary to this path.")
    args = parser.parse_args()

    if not args.artifact_dir.is_dir():
        parser.error(f"artifact directory not found: {args.artifact_dir}")

    summary = render_summary(args.artifact_dir, args.expected_remote_instance)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def render_summary(artifact_dir: Path, expected_remote_instance: str | None) -> str:
    metadata = parse_readme(read_file(artifact_dir / "README.txt"))
    register_text = read_file(artifact_dir / "dns-sd-register.txt")
    browse_events = parse_browse(read_file(artifact_dir / "dns-sd-browse.txt"))
    local_instance = metadata.get("local_instance", "")

    add_events = [event for event in browse_events if event.action == "Add"]
    remove_events = [event for event in browse_events if event.action == "Rmv"]
    local_adds = [event for event in add_events if event.instance == local_instance]
    remote_adds = [
        event
        for event in add_events
        if expected_remote_instance is not None and event.instance == expected_remote_instance
    ]
    other_adds = [
        event
        for event in add_events
        if event.instance != local_instance and event.instance != expected_remote_instance
    ]

    lines = [
        "# Redacted macOS Bonjour Visibility Summary",
        "",
        "## Source",
        "",
        f"- Artifact: `{artifact_dir.name}`",
        f"- Created: {metadata.get('created', 'unknown')}",
        f"- Duration: {metadata.get('duration', 'unknown')}",
        f"- Service: `{metadata.get('service', 'unknown')}`",
        f"- Local advertised instance: {redact_string(local_instance)}",
        f"- Advertised port: {metadata.get('port', 'unknown')}",
        f"- Advertised TXT count: {metadata.get('txt_count', 'unknown')}",
        "- Raw output: not included",
        "",
        "## Registration",
        "",
        f"- Registration active: {format_bool(registration_active(register_text))}",
        f"- Registration collision/error lines: {registration_error_count(register_text)}",
        "",
        "## Browse",
        "",
        f"- Add events: {len(add_events)}",
        f"- Remove events: {len(remove_events)}",
        f"- Service types: {format_set(event.service_type for event in browse_events)}",
        f"- Interface count: {len({event.interface for event in browse_events})}",
        f"- Local advertised instance add events: {len(local_adds)}",
        f"- Non-local instance add events: {len(other_adds)}",
        f"- Non-local instance length buckets: {format_counter(length_buckets(event.instance for event in other_adds))}",
    ]
    if expected_remote_instance is not None:
        lines.append(f"- Expected remote instance seen: {format_bool(bool(remote_adds))}")
        lines.append(f"- Expected remote instance add events: {len(remote_adds)}")
    else:
        lines.append("- Expected remote instance seen: not configured")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Mac Bonjour advertisement active: {format_bool(registration_active(register_text))}",
            f"- Mac browse saw its own project-owned advertisement: {format_bool(bool(local_adds))}",
            f"- Mac browse saw expected Windows advertisement: {remote_visibility(remote_adds, expected_remote_instance)}",
            "- Notes:",
            "  - Non-local instance counts can include the Mac's native Apple CompanionLink service.",
            "  - Treat this as LAN/mDNS visibility evidence only, not Universal Control admission.",
            "  - Do not paste raw instance names, hostnames, addresses, TXT values, or interface identifiers.",
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
        elif line.startswith("Local instance: "):
            metadata["local_instance"] = line.removeprefix("Local instance: ").strip()
        elif line.startswith("Port: "):
            metadata["port"] = line.removeprefix("Port: ").strip()
        elif line.startswith("TXT count: "):
            metadata["txt_count"] = line.removeprefix("TXT count: ").strip()
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


def registration_active(text: str) -> bool:
    return "Name now registered and active" in text


def registration_error_count(text: str) -> int:
    pattern = re.compile(r"name conflict|error|fail|denied|refused|collision", re.I)
    return sum(1 for line in text.splitlines() if pattern.search(line))


def length_buckets(values) -> Counter[str]:
    counter: Counter[str] = Counter()
    for value in values:
        length = len(str(value))
        if length <= 8:
            counter["1-8"] += 1
        elif length <= 16:
            counter["9-16"] += 1
        elif length <= 32:
            counter["17-32"] += 1
        else:
            counter[">32"] += 1
    return counter


def remote_visibility(remote_adds: list[BrowseEvent], expected_remote_instance: str | None) -> str:
    if expected_remote_instance is None:
        return "not configured"
    return format_bool(bool(remote_adds))


def redact_string(value: str) -> str:
    return f"<redacted len={len(value)}>"


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
