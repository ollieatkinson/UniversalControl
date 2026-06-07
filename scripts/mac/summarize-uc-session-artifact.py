#!/usr/bin/env python3
"""Create a commit-safe summary from a macOS Universal Control session artifact."""

from __future__ import annotations

import argparse
import ipaddress
import math
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


NATIVE_PROCESSES = ("UniversalControl", "rapportd", "mDNSResponder", "nearbyd", "wifip2pd")
KNOWN_PACKET_PORTS = ("3722", "5353")
TCPDUMP_TIMEOUT_SECONDS = 30
PCAP_LINKTYPE_ETHERNET = 1
PAYLOAD_BURST_GAP_SECONDS = 0.250
INITIAL_PAYLOAD_BURST_LIMIT = 12
PHASE_WINDOW_SECONDS = 2.0
PHASE_WINDOW_BURST_LIMIT = 4


@dataclass
class BrowseEvent:
    action: str
    flags: str
    interface: str
    domain: str
    service_type: str
    instance: str


@dataclass(frozen=True)
class PacketRecord:
    timestamp: datetime
    ip_version: str
    transport: str
    source_host: str
    source_port: str
    destination_host: str
    destination_port: str
    rest: str


@dataclass(frozen=True)
class PcapPayloadRecord:
    ip_version: str
    source_host: str
    source_port: str
    destination_host: str
    destination_port: str
    payload: bytes


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
    unified_log_text = read_file(artifact_dir / "unified-log.txt")
    log_counts = summarize_logs(unified_log_text)
    phase_signals = summarize_session_phase_signals(unified_log_text)
    lsof_before = summarize_lsof(read_file(artifact_dir / "lsof-network-before.txt"))
    lsof_after = summarize_lsof(read_file(artifact_dir / "lsof-network-after.txt"))
    launchd = {
        "ensemble_before": parse_launchctl(read_file(artifact_dir / "launchctl-ensemble-before.txt")),
        "ensemble_after": parse_launchctl(read_file(artifact_dir / "launchctl-ensemble-after.txt")),
        "rapportd_before": parse_launchctl(read_file(artifact_dir / "launchctl-rapportd-before.txt")),
        "rapportd_after": parse_launchctl(read_file(artifact_dir / "launchctl-rapportd-after.txt")),
    }
    pcap_summary = summarize_pcaps(artifact_dir, phase_signals)

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
    lines.extend(["", "## Session Phase Signals", ""])
    lines.extend(render_session_phase_signals(phase_signals))

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
            f"- TCP flow counts by capture class: {format_counter(pcap_summary['tcp_flow_capture_classes'])}",
            f"- TCP payload bytes by capture class: {format_counter(pcap_summary['tcp_payload_bytes_by_capture'])}",
            f"- TCP payload frame-shape packets by capture class: {format_counter(pcap_summary['tcp_payload_shape_packets_by_capture'])}",
            f"- mDNS service mentions: {format_counter(pcap_summary['mdns_service_mentions'])}",
            f"- pcap decode failures: {pcap_summary['decode_failures']}",
            f"- pcap frame-shape decode failures: {pcap_summary['tcp_payload_shape_decode_failures']}",
            f"- phase-window burst radius: +/-{PHASE_WINDOW_SECONDS:.1f}s around redacted session phase offsets",
            "- raw packet data: not included",
            "- raw endpoints and dynamic ports: not included",
        ]
    )
    lines.extend(["", "### AWDL TCP Flow Shapes", ""])
    lines.extend(render_tcp_flow_shapes(pcap_summary["awdl_tcp_flows"]))
    lines.extend(["", "### Primary Network TCP Flow Shapes", ""])
    lines.extend(render_tcp_flow_shapes(pcap_summary["primary_network_tcp_flows"]))

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
        ]
    )
    lines.extend(
        render_interpretation_notes(
            metadata,
            log_counts,
            phase_signals,
            pcap_summary,
        )
    )
    lines.append("")
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


def summarize_session_phase_signals(text: str) -> dict[str, object]:
    counters: Counter[str] = Counter()
    offsets: dict[str, list[float]] = {
        "connected": [],
        "disconnect": [],
        "connected_links_empty": [],
        "connected_links_present": [],
        "target_connect": [],
    }
    first_time: datetime | None = None
    for line in text.splitlines():
        timestamp = parse_log_timestamp(line)
        if timestamp is None:
            continue
        first_time = min_timestamp(first_time, timestamp)
        offset = seconds_between(first_time, timestamp)
        assert offset is not None
        signal_text = log_signal_text(line)

        if "UniversalControl" not in line and "rapportd" not in line:
            continue
        if (
            ("Disconnected" not in signal_text)
            and ("Connected links changed:" not in signal_text)
            and re.search(r": Connected\b|Accepting \(Connected\)", signal_text)
        ):
            counters["connected_events"] += 1
            offsets["connected"].append(offset)
        if "Disconnected" in signal_text or "XPC: Disconnect" in signal_text:
            counters["disconnect_events"] += 1
            offsets["disconnect"].append(offset)
        if "Connected links changed:" in signal_text:
            if " to []" in signal_text:
                counters["connected_links_empty_transitions"] += 1
                offsets["connected_links_empty"].append(offset)
            else:
                counters["connected_links_present_transitions"] += 1
                offsets["connected_links_present"].append(offset)
        if "Sync Connected Devices" in signal_text:
            counters["sync_connected_devices_updates"] += 1
        if "TargetBegin" in signal_text or "Target Begin" in signal_text:
            counters["target_begin_events"] += 1
        if "TargetReady" in signal_text or "Target Ready" in signal_text:
            counters["target_ready_events"] += 1
        if "Target Reply: Accept" in signal_text or "TargetReply status=1" in signal_text:
            counters["target_accept_events"] += 1
        if "TargetConnect message" in signal_text:
            counters["target_connect_messages"] += 1
            offsets["target_connect"].append(offset)
        if "FocusMove pointer=true" in signal_text:
            counters["pointer_focus_moves"] += 1
        if "FocusMove pointer=false keyFocus=true" in signal_text:
            counters["keyboard_focus_moves"] += 1
        if "Reset Remote Pointing Reports" in signal_text:
            counters["remote_pointing_resets"] += 1
        if "Reset Remote Keyboard Reports" in signal_text:
            counters["remote_keyboard_resets"] += 1

    return {
        "counters": counters,
        "first_connected_offset": first_offset(offsets["connected"]),
        "first_disconnect_offset": first_offset(offsets["disconnect"]),
        "first_reconnect_after_disconnect_offset": first_reconnect_after_disconnect_offset(offsets),
        "first_target_connect_offset": first_offset(offsets["target_connect"]),
    }


def parse_log_timestamp(line: str) -> datetime | None:
    match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)\s", line)
    if not match:
        return None
    return datetime.fromisoformat(match.group(1))


def first_offset(values: list[float]) -> float | None:
    return min(values) if values else None


