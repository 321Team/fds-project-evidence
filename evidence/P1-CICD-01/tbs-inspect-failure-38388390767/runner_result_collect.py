import base64,datetime,hashlib,json,os,pathlib,socket,stat
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
root=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow.lnz0tdq8')
assert not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==0o700
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.getuid(),'read_only':True,'root':str(root),'files':{},'images':{},'missing':[]}
def read(name,required=True):
 p=root/name
 if not p.exists():
  if required:raise RuntimeError('MISSING_REQUIRED:'+name)
  out['missing'].append(name);return None
 for part in (p,*p.parents):assert not part.is_symlink()
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==1000 and s.st_nlink==1 and s.st_size<8*1024**2
 raw=p.read_bytes();s1=p.stat();assert (s.st_size,s.st_mtime_ns,s.st_ino)==(s1.st_size,s1.st_mtime_ns,s1.st_ino)
 out['files'][name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'mode':oct(stat.S_IMODE(s.st_mode)),'base64':base64.b64encode(raw).decode()}
 return raw
app=json.loads(read('result.json'));read('SHA256SUMS')
assert app['context']['run_id']=='38388390767' and app['context']['workflow_sha']=='fadc07f18b5bf7febc8cf601fa138d8f35e9ccb4' and app['context']['attempt']==1
read('handoff.json',False)
for folder,receipt in [('',app),('build-scan/',None),('build-scan/scan/',None),('build-scan/scan/db/',None)]:
 if receipt is None:
  raw=read(folder+'result.json',False)
  if raw is None:continue
  receipt=json.loads(raw);read(folder+'SHA256SUMS',False)
 for step in receipt.get('steps',[]):
  name=step['name'];assert '/' not in name and '..' not in name
  raw=read(folder+name+'.log')
  assert hashlib.sha256(raw).hexdigest()==step['log_sha256']
 if folder=='build-scan/':
  for name,identity in receipt.get('images',{}).items():
   assert name in ('transaction-api','fds-engine')
   p=root/folder/(name+'.oci.tar');s=p.lstat();assert stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1
   h=hashlib.sha256()
   with p.open('rb') as f:
    for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
   s1=p.stat();assert (s.st_size,s.st_mtime_ns,s.st_ino)==(s1.st_size,s1.st_mtime_ns,s1.st_ino)
   assert h.hexdigest()==identity['archive_sha256']
   out['images'][name]={'sha256':h.hexdigest(),'bytes':s.st_size,'copied_to_workstation':False}
   read(folder+name+'-image-smoke/container.cid',False)
 if folder=='build-scan/scan/':
  for name in ('transaction-api','fds-engine'):
   for filename in ('report.json','exit-code.txt'):read(folder+name+'/'+filename,False)
 if folder=='build-scan/scan/db/':read(folder+'cache/db/metadata.json',False)
out['workers']=[]
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
 try:
  if p.read_text().strip()=='Runner.Worker':out['workers'].append(int(p.parent.name))
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
print(json.dumps(out))
