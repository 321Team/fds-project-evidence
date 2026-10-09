"""One preparation-only supply placement; no workflow dispatch or app execution."""
import base64
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT / 'cicd-candidate-intake'
COMMIT = 'c9eff5fb2e50a690818a3e67347ab4a1bfc88f51'
REVIEWED = 'b27210ee90521216ecd6eecae68737407e3aec86'
OUT = ROOT / 'private/materialize-affbc69-20261009'
OUT.mkdir(exist_ok=False)
KEY = '/home/server01_ansible/.ssh/p1_ansible_ed25519'
HOME = '/home/server01_cicd-runner'
PARENT = HOME + '/FDS_CICD_Runtime'
TARGET = PARENT + '/FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a'

def remote(cmd, data=None, timeout=60):
    nested = ['ssh', '-i', KEY, '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
              'server01_cicd-runner@10.250.10.20', cmd]
    p = subprocess.run(['ssh', '-o', 'BatchMode=yes', 'fds-ansible01', shlex.join(nested)],
                       input=data, capture_output=True, timeout=timeout)
    if p.returncode:
        (OUT / 'remote-error.txt').write_bytes(p.stderr)
        raise RuntimeError('REMOTE_COMMAND_FAILED_' + str(p.returncode))
    return p.stdout

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])

live = json.loads(subprocess.check_output(['gh', 'api', 'repos/321Team/infra-cicd/commits/main']))
assert live['sha'] == COMMIT
for repo in ('infra-cicd', 'infra-ansible'):
    for state in ('queued', 'in_progress'):
        v = json.loads(subprocess.check_output(['gh', 'api', f'repos/321Team/{repo}/actions/runs?status={state}']))
        assert v['total_count'] == 0
paths = git('ls-tree', '-r', '--name-only', COMMIT, 'tools/delivery', 'tools/trivy').decode().splitlines()
paths = [p for p in paths if p.endswith('.py') and not Path(p).name.startswith('test_')]
paths += ['config/app-build-scan.json', 'handoff/app-config-affbc69-20261009/SUPPLY_SOURCE.approved.json',
          'handoff/app-config-affbc69-20261009/TEST_SCOPE.approved.json']
payload = {}
for name in paths:
    raw = git('show', COMMIT + ':' + name)
    assert raw == git('show', REVIEWED + ':' + name)
    payload[name] = {'base64': base64.b64encode(raw).decode(), 'sha256': hashlib.sha256(raw).hexdigest()}
zip_path = ROOT / 'private/app-supply-37859961937/supply.zip'
zip_raw = zip_path.read_bytes()
assert len(zip_raw) == 109786915
assert hashlib.sha256(zip_raw).hexdigest() == '2f13771909415439bc5a4c83036284e665b47d023b6447b37e3e18c24ea2e3fd'
preflight = remote('python3 -I -B -', (ROOT / 'materialize-preflight-readonly.py').read_bytes())
(OUT / 'preflight.json').write_bytes(preflight)
v = json.loads(preflight)
assert v['free_bytes'] > 1024**3 and not v['readonly']
for x in v['paths'][:4]:
    assert x['exists'] and x['directory'] and not x['symlink']
    assert not (int(x['mode'], 8) & 0o022)
assert v['paths'][2]['uid'] == v['paths'][3]['uid'] == 1000
assert v['paths'][3]['writable'] and not v['paths'][4]['exists']
stage = remote('umask 077; mktemp -d /home/server01_cicd-runner/app-affbc69-prepare.XXXXXXXX').decode().strip()
assert stage.startswith(HOME + '/app-affbc69-prepare.') and len(stage.rsplit('.', 1)[1]) == 8
(OUT / 'session.json').write_text(json.dumps({'stage': stage, 'target': TARGET, 'source_commit': COMMIT,
    'scope': 'USER_REQUESTED_PRE_RUNTIME_SUPPLY_PREPARATION_ONLY', 'runtime_go': False}, indent=2), encoding='utf-8')
stager = r'''
import base64,hashlib,json,os,sys
from pathlib import Path
root=Path(sys.argv[1]); assert root.is_dir() and not root.is_symlink()
assert root.stat().st_uid==os.getuid()==1000 and root.stat().st_mode&0o777==0o700
os.umask(0o077)
for name,row in json.load(sys.stdin).items():
 assert not name.startswith('/') and all(x not in ('','..','.') for x in name.split('/'))
 raw=base64.b64decode(row['base64']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
 p=root/'source'/name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 with p.open('xb') as f:f.write(raw)
print('SOURCE_FILES_STAGED')
'''
remote('python3 -I -B -c ' + shlex.quote(stager) + ' ' + shlex.quote(stage), json.dumps(payload).encode())
with zip_path.open('rb') as stream:
    # Private SSH stdin transfer; archive bytes are never emitted to the chat.
    remote('umask 077; set -o noclobber; cat > ' + shlex.quote(stage + '/supply.zip'), stream.read(), timeout=180)
