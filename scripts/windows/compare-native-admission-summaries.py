#!/usr/bin/env python3
"""Compare two redacted Windows native-admission output summaries."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


DEFAULT_IGNORED_FIELDS = {
    "Source / Transcript file",
}

HIGHLIGHT_FIELDS = [
    "Command Result / Cargo finished lines",
    "Command Result / AnyUniversalControl command executed",
    "Command Result / Error lines",
    "Command Result / Observer bind errors",
    "Advertisement / Advertised service",
    "Advertisement / Advertised port",
    "Advertisement / Advertise duration",
    "TCP Observer / Observer enabled",
    "TCP Observer / Observer bind address class",
    "TCP Observer / Observer port",
    "TCP Observer / Observer duration",
    "TCP Observer / Framing probe enabled",
    "TCP Observer / Accepted connection summary",
    "TCP Observer / Accepted connection lines",
    "TCP Observer / Unique redacted peer count",
    "TCP Observer / Redacted peer classes",
    "TCP Observer / Connection outcomes",
    "TCP Observer / First-read byte counts",
    "TCP Observer / First-read hex lengths",
    "TCP Observer / Per-connection read counts",
    "TCP Observer / Per-connection total byte counts",
    "TCP Observer / Per-connection duration ms",
    "TCP Observer / Read limit reached",
    "TCP Observer / Closed by peer after data",
    "TCP Observer / Additional-read hex lengths",
    "TCP Observer / Read byte counts",
    "TCP Observer / Read byte sequences",
    "TCP Observer / Inter-read gap buckets",
    "TCP Observer / Read burst count",
    "TCP Observer / Read burst read-count buckets",
    "TCP Observer / Read burst byte buckets",
    "TCP Observer / Read burst duration buckets",
    "TCP Observer / Read burst idle gap buckets",
    "TCP Observer / Read burst length fingerprints",
    "TCP Observer / Initial read bursts",
    "TCP Observer / Framing first-byte classes",
    "TCP Observer / Framing entropy buckets",
    "TCP Observer / Framing byte-diversity buckets",
    "TCP Observer / Framing length-prefix candidates",
    "TCP Observer / Framing TLS record-like reads",
    "TCP Observer / Framing shape samples",
    "TCP Observer / Apple AWDL small-flow length hits",
    "TCP Observer / Apple AWDL large-flow length hits",
    "Interpretation / macOS attempted advertised TCP port",
    "Interpretation / Apple AWDL length fingerprint overlap",
]


@dataclass(frozen=True)
class FieldChange:
    path: str
    before: str | None
    after: str | None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare commit-safe summaries from summarize-native-admission-output.py."
    )
    parser.add_argument("before", type=Path, help="Earlier redacted Windows native-admission summary")
    parser.add_argument("after", type=Path, help="Later redacted Windows native-admission summary")
    parser.add_argument("--before-label", default="before", help="Label for the earlier summary")
    parser.add_argument("--after-label", default="after", help="Label for the later summary")
    parser.add_argument(
        "--include-source",
        action="store_true",
        help="Include source transcript file paths in the comparison.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown comparison to this path instead of stdout.",
    )
    args = parser.parse_args()

    before = parse_summary(args.before)
    after = parse_summary(args.after)
    ignored = set() if args.include_source else DEFAULT_IGNORED_FIELDS

    comparison = render_comparison(
        before,
        after,
        args.before,
        args.after,
        args.before_label,
        args.after_label,
        ignored,
    )
    if args.output:
        args.output.write_text(comparison, encoding="utf-8")
    else:
        print(comparison, end="")
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

        if not key:
            continue
        field_path = " / ".join([*section, key]) if section else key
        fields[field_path] = value
    return fields


def render_comparison(
    before: dict[str, str],
    after: dict[str, str],
    before_path: Path,
    after_path: Path,
    before_label: str,
    after_label: str,
    ignored: set[str],
) -> str:
    before_keys = set(before) - ignored
    after_keys = set(after) - ignored
    added = [FieldChange(path, None, after[path]) for path in sorted(after_keys - before_keys)]
    removed = [FieldChange(path, before[path], None) for path in sorted(before_keys - after_keys)]
    changed = [
        FieldChange(path, before[path], after[path])
        for path in sorted(before_keys & after_keys)
        if before[path] != after[path]
    ]

    lines = [
        "# Redacted Windows Native Admission Comparison",
        "",
        "## Source",
        "",
        f"- Before label: `{before_label}`",
        f"- Before file: `{before_path}`",
        f"- After label: `{after_label}`",
        f"- After file: `{after_path}`",
        f"- Ignored source metadata: {format_bool(bool(ignored))}",
        "",
        "## Summary",
        "",
        f"- Changed fields: {len(changed)}",
        f"- Added fields: {len(added)}",
        f"- Removed fields: {len(removed)}",
        "",
        "## Evidence Highlights",
        "",
    ]
    lines.extend(render_highlights(before, after, before_label, after_label, ignored))
    lines.extend(["", "## Changed Fields", ""])
    lines.extend(render_changes(changed, before_label, after_label))
    lines.extend(["", "## Added Fields", ""])
    lines.extend(render_changes(added, before_label, after_label))
    lines.extend(["", "## Removed Fields", ""])
    lines.extend(render_changes(removed, before_label, after_label))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This comparison is safe to commit only when both inputs are redacted summaries.",
            "- Use this for minimal CompanionLink versus shape-only CompanionLink Windows output summaries.",
            "- Pair this with `scripts/mac/compare-mdns-watch-summaries.py` for the same run.",
            "- Re-run with `--include-source` only when transcript paths are relevant.",
            "",
        ]
    )
    return "\n".join(lines)


def render_highlights(
    before: dict[str, str],
    after: dict[str, str],
    before_label: str,
    after_label: str,
    ignored: set[str],
) -> list[str]:
    lines: list[str] = []
    for field in HIGHLIGHT_FIELDS:
        if field in ignored:
            continue
        before_value = before.get(field)
        after_value = after.get(field)
        if before_value is None and after_value is None:
            continue
        status = "same" if before_value == after_value else "changed"
        lines.append(f"- `{field}`: {status}")
        if before_value is not None:
            lines.append(f"  - {before_label}: {before_value}")
        if after_value is not None:
            lines.append(f"  - {after_label}: {after_value}")
    if not lines:
        return ["- none"]
    return lines


def render_changes(changes: list[FieldChange], before_label: str, after_label: str) -> list[str]:
    if not changes:
        return ["- none"]

    lines: list[str] = []
    for change in changes:
        lines.append(f"- `{change.path}`")
        if change.before is not None:
            lines.append(f"  - {before_label}: {change.before}")
        if change.after is not None:
            lines.append(f"  - {after_label}: {change.after}")
    return lines


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