def first_reconnect_after_disconnect_offset(offsets: dict[str, list[float]]) -> float | None:
    disconnect = first_offset(offsets["disconnect"])
    if disconnect is None:
        return None
    candidates = [
        *offsets["connected"],
        *offsets["connected_links_present"],
        *offsets["target_connect"],
    ]
    later = [offset for offset in candidates if offset > disconnect]
    return min(later) if later else None


def render_session_phase_signals(signals: dict[str, object]) -> list[str]:
    counters = signals["counters"]
    assert isinstance(counters, Counter)
    return [
        f"- Connected event lines: {counters['connected_events']}",
        f"- Disconnect event lines: {counters['disconnect_events']}",
        f"- Connected-link empty transitions: {counters['connected_links_empty_transitions']}",
        f"- Connected-link present transitions: {counters['connected_links_present_transitions']}",
        f"- Sync connected-devices updates: {counters['sync_connected_devices_updates']}",
        f"- Target begin events: {counters['target_begin_events']}",
        f"- Target ready events: {counters['target_ready_events']}",
        f"- Target accept/reply events: {counters['target_accept_events']}",
        f"- TargetConnect message lines: {counters['target_connect_messages']}",
        f"- Pointer focus move lines: {counters['pointer_focus_moves']}",
        f"- Keyboard focus move lines: {counters['keyboard_focus_moves']}",
        f"- Remote pointing reset lines: {counters['remote_pointing_resets']}",
        f"- Remote keyboard reset lines: {counters['remote_keyboard_resets']}",
        f"- First connected offset: {format_seconds(signals['first_connected_offset'])}",
        f"- First TargetConnect offset: {format_seconds(signals['first_target_connect_offset'])}",
        f"- First disconnect offset: {format_seconds(signals['first_disconnect_offset'])}",
        f"- First reconnect-after-disconnect offset: {format_seconds(signals['first_reconnect_after_disconnect_offset'])}",
        "- Raw session IDs, device IDs, and log lines: not included",
    ]


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


def summarize_pcaps(
    artifact_dir: Path,
    phase_signals: dict[str, object],
) -> dict[str, object]:
    sizes: Counter[str] = Counter()
    capture_classes: Counter[str] = Counter()
    packet_capture_classes: Counter[str] = Counter()
    ip_versions: Counter[str] = Counter()
    transports: Counter[str] = Counter()
    known_ports: Counter[str] = Counter()
    tcp_flow_capture_classes: Counter[str] = Counter()
    tcp_payload_bytes_by_capture: Counter[str] = Counter()
    tcp_payload_shape_packets_by_capture: Counter[str] = Counter()
    mdns_service_mentions: Counter[str] = Counter()
    tcp_flows: dict[tuple[str, tuple[tuple[str, str], tuple[str, str]]], dict[str, object]] = {}
    total_bytes = 0
    decoded_packets = 0
    decode_failures = 0
    payload_shape_decode_failures = 0
    first_packet_time: datetime | None = None
    last_packet_time: datetime | None = None
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
            record = parse_packet_record(line)
            if record is None:
                continue
            first_packet_time = min_timestamp(first_packet_time, record.timestamp)
            last_packet_time = max_timestamp(last_packet_time, record.timestamp)
            count_packet_shape(record, ip_versions, transports, known_ports)
            count_mdns_service_mentions(record.rest, mdns_service_mentions)
            if record.transport == "tcp":
                update_tcp_flow(
                    tcp_flows,
                    capture_class,
                    record,
                    tcp_flow_capture_classes,
                    tcp_payload_bytes_by_capture,
                )
        payload_records = parse_pcap_tcp_payloads(pcap)
        if payload_records is None:
            payload_shape_decode_failures += 1
        else:
            tcp_payload_shape_packets_by_capture[capture_class] += len(payload_records)
            for payload_record in payload_records:
                update_tcp_flow_framing(tcp_flows, capture_class, payload_record)
    finalize_tcp_flow_bursts(tcp_flows)
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
        "tcp_flow_capture_classes": tcp_flow_capture_classes,
        "tcp_payload_bytes_by_capture": tcp_payload_bytes_by_capture,
        "tcp_payload_shape_packets_by_capture": tcp_payload_shape_packets_by_capture,
        "tcp_payload_shape_decode_failures": payload_shape_decode_failures,
        "mdns_service_mentions": mdns_service_mentions,
        "awdl_tcp_flows": top_tcp_flow_shapes(
            tcp_flows,
            first_packet_time,
            phase_signals,
            capture_class="awdl",
        ),
        "primary_network_tcp_flows": top_tcp_flow_shapes(
            tcp_flows,
            first_packet_time,
            phase_signals,
            capture_class="primary-network",
        ),
        "packet_span": seconds_between(first_packet_time, last_packet_time),
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


