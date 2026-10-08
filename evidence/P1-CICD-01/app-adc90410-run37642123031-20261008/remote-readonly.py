
import datetime,hashlib,json,os,pathlib,pwd,socket,stat,shutil
home=pathlib.Path(pwd.getpwuid(os.getuid()).pw_dir)
assert socket.gethostname().split('.')[0]=='cicd-runner01' and os.getuid()==1000 and pwd.getpwuid(os.getuid()).pw_name=='server01_cicd-runner'
assert home==pathlib.Path('/home/server01_cicd-runner') and home.stat().st_uid==1000 and stat.S_IMODE(home.stat().st_mode)==0o700
root=home/'FDS_CICD_Runtime/FDS_CICD_ApkoSupply.adc90410f99cb.f4d55db6ecbe'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert not root.is_symlink() and root.is_dir()
assert sha(root/'SUPPLY_MANIFEST.json')=='f4d55db6ecbefe2057cdb7ca6539b6818549744eb8bfc127ba12dcfa4eb6143b'
checked=[]
for line in (root/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split(maxsplit=1);name=name.lstrip('*')
 p=root/name
 assert p.resolve().is_relative_to(root.resolve()) and p.is_file() and not p.is_symlink(),name
 assert p.stat().st_uid==1000 and not(p.stat().st_mode&0o022),name
 assert sha(p)==digest,name
 checked.append(name)
assert len(checked)==125,len(checked)
free=shutil.disk_usage(home).free;assert free>=4*1024**3
active=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit() or p.stat().st_uid!=1000 or int(p.name)==os.getpid():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0')
  if any(a.endswith((b'app_workflow.py',b'build_scan.py',b'scan_images.py')) for a in args):active.append(p.name)
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
lock=home/'FDS_CICD_AppWorkflow.lock'
lock_rows=[]
if lock.exists():
 assert not lock.is_symlink() and lock.stat().st_uid==1000
 inode=str(lock.stat().st_ino)
 lock_rows=[s for s in pathlib.Path('/proc/locks').read_text().splitlines() if any(x.endswith(':'+inode) for x in s.split())]
assert not active and not lock_rows,'ACTIVE_SESSION'
print(json.dumps(dict(host=socket.gethostname(),uid=os.getuid(),home=str(home),free_bytes=free,supply_files_matched=len(checked),supply_manifest_sha256=sha(root/'SUPPLY_MANIFEST.json'),manifest_sha256=sha(root/'SHA256SUMS'),active_app_pids=active,workflow_lock_held=bool(lock_rows),checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2))
