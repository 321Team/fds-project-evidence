#!/usr/bin/env bash
# Existing accounts, interactive SSH/sudo only. Independent read-only collections.
set -uo pipefail
set +x
umask 077
cd -- "$(dirname -- "${BASH_SOURCE[0]}")" || exit 2
test "$(hostname -s)" = ansible01 || exit 2
sha256sum -c SHA256SUMS || exit 2
mkdir execution-claim || { echo 'STOP: this input collection was already started'; exit 97; }
date -Is > started-at.txt
printf '\n[1/2] mgmt-gw01: enter existing SSH password and sudo password in this terminal.\n'
bash gateway/run-interactive.sh
gateway_rc=$?
printf '%s\n' "$gateway_rc" > gateway.rc
printf '\n[2/2] monitor01: enter existing SSH password and sudo password in this terminal.\n'
bash monitor/run-interactive.sh
monitor_rc=$?
printf '%s\n' "$monitor_rc" > monitor.rc
date -Is > finished-at.txt
printf 'INPUT_READ_COMPLETE gateway_rc=%s monitor_rc=%s\n' "$gateway_rc" "$monitor_rc" | tee completed.txt
printf 'No canary, RBAC/token, policy/service change or packet trial was performed.\n'
test "$gateway_rc" -eq 0 && test "$monitor_rc" -eq 0
