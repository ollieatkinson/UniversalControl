#!/usr/bin/env python3
"""Create a commit-safe summary from Windows native-admission probe output."""

from __future__ import annotations

import argparse
import ipaddress
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


APPLE_AWDL_SMALL_LENGTHS = {"55", "82", "93", "97", "122", "126", "140", "174"}
APPLE_AWDL_LARGE_LENGTHS = {"621", "1428"}


@dataclass
class ObserverConnection:
    index: str
    peer: str
    outcome: str = "unknown"
    first_read_bytes: int | None = None
    first_read_hex_len: int | None = None
    read_count: int | None = None
    total_bytes: int | None = None
    duration_ms: int | None = None
    read_limit_reached: bool | None = None
    closed_by_peer: bool | None = None
    read_hex_lens: list[int] | None = None
    read_events: list[tuple[int, int, int]] = field(default_factory=list)
    framing_events: list[tuple[int, dict[str, str]]] = field(default_factory=list)


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
    read_lengths = all_read_lengths(connections)
    read_gap_buckets = all_read_gap_buckets(connections)
    awdl_hits = apple_awdl_length_hits(read_lengths)

    lines = [
        "# Redacted Windows Native Admission Output Summary",
        "",
        "## Source",
        "",
        f"- Transcript file: `{display_path(path)}`",
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
        f"- Framing probe enabled: {format_bool(observer['framing_probe'])}",
        f"- Accepted connection summary: {observer['accepted_summary']}",
        f"- Accepted connection lines: {len(connections)}",
        f"- Unique redacted peer count: {len({connection.peer for connection in connections})}",
        f"- Redacted peer classes: {format_counter(Counter(connection.peer for connection in connections))}",
        f"- Connection outcomes: {format_counter(Counter(connection.outcome for connection in connections))}",
        f"- First-read byte counts: {format_set(str(connection.first_read_bytes) for connection in connections if connection.first_read_bytes is not None)}",
        f"- First-read hex lengths: {format_set(str(connection.first_read_hex_len) for connection in connections if connection.first_read_hex_len is not None)}",
        f"- Per-connection read counts: {format_set(str(connection.read_count) for connection in connections if connection.read_count is not None)}",
        f"- Per-connection total byte counts: {format_set(str(connection.total_bytes) for connection in connections if connection.total_bytes is not None)}",
        f"- Per-connection duration ms: {format_set(str(connection.duration_ms) for connection in connections if connection.duration_ms is not None)}",
        f"- Read limit reached: {format_bool(any(connection.read_limit_reached for connection in connections))}",
        f"- Closed by peer after data: {format_bool(any(connection.closed_by_peer for connection in connections))}",
        f"- Additional-read hex lengths: {format_set(str(length) for connection in connections for length in (connection.read_hex_lens or []))}",
        f"- Read byte counts: {format_counter(Counter(str(length) for length in read_lengths))}",
        f"- Read byte sequences: {format_read_sequences(connections)}",
        f"- Inter-read gap buckets: {format_counter(read_gap_buckets)}",
        f"- Framing first-byte classes: {format_counter(framing_counter(connections, 'first_byte_class'))}",
        f"- Framing length-prefix candidates: {format_counter(framing_length_prefix_counter(connections))}",
        f"- Framing TLS record-like reads: {format_counter(framing_counter(connections, 'tls_record_like'))}",
        f"- Framing TLS record length matches: {format_counter(framing_counter(connections, 'tls_record_len_match'))}",
        f"- Framing shape samples: {format_framing_samples(connections)}",
        f"- Apple AWDL small-flow length hits: {awdl_hits['small']}",
        f"- Apple AWDL large-flow length hits: {awdl_hits['large']}",
        "",
        "## Interpretation",
        "",
        f"- macOS attempted advertised TCP port: {format_bool(bool(connections))}",
        f"- Apple AWDL length fingerprint overlap: {awdl_overlap_interpretation(awdl_hits)}",
        "- Notes:",
        "  - Inspect the raw transcript locally before deleting it.",
        "  - New observer output records read lengths and timing only, not payload bytes.",
        "  - Framing probe output, when enabled, records byte-class buckets and length-prefix/TLS hypotheses only.",
        "  - Older transcripts may include local-only hex prefixes; this summary preserves only their hex-string lengths.",
        "  - Compare read byte sequences and gap buckets with the Apple-to-Apple AWDL payload-length fingerprints before treating a TCP attempt as native Universal Control data-path progress.",
        "  - Do not commit raw peer addresses, hostnames, or TCP payload bytes.",
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
        "framing_probe": False,
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
        if stripped == "TCP observer framing probe enabled: yes":
            result["framing_probe"] = True
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
    first_read_length_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) first_read_elapsed_ms=(?P<elapsed>\d+) first_read_bytes=(?P<bytes>\d+)$"
    )
    read_pattern = re.compile(
        r"^TCP observer connection #(?P<index>\d+) read #(?P<read_index>\d+) elapsed_ms=(?P<elapsed>\d+) bytes=(?P<bytes>\d+) hex_prefix=(?P<hex>[0-9a-fA-F]*)$"
    )
    read_length_pattern = re.compile(
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
            connection.read_events.append((1, 0, int(first_read.group("bytes"))))
            continue

        first_read_length = first_read_length_pattern.match(stripped)
        if first_read_length:
            connection = connections.setdefault(
                first_read_length.group("index"),
                ObserverConnection(index=first_read_length.group("index"), peer="<unknown>"),
            )
            connection.outcome = "first_read"
            connection.first_read_bytes = int(first_read_length.group("bytes"))
            connection.read_events.append(
                (
                    1,
                    int(first_read_length.group("elapsed")),
                    int(first_read_length.group("bytes")),
                )
            )
            continue

        read = read_pattern.match(stripped)
        if read:
            connection = connections.setdefault(
                read.group("index"),
                ObserverConnection(index=read.group("index"), peer="<unknown>"),
            )
            if connection.read_hex_lens is None:
                connection.read_hex_lens = []
            connection.read_hex_lens.append(len(read.group("hex")))
            connection.read_events.append(
                (
                    int(read.group("read_index")),
                    int(read.group("elapsed")),
                    int(read.group("bytes")),
                )
            )
            continue

        read_length = read_length_pattern.match(stripped)
        if read_length:
            connection = connections.setdefault(
                read_length.group("index"),
                ObserverConnection(index=read_length.group("index"), peer="<unknown>"),
            )
            connection.read_events.append(
                (
                    int(read_length.group("read_index")),
                    int(read_length.group("elapsed")),
                    int(read_length.group("bytes")),
                )
            )
            continue

        framing = framing_pattern.match(stripped)
        if framing:
            connection = connections.setdefault(
                framing.group("index"),
                ObserverConnection(index=framing.group("index"), peer="<unknown>"),
            )
            connection.framing_events.append(
                (
                    int(framing.group("read_index")),
                    parse_shape_fields(framing.group("shape")),
                )
            )
            continue

        summary = summary_pattern.match(stripped)
        if summary:
            connection = connections.setdefault(
                summary.group("index"),
                ObserverConnection(index=summary.group("index"), peer="<unknown>"),
            )
            connection.read_count = int(summary.group("reads"))
            connection.total_bytes = int(summary.group("total_bytes"))
            connection.duration_ms = int(summary.group("duration_ms"))
            connection.read_limit_reached = summary.group("read_limit_reached") == "true"
            connection.closed_by_peer = summary.group("closed_by_peer") == "true"
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


def all_read_lengths(connections: list[ObserverConnection]) -> list[int]:
    return [
        bytes_read
        for connection in connections
        for _, _, bytes_read in sorted(connection.read_events)
    ]


def all_read_gap_buckets(connections: list[ObserverConnection]) -> Counter[str]:
    buckets: Counter[str] = Counter()
    for connection in connections:
        previous_elapsed: int | None = None
        for _, elapsed, _ in sorted(connection.read_events):
            if previous_elapsed is not None:
                buckets[gap_bucket(max(0, elapsed - previous_elapsed))] += 1
            previous_elapsed = elapsed
    return buckets


def parse_shape_fields(value: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in value.split():
        if "=" not in part:
            continue
        key, field_value = part.split("=", 1)
        fields[key] = field_value
    return fields


def framing_counter(connections: list[ObserverConnection], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for connection in connections:
        for _, fields in connection.framing_events:
            value = fields.get(key)
            if value:
                counter[value] += 1
    return counter


def framing_length_prefix_counter(connections: list[ObserverConnection]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for connection in connections:
        for _, fields in connection.framing_events:
            value = fields.get("length_prefix_candidates")
            if not value:
                continue
            for candidate in value.split("|"):
                counter[candidate] += 1
    return counter


def gap_bucket(milliseconds: int) -> str:
    if milliseconds < 1:
        return "<1ms"
    if milliseconds < 10:
        return "1-10ms"
    if milliseconds < 100:
        return "10-100ms"
    if milliseconds < 1000:
        return "100ms-1s"
    return ">=1s"


def apple_awdl_length_hits(lengths: list[int]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for length in lengths:
        text = str(length)
        if text in APPLE_AWDL_SMALL_LENGTHS:
            counts["small"] += 1
        if text in APPLE_AWDL_LARGE_LENGTHS:
            counts["large"] += 1
    return counts


def awdl_overlap_interpretation(hits: Counter[str]) -> str:
    small = hits["small"]
    large = hits["large"]
    if small and large:
        return "small and large Apple-session length families observed; compare timing before escalating"
    if small:
        return "small-message Apple-session length family observed"
    if large:
        return "large-message Apple-session length family observed"
    return "no Apple-session length-family overlap observed"


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
    host, port = split_host_port(value.strip())
    if port is not None:
        return f"<redacted {classify_host(host)} peer port_class={classify_port(port)}>"
    return f"<redacted {classify_host(host)} peer>"


def split_host_port(value: str) -> tuple[str, str | None]:
    bracketed = re.fullmatch(r"\[(?P<host>.+)\]:(?P<port>\d+)", value)
    if bracketed:
        return bracketed.group("host"), bracketed.group("port")
    if value.startswith("[") and value.endswith("]"):
        return value[1:-1], None

    host, separator, port = value.rpartition(":")
    if separator and port.isdigit() and ":" not in host:
        return host, port
    return value, None


def classify_bind_addr(value: str) -> str:
    if value in {"0.0.0.0", "[::]", "::"}:
        return "unspecified"
    if value.startswith("127.") or value == "::1" or value == "[::1]":
        return "loopback"
    return classify_host(value)


def classify_host(value: str) -> str:
    normalized = value.strip("[]")
    host_without_zone = normalized.split("%", 1)[0]
    try:
        address = ipaddress.ip_address(host_without_zone)
    except ValueError:
        return "hostname"

    if address.version == 6:
        if address.is_loopback:
            return "loopback-v6"
        if address.is_link_local:
            return "link-local-v6"
        if address.is_private:
            return "private-v6"
        if address.is_multicast:
            return "multicast-v6"
        return "public-v6"

    if address.is_loopback:
        return "loopback-v4"
    if address.is_link_local:
        return "link-local-v4"
    if address.is_private:
        return "private-v4"
    if address.is_multicast:
        return "multicast-v4"
    if address.is_reserved:
        return "reserved-v4"
    return "public-v4"


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


def format_read_sequences(connections: list[ObserverConnection]) -> str:
    rendered: list[str] = []
    for connection in connections:
        lengths = [str(bytes_read) for _, _, bytes_read in sorted(connection.read_events)]
        if lengths:
            rendered.append(f"`#{connection.index}:{','.join(lengths[:16])}`")
    return ", ".join(rendered) if rendered else "none"


def format_framing_samples(connections: list[ObserverConnection]) -> str:
    rendered: list[str] = []
    for connection in connections:
        for read_index, fields in sorted(connection.framing_events, key=lambda event: event[0])[:8]:
            rendered.append(
                "`#{}/{}:first={},len_prefix={},tls={},ascii={},high={}`".format(
                    connection.index,
                    read_index,
                    fields.get("first_byte_class", "missing"),
                    fields.get("length_prefix_candidates", "missing"),
                    fields.get("tls_record_like", "missing"),
                    fields.get("ascii_ratio", "missing"),
                    fields.get("high_ratio", "missing"),
                )
            )
    return ", ".join(rendered) if rendered else "none"


def display_path(path: Path) -> str:
    parts = path.parts
    for marker in ("artifacts", "docs"):
        if marker in parts:
            return "/".join(parts[parts.index(marker) :])
    return path.name


def format_bool(value) -> str:
    return "yes" if bool(value) else "no"


if __name__ == "__main__":
    raise SystemExit(main())
