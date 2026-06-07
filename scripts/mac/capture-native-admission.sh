#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mode="benign"
duration=""
instance=""
output=""
windows_seconds=60
no_prompt=0
print_windows_command_only=0

usage() {
  cat <<'EOF'
Usage: scripts/mac/capture-native-admission.sh [options]

Options:
  --mode MODE                     Capture mode: benign, companion-link, or shape. Default: benign.
  --duration SECONDS              Mac capture duration. Defaults: benign=60, companion-link/shape=90.
  --instance NAME                 Expected Windows service instance.
  --windows-seconds SECONDS       Seconds to print in the Windows advertise command. Default: 60.
  --output PATH                   Redacted summary output path under docs/observations/.
  --no-prompt                     Start capture immediately.
  --print-windows-command-only    Print the matching Windows command and exit.
  -h, --help                      Show this help.

Modes:
  benign
    Watches _anykbflow-probe._tcp while Windows advertises a non-Apple probe.

  companion-link
    Watches _companion-link._tcp while Windows advertises the controlled native
    candidate with --allow-apple-service.

  shape
    Watches _companion-link._tcp while Windows advertises placeholder rp* TXT
    key/value classes with advertise-companion-link-shape.

Raw artifacts are written under artifacts/ and can contain identifiers. The
summary written by this wrapper is generated through summarize-mdns-watch-artifact.py.
The printed Windows command uses scripts/windows/capture-native-admission.py so
the Windows side also writes a redacted summary and, for native modes, an AWDL
baseline comparison.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      mode="$2"
      shift 2
      ;;
    --duration)
      duration="$2"
      shift 2
      ;;
    --instance)
      instance="$2"
      shift 2
      ;;
    --windows-seconds)
      windows_seconds="$2"
      shift 2
      ;;
    --output)
      output="$2"
      shift 2
      ;;
    --no-prompt)
      no_prompt=1
      shift
      ;;
    --print-windows-command-only)
      print_windows_command_only=1
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

case "${mode}" in
  benign|companion-link|shape)
    ;;
  *)
    printf 'mode must be benign, companion-link, or shape\n' >&2
    exit 2
    ;;
esac

if [[ -z "${duration}" ]]; then
  case "${mode}" in
    benign) duration=60 ;;
    companion-link) duration=90 ;;
    shape) duration=90 ;;
  esac
fi

for value_name in duration windows_seconds; do
  value="${!value_name}"
  if ! [[ "${value}" =~ ^[0-9]+$ ]] || [[ "${value}" -lt 1 ]]; then
    printf '%s must be a positive integer\n' "${value_name}" >&2
    exit 2
  fi
done

if [[ -z "${instance}" ]]; then
  case "${mode}" in
    benign) instance="AnyKBFlow Probe" ;;
    companion-link) instance="AnyKBFlow Native Probe" ;;
    shape) instance="AnyKBFlow Native Shape Probe" ;;
  esac
fi

windows_command() {
  cat <<EOF
python scripts/windows/capture-native-admission.py \`
  --mode ${mode} \`
  --seconds ${windows_seconds} \`
  --instance "${instance}" \`
  --no-prompt
EOF
}

if [[ "${print_windows_command_only}" -eq 1 ]]; then
  windows_command
  exit 0
fi

resolve_repo_path() {
  local path="$1"
  if [[ "${path}" = /* ]]; then
    printf '%s\n' "${path}"
  else
    printf '%s/%s\n' "${repo_root}" "${path}"
  fi
}

stamp="$(date -u +"%Y%m%dT%H%M%SZ")"
day="$(date -u +"%Y-%m-%d")"
artifact_dir="${repo_root}/artifacts/mac-native-admission-${mode}-${stamp}"

if [[ -z "${output}" ]]; then
  case "${mode}" in
    benign)
      output="${repo_root}/docs/observations/${day}-redacted-benign-mdns-watch.md"
      ;;
    companion-link)
      output="${repo_root}/docs/observations/${day}-redacted-companion-link-candidate.md"
      ;;
    shape)
      output="${repo_root}/docs/observations/${day}-redacted-companion-link-shape-candidate.md"
      ;;
  esac
  if [[ -e "${output}" ]]; then
    case "${mode}" in
      benign)
        output="${repo_root}/docs/observations/${day}-${stamp}-redacted-benign-mdns-watch.md"
        ;;
      companion-link)
        output="${repo_root}/docs/observations/${day}-${stamp}-redacted-companion-link-candidate.md"
        ;;
      shape)
        output="${repo_root}/docs/observations/${day}-${stamp}-redacted-companion-link-shape-candidate.md"
        ;;
    esac
  fi
else
  output="$(resolve_repo_path "${output}")"
fi

printf 'Native admission capture mode: %s\n' "${mode}"
printf 'Raw artifact directory: %s\n' "${artifact_dir}"
printf 'Redacted summary output: %s\n\n' "${output}"
printf 'Run this on Windows while the macOS capture is active:\n\n'
windows_command
printf '\n'

if [[ "${no_prompt}" -eq 0 && -t 0 ]]; then
  printf 'Press Return to start the macOS capture, then start the Windows command immediately...'
  read -r _
fi

watch_args=(
  --duration "${duration}"
  --output-dir "${artifact_dir}"
)

case "${mode}" in
  benign)
    watch_args+=(--service "_anykbflow-probe._tcp" --instance "${instance}")
    "${repo_root}/scripts/mac/watch-mdns-service.sh" "${watch_args[@]}"
    ;;
  companion-link)
    watch_args+=(--instance "${instance}")
    "${repo_root}/scripts/mac/watch-companion-link-candidate.sh" "${watch_args[@]}"
    ;;
  shape)
    watch_args+=(--instance "${instance}")
    "${repo_root}/scripts/mac/watch-companion-link-candidate.sh" "${watch_args[@]}"
    ;;
esac

mkdir -p "$(dirname "${output}")"
"${repo_root}/scripts/mac/summarize-mdns-watch-artifact.py" \
  "${artifact_dir}" \
  --expected-instance "${instance}" \
  --output "${output}"

printf 'Wrote redacted summary: %s\n' "${output}"
