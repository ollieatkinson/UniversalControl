#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
duration=60
service="_anykbflow-probe._tcp"
instance="AnyKBFlow Probe"
include_resolve=1
output_dir=""

usage() {
  cat <<'EOF'
Usage: scripts/mac/watch-mdns-service.sh [options]

Options:
  --duration SECONDS    Capture duration. Default: 60.
  --service TYPE        DNS-SD service type without .local. Default: _anykbflow-probe._tcp.
  --instance NAME       Instance to resolve with dns-sd -L. Default: AnyKBFlow Probe.
  --output-dir DIR      Write artifact files to DIR. Default: artifacts/mac-mdns-watch-<timestamp>/.
  --no-resolve          Skip dns-sd -L.
  -h, --help            Show this help.

The script writes to artifacts/mac-mdns-watch-<timestamp>/.
Review and redact output before sharing.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration)
      duration="$2"
      shift 2
      ;;
    --service)
      service="$2"
      shift 2
      ;;
    --instance)
      instance="$2"
      shift 2
      ;;
    --output-dir)
      output_dir="$2"
      shift 2
      ;;
    --no-resolve)
      include_resolve=0
      shift
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

stamp="$(date -u +"%Y%m%dT%H%M%SZ")"
if [[ -n "${output_dir}" ]]; then
  if [[ "${output_dir}" = /* ]]; then
    out_dir="${output_dir}"
  else
    out_dir="${repo_root}/${output_dir}"
  fi
else
  out_dir="${repo_root}/artifacts/mac-mdns-watch-${stamp}"
fi
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

run_capture "dns-sd-browse" dns-sd -B "${service}" local

if [[ "${include_resolve}" -eq 1 ]]; then
  run_capture "dns-sd-resolve" dns-sd -L "${instance}" "${service}" local
fi

{
  printf '$ log stream --style compact --predicate ...\n\n'
  log stream --style compact --predicate 'process == "UniversalControl" || process == "rapportd" || process == "mDNSResponder"'
} >"${out_dir}/unified-log.txt" 2>&1 &
pids+=("$!")

{
  printf '$ launchctl print gui/%s/com.apple.ensemble\n\n' "$(id -u)"
  launchctl print "gui/$(id -u)/com.apple.ensemble"
} >"${out_dir}/launchctl-ensemble-before.txt" 2>&1 || true

{
  printf '$ launchctl print gui/%s/com.apple.rapportd\n\n' "$(id -u)"
  launchctl print "gui/$(id -u)/com.apple.rapportd"
} >"${out_dir}/launchctl-rapportd-before.txt" 2>&1 || true

cat >"${out_dir}/README.txt" <<EOF
macOS mDNS/watch output.

Created: ${stamp}
Duration: ${duration}s
Service: ${service}
Instance: ${instance}

Review and redact before sharing. Output can contain hostnames, addresses,
Bonjour TXT values, local interface identifiers, and local process details.
EOF

printf 'Watching %s for %ss; output: %s\n' "${service}" "${duration}" "${out_dir}"
sleep "${duration}"
cleanup
trap - EXIT

{
  printf '$ launchctl print gui/%s/com.apple.ensemble\n\n' "$(id -u)"
  launchctl print "gui/$(id -u)/com.apple.ensemble"
} >"${out_dir}/launchctl-ensemble-after.txt" 2>&1 || true

{
  printf '$ launchctl print gui/%s/com.apple.rapportd\n\n' "$(id -u)"
  launchctl print "gui/$(id -u)/com.apple.rapportd"
} >"${out_dir}/launchctl-rapportd-after.txt" 2>&1 || true

printf 'Wrote %s\n' "${out_dir}"
