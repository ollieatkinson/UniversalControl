#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

duration=300
service="_companion-link._tcp"
instance="AnyKBFlow Mac Bonjour Probe"
port=49152
output_dir=""
summary_output=""
expected_remote_instance=""
txt_values=("probe=mac-bonjour" "role=mac-native-visibility")

usage() {
  cat <<'EOF'
Usage: scripts/mac/capture-bonjour-visibility.sh [options]

Options:
  --duration SECONDS              Capture duration. Default: 300.
  --service TYPE                  DNS-SD service type. Default: _companion-link._tcp.
  --instance NAME                 Local instance to advertise.
  --port PORT                     Local advertised TCP port. Default: 49152.
  --txt KEY=VALUE                 TXT value to advertise. May be repeated.
  --expected-remote-instance NAME Remote Windows instance to match by yes/no only.
  --output-dir DIR                Raw artifact directory under artifacts/.
  --summary-output PATH           Redacted summary output path under docs/observations/.
  -h, --help                      Show this help.

This advertises a project-owned Bonjour service from macOS and simultaneously
browses the same service type. Raw artifacts can contain hostnames, interface
IDs, and instance names. Commit only the redacted summary.
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
    --port)
      port="$2"
      shift 2
      ;;
    --txt)
      txt_values+=("$2")
      shift 2
      ;;
    --expected-remote-instance)
      expected_remote_instance="$2"
      shift 2
      ;;
    --output-dir)
      output_dir="$2"
      shift 2
      ;;
    --summary-output)
      summary_output="$2"
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

for value_name in duration port; do
  value="${!value_name}"
  if ! [[ "${value}" =~ ^[0-9]+$ ]] || [[ "${value}" -lt 1 ]]; then
    printf '%s must be a positive integer\n' "${value_name}" >&2
    exit 2
  fi
done

if [[ "${service}" != _*._* ]]; then
  printf 'service must look like _name._proto\n' >&2
  exit 2
fi

stamp="$(date -u +"%Y%m%dT%H%M%SZ")"
day="$(date -u +"%Y-%m-%d")"

resolve_repo_path() {
  local path="$1"
  if [[ "${path}" = /* ]]; then
    printf '%s\n' "${path}"
  else
    printf '%s/%s\n' "${repo_root}" "${path}"
  fi
}

if [[ -n "${output_dir}" ]]; then
  out_dir="$(resolve_repo_path "${output_dir}")"
else
  out_dir="${repo_root}/artifacts/mac-bonjour-visibility-${stamp}"
fi

if [[ -n "${summary_output}" ]]; then
  summary_path="$(resolve_repo_path "${summary_output}")"
else
  summary_path="${repo_root}/docs/observations/${day}-redacted-macos-bonjour-visibility.md"
  if [[ -e "${summary_path}" ]]; then
    summary_path="${repo_root}/docs/observations/${day}-${stamp}-redacted-macos-bonjour-visibility.md"
  fi
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

register_command=(dns-sd -R "${instance}" "${service}" local "${port}" "${txt_values[@]}")
run_capture "dns-sd-register" "${register_command[@]}"
run_capture "dns-sd-browse" dns-sd -B "${service}" local

cat >"${out_dir}/README.txt" <<EOF
macOS Bonjour cross-visibility capture.

Created: ${stamp}
Duration: ${duration}s
Service: ${service}
Local instance: ${instance}
Port: ${port}
TXT count: ${#txt_values[@]}
Expected remote instance: ${expected_remote_instance}

Review and redact before sharing. Output can contain hostnames, addresses,
Bonjour TXT values, local interface identifiers, and local instance names.
EOF

printf 'Advertising and browsing %s for %ss; output: %s\n' "${service}" "${duration}" "${out_dir}"
sleep "${duration}"
cleanup
trap - EXIT

mkdir -p "$(dirname "${summary_path}")"
summary_args=("${repo_root}/scripts/mac/summarize-bonjour-visibility-artifact.py" "${out_dir}" --output "${summary_path}")
if [[ -n "${expected_remote_instance}" ]]; then
  summary_args+=(--expected-remote-instance "${expected_remote_instance}")
fi
"${summary_args[@]}"

printf 'Wrote redacted summary: %s\n' "${summary_path}"
