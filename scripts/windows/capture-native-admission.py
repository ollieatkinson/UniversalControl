#!/usr/bin/env python3
"""Run a Windows native-admission advertisement and write a redacted summary."""

from __future__ import annotations

import argparse
import datetime as dt
import shlex
import subprocess
import sys
from pathlib import Path


MODE_DEFAULTS = {
    "benign": {
        "instance": "AnyKBFlow Probe",
        "hostname": None,
        "port": 49152,
        "output_suffix": "redacted-native-admission-benign.md",
    },
    "companion-link": {
        "instance": "AnyKBFlow Native Probe",
        "hostname": "anykbflow-native-probe",
        "port": 49152,
        "output_suffix": "redacted-native-admission-companion-link.md",
    },
    "shape": {
        "instance": "AnyKBFlow Native Shape Probe",
        "hostname": "anykbflow-native-shape-probe",
        "port": 61833,
        "output_suffix": "redacted-native-admission-shape.md",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture Windows-side output for coordinated native-admission probes."
    )
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_DEFAULTS),
        default="benign",
        help="Capture mode. Default: benign.",
    )
    parser.add_argument("--seconds", type=positive_int, default=60, help="Advertise duration.")
    parser.add_argument("--instance", help="DNS-SD instance name to advertise.")
    parser.add_argument("--hostname", help="Hostname to publish where the command supports it.")
    parser.add_argument("--addr", help="Explicit IP address to publish.")
    parser.add_argument("--port", type=positive_int, help="TCP port to advertise.")
    parser.add_argument("--transcript", type=Path, help="Raw transcript path under artifacts/.")
    parser.add_argument(
        "--framing-probe",
        action="store_true",
        help="Pass --observe-framing with --observe-tcp for non-payload frame-shape hypotheses.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Redacted summary path under docs/windows-inbox/.",
    )
    parser.add_argument(
        "--awdl-baseline",
        type=Path,
        help=(
            "Apple-to-Apple AWDL baseline summary used for companion-link/shape "
            "comparison. Defaults to the committed reconnect baseline."
        ),
    )
    parser.add_argument(
        "--awdl-output",
        type=Path,
        help="Redacted AWDL comparison output path under docs/observations/.",
    )
    parser.add_argument(
        "--skip-awdl-compare",
        action="store_true",
        help="Skip the AWDL baseline comparison for companion-link/shape modes.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Start the Windows command immediately.",
    )
    parser.add_argument(
        "--print-mac-command-only",
        action="store_true",
        help="Print the matching macOS watcher command and exit.",
    )
    parser.add_argument(
        "--print-windows-command-only",
        action="store_true",
        help="Print the Windows advertisement command and exit.",
    )
    args = parser.parse_args()
    if args.framing_probe and args.mode == "benign":
        parser.error("--framing-probe requires companion-link or shape mode")

    repo_root = Path(__file__).resolve().parents[2]
    defaults = MODE_DEFAULTS[args.mode]
    instance = args.instance or defaults["instance"]
    hostname = args.hostname if args.hostname is not None else defaults["hostname"]
    port = args.port or defaults["port"]
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    day = now.strftime("%Y-%m-%d")
    transcript = resolve_path(
        repo_root,
        args.transcript,
        repo_root / "artifacts" / f"windows-native-admission-{args.mode}-{stamp}.txt",
    )
    output = resolve_path(
        repo_root,
        args.output,
        repo_root / "docs" / "windows-inbox" / f"{day}-{defaults['output_suffix']}",
    )
    if output.exists() and args.output is None:
        output = (
            repo_root
            / "docs"
            / "windows-inbox"
            / f"{day}-{stamp}-{defaults['output_suffix']}"
        )
    awdl_baseline = resolve_path(
        repo_root,
        args.awdl_baseline,
        repo_root / "docs" / "observations" / "2026-06-07-redacted-uc-session-reconnect.md",
    )
    awdl_output = resolve_path(
        repo_root,
        args.awdl_output,
        repo_root
        / "docs"
        / "observations"
        / f"{day}-redacted-native-admission-{args.mode}-awdl-compare.md",
    )
    if awdl_output.exists() and args.awdl_output is None:
        awdl_output = (
            repo_root
            / "docs"
            / "observations"
            / f"{day}-{stamp}-redacted-native-admission-{args.mode}-awdl-compare.md"
        )

    windows_command = build_windows_command(
        args.mode,
        args.seconds,
        instance,
        hostname,
        args.addr,
        port,
        args.framing_probe,
    )
    mac_command = f"./scripts/mac/capture-native-admission.sh --mode {args.mode}"

    if args.print_mac_command_only:
        print(mac_command)
        return 0
    if args.print_windows_command_only:
        print(format_command(windows_command))
        return 0

    print(f"Native admission capture mode: {args.mode}")
    print(f"Raw Windows transcript: {transcript}")
    print(f"Redacted summary output: {output}\n")
    if should_compare_awdl(args.mode, args.skip_awdl_compare):
        print(f"AWDL baseline summary: {awdl_baseline}")
        print(f"Redacted AWDL comparison output: {awdl_output}\n")
    print("Start this on macOS first:\n")
    print(mac_command)
    print("\nWindows command:\n")
    print(format_command(windows_command))
    print()

    if not args.no_prompt and sys.stdin.isatty():
        input("Press Return once the macOS capture is active...")

    transcript.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    return_code = run_and_tee(windows_command, repo_root, transcript)
    summary_code = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "windows" / "summarize-native-admission-output.py"),
            str(transcript),
            "--output",
            str(output),
        ],
        cwd=repo_root,
        check=False,
    ).returncode

    print(f"Wrote redacted summary: {output}")
    compare_code = 0
    if summary_code == 0:
        compare_code = run_awdl_comparison(
            repo_root,
            args.mode,
            args.skip_awdl_compare,
            awdl_baseline,
            output,
            awdl_output,
        )
    if return_code != 0:
        print(f"Windows advertisement command exited with status {return_code}", file=sys.stderr)
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


