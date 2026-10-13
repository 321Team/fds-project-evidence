#!/usr/bin/env bash
# Executes the reviewed read/capture cards; no request, policy write or service change.
set -uo pipefail
set +x
umask 077
cd "$1" || exit 2
ROLE=$2
case "$ROLE" in gateway) EXPECT=mgmt-gw01;; monitor) EXPECT=monitor01;; *) exit 2;; esac
test "$(hostname -s)" = "$EXPECT" || exit 2
sha256sum -c SOURCE_SHA256SUMS || exit 2
sudo -v || exit 2
OUT=$PWD/field
mkdir "$OUT" || exit 97
printf '%s\n' "$OUT" > field-path.txt
collect_phase() {
  local phase=$1 rc=0 captured
  date -Is > "$OUT/$phase.time"
  sudo -n python3 "$PWD/collect.py" > "$OUT/$phase.stdout" 2> "$OUT/$phase.stderr" || rc=$?
  printf '%s\n' "$rc" > "$OUT/$phase.rc"
  captured=$(sed -n 's/^OUT=//p' "$OUT/$phase.stdout" | head -1)
  case "$ROLE:$captured" in gateway:/root/if06b-policy-*|monitor:/root/if06b-mon-inputs-*) ;; *) return 2;; esac
  sudo -n tar -C /root -czf - "${captured##*/}" > "$OUT/$phase.tar.gz" || return 12
  return "$rc"
}
collect_phase pre || exit $?
date -Is > "$OUT/READY"
echo "AUTH_AND_PRE_READ_READY role=$ROLE; waiting for this session's capture start"
READY_BEGIN=$SECONDS
while ! test -f "$OUT/GO"; do
  test "$((SECONDS-READY_BEGIN))" -lt 600 || { echo READY_WAIT_EXPIRED; exit 4; }
  sleep 1
done
# A stale sudo ticket must stop before captures, not consume their window.
sudo -n true || { echo AUTH_EXPIRED_BEFORE_CAPTURE; exit 4; }
capture_point() (
  set -eu
  POINT=$1; IF=$2; C=$OUT/$POINT
  mkdir "$C"
  set -C
  date -Is > "$C/cap-start.txt"
  sudo -n timeout --signal=INT --preserve-status 300 tcpdump -nn -tttt -l -i "$IF" '(host 10.1.93.108 and host 10.250.10.30) and ((tcp and (port 443 or port 8443)) or icmp)' > "$C/cap.txt" 2> "$C/cap-stats.txt" &
  CAP_PID=$!
  echo "cap_pid=$CAP_PID window_s=300 point=$POINT if=$IF" > "$C/cap-pid.txt"
  if wait "$CAP_PID"; then CAP_RC=0; else CAP_RC=$?; fi
  echo "rc=$CAP_RC" > "$C/cap-rc.txt"
  date -Is > "$C/cap-end.txt"
)
# Each point has a separate waiting subshell and result directory. No PID-wide kills.
if test "$ROLE" = gateway; then
  capture_point gateway-in ens160 & P1=$!
  capture_point gateway-out ens224 & P2=$!
  printf 'CAPTURES_STARTING role=gateway path=%s\n' "$OUT"
  wait "$P1"; R1=$?
  wait "$P2"; R2=$?
  printf 'point_shell_rc=%s,%s\n' "$R1" "$R2" > "$OUT/capture-shell.rc"
else
  capture_point monitor-in ens160 & P1=$!
  printf 'CAPTURES_STARTING role=monitor path=%s\n' "$OUT"
  wait "$P1"; R1=$?
  printf 'point_shell_rc=%s\n' "$R1" > "$OUT/capture-shell.rc"
fi
echo "Captures ended. Renew sudo authentication for the read-only post snapshot."
if sudo -v; then
  collect_phase post
  POST_RC=$?
else
  POST_RC=1
  printf '%s\n' 'Post snapshot authentication failed' > "$OUT/post-auth.stderr"
fi
printf '%s\n' "$POST_RC" > "$OUT/post-collection.rc"
date -Is > "$OUT/completed.time"
find "$OUT" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$OUT/SHA256SUMS"
tar -czf capture.tar.gz field
sha256sum capture.tar.gz > capture.tar.gz.sha256
echo "FIELD_COMPLETE role=$ROLE post_rc=$POST_RC"
exit "$POST_RC"
