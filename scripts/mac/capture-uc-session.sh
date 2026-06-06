#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
duration=120
interfaces=()
enable_tcpdump=0
tcpdump_filter='udp port 5353 or udp port 3722 or tcp'

usage() {
  cat <<'EOF'
Usage: scripts/mac/capture-uc-session.sh [options]

Options:
  --duration SECONDS       Capture duration. Default: 120.
  --tcpdump                Capture packet traces with sudo tcpdump.
  --interface NAME         Interface for tcpdump. Repeatable. Default with --tcpdump: en0 plus awdl0 when present.
  --filter EXPR            tcpdump filter. Default: udp port 5353 or udp port 3722 or tcp.
  -h, --help               Show this help.

Use this during a real Apple-to-Apple Universal Control session. Start the
script, then perform a controlled sequence: idle, edge push, pointer movement,
key press, scroll, and return to local. The script writes raw artifacts under
artifacts/ and does not redact them.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration)
      duration="$2"
      shift 2
      ;;
    --tcpdump)
      enable_tcpdump=1
      shift
      ;;
    --interface)
      interfaces+=("$2")
      shift 2
      ;;
    --filter)
      tcpdump_filter="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "${duration}" =~ ^[0-9]+$ ]] || [[ "${duration}" -lt 1 ]]; then
  printf 'duration must be a positive integer\n' >&2
  exit 2
fi

if [[ "${enable_tcpdump}" -eq 1 && "${#interfaces[@]}" -eq 0 ]]; then
  interfaces=(en0)
  if ifconfig awdl0 >/dev/null 2>&1; then
    interfaces+=(awdl0)
  fi
fi

stamp="$(date -u +"%Y%m%dT%H%M%SZ")"
out_dir="${repo_root}/artifacts/mac-uc-session-${stamp}"
mkdir -p "${out_dir}"

pids=()
cleanup() {
  for pid in "${pids[@]}"; do
    kill "${pid}" 2>/dev/null || true
  done
  for pid in "${pids[@]}"; do
    wait "${pid}" 2>/dev/null || true
  done
}
trap cleanup EXIT

run_capture() {
  local name="$1"
  shift
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n\n'
    "$@"
  } >"${out_dir}/${name}.txt" 2>&1 &
  pids+=("$!")
}

snapshot_launchd() {
  local suffix="$1"
  {
    printf '$ launchctl print gui/%s/com.apple.ensemble\n\n' "$(id -u)"
    launchctl print "gui/$(id -u)/com.apple.ensemble"
  } >"${out_dir}/launchctl-ensemble-${suffix}.txt" 2>&1 || true

  {
    printf '$ launchctl print gui/%s/com.apple.rapportd\n\n' "$(id -u)"
    launchctl print "gui/$(id -u)/com.apple.rapportd"
  } >"${out_dir}/launchctl-rapportd-${suffix}.txt" 2>&1 || true
}

snapshot_lsof() {
  local suffix="$1"
  {
    printf '$ lsof -nP -iTCP -iUDP | grep -E "rapportd|UniversalControl"\n\n'
    lsof -nP -iTCP -iUDP | grep -E 'rapportd|UniversalControl' || true
  } >"${out_dir}/lsof-network-${suffix}.txt" 2>&1 || true
}

snapshot_launchd "before"
snapshot_lsof "before"

run_capture "companion-link-browse" dns-sd -B _companion-link._tcp local
run_capture "universalcontrol-browse" dns-sd -B _universalcontrol._tcp local

{
  printf '$ log stream --style compact --predicate ...\n\n'
  log stream --style compact --predicate 'process == "UniversalControl" || process == "rapportd" || process == "mDNSResponder" || process == "nearbyd" || process == "wifip2pd"'
} >"${out_dir}/unified-log.txt" 2>&1 &
pids+=("$!")

if [[ "${enable_tcpdump}" -eq 1 ]]; then
  for interface in "${interfaces[@]}"; do
    {
      printf '$ sudo tcpdump -i %q -w %q %q\n\n' "${interface}" "${out_dir}/tcpdump-${interface}.pcap" "${tcpdump_filter}"
      sudo tcpdump -i "${interface}" -w "${out_dir}/tcpdump-${interface}.pcap" "${tcpdump_filter}"
    } >"${out_dir}/tcpdump-${interface}.txt" 2>&1 &
    pids+=("$!")
  done
fi

cat >"${out_dir}/README.txt" <<EOF
macOS Universal Control session capture.

Created: ${stamp}
Duration: ${duration}s
tcpdump: ${enable_tcpdump}
interfaces: ${interfaces[*]:-none}
tcpdump_filter: ${tcpdump_filter}

Suggested action timeline:
1. 0-10s: leave both devices idle.
2. 10-25s: push pointer across the configured edge.
3. 25-45s: move pointer on the target.
4. 45-60s: type one harmless key.
5. 60-75s: scroll once.
6. 75-90s: return pointer to the source Mac.
7. Remaining time: leave both devices idle.

Review and redact before sharing. Output can contain hostnames, addresses,
Bonjour TXT values, local interface identifiers, Apple-account-linked device
identifiers, packet payloads, and local process details.
EOF

printf 'Capturing Universal Control session for %ss; output: %s\n' "${duration}" "${out_dir}"
if [[ "${enable_tcpdump}" -eq 1 ]]; then
  printf 'tcpdump enabled on: %s\n' "${interfaces[*]}"
else
  printf 'tcpdump disabled; rerun with --tcpdump for packet captures\n'
fi
sleep "${duration}"
cleanup
trap - EXIT

snapshot_launchd "after"
snapshot_lsof "after"

printf 'Wrote %s\n' "${out_dir}"
