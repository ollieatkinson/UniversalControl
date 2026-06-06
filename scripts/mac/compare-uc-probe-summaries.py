#!/usr/bin/env python3
"""Compare two redacted macOS Universal Control probe summaries."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


DEFAULT_IGNORED_FIELDS = {
    "Source / Artifact",
    "Source / Created",
}


@dataclass(frozen=True)
class FieldChange:
    path: str
    before: str | None
    after: str | None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare commit-safe summaries from summarize-uc-probe-artifact.py."
    )
    parser.add_argument("before", type=Path, help="Earlier redacted UC probe summary")
    parser.add_argument("after", type=Path, help="Later redacted UC probe summary")
    parser.add_argument("--before-label", default="before", help="Label for the earlier summary")
    parser.add_argument("--after-label", default="after", help="Label for the later summary")
    parser.add_argument(
        "--include-source",
        action="store_true",
        help="Include source artifact name and created timestamp in the comparison.",
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
        "# Redacted macOS Universal Control Probe Comparison",
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
        "## Changed Fields",
        "",
    ]
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
            "- Re-run with `--include-source` only when artifact timestamps and names are relevant.",
            "",
        ]
    )
    return "\n".join(lines)


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
