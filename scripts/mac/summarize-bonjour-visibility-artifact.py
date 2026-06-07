#!/usr/bin/env python3
"""Create a commit-safe summary from a macOS Bonjour visibility artifact."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass, field
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
class TcpConnection:
    index: str
    peer_class: str
    outcome: str = "unknown"
    first_read_bytes: int | None = None
    read_count: int | None = None
    total_bytes: int | None = None
    duration_ms: int | None = None
    read_limit_reached: bool | None = None
    closed_by_peer: bool | None = None
    read_events: list[tuple[int, int, int]] = field(default_factory=list)
    framing_events: list[tuple[int, dict[str, str]]] = field(default_factory=list)


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
    observer_text = read_file(artifact_dir / "tcp-observer.txt")
    observer = parse_tcp_observer(observer_text)
    connections = parse_tcp_connections(observer_text)
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

    lines.extend(render_tcp_observer_section(metadata, observer, connections))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Mac Bonjour advertisement active: {format_bool(registration_active(register_text))}",
            f"- Mac browse saw its own project-owned advertisement: {format_bool(bool(local_adds))}",
            f"- Mac browse saw expected Windows advertisement: {remote_visibility(remote_adds, expected_remote_instance)}",
            f"- Windows reached controlled Mac TCP port: {tcp_visibility(metadata, connections)}",
            "- Notes:",
            "  - Non-local instance counts can include the Mac's native Apple CompanionLink service.",
            "  - TCP observer connections prove reachability to the controlled probe only; they are not Rapport admission.",
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
        elif line.startswith("Observe TCP: "):
            metadata["observe_tcp"] = line.removeprefix("Observe TCP: ").strip()
        elif line.startswith("Observe framing: "):
            metadata["observe_framing"] = line.removeprefix("Observe framing: ").strip()
        elif line.startswith("Observer bind address: "):
            metadata["observer_bind_address"] = line.removeprefix(
                "Observer bind address: "
            ).strip()
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


def parse_tcp_observer(text: str) -> dict[str, str | bool]:
    result: dict[str, str | bool] = {
        "enabled": False,
        "bind_class": "none",
        "port": "unknown",
        "duration": "unknown",
        "framing_probe": False,
        "accepted_summary": "missing",
        "output_present": bool(text.strip()),
    }
    listen_pattern = re.compile(
        r"^TCP observer listening bind_class=(?P<bind_class>\S+) port=(?P<port>\d+) duration=(?P<duration>\S+)$"
    )
    summary_pattern = re.compile(r"^TCP observer summary: accepted_connections=(?P<count>\d+)$")
    for line in text.splitlines():
        stripped = line.strip()
        listen = listen_pattern.match(stripped)
        if listen:
            result["enabled"] = True
            result["bind_class"] = listen.group("bind_class")
            result["port"] = listen.group("port")
            result["duration"] = listen.group("duration")
            continue
        if stripped == "TCP observer framing probe enabled: yes":
            result["framing_probe"] = True
            continue
        summary = summary_pattern.match(stripped)
        if summary:
            result["accepted_summary"] = summary.group("count")
    return result


def parse_tcp_connections(text: str) -> list[TcpConnection]:
    connections: dict[str, TcpConnection] = {}
    accepted_pattern = re.compile(
        r"^TCP observer accepted connection #(?P<index>\d+) peer_class=(?P<peer_class>\S+)$"
    )
    first_read_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) first_read_elapsed_ms=(?P<elapsed>\d+) first_read_bytes=(?P<bytes>\d+)$"
    )
    read_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) read #(?P<read_index>\d+) elapsed_ms=(?P<elapsed>\d+) bytes=(?P<bytes>\d+)$"
    )
    framing_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) read #(?P<read_index>\d+) framing (?P<shape>.+)$"
    )
    summary_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) summary reads=(?P<reads>\d+) total_bytes=(?P<total_bytes>\d+) duration_ms=(?P<duration_ms>\d+) read_limit_reached=(?P<read_limit_reached>true|false) closed_by_peer=(?P<closed_by_peer>true|false)$"
    )
    closed_pattern = re.compile(r"^TCP observer connection #(?P<index>\d+) closed without data$")
    timeout_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) produced no data before timeout$"
    )
    read_error_pattern = re.compile(r"^TCP observer read error on connection #(?P<index>\d+):")

    for line in text.splitlines():
        stripped = line.strip()
        accepted = accepted_pattern.match(stripped)
        if accepted:
            index = accepted.group("index")
            connections[index] = TcpConnection(
                index=index,
                peer_class=accepted.group("peer_class"),
            )
            continue

        first_read = first_read_pattern.match(stripped)
        if first_read:
            connection = connections.setdefault(
                first_read.group("index"),
                TcpConnection(index=first_read.group("index"), peer_class="unknown"),
            )
            connection.outcome = "first_read"
            connection.first_read_bytes = int(first_read.group("bytes"))
            connection.read_events.append(
                (1, int(first_read.group("elapsed")), int(first_read.group("bytes")))
            )
            continue

        read = read_pattern.match(stripped)
        if read:
            connection = connections.setdefault(
                read.group("index"),
                TcpConnection(index=read.group("index"), peer_class="unknown"),
            )
            connection.read_events.append(
                (
                    int(read.group("read_index")),
                    int(read.group("elapsed")),
                    int(read.group("bytes")),
                )
            )
            continue

        framing = framing_pattern.match(stripped)
        if framing:
            connection = connections.setdefault(
                framing.group("index"),
                TcpConnection(index=framing.group("index"), peer_class="unknown"),
            )
            connection.framing_events.append(
                (int(framing.group("read_index")), parse_shape(framing.group("shape")))
            )
            continue

        summary = summary_pattern.match(stripped)
        if summary:
            connection = connections.setdefault(
                summary.group("index"),
                TcpConnection(index=summary.group("index"), peer_class="unknown"),
            )
            connection.read_count = int(summary.group("reads"))
            connection.total_bytes = int(summary.group("total_bytes"))
            connection.duration_ms = int(summary.group("duration_ms"))
            connection.read_limit_reached = parse_bool(summary.group("read_limit_reached"))
            connection.closed_by_peer = parse_bool(summary.group("closed_by_peer"))
            continue

        closed = closed_pattern.match(stripped)
        if closed:
            connection = connections.setdefault(
                closed.group("index"),
                TcpConnection(index=closed.group("index"), peer_class="unknown"),
            )
            connection.outcome = "closed_without_data"
            continue

        timeout = timeout_pattern.match(stripped)
        if timeout:
            connection = connections.setdefault(
                timeout.group("index"),
                TcpConnection(index=timeout.group("index"), peer_class="unknown"),
            )
            connection.outcome = "no_data_before_timeout"
            continue

        read_error = read_error_pattern.match(stripped)
        if read_error:
            connection = connections.setdefault(
                read_error.group("index"),
                TcpConnection(index=read_error.group("index"), peer_class="unknown"),
            )
            connection.outcome = "read_error"

    return [connections[key] for key in sorted(connections, key=int)]


def parse_shape(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in value.split():
        key, separator, val = item.partition("=")
        if separator:
            result[key] = val
    return result


def parse_bool(value: str) -> bool:
    return value == "true"


def render_tcp_observer_section(
    metadata: dict[str, str],
    observer: dict[str, str | bool],
    connections: list[TcpConnection],
) -> list[str]:
    read_lengths = [event[2] for connection in connections for event in connection.read_events]
    return [
        "",
        "## TCP Observer",
        "",
        f"- Observer requested: {format_bool(metadata.get('observe_tcp') == '1')}",
        f"- Observer output present: {format_bool(bool(observer['output_present']))}",
        f"- Observer enabled: {format_bool(bool(observer['enabled']))}",
        f"- Observer bind address class: {observer['bind_class']}",
        f"- Observer port: {observer['port']}",
        f"- Observer duration: {observer['duration']}",
        f"- Framing probe enabled: {format_bool(bool(observer['framing_probe']))}",
        f"- Accepted connection summary: {observer['accepted_summary']}",
        f"- Accepted connection lines: {len(connections)}",
        f"- Redacted peer classes: {format_counter(Counter(connection.peer_class for connection in connections))}",
        f"- Connection outcomes: {format_counter(Counter(connection.outcome for connection in connections))}",
        f"- First-read byte counts: {format_set(str(connection.first_read_bytes) for connection in connections if connection.first_read_bytes is not None)}",
        f"- Per-connection read counts: {format_set(str(connection.read_count) for connection in connections if connection.read_count is not None)}",
        f"- Per-connection total byte counts: {format_set(str(connection.total_bytes) for connection in connections if connection.total_bytes is not None)}",
        f"- Per-connection duration ms: {format_set(str(connection.duration_ms) for connection in connections if connection.duration_ms is not None)}",
        f"- Read limit reached: {format_bool(any(connection.read_limit_reached for connection in connections))}",
        f"- Closed by peer after data: {format_bool(any(connection.closed_by_peer for connection in connections))}",
        f"- Read byte counts: {format_counter(Counter(str(length) for length in read_lengths))}",
        f"- Read byte sequences: {format_read_sequences(connections)}",
        f"- Inter-read gap buckets: {format_counter(inter_read_gap_buckets(connections))}",
        f"- Framing first-byte classes: {format_counter(framing_counter(connections, 'first_byte_class'))}",
        f"- Framing entropy buckets: {format_counter(framing_counter(connections, 'entropy_bucket'))}",
        f"- Framing byte-diversity buckets: {format_counter(framing_counter(connections, 'byte_diversity_bucket'))}",
        f"- Framing length-prefix candidates: {format_counter(framing_length_prefix_counter(connections))}",
        f"- Framing TLS record-like reads: {format_counter(framing_counter(connections, 'tls_record_like'))}",
        f"- Framing TLS record length matches: {format_counter(framing_counter(connections, 'tls_record_len_match'))}",
        f"- Framing shape samples: {format_framing_samples(connections)}",
    ]


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


def tcp_visibility(metadata: dict[str, str], connections: list[TcpConnection]) -> str:
    if metadata.get("observe_tcp") != "1":
        return "not enabled"
    return format_bool(bool(connections))


def redact_string(value: str) -> str:
    return f"<redacted len={len(value)}>"


def format_set(values) -> str:
    unique = sorted({str(value) for value in values if str(value)})
    if not unique:
        return "none"
    return ", ".join(f"`{value}`" for value in unique)


def format_read_sequences(connections: list[TcpConnection]) -> str:
    sequences = Counter(
        ",".join(str(event[2]) for event in connection.read_events) or "none"
        for connection in connections
    )
    return format_counter(sequences)


def inter_read_gap_buckets(connections: list[TcpConnection]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for connection in connections:
        events = sorted(connection.read_events)
        for before, after in zip(events, events[1:]):
            counter[duration_bucket(max(0, after[1] - before[1]))] += 1
    return counter


def duration_bucket(ms: int) -> str:
    if ms == 0:
        return "0ms"
    if ms <= 10:
        return "1-10ms"
    if ms <= 50:
        return "11-50ms"
    if ms <= 250:
        return "51-250ms"
    if ms <= 1000:
        return "251-1000ms"
    return ">1000ms"


def framing_counter(connections: list[TcpConnection], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for connection in connections:
        for _, shape in connection.framing_events:
            value = shape.get(key)
            if value:
                counter[value] += 1
    return counter


def framing_length_prefix_counter(connections: list[TcpConnection]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for connection in connections:
        for _, shape in connection.framing_events:
            candidates = shape.get("length_prefix_candidates", "none")
            for candidate in candidates.split("|"):
                counter[candidate or "none"] += 1
    return counter


def format_framing_samples(connections: list[TcpConnection]) -> str:
    samples = []
    for connection in connections:
        for read_index, shape in connection.framing_events[:3]:
            samples.append(
                "read{read_index}:first={first}:entropy={entropy}:tls={tls}".format(
                    read_index=read_index,
                    first=shape.get("first_byte_class", "unknown"),
                    entropy=shape.get("entropy_bucket", "unknown"),
                    tls=shape.get("tls_record_like", "unknown"),
                )
            )
    if not samples:
        return "none"
    return ", ".join(f"`{sample}`" for sample in samples[:6])


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
