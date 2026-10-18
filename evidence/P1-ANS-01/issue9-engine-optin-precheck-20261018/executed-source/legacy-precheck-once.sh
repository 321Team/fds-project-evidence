#!/usr/bin/env bash
# Reviewed execution candidate only. Do not execute before central input review.
# Run as a child under the exact env -i invocation in EXECUTION_PLAN.md.
set -Eeuo pipefail
umask 077
SRC=/home/server01_ansible/worker02-session-plan-3hetha3t/source
EXPECTED_HEAD=0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea
CANDIDATE=/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin
export SRC EXPECTED_HEAD CANDIDATE
cd -- "$SRC"
# No directory is created before this identity/source/input check succeeds.
/usr/bin/python3 -I -B - <<'PY'
import os,pathlib,pwd,stat,subprocess,hashlib,json,shlex
import yaml
P=pathlib.Path;H=P('/home/server01_ansible');S=P(os.environ['SRC'])
assert os.uname().nodename.split('.')[0]=='ansible01'
assert pwd.getpwuid(os.geteuid()).pw_name=='server01_ansible' and os.getuid()==os.geteuid()==1000 and os.getgid()==1000
assert P('/etc/machine-id').read_text().strip()=='17501f5b4e3f4fc1b97cdc82ffc45b83'
assert P('/proc/sys/kernel/random/boot_id').read_text().strip()=='0317c0f8-cdc9-4c5e-a28e-48961c75e62e'
def git(*args):
 r=subprocess.run(['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-c','core.untrackedCache=false','-C',str(S),*args],capture_output=True,check=True)
 return r.stdout.decode().strip()
