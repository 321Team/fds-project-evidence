#!/bin/bash
set -euo pipefail
umask 077
TASK_KIT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$TASK_KIT_ROOT/common-start.sh"
check_login server01_cicd-runner cicd-runner01 /home/server01_cicd-runner
cd -- "$TASK_KIT_ROOT"
sha256sum -c SHA256SUMS
TASK_STAGE=$(mktemp -d "$TASK_LOGIN_HOME/ansible-export-fix-readiness.XXXXXXXX")
mkdir -- "$TASK_STAGE/evidence"
cp -- EXPECTED.json "$TASK_STAGE/evidence/EXPECTED.json"
set +e
sudo runuser -u ansible-verify -- env -i HOME=/home/ansible-verify USER=ansible-verify LOGNAME=ansible-verify \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin LANG=C.UTF-8 \
  XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus \
  python3 -I -B - < "$TASK_KIT_ROOT/check-readiness.py" > "$TASK_STAGE/evidence/READINESS.json"
TASK_RC=$?
set -e
printf '%s\n' "$TASK_RC" > "$TASK_STAGE/evidence/execution.rc"
(cd -- "$TASK_STAGE/evidence" && sha256sum ./*.json execution.rc > SHA256SUMS)
tar -czf "$TASK_STAGE/ansible-export-fix-readiness.tar.gz" -C "$TASK_STAGE" evidence
(cd -- "$TASK_STAGE" && sha256sum ansible-export-fix-readiness.tar.gz > ansible-export-fix-readiness.tar.gz.sha256)
cat -- "$TASK_STAGE/evidence/READINESS.json"
printf 'HOME_READINESS=%s\n' "$TASK_STAGE/ansible-export-fix-readiness.tar.gz"
exit "$TASK_RC"
