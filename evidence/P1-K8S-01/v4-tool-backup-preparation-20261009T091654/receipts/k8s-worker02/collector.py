"""Bounded read-only export of fixed tool bytes and restorable metadata."""
import base64
import datetime
import hashlib
import json
import os
import pathlib
import socket
import stat
import subprocess
import sys

SPEC = {'host': 'k8s-worker02', 'files': [{'path': '/opt/fds/P1-K8S-01-v4/RUNBOOK_FINAL.md', 'export': False, 'expected_sha256': 'b5388dc52071952608e6bcd642cda4d5a3d6d4c7d6ee8e820e8d4330b32c25c3'}, {'path': '/opt/fds/P1-K8S-01-v4/code/audit-window.py', 'export': True, 'expected_sha256': '75ea9962b84c064ad04a301a8086ecc7ab21c201ec86749a888715cf45a8a80b'}, {'path': '/opt/fds/P1-K8S-01-v4/code/cluster-change.py', 'export': True, 'expected_sha256': '07696cee257fde462f193d95f17c26415b10628e4aa2b58f6f3920a46cc18ff6'}, {'path': '/opt/fds/P1-K8S-01-v4/code/cockpit.sh', 'export': False, 'expected_sha256': 'bb8c951d25ff7176edfe7719e0a844f07816eec9cbf1a9cf1c0ab539995de7b1'}, {'path': '/opt/fds/P1-K8S-01-v4/code/node-evidence.py', 'export': True, 'expected_sha256': '318ac4b28c398de46dad6a7049400d75ac211f06fe5a2cfc88c4e64300039023'}, {'path': '/opt/fds/P1-K8S-01-v4/code/prepare-calico.py', 'export': False, 'expected_sha256': '205025f1b48c0103db945968e18184be519c56315ce3d3357d45439b7c80ddc9'}, {'path': '/opt/fds/P1-K8S-01-v4/code/probe.py', 'export': False, 'expected_sha256': 'd06ccc2a20770313475ae5e6f04dfba11ce433807b2c5139544f8cc2bd57c50c'}, {'path': '/opt/fds/P1-K8S-01-v4/code/regression.py', 'export': False, 'expected_sha256': '2955eafb6f39b1fd4dc574c784088a082582088ec60d1373b6186f887358810d'}, {'path': '/opt/fds/P1-K8S-01-v4/code/render.py', 'export': True, 'expected_sha256': 'fe0a99f364f7eaca6f726a4d280c8ff38c7a06652db809edaf3e8499adb5b71b'}]}
BASE = pathlib.Path('/opt/fds/P1-K8S-01-v4')
PARENTS = ['/opt', '/opt/fds', str(BASE), str(BASE / 'code')]

def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def gate():
    if socket.gethostname() != SPEC['host'] or os.geteuid() != 0:
        raise ValueError('HOST_OR_EUID')
    if not '2026-10-09T09:10:00+09:00' <= now() < '2026-10-09T12:00:00+09:00':
        raise ValueError('OUTSIDE_WINDOW')

def meta(s):
    return dict(uid=s.st_uid, gid=s.st_gid, mode=oct(stat.S_IMODE(s.st_mode)),
                size=s.st_size, dev=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                atime_ns=s.st_atime_ns, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)

def open_fixed(path, directory=False):
    # Open every ancestor without following links, not only the final file.
    parts=pathlib.PurePosixPath(path).parts[1:]
    fd=os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for index, part in enumerate(parts):
            flags=os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_NOATIME
            if index < len(parts)-1 or directory:
                flags |= os.O_DIRECTORY
            new_fd=os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd=new_fd
        return fd
    except BaseException:
        os.close(fd)
        raise

def xattrs(fd):
    names=sorted(os.listxattr(fd))
    if len(names)>16:
        raise ValueError('XATTR_COUNT_LIMIT')
    result={}
    total=0
    for name in names:
        raw=os.getxattr(fd,name)
        total+=len(raw)
        if len(raw)>16384 or total>65536:
            raise ValueError('XATTR_SIZE_LIMIT')
        result[name]=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                          content_base64=base64.b64encode(raw).decode('ascii'))
    return result

