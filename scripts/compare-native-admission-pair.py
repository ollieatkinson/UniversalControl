#!/usr/bin/env python3
"""Pair redacted macOS and Windows native-admission summaries."""

from __future__ import annotations

import argparse
from pathlib import Path


MAC_HIGHLIGHTS = [
    "Source / Service",
    "DNS-SD Browse / Add events",
    "DNS-SD Browse / Expected instance seen",
    "DNS-SD Resolve / Resolve events",
    "DNS-SD Resolve / Ports",
    "DNS-SD Resolve / TXT keys",
    "DNS-SD Resolve / TXT value classes",
    "Unified Log / UniversalControl/rapportd candidate keyword lines",
    "Unified Log / UniversalControl/rapportd error/rejection keyword lines",
    "Unified Log / Native stream keyword lines",
    "Unified Log / Native target/input keyword lines",
    "Unified Log / Native sync/layout keyword lines",
    "Unified Log / Native/proximity-process proximity keyword lines",
    "Unified Log / Native/transport-process Wi-Fi P2P keyword lines",
    "Interpretation / macOS browse saw expected Windows service",
    "Interpretation / macOS resolve succeeded",
    "Interpretation / Native Universal Control candidate reaction",
    "Interpretation / Proximity or Wi-Fi P2P side-channel signal",
]

WINDOWS_HIGHLIGHTS = [
    "Advertisement / Advertised service",
    "Advertisement / Advertised port",
    "TCP Observer / Observer enabled",
    "TCP Observer / Framing probe enabled",
    "TCP Observer / Accepted connection summary",
    "TCP Observer / Accepted connection lines",
    "TCP Observer / Redacted peer classes",
    "TCP Observer / Connection outcomes",
    "TCP Observer / First-read byte counts",
    "TCP Observer / First-read hex lengths",
    "TCP Observer / Per-connection read counts",
    "TCP Observer / Per-connection total byte counts",
    "TCP Observer / Read limit reached",
    "TCP Observer / Closed by peer after data",
    "TCP Observer / Additional-read hex lengths",
    "TCP Observer / Read byte counts",
    "TCP Observer / Read byte sequences",
    "TCP Observer / Inter-read gap buckets",
    "TCP Observer / Framing first-byte classes",
    "TCP Observer / Framing length-prefix candidates",
    "TCP Observer / Framing TLS record-like reads",
    "TCP Observer / Framing shape samples",
    "TCP Observer / Apple AWDL small-flow length hits",
    "TCP Observer / Apple AWDL large-flow length hits",
    "Interpretation / macOS attempted advertised TCP port",
    "Interpretation / Apple AWDL length fingerprint overlap",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a paired native-admission report from redacted Mac and Windows summaries."
    )
    parser.add_argument("mac_summary", type=Path, help="Redacted macOS watcher summary")
    parser.add_argument("windows_summary", type=Path, help="Redacted Windows output summary")
    parser.add_argument("--label", default="native admission attempt", help="Short run label")
    parser.add_argument("--output", type=Path, help="Write Markdown report to this path")
    args = parser.parse_args()

    mac = parse_summary(args.mac_summary)
    windows = parse_summary(args.windows_summary)
    report = render_report(args.label, args.mac_summary, args.windows_summary, mac, windows)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


def parse_summary(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    section: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            section = section[:1] + [line.removeprefix("### ").strip()]
            continue
        if line.startswith("## "):
            section = [line.removeprefix("## ").strip()]
            continue
        if not line.startswith("- "):
            continue

        item = line.removeprefix("- ").strip()
        if ":" in item:
            key, value = item.split(":", 1)
            key = key.strip()
            value = value.strip()
        else:
            key = item
            value = "present"

        if key:
            fields[" / ".join([*section, key]) if section else key] = value
    return fields


def render_report(
    label: str,
    mac_path: Path,
    windows_path: Path,
    mac: dict[str, str],
    windows: dict[str, str],
) -> str:
    mac_seen = yes_value(mac.get("Interpretation / macOS browse saw expected Windows service"))
    mac_resolved = yes_value(mac.get("Interpretation / macOS resolve succeeded"))
    tcp_attempt = yes_value(windows.get("Interpretation / macOS attempted advertised TCP port"))
    native_signal = mac.get("Interpretation / Native Universal Control candidate reaction", "unknown")
    side_channel_signal = mac.get("Interpretation / Proximity or Wi-Fi P2P side-channel signal", "unknown")

    lines = [
        "# Redacted Native Admission Pair Report",
        "",
        "## Source",
        "",
        f"- Label: `{label}`",
        f"- macOS summary: `{mac_path}`",
        f"- Windows summary: `{windows_path}`",
        "- Raw output: not included",
        "",
        "## Gate Summary",
        "",
        f"- macOS saw expected service: {format_bool(mac_seen)}",
        f"- macOS resolved service: {format_bool(mac_resolved)}",
        f"- Windows observed TCP attempt: {format_bool(tcp_attempt)}",
        f"- Native candidate/log signal: {native_signal}",
        f"- Proximity or Wi-Fi P2P side-channel signal: {side_channel_signal}",
        f"- Admission evidence tier: {admission_tier(mac_seen, mac_resolved, tcp_attempt, native_signal)}",
        "",
        "## macOS Highlights",
        "",
    ]
    lines.extend(render_highlights(MAC_HIGHLIGHTS, mac))
    lines.extend(["", "## Windows Highlights", ""])
    lines.extend(render_highlights(WINDOWS_HIGHLIGHTS, windows))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- DNS-SD browse/resolve alone is visibility, not native admission.",
            "- A Windows TCP observer connection is evidence that macOS tried the advertised SRV endpoint.",
            "- Read-length overlap with the Apple AWDL baseline is only a framing clue; compare timing and native macOS logs before escalating.",
            "- Candidate or rejection keywords in native macOS logs should be inspected locally in raw artifacts before drawing conclusions.",
            "- Do not commit raw peer addresses, hostnames, TXT values, log lines, or TCP payload bytes.",
            "",
        ]
    )
    return "\n".join(lines)


def render_highlights(fields: list[str], summary: dict[str, str]) -> list[str]:
    lines = []
    for field in fields:
        lines.append(f"- `{field}`: {summary.get(field, 'missing')}")
    return lines


def admission_tier(
    mac_seen: bool,
    mac_resolved: bool,
    tcp_attempt: bool,
    native_signal: str,
) -> str:
    if not mac_seen:
        return "not_visible"
    if not mac_resolved:
        return "browse_only"
    if tcp_attempt and native_log_signal(native_signal):
        return "resolved_with_tcp_attempt_and_native_log_signal"
    if tcp_attempt:
        return "resolved_with_tcp_attempt"
    if native_log_signal(native_signal):
        return "resolved_with_native_log_signal"
    return "resolved_no_tcp_attempt"


def native_log_signal(value: str) -> bool:
    normalized = value.lower()
    return (
        "possible signal" in normalized
        or "stream, target, or sync/layout signal" in normalized
        or "stream or sync/layout signal" in normalized
    )


def yes_value(value: str | None) -> bool:
    return (value or "").strip().lower() == "yes"


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
