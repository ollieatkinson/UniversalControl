#!/usr/bin/env python3
"""Create a commit-safe summary from Windows native-admission probe output."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ObserverConnection:
    index: str
    peer: str
    outcome: str = "unknown"
    first_read_bytes: int | None = None
    first_read_hex_len: int | None = None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize Windows AnyKBFlow native-admission stdout without leaking addresses."
    )
    parser.add_argument("transcript", type=Path, help="Captured Windows command output")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown summary to this path instead of stdout.",
    )
    args = parser.parse_args()

    text = args.transcript.read_text(encoding="utf-8", errors="replace")
    summary = render_summary(args.transcript, text)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def render_summary(path: Path, text: str) -> str:
    advertising = parse_advertising(text)
    observer = parse_observer(text)
    connections = parse_connections(text)
    cargo = summarize_cargo(text)
    errors = summarize_errors(text)

    lines = [
        "# Redacted Windows Native Admission Output Summary",
        "",
        "## Source",
        "",
        f"- Transcript file: `{path}`",
        "- Raw output: not included",
        "",
        "## Command Result",
        "",
        f"- Cargo finished lines: {cargo['finished']}",
        f"- AnyKBFlow command executed: {format_bool(cargo['ran_anykbflow'])}",
        f"- Error lines: {errors['error_lines']}",
        f"- Observer bind errors: {errors['observer_bind_errors']}",
        "",
        "## Advertisement",
        "",
        f"- Advertised service: `{advertising.get('service', 'unknown')}`",
        f"- Advertised port: {advertising.get('port', 'unknown')}",
        f"- Advertised host length: {advertising.get('host_len', 'unknown')}",
        f"- Advertise duration: {advertising.get('duration', 'unknown')}",
        "",
        "## TCP Observer",
        "",
        f"- Observer enabled: {format_bool(observer['enabled'])}",
        f"- Observer bind address class: {observer['bind_class']}",
        f"- Observer port: {observer['port']}",
        f"- Observer duration: {observer['duration']}",
        f"- Accepted connection summary: {observer['accepted_summary']}",
        f"- Accepted connection lines: {len(connections)}",
        f"- Unique redacted peer count: {len({connection.peer for connection in connections})}",
        f"- Connection outcomes: {format_counter(Counter(connection.outcome for connection in connections))}",
        f"- First-read byte counts: {format_set(str(connection.first_read_bytes) for connection in connections if connection.first_read_bytes is not None)}",
        f"- First-read hex lengths: {format_set(str(connection.first_read_hex_len) for connection in connections if connection.first_read_hex_len is not None)}",
        "",
        "## Interpretation",
        "",
        f"- macOS attempted advertised TCP port: {format_bool(bool(connections))}",
        "- Notes:",
        "  - Inspect the raw transcript locally before deleting it.",
        "  - Do not commit raw peer addresses, hostnames, or first-read hex payloads.",
        "",
    ]
    return "\n".join(lines)


def parse_advertising(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(
        r"^Advertising (?P<fullname>.+?) at (?P<host>.+?):(?P<port>\d+) for (?P<duration>\d+)s$"
    )
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        fullname = match.group("fullname")
        result["service"] = service_from_fullname(fullname)
        result["host_len"] = str(len(match.group("host")))
        result["port"] = match.group("port")
        result["duration"] = f"{match.group('duration')}s"
    return result


def service_from_fullname(fullname: str) -> str:
    parts = fullname.split(".")
    for index, part in enumerate(parts):
        if part.startswith("_") and index + 1 < len(parts) and parts[index + 1].startswith("_"):
            return ".".join(parts[index:])
    return "unknown"


def parse_observer(text: str) -> dict[str, str | bool]:
    result: dict[str, str | bool] = {
        "enabled": False,
        "bind_class": "none",
        "port": "unknown",
        "duration": "unknown",
        "accepted_summary": "missing",
    }
    listen_pattern = re.compile(
        r"^TCP observer listening on (?P<addr>.+?):(?P<port>\d+) for (?P<duration>\d+)s$"
    )
    summary_pattern = re.compile(r"^TCP observer summary: accepted_connections=(?P<count>\d+)$")
    for line in text.splitlines():
        stripped = line.strip()
        listen = listen_pattern.match(stripped)
        if listen:
            result["enabled"] = True
            result["bind_class"] = classify_bind_addr(listen.group("addr"))
            result["port"] = listen.group("port")
            result["duration"] = f"{listen.group('duration')}s"
            continue
        summary = summary_pattern.match(stripped)
        if summary:
            result["accepted_summary"] = summary.group("count")
    return result


def parse_connections(text: str) -> list[ObserverConnection]:
    connections: dict[str, ObserverConnection] = {}
    accepted_pattern = re.compile(
        r"^TCP observer accepted connection #(?P<index>\d+) from (?P<peer>.+)$"
    )
    first_read_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) first_read_bytes=(?P<bytes>\d+) first_read_hex=(?P<hex>[0-9a-fA-F]*)$"
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
            connections[index] = ObserverConnection(
                index=index,
                peer=redact_peer(accepted.group("peer")),
            )
            continue

        first_read = first_read_pattern.match(stripped)
        if first_read:
            connection = connections.setdefault(
                first_read.group("index"),
                ObserverConnection(index=first_read.group("index"), peer="<unknown>"),
            )
            connection.outcome = "first_read"
            connection.first_read_bytes = int(first_read.group("bytes"))
            connection.first_read_hex_len = len(first_read.group("hex"))
            continue

        for pattern, outcome in (
            (closed_pattern, "closed_without_data"),
            (timeout_pattern, "read_timeout"),
            (read_error_pattern, "read_error"),
        ):
            match = pattern.match(stripped)
            if match:
                connection = connections.setdefault(
                    match.group("index"),
                    ObserverConnection(index=match.group("index"), peer="<unknown>"),
                )
                connection.outcome = outcome
                break

    return [connections[index] for index in sorted(connections, key=int)]


def summarize_cargo(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        if "Finished `" in line:
            counts["finished"] += 1
        if "Running `" in line and "anykbflow" in line:
            counts["ran_anykbflow"] = 1
    return counts


def summarize_errors(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Error:") or " error" in stripped.lower():
            counts["error_lines"] += 1
        if "failed to bind TCP observer" in stripped:
            counts["observer_bind_errors"] += 1
    return counts


def redact_peer(value: str) -> str:
    if value.startswith("["):
        return "<redacted ipv6 peer>"
    host, separator, port = value.rpartition(":")
    if separator and port.isdigit():
        return f"<redacted {classify_host(host)} peer port_class={classify_port(port)}>"
    return f"<redacted {classify_host(value)} peer>"


def classify_bind_addr(value: str) -> str:
    if value in {"0.0.0.0", "[::]", "::"}:
        return "unspecified"
    if value.startswith("127.") or value == "::1" or value == "[::1]":
        return "loopback"
    if value.startswith("[") or ":" in value:
        return "ipv6"
    return "ipv4"


def classify_host(value: str) -> str:
    if value.startswith("[") or ":" in value:
        return "ipv6"
    if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", value):
        return "ipv4"
    return "hostname"


def classify_port(value: str) -> str:
    port = int(value)
    if port < 1024:
        return "well_known"
    if port < 49152:
        return "registered"
    return "dynamic"


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_set(values) -> str:
    unique = sorted({str(value) for value in values if str(value)})
    if not unique:
        return "none"
    return ", ".join(f"`{value}`" for value in unique)


def format_bool(value) -> str:
    return "yes" if bool(value) else "no"


if __name__ == "__main__":
    raise SystemExit(main())
