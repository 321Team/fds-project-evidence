"""Bounded execution of user-approved OID commands; parameters injected by dispatch.
No registry calls, pod mutation, service changes, deletion, or automatic retry.
"""
import datetime,hashlib,json,os,pathlib,socket,stat,subprocess,time,tomllib
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
out={'host':socket.gethostname(),'started_at_utc':now(),'action':CFG['action'],'commands':[]}
root=pathlib.Path(CFG['plan']['root']);ctr=['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io']
def cmd(argv,timeout=10,keep=True):
 row={'argv':argv,'started_at_utc':now()};out['commands'].append(row)
 try:p=subprocess.run(argv,capture_output=True,timeout=timeout,env=dict(os.environ,LC_ALL='C'))
 except subprocess.TimeoutExpired as e:
  row.update(rc=None,status='TIMEOUT_NO_RETRY',stdout=(e.stdout or b'').decode(errors='replace'),stderr=(e.stderr or b'').decode(errors='replace'));raise
 row.update(rc=p.returncode,finished_at_utc=now(),stdout_bytes=len(p.stdout),stdout_sha256=sha(p.stdout),stderr=p.stderr.decode(errors='replace'))
 if keep:row['stdout']=p.stdout.decode(errors='replace')
 assert p.returncode==0,'COMMAND_FAILED:'+str(argv)
 return p.stdout
def refs():
 raw=cmd(ctr+['images','list']).decode();result={}
 for line in raw.splitlines()[1:]:
  v=line.split()
  if v:assert len(v)>=7;result[v[0]]={'type':v[1],'digest':v[2],'size_text':' '.join(v[3:5]),'platforms':v[5],'labels':v[6:]}
 return result
def check(job):
 for ref in job['refs']:
  raw=cmd(ctr+['images','check','name=='+ref]).decode();lines=[l.split() for l in raw.splitlines()[1:] if l.strip()]
  assert len(lines)==1 and lines[0][0]==ref and lines[0][2]==job['top_digest'] and lines[0][3]=='complete' and lines[0][-1]=='true','CACHE_NOT_COMPLETE_UNPACKED'
def guard():
 assert os.geteuid()==0 and socket.gethostname()==CFG['host'],'HOST_ROOT'
 boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip();out['boot']=boot;assert boot==CFG['boot'],'BOOT_DRIFT'
 assert sha(pathlib.Path('/usr/bin/ctr').read_bytes())=='a57b362df3a6029ddf8d398ff90d9e02ca68d37bca2ccc3e0f664deb7ae942c2','CTR_DRIFT'
 assert stat.S_ISSOCK(os.stat('/run/containerd/containerd.sock').st_mode)
 for p in ['/root','/var/lib/containerd']:
  v=os.statvfs(p);out.setdefault('space',[]).append({'path':p,'free_bytes':v.f_bavail*v.f_frsize});assert v.f_bavail*v.f_frsize>=2147483648,'SPACE'
 cmd(['/usr/bin/systemctl','is-active','containerd','kubelet'])
 cfg=cmd(['/usr/bin/containerd','--config','/etc/containerd/config.toml','config','dump'],keep=False)
 assert sha(cfg)==CFG['effective_sha'],'CONFIG_DRIFT'
 d=tomllib.loads(cfg.decode())['plugins'];assert d['io.containerd.cri.v1.images']['snapshotter']=='overlayfs'
 assert all(x.get('snapshotter') in [None,'','overlayfs'] for x in d['io.containerd.cri.v1.runtime']['containerd']['runtimes'].values())
 out['snapshotter']='overlayfs'
def write_new(p,raw):
 fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def archive_verify(job):
 raw=cmd(['/usr/bin/python3','-B','-I',str(root/'verify_archive.py'),str(root/'OBSERVED_SUPPLY.json'),job['image'],job['archive_path']],30)
 d=json.loads(raw);assert d['status']=='ARCHIVE_CLOSURE_VERIFIED';return d