def parse_pcap_tcp_payloads(path: Path) -> list[PcapPayloadRecord] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24:
        return None

    magic = data[:4]
    if magic in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1"):
        endian = "<"
    elif magic in (b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d"):
        endian = ">"
    else:
        return None

    try:
        linktype = int.from_bytes(data[20:24], endian_byteorder(endian))
    except ValueError:
        return None
    if linktype != PCAP_LINKTYPE_ETHERNET:
        return None

    records: list[PcapPayloadRecord] = []
    offset = 24
    while offset + 16 <= len(data):
        try:
            incl_len = int.from_bytes(data[offset + 8 : offset + 12], endian_byteorder(endian))
        except ValueError:
            return None
        offset += 16
        packet = data[offset : offset + incl_len]
        if len(packet) != incl_len:
            return None
        offset += incl_len
        payload_record = parse_ethernet_tcp_payload(packet)
        if payload_record is not None and payload_record.payload:
            records.append(payload_record)
    return records


def endian_byteorder(endian: str) -> str:
    return "little" if endian == "<" else "big"


def parse_ethernet_tcp_payload(packet: bytes) -> PcapPayloadRecord | None:
    if len(packet) < 14:
        return None
    offset = 14
    ethertype = int.from_bytes(packet[12:14], "big")
    if ethertype in {0x8100, 0x88A8}:
        if len(packet) < 18:
            return None
        ethertype = int.from_bytes(packet[16:18], "big")
        offset = 18

    if ethertype == 0x0800:
        return parse_ipv4_tcp_payload(packet, offset)
    if ethertype == 0x86DD:
        return parse_ipv6_tcp_payload(packet, offset)
    return None


def parse_ipv4_tcp_payload(packet: bytes, offset: int) -> PcapPayloadRecord | None:
    if len(packet) < offset + 20:
        return None
    version = packet[offset] >> 4
    header_len = (packet[offset] & 0x0F) * 4
    if version != 4 or header_len < 20:
        return None
    total_len = int.from_bytes(packet[offset + 2 : offset + 4], "big")
    if len(packet) < offset + total_len or total_len < header_len:
        return None
    protocol = packet[offset + 9]
    if protocol != 6:
        return None
    source_host = str(ipaddress.ip_address(packet[offset + 12 : offset + 16]))
    destination_host = str(ipaddress.ip_address(packet[offset + 16 : offset + 20]))
    tcp_offset = offset + header_len
    segment_end = offset + total_len
    return parse_tcp_segment(packet, tcp_offset, segment_end, "ipv4", source_host, destination_host)


def parse_ipv6_tcp_payload(packet: bytes, offset: int) -> PcapPayloadRecord | None:
    if len(packet) < offset + 40:
        return None
    version = packet[offset] >> 4
    if version != 6:
        return None
    payload_len = int.from_bytes(packet[offset + 4 : offset + 6], "big")
    next_header = packet[offset + 6]
    source_host = str(ipaddress.ip_address(packet[offset + 8 : offset + 24]))
    destination_host = str(ipaddress.ip_address(packet[offset + 24 : offset + 40]))
    cursor = offset + 40
    segment_end = cursor + payload_len
    if len(packet) < segment_end:
        return None

    while next_header in {0, 43, 44, 50, 51, 60} and cursor < segment_end:
        if next_header == 44:
            if cursor + 8 > segment_end:
                return None
            next_header = packet[cursor]
            cursor += 8
            continue
        if next_header == 51:
            if cursor + 2 > segment_end:
                return None
            header_len = (packet[cursor + 1] + 2) * 4
        else:
            if cursor + 2 > segment_end:
                return None
            header_len = (packet[cursor + 1] + 1) * 8
        if cursor + header_len > segment_end:
            return None
        next_header = packet[cursor]
        cursor += header_len

    if next_header != 6:
        return None
    return parse_tcp_segment(packet, cursor, segment_end, "ipv6", source_host, destination_host)


def parse_tcp_segment(
    packet: bytes,
    tcp_offset: int,
    segment_end: int,
    ip_version: str,
    source_host: str,
    destination_host: str,
) -> PcapPayloadRecord | None:
    if segment_end < tcp_offset + 20 or len(packet) < segment_end:
        return None
    source_port = str(int.from_bytes(packet[tcp_offset : tcp_offset + 2], "big"))
    destination_port = str(int.from_bytes(packet[tcp_offset + 2 : tcp_offset + 4], "big"))
    header_len = (packet[tcp_offset + 12] >> 4) * 4
    if header_len < 20 or tcp_offset + header_len > segment_end:
        return None
    payload = packet[tcp_offset + header_len : segment_end]
    return PcapPayloadRecord(
        ip_version=ip_version,
        source_host=source_host,
        source_port=source_port,
        destination_host=destination_host,
        destination_port=destination_port,
        payload=payload,
    )


def parse_packet_record(line: str) -> PacketRecord | None:
    prefix_match = re.match(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?) (?P<version>IP6|IP) (?P<body>.+)$",
        line,
    )
    if not prefix_match:
        return None
    body = prefix_match.group("body")
    source, separator, remainder = body.partition(" > ")
    if not separator:
        return None
    destination, separator, rest = remainder.partition(": ")
    if not separator:
        return None
    source_host, source_port = split_endpoint(source)
    destination_host, destination_port = split_endpoint(destination)
    transport = packet_transport(rest, source_port, destination_port)
    return PacketRecord(
        timestamp=datetime.fromisoformat(prefix_match.group("timestamp")),
        ip_version="ipv6" if prefix_match.group("version") == "IP6" else "ipv4",
        transport=transport,
        source_host=source_host,
        source_port=source_port,
        destination_host=destination_host,
        destination_port=destination_port,
        rest=rest,
    )


def split_endpoint(value: str) -> tuple[str, str]:
    host, separator, port = value.rpartition(".")
    if separator and port.isdigit():
        return host, port
    return value, ""


def packet_transport(rest: str, source_port: str, destination_port: str) -> str:
    if "Flags [" in rest:
        return "tcp"
    if source_port in KNOWN_PACKET_PORTS or destination_port in KNOWN_PACKET_PORTS:
        return "udp"
    return "unknown"


def min_timestamp(current: datetime | None, candidate: datetime) -> datetime:
    if current is None or candidate < current:
        return candidate
    return current


def max_timestamp(current: datetime | None, candidate: datetime) -> datetime:
    if current is None or candidate > current:
        return candidate
    return current


def count_packet_shape(
    record: PacketRecord,
    ip_versions: Counter[str],
    transports: Counter[str],
    known_ports: Counter[str],
) -> None:
    ip_versions[record.ip_version] += 1

    transports[record.transport] += 1

    for port in KNOWN_PACKET_PORTS:
        if record.source_port == port or record.destination_port == port:
            known_ports[port] += 1


def count_mdns_service_mentions(text: str, mentions: Counter[str]) -> None:
    for service in re.findall(r"_[A-Za-z0-9-]+\._tcp\.local\.", text):
        mentions[service] += 1


def update_tcp_flow(
    tcp_flows: dict[tuple[str, tuple[tuple[str, str], tuple[str, str]]], dict[str, object]],
    capture_class: str,
    record: PacketRecord,
    tcp_flow_capture_classes: Counter[str],
    tcp_payload_bytes_by_capture: Counter[str],
) -> None:
    endpoints = tuple(
        sorted(
            (
                (record.source_host, record.source_port),
                (record.destination_host, record.destination_port),
            )
        )
    )
    key = (capture_class, endpoints)
    flow = tcp_flows.setdefault(
        key,
        {
            "capture_class": capture_class,
            "ip_version": record.ip_version,
            "endpoint_classes": tuple(sorted((host_class(record.source_host), host_class(record.destination_host)))),
            "port_classes": tuple(sorted((port_class(record.source_port), port_class(record.destination_port)))),
            "packets": 0,
            "payload_bytes": 0,
            "nonzero_payload_packets": 0,
            "max_payload_bytes": 0,
            "endpoints": endpoints,
            "payload_packets_by_direction": Counter(),
            "payload_bytes_by_direction": Counter(),
            "payload_lengths_by_direction": {
                "a_to_b": Counter(),
                "b_to_a": Counter(),
            },
            "payload_gap_buckets": Counter(),
            "initial_payload_sequence": [],
            "last_payload_time": None,
            "payload_burst_count": 0,
            "payload_burst_packet_buckets": Counter(),
            "payload_burst_byte_buckets": Counter(),
            "payload_burst_duration_buckets": Counter(),
            "payload_burst_idle_gap_buckets": Counter(),
            "payload_burst_direction_patterns": Counter(),
            "payload_burst_length_fingerprints": Counter(),
            "initial_payload_bursts": [],
            "payload_bursts": [],
            "current_payload_burst": None,
            "framing_first_byte_classes": Counter(),
            "framing_length_prefix_candidates": Counter(),
            "framing_tls_record_like": Counter(),
            "framing_tls_record_len_match": Counter(),
            "framing_ascii_ratios": Counter(),
            "framing_high_ratios": Counter(),
            "framing_zero_ratios": Counter(),
            "framing_control_ratios": Counter(),
            "framing_entropy_buckets": Counter(),
            "framing_byte_diversity_buckets": Counter(),
            "initial_framing_samples": [],
            "first_time": record.timestamp,
            "last_time": record.timestamp,
            "flags": Counter(),
        },
    )
    payload_length = packet_payload_length(record.rest)
    flow["packets"] = int(flow["packets"]) + 1
    flow["payload_bytes"] = int(flow["payload_bytes"]) + payload_length
    if payload_length:
        flow["nonzero_payload_packets"] = int(flow["nonzero_payload_packets"]) + 1
        update_flow_payload_sequence(flow, endpoints, record, payload_length)
    flow["max_payload_bytes"] = max(int(flow["max_payload_bytes"]), payload_length)
    flow["first_time"] = min(flow["first_time"], record.timestamp)
    flow["last_time"] = max(flow["last_time"], record.timestamp)
    flow["flags"].update(tcp_flag_classes(record.rest, payload_length))
    tcp_flow_capture_classes[capture_class] += 1 if int(flow["packets"]) == 1 else 0
    tcp_payload_bytes_by_capture[capture_class] += payload_length


