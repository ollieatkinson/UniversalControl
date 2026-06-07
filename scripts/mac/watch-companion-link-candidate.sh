#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
duration=90
instance=""
include_resolve=1
output_dir=""

usage() {
  cat <<'EOF'
Usage: scripts/mac/watch-companion-link-candidate.sh [options]

Options:
  --duration SECONDS    Capture duration. Default: 90.
  --instance NAME       _companion-link._tcp instance to resolve.
  --output-dir DIR      Write artifact files to DIR. Default: artifacts/mac-mdns-watch-<timestamp>/.
  --no-resolve          Browse only; skip dns-sd -L.
  -h, --help            Show this help.

Use this while Windows advertises a controlled _companion-link._tcp candidate.
The script wraps watch-mdns-service.sh with the native Universal Control service
type and captures dns-sd plus UniversalControl/rapportd/mDNSResponder logs.

Raw output is written under artifacts/ and can contain device identifiers,
hostnames, addresses, TXT values, and local interface identifiers.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration)
      duration="$2"
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

if [[ "${include_resolve}" -eq 1 && -z "${instance}" ]]; then
  printf 'missing --instance; pass the Windows-advertised instance or use --no-resolve\n' >&2
  usage >&2
  exit 2
fi

args=(
  --duration "${duration}"
  --service "_companion-link._tcp"
)

if [[ -n "${output_dir}" ]]; then
  args+=(--output-dir "${output_dir}")
fi

if [[ "${include_resolve}" -eq 1 ]]; then
  args+=(--instance "${instance}")
else
  args+=(--no-resolve)
fi

exec "${repo_root}/scripts/mac/watch-mdns-service.sh" "${args[@]}"
