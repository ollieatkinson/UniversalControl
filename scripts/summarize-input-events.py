#!/usr/bin/env python3
"""Summarize normalized AnyUniversalControl InputEvent JSONL without leaking typed text."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize listen-events/grab-events JSONL without typed text."
    )
    parser.add_argument("jsonl", type=Path, help="Normalized InputEvent JSONL file")
    parser.add_argument("--output", type=Path, help="Write Markdown summary to this path")
    args = parser.parse_args()

    events, parse_errors = load_events(args.jsonl)
    summary = render_summary(args.jsonl, events, parse_errors)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def load_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    parse_errors = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            parse_errors += 1
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            parse_errors += 1
    return events, parse_errors


def render_summary(path: Path, events: list[dict[str, Any]], parse_errors: int) -> str:
    kinds = Counter(str(event.get("kind", "<missing>")) for event in events)
    keys = Counter(
        str(event.get("key"))
        for event in events
        if str(event.get("kind", "")).startswith("key_") and event.get("key") is not None
    )
    buttons = Counter(
        str(event.get("button"))
        for event in events
        if str(event.get("kind", "")).startswith("button_") and event.get("button") is not None
    )
    text_classes = Counter(text_class(event.get("text")) for event in events if event.get("kind") == "key_press")
    mouse_bounds = summarize_mouse_bounds(events)
    wheel_deltas = Counter(
        f"dx={event.get('delta_x')} dy={event.get('delta_y')}"
        for event in events
        if event.get("kind") == "wheel"
    )

    lines = [
        "# Redacted Input Event Summary",
        "",
        "## Source",
        "",
        f"- JSONL file: `{path}`",
        "- Raw events: not included",
        "",
        "## Event Counts",
        "",
        f"- Parsed events: {len(events)}",
        f"- Parse errors: {parse_errors}",
        f"- Event kinds: {format_counter(kinds)}",
        "",
        "## Keyboard",
        "",
        f"- Key names: {format_counter(keys)}",
        f"- Key text classes: {format_counter(text_classes)}",
        f"- Key press/release balance: {key_balance(events)}",
        "",
        "## Pointer And Buttons",
        "",
        f"- Button names: {format_counter(buttons)}",
        f"- Mouse move bounds: {mouse_bounds}",
        f"- Wheel deltas: {format_counter(wheel_deltas)}",
        "",
        "## Interpretation",
        "",
        f"- Contains keyboard events: {format_bool(any(kind.startswith('key_') for kind in kinds))}",
        f"- Contains pointer events: {format_bool('mouse_move' in kinds)}",
        f"- Contains button events: {format_bool(any(kind.startswith('button_') for kind in kinds))}",
        f"- Contains wheel events: {format_bool('wheel' in kinds)}",
        "- Notes:",
        "  - Typed text values are summarized by length/class only.",
        "  - Key names are normalized `rdev` names used by replay and bridge injection.",
        "  - Pointer bounds should be compared with `probe displays` geometry.",
        "",
    ]
    return "\n".join(lines)


def text_class(value: Any) -> str:
    if value is None:
        return "none"
    if not isinstance(value, str):
        return "non_string"
    if value == "":
        return "empty"
    if value.isascii() and value.isprintable():
        return f"printable_len_{len(value)}"
    return f"non_ascii_or_control_len_{len(value)}"


def summarize_mouse_bounds(events: list[dict[str, Any]]) -> str:
    points = [
        (event.get("x"), event.get("y"))
        for event in events
        if event.get("kind") == "mouse_move"
        and isinstance(event.get("x"), (int, float))
        and isinstance(event.get("y"), (int, float))
    ]
    if not points:
        return "none"
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return f"x_min={min(xs):.2f} x_max={max(xs):.2f} y_min={min(ys):.2f} y_max={max(ys):.2f}"


def key_balance(events: list[dict[str, Any]]) -> str:
    presses = Counter(str(event.get("key")) for event in events if event.get("kind") == "key_press")
    releases = Counter(str(event.get("key")) for event in events if event.get("kind") == "key_release")
    names = sorted(set(presses) | set(releases))
    if not names:
        return "none"
    deltas = [f"`{name}`={presses[name] - releases[name]}" for name in names if presses[name] != releases[name]]
    if not deltas:
        return "balanced"
    return ", ".join(deltas)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_bool(value: object) -> str:
    return "yes" if bool(value) else "no"


if __name__ == "__main__":
    raise SystemExit(main())
