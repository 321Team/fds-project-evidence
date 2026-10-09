import datetime,gzip,hashlib,io,json,os,pathlib,stat,tarfile,tempfile
os.umask(0o077)
root=pathlib.Path('/home/server01_cicd-runner/FDS_CICD_AppWorkflow.57rithja')
expected=json.loads(EXPECTED_JSON)
assert len(expected)==69 and sum(x['size'] for x in expected.values())==1632589467
folder=pathlib.Path(tempfile.mkdtemp(prefix='app-raw-handoff-37890963668-',dir=str(pathlib.Path.home())))
archive=folder/'app-raw-37890963668.tar.gz'
results=[]
class HashReader:
 def __init__(self,f):self.f=f;self.h=hashlib.sha256();self.count=0
 def read(self,n=-1):
  b=self.f.read(n);self.h.update(b);self.count+=len(b);return b
with archive.open('xb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',compresslevel=1,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w|') as tar:
 for name,info in sorted(expected.items()):
  parts=pathlib.PurePosixPath(name).parts
  assert parts and not name.startswith('/') and '..' not in parts
  p=root/name
  assert p.resolve()==p and root in p.parents
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb') as f:
   before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode) and before.st_size==info['size']
   reader=HashReader(f)
   member=tarfile.TarInfo(name);member.size=before.st_size;member.mode=0o600;member.mtime=int(before.st_mtime)
   tar.addfile(member,reader)
   after=os.fstat(f.fileno())
   assert (before.st_size,before.st_mtime_ns,before.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino)
   assert reader.count==info['size'] and reader.h.hexdigest()==info['sha256'],'ORIGINAL_MANIFEST_MISMATCH'
   results.append({'path':name,**info})
 receipt={'schema':'P1-CICD-private-raw-export-1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_run':37890963668,'source_attempt':1,'source_root':str(root),'expected_metadata_archive_sha256':'9dd174dafbbb0f8f198288e5bb7a747948cec97bff86b251db56eeffa6a56ff2','files':results,'status':'69_ORIGINAL_MANIFEST_HASHES_MATCH','originals_preserved':True,'scope':'manifest-listed raw payloads only; excludes container image store/internal caches and credentials not in manifest'}
 raw=(json.dumps(receipt,indent=2)+'\n').encode();member=tarfile.TarInfo('EXPORT_RECEIPT.json');member.size=len(raw);member.mode=0o600;tar.addfile(member,io.BytesIO(raw))
with archive.open('rb') as f:
 h=hashlib.sha256()
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
sidecar=folder/'app-raw-37890963668.tar.gz.sha256';sidecar.write_text(h.hexdigest()+'  '+archive.name+'\n')
receipt['archive']=str(archive);receipt['archive_bytes']=archive.stat().st_size;receipt['archive_sha256']=h.hexdigest()
(folder/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