def update_tcp_flow_framing(
    tcp_flows: dict[tuple[str, tuple[tuple[str, str], tuple[str, str]]], dict[str, object]],
    capture_class: str,
    record: PcapPayloadRecord,
) -> None:
    endpoints = tuple(
        sorted(
            (
                (record.source_host, record.source_port),
                (record.destination_host, record.destination_port),
            )
        )
    )
    flow = tcp_flows.get((capture_class, endpoints))
    if flow is None:
        return

    shape = frame_shape_fields(record.payload)
    increment_counter_field(flow, "framing_first_byte_classes", shape["first_byte_class"])
    increment_counter_field(flow, "framing_tls_record_like", shape["tls_record_like"])
    increment_counter_field(flow, "framing_tls_record_len_match", shape["tls_record_len_match"])
    increment_counter_field(flow, "framing_ascii_ratios", shape["ascii_ratio"])
    increment_counter_field(flow, "framing_high_ratios", shape["high_ratio"])
    increment_counter_field(flow, "framing_zero_ratios", shape["zero_ratio"])
    increment_counter_field(flow, "framing_control_ratios", shape["control_ratio"])
    increment_counter_field(flow, "framing_entropy_buckets", shape["entropy_bucket"])
    increment_counter_field(flow, "framing_byte_diversity_buckets", shape["byte_diversity_bucket"])

    prefix_counter = flow["framing_length_prefix_candidates"]
    assert isinstance(prefix_counter, Counter)
    for candidate in shape["length_prefix_candidates"].split("|"):
        prefix_counter[candidate] += 1

    samples = flow["initial_framing_samples"]
    assert isinstance(samples, list)
    if len(samples) < 12:
        samples.append(shape)


def increment_counter_field(flow: dict[str, object], key: str, value: str) -> None:
    counter = flow[key]
    assert isinstance(counter, Counter)
    counter[value] += 1


def update_flow_payload_sequence(
    flow: dict[str, object],
    endpoints: tuple[tuple[str, str], tuple[str, str]],
    record: PacketRecord,
    payload_length: int,
) -> None:
    direction = "a_to_b" if (record.source_host, record.source_port) == endpoints[0] else "b_to_a"

    payload_packets_by_direction = flow["payload_packets_by_direction"]
    assert isinstance(payload_packets_by_direction, Counter)
    payload_packets_by_direction[direction] += 1

    payload_bytes_by_direction = flow["payload_bytes_by_direction"]
    assert isinstance(payload_bytes_by_direction, Counter)
    payload_bytes_by_direction[direction] += payload_length

    payload_lengths_by_direction = flow["payload_lengths_by_direction"]
    assert isinstance(payload_lengths_by_direction, dict)
    payload_lengths = payload_lengths_by_direction[direction]
    assert isinstance(payload_lengths, Counter)
    payload_lengths[str(payload_length)] += 1

    last_payload_time = flow["last_payload_time"]
    if isinstance(last_payload_time, datetime):
        gap = seconds_between(last_payload_time, record.timestamp)
        if gap is not None:
            payload_gap_buckets = flow["payload_gap_buckets"]
            assert isinstance(payload_gap_buckets, Counter)
            payload_gap_buckets[payload_gap_bucket(gap)] += 1
    flow["last_payload_time"] = record.timestamp

    initial_payload_sequence = flow["initial_payload_sequence"]
    assert isinstance(initial_payload_sequence, list)
    if len(initial_payload_sequence) < 24:
        initial_payload_sequence.append(
            {
                "direction": direction,
                "length": payload_length,
            }
        )
    update_flow_payload_burst(flow, direction, payload_length, record.timestamp)


def update_flow_payload_burst(
    flow: dict[str, object],
    direction: str,
    payload_length: int,
    timestamp: datetime,
) -> None:
    current = flow.get("current_payload_burst")
    if not isinstance(current, dict):
        flow["current_payload_burst"] = new_payload_burst(direction, payload_length, timestamp)
        return

    end_time = current.get("end_time")
    gap = seconds_between(end_time if isinstance(end_time, datetime) else None, timestamp)
    if gap is not None and gap >= PAYLOAD_BURST_GAP_SECONDS:
        idle_gaps = flow["payload_burst_idle_gap_buckets"]
        assert isinstance(idle_gaps, Counter)
        idle_gaps[payload_burst_idle_gap_bucket(gap)] += 1
        finalize_payload_burst(flow, current)
        flow["current_payload_burst"] = new_payload_burst(direction, payload_length, timestamp)
        return

    current["end_time"] = timestamp
    current["packets"] = int(current["packets"]) + 1
    current["bytes"] = int(current["bytes"]) + payload_length
    directions = current["directions"]
    assert isinstance(directions, Counter)
    directions[direction] += 1
    lengths = current["lengths"]
    assert isinstance(lengths, Counter)
    lengths[str(payload_length)] += 1


def new_payload_burst(
    direction: str,
    payload_length: int,
    timestamp: datetime,
) -> dict[str, object]:
    return {
        "start_time": timestamp,
        "end_time": timestamp,
        "packets": 1,
        "bytes": payload_length,
        "directions": Counter({direction: 1}),
        "lengths": Counter({str(payload_length): 1}),
    }


def finalize_tcp_flow_bursts(
    tcp_flows: dict[tuple[str, tuple[tuple[str, str], tuple[str, str]]], dict[str, object]],
) -> None:
    for flow in tcp_flows.values():
        current = flow.get("current_payload_burst")
        if isinstance(current, dict):
            finalize_payload_burst(flow, current)
            flow["current_payload_burst"] = None


