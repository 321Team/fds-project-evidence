import datetime,hashlib,json,os,pathlib,socket,stat
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
p=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow.log3xwta/build-scan/scan/transaction-api.oci.tar')
for part in (p,*p.parents):assert not part.is_symlink()
s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==1000 and s.st_nlink==1 and s.st_size==93404160
h=hashlib.sha256()
with p.open('rb') as f:
    for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
assert h.hexdigest()=='218c57b0613dc37e9628745d3ae580886543902714bbb9ab6249b5ac90d1266f'
after=p.stat();assert (s.st_ino,s.st_size,s.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,'path':str(p),'relative':'build-scan/scan/transaction-api.oci.tar','bytes':s.st_size,'sha256':h.hexdigest(),'expected_match':True,'raw_copied':False}))