def collect(path, directory=False, export=False):
    gate()
    fd=open_fixed(path,directory)
    try:
        before=os.fstat(fd)
        if directory:
            if not stat.S_ISDIR(before.st_mode): raise ValueError('NOT_DIRECTORY')
        elif not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>131072:
            raise ValueError('FILE_TYPE_LINK_OR_SIZE')
        attrs=xattrs(fd)
        # getfacl reads the same open object; no shell or runtime tool invocation.
        argv=['/usr/bin/getfacl','-c','-p','-n','--','/proc/self/fd/'+str(fd)]
        p=subprocess.run(argv,pass_fds=(fd,),capture_output=True,timeout=3,
                         env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
        if p.returncode or p.stderr or len(p.stdout)>16384:
            raise ValueError('ACL_QUERY_FAILED')
        row=dict(path=path,metadata=meta(before),xattrs=attrs,
                 acl=dict(command=argv,rc=p.returncode,stdout=p.stdout.decode('ascii'),
                          stderr=p.stderr.decode('ascii')))
        if directory:
            v=os.fstatvfs(fd)
            row['filesystem']=dict(readonly=bool(v.f_flag & os.ST_RDONLY),
                                   available_bytes=v.f_bavail*v.f_frsize,
                                   available_inodes=v.f_favail)
        else:
            raw=b''
            while len(raw)<=before.st_size:
                block=os.read(fd,min(65536,before.st_size+1-len(raw)))
                if not block: break
                raw+=block
            if len(raw)!=before.st_size: raise ValueError('FILE_SIZE_CHANGED')
            row['sha256']=hashlib.sha256(raw).hexdigest()
            row['exported']=export
            if export:
                compile(raw,path,'exec')  # Parse only; no import, exec, or pycache.
                row['content_base64']=base64.b64encode(raw).decode('ascii')
                row['syntax']='COMPILED_NOT_EXECUTED'
        after=os.fstat(fd)
        if meta(before)!=meta(after) or attrs!=xattrs(fd):
            raise ValueError('OBJECT_CHANGED_DURING_READ')
        check_fd=open_fixed(path,directory)
        try:
            if meta(before)!=meta(os.fstat(check_fd)):
                raise ValueError('PATH_CHANGED_DURING_READ')
        finally: os.close(check_fd)
        row['stable_during_read']=True
        return row
    finally: os.close(fd)

def main():
    result=dict(schema='fds.k8s-tool-backup-readonly.v1',host=socket.gethostname(),
                started_at_kst=now(),files=[],parents=[],status='INCOMPLETE',
                remote_write=False,tool_execution='NOT_RUN',runtime_apply='NOT_RUN',
                restore_test='NOT_RUN',concurrent_writer_exclusion='NOT_ESTABLISHED',
                backup_readiness='NOT_ESTABLISHED',cross_file_atomic_snapshot=False)
    rc=2
    try:
        gate()
        result['selinux_enforce']=pathlib.Path('/sys/fs/selinux/enforce').read_text().strip()
        for path in PARENTS: result['parents'].append(collect(path,directory=True))
        for item in SPEC['files']:
            row=collect(item['path'],export=item['export'])
            result['files'].append(row)
            if row['sha256']!=item['expected_sha256']:
                raise ValueError('SOURCE_DRIFT')
        for parent in result['parents']:
            current=collect(parent['path'],directory=True)
            if current['metadata']!=parent['metadata'] or current['xattrs']!=parent['xattrs'] or current['acl']['stdout']!=parent['acl']['stdout']:
                raise ValueError('PARENT_CHANGED_DURING_COLLECTION')
        gate()
        result['status']='COLLECTED'
        rc=0
    except (OSError,ValueError,SyntaxError,subprocess.TimeoutExpired) as exc:
        result['error_type']=type(exc).__name__
        result['error_code']=str(exc) if isinstance(exc,ValueError) else 'READ_QUERY_OR_SYNTAX_ERROR'
        result['errno']=getattr(exc,'errno',None)
    result['finished_at_kst']=now()
    print(json.dumps(result,sort_keys=True))
    return rc

if __name__=='__main__': sys.exit(main())
