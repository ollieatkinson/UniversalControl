#!/usr/bin/env python3
"""Create a commit-safe summary from redacted CompanionLink discovery output."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResolvedEvent:
    fullname_len: str
    service_type: str
    host_len: str
    port: str
    address_count: str
    txt: tuple[tuple[str, str, str], ...]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize --redact output from discover-companion-link without leaking identifiers."
    )
    parser.add_argument("transcript", type=Path, help="Captured redacted discovery command output")
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
    command = summarize_command(text)
    events = summarize_events(text)
    resolved = parse_resolved_events(text)
    txt_keys = sorted({key for event in resolved for key, _, _ in event.txt})
    txt_classes = Counter(
        f"{key}:{value_class}:{length}"
        for event in resolved
        for key, length, value_class in event.txt
    )
    ports = Counter(event.port for event in resolved)
    service_types = Counter(event.service_type for event in resolved)
    fullname_lengths = Counter(event.fullname_len for event in resolved)
    host_lengths = Counter(event.host_len for event in resolved)
    address_counts = Counter(event.address_count for event in resolved)

    lines = [
        "# Redacted CompanionLink Discovery Summary",
        "",
        "## Source",
        "",
        f"- Transcript file: `{path}`",
        "- Raw output: not included",
        "",
        "## Command Result",
        "",
        f"- Cargo finished lines: {command['finished']}",
        f"- AnyKBFlow command executed: {format_bool(command['ran_anykbflow'])}",
        f"- Redaction enabled line: {format_bool(command['redaction_enabled'])}",
        f"- Error lines: {command['error_lines']}",
        "",
        "## Discovery Events",
        "",
        f"- Search started lines: {events['search_started']}",
        f"- Service found lines: {events['service_found']}",
        f"- Service resolved lines: {len(resolved)}",
        f"- Service removed lines: {events['service_removed']}",
        f"- Other event lines: {events['other_event']}",
        "",
        "## Resolved Service Shape",
        "",
        f"- Service types: {format_counter(service_types)}",
        f"- Ports: {format_counter(ports)}",
        f"- Fullname lengths: {format_counter(fullname_lengths)}",
        f"- Host lengths: {format_counter(host_lengths)}",
        f"- Address counts: {format_counter(address_counts)}",
        f"- TXT keys: {format_set(txt_keys)}",
        f"- TXT value length/classes: {format_counter(txt_classes)}",
        "",
        "## Interpretation",
        "",
        f"- CompanionLink service resolved: {format_bool(bool(resolved))}",
        f"- Output appears redacted: "
        f"{format_bool(command['redaction_enabled'] and looks_redacted(text))}",
        "- Notes:",
        "  - This summary is commit-safe only when the input command used `--redact`.",
        "  - Do not commit unredacted hostnames, addresses, instance names, or TXT values.",
        "",
    ]
    return "\n".join(lines)


def summarize_command(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        stripped = line.strip()
        if "Finished `" in stripped:
            counts["finished"] += 1
        if "Running `" in stripped and "anykbflow" in stripped:
            counts["ran_anykbflow"] = 1
        if "Redaction enabled:" in stripped:
            counts["redaction_enabled"] = 1
        if stripped.startswith("Error:") or " error" in stripped.lower():
            counts["error_lines"] += 1
    return counts


def summarize_events(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        if "] search_started " in line:
            counts["search_started"] += 1
        elif "] service_found " in line:
            counts["service_found"] += 1
        elif "] service_removed " in line:
            counts["service_removed"] += 1
        elif re.search(r"\[[^\]]+\]\s+event\s+", line):
            counts["other_event"] += 1
    return counts


def parse_resolved_events(text: str) -> list[ResolvedEvent]:
    events: list[ResolvedEvent] = []
    pattern = re.compile(
        r"\[[^\]]+\]\s+service_resolved\s+"
        r"fullname=<redacted len=(?P<fullname_len>\d+)>\s+"
        r"type=(?P<service_type>\S+)\s+"
        r"host=<redacted len=(?P<host_len>\d+)>\s+"
        r"port=(?P<port>\d+)\s+"
        r"addresses=\[<redacted count=(?P<address_count>\d+)>\]\s+"
        r"txt=\[(?P<txt>.*)\]$"
    )
    for line in text.splitlines():
        match = pattern.search(line.strip())
        if not match:
            continue
        events.append(
            ResolvedEvent(
                fullname_len=match.group("fullname_len"),
                service_type=match.group("service_type"),
                host_len=match.group("host_len"),
                port=match.group("port"),
                address_count=match.group("address_count"),
                txt=tuple(parse_txt_summary(match.group("txt"))),
            )
        )
    return events


def parse_txt_summary(text: str) -> list[tuple[str, str, str]]:
    result: list[tuple[str, str, str]] = []
    pattern = re.compile(
        r"(?P<key>[^=\s]+)=<redacted len=(?P<length>\d+) class=(?P<value_class>[^>]+)>"
    )
    for match in pattern.finditer(text):
        result.append((match.group("key"), match.group("length"), match.group("value_class")))
    return result


def looks_redacted(text: str) -> bool:
    return "<redacted" in text and " service_resolved " in text


def format_bool(value: object) -> str:
    return "yes" if bool(value) else "no"


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_set(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in values)


if __name__ == "__main__":
    raise SystemExit(main())