def finalize_payload_burst(flow: dict[str, object], burst: dict[str, object]) -> None:
    packets = int(burst.get("packets", 0) or 0)
    bytes_total = int(burst.get("bytes", 0) or 0)
    start_time = burst.get("start_time")
    end_time = burst.get("end_time")
    duration = seconds_between(
        start_time if isinstance(start_time, datetime) else None,
        end_time if isinstance(end_time, datetime) else None,
    )
    directions = burst.get("directions")
    lengths = burst.get("lengths")
    if not isinstance(directions, Counter):
        directions = Counter()
    if not isinstance(lengths, Counter):
        lengths = Counter()

    flow["payload_burst_count"] = int(flow["payload_burst_count"]) + 1
    packet_buckets = flow["payload_burst_packet_buckets"]
    assert isinstance(packet_buckets, Counter)
    packet_buckets[payload_burst_packet_bucket(packets)] += 1

    byte_buckets = flow["payload_burst_byte_buckets"]
    assert isinstance(byte_buckets, Counter)
    byte_buckets[payload_burst_byte_bucket(bytes_total)] += 1

    duration_buckets = flow["payload_burst_duration_buckets"]
    assert isinstance(duration_buckets, Counter)
    duration_buckets[payload_burst_duration_bucket(duration)] += 1

    pattern = payload_burst_direction_pattern(directions)
    direction_patterns = flow["payload_burst_direction_patterns"]
    assert isinstance(direction_patterns, Counter)
    direction_patterns[pattern] += 1

    fingerprints = flow["payload_burst_length_fingerprints"]
    assert isinstance(fingerprints, Counter)
    fingerprints[payload_burst_length_fingerprint(lengths)] += 1

    initial_bursts = flow["initial_payload_bursts"]
    assert isinstance(initial_bursts, list)
    all_bursts = flow["payload_bursts"]
    assert isinstance(all_bursts, list)
    burst_record = {
        "index": len(all_bursts) + 1,
        "start_time": start_time,
        "end_time": end_time,
        "packets": packets,
        "bytes": bytes_total,
        "direction_pattern": pattern,
        "lengths": lengths,
    }
    all_bursts.append(burst_record)
    if len(initial_bursts) < INITIAL_PAYLOAD_BURST_LIMIT:
        initial_bursts.append(burst_record)


def payload_burst_packet_bucket(packets: int) -> str:
    if packets <= 1:
        return "1"
    if packets == 2:
        return "2"
    if packets <= 5:
        return "3-5"
    if packets <= 20:
        return "6-20"
    if packets <= 100:
        return "21-100"
    return ">100"


def payload_burst_byte_bucket(bytes_total: int) -> str:
    if bytes_total <= 128:
        return "1-128"
    if bytes_total <= 512:
        return "129-512"
    if bytes_total <= 2048:
        return "513-2048"
    if bytes_total <= 16384:
        return "2049-16384"
    return ">16384"


