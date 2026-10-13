#!/usr/bin/env bash
set -euo pipefail
set +x
umask 077
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
test "$(hostname -s)" = ansible01
sha256sum -c SHA256SUMS
mkdir execution-claim || exit 97
TARGET=server01_monitor@10.250.10.30
SOCKET=$PWD/ssh-control
SSH=(-o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ControlPath="$SOCKET")
finish() { ssh "${SSH[@]}" -O exit "$TARGET" >/dev/null 2>&1 || true; }
trap finish EXIT
ssh "${SSH[@]}" -o ControlMaster=yes -o ControlPersist=600 -Nf "$TARGET"
SSH+=(-o BatchMode=yes)
REMOTE=$(ssh "${SSH[@]}" "$TARGET" 'umask 077; mktemp -d /tmp/if06b-field.XXXXXXXX')
[[ "$REMOTE" =~ ^/tmp/if06b-field\.[A-Za-z0-9]+$ ]] || exit 2
printf '%s\n' "$REMOTE" > remote-stage.txt
scp "${SSH[@]}" collect.py field-remote.sh SOURCE_SHA256SUMS "$TARGET:$REMOTE/"
set +e
ssh -t "${SSH[@]}" "$TARGET" "bash '$REMOTE/field-remote.sh' '$REMOTE' monitor"
rc=$?
set -e
printf '%s\n' "$rc" > remote.rc
scp "${SSH[@]}" "$TARGET:$REMOTE/capture.tar.gz" "$TARGET:$REMOTE/capture.tar.gz.sha256" .
sha256sum -c capture.tar.gz.sha256
date -Is > completed.time
exit "$rc"
