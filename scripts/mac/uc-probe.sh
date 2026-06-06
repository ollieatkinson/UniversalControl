#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
stamp="$(date -u +"%Y%m%dT%H%M%SZ")"
out_dir="${repo_root}/artifacts/mac-uc-probe-${stamp}"
uc_app="/System/Library/CoreServices/UniversalControl.app"
uc_bin="${uc_app}/Contents/MacOS/UniversalControl"

mkdir -p "${out_dir}"

run() {
  local name="$1"
  shift
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n\n'
    "$@"
  } >"${out_dir}/${name}.txt" 2>&1 || true
}

run_shell() {
  local name="$1"
  local command="$2"
  {
    printf '$ %s\n\n' "${command}"
    bash -lc "${command}"
  } >"${out_dir}/${name}.txt" 2>&1 || true
}

sample_dns_sd() {
  local name="$1"
  local service="$2"
  local output="${out_dir}/${name}.txt"

  {
    printf '$ dns-sd -B %s local\n\n' "${service}"
    dns-sd -B "${service}" local &
    local pid=$!
    sleep 5
    kill "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  } >"${output}" 2>&1
}

sample_companion_link_self_resolve() {
  local output="${out_dir}/companion-link-resolve-self.txt"

  {
    local computer_name
    computer_name="$(scutil --get ComputerName)"
    printf '$ dns-sd -L %q _companion-link._tcp local\n\n' "${computer_name}"
    dns-sd -L "${computer_name}" _companion-link._tcp local &
    local pid=$!
    sleep 5
    kill "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  } >"${output}" 2>&1
}

run os sw_vers
run uname uname -a
run network-hardware networksetup -listallhardwareports
run_shell processes "pgrep -lf 'UniversalControl|rapportd|sharingd|useractivityd|mDNSResponder|bluetoothd|nearbyd|CLinkD'"

if [[ -d "${uc_app}" ]]; then
  run universalcontrol-info-plist plutil -p "${uc_app}/Contents/Info.plist"
  run universalcontrol-entitlements codesign -d --entitlements - "${uc_app}"
  run_shell universalcontrol-ls "ls -la '${uc_app}/Contents' '${uc_app}/Contents/MacOS'"
fi

if [[ -x "${uc_bin}" ]]; then
  run_shell universalcontrol-strings "strings -a '${uc_bin}' | rg -i 'com\\.apple\\.|UniversalControl|rapport|Companion|HID|keyboard|mouse|cursor|pointer|nearby|awdl|wifip2p|bonjour|_tcp|mdns|link|ensemble|OPACK|P2P' | sort -u"
fi

run_shell launchctl-ensemble "launchctl print gui/$(id -u)/com.apple.ensemble"
run_shell launchctl-rapportd "launchctl print gui/$(id -u)/com.apple.rapportd"
run_shell lsof-universalcontrol "pid=\$(pgrep -x UniversalControl | head -n 1); test -n \"\${pid}\" && lsof -nP -p \"\${pid}\" -a -iTCP -iUDP"
run_shell lsof-rapportd "pid=\$(pgrep -x rapportd | head -n 1); test -n \"\${pid}\" && lsof -nP -p \"\${pid}\" -a -iTCP -iUDP"
run_shell defaults-rapport-sharing "defaults read com.apple.rapport; defaults read com.apple.Sharing"
run_shell recent-uc-logs "log show --last 30m --style compact --predicate 'process == \"UniversalControl\" || process == \"rapportd\"' | rg -i 'universal|companion|clink|awdl|p2p|keyboard|mouse|pointer|nearby|rapport|error|fault' | tail -n 200"

sample_dns_sd companion-link-browse _companion-link._tcp
sample_companion_link_self_resolve
sample_dns_sd universalcontrol-browse _universalcontrol._tcp

cat >"${out_dir}/README.txt" <<EOF
macOS Universal Control probe output.

Created: ${stamp}

Review and redact before sharing or committing. DNS-SD TXT records, hostnames,
local addresses, Bluetooth addresses, and log lines may contain stable local
identifiers.
EOF

printf 'Wrote %s\n' "${out_dir}"
