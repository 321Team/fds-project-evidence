#!/bin/bash
set -euo pipefail
umask 077
TASK_KIT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$TASK_KIT_ROOT/common-start.sh"
check_login server01_ansible ansible01 /home/server01_ansible
cd -- "$TASK_KIT_ROOT"
sha256sum -c SHA256SUMS
TASK_STAGE=$(mktemp -d "$TASK_LOGIN_HOME/ansible-actions-test-admin.XXXXXXXX")
mkdir -- "$TASK_STAGE/evidence"
finish_preflight() {
  local rc=$?
  trap - EXIT
  printf '%s\n' "$rc" > "$TASK_STAGE/evidence/execution.rc"
  (cd -- "$TASK_STAGE/evidence" && sha256sum -- ./*.json execution.rc > SHA256SUMS)
  tar -czf "$TASK_STAGE/ansible-actions-test-preflight.tar.gz" -C "$TASK_STAGE" evidence
  (cd -- "$TASK_STAGE" && sha256sum ansible-actions-test-preflight.tar.gz > ansible-actions-test-preflight.tar.gz.sha256)
  printf 'HOME_PREFLIGHT=%s\n' "$TASK_STAGE/ansible-actions-test-preflight.tar.gz"
  exit "$rc"
}
printf '{"run_id":35139314896,"attempt":1,"source_commit":"2750634766862d7fe19479acacc4259ee8315061"}\n' > "$TASK_STAGE/evidence/EXPECTED.json"
trap finish_preflight EXIT
gh api --hostname github.com --method GET repos/321Team/infra-ansible/pulls/20 > "$TASK_STAGE/evidence/pr.json"
gh api --hostname github.com --method GET repos/321Team/infra-ansible/actions/runs/35139314896 > "$TASK_STAGE/evidence/run.json"
gh api --hostname github.com --method GET 'repos/321Team/infra-ansible/actions/runs/35139314896/attempts/1/jobs?per_page=100' > "$TASK_STAGE/evidence/jobs.json"
python3 -I -B - "$TASK_STAGE/evidence" <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
pr, run, jobs = [json.loads((d / n).read_text()) for n in ('pr.json','run.json','jobs.json')]
sha = '2750634766862d7fe19479acacc4259ee8315061'
repo = '321Team/infra-ansible'
valid = (pr['state'] == 'open' and pr['head']['sha'] == sha and pr['head']['repo']['full_name'] == repo
         and run['id'] == 35139314896 and run['run_attempt'] == 1 and run['head_sha'] == sha
         and run['repository']['full_name'] == repo and run['event'] == 'pull_request'
         and run['status'] == 'queued' and run['conclusion'] is None
         and jobs['total_count'] == len(jobs['jobs']) == 1)
if valid:
    job = jobs['jobs'][0]
    valid = (job['run_id'] == run['id'] and job['run_attempt'] == 1 and job['head_sha'] == sha
             and job['name'] == 'regression' and job['status'] == 'queued' and job['conclusion'] is None
             and set(job['labels']) == {'self-hosted','Linux','X64','fds-ci','ansible-isolated'})
(d / 'PREFLIGHT.json').write_text(json.dumps({'status':'PASS_QUEUED_SOURCE' if valid else 'FAIL_STATE_CHANGED',
                                          'run_id':run.get('id'),'attempt':run.get('run_attempt')},indent=2)+'\n')
if not valid:
    raise SystemExit('STOP: Run/PR/Job changed or no longer queued; do not issue another token')
print('STATUS=PASS_QUEUED_SOURCE')
PY
unzip -q "$TASK_KIT_ROOT/payload/FDS_Ansible_Admin_Token_v1_1_1.zip" -d "$TASK_STAGE"
cd -- "$TASK_STAGE/FDS_Ansible_Admin_Token_v1_1_1"
sha256sum -c SHA256SUMS
python3 -I -B admin-token.py
