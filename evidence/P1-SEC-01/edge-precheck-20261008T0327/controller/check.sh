#!/usr/bin/env bash
set -euo pipefail
umask 077
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
sha256sum -c SOURCE_SHA256SUMS
mkdir "$HERE/execution-lock" || { echo 'STOP: already started; preserve this receipt'; exit 2; }
date -u +%FT%TZ > started-utc.txt
RUN=$(TZ=Asia/Seoul date +%Y%m%dT%H%M)
printf '%s\n' "$RUN" > run-id.txt
BASE=(-o StrictHostKeyChecking=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=3)
test -t 0 && test -t 1 || { echo 'STOP: interactive terminal required'; exit 2; }
TTY_STATE=$(stty -g < /dev/tty)
stty -echo < /dev/tty
SOCKET_DIR=$(mktemp -d /tmp/edge-access.XXXXXXXX)
ACTIVE_TARGET=''
finish() {
  rc=$?
  trap - EXIT
  stty "$TTY_STATE" < /dev/tty || true
  if test -n "$ACTIVE_TARGET"; then
    ssh "${BASE[@]}" -S "$SOCKET_DIR/m" -O exit "$ACTIVE_TARGET" >/dev/null 2>&1 || true
  fi
  rmdir "$SOCKET_DIR" 2>/dev/null || true
  printf '%s\n' "$rc" > handoff.rc
  date -u +%FT%TZ > finished-utc.txt
  echo "HANDOFF_RC=$rc RECEIPT=$HERE RUN=$RUN"
  exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
connect() {
  ACTIVE_TARGET=$1
  echo "SSH password: $ACTIVE_TARGET (type only in this terminal)"
  ssh "${BASE[@]}" -o PubkeyAuthentication=no -o PreferredAuthentications=keyboard-interactive,password -o ControlMaster=yes -o ControlPersist=600 -S "$SOCKET_DIR/m" -Nf "$ACTIVE_TARGET"
}
disconnect() {
  ssh "${BASE[@]}" -S "$SOCKET_DIR/m" -O exit "$ACTIVE_TARGET"
  ACTIVE_TARGET=''
}
stage() {
  REMOTE_DIR=$(ssh "${BASE[@]}" -o BatchMode=yes -S "$SOCKET_DIR/m" "$ACTIVE_TARGET" 'umask 077; mktemp -d "$HOME/edge-access-precheck.XXXXXXXX"')
  [[ "$REMOTE_DIR" =~ ^/home/server08/edge-access-precheck\.[A-Za-z0-9]+$ ]] || { echo 'STOP: unexpected remote path'; exit 2; }
  scp "${BASE[@]}" -o BatchMode=yes -o ControlPath="$SOCKET_DIR/m" "$@" "$ACTIVE_TARGET:$REMOTE_DIR/"
}

# DB access proof: read-only transaction; no application rows are returned.
connect server08@10.1.93.55
stage db-readiness.sh db-readiness.sql DB_SHA256SUMS authenticated-check.sh AUTH_SHA256SUMS
printf '%s\n' "$REMOTE_DIR" > db-source-dir.txt
echo 'db01 server08 sudo password will be requested.'
set +e
timeout --foreground 240 ssh "${BASE[@]}" -o BatchMode=yes -S "$SOCKET_DIR/m" -tt "$ACTIVE_TARGET" "cd '$REMOTE_DIR' && sha256sum -c DB_SHA256SUMS AUTH_SHA256SUMS && bash authenticated-check.sh db '$RUN'" < /dev/tty > /dev/tty 2> /dev/tty
rc=$?
set -e
printf '%s\n' "$rc" > db-readiness.rc
scp "${BASE[@]}" -o BatchMode=yes -o ControlPath="$SOCKET_DIR/m" "$ACTIVE_TARGET:$REMOTE_DIR/result.stdout" db-readiness.stdout
scp "${BASE[@]}" -o BatchMode=yes -o ControlPath="$SOCKET_DIR/m" "$ACTIVE_TARGET:$REMOTE_DIR/result.stderr" db-readiness.stderr
cat db-readiness.stdout
test "$rc" = 0 || exit 3
grep -q '^DB_READONLY_ACCESS=READY' db-readiness.stdout || exit 3
disconnect

# Fresh cluster checks and immediate trace are run with existing managed access.
CTL=(ssh -i /home/server01_ansible/.ssh/p1_ansible_ed25519 "${BASE[@]}" -o BatchMode=yes -o IdentitiesOnly=yes svc_ansible@10.1.93.102)
CONTROL_DIR=$("${CTL[@]}" 'umask 077; mktemp -d "$HOME/edge-access-precheck.XXXXXXXX"')
[[ "$CONTROL_DIR" =~ ^/home/svc_ansible/edge-access-precheck\.[A-Za-z0-9]+$ ]] || exit 2
printf '%s\n' "$CONTROL_DIR" > control-source-dir.txt
scp -i /home/server01_ansible/.ssh/p1_ansible_ed25519 "${BASE[@]}" -o BatchMode=yes -o IdentitiesOnly=yes control01-cutover-check.sh CONTROL_SHA256SUMS "svc_ansible@10.1.93.102:$CONTROL_DIR/"
"${CTL[@]}" "cd '$CONTROL_DIR' && sha256sum -c CONTROL_SHA256SUMS"
set +e
timeout 120 "${CTL[@]}" "if ss -H -ltn 'sport = :19093' | grep -q .; then echo 'STOP: port 19093 already occupied'; exit 3; fi; sudo -n bash '$CONTROL_DIR/control01-cutover-check.sh' pre '$RUN'" > control-pre.stdout 2> control-pre.stderr
rc=$?
set -e
printf '%s\n' "$rc" > control-pre.rc
cat control-pre.stdout
test "$rc" = 0 || exit 3

connect server08@10.1.93.50
stage edge01-cutover.sh EDGE_SHA256SUMS authenticated-check.sh AUTH_SHA256SUMS
printf '%s\n' "$REMOTE_DIR" > edge-source-dir.txt
echo 'edge01 server08 sudo password will be requested. CHECK ONLY; no apply/reload/POST.'
set +e
timeout --foreground 240 ssh "${BASE[@]}" -o BatchMode=yes -S "$SOCKET_DIR/m" -tt "$ACTIVE_TARGET" "cd '$REMOTE_DIR' && sha256sum -c EDGE_SHA256SUMS AUTH_SHA256SUMS && bash authenticated-check.sh edge '$RUN'" < /dev/tty > /dev/tty 2> /dev/tty
rc=$?
set -e
printf '%s\n' "$rc" > edge-check.rc
scp "${BASE[@]}" -o BatchMode=yes -o ControlPath="$SOCKET_DIR/m" "$ACTIVE_TARGET:$REMOTE_DIR/result.stdout" edge-check.stdout
scp "${BASE[@]}" -o BatchMode=yes -o ControlPath="$SOCKET_DIR/m" "$ACTIVE_TARGET:$REMOTE_DIR/result.stderr" edge-check.stderr
cat edge-check.stdout
test "$rc" = 0 || exit 3
disconnect
TAG=$(sed -n 's/.*tag=\(check[0-9]\{6\}\).*/\1/p' edge-check.stdout | sort -u)
[[ "$TAG" =~ ^check[0-9]{6}$ ]] || { echo 'STOP: no unique check tag'; exit 3; }
printf '%s\n' "$TAG" > check-tag.txt
set +e
timeout 90 "${CTL[@]}" "sudo -n bash '$CONTROL_DIR/control01-cutover-check.sh' trace '$RUN' '$TAG'" > control-trace.stdout 2> control-trace.stderr
rc=$?
set -e
printf '%s\n' "$rc" > control-trace.rc
cat control-trace.stdout
test "$rc" = 0 || exit 3
grep -q '^RESULT cutover-check=TRACE_READY' edge-check.stdout || exit 3
grep -q "^TRACE k8s tag=$TAG err=0 verdict=TRACE_READY " control-trace.stdout || exit 3
echo 'COLLECTION_FINISHED: raw results need review; no automatic apply or AC acceptance.'
