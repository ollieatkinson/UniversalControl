#!/usr/bin/env python3
"""Capture normalized AnyKBFlow input events and write a redacted summary."""

from __future__ import annotations

import argparse
import datetime as dt
import shlex
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture listen-events/grab-events output for native input validation."
    )
    parser.add_argument(
        "--mode",
        choices=["listen", "grab", "grab-suppress"],
        default="listen",
        help="Capture mode. Default: listen.",
    )
    parser.add_argument("--count", type=positive_int, default=20, help="Event count to capture.")
    parser.add_argument("--jsonl", type=Path, help="JSONL event output path under artifacts/.")
    parser.add_argument("--transcript", type=Path, help="Raw transcript path under artifacts/.")
    parser.add_argument("--output", type=Path, help="Redacted summary output path.")
    parser.add_argument(
        "--route-config",
        type=Path,
        help="Run probe route-events with this input-owner config after capture.",
    )
    parser.add_argument(
        "--route-transcript",
        type=Path,
        help="Raw route-events transcript path under artifacts/.",
    )
    parser.add_argument(
        "--expect-activation",
        action="store_true",
        help="Route gate: require at least one remote activation.",
    )
    parser.add_argument(
        "--expect-deactivation",
        action="store_true",
        help="Route gate: require at least one remote deactivation.",
    )
    parser.add_argument(
        "--min-forwarded-inputs",
        type=non_negative_int,
        default=0,
        help="Route gate: require at least this many forwarded input messages.",
    )
    parser.add_argument(
        "--dry-run-replay",
        action="store_true",
        help="Run replay-events --dry-run against the captured JSONL after capture.",
    )
    parser.add_argument(
        "--print-command-only",
        action="store_true",
        help="Print the capture command and exit.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    command = build_command(args.mode, args.count)
    if args.print_command_only:
        print(format_command(command))
        return 0

    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    day = now.strftime("%Y-%m-%d")
    jsonl = resolve_path(
        repo_root,
        args.jsonl,
        repo_root / "artifacts" / f"input-events-{args.mode}-{stamp}.jsonl",
    )
    transcript = resolve_path(
        repo_root,
        args.transcript,
        repo_root / "artifacts" / f"input-events-{args.mode}-{stamp}.log",
    )
    route_transcript = resolve_path(
        repo_root,
        args.route_transcript,
        repo_root / "artifacts" / f"input-events-{args.mode}-{stamp}-route.log",
    )
    output = resolve_path(
        repo_root,
        args.output,
        repo_root / "docs" / "windows-inbox" / f"{day}-redacted-input-events-{args.mode}.md",
    )
    if output.exists() and args.output is None:
        output = (
            repo_root
            / "docs"
            / "windows-inbox"
            / f"{day}-{stamp}-redacted-input-events-{args.mode}.md"
        )

    print("AnyKBFlow input event capture")
    print(f"Mode: {args.mode}")
    print(f"JSONL events: {jsonl}")
    print(f"Raw transcript: {transcript}")
    print(f"Redacted summary output: {output}")
    if args.route_config:
        print(f"Route config: {resolve_path(repo_root, args.route_config, args.route_config)}")
        print(f"Route transcript: {route_transcript}")
    print(f"Command: {format_command(command)}\n")

    jsonl.parent.mkdir(parents=True, exist_ok=True)
    transcript.parent.mkdir(parents=True, exist_ok=True)
    route_transcript.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    return_code = run_capture(command, repo_root, jsonl, transcript)
    summary_code = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "summarize-input-events.py"),
            str(jsonl),
            "--output",
            str(output),
        ],
        cwd=repo_root,
        check=False,
    ).returncode

    if args.route_config and return_code == 0:
        route_config = resolve_path(repo_root, args.route_config, args.route_config)
        route_code = run_logged(
            build_route_command(
                route_config,
                jsonl,
                args.expect_activation,
                args.expect_deactivation,
                args.min_forwarded_inputs,
            ),
            repo_root,
            route_transcript,
        )
    else:
        route_code = 0

    if args.dry_run_replay and return_code == 0 and route_code == 0:
        replay_code = run_logged(
            [
                "cargo",
                "run",
                "--",
                "probe",
                "replay-events",
                "--path",
                str(jsonl),
                "--dry-run",
            ],
            cwd=repo_root,
            transcript=None,
        )
    else:
        replay_code = 0

    print(f"Wrote normalized events: {jsonl}")
    print(f"Wrote redacted summary: {output}")
    if args.route_config:
        print(f"Wrote route transcript: {route_transcript}")
    if return_code != 0:
        print(f"Capture command exited with status {return_code}", file=sys.stderr)
        return return_code
    if summary_code != 0:
        return summary_code
    if route_code != 0:
        return route_code
    return replay_code


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def build_command(mode: str, count: int) -> list[str]:
    if mode == "listen":
        return ["cargo", "run", "--", "probe", "listen-events", "--count", str(count)]
    command = ["cargo", "run", "--", "probe", "grab-events", "--count", str(count)]
    if mode == "grab-suppress":
        command.append("--suppress")
    return command


def build_route_command(
    config: Path,
    jsonl: Path,
    expect_activation: bool,
    expect_deactivation: bool,
    min_forwarded_inputs: int,
) -> list[str]:
    command = [
        "cargo",
        "run",
        "--",
        "--config",
        str(config),
        "probe",
        "route-events",
        "--path",
        str(jsonl),
    ]
    if expect_activation:
        command.append("--expect-activation")
    if expect_deactivation:
        command.append("--expect-deactivation")
    if min_forwarded_inputs:
        command.extend(["--min-forwarded-inputs", str(min_forwarded_inputs)])
    return command


def resolve_path(repo_root: Path, value: Path | None, default: Path) -> Path:
    if value is None:
        return default
    if value.is_absolute():
        return value
    return repo_root / value


def format_command(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def run_capture(command: list[str], cwd: Path, jsonl: Path, transcript: Path) -> int:
    with (
        jsonl.open("w", encoding="utf-8", errors="replace") as events_out,
        transcript.open("w", encoding="utf-8", errors="replace") as transcript_out,
    ):
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
            transcript_out.write(line)
            if line.lstrip().startswith("{"):
                events_out.write(line)
        return process.wait()


def run_logged(
    command: list[str],
    cwd: Path,
    transcript: Path | None,
) -> int:
    print(f"\nCommand: {format_command(command)}")
    if transcript is None:
        return subprocess.run(command, cwd=cwd, check=False).returncode

    transcript.parent.mkdir(parents=True, exist_ok=True)
    with transcript.open("w", encoding="utf-8", errors="replace") as transcript_out:
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
            transcript_out.write(line)
        return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
