#!/bin/bash
set -euo pipefail
umask 077
TASK_KIT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$TASK_KIT_ROOT/common-start.sh"
check_login server01_ansible ansible01 /home/server01_ansible
cd -- "$TASK_KIT_ROOT"
sha256sum -c SHA256SUMS
TASK_STAGE=$(mktemp -d "$TASK_LOGIN_HOME/ansible-export-fix-admin.XXXXXXXX")
mkdir -- "$TASK_STAGE/evidence"
cp -- EXPECTED.json "$TASK_STAGE/evidence/EXPECTED.json"
finish_preflight() {
  local rc=$?
  trap - EXIT
  printf '%s\n' "$rc" > "$TASK_STAGE/evidence/execution.rc"
  (cd -- "$TASK_STAGE/evidence" && sha256sum -- ./*.json execution.rc > SHA256SUMS)
  tar -czf "$TASK_STAGE/ansible-export-fix-preflight.tar.gz" -C "$TASK_STAGE" evidence
  (cd -- "$TASK_STAGE" && sha256sum ansible-export-fix-preflight.tar.gz > ansible-export-fix-preflight.tar.gz.sha256)
  printf 'HOME_PREFLIGHT=%s\n' "$TASK_STAGE/ansible-export-fix-preflight.tar.gz"
  exit "$rc"
}
trap finish_preflight EXIT
python3 -I -B "$TASK_KIT_ROOT/preflight.py" "$TASK_STAGE/evidence"
unzip -q "$TASK_KIT_ROOT/payload/FDS_Ansible_Admin_Token_v1_1_1.zip" -d "$TASK_STAGE"
cd -- "$TASK_STAGE/FDS_Ansible_Admin_Token_v1_1_1"
sha256sum -c SHA256SUMS
python3 -I -B admin-token.py
