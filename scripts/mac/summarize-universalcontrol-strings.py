#!/usr/bin/env python3
"""Summarize UniversalControl binary strings without local machine identifiers."""

from __future__ import annotations

import argparse
import re
import subprocess
from collections import Counter
from pathlib import Path


DEFAULT_BINARY = Path(
    "/System/Library/CoreServices/UniversalControl.app/Contents/MacOS/UniversalControl"
)

RELEVANT_RE = re.compile(
    r"UniversalControl|CompanionLink|Rapport|Ensemble|P2P|OPACK|HID|"
    r"Pointer|Keyboard|Pasteboard|Drag|AWDL|WiFiP2P|Nearby|Target|Focus|"
    r"Display|Device|Stream|Message|Sync|com\.apple\.",
    re.I,
)

SERVICE_ID_RE = re.compile(
    r"^(?:\.)?(?:com\.apple\.|universalcontrol\.)[A-Za-z0-9_.-]+$"
)

SERVICE_ID_TOKENS = (
    "universalcontrol",
    "ensemble",
    "rapport",
    "sharing.EnhancedDiscovery",
    "pasteboard",
    "UIKit.private.drag",
    "uikit.private.drag",
    "NSFilePromise",
    "ec.UniversalControl",
)

SOURCE_RE = re.compile(r"/Sources/(?P<path>Ensemble_executables/[^:\s]+)")

LOG_CATEGORIES = {
    "CompanionLink And Rapport": re.compile(r"CLink|Rapport|RPStream|Stream", re.I),
    "Peer-To-Peer Links": re.compile(r"P2P|DirectLink", re.I),
    "Message Synchronization": re.compile(
        r"Message|IDS|Sync|Merge|Pend|Skipping Message|Sending Message", re.I
    ),
    "Focus And Target Input": re.compile(
        r"Focus|Target|Keyboard|Pointer|HID|report|Pointing", re.I
    ),
    "Display And Device Layout": re.compile(
        r"Display|Device|Source Device|connected devices|reachable links|visible", re.I
    ),
    "Drag And Pasteboard": re.compile(r"Drag|Pasteboard|archive|promise", re.I),
    "Rejections And Errors": re.compile(
        r"Reject|Reset Remote|Failed|Failure|unexpected|timeout|error|mismatch", re.I
    ),
}

LOG_PRIORITIES = {
    "CompanionLink And Rapport": (
        "CLink Activated",
        "RPStreamServer Activated",
        "Accept Stream",
        "P2PStream Activated (Connection Ready)",
        "P2PStream Connection Ready",
        "P2PStream Canceled",
    ),
    "Peer-To-Peer Links": (
        "P2PDirectLink Activated",
        "Preparing P2PStream",
        "P2PStream Activated (Connection Ready)",
        "P2PStream Connection Ready",
        "P2PStream Canceled",
    ),
    "Message Synchronization": (
        "Initial Sync",
        "Create Message",
        "Send Message",
        "Receive Message",
        "Received Message",
        "Merge message",
        "Ignore past message",
        "Synchronization Failed",
    ),
    "Focus And Target Input": (
        "FocusMove",
        "TargetBegin",
        "TargetConnect",
        "TargetReady",
        "TargetEvent",
        "TargetReply",
        "Target Reply: Reject",
        "Removed Local Keyboard Reports",
    ),
    "Display And Device Layout": (
        "Device Found",
        "Ineligible Device Found",
        "Remote Display Layout",
        "Remote Source Device",
        "Remote Connected Devices",
        "Local Device Change",
        "Connected Devices Clock",
        "No main display",
    ),
    "Drag And Pasteboard": (
        "TargetReady drag",
        "preparing drag session",
        "skipping drag session",
        "Pasteboard Data Session",
        "pasteboard stream cancelled",
        "creating promise target",
        "setting promise target on pasteboard",
    ),
    "Rejections And Errors": (
        "Target Reply: Reject",
        "Reset Remote",
        "mismatched signature",
        "unexpected TargetReady",
        "timeout during HID",
        "TargetReply Failure",
        "Synchronization Failed",
    ),
}

