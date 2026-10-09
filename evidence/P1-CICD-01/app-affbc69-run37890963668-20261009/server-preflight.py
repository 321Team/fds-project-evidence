
import hashlib,json,os,pwd,shutil,socket,stat,subprocess,sys,datetime
from pathlib import Path
assert os.getuid()==os.geteuid()==1000 and pwd.getpwuid(1000).pw_name=='server01_cicd-runner'
assert socket.gethostname().split('.')[0]=='cicd-runner01'
stage=Path(sys.argv[1]);parent=Path('/home/server01_cicd-runner/FDS_CICD_Runtime')
target=parent/'FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a'
for p in [Path('/'),Path('/home'),parent.parent,parent,target,stage]:
 s=p.lstat();assert stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode) and not s.st_mode&0o022
assert target.stat().st_uid==stage.stat().st_uid==1000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(stage/'app-build-scan.generated.json')=='72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3'
assert (stage/'app-build-scan.generated.json').read_bytes()==(stage/'source/config/app-build-scan.json').read_bytes()
rows=(target/'SHA256SUMS').read_text().splitlines()
for line in rows:
 h,n=line.split('  ',1);p=target/n
 assert not p.is_symlink() and p.resolve().is_relative_to(target) and sha(p)==h
assert sha(target/'SUPPLY_MANIFEST.json')=='6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4'
free=shutil.disk_usage(parent).free;assert free>10*1024**3
env={'HOME':str(parent.parent),'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','XDG_RUNTIME_DIR':'/run/user/1000'}
p=subprocess.run(['/usr/bin/podman','ps','--format','{{.ID}} {{.Names}}'],env=env,capture_output=True,text=True,timeout=20)
assert p.returncode==0 and not p.stdout.strip(),'RUNNING_DEFAULT_STORE_CONTAINERS'
print(json.dumps({'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'account':'server01_cicd-runner',
 'uid':1000,'host':socket.gethostname(),'supply_manifest_files':len(rows),'config_sha256':sha(stage/'app-build-scan.generated.json'),
 'free_bytes':free,'default_store_running_containers':0,'runtime_dispatch':'NOT_YET_RUN'}))
