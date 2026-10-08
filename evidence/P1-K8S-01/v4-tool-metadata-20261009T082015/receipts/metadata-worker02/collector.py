"""Read fixed v4 tool metadata and bytes; no import/execute/deploy of tools."""
import datetime,errno,hashlib,json,os,pathlib,socket,stat,subprocess
EXPECTED_HOST='k8s-worker02'
FILES=('RUNBOOK_FINAL.md','code/audit-window.py','code/cluster-change.py','code/cockpit.sh','code/node-evidence.py','code/prepare-calico.py','code/probe.py','code/regression.py','code/render.py')
ROOT=pathlib.Path('/opt/fds/P1-K8S-01-v4')
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def gate():
    assert socket.gethostname()==EXPECTED_HOST and os.geteuid()==0,'STOP host/euid'
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00','STOP window'
def attrs(path):
    out={}
    for key in ('security.selinux','system.posix_acl_access','security.capability'):
        try:
            b=os.getxattr(path,key,follow_symlinks=False)
            out[key]={'status':'PRESENT','size':len(b),'sha256':hashlib.sha256(b).hexdigest()}
            if key=='security.selinux':out[key]['value']=b.rstrip(b'\0').decode('ascii')
        except OSError as e:out[key]={'status':'ABSENT' if e.errno==errno.ENODATA else 'READ_ERROR','errno':e.errno}
    return out
def metadata(s):
    return {'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)), 'size':s.st_size,'inode':s.st_ino,'dev':s.st_dev,'nlink':s.st_nlink,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
gate();out={'schema':'fds.k8s-tool-metadata.v1','host':socket.gethostname(),'started_at_kst':now(),'files':[],'parents':[],
           'boundary':'Read fixed9 files, selected xattrs and numeric getfacl only. No tool execution, backup, staging, metadata change, deployment or policy operation.',
           'backup':'NOT_CREATED','concurrent_invocation_exclusion':'NOT_ESTABLISHED','runtime_go':'NOT_GRANTED'}
try:out['selinux_enforce']=pathlib.Path('/sys/fs/selinux/enforce').read_text().strip()
except OSError as e:out['selinux_enforce']={'read_error_errno':e.errno}
for path in (pathlib.Path('/opt'),pathlib.Path('/opt/fds'),ROOT,ROOT/'code'):
    gate();s=path.lstat();assert stat.S_ISDIR(s.st_mode) and path.resolve()==path,'STOP parent/link'
    v=os.statvfs(path)
    out['parents'].append({'path':str(path),'metadata':metadata(s),'xattrs':attrs(path),'filesystem_readonly':bool(v.f_flag & os.ST_RDONLY)})
for name in FILES:
    gate();path=ROOT/name;row={'path':str(path)}
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_NOATIME)
        with os.fdopen(fd,'rb') as f:
            a=os.fstat(f.fileno());assert stat.S_ISREG(a.st_mode) and a.st_nlink==1 and a.st_size<2*1024*1024,'STOP type/link/size'
            before=attrs(path);raw=f.read(a.st_size+1)
            cmd=['getfacl','-c','-p','-n','--',str(path)]
            try:
                p=subprocess.run(cmd,capture_output=True,timeout=3,env={**os.environ,'LC_ALL':'C'})
                acl={'command':cmd,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
            except FileNotFoundError:acl={'command':cmd,'rc':127,'error':'getfacl unavailable; no install attempted'}
            except subprocess.TimeoutExpired:acl={'command':cmd,'rc':124,'error':'getfacl timeout'}
            after=attrs(path);b=os.fstat(f.fileno());c=path.lstat()
        stable=metadata(a)==metadata(b) and a.st_ino==c.st_ino and a.st_dev==c.st_dev and before==after
        row.update(metadata=metadata(a),sha256=hashlib.sha256(raw).hexdigest(),read_bytes=len(raw),xattrs=before,acl=acl,stable_during_read=stable,
                   status='COLLECTED' if stable and len(raw)==a.st_size and acl['rc']==0 and all(x['status']!='READ_ERROR' for x in before.values()) else 'INCOMPLETE')
    except (OSError,AssertionError) as e:row.update(status='INCOMPLETE',error_type=type(e).__name__,errno=getattr(e,'errno',None))
    out['files'].append(row)
out['finished_at_kst']=now();print(json.dumps(out))