assert git('rev-parse','HEAD')==os.environ['EXPECTED_HEAD']
assert not git('status','--porcelain','--untracked-files=no')
assert not git('ls-files','--others','--exclude-standard','--','inventory','roles','scripts','tools','library','module_utils','playbooks','ansible.cfg')
assert hashlib.sha256((S/'ansible.cfg').read_bytes()).hexdigest()=='73e6f6b5844a7a2dee8cf042b67a1c7b61c3e4b4198f4f7f7b65907e883de90e'
assert hashlib.sha256((S/'scripts/lib/ansible-engine.sh').read_bytes()).hexdigest()=='aedf6cd8d2fa656784e5f93e4d507582efb39755655d2e2ad0696e6353f316dd'
v=yaml.safe_load((S/'inventory/group_vars/all.yml').read_text())
assert v['cr_ntp_migrate_main'] is False and v['cr_ntp_source_upstreams']==[]
assert v['cr_ntp_change_id']=='CR-P1-NTP-01-01' and v['cr_ntp_source_host']=='k8s-control01' and v['cr_ntp_source_ip']=='10.1.93.102'
assert v['cr_ntp_client_ips']==['10.1.93.103','10.1.93.104','10.1.93.105','10.1.93.107','10.1.93.108']
assert v['cr_ntp_dropin_path']=='/etc/chrony.d/50-cr-p1-ntp-01-01.conf' and v['cr_ntp_offset_max_ms']==100
assert shlex.split(v['ansible_ssh_common_args'])==['-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=%d/.ssh/known_hosts','-o','IdentitiesOnly=yes']
inv=yaml.safe_load((S/'inventory/hosts.yml').read_text());nodes=inv['all']['children']['k8s_nodes']['children']
assert inv['all']['vars']['ansible_user']=='svc_ansible' and inv['all']['vars']['ansible_python_interpreter']=='/usr/bin/python3'
expected={'k8s-control01':'10.1.93.102','k8s-control02':'10.1.93.103','k8s-control03':'10.1.93.104','k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
actual={host:row['ansible_host'] for g in nodes.values() for host,row in g['hosts'].items()};assert actual==expected
for f in [H/'.ssh/p1_ansible_ed25519',H/'.ssh/known_hosts']:
 s=f.lstat();assert stat.S_ISREG(s.st_mode) and not stat.S_ISLNK(s.st_mode) and s.st_uid==1000 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
for binary in ['ansible','ansible-playbook','ansible-inventory','ansible-config']:
 f=P(os.environ['CANDIDATE'])/binary;assert f.is_file() and os.access(f,os.X_OK)
assert S.resolve()==S and H.resolve()==H
print('PREFLIGHT_IDENTITY_SOURCE_INPUT_MATCH')
PY

# A central one-shot claim must already name this invocation. No rerun on failure.
WORK=$(mktemp -d /home/server01_ansible/ntp-precheck-20261018.XXXXXXXX)
export WORK
mkdir -- "$WORK/tmp" "$WORK/cp" "$WORK/cli" "$WORK/evidence"
printf '%s\n' "$WORK" > "$WORK/OWNED_WORK_PATH"
date --iso-8601=seconds > "$WORK/STARTED_AT"
printf '%s\n' "$EXPECTED_HEAD" > "$WORK/EXPECTED_HEAD"
printf '%s\n' 'NTP_PRECHECK_ONLY_NO_APPLY_NO_ROLLBACK' > "$WORK/SCOPE"
export ANSIBLE_CONFIG="$SRC/ansible.cfg"
export ANSIBLE_PRIVATE_KEY_FILE=/home/server01_ansible/.ssh/p1_ansible_ed25519
export ANSIBLE_LOCAL_TEMP="$WORK/tmp"
export ANSIBLE_SSH_CONTROL_PATH_DIR="$WORK/cp"
export ANSIBLE_SSH_ARGS='-C -o ControlMaster=no -o ControlPersist=no -o ConnectionAttempts=1 -o ConnectTimeout=10 -o BatchMode=yes'
export ANSIBLE_HOST_KEY_CHECKING=True ANSIBLE_NOCOLOR=1 PYTHONDONTWRITEBYTECODE=1
export FDS_ANSIBLE_ENGINE_DIR="$CANDIDATE" FDS_ANSIBLE_ENGINE_VERSION=2.21.3
export CR_EVIDENCE_DIR="$WORK/evidence" CR_NTP_MIGRATE_MAIN=0
unset CR_CHANGE_APPROVED CR_NTP_RUNTIME_VARS_FILE CR_NTP_WORKFLOW_LOCK_FD
printf 'WORK=%s\n' "$WORK"
selected_rc=0
for cli in ansible ansible-playbook ansible-inventory ansible-config; do
  if "$CANDIDATE/$cli" --version > "$WORK/cli/selected-$cli.txt" 2>&1; then rc=0; else rc=$?; fi
  printf '%s\n' "$rc" > "$WORK/cli/selected-$cli.rc"
  first=$(head -n 1 "$WORK/cli/selected-$cli.txt")
  if [[ "$rc" != 0 || "$first" != "$cli [core 2.21.3]" ]]; then selected_rc=1; break; fi
done
printf '%s\n' "$selected_rc" > "$WORK/SELECTED_CLI_RC"
precheck_rc=125
if [[ "$selected_rc" == 0 ]]; then
  date --iso-8601=seconds > "$WORK/PRECHECK_STARTED_AT"
  # Existing wrapper performs its mandatory CLI4 check and controller lock itself.
  if /bin/bash "$SRC/scripts/cr-p1-ntp-01-01-run.sh" precheck > "$WORK/precheck.log" 2>&1; then precheck_rc=0; else precheck_rc=$?; fi
  date --iso-8601=seconds > "$WORK/PRECHECK_ENDED_AT"
fi
printf '%s\n' "$precheck_rc" > "$WORK/PRECHECK_RC"

# This process alone selected the candidate. Return via the existing helper to
# its explicit /usr/bin:/bin caller PATH; profiles and the user's shell are unchanged.
unset FDS_ANSIBLE_ENGINE_DIR FDS_ANSIBLE_ENGINE_VERSION
source "$SRC/scripts/lib/ansible-engine.sh"
fds_engine_init
return_rc=0
for cli in ansible ansible-playbook ansible-inventory ansible-config; do
  command -v "$cli" > "$WORK/cli/return-$cli.path"
  if fds_engine_exec "$cli" --version > "$WORK/cli/return-$cli.txt" 2>&1; then rc=0; else rc=$?; fi
  printf '%s\n' "$rc" > "$WORK/cli/return-$cli.rc"
  first=$(head -n 1 "$WORK/cli/return-$cli.txt")
  [[ "$rc" == 0 && "$first" == "$cli [core 2.16.19]" && "$(cat "$WORK/cli/return-$cli.path")" == "/usr/bin/$cli" ]] || return_rc=1
done
printf '%s\n' "$return_rc" > "$WORK/RETURN_CLI_RC"
git --no-optional-locks -C "$SRC" rev-parse HEAD > "$WORK/SOURCE_HEAD_AFTER"
git --no-optional-locks -C "$SRC" status --porcelain --untracked-files=no > "$WORK/SOURCE_STATUS_AFTER"
date --iso-8601=seconds > "$WORK/ENDED_AT"

# Normal foreground return only. Preserve logs and evidence; never remove the
# existing shared workflow lock or remote/other-session Ansible directories.
cleanup_rc=0
if [[ "$precheck_rc" -lt 128 ]]; then
 if /usr/bin/python3 -I -B - <<'PY'
import os,pathlib,stat,shutil,json,re
p=pathlib.Path(os.environ['WORK']);h=pathlib.Path('/home/server01_ansible')
assert p.parent==h and p.resolve()==p and re.fullmatch(r'ntp-precheck-20261018\.[A-Za-z0-9]{8}',p.name)
s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==os.geteuid()==1000 and stat.S_IMODE(s.st_mode)==0o700
removed=[]
for n in ['tmp','cp']:
 root=p/n;s=root.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==1000 and not root.is_symlink()
 for base,dirs,files in os.walk(root,followlinks=False):
  for child in dirs+files:
   q=pathlib.Path(base)/child;z=q.lstat();assert z.st_uid==1000 and not stat.S_ISLNK(z.st_mode)
   assert stat.S_ISDIR(z.st_mode) or (stat.S_ISREG(z.st_mode) and z.st_nlink==1)
 shutil.rmtree(root);removed.append(n)
(p/'LOCAL_TEMP_CLEANUP.json').write_text(json.dumps({'removed_owned_children':removed,'work_evidence_preserved':True,'remote_temp_absence_claimed':False})+'\n')
PY
 then cleanup_rc=0; else cleanup_rc=$?; fi
else
 cleanup_rc=125
fi
printf '%s\n' "$cleanup_rc" > "$WORK/LOCAL_TEMP_CLEANUP_RC"
printf 'SELECTED_CLI_RC=%s PRECHECK_RC=%s RETURN_CLI_RC=%s LOCAL_TEMP_CLEANUP_RC=%s WORK=%s\n' "$selected_rc" "$precheck_rc" "$return_rc" "$cleanup_rc" "$WORK"
[[ "$selected_rc" == 0 && "$precheck_rc" == 0 && "$return_rc" == 0 && "$cleanup_rc" == 0 && "$(cat "$WORK/SOURCE_HEAD_AFTER")" == "$EXPECTED_HEAD" && ! -s "$WORK/SOURCE_STATUS_AFTER" ]]
