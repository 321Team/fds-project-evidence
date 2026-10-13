"""Mechanical fixed-file preparation or replacement; never runs deployed tools."""
import base64,datetime,hashlib,json,os,pathlib,socket,stat,subprocess,time
REQUEST=__REQUEST__
ROOT=pathlib.Path('/opt/fds/P1-K8S-01-v4')
BASE=pathlib.Path('/root/p1-k8s17-20261013-r1')
PHASE=REQUEST['phase'];HOST=REQUEST['host'];FILES=REQUEST['files'];SUPPLY=REQUEST['supply']
start=time.monotonic();end=start+(45 if PHASE=='apply' else 70)
out={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'phase':PHASE,'backup_root':str(BASE),'changed':[],'restored':[],'temporary_paths':[]}
def check(ok,why):
 if not ok:raise RuntimeError(why)
def budget():check(time.monotonic()<end,'BUDGET_EXHAUSTED')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def identity():return {'host':socket.gethostname(),'uid':os.geteuid(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'product_uuid':pathlib.Path('/sys/class/dmi/id/product_uuid').read_text().strip()}
def attrs(p):return {k:base64.b64encode(os.getxattr(p,k,follow_symlinks=False)).decode() for k in sorted(os.listxattr(p,follow_symlinks=False))}
def acl(p):
 r=subprocess.run(['/usr/bin/getfacl','-c','-p','-n','--',str(p)],capture_output=True,timeout=3,env=dict(os.environ,LC_ALL='C'))
 check(r.returncode==0,'ACL_READ');return r.stdout.decode().strip()
def meta(s):return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'size':s.st_size,'dev':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
def snapshot(p):
 budget();check(p.parent.resolve()==p.parent,'PATH_PARENT_LINK')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME|os.O_NONBLOCK)
 with os.fdopen(fd,'rb') as f:
  a=meta(os.fstat(f.fileno()));check(stat.S_ISREG(p.lstat().st_mode) and a['nlink']==1 and a['size']<2097152,'FILE_TYPE')
  x=attrs(p);ac=acl(p);raw=f.read(a['size']+1);b=meta(os.fstat(f.fileno()))
 check(a==b==meta(p.lstat()) and x==attrs(p) and len(raw)==a['size'],'UNSTABLE_READ')
 return {'path':str(p),'metadata':a,'xattrs':x,'acl':ac,'sha256':sha(raw)},raw
def comparable(s):return {k:s[k] for k in ['sha256','xattrs','acl']}|{'metadata':{k:s['metadata'][k] for k in ['uid','gid','mode','size','nlink','mtime_ns']}}
def inspect_all():return {r['path']:snapshot(pathlib.Path(r['path']))[0] for r in FILES}
def parents():
 result=[]
 for p in [pathlib.Path('/root'),pathlib.Path('/opt'),pathlib.Path('/opt/fds'),ROOT,ROOT/'code']:
  st=p.lstat();check(stat.S_ISDIR(st.st_mode) and p.resolve()==p and st.st_uid==0 and not stat.S_IMODE(st.st_mode)&0o022,'UNSAFE_PARENT')
  ac=acl(p);check(all(line.startswith(('user::','group::','other::')) for line in ac.splitlines()),'EXTENDED_PARENT_ACL')
  fs=os.statvfs(p);check(not fs.f_flag&os.ST_RDONLY and fs.f_bavail*fs.f_frsize>2097152 and fs.f_favail>32,'FILESYSTEM_NOT_READY')
  result.append({'path':str(p),'metadata':meta(st),'acl':ac,'xattrs':attrs(p)})
 return result
def processes():
 matches=[]
 for p in pathlib.Path('/proc').iterdir():
  if not p.name.isdigit() or int(p.name)==os.getpid():continue
  try:
   cmd=(p/'cmdline').read_bytes()
   if str(ROOT).encode() in cmd:matches.append({'pid':int(p.name),'comm':(p/'comm').read_text().strip()})
  except OSError:pass
 check(not matches,'TOOL_PROCESS_ACTIVE');return matches
def fsyncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def create(p,raw,m,x):
 check(p.parent.resolve()==p.parent,'DEST_PARENT_LINK')
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:
  f.write(raw);f.flush();os.fchown(f.fileno(),m['uid'],m['gid']);os.fchmod(f.fileno(),m['mode'])
  for key in os.listxattr(p,follow_symlinks=False):
   if key not in x:os.removexattr(p,key,follow_symlinks=False)
  for key,value in x.items():os.setxattr(p,key,base64.b64decode(value),follow_symlinks=False)
  os.utime(p,ns=(m['mtime_ns'],m['mtime_ns']),follow_symlinks=False);os.fsync(f.fileno())
 fsyncdir(p.parent)