def payload_burst_duration_bucket(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    if seconds < 0.010:
        return "<10ms"
    if seconds < 0.100:
        return "10-100ms"
    if seconds < 1.000:
        return "100ms-1s"
    if seconds < 5.000:
        return "1-5s"
    return ">=5s"


def payload_burst_idle_gap_bucket(seconds: float) -> str:
    if seconds < 1.000:
        return "250ms-1s"
    if seconds < 5.000:
        return "1-5s"
    if seconds < 15.000:
        return "5-15s"
    return ">=15s"


def payload_burst_direction_pattern(directions: Counter[str]) -> str:
    has_a_to_b = directions["a_to_b"] > 0
    has_b_to_a = directions["b_to_a"] > 0
    if has_a_to_b and has_b_to_a:
        return "bidirectional"
    if has_a_to_b:
        return "a_to_b_only"
    if has_b_to_a:
        return "b_to_a_only"
    return "unknown"


def payload_burst_length_fingerprint(lengths: Counter[str]) -> str:
    if not lengths:
        return "none"
    parts = [f"{length}x{count}" for length, count in sorted(lengths.items(), key=lambda item: (-item[1], sort_key(item[0])))[:4]]
    return "+".join(parts)


def payload_gap_bucket(seconds: float) -> str:
    if seconds < 0.001:
        return "<1ms"
    if seconds < 0.010:
        return "1-10ms"
    if seconds < 0.100:
        return "10-100ms"
    if seconds < 1.000:
        return "100ms-1s"
    return ">=1s"


def frame_shape_fields(payload: bytes) -> dict[str, str]:
    classes = byte_class_counts(payload)
    tls_record_like, tls_record_len_match = tls_record_shape(payload)
    return {
        "first_byte_class": first_byte_class(payload),
        "ascii_ratio": ratio_bucket(classes["ascii"], len(payload)),
        "high_ratio": ratio_bucket(classes["high"], len(payload)),
        "zero_ratio": ratio_bucket(classes["zero"], len(payload)),
        "control_ratio": ratio_bucket(classes["control"], len(payload)),
        "entropy_bucket": entropy_bucket(payload),
        "byte_diversity_bucket": byte_diversity_bucket(payload),
        "length_prefix_candidates": "|".join(length_prefix_candidates(payload)) or "none",
        "tls_record_like": format_bool(tls_record_like),
        "tls_record_len_match": format_bool(tls_record_len_match),
    }


def byte_class_counts(payload: bytes) -> Counter[str]:
    counts: Counter[str] = Counter()
    for byte in payload:
        if byte == 0:
            counts["zero"] += 1
        elif byte in {9, 10, 13} or 0x20 <= byte <= 0x7E:
            counts["ascii"] += 1
        elif 0x01 <= byte <= 0x1F or byte == 0x7F:
            counts["control"] += 1
        else:
            counts["high"] += 1
    return counts


def first_byte_class(payload: bytes) -> str:
    if not payload:
        return "none"
    byte = payload[0]
    if byte == 0:
        return "zero"
    if byte in {9, 10, 13}:
        return "ascii-whitespace"
    if 0x20 <= byte <= 0x7E:
        return "ascii"
    if 0x01 <= byte <= 0x1F or byte == 0x7F:
        return "control"
    return "high"


def ratio_bucket(count: int, total: int) -> str:
    if total == 0 or count == 0:
        return "0pct"
    if count == total:
        return "100pct"
    percent = count * 100 // total
    if percent <= 9:
        return "1-9pct"
    if percent <= 49:
        return "10-49pct"
    if percent <= 89:
        return "50-89pct"
    return "90-99pct"


def entropy_bucket(payload: bytes) -> str:
    if not payload:
        return "empty"
    counts = Counter(payload)
    total = len(payload)
    entropy = 0.0
    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    if entropy < 2.0:
        return "0-2bits"
    if entropy < 4.0:
        return "2-4bits"
    if entropy < 6.0:
        return "4-6bits"
    if entropy < 7.0:
        return "6-7bits"
    return "7-8bits"


def byte_diversity_bucket(payload: bytes) -> str:
    if not payload:
        return "empty"
    unique = len(set(payload))
    if unique == 1:
        return "1"
    if unique <= 4:
        return "2-4"
    if unique <= 16:
        return "5-16"
    if unique <= 64:
        return "17-64"
    if unique <= 128:
        return "65-128"
    return "129-256"


def length_prefix_candidates(payload: bytes) -> list[str]:
    candidates: list[str] = []
    if len(payload) >= 2:
        push_length_matches(candidates, "be16", int.from_bytes(payload[0:2], "big"), 2, len(payload))
        push_length_matches(
            candidates,
            "le16",
            int.from_bytes(payload[0:2], "little"),
            2,
            len(payload),
        )
    if len(payload) >= 4:
        push_length_matches(candidates, "be32", int.from_bytes(payload[0:4], "big"), 4, len(payload))
        push_length_matches(
            candidates,
            "le32",
            int.from_bytes(payload[0:4], "little"),
            4,
            len(payload),
        )
    return candidates


def push_length_matches(
    candidates: list[str],
    endian: str,
    value: int,
    prefix_bytes: int,
    total_bytes: int,
) -> None:
    if value == total_bytes:
        candidates.append(f"{endian}_total")
    if value + prefix_bytes == total_bytes:
        candidates.append(f"{endian}_payload")


def tls_record_shape(payload: bytes) -> tuple[bool, bool]:
    if len(payload) < 5:
        return False, False
    content_type = 0x14 <= payload[0] <= 0x18
    version = payload[1] == 0x03 and payload[2] <= 0x04
    payload_len = int.from_bytes(payload[3:5], "big")
    record_like = content_type and version
    return record_like, record_like and payload_len + 5 == len(payload)


def host_class(host: str) -> str:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return "name-or-unknown"
    if address.is_multicast:
        if str(address) in {"224.0.0.251", "ff02::fb"}:
            return "mdns-multicast"
        return "multicast"
    if address.is_loopback:
        return "loopback"
    if address.is_link_local:
        return "link-local-v6" if address.version == 6 else "link-local-v4"
    if address.is_private:
        return "private-v6" if address.version == 6 else "private-v4"
    return "public-v6" if address.version == 6 else "public-v4"


def port_class(port: str) -> str:
    if not port.isdigit():
        return "unknown"
    value = int(port)
    if value == 5353:
        return "mdns"
    if value == 3722:
        return "companionlink-udp"
    if value == 7000:
        return "apple-media-7000"
    if value == 443:
        return "https"
    if value == 80:
        return "http"
    if value >= 49152:
        return "dynamic"
    if value >= 1024:
        return "registered"
    return "well-known"


def packet_payload_length(rest: str) -> int:
    match = re.search(r"length (\d+)", rest)
    if not match:
        return 0
    return int(match.group(1))


def tcp_flag_classes(rest: str, payload_length: int) -> Counter[str]:
    flags = Counter()
    match = re.search(r"Flags \[([^\]]+)\]", rest)
    if not match:
        return flags
    raw = match.group(1)
    if "S" in raw:
        flags["syn"] += 1
    if "F" in raw:
        flags["fin"] += 1
    if "R" in raw:
        flags["rst"] += 1
    if "P" in raw:
        flags["push"] += 1
    if "W" in raw:
        flags["ecn-cwr"] += 1
    if "." in raw and payload_length == 0 and not any(flag in raw for flag in "SFRP"):
        flags["ack-only"] += 1
    return flags


def top_tcp_flow_shapes(
    tcp_flows: dict[tuple[str, tuple[tuple[str, str], tuple[str, str]]], dict[str, object]],
    first_packet_time: datetime | None,
    phase_signals: dict[str, object],
    *,
    capture_class: str,
    limit: int = 5,
) -> list[dict[str, object]]:
    flows = [flow for flow in tcp_flows.values() if flow["capture_class"] == capture_class]
    flows.sort(key=lambda flow: (int(flow["payload_bytes"]), int(flow["packets"])), reverse=True)
    result: list[dict[str, object]] = []
    for flow in flows[:limit]:
        first_time = flow["first_time"]
        last_time = flow["last_time"]
        result.append(
            {
                "ip_version": flow["ip_version"],
                "endpoint_classes": flow["endpoint_classes"],
                "port_classes": flow["port_classes"],
                "packets": flow["packets"],
                "payload_bytes": flow["payload_bytes"],
                "nonzero_payload_packets": flow["nonzero_payload_packets"],
                "max_payload_bytes": flow["max_payload_bytes"],
                "payload_packets_by_direction": flow["payload_packets_by_direction"],
                "payload_bytes_by_direction": flow["payload_bytes_by_direction"],
                "payload_lengths_by_direction": flow["payload_lengths_by_direction"],
                "payload_gap_buckets": flow["payload_gap_buckets"],
                "initial_payload_sequence": flow["initial_payload_sequence"],
                "payload_burst_count": flow["payload_burst_count"],
                "payload_burst_packet_buckets": flow["payload_burst_packet_buckets"],
                "payload_burst_byte_buckets": flow["payload_burst_byte_buckets"],
                "payload_burst_duration_buckets": flow["payload_burst_duration_buckets"],
                "payload_burst_idle_gap_buckets": flow["payload_burst_idle_gap_buckets"],
                "payload_burst_direction_patterns": flow["payload_burst_direction_patterns"],
                "payload_burst_length_fingerprints": flow["payload_burst_length_fingerprints"],
                "initial_payload_bursts": initial_payload_bursts(
                    flow["initial_payload_bursts"], first_packet_time
                ),
                "phase_window_payload_bursts": phase_window_payload_bursts(
                    flow["payload_bursts"],
                    first_packet_time,
                    phase_signals,
                ),
                "framing_first_byte_classes": flow["framing_first_byte_classes"],
                "framing_length_prefix_candidates": flow["framing_length_prefix_candidates"],
                "framing_tls_record_like": flow["framing_tls_record_like"],
                "framing_tls_record_len_match": flow["framing_tls_record_len_match"],
                "framing_ascii_ratios": flow["framing_ascii_ratios"],
                "framing_high_ratios": flow["framing_high_ratios"],
                "framing_zero_ratios": flow["framing_zero_ratios"],
                "framing_control_ratios": flow["framing_control_ratios"],
                "framing_entropy_buckets": flow["framing_entropy_buckets"],
                "framing_byte_diversity_buckets": flow["framing_byte_diversity_buckets"],
                "initial_framing_samples": flow["initial_framing_samples"],
                "flags": flow["flags"],
                "first_offset": seconds_between(first_packet_time, first_time),
                "last_offset": seconds_between(first_packet_time, last_time),
                "span": seconds_between(first_time, last_time),
            }
        )
    return result


def seconds_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return max(0.0, (end - start).total_seconds())


def render_tcp_flow_shapes(flows: list[dict[str, object]]) -> list[str]:
    if not flows:
        return ["- none observed"]
    lines: list[str] = []
    for index, flow in enumerate(flows, start=1):
        lines.append(
            "- "
            + f"#{index}: "
            + f"ip={flow['ip_version']} "
            + f"endpoints={format_pair(flow['endpoint_classes'])} "
            + f"ports={format_pair(flow['port_classes'])} "
            + f"packets={flow['packets']} "
            + f"payload_bytes={flow['payload_bytes']} "
            + f"nonzero_payload_packets={flow['nonzero_payload_packets']} "
            + f"max_payload_bytes={flow['max_payload_bytes']} "
            + f"flags={format_counter(flow['flags'])} "
            + f"first_offset={format_seconds(flow['first_offset'])} "
            + f"last_offset={format_seconds(flow['last_offset'])} "
            + f"span={format_seconds(flow['span'])}"
        )
        lines.append(
            "  - payload directions: "
            + format_payload_directions(
                flow["payload_packets_by_direction"],
                flow["payload_bytes_by_direction"],
                flow["payload_lengths_by_direction"],
            )
        )
        lines.append(
            "  - initial nonzero payload sequence: "
            + format_payload_sequence(flow["initial_payload_sequence"])
        )
        lines.append(
            "  - inter-payload gap buckets: "
            + format_counter(flow["payload_gap_buckets"])
        )
        lines.append(f"  - payload burst count: {flow['payload_burst_count']}")
        lines.append(
            "  - payload burst packet buckets: "
            + format_counter(flow["payload_burst_packet_buckets"])
        )
        lines.append(
            "  - payload burst byte buckets: "
            + format_counter(flow["payload_burst_byte_buckets"])
        )
        lines.append(
            "  - payload burst duration buckets: "
            + format_counter(flow["payload_burst_duration_buckets"])
        )
        lines.append(
            "  - payload burst idle gap buckets: "
            + format_counter(flow["payload_burst_idle_gap_buckets"])
        )
        lines.append(
            "  - payload burst direction patterns: "
            + format_counter(flow["payload_burst_direction_patterns"])
        )
        lines.append(
            "  - payload burst length fingerprints: "
            + format_top_counter(flow["payload_burst_length_fingerprints"], limit=8)
        )
        lines.append(
            "  - initial payload bursts: "
            + format_initial_payload_bursts(flow["initial_payload_bursts"])
        )
        lines.append(
            "  - phase-window payload bursts: "
            + format_phase_window_payload_bursts(flow["phase_window_payload_bursts"])
        )
        lines.append(
            "  - framing first-byte classes: "
            + format_counter(flow["framing_first_byte_classes"])
        )
        lines.append(
            "  - framing byte-class ratios: "
            + format_framing_ratios(
                flow["framing_ascii_ratios"],
                flow["framing_high_ratios"],
                flow["framing_zero_ratios"],
                flow["framing_control_ratios"],
            )
        )
        lines.append(
            "  - framing entropy buckets: "
            + format_counter(flow["framing_entropy_buckets"])
        )
        lines.append(
            "  - framing byte-diversity buckets: "
            + format_counter(flow["framing_byte_diversity_buckets"])
        )
        lines.append(
            "  - framing length-prefix candidates: "
            + format_counter(flow["framing_length_prefix_candidates"])
        )
        lines.append(
            "  - framing TLS record-like reads: "
            + format_counter(flow["framing_tls_record_like"])
        )
        lines.append(
            "  - framing TLS record length matches: "
            + format_counter(flow["framing_tls_record_len_match"])
        )
        lines.append(
            "  - initial framing samples: "
            + format_framing_samples(flow["initial_framing_samples"])
        )
    lines.append("- Raw endpoints, dynamic ports, and packet payloads: not included")
    return lines


def format_payload_directions(
    packet_counter: object,
    byte_counter: object,
    length_counters: object,
) -> str:
    if not isinstance(packet_counter, Counter) or not isinstance(byte_counter, Counter):
        return "unknown"
    if not isinstance(length_counters, dict):
        return "unknown"
    parts: list[str] = []
    for direction in ("a_to_b", "b_to_a"):
        length_counter = length_counters.get(direction)
        if not isinstance(length_counter, Counter):
            length_counter = Counter()
        parts.append(
            f"`{direction}` packets={packet_counter[direction]} "
            f"bytes={byte_counter[direction]} "
            f"top_lengths={format_top_counter(length_counter, limit=6)}"
        )
    return "; ".join(parts)


def format_payload_sequence(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    rendered: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        direction = item.get("direction", "unknown")
        length = item.get("length", "unknown")
        rendered.append(f"`{direction}:{length}`")
    return ", ".join(rendered) if rendered else "none"


def initial_payload_bursts(value: object, first_packet_time: datetime | None) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    bursts: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        lengths = item.get("lengths")
        bursts.append(
            {
                "start_offset": seconds_between(
                    first_packet_time,
                    start_time if isinstance(start_time, datetime) else None,
                ),
                "end_offset": seconds_between(
                    first_packet_time,
                    end_time if isinstance(end_time, datetime) else None,
                ),
                "packets": item.get("packets", "unknown"),
                "bytes": item.get("bytes", "unknown"),
                "direction_pattern": item.get("direction_pattern", "unknown"),
                "length_fingerprint": payload_burst_length_fingerprint(lengths if isinstance(lengths, Counter) else Counter()),
            }
        )
    return bursts


def phase_window_payload_bursts(
    bursts: object,
    first_packet_time: datetime | None,
    phase_signals: dict[str, object],
) -> list[dict[str, object]]:
    if not isinstance(bursts, list) or not bursts:
        return []
    phase_windows = session_phase_windows(phase_signals)
    if not phase_windows:
        return []

    matches: list[dict[str, object]] = []
    for phase_name, phase_offset in phase_windows:
        phase_matches = []
        for burst in bursts:
            if not isinstance(burst, dict):
                continue
            start_time = burst.get("start_time")
            end_time = burst.get("end_time")
            start_offset = seconds_between(
                first_packet_time,
                start_time if isinstance(start_time, datetime) else None,
            )
            end_offset = seconds_between(
                first_packet_time,
                end_time if isinstance(end_time, datetime) else None,
            )
            if not burst_overlaps_phase_window(start_offset, end_offset, phase_offset):
                continue
            lengths = burst.get("lengths")
            phase_matches.append(
                {
                    "phase": phase_name,
                    "phase_offset": phase_offset,
                    "burst_index": burst.get("index", "unknown"),
                    "start_offset": start_offset,
                    "end_offset": end_offset,
                    "packets": burst.get("packets", "unknown"),
                    "bytes": burst.get("bytes", "unknown"),
                    "direction_pattern": burst.get("direction_pattern", "unknown"),
                    "length_fingerprint": payload_burst_length_fingerprint(
                        lengths if isinstance(lengths, Counter) else Counter()
                    ),
                }
            )
        matches.extend(phase_matches[:PHASE_WINDOW_BURST_LIMIT])
    return matches


def session_phase_windows(phase_signals: dict[str, object]) -> list[tuple[str, float]]:
    windows: list[tuple[str, float]] = []
    for label, key in (
        ("first_connected", "first_connected_offset"),
        ("first_target_connect", "first_target_connect_offset"),
        ("first_disconnect", "first_disconnect_offset"),
        ("first_reconnect", "first_reconnect_after_disconnect_offset"),
    ):
        value = phase_signals.get(key)
        if isinstance(value, (int, float)):
            windows.append((label, float(value)))
    return windows


def burst_overlaps_phase_window(
    start_offset: float | None,
    end_offset: float | None,
    phase_offset: float,
) -> bool:
    if start_offset is None and end_offset is None:
        return False
    start = start_offset if start_offset is not None else end_offset
    end = end_offset if end_offset is not None else start_offset
    assert start is not None and end is not None
    return start <= phase_offset + PHASE_WINDOW_SECONDS and end >= phase_offset - PHASE_WINDOW_SECONDS


def format_initial_payload_bursts(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    rendered: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        rendered.append(
            "`#{}:start={},end={},packets={},bytes={},pattern={},lengths={}`".format(
                index,
                format_seconds(item.get("start_offset")),
                format_seconds(item.get("end_offset")),
                item.get("packets", "unknown"),
                item.get("bytes", "unknown"),
                item.get("direction_pattern", "unknown"),
                item.get("length_fingerprint", "unknown"),
            )
        )
    return ", ".join(rendered) if rendered else "none"


def format_phase_window_payload_bursts(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    rendered: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        rendered.append(
            "`phase={},phase_offset={},burst=#{},start={},end={},packets={},bytes={},pattern={},lengths={}`".format(
                item.get("phase", "unknown"),
                format_seconds(item.get("phase_offset")),
                item.get("burst_index", "unknown"),
                format_seconds(item.get("start_offset")),
                format_seconds(item.get("end_offset")),
                item.get("packets", "unknown"),
                item.get("bytes", "unknown"),
                item.get("direction_pattern", "unknown"),
                item.get("length_fingerprint", "unknown"),
            )
        )
    return ", ".join(rendered) if rendered else "none"


def format_framing_ratios(
    ascii_ratios: object,
    high_ratios: object,
    zero_ratios: object,
    control_ratios: object,
) -> str:
    if not all(isinstance(value, Counter) for value in (ascii_ratios, high_ratios, zero_ratios, control_ratios)):
        return "unknown"
    return (
        f"ascii={format_counter(ascii_ratios)}; "
        f"high={format_counter(high_ratios)}; "
        f"zero={format_counter(zero_ratios)}; "
        f"control={format_counter(control_ratios)}"
    )


def format_framing_samples(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    rendered: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        rendered.append(
            "`#{}:first={},len_prefix={},tls={},entropy={},diversity={},ascii={},high={}`".format(
                index,
                item.get("first_byte_class", "missing"),
                item.get("length_prefix_candidates", "missing"),
                item.get("tls_record_like", "missing"),
                item.get("entropy_bucket", "missing"),
                item.get("byte_diversity_bucket", "missing"),
                item.get("ascii_ratio", "missing"),
                item.get("high_ratio", "missing"),
            )
        )
    return ", ".join(rendered) if rendered else "none"


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


def render_interpretation_notes(
    metadata: dict[str, str],
    log_counts: Counter[str],
    phase_signals: dict[str, object],
    pcap_summary: dict[str, object],
) -> list[str]:
    notes = [
        "- Notes:",
        "  - Packet flow summaries are length/timing evidence only: direction labels are arbitrary within each flow, and raw endpoints, dynamic ports, TCP payloads, TXT values, interface identifiers, and unified-log lines are not included.",
    ]

    requested_duration = parse_duration_seconds(metadata.get("duration", ""))
    packet_span = pcap_summary.get("packet_span")
    if isinstance(packet_span, float) and requested_duration and packet_span > requested_duration * 1.2:
        notes.append(
            "  - Decoded pcap timing exceeds the requested capture duration; treat packet and unified-log counts as active-session signal shape rather than an exact bounded window."
        )

    first_disconnect = phase_signals.get("first_disconnect_offset")
    first_reconnect = phase_signals.get("first_reconnect_after_disconnect_offset")
    if first_disconnect is not None and first_reconnect is not None:
        notes.append(
            "  - Redacted phase counters show disconnect activity followed by reconnect/focus activity, so this run is useful for comparing Windows reconnect-state behavior."
        )

    awdl_flows = pcap_summary.get("awdl_tcp_flows")
    if isinstance(awdl_flows, list) and awdl_flows:
        first_flow = awdl_flows[0]
        if isinstance(first_flow, dict) and int(first_flow.get("payload_bytes", 0) or 0) > 0:
            notes.append(
                "  - The strongest packet clue is the dominant AWDL IPv6 link-local dynamic-port TCP flow. A Windows native probe that reaches admission should be compared against this flow's payload-length frequencies, initial length sequence, and gap buckets before chasing generic primary-network HTTPS traffic."
            )

    if log_counts["native_target_keywords"] or log_counts["native_sync_layout_keywords"]:
        notes.append(
            "  - Native UniversalControl/Rapport target or sync/layout counters are active, so packet bursts should be interpreted together with focus, target-ready, and layout state rather than as raw pointer traffic alone."
        )

    if any(
        phase_signals.get(key) is not None
        for key in (
            "first_connected_offset",
            "first_target_connect_offset",
            "first_disconnect_offset",
            "first_reconnect_after_disconnect_offset",
        )
    ):
        notes.append(
            "  - Phase-window payload bursts are correlation hints within +/-2s of redacted session phase offsets; they are not decoded messages."
        )

    notes.append(
        "  - The action timeline includes pointer movement, scrolling, and harmless key activity; interpret input/action counters and packet bursts as mixed input activity, not pointer-only traffic. Literal typed text is intentionally not recorded."
    )
    notes.append(
        "  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, typed text, or unified-log lines."
    )
    return notes


def parse_duration_seconds(value: str) -> int | None:
    match = re.match(r"^(\d+)s$", value.strip())
    if not match:
        return None
    return int(match.group(1))


def format_set(values) -> str:
    unique = sorted({str(value) for value in values if str(value)})
    if not unique:
        return "none"
    return ", ".join(f"`{value}`" for value in unique)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={counter[key]}" for key in sorted(counter))


def format_top_counter(counter: Counter[str], *, limit: int) -> str:
    if not counter:
        return "none"
    return ", ".join(f"`{key}`={value}" for key, value in counter.most_common(limit))


def sort_key(value: str) -> tuple[int, int | str]:
    if value.isdigit():
        return (0, int(value))
    return (1, value)


def format_pair(values: object) -> str:
    if not isinstance(values, tuple) or len(values) != 2:
        return "unknown"
    return f"`{values[0]}`<->`{values[1]}`"


def format_seconds(value: object) -> str:
    if value is None:
        return "unknown"
    seconds = float(value)
    if seconds < 1:
        return f"{seconds:.3f}s"
    if seconds < 10:
        return f"{seconds:.2f}s"
    return f"{seconds:.1f}s"


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
