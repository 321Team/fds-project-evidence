
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
