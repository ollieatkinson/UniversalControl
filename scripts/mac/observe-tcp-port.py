#!/usr/bin/env python3
"""Bounded redacted TCP observer for coordinated Bonjour visibility probes."""

from __future__ import annotations

import argparse
import ipaddress
import math
import socket
import time
from collections import Counter


DEFAULT_READ_LIMIT = 16
DEFAULT_READ_CHUNK_BYTES = 4096
DEFAULT_READ_TIMEOUT_MS = 250


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Listen on a TCP port for a bounded time and print connection "
            "length/timing shapes without payload bytes or peer addresses."
        )
    )
    parser.add_argument("--bind", default="0.0.0.0", help="Bind address. Default: 0.0.0.0.")
    parser.add_argument("--port", type=positive_int, required=True, help="TCP port to listen on.")
    parser.add_argument(
        "--duration",
        type=positive_int,
        default=30,
        help="Observer duration in seconds. Default: 30.",
    )
    parser.add_argument(
        "--read-limit",
        type=positive_int,
        default=DEFAULT_READ_LIMIT,
        help=f"Maximum reads per connection. Default: {DEFAULT_READ_LIMIT}.",
    )
    parser.add_argument(
        "--read-chunk-bytes",
        type=positive_int,
        default=DEFAULT_READ_CHUNK_BYTES,
        help=f"Maximum bytes per read. Default: {DEFAULT_READ_CHUNK_BYTES}.",
    )
    parser.add_argument(
        "--read-timeout-ms",
        type=positive_int,
        default=DEFAULT_READ_TIMEOUT_MS,
        help=f"Per-read timeout in milliseconds. Default: {DEFAULT_READ_TIMEOUT_MS}.",
    )
    parser.add_argument(
        "--framing",
        action="store_true",
        help="Print byte-class, entropy, length-prefix, and TLS-shape buckets.",
    )
    args = parser.parse_args()

    accepted = observe(args)
    print(f"TCP observer summary: accepted_connections={accepted}", flush=True)
    return 0


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def observe(args: argparse.Namespace) -> int:
    deadline = time.monotonic() + args.duration
    accepted = 0

    with socket.socket(socket.AF_INET6 if ":" in args.bind else socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.bind, args.port))
        server.listen()
        server.settimeout(0.1)

        print(
            "TCP observer listening "
            f"bind_class={classify_ip(args.bind)} port={args.port} duration={args.duration}s",
            flush=True,
        )
        if args.framing:
            print("TCP observer framing probe enabled: yes", flush=True)

        while time.monotonic() < deadline:
            try:
                connection, peer = server.accept()
            except socket.timeout:
                continue

            accepted += 1
            print(
                "TCP observer accepted connection "
                f"#{accepted} peer_class={classify_ip(peer[0])}",
                flush=True,
            )
            with connection:
                observe_connection(connection, accepted, args)

    return accepted


def observe_connection(connection: socket.socket, index: int, args: argparse.Namespace) -> None:
    started = time.monotonic()
    reads = 0
    total_bytes = 0
    closed_by_peer = False
    connection.settimeout(args.read_timeout_ms / 1000)

    for read_index in range(1, args.read_limit + 1):
        try:
            chunk = connection.recv(args.read_chunk_bytes)
        except socket.timeout:
            if reads == 0:
                print(
                    f"TCP observer connection #{index} produced no data before timeout",
                    flush=True,
                )
            break
        except OSError:
            print(f"TCP observer read error on connection #{index}: redacted", flush=True)
            break

        if not chunk:
            if reads == 0:
                print(f"TCP observer connection #{index} closed without data", flush=True)
            else:
                closed_by_peer = True
            break

        reads += 1
        total_bytes += len(chunk)
        elapsed_ms = int((time.monotonic() - started) * 1000)
        if read_index == 1:
            print(
                "TCP observer connection "
                f"#{index} first_read_elapsed_ms={elapsed_ms} first_read_bytes={len(chunk)}",
                flush=True,
            )
        else:
            print(
                "TCP observer connection "
                f"#{index} read #{read_index} elapsed_ms={elapsed_ms} bytes={len(chunk)}",
                flush=True,
            )
        if args.framing:
            print(
                f"TCP observer connection #{index} read #{read_index} framing "
                f"{frame_shape_summary(chunk)}",
                flush=True,
            )

    if reads:
        duration_ms = int((time.monotonic() - started) * 1000)
        print(
            f"TCP observer connection #{index} summary reads={reads} "
            f"total_bytes={total_bytes} duration_ms={duration_ms} "
            f"read_limit_reached={format_bool(reads >= args.read_limit)} "
            f"closed_by_peer={format_bool(closed_by_peer)}",
            flush=True,
        )