def build_windows_command(
    mode: str,
    seconds: int,
    instance: str,
    hostname: str | None,
    addr: str | None,
    port: int,
    framing_probe: bool,
) -> list[str]:
    if mode == "benign":
        command = [
            "cargo",
            "run",
            "--",
            "advertise-mdns",
            "--seconds",
            str(seconds),
            "--instance",
            instance,
            "--port",
            str(port),
            "--txt",
            "phase=visibility",
            "--txt",
            "role=windows-probe",
        ]
        if addr:
            command.extend(["--addr", addr])
        return command

    if mode == "companion-link":
        command = [
            "cargo",
            "run",
            "--",
            "advertise-mdns",
            "--service-type",
            "_companion-link._tcp",
            "--instance",
            instance,
            "--hostname",
            hostname or "anykbflow-native-probe",
            "--port",
            str(port),
            "--txt",
            "probe=visibility",
            "--txt",
            "role=windows-native-candidate",
            "--allow-apple-service",
            "--observe-tcp",
            "--seconds",
            str(seconds),
        ]
        if addr:
            command.extend(["--addr", addr])
        if framing_probe:
            command.append("--observe-framing")
        return command

    command = [
        "cargo",
        "run",
        "--",
        "advertise-companion-link-shape",
        "--acknowledge-shape-experiment",
        "--instance",
        instance,
        "--hostname",
        hostname or "anykbflow-native-shape-probe",
        "--port",
        str(port),
        "--observe-tcp",
        "--seconds",
        str(seconds),
    ]
    if addr:
        command.extend(["--addr", addr])
    if framing_probe:
        command.append("--observe-framing")
    return command


def should_compare_awdl(mode: str, skip_awdl_compare: bool) -> bool:
    return mode in {"companion-link", "shape"} and not skip_awdl_compare


def run_awdl_comparison(
    repo_root: Path,
    mode: str,
    skip_awdl_compare: bool,
    baseline: Path,
    windows_summary: Path,
    output: Path,
) -> int:
    if not should_compare_awdl(mode, skip_awdl_compare):
        return 0
    if not baseline.exists():
        print(f"Skipping AWDL comparison; baseline not found: {baseline}", file=sys.stderr)
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    code = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "compare-native-admission-awdl-baseline.py"),
            str(baseline),
            str(windows_summary),
            "--baseline-label",
            "apple-reconnect-awdl",
            "--windows-label",
            mode,
            "--output",
            str(output),
        ],
        cwd=repo_root,
        check=False,
    ).returncode
    if code == 0:
        print(f"Wrote redacted AWDL comparison: {output}")
    return code


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
