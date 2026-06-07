#!/usr/bin/env python3
"""Create a commit-safe summary from a macOS Universal Control session artifact."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


NATIVE_PROCESSES = ("UniversalControl", "rapportd", "mDNSResponder", "nearbyd", "wifip2pd")
KNOWN_PACKET_PORTS = ("3722", "5353")
TCPDUMP_TIMEOUT_SECONDS = 30


@dataclass
class BrowseEvent:
    action: str
    flags: str
    interface: str
    domain: str
    service_type: str
    instance: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize artifacts from scripts/mac/capture-uc-session.sh without leaking identifiers."
    )
    parser.add_argument("artifact_dir", type=Path, help="Artifact directory under artifacts/")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown summary to this path instead of stdout.",
    )
    args = parser.parse_args()

    if not args.artifact_dir.is_dir():
        parser.error(f"artifact directory not found: {args.artifact_dir}")

    summary = render_summary(args.artifact_dir)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


def render_summary(artifact_dir: Path) -> str:
    metadata = parse_readme(read_file(artifact_dir / "README.txt"))
    companion_events = parse_browse(read_file(artifact_dir / "companion-link-browse.txt"))
    universalcontrol_events = parse_browse(read_file(artifact_dir / "universalcontrol-browse.txt"))
    log_counts = summarize_logs(read_file(artifact_dir / "unified-log.txt"))
    lsof_before = summarize_lsof(read_file(artifact_dir / "lsof-network-before.txt"))
    lsof_after = summarize_lsof(read_file(artifact_dir / "lsof-network-after.txt"))
    launchd = {
        "ensemble_before": parse_launchctl(read_file(artifact_dir / "launchctl-ensemble-before.txt")),
        "ensemble_after": parse_launchctl(read_file(artifact_dir / "launchctl-ensemble-after.txt")),
        "rapportd_before": parse_launchctl(read_file(artifact_dir / "launchctl-rapportd-before.txt")),
        "rapportd_after": parse_launchctl(read_file(artifact_dir / "launchctl-rapportd-after.txt")),
    }
    pcap_summary = summarize_pcaps(artifact_dir)

    lines = [
        "# Redacted macOS Universal Control Session Summary",
        "",
        "## Source",
        "",
        f"- Artifact: `{artifact_dir.name}`",
        f"- Created: {metadata.get('created', 'unknown')}",
        f"- Duration: {metadata.get('duration', 'unknown')}",
        f"- tcpdump enabled: {metadata.get('tcpdump', 'unknown')}",
        f"- tcpdump interface count: {metadata.get('interface_count', '0')}",
        f"- Raw output: not included",
        "",
        "## Action Timeline",
        "",
        "- Timeline source: artifact README",
        "- Idle before edge push: expected",
        "- Edge push: expected",
        "- Pointer movement on target: expected",
        "- Harmless key press: expected",
        "- Scroll: expected",
        "- Return to local: expected",
        "- Idle after return: expected",
        "",
        "## DNS-SD Browse",
        "",
        "### _companion-link._tcp",
        "",
    ]
    lines.extend(render_browse_summary(companion_events))
    lines.extend(["", "### _universalcontrol._tcp", ""])
    lines.extend(render_browse_summary(universalcontrol_events))

    lines.extend(["", "## Unified Log", ""])
    lines.extend(
        [
            f"- Total captured lines: {log_counts['total']}",
            f"- UniversalControl lines: {log_counts['UniversalControl']}",
            f"- rapportd lines: {log_counts['rapportd']}",
            f"- mDNSResponder lines: {log_counts['mDNSResponder']}",
            f"- nearbyd lines: {log_counts['nearbyd']}",
            f"- wifip2pd lines: {log_counts['wifip2pd']}",
            f"- Discovery keyword lines: {log_counts['discovery_keywords']}",
            f"- Session/control keyword lines: {log_counts['session_keywords']}",
            f"- Input/action keyword lines: {log_counts['input_keywords']}",
            f"- Error/rejection keyword lines: {log_counts['error_keywords']}",
            f"- UniversalControl/rapportd discovery keyword lines: {log_counts['native_discovery_keywords']}",
            f"- UniversalControl/rapportd session/control keyword lines: {log_counts['native_session_keywords']}",
            f"- UniversalControl/rapportd input/action keyword lines: {log_counts['native_input_keywords']}",
            f"- UniversalControl/rapportd error/rejection keyword lines: {log_counts['native_error_keywords']}",
            f"- Native stream keyword lines: {log_counts['native_stream_keywords']}",
            f"- Native target/input keyword lines: {log_counts['native_target_keywords']}",
            f"- Native sync/layout keyword lines: {log_counts['native_sync_layout_keywords']}",
            f"- Proximity/ranging keyword lines: {log_counts['proximity_keywords']}",
            f"- Native/proximity-process proximity keyword lines: {log_counts['native_proximity_keywords']}",
            f"- Wi-Fi peer-to-peer/AWDL keyword lines: {log_counts['p2p_transport_keywords']}",
            f"- Native/transport-process Wi-Fi P2P keyword lines: {log_counts['native_p2p_transport_keywords']}",
            "- Raw log lines: not included",
        ]
    )

    lines.extend(["", "## Network Snapshot", ""])
    lines.extend(["### Before", ""])
    lines.extend(render_lsof_summary(lsof_before))
    lines.extend(["", "### After", ""])
    lines.extend(render_lsof_summary(lsof_after))

    lines.extend(["", "## Packet Capture", ""])
    lines.extend(
        [
            f"- pcap files: {pcap_summary['count']}",
            f"- total pcap bytes: {pcap_summary['bytes']}",
            f"- pcap byte sizes: {format_counter(pcap_summary['sizes'])}",
            f"- pcap capture classes: {format_counter(pcap_summary['capture_classes'])}",
            f"- tcpdump packet decode: {pcap_summary['decode_status']}",
            f"- decoded packet lines: {pcap_summary['decoded_packets']}",
            f"- packet counts by capture class: {format_counter(pcap_summary['packet_capture_classes'])}",
            f"- IP version counts: {format_counter(pcap_summary['ip_versions'])}",
            f"- transport counts: {format_counter(pcap_summary['transports'])}",
            f"- protocol-relevant port hits: {format_counter(pcap_summary['known_ports'])}",
            f"- pcap decode failures: {pcap_summary['decode_failures']}",
            "- raw packet data: not included",
            "- raw endpoints and dynamic ports: not included",
        ]
    )

    lines.extend(["", "## Launchd", ""])
    lines.extend(
        [
            f"- UniversalControl before: {format_launchd(launchd['ensemble_before'])}",
            f"- UniversalControl after: {format_launchd(launchd['ensemble_after'])}",
            f"- rapportd before: {format_launchd(launchd['rapportd_before'])}",
            f"- rapportd after: {format_launchd(launchd['rapportd_after'])}",
        ]
    )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- CompanionLink browse observed: {format_bool(bool(companion_events))}",
            f"- Universal Control DNS-SD browse observed: {format_bool(bool(universalcontrol_events))}",
            f"- UniversalControl/rapportd session signal: {session_signal(log_counts)}",
            f"- Target/input negotiation signal: {target_signal(log_counts)}",
            f"- Proximity or Wi-Fi P2P side-channel signal: {side_channel_signal(log_counts)}",
            "- Notes:",
            "  - Fill this section manually after inspecting local raw artifacts.",
            "  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, or unified-log lines.",
            "",
        ]
    )
    return "\n".join(lines)


def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_readme(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("Created: "):
            metadata["created"] = line.removeprefix("Created: ").strip()
        elif line.startswith("Duration: "):
            metadata["duration"] = line.removeprefix("Duration: ").strip()
        elif line.startswith("tcpdump: "):
            metadata["tcpdump"] = line.removeprefix("tcpdump: ").strip()
        elif line.startswith("interfaces: "):
            interfaces = line.removeprefix("interfaces: ").strip()
            metadata["interface_count"] = "0" if interfaces == "none" else str(len(interfaces.split()))
    return metadata


def parse_browse(text: str) -> list[BrowseEvent]:
    events: list[BrowseEvent] = []
    pattern = re.compile(
        r"^\d{1,2}:\d{2}:\d{2}\.\d+\s+"
        r"(?P<action>Add|Rmv)\s+"
        r"(?P<flags>\d+)\s+"
        r"(?P<interface>\d+)\s+"
        r"(?P<domain>\S+)\s+"
        r"(?P<service_type>\S+)\s+"
        r"(?P<instance>.+?)\s*$"
    )
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            events.append(BrowseEvent(**match.groupdict()))
    return events


def render_browse_summary(events: list[BrowseEvent]) -> list[str]:
    if not events:
        return ["- Events: none observed"]
    added = [event for event in events if event.action.lower() == "add"]
    removed = [event for event in events if event.action.lower() != "add"]
    return [
        f"- Add events: {len(added)}",
        f"- Remove events: {len(removed)}",
        f"- Service types: {format_set(event.service_type for event in events)}",
        f"- Instance lengths: {format_set(str(len(event.instance)) for event in added)}",
        f"- Interface count: {len({event.interface for event in events})}",
    ]


def summarize_logs(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    discovery_pattern = re.compile(r"companion|_companion-link|dnsservice|browse|resolve|matching", re.I)
    session_pattern = re.compile(r"clink|p2p|direct|stream|target|ready|focus|session|edge|control message", re.I)
    input_pattern = re.compile(r"hid|keyboard|key|pointer|mouse|scroll|drag|pasteboard|event", re.I)
    error_pattern = re.compile(r"reject|den(?:y|ied)|fail(?:ed|ure)?|(?<!no)error|invalid|refus|timeout", re.I)
    stream_pattern = re.compile(r"RPStreamServer|P2PStream|P2PDirectLink|Accept Stream|Prepare Stream", re.I)
    target_pattern = re.compile(
        r"FocusMove|FocusReset|TargetBegin|TargetConnect|TargetReady|TargetEvent|"
        r"TargetReply|Target Reply|Keyboard Reports|Pointing Reports|HID accumulation",
        re.I,
    )
    sync_layout_pattern = re.compile(
        r"Initial Sync|Create Message|Send Message|Receive Message|Received Message|"
        r"Remote Display Layout|Remote Source Device|Remote Connected Devices|"
        r"Remote Synced Devices|Reset Remote|Connected Devices Clock",
        re.I,
    )
    proximity_pattern = re.compile(
        r"nearby|proximity|ranging|NISession|NINearby|Bluetooth|\bBLE\b|\bUWB\b",
        re.I,
    )
    p2p_transport_pattern = re.compile(
        r"AWDL|WiFiP2P|wifip2p|peer[- ]to[- ]peer|P2PDirectLink|P2PStream",
        re.I,
    )
    for line in text.splitlines():
        if not line or line.startswith("$ ") or line.startswith("Filtering ") or line.startswith("Timestamp "):
            continue
        counts["total"] += 1
        native_session_process = "UniversalControl" in line or "rapportd" in line
        native_proximity_process = native_session_process or "nearbyd" in line
        native_p2p_transport_process = native_session_process or "wifip2pd" in line
        for process in NATIVE_PROCESSES:
            if process in line:
                counts[process] += 1
        signal_text = log_signal_text(line)
        if discovery_pattern.search(signal_text):
            counts["discovery_keywords"] += 1
            if native_session_process:
                counts["native_discovery_keywords"] += 1
        if session_pattern.search(signal_text):
            counts["session_keywords"] += 1
            if native_session_process:
                counts["native_session_keywords"] += 1
        if input_pattern.search(signal_text):
            counts["input_keywords"] += 1
            if native_session_process:
                counts["native_input_keywords"] += 1
        if error_pattern.search(signal_text):
            counts["error_keywords"] += 1
            if native_session_process:
                counts["native_error_keywords"] += 1
        if stream_pattern.search(signal_text) and native_session_process:
            counts["native_stream_keywords"] += 1
        if target_pattern.search(signal_text) and native_session_process:
            counts["native_target_keywords"] += 1
        if sync_layout_pattern.search(signal_text) and native_session_process:
            counts["native_sync_layout_keywords"] += 1
        if proximity_pattern.search(signal_text):
            counts["proximity_keywords"] += 1
            if native_proximity_process:
                counts["native_proximity_keywords"] += 1
        if p2p_transport_pattern.search(signal_text):
            counts["p2p_transport_keywords"] += 1
            if native_p2p_transport_process:
                counts["native_p2p_transport_keywords"] += 1
    return counts


def log_signal_text(line: str) -> str:
    text = line
    for process in NATIVE_PROCESSES:
        text = text.replace(process, "")
    return text


def summarize_lsof(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        if not line or line.startswith("$ "):
            continue
        if not (line.startswith("rapportd") or line.startswith("UniversalControl")):
            continue
        counts["total"] += 1
        if line.startswith("rapportd"):
            counts["rapportd"] += 1
        if line.startswith("UniversalControl"):
            counts["UniversalControl"] += 1
        if " TCP " in line:
            counts["tcp"] += 1
        if " UDP " in line:
            counts["udp"] += 1
        state_match = re.search(r"\(([^)]+)\)\s*$", line)
        if state_match:
            counts[f"state:{state_match.group(1)}"] += 1
        if ":3722" in line:
            counts["known_port:3722"] += 1
        if ":5353" in line:
            counts["known_port:5353"] += 1
    return counts


def render_lsof_summary(counts: Counter[str]) -> list[str]:
    if not counts["total"]:
        return ["- Entries: none observed"]
    state_counts = Counter({key.removeprefix("state:"): value for key, value in counts.items() if key.startswith("state:")})
    known_ports = Counter(
        {key.removeprefix("known_port:"): value for key, value in counts.items() if key.startswith("known_port:")}
    )
    return [
        f"- Entries: {counts['total']}",
        f"- rapportd entries: {counts['rapportd']}",
        f"- UniversalControl entries: {counts['UniversalControl']}",
        f"- TCP entries: {counts['tcp']}",
        f"- UDP entries: {counts['udp']}",
        f"- TCP states: {format_counter(state_counts)}",
        f"- Known Apple ports seen: {format_counter(known_ports)}",
        "- Raw endpoints and dynamic ports: not included",
    ]


def summarize_pcaps(artifact_dir: Path) -> dict[str, object]:
    sizes: Counter[str] = Counter()
    capture_classes: Counter[str] = Counter()
    packet_capture_classes: Counter[str] = Counter()
    ip_versions: Counter[str] = Counter()
    transports: Counter[str] = Counter()
    known_ports: Counter[str] = Counter()
    total_bytes = 0
    decoded_packets = 0
    decode_failures = 0
    tcpdump = shutil.which("tcpdump")
    pcaps = sorted(artifact_dir.glob("*.pcap"))
    for pcap in pcaps:
        size = pcap.stat().st_size
        total_bytes += size
        sizes[str(size)] += 1
        capture_class = pcap_capture_class(pcap)
        capture_classes[capture_class] += 1
        if tcpdump is None:
            continue
        result = decode_pcap_lines(tcpdump, pcap)
        if result is None:
            decode_failures += 1
            continue
        decoded_packets += len(result)
        packet_capture_classes[capture_class] += len(result)
        for line in result:
            count_packet_shape(line, ip_versions, transports, known_ports)
    decode_status = "not attempted"
    if pcaps and tcpdump is None:
        decode_status = "tcpdump unavailable"
    elif pcaps:
        decode_status = "ok" if not decode_failures else "partial"
    return {
        "count": len(pcaps),
        "bytes": total_bytes,
        "sizes": sizes,
        "capture_classes": capture_classes,
        "decode_status": decode_status,
        "decoded_packets": decoded_packets,
        "packet_capture_classes": packet_capture_classes,
        "ip_versions": ip_versions,
        "transports": transports,
        "known_ports": known_ports,
        "decode_failures": decode_failures,
    }


def pcap_capture_class(path: Path) -> str:
    name = path.stem.lower()
    if "awdl" in name:
        return "awdl"
    return "primary-network"


def decode_pcap_lines(tcpdump: str, path: Path) -> list[str] | None:
    try:
        result = subprocess.run(
            [tcpdump, "-nn", "-tttt", "-r", str(path)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=TCPDUMP_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line.strip()]


def count_packet_shape(
    line: str,
    ip_versions: Counter[str],
    transports: Counter[str],
    known_ports: Counter[str],
) -> None:
    if " IP6 " in line:
        ip_versions["ipv6"] += 1
    elif " IP " in line:
        ip_versions["ipv4"] += 1

    if " UDP," in line or " UDP " in line:
        transports["udp"] += 1
    if " Flags [" in line:
        transports["tcp"] += 1

    for port in KNOWN_PACKET_PORTS:
        if packet_line_mentions_port(line, port):
            known_ports[port] += 1


def packet_line_mentions_port(line: str, port: str) -> bool:
    return re.search(rf"\.{re.escape(port)}(?:[ >:,]|$)", line) is not None


def parse_launchctl(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("state = "):
            result["state"] = stripped.removeprefix("state = ").strip()
        elif stripped.startswith("runs = "):
            result["runs"] = stripped.removeprefix("runs = ").strip()
    return result


def format_launchd(value: dict[str, str]) -> str:
    if not value:
        return "missing"
    return f"state={value.get('state', 'unknown')} runs={value.get('runs', 'unknown')}"


def session_signal(log_counts: Counter[str]) -> str:
    native_lines = log_counts["UniversalControl"] + log_counts["rapportd"]
    deeper_signal = (
        log_counts["native_stream_keywords"]
        or log_counts["native_sync_layout_keywords"]
    )
    if deeper_signal:
        return "stream or sync/layout signal in redacted counts; inspect raw local artifacts"
    if log_counts["native_session_keywords"] or log_counts["native_input_keywords"]:
        return "possible signal in redacted counts; inspect raw local artifacts"
    if native_lines:
        return "native process logs present, no session/input keywords counted"
    return "no UniversalControl or rapportd lines counted"


def target_signal(log_counts: Counter[str]) -> str:
    if log_counts["native_target_keywords"]:
        return "target/input negotiation signal in redacted counts; inspect raw local artifacts"
    if log_counts["native_input_keywords"]:
        return "generic input/action keywords counted without target-state templates"
    return "no native target/input keywords counted"


def side_channel_signal(log_counts: Counter[str]) -> str:
    if log_counts["native_proximity_keywords"] or log_counts["native_p2p_transport_keywords"]:
        return "possible proximity or Wi-Fi peer-to-peer signal in redacted counts"
    if log_counts["proximity_keywords"] or log_counts["p2p_transport_keywords"]:
        return "only generic proximity or Wi-Fi peer-to-peer keywords counted"
    if log_counts["nearbyd"] or log_counts["wifip2pd"]:
        return "nearbyd or wifip2pd logs present without counted protocol keywords"
    return "no nearbyd or wifip2pd lines counted"


def format_set(values) -> str:
    unique = sorted({str(value) for value in values if str(value)})
    if not unique:
        return "none"
    return ", ".join(f"`{value}`" for value in unique)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
