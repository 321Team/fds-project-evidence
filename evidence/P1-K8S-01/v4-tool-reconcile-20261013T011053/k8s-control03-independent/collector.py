"""Read fixed 9 tool files and 4 parent metadata sets. Never execute tool code."""
import datetime as dt,hashlib,json,os,pathlib,socket,stat,subprocess,time
EXPECTED_HOST='k8s-control03'
ROOT=pathlib.Path('/opt/fds/P1-K8S-01-v4')
FILES=('RUNBOOK_FINAL.md','code/audit-window.py','code/cluster-change.py','code/cockpit.sh','code/node-evidence.py','code/prepare-calico.py','code/probe.py','code/regression.py','code/render.py')
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def identity():return {'host':socket.gethostname(),'uid':os.geteuid(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'product_uuid':pathlib.Path('/sys/class/dmi/id/product_uuid').read_text().strip()}
before=identity();assert before['host']==EXPECTED_HOST and before['uid']==0,'STOP_HOST'
end=time.monotonic()+55
def check():assert time.monotonic()<end,'STOP_BUDGET'
def metadata(s):return {'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'size':s.st_size,'dev':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
def attrs(path):
    result={}
    for key in os.listxattr(path,follow_symlinks=False):
        value=os.getxattr(path,key,follow_symlinks=False)
        result[key]={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
        if key=='security.selinux':result[key]['value']=value.rstrip(b'\0').decode('ascii')
    return result
def acl(path):
    p=subprocess.run(['/usr/bin/getfacl','-c','-p','-n','--',str(path)],capture_output=True,timeout=3,env=dict(os.environ,LC_ALL='C'))
    return {'rc':p.returncode,'stdout':p.stdout.decode('utf-8','replace'),'stderr':p.stderr.decode('utf-8','replace')}
out={'started_at_utc':now(),'identity_before':before,'files':[],'parents':[],'errors':[],'scope':'Fixed files/parents read only; no file content export, tool invocation, backup, metadata mutation or service operation','concurrent_invocation_exclusion':'NOT_ESTABLISHED','server_backup':'NOT_CREATED','restore_test':'NOT_RUN','deliberate_guest_writes':0,'api_mutations':0}
out['selinux_enforce']=pathlib.Path('/sys/fs/selinux/enforce').read_text().strip()
parents=[pathlib.Path('/opt'),pathlib.Path('/opt/fds'),ROOT,ROOT/'code']
try:
    for path in parents:
        check();s=path.lstat();assert stat.S_ISDIR(s.st_mode) and path.resolve()==path,'STOP_PARENT_LINK'
        v=os.statvfs(path);a=attrs(path);ac=acl(path)
        out['parents'].append({'path':str(path),'metadata':metadata(s),'xattrs':a,'acl':ac,'readonly':bool(v.f_flag&os.ST_RDONLY),'free_bytes':v.f_bavail*v.f_frsize,'free_inodes':v.f_favail})
    for name in FILES:
        check();path=ROOT/name;row={'path':str(path)}
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_NOATIME)
            with os.fdopen(fd,'rb') as f:
                a=os.fstat(f.fileno());assert stat.S_ISREG(a.st_mode) and a.st_nlink==1 and a.st_size<2097152,'STOP_FILE_TYPE_OR_SIZE'
                xa=attrs(path);raw=f.read(a.st_size+1);ac=acl(path);xb=attrs(path);b=os.fstat(f.fileno());c=path.lstat()
            stable=metadata(a)==metadata(b)==metadata(c) and xa==xb and len(raw)==a.st_size
            row.update(metadata=metadata(a),sha256=hashlib.sha256(raw).hexdigest(),xattrs=xa,acl=ac,stable_during_read=stable,status='COLLECTED' if stable and ac['rc']==0 else 'INCOMPLETE')
        except (OSError,ValueError,AssertionError,subprocess.TimeoutExpired) as e:row.update(status='INCOMPLETE',error=type(e).__name__,errno=getattr(e,'errno',None))
        out['files'].append(row)
    for parent in out['parents']:
        path=pathlib.Path(parent['path']);parent['stable_during_collection']=parent['metadata']==metadata(path.lstat()) and parent['xattrs']==attrs(path)
    # Diagnostic process snapshot only; no full arguments or environment exported.
    matches=[]
    for p in pathlib.Path('/proc').iterdir():
        check()
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try:
            cmd=(p/'cmdline').read_bytes()
            if str(ROOT).encode() in cmd:matches.append({'pid':int(p.name),'comm':(p/'comm').read_text().strip()})
        except (OSError,UnicodeError):pass
    out['matching_process_snapshot']=matches
except (OSError,ValueError,AssertionError,subprocess.TimeoutExpired) as e:out['errors'].append({'error':type(e).__name__,'errno':getattr(e,'errno',None)})
out.update(identity_after=identity(),finished_at_utc=now());out['identity_unchanged']=before==out['identity_after']
good=out['identity_unchanged'] and not out['errors'] and len(out['files'])==9 and all(x['status']=='COLLECTED' for x in out['files']) and all(x['acl']['rc']==0 and x['stable_during_collection'] for x in out['parents'])
out['status']='COLLECTED_REVIEW_REQUIRED' if good else 'INCOMPLETE'
print(json.dumps(out));raise SystemExit(0 if good else 2)
