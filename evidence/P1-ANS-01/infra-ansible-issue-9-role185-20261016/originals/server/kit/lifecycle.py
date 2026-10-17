"""Local-only command, evidence and bounded exact-object recovery primitives."""
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import socket
import stat
import subprocess
import time
import uuid

spec=importlib.util.spec_from_file_location('contract',Path(__file__).with_name('contract.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def now():return dt.datetime.now(dt.timezone.utc)
def error(exc):return {'type':type(exc).__name__,'message':str(exc)}

def secure(path):
    for p in (path,*path.parents):
        s=p.lstat()
        c.require(stat.S_ISDIR(s.st_mode) and not p.is_symlink(),'PATH_TYPE')
        c.require(s.st_uid in (0,os.getuid()) and not s.st_mode&0o022,'UNPROTECTED_PATH')

def host_identity(root):
    c.require(os.getuid()==c.HOST_UID and os.getgid()==c.HOST_GID and socket.gethostname()=='cicd-runner01','WRONG_HOST_USER')
    c.require(root.parent==Path('/home/ansible-verify') and re.fullmatch(r'p1-role-[0-9a-f]{16}',root.name),'WRONG_ROOT')
    secure(root)

def binding(control,root):
    c.require(control['session']==root.name and control['host']=='cicd-runner01'
              and control['host_uid']==c.HOST_UID and control['host_gid']==c.HOST_GID,'CONTROL_IDENTITY')
    c.require(control['boot']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'WRONG_BOOT_HANDOFF')
    start=dt.datetime.fromisoformat(control['not_before']);end=dt.datetime.fromisoformat(control['end_by'])
    c.require(start.utcoffset() is not None and end.utcoffset() is not None and start<end,'WINDOW_FORMAT')
    c.require(start<=now()<end,'OUTSIDE_RECOVERY_WINDOW')
    return end

class SessionLock:
    def __init__(self,root,create=False):self.path=root.parent/'.p1-standalone-fixture.lock';self.create=create;self.fd=None
    def __enter__(self):
        flags=os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK|(os.O_CREAT if self.create else 0)
        self.fd=os.open(self.path,flags,0o600)
        try:
            s=os.fstat(self.fd)
            c.require(stat.S_ISREG(s.st_mode) and s.st_uid==c.HOST_UID and s.st_gid==c.HOST_GID
                      and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,'LOCK_IDENTITY')
            fcntl.flock(self.fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            p=self.path.lstat()
            c.require(not self.path.is_symlink() and (p.st_dev,p.st_ino)==(s.st_dev,s.st_ino),'LOCK_PATH_CHANGED')
            return self
        except BaseException:
            os.close(self.fd);self.fd=None;raise
    def __exit__(self,*_):
        if self.fd is not None:os.close(self.fd);self.fd=None

def assert_no_active(root,cid=None):
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try:
            if p.stat().st_uid!=c.HOST_UID:continue
            args=(p/'cmdline').read_bytes().split(b'\0')
        except (FileNotFoundError,ProcessLookupError):continue
        names=[os.path.basename(x) for x in args]
        own=any(root.name.encode() in x for x in args)
        controller=any(x in names for x in (b'host_session.py',b'cleanup_session.py')) and own
        podman=b'podman' in names and (own or bool(cid and cid.encode() in args))
        c.require(not controller and not podman,'ACTIVE_SESSION_COMMAND_HANDOFF')

class Evidence:
    def __init__(self,root,prefix):self.root=root;self.prefix=prefix+'-'+uuid.uuid4().hex;self.errors=[]
    def save(self,name,value,required=False,raw=False):
        path=self.root/(self.prefix+'-'+name)
        try:
            data=value if raw else (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
            c.atomic_record(path,data)
            return True
        except OSError as exc:
            self.errors.append({'file':path.name,**error(exc)})
            if required:raise
            return False
    def fixed(self,name,value):
        # Mandatory once-only provenance; caller separates this failure from recovery.
        c.atomic_record(self.root/name,(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())

class CommandFailure(RuntimeError):
    def __init__(self,row):self.row=row;super().__init__(row['status']+':'+str(row['argv'][3:5]))

class Commands:
    def __init__(self,evidence):self.e=evidence;self.rows=[];self.sequence=0;self.mutations={};self.deadline=None;self.end=None
    def run(self,args,timeout=30,allowed=(0,),mutation=False,recovery=False):
        argv=c.podman_argv(*args)
        action=args[0];self.sequence+=1
        tag=f'{self.sequence:04d}-{action}'
        row={'argv':argv,'started_at_utc':now().isoformat(),'status':'INTENT_ONLY'}
        if mutation:
            c.require(self.mutations.get(action,0)==0,'DUPLICATE_MUTATION:'+action)
        if self.deadline is not None:
            timeout=min(timeout,self.deadline-time.monotonic())
        if self.end is not None:timeout=min(timeout,(self.end-now()).total_seconds())
        c.require(timeout>0,'COMMAND_BUDGET_EXHAUSTED')
        row['timeout_seconds']=timeout
        self.e.save(tag+'.intent.json',row,required=mutation and not recovery)
        if mutation:self.mutations[action]=1
        problem=None;raw_stdout=None;raw_stderr=None
        row['raw_capture']='NOT_CAPTURED'
        try:
            result=subprocess.run(argv,capture_output=True,timeout=timeout,env=c.podman_environment())
            raw_stdout=result.stdout;raw_stderr=result.stderr
            row.update(raw_capture='RETURNED_BYTES',rc=result.returncode,
                       status='RETURNED' if result.returncode in allowed else 'COMMAND_FAILED')
            if result.returncode not in allowed:problem=CommandFailure(row)
        except subprocess.TimeoutExpired as exc:
            raw_stdout=exc.stdout;raw_stderr=exc.stderr
            row.update(status='TIMEOUT_UNCONFIRMED',raw_capture='PARTIAL_TIMEOUT_BYTES')
            self.e.errors.append({'operation':'raw_capture_partial_timeout','command':tag,
                                  'note':'Only bytes returned by TimeoutExpired are available; full output is unconfirmed.'})
            problem=CommandFailure(row)
        except (OSError,KeyboardInterrupt) as exc:
            row.update(status='INTERRUPTED_OR_LAUNCH_FAILED_UNCONFIRMED',cause=error(exc),raw_capture='UNAVAILABLE')
            self.e.errors.append({'operation':'raw_capture_unavailable','command':tag,**error(exc)})
            problem=CommandFailure(row)
        finally:
            row['ended_at_utc']=now().isoformat();self.rows.append(row)
            # Raw bytes are evidence; JSON text is only a lossy display derivative.
            row['text_derivation']='UTF-8 decode with replacement; raw files are authoritative'
            row['raw_channels']={}
            for name,raw in (('stdout',raw_stdout),('stderr',raw_stderr)):
                row[name]=raw.decode('utf-8','replace') if raw is not None else None
                channel={'capture':'UNAVAILABLE','bytes':None,'sha256':None,'file':None}
                if raw is not None:
                    channel.update(capture='COMPLETE_RETURNED' if row['raw_capture']=='RETURNED_BYTES' else 'PARTIAL_RETURNED',
                                   bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),file=self.e.prefix+'-'+tag+'.'+name)
                    channel['stored']=self.e.save(tag+'.'+name,raw,raw=True)
                row['raw_channels'][name]=channel
            self.e.save(tag+'.completion.json',row)
        if problem:raise problem
        return row

class Signals:
    def __init__(self):self.recovering=False;self.events=[];self.old={}
    def handler(self,number,_):
        self.events.append({'signal':number,'at':now().isoformat(),'recovering':self.recovering})
        if not self.recovering:raise KeyboardInterrupt('SIGNAL:'+str(number))
    def __enter__(self):
        for s in (signal.SIGINT,signal.SIGTERM):self.old[s]=signal.signal(s,self.handler)
        return self
    def __exit__(self,*_):
        for s,handler in self.old.items():signal.signal(s,handler)

def inspected(commands,cid,root,sha):
    row=commands.run(['inspect',cid]);values=json.loads(row['stdout'])
    c.require(isinstance(values,list) and len(values)==1,'INSPECT_SHAPE')
    value=values[0];c.assert_owned(value,cid,root.name,sha)
    c.assert_saved_identity(root,cid,root.name,sha)
    return value

def assert_local_store(commands,control):
    c.require(control.get('podman_binary')==c.PODMAN,'PODMAN_BINDING_MISSING_OR_CHANGED')
    expected=control.get('store')
    c.require(isinstance(expected,dict) and set(expected)=={'graphRoot','runRoot'}
              and all(isinstance(v,str) and v.startswith('/') for v in expected.values()),'STORE_BINDING_MISSING_OR_INVALID')
    info=json.loads(commands.run(['info','--format','json'])['stdout'])
    c.require(info['host']['security']['rootless'] is True,'RECOVERY_NOT_ROOTLESS')
    c.require({key:info['store'][key] for key in expected}==expected,'STORE_IDENTITY_CHANGED')

def preserve_recovery_identity(commands,root,value,cid,control):
    sha=control['manifest_sha256'];name=root.name
    c.assert_owned(value,cid,name,sha)
    path=root/'OWNED_IDENTITY.json'
    previous=c.read_protected_record(path)
    if previous is not None:
        c.require(c.identity_cid(json.loads(previous),name,sha)==cid,'IDENTITY_CHANGED')
        return True
    record={'schema':1,'cid':cid,'session':name,'image':c.IMAGE,'manifest_sha256':sha}
    try:c.atomic_record(path,(json.dumps(record,sort_keys=True,indent=2)+'\n').encode('ascii'))
    except OSError as exc:
        commands.e.errors.append({'operation':'recovery_identity_publish',**error(exc)})
        # Read failure, partial data or a conflicting final is not a harmless write failure.
        after=c.read_protected_record(path)
        if after is None:return False
        c.require(c.identity_cid(json.loads(after),name,sha)==cid,'IDENTITY_CHANGED')
    return True

def recover(commands,root,control,cid,signals):
    result={'status':'HANDOFF','cid':cid,'error':None}
    signals.recovering=True
    try:
        commands.end=binding(control,root)
        commands.deadline=time.monotonic()+180
        assert_no_active(root,cid)
        # Verify durable identity conflicts even if existence is already false.
        c.assert_saved_identity(root,cid,root.name,control['manifest_sha256'])
        assert_local_store(commands,control)
        r=commands.run(['container','exists',cid],15,allowed=(0,1))
        if r['rc']==1:
            result['status']='ALREADY_ABSENT';return result
        value=inspected(commands,cid,root,control['manifest_sha256'])
        result['identity_preserved_for_reentry']=preserve_recovery_identity(commands,root,value,cid,control)
        if not result['identity_preserved_for_reentry']:
            result['identity_limitation']='Durable identity unavailable; rm also removes CID file. Later automatic reentry may require handoff; do not guess by name.'
        commands.e.save('RECOVERY_BEFORE.json',value)
        if value['State']['Running']:
            binding(control,root);assert_no_active(root,cid)
            commands.run(['stop','--time','30',cid],45,mutation=True,recovery=True)
        value=inspected(commands,cid,root,control['manifest_sha256'])
        c.require(not value['State']['Running'],'STOP_NOT_CONFIRMED')
        commands.e.save('RECOVERY_TERMINAL.json',value)
        binding(control,root);assert_no_active(root,cid)
        commands.run(['rm',cid],30,mutation=True,recovery=True)
        absent=commands.run(['container','exists',cid],15,allowed=(0,1))
        c.require(absent['rc']==1,'REMOVAL_UNCONFIRMED')
        assert_no_active(root,cid)
        result.update(status='OWN_CONTAINER_REMOVED',absence_query_rc=1)
    except (Exception,KeyboardInterrupt) as exc:result['error']=error(exc)
    finally:
        commands.e.save('RECOVERY_RESULT.json',result)
    return result

def finish(evidence,commands,execution,cleanup,initial_error,signals=None):
    report={'execution':execution,'cleanup':cleanup,'initial_error':initial_error,
            'evidence':'INCOMPLETE' if evidence.errors else 'COMPLETE','evidence_errors':evidence.errors,
            'signals':signals.events if signals else [],'production_runtime':False,'phase1_acceptance':False}
    evidence.save('COMMANDS.json',commands.rows)
    # This snapshot may predate its own persistence error; stdout below is authoritative for that error.
    report['evidence']='INCOMPLETE' if evidence.errors else 'COMPLETE'
    evidence.save('FINAL.json',report)
    report['evidence']='INCOMPLETE' if evidence.errors else 'COMPLETE'
    print(json.dumps(report,ensure_ascii=False))
    return 0 if execution in ('PASS_LOCAL_ROLE_FIXTURES','RECOVERY_ONLY') and cleanup.get('status') in ('OWN_CONTAINER_REMOVED','ALREADY_ABSENT') and not evidence.errors else 1