def classify_ip(value: str) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return "unknown"
    if address.is_loopback:
        return "loopback"
    if address.is_unspecified:
        return "unspecified"
    if address.is_multicast:
        return "multicast"
    if address.is_link_local:
        return "link-local"
    if address.is_private:
        return "private"
    if address.is_global:
        return "global"
    return "other"


def frame_shape_summary(data: bytes) -> str:
    byte_classes = byte_class_counts(data)
    tls_record_like, tls_record_len_match = tls_record_shape(data)
    return (
        f"first_byte_class={first_byte_class(data)} "
        f"ascii_ratio={ratio_bucket(byte_classes['ascii'], len(data))} "
        f"high_ratio={ratio_bucket(byte_classes['high'], len(data))} "
        f"zero_ratio={ratio_bucket(byte_classes['zero'], len(data))} "
        f"control_ratio={ratio_bucket(byte_classes['control'], len(data))} "
        f"entropy_bucket={entropy_bucket(data)} "
        f"byte_diversity_bucket={byte_diversity_bucket(data)} "
        f"length_prefix_candidates={format_candidates(length_prefix_candidates(data))} "
        f"tls_record_like={format_bool(tls_record_like)} "
        f"tls_record_len_match={format_bool(tls_record_len_match)}"
    )


def byte_class_counts(data: bytes) -> Counter[str]:
    counts: Counter[str] = Counter()
    for byte in data:
        if byte == 0:
            counts["zero"] += 1
        elif byte in (9, 10, 13) or 0x20 <= byte <= 0x7E:
            counts["ascii"] += 1
        elif 0x01 <= byte <= 0x1F or byte == 0x7F:
            counts["control"] += 1
        else:
            counts["high"] += 1
    return counts


def first_byte_class(data: bytes) -> str:
    if not data:
        return "none"
    byte = data[0]
    if byte == 0:
        return "zero"
    if byte in (9, 10, 13):
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


def entropy_bucket(data: bytes) -> str:
    if not data:
        return "empty"
    counts = Counter(data)
    entropy = 0.0
    total = len(data)
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


def byte_diversity_bucket(data: bytes) -> str:
    if not data:
        return "empty"
    unique = len(set(data))
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


def length_prefix_candidates(data: bytes) -> list[str]:
    candidates: list[str] = []
    if len(data) >= 2:
        push_length_matches(candidates, "be16", int.from_bytes(data[:2], "big"), 2, len(data))
        push_length_matches(candidates, "le16", int.from_bytes(data[:2], "little"), 2, len(data))
    if len(data) >= 4:
        push_length_matches(candidates, "be32", int.from_bytes(data[:4], "big"), 4, len(data))
        push_length_matches(candidates, "le32", int.from_bytes(data[:4], "little"), 4, len(data))
    return candidates


def push_length_matches(
    candidates: list[str], endian: str, value: int, prefix_bytes: int, total_bytes: int
) -> None:
    if value == total_bytes:
        candidates.append(f"{endian}_total")
    if value + prefix_bytes == total_bytes:
        candidates.append(f"{endian}_payload")


def tls_record_shape(data: bytes) -> tuple[bool, bool]:
    if len(data) < 5:
        return False, False
    content_type = 0x14 <= data[0] <= 0x18
    version = data[1] == 0x03 and data[2] <= 0x04
    payload_len = int.from_bytes(data[3:5], "big")
    record_like = content_type and version
    return record_like, record_like and payload_len + 5 == len(data)


def format_candidates(candidates: list[str]) -> str:
    if not candidates:
        return "none"
    return "|".join(candidates)


def format_bool(value: bool) -> str:
    return "true" if value else "false"


if __name__ == "__main__":
    raise SystemExit(main())
