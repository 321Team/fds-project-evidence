#!/usr/bin/env bash
set -euo pipefail
umask 077
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
MODE=${1:-}
RUN=${2:-}
[[ "$RUN" =~ ^[0-9]{8}T[0-9]{4}$ ]] || exit 2
case "$MODE:$(hostname -s)" in db:db01|edge:edge01) ;; *) echo 'STOP: unexpected host/mode'; exit 2;; esac
test -t 0 && test -t 1 || { echo 'STOP: interactive terminal required'; exit 2; }
TTY_STATE=$(stty -g < /dev/tty)
restore_tty() { stty "$TTY_STATE" < /dev/tty || true; }
trap restore_tty EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
stty -echo < /dev/tty
# Authentication is never piped, redirected to a receipt, or run in a background process group.
echo 'AUTHENTICATION ONLY: enter sudo password at the prompt; input echo is disabled.' > /dev/tty
sudo -v < /dev/tty > /dev/tty 2> /dev/tty || exit 3
echo 'Authentication finished. Recording read-only results now.' > /dev/tty
date -u +%FT%TZ > result.started-utc.txt
set +e
if test "$MODE" = db; then
  bash db-readiness.sh > result.stdout 2> result.stderr
  rc=$?
else
  printf '%s\n' '4d13819ab9ff50b34c4c783b0f48db058a22e6503e6df821b5b25feb5d74c562  /etc/nginx/conf.d/fds.conf' | sha256sum -c - > config-check.stdout 2> config-check.stderr
  rc=$?
  if test "$rc" = 0; then
    # The root-run approved check cannot reopen a password prompt inside recorded output.
    sudo -n -H bash "$HERE/edge01-cutover.sh" check "$RUN" > result.stdout 2> result.stderr
    rc=$?
  else
    printf '%s\n' 'STOP: configuration hash changed' > result.stdout
    : > result.stderr
  fi
fi
set -e
printf '%s\n' "$rc" > result.rc
date -u +%FT%TZ > result.finished-utc.txt
echo "READONLY_STEP_RC=$rc" > /dev/tty
exit "$rc"
