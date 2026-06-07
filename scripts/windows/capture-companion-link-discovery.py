#!/usr/bin/env python3
"""Run passive CompanionLink discovery and write redacted summaries."""

from __future__ import annotations

import argparse
import datetime as dt
import shlex
import subprocess
import sys
from pathlib import Path


DEFAULT_BASELINE = Path(
    "docs/observations/2026-06-07-redacted-macos-rust-mdns-companion-link.md"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture Windows passive CompanionLink discovery output and "
            "compare redacted Rust mDNS output with a baseline."
        )
    )
    parser.add_argument(
        "--seconds",
        type=positive_int,
        default=30,
        help="Discovery duration in seconds. Default: 30.",
    )
    parser.add_argument(
        "--backend",
        choices=["rust-mdns", "system"],
        default="rust-mdns",
        help="Discovery backend. Default: rust-mdns.",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Raw transcript path under artifacts/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Redacted summary path under docs/windows-inbox/.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Redacted baseline summary to compare against.",
    )
    parser.add_argument(
        "--compare-output",
        type=Path,
        help="Redacted comparison output path under docs/windows-inbox/.",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="Write only the discovery summary; skip baseline comparison.",
    )
    parser.add_argument(
        "--allow-unredacted-system",
        action="store_true",
        help=(
            "Permit backend=system, which cannot produce commit-safe output "
            "automatically."
        ),
    )
    parser.add_argument(
        "--print-command-only",
        action="store_true",
        help="Print the Windows discovery command and exit.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    command = build_command(args.backend, args.seconds)
    if args.print_command_only:
        print(format_command(command))
        return 0

    if args.backend == "system" and not args.allow_unredacted_system:
        parser.error("--backend system requires --allow-unredacted-system")

    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    day = now.strftime("%Y-%m-%d")
    transcript = resolve_path(
        repo_root,
        args.transcript,
        repo_root / "artifacts" / f"windows-companion-link-discovery-{stamp}.txt",
    )
    output = resolve_path(
        repo_root,
        args.output,
        repo_root
        / "docs"
        / "windows-inbox"
        / f"{day}-redacted-companion-link-discovery.md",
    )
    if output.exists() and args.output is None:
        output = (
            repo_root
            / "docs"
            / "windows-inbox"
            / f"{day}-{stamp}-redacted-companion-link-discovery.md"
        )
    compare_output = resolve_path(
        repo_root,
        args.compare_output,
        repo_root
        / "docs"
        / "windows-inbox"
        / f"{day}-redacted-companion-link-discovery-compare.md",
    )
    if compare_output.exists() and args.compare_output is None:
        compare_output = (
            repo_root
            / "docs"
            / "windows-inbox"
            / f"{day}-{stamp}-redacted-companion-link-discovery-compare.md"
        )
    baseline = resolve_path(repo_root, args.baseline, args.baseline)

    print("Passive CompanionLink discovery capture")
    print(f"Raw Windows transcript: {transcript}")
    print(f"Redacted summary output: {output}")
    if args.backend == "rust-mdns" and not args.no_compare:
        print(f"Baseline summary: {baseline}")
        print(f"Redacted comparison output: {compare_output}")
    print("\nWindows command:\n")
    print(format_command(command))
    print()

    transcript.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.backend == "rust-mdns" and not args.no_compare:
        compare_output.parent.mkdir(parents=True, exist_ok=True)

    return_code = run_and_tee(command, repo_root, transcript)
    if args.backend == "system":
        print(
            "System backend output is not automatically redacted; raw "
            "transcript was not summarized.",
            file=sys.stderr,
        )
        return return_code

    summary_code = subprocess.run(
        [
            sys.executable,
            str(
                repo_root
                / "scripts"
                / "windows"
                / "summarize-companion-link-discovery-output.py"
            ),
            str(transcript),
            "--output",
            str(output),
        ],
        cwd=repo_root,
        check=False,
    ).returncode

    print(f"Wrote redacted summary: {output}")
    compare_code = 0
    if not args.no_compare:
        compare_code = subprocess.run(
            [
                sys.executable,
                str(
                    repo_root
                    / "scripts"
                    / "windows"
                    / "compare-companion-link-discovery-summaries.py"
                ),
                str(baseline),
                str(output),
                "--before-label",
                "local-macos-rust-mdns",
                "--after-label",
                "windows-passive",
                "--output",
                str(compare_output),
            ],
            cwd=repo_root,
            check=False,
        ).returncode
        print(f"Wrote redacted comparison: {compare_output}")

    if return_code != 0:
        print(f"Windows discovery command exited with status {return_code}")
        return return_code
    if summary_code != 0:
        return summary_code
    return compare_code


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def resolve_path(repo_root: Path, value: Path | None, default: Path) -> Path:
    if value is None:
        return default
    if value.is_absolute():
        return value
    return repo_root / value


def build_command(backend: str, seconds: int) -> list[str]:
    command = [
        "cargo",
        "run",
        "--",
        "discover-companion-link",
        "--backend",
        backend,
        "--seconds",
        str(seconds),
    ]
    if backend == "rust-mdns":
        command.append("--redact")
    return command


def format_command(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def run_and_tee(command: list[str], cwd: Path, transcript: Path) -> int:
    with transcript.open("w", encoding="utf-8", errors="replace") as output:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            output.write(line)
        return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
