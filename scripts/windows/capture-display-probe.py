#!/usr/bin/env python3
"""Capture Windows display probe output and write a redacted summary."""

from __future__ import annotations

import argparse
import datetime as dt
import shlex
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture native Windows display geometry for AnyUniversalControl calibration."
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
        "--print-command-only",
        action="store_true",
        help="Print the display probe command and exit.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    command = ["cargo", "run", "--", "probe", "displays"]
    if args.print_command_only:
        print(format_command(command))
        return 0

    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    day = now.strftime("%Y-%m-%d")
    transcript = resolve_path(
        repo_root,
        args.transcript,
        repo_root / "artifacts" / f"windows-display-probe-{stamp}.txt",
    )
    output = resolve_path(
        repo_root,
        args.output,
        repo_root / "docs" / "windows-inbox" / f"{day}-redacted-display-probe.md",
    )
    if output.exists() and args.output is None:
        output = (
            repo_root
            / "docs"
            / "windows-inbox"
            / f"{day}-{stamp}-redacted-display-probe.md"
        )

    print("Windows display probe capture")
    print(f"Raw transcript: {transcript}")
    print(f"Redacted summary output: {output}")
    print(f"Command: {format_command(command)}\n")

    transcript.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    return_code = run_and_tee(command, repo_root, transcript)
    summary_code = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "windows" / "summarize-display-probe-output.py"),
            str(transcript),
            "--output",
            str(output),
        ],
        cwd=repo_root,
        check=False,
    ).returncode

    print(f"Wrote redacted summary: {output}")
    if return_code != 0:
        print(f"Display probe command exited with status {return_code}", file=sys.stderr)
        return return_code
    return summary_code


def resolve_path(repo_root: Path, value: Path | None, default: Path) -> Path:
    if value is None:
        return default
    if value.is_absolute():
        return value
    return repo_root / value


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
