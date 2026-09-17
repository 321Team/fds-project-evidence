#!/bin/bash
set -euo pipefail
umask 077
TASK_KIT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$TASK_KIT_ROOT/common-start.sh"
check_login server01_cicd-runner cicd-runner01 /home/server01_cicd-runner
cd -- "$TASK_KIT_ROOT"
sha256sum -c SHA256SUMS
TASK_STAGE=$(mktemp -d "$TASK_LOGIN_HOME/ansible-actions-test-runner.XXXXXXXX")
unzip -q "$TASK_KIT_ROOT/payload/FDS_Ansible_Actions_Runner_v1_3.zip" -d "$TASK_STAGE"
unzip -q "$TASK_KIT_ROOT/payload/FDS_Ansible_Runner_Input_Guard_v1_0.zip" -d "$TASK_STAGE"
TASK_GUARD="$TASK_STAGE/FDS_Ansible_Runner_Input_Guard_v1_0"
TASK_RUNNER="$TASK_STAGE/FDS_Ansible_Actions_Runner_v1_3"
(cd -- "$TASK_GUARD" && sha256sum -c SHA256SUMS)
(cd -- "$TASK_RUNNER" && sha256sum -c SHA256SUMS)
read -r -p '홈에 비공개 복사한 token packet 파일명만 입력: ' TASK_TOKEN_NAME
[[ "$TASK_TOKEN_NAME" =~ ^ansible-runner-token-[A-Za-z0-9_-]+\.json$ ]] || stop 'token filename rejected; enter only the original basename'
TASK_TOKEN_PATH="$TASK_LOGIN_HOME/$TASK_TOKEN_NAME"
python3 -I -B "$TASK_GUARD/safe_input.py" --token-file "$TASK_TOKEN_PATH"
cd -- "$TASK_RUNNER"
sudo bash run.sh serve \
  --prepared /home/ansible-verify/ansible-actions-0965ce3ff3464f54acdddd46f24af4f6/evidence/PREPARED.json \
  --token-file "$TASK_TOKEN_PATH"
