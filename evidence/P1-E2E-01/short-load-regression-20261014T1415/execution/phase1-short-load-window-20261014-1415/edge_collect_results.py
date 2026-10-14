import base64,datetime,hashlib,json,os,pathlib,socket
assert socket.gethostname()=='edge01' and os.geteuid()==1003
p=pathlib.Path('/home/svc_ansible/p1-short-load-202610141415');rows=[]
files=[p/'supply/gen3.py',p/'criteria.txt']+sorted((p/'results').glob('*'))
assert (p/'results/completion.json').is_file() and len(files)<=12
for f in files:
    assert f.is_file() and not f.is_symlink() and f.stat().st_uid==1003
    raw=f.read_bytes();assert len(raw)<2*1024*1024
    rows.append({'relative':f.relative_to(p).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'uid':f.stat().st_uid,'mode':oct(f.stat().st_mode&0o777),'base64':base64.b64encode(raw).decode()})
print(json.dumps({'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'mutation':False}))
