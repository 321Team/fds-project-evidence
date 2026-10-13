from pathlib import Path
import hashlib,json
from read_transport import run
from controller_transport import run as controller_run
R=Path(__file__).resolve().parent;P=R.parent
r=run('backup-final','10.1.93.107',(R/'backup-read/collector.py').read_text(),60);assert r['rc']==0
plan=json.loads((P/'EXECUTION_INPUT.json').read_bytes())
source='ROOT='+repr(plan['controller_evidence_root'])+'\n'+'''import datetime,hashlib,json,os,pathlib,stat
assert os.uname().nodename=='ansible01' and os.geteuid()==1000
root=pathlib.Path(ROOT);out={'host':'ansible01','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':ROOT,'files':[],'directories':[],'status':'PRIVATE_LOGS_COLLECTED'}
total=0
for p in [root]+sorted(root.rglob('*')):
 s=p.lstat();assert not p.is_symlink() and s.st_uid==1000
 if p.is_dir():
  assert stat.S_IMODE(s.st_mode)==0o700;out['directories'].append({'path':str(p),'mode':'0700','uid':s.st_uid})
 else:
  assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
  b=p.read_bytes();total+=len(b);assert len(b)<256000 and total<1048576
  out['files'].append({'path':p.relative_to(root).as_posix(),'uid':s.st_uid,'gid':s.st_gid,'mode':'0600','size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'raw_utf8':b.decode('utf-8')})
assert len(out['files'])<=40
print(json.dumps(out))
'''
r=controller_run('controller-logs',source,60);assert r['rc']==0
d=json.loads((R/'controller-logs/stdout.json').read_bytes());dest=R/'controller-files';dest.mkdir(exist_ok=False)
for item in d['files']:
 p=dest/item['path'];assert p.resolve().is_relative_to(dest.resolve());p.parent.mkdir(parents=True,exist_ok=True);raw=item['raw_utf8'].encode();assert hashlib.sha256(raw).hexdigest()==item['sha256'];p.write_bytes(raw)
for step in ['prepare','apply-check','apply','reapply','rollback-check','rollback']:
 d=json.loads((R/step/'stdout.json').read_bytes())
 for stream in ['stdout','stderr']:
  assert hashlib.sha256((dest/(step+'.'+stream+'.txt')).read_bytes()).hexdigest()==d[stream+'_sha256']
print(json.dumps({'status':'CLOSURE_FILES_VERIFIED','controller_files':sum(p.is_file() for p in dest.rglob('*'))}))
