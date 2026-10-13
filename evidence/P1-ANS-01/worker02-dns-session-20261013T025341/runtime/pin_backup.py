from pathlib import Path
import json
from read_transport import run
from controller_transport import run as controller_run
R=Path(__file__).resolve().parent;P=R.parent
plan=json.loads((P/'EXECUTION_INPUT.json').read_bytes());s=json.loads((R/'prepare-VERIFIED.json').read_bytes())['session_receipt']
source='EXPECTED='+repr(s)+'\n'+'''import hashlib,json,os,pathlib,stat,datetime
assert os.uname().nodename=='k8s-worker02' and os.geteuid()==0
p=pathlib.Path(EXPECTED['path']);st=p.lstat();raw=p.read_bytes();d=json.loads(raw)
assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600
assert hashlib.sha256(raw).hexdigest()==EXPECTED['sha256'] and d['session_id']==EXPECTED['session_id'] and d['source_sha']==EXPECTED['source_sha']
assert stat.S_IMODE(p.parent.stat().st_mode)==0o700 and p.parent.stat().st_uid==0
assert set(os.listxattr(p,follow_symlinks=False))<= {'security.selinux'}
assert d['original']=={'interface':'ens160','connection':'fds-k8s-worker02','ipv4_dns':'10.1.93.52,10.1.93.53','ipv4_dns_search':'fds.internal','ipv4_ignore_auto_dns':'yes'}
print(json.dumps({'status':'BACKUP_BYTES_METADATA_VERIFIED','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':EXPECTED['sha256'],'path':str(p),'size':len(raw),'uid':st.st_uid,'gid':st.st_gid,'mode':'0600','parent_mode':'0700','selinux_context':os.getxattr(p,'security.selinux').decode().rstrip('\\0'),'data':d,'raw_utf8':raw.decode()}))
'''
r=run('backup-read','10.1.93.107',source,60);assert r['rc']==0
receipt=json.loads((R/'backup-read/stdout.json').read_bytes());pin={'session_id':s['session_id'],'source_sha':s['source_sha'],'sha256':s['sha256'],'path':s['path'],'captured_at':receipt['data']['captured_at'],'verified_worker_receipt':'backup-read/receipt.json'}
raw=(json.dumps(pin,indent=2)+'\n').encode();(R/'PINNED_BACKUP.json').write_bytes(raw);(R/'backup-read/original-resolver.json').write_bytes(receipt['raw_utf8'].encode())
source='RAW='+repr(raw)+'\nDEST='+repr(plan['controller_evidence_root']+'/PINNED_BACKUP.json')+'\n'+'''import hashlib,json,os,pathlib
assert os.uname().nodename=='ansible01' and os.geteuid()==1000
fd=os.open(DEST,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'wb') as f:f.write(RAW);f.flush();os.fsync(f.fileno())
assert pathlib.Path(DEST).read_bytes()==RAW
print(json.dumps({'status':'PIN_PRESERVED','path':DEST,'sha256':hashlib.sha256(RAW).hexdigest()}))
'''
r=controller_run('pin-controller',source);assert r['rc']==0
print('BACKUP_PINNED '+s['sha256'])
