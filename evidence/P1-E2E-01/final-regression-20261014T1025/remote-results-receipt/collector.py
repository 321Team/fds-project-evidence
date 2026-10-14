import base64,datetime,hashlib,json,os,pathlib,socket
assert socket.gethostname()=='edge01' and os.geteuid()==1003
p=pathlib.Path('/home/svc_ansible/p1-app-20261014-1025');rows=[]
files=[p/'supply/rg.py']+sorted((p/'results').glob('*'))
assert len(files)<=40
for f in files:
 assert f.is_file() and not f.is_symlink();raw=f.read_bytes();assert len(raw)<1048576
 rows.append({'relative':f.relative_to(p).as_posix(),'path':str(f),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'uid':f.stat().st_uid,'mode':oct(f.stat().st_mode&0o777),'base64':base64.b64encode(raw).decode()})
print(json.dumps({'host':socket.gethostname(),'uid':os.geteuid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'new_requests':0}))