try:
 guard();before=refs();out['refs_before']=before
 action=CFG['action'];jobs=CFG['jobs']
 if action in ['precheck','stage']:
  assert not root.exists() and not root.is_symlink(),'ROOT_EXISTS'
  for job in jobs:
   if CFG['host']=='k8s-control01':
    assert all(before[r]['digest']==job['top_digest'] for r in job['refs']);check(job)
   else:assert all(r not in before for r in job['refs']),'TARGET_REF_PRESENT'
  if CFG['host']=='k8s-control01' and action=='precheck':cmd(ctr+['images','list','--help'])
  if action=='stage':
   os.umask(0o077);root.mkdir(mode=0o700)
   for name,raw in CFG['files'].items():write_new(root/name,raw.encode())
   out['staged_files']={n:sha((root/n).read_bytes()) for n in CFG['files']}
 elif action=='export':
  assert CFG['host']=='k8s-control01' and len(jobs)==1
  job=jobs[0];assert not pathlib.Path(job['archive_path']).exists();check(job)
  os.umask(0o077);cmd(job['export_argv'],120)
  out['archive']=archive_verify(job);after=refs();out['refs_after']=after;assert before==after,'SOURCE_REFS_CHANGED'
 elif action=='import':
  assert CFG['host']!='k8s-control01' and len(jobs)==1
  job=jobs[0];assert all(r not in before for r in job['refs']),'TARGET_REF_PRESENT'
  out['archive']=archive_verify(job);assert out['archive']['archive_sha256']==CFG['archive_sha256'],'ARCHIVE_DRIFT'
  cmd(job['import_argv'],180)
  after=refs();out['refs_after']=after
  assert all(k in after and after[k]==v for k,v in before.items()),'EXISTING_REF_CHANGED'
  new=set(after)-set(before);expected=set(job['refs']);allowed=expected|{job['config_digest']}
  assert expected<=new and new<=allowed,'UNEXPECTED_NEW_REFS'
  assert all(after[r]['digest']==job['top_digest'] and 'io.cri-containerd.image=managed' in after[r]['labels'] for r in new),'REF_METADATA'
  out['added_refs']=sorted(new);check(job)
  start=time.monotonic();im=next(x for x in CFG['supply']['images'] if x['name']==job['image']);checks=[]
  wanted={im['approved_top_digest']:None,im['linux_amd64_manifest_digest']:None,im['config']['digest']:im['config']['size']}
  wanted.update({x['digest']:x['size'] for x in im['layers']})
  for dig,size in wanted.items():
   assert time.monotonic()-start<60,'VERIFY_BUDGET'
   b=cmd(ctr+['content','get',dig],timeout=15,keep=False)
   assert 'sha256:'+sha(b)==dig and (size is None or size==len(b)),'STORE_CONTENT_MISMATCH';checks.append({'digest':dig,'size':len(b)})
  out['store_content_verified']=checks
 elif action=='final':
  for job in jobs:check(job)
  initial=CFG['initial_refs'];assert all(k in before and before[k]==v for k,v in initial.items()),'OLD_REF_DRIFT'
  added=set(before)-set(initial);allowed=set()
  for job in jobs:allowed.update(job['refs']+[job['config_digest']])
  assert added<=allowed,'UNEXPECTED_REF_DRIFT'
  out['added_since_precheck']=sorted(added)
  assert root.is_dir() and not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==0o700
  out['private_files']=[]
  for p in sorted(root.iterdir()):
   s=p.lstat();assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==0,'PRIVATE_FILE_MODE'
   out['private_files'].append({'name':p.name,'size':s.st_size,'mode':'0600','uid':s.st_uid,'sha256':sha(p.read_bytes())})
 else:raise ValueError('ACTION')
 out['status']='STEP_VERIFIED'
except Exception as e:out.update(status='STOP_NO_RETRY',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='STEP_VERIFIED' else 2)