def write_result(name,obj):
 raw=(json.dumps(obj,sort_keys=True,indent=2)+'\n').encode();p=BASE/name
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 fsyncdir(BASE);return sha(raw)
stages=[];prepared=None;backups={}
try:
 os.umask(0o077);who=identity();out['identity_before']=who
 check(who['uid']==0 and who['host']==HOST,'HOST_IDENTITY')
 check(pathlib.Path('/sys/fs/selinux/enforce').read_text().strip()=='1','SELINUX_NOT_ENFORCING')
 check(len(FILES)==9 and len({r['path'] for r in FILES})==9,'FILE_SCOPE')
 check(all(pathlib.Path(r['path']).is_relative_to(ROOT) and pathlib.Path(r['path']).parent in [ROOT,ROOT/'code'] for r in FILES),'PATH_SCOPE')
 replacements=[r for r in FILES if r['action']=='REPLACE'];check(len(replacements)==(1 if HOST=='k8s-control01' else 4),'REPLACE_SCOPE')
 parent_before=parents();out['process_snapshot']=processes();current=inspect_all()
 if PHASE=='prepare':
  for r in FILES:
   got=current[r['path']];m=got['metadata']
   check(got['sha256']==r['sha256'],'SOURCE_DRIFT')
   check((m['uid'],m['gid'],m['mode'])==(r['uid'],r['gid'],int(r['mode'],8)) and got['acl']==r['acl'].strip(),'METADATA_DRIFT')
   check(set(got['xattrs'])=={'security.selinux'} and base64.b64decode(got['xattrs']['security.selinux']).rstrip(b'\0').decode()==r['selinux'],'XATTR_DRIFT')
  check(not BASE.exists() and not BASE.is_symlink(),'BACKUP_PATH_EXISTS')
  BASE.mkdir(mode=0o700);fsyncdir(BASE.parent)
  for sub in ['backup','restore-trial','candidate']:(BASE/sub).mkdir(mode=0o700)
  prepared={'schema':'P1_K8S17_PREPARED_1','identity':who,'files':current,'parent_before':parent_before,'input_sha256':REQUEST['input_sha256'],'replacements':[]}
  for r in replacements:
   p=pathlib.Path(r['path']);name=p.name;before,raw=snapshot(p);check(before==current[str(p)],'DRIFT_BEFORE_BACKUP')
   create(BASE/'backup'/name,raw,before['metadata'],before['xattrs'])
   backup,braw=snapshot(BASE/'backup'/name);check(comparable(backup)==comparable(before),'BACKUP_MISMATCH')
   create(BASE/'restore-trial'/name,braw,before['metadata'],before['xattrs'])
   trial,_=snapshot(BASE/'restore-trial'/name);check(comparable(trial)==comparable(before),'RESTORE_TRIAL_MISMATCH')
   source=SUPPLY[name];new=base64.b64decode(source['content']);check(sha(new)==r['target_sha256']==source['sha256'],'SUPPLY_HASH');compile(new,name,'exec')
   target_m=dict(before['metadata'],uid=0,gid=0,mode=0o750,size=len(new))
   target_x={'security.selinux':base64.b64encode(b'system_u:object_r:usr_t:s0\0').decode()}
   create(BASE/'candidate'/name,new,target_m,target_x);candidate,_=snapshot(BASE/'candidate'/name)
   check(candidate['sha256']==r['target_sha256'] and candidate['acl']=='user::rwx\ngroup::r-x\nother::---' and candidate['xattrs']==target_x,'CANDIDATE_METADATA')
   prepared['replacements'].append({'path':str(p),'backup':backup,'restore_trial':trial,'candidate':candidate})
  check(inspect_all()==current,'DRIFT_DURING_PREPARE')
  prepared['status']='BACKUP_RESTORE_AND_CANDIDATE_VERIFIED';out['prepared_sha256']=write_result('PREPARED.json',prepared);out['prepared']=prepared;out['status']=prepared['status']
 elif PHASE=='apply':
  check(BASE.is_dir() and not BASE.is_symlink() and stat.S_IMODE(BASE.stat().st_mode)==0o700 and BASE.stat().st_uid==0,'BACKUP_ROOT')
  saved=BASE/'PREPARED.json';saved_meta,saved_raw=snapshot(saved);check(sha(saved_raw)==REQUEST['prepared_sha256'],'PREPARED_BINDING')
  prepared=json.loads(saved_raw);check(prepared['identity']==who and prepared['input_sha256']==REQUEST['input_sha256'],'PREPARED_IDENTITY')
  check(current==prepared['files'],'DRIFT_AFTER_PREPARE')
  for original,newparent in zip(prepared['parent_before'],parent_before):
   check(original['path']==newparent['path'] and original['acl']==newparent['acl'] and original['xattrs']==newparent['xattrs'],'PARENT_METADATA_DRIFT')
   check(all(original['metadata'][k]==newparent['metadata'][k] for k in ['uid','gid','mode','dev','inode']),'PARENT_IDENTITY_DRIFT')
  check(not (BASE/'APPLY_RESULT.json').exists(),'APPLY_ALREADY_RECORDED')
  for item in prepared['replacements']:
   p=pathlib.Path(item['path']);name=p.name
   backup,braw=snapshot(BASE/'backup'/name);check(comparable(backup)==comparable(item['backup']),'BACKUP_CHANGED');backups[str(p)]=(backup,braw)
   candidate,raw=snapshot(BASE/'candidate'/name);check(comparable(candidate)==comparable(item['candidate']),'CANDIDATE_CHANGED');compile(raw,name,'exec')
   stage=p.parent/('.p1-k8s17-r1-'+name);create(stage,raw,candidate['metadata'],candidate['xattrs']);stages.append(stage);out['temporary_paths'].append(str(stage))
   staged,_=snapshot(stage);check(comparable(staged)==comparable(candidate),'STAGED_MISMATCH')
  check(inspect_all()==current,'DRIFT_BEFORE_REPLACE');processes()
  for item,stage in zip(prepared['replacements'],stages):
   budget();p=pathlib.Path(item['path']);before,_=snapshot(p);check(before==current[str(p)],'TARGET_DRIFT_AT_REPLACE')
   os.replace(stage,p);out['changed'].append(str(p));fsyncdir(p.parent)
   after,_=snapshot(p);check(comparable(after)==comparable(item['candidate']),'POST_REPLACE_MISMATCH')
  after=inspect_all()
  for r in FILES:
   expected=next((x['candidate'] for x in prepared['replacements'] if x['path']==r['path']),current[r['path']])
   check(comparable(after[r['path']])==comparable(expected),'POST_ALL_MISMATCH')
  check(all(not p.exists() and not p.is_symlink() for p in stages),'TEMPORARY_REMAINS')
  out['after']=after;out['status']='APPLIED_AND_VERIFIED';out['identity_after']=identity();check(out['identity_after']==who,'IDENTITY_CHANGED')
  out['server_result_sha256']=write_result('APPLY_RESULT.json',out)
 else:raise RuntimeError('UNKNOWN_PHASE')