TYPE_HINT_RE = re.compile(
    r"^(?:UniversalControl|CompanionLink|Rapport|P2P|EnsembleHID|"
    r"EventReport|Display|Pointer|Pasteboard|Drag|Sync|SecureLayer)[A-Za-z0-9_]+$"
)

TYPE_HINT_PRIORITIES = (
    "CompanionLinkClient",
    "CompanionLinkServer",
    "CompanionLinkSession",
    "RapportStreamServer",
    "RapportStreamSession",
    "P2PBrowser",
    "P2PController",
    "P2PDirectLink",
    "P2PLink",
    "P2PMessage",
    "P2PPeerCoordinator",
    "P2PStream",
    "SyncController",
    "SyncCoordinator",
    "SyncMessage",
    "EventReport",
    "EnsembleHIDController",
    "DisplayController",
    "PointerController",
    "PasteboardController",
    "PasteboardDataSession",
    "DragSourceCoordinator",
    "DragSinkCoordinator",
    "SecureLayerHost",
    "UniversalControlVirtualService",
)

NEARBY_SELECTOR_RE = re.compile(r"^session:did[A-Za-z]+")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a commit-safe UniversalControl string surface summary. "
            "Apple build-root paths are reduced to source-relative paths."
        )
    )
    parser.add_argument(
        "--binary",
        type=Path,
        default=DEFAULT_BINARY,
        help=f"UniversalControl binary path. Default: {DEFAULT_BINARY}",
    )
    parser.add_argument(
        "--strings-file",
        type=Path,
        help="Read pre-captured strings output instead of running strings(1).",
    )
    parser.add_argument("--output", type=Path, help="Write Markdown summary here.")
    args = parser.parse_args()

    if args.strings_file:
        text = args.strings_file.read_text(encoding="utf-8", errors="replace")
    else:
        if not args.binary.is_file():
            parser.error(f"binary not found: {args.binary}")
        text = run_strings(args.binary)

    summary = render_summary(args.binary, text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def run_strings(binary: Path) -> str:
    completed = subprocess.run(
        ["strings", "-a", str(binary)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or "strings command failed")
    return completed.stdout


def render_summary(binary: Path, text: str) -> str:
    strings = unique_lines(text)
    relevant = [line for line in strings if RELEVANT_RE.search(line)]
    source_paths = source_relative_paths(strings)
    service_ids = sorted(
        line.lstrip(".")
        for line in strings
        if SERVICE_ID_RE.match(line) and is_relevant_identifier(line)
    )
    type_hints = sorted(line for line in strings if TYPE_HINT_RE.match(line))
    nearby_selectors = sorted(line for line in strings if NEARBY_SELECTOR_RE.match(line))
    log_templates = [
        line for line in strings if is_log_template(line) and RELEVANT_RE.search(line)
    ]
    log_categories = categorize_logs(log_templates)
    source_groups = Counter(path.split("/", 1)[0] for path in source_paths)
    program_lines = [line for line in strings if line.startswith("@(#)PROGRAM:")]

    lines = [
        "# Redacted UniversalControl String Surface Summary",
        "",
        "## Source",
        "",
        f"- Binary: `{binary}`",
        f"- Program lines: {format_list(program_lines, limit=4)}",
        f"- Total unique strings: {len(strings)}",
        f"- Relevant strings matched: {len(relevant)}",
        "- Raw binary strings: not included",
        "- Redaction: Apple build roots are reduced to source-relative paths; "
        "private log placeholders are kept only as templates.",
        "",
        "## Source-Relative Files",
        "",
        f"- Source-relative file count: {len(source_paths)}",
        f"- Top-level groups: {format_counter(source_groups)}",
        "",
    ]
    lines.extend(format_bullets(source_paths, limit=80))

    lines.extend(
        [
            "",
            "## Stable Identifiers",
            "",
            f"- Identifier count: {len(service_ids)}",
            "",
        ]
    )
    lines.extend(format_bullets(service_ids, limit=80))

    lines.extend(
        [
            "",
            "## Runtime Type Hints",
            "",
            f"- Type hint count: {len(type_hints)}",
            "",
        ]
    )
    lines.extend(format_bullets(prioritize_type_hints(type_hints), limit=32))

    lines.extend(
        [
            "",
            "## NearbyInteraction Selectors",
            "",
            f"- Selector count: {len(nearby_selectors)}",
            "",
        ]
    )
    lines.extend(format_bullets(nearby_selectors, limit=40))

    lines.extend(["", "## Log Template Categories", ""])
    for name in sorted(LOG_CATEGORIES):
        entries = log_categories[name]
        lines.extend([f"### {name}", "", f"- Template count: {len(entries)}", ""])
        lines.extend(format_bullets(prioritize_logs(name, entries), limit=8))
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- The native app exposes a CompanionLink/Rapport stream server surface, "
            "plus P2P stream/message coordination and OPACK-adjacent glue.",
            "- Target-state log templates name `TargetBegin`, `TargetConnect`, "
            "`TargetReady`, `TargetEvent`, `TargetReply`, and rejection paths; "
            "future native-admission captures should search for those terms.",
            "- Display layout, synced devices, source devices, pointer focus, "
            "keyboard readiness, drag, and pasteboard all appear in the same "
            "UniversalControl binary, so an accepted peer likely enters one "
            "coordinated control plane before input transport.",
            "",
        ]
    )
    return "\n".join(lines)


