#!/usr/bin/env python3
"""Summarize historical macOS Universal Control unified logs without raw lines."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
import re


DEFAULT_PROCESSES = ("UniversalControl", "rapportd", "nearbyd", "wifip2pd")
OPTIONAL_MDNS_PROCESS = "mDNSResponder"


PATTERNS = {
    "discovery_keywords": re.compile(r"companion|_companion-link|dnsservice|browse|resolve|matching", re.I),
    "session_keywords": re.compile(r"clink|p2p|direct|stream|target|ready|focus|session|edge|control message", re.I),
    "input_keywords": re.compile(r"hid|keyboard|key|pointer|mouse|scroll|drag|pasteboard|event", re.I),
    "error_keywords": re.compile(r"reject|den(?:y|ied)|fail(?:ed|ure)?|(?<!no)error|invalid|refus|timeout", re.I),
    "stream_keywords": re.compile(r"RPStreamServer|P2PStream|P2PDirectLink|Accept Stream|Prepare Stream", re.I),
    "target_keywords": re.compile(
        r"FocusMove|FocusReset|TargetBegin|TargetConnect|TargetReady|TargetEvent|"
        r"TargetReply|Target Reply|Keyboard Reports|Pointing Reports|HID accumulation",
        re.I,
    ),
    "sync_layout_keywords": re.compile(
        r"Initial Sync|Create Message|Send Message|Receive Message|Received Message|"
        r"Remote Display Layout|Remote Source Device|Remote Connected Devices|"
        r"Remote Synced Devices|Reset Remote|Connected Devices Clock",
        re.I,
    ),
    "proximity_keywords": re.compile(r"nearby|proximity|ranging|NISession|NINearby|Bluetooth|\bBLE\b|\bUWB\b", re.I),
    "p2p_transport_keywords": re.compile(r"AWDL|WiFiP2P|wifip2p|peer[- ]to[- ]peer|P2PDirectLink|P2PStream", re.I),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Count native Universal Control signal families in a historical macOS unified-log window. "
            "The summary omits raw log lines and local identifiers."
        )
    )
    parser.add_argument("--start", required=True, help="Start time accepted by /usr/bin/log, e.g. '2026-06-05 00:00:00'.")
    parser.add_argument("--end", required=True, help="End time accepted by /usr/bin/log, e.g. '2026-06-06 00:00:00'.")
    parser.add_argument("--include-mdns", action="store_true", help="Also count mDNSResponder lines. Useful for short windows.")
    parser.add_argument("--info", action="store_true", help="Pass --info to log show.")
    parser.add_argument("--debug", action="store_true", help="Pass --debug to log show.")
    parser.add_argument("--context", help="Commit-safe operator note about the window, without identifiers.")
    parser.add_argument("--output", type=Path, help="Write Markdown summary to this path instead of stdout.")
    args = parser.parse_args()

    validate_timestamp(args.start, "--start")
    validate_timestamp(args.end, "--end")

    processes = list(DEFAULT_PROCESSES)
    if args.include_mdns:
        processes.append(OPTIONAL_MDNS_PROCESS)

    try:
        counts = count_log_window(
            start=args.start,
            end=args.end,
            processes=processes,
            include_info=args.info,
            include_debug=args.debug,
        )
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    summary = render_summary(
        start=args.start,
        end=args.end,
        processes=processes,
        include_info=args.info,
        include_debug=args.debug,
        context=args.context,
        counts=counts,
    )
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def validate_timestamp(value: str, label: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as error:
        raise SystemExit(f"{label} must use YYYY-MM-DD HH:MM:SS") from error


def count_log_window(
    *,
    start: str,
    end: str,
    processes: list[str],
    include_info: bool,
    include_debug: bool,
) -> Counter[str]:
    predicate = " || ".join(f'process == "{process}"' for process in processes)
    command = ["/usr/bin/log", "show"]
    if include_info:
        command.append("--info")
    if include_debug:
        command.append("--debug")
    command.extend(["--start", start, "--end", end, "--style", "compact", "--predicate", predicate])

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    counts: Counter[str] = Counter()
    for line in process.stdout:
        count_line(line, processes, counts)

    assert process.stderr is not None
    stderr = process.stderr.read().strip()
    return_code = process.wait()
    if return_code != 0:
        message = f"/usr/bin/log show failed with exit code {return_code}"
        if stderr:
            message += f": {stderr.splitlines()[-1]}"
        raise RuntimeError(message)
    return counts


def count_line(line: str, processes: list[str], counts: Counter[str]) -> None:
    if not is_log_line(line):
        return

    counts["total"] += 1
    native_session_process = "UniversalControl" in line or "rapportd" in line
    native_proximity_process = native_session_process or "nearbyd" in line
    native_p2p_transport_process = native_session_process or "wifip2pd" in line

    for process in processes:
        if process in line:
            counts[process] += 1

    signal_text = log_signal_text(line, processes)
    for name, pattern in PATTERNS.items():
        if not pattern.search(signal_text):
            continue
        counts[name] += 1
        if name in {"discovery_keywords", "session_keywords", "input_keywords", "error_keywords"} and native_session_process:
            counts[f"native_{name}"] += 1
        elif name in {"stream_keywords", "target_keywords", "sync_layout_keywords"} and native_session_process:
            counts[f"native_{name}"] += 1
        elif name == "proximity_keywords" and native_proximity_process:
            counts["native_proximity_keywords"] += 1
        elif name == "p2p_transport_keywords" and native_p2p_transport_process:
            counts["native_p2p_transport_keywords"] += 1


def log_signal_text(line: str, processes: list[str]) -> str:
    text = line
    for process in processes:
        text = text.replace(process, "")
    return text


def is_log_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return not (
        stripped.startswith("Filtering ")
        or stripped.startswith("Timestamp ")
        or stripped.startswith("Skipping ")
        or stripped.startswith("Persisting ")
    )


def render_summary(
    *,
    start: str,
    end: str,
    processes: list[str],
    include_info: bool,
    include_debug: bool,
    context: str | None,
    counts: Counter[str],
) -> str:
    lines = [
        "# Redacted Historical Universal Control Log Summary",
        "",
        "## Source",
        "",
        f"- Window start: {start}",
        f"- Window end: {end}",
        f"- Processes counted: {format_list(processes)}",
        f"- `log show --info`: {format_bool(include_info)}",
        f"- `log show --debug`: {format_bool(include_debug)}",
        "- Raw unified-log lines: not included",
        "- Hostnames, addresses, device names, and payloads: not included",
    ]
    if context:
        lines.append(f"- Context: {context}")

    lines.extend(
        [
            "",
            "## Process Counts",
            "",
            f"- Total counted lines: {counts['total']}",
            f"- UniversalControl lines: {counts['UniversalControl']}",
            f"- rapportd lines: {counts['rapportd']}",
            f"- nearbyd lines: {counts['nearbyd']}",
            f"- wifip2pd lines: {counts['wifip2pd']}",
            f"- mDNSResponder lines: {counts['mDNSResponder']}",
            "",
            "## Signal Families",
            "",
            f"- Discovery keyword lines: {counts['discovery_keywords']}",
            f"- Session/control keyword lines: {counts['session_keywords']}",
            f"- Input/action keyword lines: {counts['input_keywords']}",
            f"- Error/rejection keyword lines: {counts['error_keywords']}",
            f"- UniversalControl/rapportd discovery keyword lines: {counts['native_discovery_keywords']}",
            f"- UniversalControl/rapportd session/control keyword lines: {counts['native_session_keywords']}",
            f"- UniversalControl/rapportd input/action keyword lines: {counts['native_input_keywords']}",
            f"- UniversalControl/rapportd error/rejection keyword lines: {counts['native_error_keywords']}",
            f"- Native stream keyword lines: {counts['native_stream_keywords']}",
            f"- Native target/input keyword lines: {counts['native_target_keywords']}",
            f"- Native sync/layout keyword lines: {counts['native_sync_layout_keywords']}",
            f"- Proximity/ranging keyword lines: {counts['proximity_keywords']}",
            f"- Native/proximity-process proximity keyword lines: {counts['native_proximity_keywords']}",
            f"- Wi-Fi peer-to-peer/AWDL keyword lines: {counts['p2p_transport_keywords']}",
            f"- Native/transport-process Wi-Fi P2P keyword lines: {counts['native_p2p_transport_keywords']}",
            "",
            "## Interpretation",
            "",
            f"- Native session signal: {session_signal(counts)}",
            f"- Target/input negotiation signal: {target_signal(counts)}",
            f"- Proximity or Wi-Fi P2P side-channel signal: {side_channel_signal(counts)}",
            "- Notes:",
            "  - This is a historical log count, not a labeled action trace.",
            "  - Use it to decide whether old logs are worth narrower follow-up windows.",
            "  - A fresh `capture-uc-session.sh --duration 120` run is still the stronger Apple-to-Apple baseline.",
            "",
        ]
    )
    return "\n".join(lines)


def session_signal(counts: Counter[str]) -> str:
    if counts["native_stream_keywords"] or counts["native_sync_layout_keywords"]:
        return "stream or sync/layout signal in redacted counts; inspect raw local logs for a narrow window"
    if counts["native_session_keywords"] or counts["native_input_keywords"]:
        return "possible signal in redacted counts; inspect raw local logs for a narrow window"
    if counts["UniversalControl"] or counts["rapportd"]:
        return "native process logs present, no session/input keywords counted"
    return "no UniversalControl or rapportd lines counted"


def target_signal(counts: Counter[str]) -> str:
    if counts["native_target_keywords"]:
        return "target/input negotiation signal in redacted counts; inspect raw local logs for a narrow window"
    if counts["native_input_keywords"]:
        return "generic input/action keywords counted without target-state templates"
    return "no native target/input keywords counted"


def side_channel_signal(counts: Counter[str]) -> str:
    if counts["native_proximity_keywords"] or counts["native_p2p_transport_keywords"]:
        return "possible proximity or Wi-Fi peer-to-peer signal in redacted counts"
    if counts["proximity_keywords"] or counts["p2p_transport_keywords"]:
        return "only generic proximity or Wi-Fi peer-to-peer keywords counted"
    if counts["nearbyd"] or counts["wifip2pd"]:
        return "nearbyd or wifip2pd logs present without counted protocol keywords"
    return "no nearbyd or wifip2pd lines counted"


def format_list(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values)


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