runner = r'''
import datetime,fcntl,hashlib,json,os,pwd,socket,stat,subprocess,sys,time
from pathlib import Path
stage=Path(sys.argv[1]); parent=Path('/home/server01_cicd-runner/FDS_CICD_Runtime')
target=parent/'FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a'
assert pwd.getpwuid(os.getuid()).pw_name=='server01_cicd-runner' and os.getuid()==os.geteuid()==1000
assert socket.gethostname().split('.')[0]=='cicd-runner01'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-09T17:00:00+09:00')
for p in [Path('/'),Path('/home'),parent.parent,parent,stage]:
 s=p.lstat();assert stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode) and not s.st_mode&0o022
assert parent.stat().st_uid==stage.stat().st_uid==1000
os.umask(0o077)
fd=os.open(str(parent.parent/'.affbc69-materialize.lock'),os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW,0o600)
assert os.fstat(fd).st_uid==1000 and os.fstat(fd).st_nlink==1
fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not os.path.lexists(target)
expected=json.load(open(stage/'source-files.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in expected.items():assert sha(stage/'source'/name)==h
assert sha(stage/'supply.zip')=='2f13771909415439bc5a4c83036284e665b47d023b6447b37e3e18c24ea2e3fd'
old=parent/'FDS_CICD_ApkoSupply.adc90410f99cb.f4d55db6ecbe'
before=old.stat(); old_binding=(before.st_dev,before.st_ino,before.st_mtime_ns,before.st_ctime_ns)
cmd=['/usr/bin/python3','-B',str(stage/'source/tools/delivery/materialize_app_build_scan_v3.py'),
 '--artifact-zip',str(stage/'supply.zip'),'--target-parent',str(parent),
 '--handoff',str(stage/'source/handoff/app-config-affbc69-20261009/SUPPLY_SOURCE.approved.json'),
 '--test-scope',str(stage/'source/handoff/app-config-affbc69-20261009/TEST_SCOPE.approved.json'),
 '--output',str(stage/'app-build-scan.generated.json')]
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
env={'HOME':str(parent.parent),'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'}
try:
 p=subprocess.run(cmd,cwd=stage,env=env,capture_output=True,timeout=120)
except subprocess.TimeoutExpired:
 print('STOP_MATERIALIZER_TIMEOUT_PRESERVE_STAGE');raise
(stage/'materialize.stdout').write_bytes(p.stdout);(stage/'materialize.stderr').write_bytes(p.stderr)
result={'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'command':cmd,'rc':p.returncode,'source_commit':'c9eff5fb2e50a690818a3e67347ab4a1bfc88f51',
 'application_runtime':'NOT_RUN','runner_dispatch':'NOT_RUN','push_deploy':'NOT_RUN','sudo':'NOT_USED'}
(stage/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
assert p.returncode==0,'STOP_MATERIALIZER_FAILURE_PRESERVE_STAGE'
generated=stage/'app-build-scan.generated.json';reviewed=stage/'source/config/app-build-scan.json'
assert generated.read_bytes()==reviewed.read_bytes(),'STOP_CONFIG_BYTE_MISMATCH_PRESERVE_STAGE'
rows=(target/'SHA256SUMS').read_text().splitlines()
for line in rows:
 h,n=line.split('  ',1);q=target/n
 assert not q.is_symlink() and q.resolve().is_relative_to(target) and sha(q)==h,n
s=old.stat();assert old_binding==(s.st_dev,s.st_ino,s.st_mtime_ns,s.st_ctime_ns)
result.update(status='MATERIALIZED_CONFIG_BYTE_IDENTICAL',config_sha256=sha(generated),
 verified_manifest_files=len(rows),target=str(target),old_supply_directory_metadata_unchanged=True,
 target_mode=oct(target.stat().st_mode&0o777),target_uid=target.stat().st_uid)
(stage/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
'''
hashes = {k: v['sha256'] for k, v in payload.items()}
remote('umask 077; set -o noclobber; cat > ' + shlex.quote(stage + '/source-files.json'), json.dumps(hashes).encode())
remote('umask 077; set -o noclobber; cat > ' + shlex.quote(stage + '/prepare-only.py'), runner.encode())
(OUT / 'prepare-only.py').write_text(runner, encoding='utf-8')
(OUT / 'source-files.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
# Materializer execution has no app, Podman, DB, workflow or credential action.
result = remote('python3 -I -B ' + shlex.quote(stage + '/prepare-only.py') + ' ' + shlex.quote(stage), timeout=150)
(OUT / 'result.json').write_bytes(result)
for name in ('materialize.stdout', 'materialize.stderr', 'RESULT.json', 'app-build-scan.generated.json'):
    (OUT / name).write_bytes(remote('cat ' + shlex.quote(stage + '/' + name)))
print(result.decode())
