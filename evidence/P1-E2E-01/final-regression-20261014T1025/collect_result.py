"""Read-only receipt of the one APP run; never rerun rg.py run."""
from pathlib import Path
import importlib.util,base64,hashlib,json
R=Path(__file__).resolve().parent;W=R.parent.parent
s=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t);t.OUT=R
source='''import base64,datetime,hashlib,json,os,pathlib,socket
assert socket.gethostname()=='edge01' and os.geteuid()==1003
p=pathlib.Path('/home/svc_ansible/p1-app-20261014-1025');rows=[]
files=[p/'supply/rg.py']+sorted((p/'results').glob('*'))
assert len(files)<=40
for f in files:
 assert f.is_file() and not f.is_symlink();raw=f.read_bytes();assert len(raw)<1048576
 rows.append({'relative':f.relative_to(p).as_posix(),'path':str(f),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'uid':f.stat().st_uid,'mode':oct(f.stat().st_mode&0o777),'base64':base64.b64encode(raw).decode()})
print(json.dumps({'host':socket.gethostname(),'uid':os.geteuid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'new_requests':0}))
'''
rc=t.run('remote-results-receipt','10.1.93.50',source,90,False);assert rc['rc']==0
x=json.loads((R/'remote-results-receipt/stdout.json').read_bytes());out=R/'remote-originals';out.mkdir(exist_ok=False)
for f in x['files']:
 p=Path(f['relative']);assert not p.is_absolute() and '..' not in p.parts
 raw=base64.b64decode(f['base64']);assert hashlib.sha256(raw).hexdigest()==f['sha256']
 dest=out/p;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_bytes(raw)
print(json.dumps({'files':len(x['files']),'directory':str(out)}))
