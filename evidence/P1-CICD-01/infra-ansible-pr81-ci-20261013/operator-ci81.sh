#!/bin/bash
set -euo pipefail
umask 077
task_dir=/home/server01_cicd-runner/ci81-operator.NB1FQsGc
kit=/home/server01_cicd-runner/ansible-pr63-runner.nrPxm06G/FDS_Ansible_Actions_Runner_v1_3
guard=/home/server01_cicd-runner/ansible-pr63-runner.nrPxm06G/FDS_Ansible_Runner_Input_Guard_v1_0
prepared=/home/ansible-verify/ansible-actions-1c6c4123b62a4ebcb4b1b9042a02e332/evidence/PREPARED.json
packet=/home/server01_cicd-runner/ansible-runner-token-ci81-NB1FQsGc.json
source "$kit/common-start.sh"
check_login server01_cicd-runner cicd-runner01 /home/server01_cicd-runner
cd "$kit"
sha256sum -c SHA256SUMS > "$task_dir/bundle-check.txt"
cd "$guard"
sha256sum -c SHA256SUMS > "$task_dir/input-guard-check.txt"
cd "$task_dir"
exec 9> /home/server01_cicd-runner/ansible-ci-job-115077894860.lock
flock -n 9 || { echo STOP_DUPLICATE_OPERATOR; exit 1; }
cleanup() {
  task_rc=$?
  python3 - "$packet" <<'PY'
import os, stat, sys
from pathlib import Path
p=Path(sys.argv[1])
if p.exists() or p.is_symlink():
    i=p.lstat()
    if stat.S_ISREG(i.st_mode) and i.st_uid==os.getuid() and i.st_nlink==1:
        p.unlink()
        print('TOKEN_PACKET_DELETED')
    else:
        print('TOKEN_PACKET_DELETE_HOLD')
PY
  printf '%s\n' "$task_rc" > "$task_dir/operator.rc"
  date -Is > "$task_dir/operator-ended.txt"
}
trap cleanup EXIT
python3 - <<'PY'
import datetime
assert datetime.datetime.now(datetime.timezone.utc) >= datetime.datetime.fromisoformat('2026-10-13T11:15:00+09:00'), 'STOP_BEFORE_PREPARATION'
PY
python3 - <<'PY'
import datetime
assert datetime.datetime.now(datetime.timezone.utc) < datetime.datetime.fromisoformat('2026-10-13T11:45:00+09:00'), 'STOP_WINDOW_START_EXPIRED'
PY
echo 'Authenticate sudo in this terminal. Password is not logged or sent to the chat.'
sudo -v
sudo -n true
date -Is > "$task_dir/auth-ready.txt"
echo 'AUTH_READY: waiting up to 180 seconds for fresh CI preflight and token transfer.'
for ((task_wait=0; task_wait<180; task_wait++)); do
  if [[ -f "$task_dir/preflight.json" && -f "$packet" ]]; then break; fi
  sleep 1
done
[[ -f "$task_dir/preflight.json" && -f "$packet" ]] || { echo STOP_INPUT_TIMEOUT; exit 1; }
python3 - "$task_dir/preflight.json" <<'PY'
import json,sys,time
v=json.load(open(sys.argv[1]))
assert v['job']==115077894860 and v['run']==38330170015
assert v['head']=='874dc8bb052cfe3295fb79038872c785bbcc2592'
assert v['status']=='queued' and v['registered_runners']==0 and v['running_containers']==0
assert 0 <= time.time()-v['observed_at_unix'] <= 90
PY
python3 -I -B "$guard/safe_input.py" --token-file "$packet" 2>&1 | tee "$task_dir/input-guard-result.log"
sudo -n bash "$kit/run.sh" serve --prepared "$prepared" --token-file "$packet" 2>&1 | tee "$task_dir/serve.log"
