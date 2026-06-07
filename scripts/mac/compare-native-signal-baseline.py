#!/usr/bin/env python3
"""Compare a Windows-candidate Mac watcher summary against an Apple UC session baseline."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SIGNAL_FIELDS = {
    "stream": "Unified Log / Native stream keyword lines",
    "target_input": "Unified Log / Native target/input keyword lines",
    "sync_layout": "Unified Log / Native sync/layout keyword lines",
    "proximity": "Unified Log / Native/proximity-process proximity keyword lines",
    "wifi_p2p": "Unified Log / Native/transport-process Wi-Fi P2P keyword lines",
}

WATCH_HIGHLIGHTS = [
    "Source / Service",
    "DNS-SD Browse / Expected instance seen",
    "DNS-SD Resolve / Resolve events",
    "Unified Log / UniversalControl/rapportd candidate keyword lines",
    "Unified Log / UniversalControl/rapportd error/rejection keyword lines",
    "Interpretation / Native Universal Control candidate reaction",
    "Interpretation / Proximity or Wi-Fi P2P side-channel signal",
]


@dataclass(frozen=True)
class SignalCounts:
    stream: int
    target_input: int
    sync_layout: int
    proximity: int
    wifi_p2p: int

    def as_dict(self) -> dict[str, int]:
        return {
            "stream": self.stream,
            "target_input": self.target_input,
            "sync_layout": self.sync_layout,
            "proximity": self.proximity,
            "wifi_p2p": self.wifi_p2p,
        }

    def active_families(self) -> set[str]:
        return {name for name, value in self.as_dict().items() if value > 0}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare commit-safe native signal counters from an Apple-to-Apple "
            "Universal Control session summary and a Mac watcher summary from a "
            "Windows native-admission candidate."
        )
    )
    parser.add_argument("baseline_summary", type=Path, help="Redacted Apple UC session summary")
    parser.add_argument("candidate_summary", type=Path, help="Redacted macOS watcher summary")
    parser.add_argument("--baseline-label", default="apple-session", help="Label for the baseline summary")
    parser.add_argument("--candidate-label", default="candidate", help="Label for the candidate summary")
    parser.add_argument("--output", type=Path, help="Write Markdown comparison to this path instead of stdout")
    args = parser.parse_args()

    baseline = parse_summary(args.baseline_summary)
    candidate = parse_summary(args.candidate_summary)
    comparison = render_comparison(
        baseline,
        candidate,
        args.baseline_summary,
        args.candidate_summary,
        args.baseline_label,
        args.candidate_label,
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

        if key:
            fields[" / ".join([*section, key]) if section else key] = value
    return fields


def render_comparison(
    baseline: dict[str, str],
    candidate: dict[str, str],
    baseline_path: Path,
    candidate_path: Path,
    baseline_label: str,
    candidate_label: str,
) -> str:
    baseline_signals = read_signal_counts(baseline)
    candidate_signals = read_signal_counts(candidate)
    baseline_active = baseline_signals.active_families()
    candidate_active = candidate_signals.active_families()
    overlapping = baseline_active & candidate_active
    missing = baseline_active - candidate_active
    candidate_only = candidate_active - baseline_active
    visible = candidate_visible(candidate)
    resolved = candidate_resolved(candidate)
    tier = candidate_tier(candidate, candidate_signals, visible, resolved)

    lines = [
        "# Redacted Native Signal Baseline Comparison",
        "",
        "## Source",
        "",
        f"- Baseline label: `{baseline_label}`",
        f"- Baseline summary: `{baseline_path}`",
        f"- Candidate label: `{candidate_label}`",
        f"- Candidate summary: `{candidate_path}`",
        "- Raw output: not included",
        "",
        "## Gate Summary",
        "",
        f"- Candidate visible to macOS: {format_bool(visible)}",
        f"- Candidate resolved by macOS: {format_bool(resolved)}",
        f"- Baseline active signal families: {format_families(baseline_active)}",
        f"- Candidate active signal families: {format_families(candidate_active)}",
        f"- Candidate overlaps baseline families: {format_families(overlapping)}",
        f"- Candidate missing baseline families: {format_families(missing)}",
        f"- Candidate-only families: {format_families(candidate_only)}",
        f"- Candidate baseline tier: {tier}",
        "",
        "## Signal Counts",
        "",
        "| Signal family | Baseline count | Candidate count | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    lines.extend(render_signal_rows(baseline_signals, candidate_signals))
    lines.extend(["", "## Candidate Highlights", ""])
    lines.extend(render_highlights(candidate))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This comparison uses only redacted summary counters.",
            "- Matching the Apple baseline signal families is not admission by itself; it identifies which raw local artifact window deserves inspection.",
            "- DNS-SD visibility and resolve must be paired with native log signal before changing the Windows candidate shape.",
            "- Side-channel-only overlap is weaker than stream, target/input, or sync/layout overlap.",
            "- Do not commit raw hostnames, addresses, TXT values, log lines, packet payloads, or dynamic peer ports.",
            "",
        ]
    )
    return "\n".join(lines)


def read_signal_counts(fields: dict[str, str]) -> SignalCounts:
    values = {name: parse_int(fields.get(field, "0")) for name, field in SIGNAL_FIELDS.items()}
    return SignalCounts(**values)


def render_signal_rows(baseline: SignalCounts, candidate: SignalCounts) -> list[str]:
    rows = []
    for name in SIGNAL_FIELDS:
        baseline_count = baseline.as_dict()[name]
        candidate_count = candidate.as_dict()[name]
        if candidate_count and baseline_count:
            status = "overlap"
        elif candidate_count:
            status = "candidate-only"
        elif baseline_count:
            status = "missing"
        else:
            status = "inactive"
        rows.append(f"| `{name}` | {baseline_count} | {candidate_count} | {status} |")
    return rows


def render_highlights(candidate: dict[str, str]) -> list[str]:
    lines = []
    for field in WATCH_HIGHLIGHTS:
        lines.append(f"- `{field}`: {candidate.get(field, 'missing')}")
    return lines


def candidate_visible(fields: dict[str, str]) -> bool:
    return yes_value(fields.get("Interpretation / macOS browse saw expected Windows service")) or yes_value(
        fields.get("DNS-SD Browse / Expected instance seen")
    )


def candidate_resolved(fields: dict[str, str]) -> bool:
    if yes_value(fields.get("Interpretation / macOS resolve succeeded")):
        return True
    return parse_int(fields.get("DNS-SD Resolve / Resolve events", "0")) > 0


def candidate_tier(
    fields: dict[str, str],
    signals: SignalCounts,
    visible: bool,
    resolved: bool,
) -> str:
    if not visible:
        return "not_visible"
    if not resolved:
        return "browse_only"
    if signals.stream or signals.target_input or signals.sync_layout:
        return "resolved_with_session_like_signal"
    candidate_keywords = parse_int(fields.get("Unified Log / UniversalControl/rapportd candidate keyword lines", "0"))
    error_keywords = parse_int(fields.get("Unified Log / UniversalControl/rapportd error/rejection keyword lines", "0"))
    if candidate_keywords or error_keywords:
        return "resolved_with_candidate_or_rejection_signal"
    if signals.proximity or signals.wifi_p2p:
        return "resolved_with_side_channel_signal"
    return "resolved_no_native_signal"


def parse_int(value: str | None) -> int:
    if not value:
        return 0
    match = re.search(r"-?\d+", value.replace(",", ""))
    if not match:
        return 0
    return int(match.group(0))


def yes_value(value: str | None) -> bool:
    return (value or "").strip().lower() == "yes"


def format_families(values: set[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in sorted(values))


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
