#!/usr/bin/env python3
"""Compare a Windows native-admission summary with an Apple AWDL session baseline."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


APPLE_AWDL_SMALL_LENGTHS = {"55", "82", "93", "97", "122", "126", "140", "174"}
APPLE_AWDL_LARGE_LENGTHS = {"621", "1428"}


@dataclass
class AwdlFlow:
    index: str
    summary: str
    payload_lengths: Counter[str] = field(default_factory=Counter)
    initial_sequence: list[str] = field(default_factory=list)
    gap_buckets: Counter[str] = field(default_factory=Counter)
    framing_first_byte_classes: Counter[str] = field(default_factory=Counter)
    framing_length_prefix_candidates: Counter[str] = field(default_factory=Counter)
    framing_tls_record_like: Counter[str] = field(default_factory=Counter)
    framing_tls_record_len_match: Counter[str] = field(default_factory=Counter)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a redacted Windows native-admission TCP observer summary "
            "against a redacted Apple-to-Apple AWDL Universal Control session summary."
        )
    )
    parser.add_argument(
        "awdl_baseline",
        type=Path,
        help="Redacted Apple-to-Apple session summary containing AWDL TCP Flow Shapes.",
    )
    parser.add_argument(
        "windows_summary",
        type=Path,
        help="Redacted Windows native-admission output summary.",
    )
    parser.add_argument("--baseline-label", default="apple-awdl-session")
    parser.add_argument("--windows-label", default="windows-native-admission")
    parser.add_argument("--output", type=Path, help="Write Markdown report to this path")
    args = parser.parse_args()

    baseline_flows = parse_awdl_flows(args.awdl_baseline)
    windows = parse_summary(args.windows_summary)
    report = render_report(
        args.baseline_label,
        args.windows_label,
        args.awdl_baseline,
        args.windows_summary,
        baseline_flows,
        windows,
    )
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


def parse_awdl_flows(path: Path) -> list[AwdlFlow]:
    flows: list[AwdlFlow] = []
    current: AwdlFlow | None = None
    in_awdl_section = False

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### AWDL TCP Flow Shapes"):
            in_awdl_section = True
            continue
        if in_awdl_section and (line.startswith("### ") or line.startswith("## ")):
            break
        if not in_awdl_section:
            continue

        flow_match = re.match(r"^- #(?P<index>\d+): (?P<summary>.+)$", line)
        if flow_match:
            current = AwdlFlow(
                index=flow_match.group("index"),
                summary=flow_match.group("summary"),
            )
            flows.append(current)
            continue

        if current is None:
            continue

        stripped = line.strip()
        if stripped.startswith("- payload directions:"):
            current.payload_lengths.update(parse_backtick_counter(stripped))
            continue
        if stripped.startswith("- initial nonzero payload sequence:"):
            current.initial_sequence = re.findall(r"`(?:a_to_b|b_to_a):(\d+)`", stripped)
            continue
        if stripped.startswith("- inter-payload gap buckets:"):
            current.gap_buckets.update(parse_backtick_counter(stripped))
            continue
        if stripped.startswith("- framing first-byte classes:"):
            current.framing_first_byte_classes.update(parse_backtick_counter(stripped))
            continue
        if stripped.startswith("- framing length-prefix candidates:"):
            current.framing_length_prefix_candidates.update(parse_backtick_counter(stripped))
            continue
        if stripped.startswith("- framing TLS record-like reads:"):
            current.framing_tls_record_like.update(parse_backtick_counter(stripped))
            continue
        if stripped.startswith("- framing TLS record length matches:"):
            current.framing_tls_record_len_match.update(parse_backtick_counter(stripped))

    return flows


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


def parse_backtick_counter(value: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for key, count in re.findall(r"`([^`]+)`=(\d+)", value):
        counter[key] += int(count)
    return counter


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def render_report(
    baseline_label: str,
    windows_label: str,
    baseline_path: Path,
    windows_path: Path,
    baseline_flows: list[AwdlFlow],
    windows: dict[str, str],
) -> str:
    baseline_lengths = combined_lengths(baseline_flows)
    baseline_gaps = combined_gaps(baseline_flows)
    baseline_framing = combined_framing(baseline_flows)
    windows_lengths = parse_backtick_counter(
        windows.get("TCP Observer / Read byte counts", "none")
    )
    windows_gaps = parse_backtick_counter(
        windows.get("TCP Observer / Inter-read gap buckets", "none")
    )
    common_lengths = Counter(
        {
            length: windows_lengths[length]
            for length in sorted(set(baseline_lengths) & set(windows_lengths), key=sort_length)
        }
    )
    common_gaps = Counter(
        {
            bucket: windows_gaps[bucket]
            for bucket in sorted(set(baseline_gaps) & set(windows_gaps))
        }
    )
    windows_framing = {
        "first_byte_classes": parse_backtick_counter(
            windows.get("TCP Observer / Framing first-byte classes", "none")
        ),
        "length_prefix_candidates": parse_backtick_counter(
            windows.get("TCP Observer / Framing length-prefix candidates", "none")
        ),
        "tls_record_like": parse_backtick_counter(
            windows.get("TCP Observer / Framing TLS record-like reads", "none")
        ),
        "tls_record_len_match": parse_backtick_counter(
            windows.get("TCP Observer / Framing TLS record length matches", "none")
        ),
    }
    tier = evidence_tier(windows, windows_lengths, common_lengths, common_gaps)

    lines = [
        "# Redacted Windows Native Admission AWDL Baseline Comparison",
        "",
        "## Source",
        "",
        f"- Baseline label: `{baseline_label}`",
        f"- Baseline summary: `{display_path(baseline_path)}`",
        f"- Windows label: `{windows_label}`",
        f"- Windows summary: `{display_path(windows_path)}`",
        "- Raw output: not included",
        "",
        "## Baseline AWDL Shape",
        "",
        f"- AWDL flow count: {len(baseline_flows)}",
        f"- Baseline payload length counts: {format_counter_top(baseline_lengths, 16)}",
        f"- Baseline small-family lengths: {format_family(baseline_lengths, APPLE_AWDL_SMALL_LENGTHS)}",
        f"- Baseline large-family lengths: {format_family(baseline_lengths, APPLE_AWDL_LARGE_LENGTHS)}",
        f"- Baseline inter-payload gap buckets: {format_counter(baseline_gaps)}",
        f"- Baseline framing first-byte classes: {format_counter(baseline_framing['first_byte_classes'])}",
        f"- Baseline framing length-prefix candidates: {format_counter(baseline_framing['length_prefix_candidates'])}",
        f"- Baseline framing TLS record-like reads: {format_counter(baseline_framing['tls_record_like'])}",
        f"- Baseline framing TLS record length matches: {format_counter(baseline_framing['tls_record_len_match'])}",
        "",
        "## Windows Read Shape",
        "",
        f"- macOS attempted advertised TCP port: {windows.get('Interpretation / macOS attempted advertised TCP port', 'missing')}",
        f"- Accepted connection summary: {windows.get('TCP Observer / Accepted connection summary', 'missing')}",
        f"- Accepted connection lines: {windows.get('TCP Observer / Accepted connection lines', 'missing')}",
        f"- Redacted peer classes: {windows.get('TCP Observer / Redacted peer classes', 'missing')}",
        f"- Connection outcomes: {windows.get('TCP Observer / Connection outcomes', 'missing')}",
        f"- Read byte counts: {format_counter(windows_lengths)}",
        f"- Read byte sequences: {windows.get('TCP Observer / Read byte sequences', 'missing')}",
        f"- Inter-read gap buckets: {format_counter(windows_gaps)}",
        f"- Framing probe enabled: {windows.get('TCP Observer / Framing probe enabled', 'missing')}",
        f"- Framing first-byte classes: {windows.get('TCP Observer / Framing first-byte classes', 'missing')}",
        f"- Framing length-prefix candidates: {windows.get('TCP Observer / Framing length-prefix candidates', 'missing')}",
        f"- Framing TLS record-like reads: {windows.get('TCP Observer / Framing TLS record-like reads', 'missing')}",
        f"- Framing shape samples: {windows.get('TCP Observer / Framing shape samples', 'missing')}",
        f"- Summary small-family hits: {windows.get('TCP Observer / Apple AWDL small-flow length hits', 'missing')}",
        f"- Summary large-family hits: {windows.get('TCP Observer / Apple AWDL large-flow length hits', 'missing')}",
        "",
        "## Comparison",
        "",
        f"- Length overlap: {format_overlap(common_lengths, baseline_lengths)}",
        f"- Gap bucket overlap: {format_overlap(common_gaps, baseline_gaps)}",
        f"- Small-family overlap count: {family_overlap_count(common_lengths, APPLE_AWDL_SMALL_LENGTHS)}",
        f"- Large-family overlap count: {family_overlap_count(common_lengths, APPLE_AWDL_LARGE_LENGTHS)}",
        f"- Framing first-byte overlap: {format_overlap(overlap_counter(windows_framing['first_byte_classes'], baseline_framing['first_byte_classes']), baseline_framing['first_byte_classes'])}",
        f"- Framing length-prefix overlap: {format_overlap(overlap_counter(windows_framing['length_prefix_candidates'], baseline_framing['length_prefix_candidates']), baseline_framing['length_prefix_candidates'])}",
        f"- Framing TLS record-like overlap: {format_overlap(overlap_counter(windows_framing['tls_record_like'], baseline_framing['tls_record_like']), baseline_framing['tls_record_like'])}",
        f"- Framing compatibility: {framing_compatibility(windows_framing, baseline_framing)}",
        f"- Evidence tier: {tier}",
        "",
        "## Notes",
        "",
        "- This report compares length and timing shapes only; it does not identify a protocol or prove admission.",
        "- Direction labels in the Apple baseline are arbitrary within each flow and are intentionally ignored here.",
        "- A session-like tier should still be paired with macOS native logs and same Apple Account/iCloud evidence before building a richer listener.",
        "- Do not commit raw peer addresses, hostnames, TXT values, TCP payload bytes, Apple Account identifiers, or credential material.",
        "",
    ]
    return "\n".join(lines)


def evidence_tier(
    windows: dict[str, str],
    windows_lengths: Counter[str],
    common_lengths: Counter[str],
    common_gaps: Counter[str],
) -> str:
    tcp_attempt = yes_value(windows.get("Interpretation / macOS attempted advertised TCP port"))
    accepted = parse_int(windows.get("TCP Observer / Accepted connection lines")) or 0
    if not tcp_attempt and accepted == 0:
        return "no_tcp_attempt"
    if not windows_lengths:
        return "tcp_attempt_no_read_data"

    small = family_overlap_count(common_lengths, APPLE_AWDL_SMALL_LENGTHS)
    large = family_overlap_count(common_lengths, APPLE_AWDL_LARGE_LENGTHS)
    if small and large and common_gaps:
        return "session_like_length_and_gap_overlap"
    if small and large:
        return "small_and_large_length_overlap"
    if small:
        return "small_length_overlap"
    if large:
        return "large_length_overlap"
    if common_lengths:
        return "other_baseline_length_overlap"
    return "no_length_overlap"


def combined_lengths(flows: list[AwdlFlow]) -> Counter[str]:
    combined: Counter[str] = Counter()
    for flow in flows:
        combined.update(flow.payload_lengths)
    return combined


def combined_gaps(flows: list[AwdlFlow]) -> Counter[str]:
    combined: Counter[str] = Counter()
    for flow in flows:
        combined.update(flow.gap_buckets)
    return combined


def combined_framing(flows: list[AwdlFlow]) -> dict[str, Counter[str]]:
    combined = {
        "first_byte_classes": Counter(),
        "length_prefix_candidates": Counter(),
        "tls_record_like": Counter(),
        "tls_record_len_match": Counter(),
    }
    for flow in flows:
        combined["first_byte_classes"].update(flow.framing_first_byte_classes)
        combined["length_prefix_candidates"].update(flow.framing_length_prefix_candidates)
        combined["tls_record_like"].update(flow.framing_tls_record_like)
        combined["tls_record_len_match"].update(flow.framing_tls_record_len_match)
    return combined


def overlap_counter(candidate: Counter[str], baseline: Counter[str]) -> Counter[str]:
    return Counter(
        {
            key: candidate[key]
            for key in sorted(set(candidate) & set(baseline), key=sort_key)
        }
    )


def framing_compatibility(
    windows_framing: dict[str, Counter[str]],
    baseline_framing: dict[str, Counter[str]],
) -> str:
    if not any(windows_framing[key] for key in windows_framing):
        return "not_observed"
    if not any(baseline_framing[key] for key in baseline_framing):
        return "baseline_framing_not_observed"
    if baseline_framing["tls_record_like"]["yes"] == 0 and windows_framing["tls_record_like"]["yes"]:
        return "tls_like_where_awdl_baseline_is_not_tls_like"
    if not overlap_counter(
        windows_framing["first_byte_classes"], baseline_framing["first_byte_classes"]
    ):
        return "no_first_byte_class_overlap"
    if overlap_counter(
        windows_framing["length_prefix_candidates"], baseline_framing["length_prefix_candidates"]
    ):
        return "framing_bucket_overlap"
    return "first_byte_class_overlap_only"


def family_overlap_count(counter: Counter[str], family: set[str]) -> int:
    return sum(counter[length] for length in family)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter, key=sort_key))


def format_counter_top(counter: Counter[str], limit: int) -> str:
    if not counter:
        return "none"
    items = sorted(counter.items(), key=lambda item: (-item[1], sort_key(item[0])))
    return ", ".join(f"`{key}`={count}" for key, count in items[:limit])


def format_family(counter: Counter[str], family: set[str]) -> str:
    return format_counter(Counter({key: counter[key] for key in family if counter[key]}))


def format_overlap(overlap: Counter[str], baseline: Counter[str]) -> str:
    if not overlap:
        return "none"
    return ", ".join(
        f"`{key}` windows={overlap[key]} baseline={baseline[key]}"
        for key in sorted(overlap, key=sort_key)
    )


def sort_key(value: str) -> tuple[int, int | str]:
    if value.isdigit():
        return (0, int(value))
    return (1, value)


def sort_length(value: str) -> int:
    return int(value) if value.isdigit() else 0


def yes_value(value: str | None) -> bool:
    return (value or "").strip().lower() == "yes"


def display_path(path: Path) -> str:
    parts = path.parts
    for marker in ("docs", "artifacts"):
        if marker in parts:
            return "/".join(parts[parts.index(marker) :])
    return path.name


if __name__ == "__main__":
    raise SystemExit(main())