def unique_lines(text: str) -> list[str]:
    values = {line.strip() for line in text.splitlines() if line.strip()}
    return sorted(values)


def source_relative_paths(strings: list[str]) -> list[str]:
    paths: set[str] = set()
    for line in strings:
        match = SOURCE_RE.search(line)
        if match:
            path = match.group("path").removeprefix("Ensemble_executables/")
            paths.add(path)
    return sorted(paths)


def is_log_template(line: str) -> bool:
    return "%{public}s" in line or "%llx" in line or "TargetReply Failure" in line


def is_relevant_identifier(line: str) -> bool:
    lowered = line.lower()
    return any(token.lower() in lowered for token in SERVICE_ID_TOKENS)


def categorize_logs(log_templates: list[str]) -> dict[str, list[str]]:
    categorized: dict[str, list[str]] = {name: [] for name in LOG_CATEGORIES}
    for line in log_templates:
        for name, pattern in LOG_CATEGORIES.items():
            if pattern.search(line):
                categorized[name].append(line)
    return {name: sorted(set(values)) for name, values in categorized.items()}


def prioritize_logs(category: str, entries: list[str]) -> list[str]:
    remaining = list(entries)
    selected: list[str] = []
    for token in LOG_PRIORITIES.get(category, ()):
        for entry in list(remaining):
            if token in entry:
                selected.append(entry)
                remaining.remove(entry)
                break
    selected.extend(remaining)
    return selected


def prioritize_type_hints(entries: list[str]) -> list[str]:
    remaining = list(entries)
    selected: list[str] = []
    for token in TYPE_HINT_PRIORITIES:
        for entry in list(remaining):
            if token in entry:
                selected.append(entry)
                remaining.remove(entry)
                break
    selected.extend(remaining)
    return selected


def format_bullets(values: list[str], limit: int) -> list[str]:
    if not values:
        return ["- none"]
    selected = values[:limit]
    lines = [f"- `{value}`" for value in selected]
    remaining = len(values) - len(selected)
    if remaining:
        lines.append(f"- ... {remaining} more")
    return lines


def format_list(values: list[str], limit: int) -> str:
    if not values:
        return "none"
    selected = ", ".join(f"`{value}`" for value in values[:limit])
    remaining = len(values) - limit
    if remaining > 0:
        return f"{selected}, ... {remaining} more"
    return selected


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={value}" for key, value in sorted(counter.items()))


if __name__ == "__main__":
    raise SystemExit(main())
