#!/usr/bin/env python3
"""Create a commit-safe summary from `cargo run -- probe displays` output."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DisplayRow:
    index: str
    primary: str
    builtin: str
    name_len: int
    friendly_name_len: int
    x: str
    y: str
    width: str
    height: str
    scale: str
    rotation: str
    hz: str
    width_mm: str
    height_mm: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize display probe output without leaking display names."
    )
    parser.add_argument("transcript", type=Path, help="Captured display probe output")
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
    displays = parse_display_count(text)
    source = parse_display_source(text)
    rows = parse_display_rows(text)
    virtual_bounds = parse_virtual_bounds(text)
    command = summarize_command(text)

    lines = [
        "# Redacted Display Probe Summary",
        "",
        "## Source",
        "",
        f"- Transcript file: `{path}`",
        "- Raw output: not included",
        "",
        "## Command Result",
        "",
        f"- Cargo finished lines: {command['finished']}",
        f"- AnyUniversalControl command executed: {format_bool(command['ran_anyuniversalcontrol'])}",
        f"- Warning lines: {command['warnings']}",
        f"- Error lines: {command['errors']}",
        "",
        "## Display Inventory",
        "",
        f"- Reported display count: {displays or 'unknown'}",
        f"- Parsed display rows: {len(rows)}",
        f"- Display source: `{source or 'unknown'}`",
        f"- Primary rows: {format_counter(Counter(row.primary for row in rows))}",
        f"- Built-in rows: {format_counter(Counter(row.builtin for row in rows))}",
        f"- Negative origin observed: {format_bool(any(negative_origin(row) for row in rows))}",
        f"- Virtual bounds: {virtual_bounds or 'missing'}",
        "",
        "## Displays",
        "",
    ]
    lines.extend(render_display_rows(rows))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Native display geometry available: {format_bool(bool(rows))}",
            "- Notes:",
            "  - Display names and friendly names are omitted; only their lengths are preserved.",
            "  - Use primary width/height and virtual bounds to calibrate AnyUniversalControl bridge configs.",
            "  - Negative origins matter for displays placed left or above the primary display.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_display_count(text: str) -> str | None:
    match = re.search(r"^displays:\s*(\d+)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def parse_display_source(text: str) -> str | None:
    match = re.search(r"^display_source:\s*(\S+)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def parse_virtual_bounds(text: str) -> str | None:
    match = re.search(
        r"^virtual_bounds:\s*x=(?P<x>-?\d+)\s+y=(?P<y>-?\d+)\s+width=(?P<width>\d+)\s+height=(?P<height>\d+)\s*$",
        text,
        re.MULTILINE,
    )
    if not match:
        return None
    return (
        f"x={match.group('x')} y={match.group('y')} "
        f"width={match.group('width')} height={match.group('height')}"
    )


def parse_display_rows(text: str) -> list[DisplayRow]:
    rows: list[DisplayRow] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "index" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 14 or not cells[0].isdigit():
            continue
        rows.append(
            DisplayRow(
                index=cells[0],
                primary=cells[1],
                builtin=cells[2],
                name_len=len(cells[3]),
                friendly_name_len=len(cells[4]),
                x=cells[5],
                y=cells[6],
                width=cells[7],
                height=cells[8],
                scale=cells[9],
                rotation=cells[10],
                hz=cells[11],
                width_mm=cells[12],
                height_mm=cells[13],
            )
        )
    return rows


def summarize_command(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        stripped = line.strip()
        if "Finished `" in stripped:
            counts["finished"] += 1
        if "Running `" in stripped and "anyuniversalcontrol" in stripped:
            counts["ran_anyuniversalcontrol"] = 1
        if "WARN" in stripped or stripped.lower().startswith("warning"):
            counts["warnings"] += 1
        if stripped.startswith("Error:") or " error" in stripped.lower():
            counts["errors"] += 1
    return counts


def render_display_rows(rows: list[DisplayRow]) -> list[str]:
    if not rows:
        return ["- none"]
    return [
        "- "
        f"index={row.index} primary={row.primary} builtin={row.builtin} "
        f"name_len={row.name_len} friendly_name_len={row.friendly_name_len} "
        f"x={row.x} y={row.y} width={row.width} height={row.height} "
        f"scale={row.scale} rotation={row.rotation} hz={row.hz} "
        f"width_mm={row.width_mm} height_mm={row.height_mm}"
        for row in rows
    ]


def negative_origin(row: DisplayRow) -> bool:
    return row.x.startswith("-") or row.y.startswith("-")


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_bool(value: object) -> str:
    return "yes" if bool(value) else "no"


if __name__ == "__main__":
    raise SystemExit(main())