except Exception as e:
 out['status']='STOP';out['error']=type(e).__name__+':'+str(e)
 if PHASE=='apply' and out['changed']:
  try:
   end=start+70  # Reserve up to 25 seconds beyond the apply budget for file-only recovery.
   for path in reversed(out['changed']):
    p=pathlib.Path(path);backup,braw=backups[path];present,_=snapshot(p)
    expected=next(x['candidate'] for x in prepared['replacements'] if x['path']==path)
    check(comparable(present)==comparable(expected),'ROLLBACK_EXTERNAL_DRIFT')
    temp=p.parent/('.p1-k8s17-r1-restore-'+p.name);create(temp,braw,backup['metadata'],backup['xattrs']);check(comparable(snapshot(temp)[0])==comparable(backup),'ROLLBACK_STAGE')
    os.replace(temp,p);fsyncdir(p.parent);check(comparable(snapshot(p)[0])==comparable(backup),'ROLLBACK_MISMATCH');out['restored'].append(path)
   out['status']='RESTORED_WITH_KNOWN_TOOL_DEFECT'
  except Exception as failure:out['status']='HANDOFF_REQUIRED';out['rollback_error']=type(failure).__name__+':'+str(failure)
 # Partial preparations and exact owned staging are preserved for explicit inspection.
 if BASE.is_dir() and not BASE.is_symlink():
  try:out['failure_record_sha256']=write_result(PHASE.upper()+'_FAILURE.json',out)
  except Exception as failure:out['record_error']=type(failure).__name__+':'+str(failure)
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps(out))
raise SystemExit(0 if out['status'] in ['BACKUP_RESTORE_AND_CANDIDATE_VERIFIED','APPLIED_AND_VERIFIED'] else 2)
