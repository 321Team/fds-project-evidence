"""Pure contract for the standalone fixture, never the GitHub Runner."""
from pathlib import PurePosixPath
import json
import os
import re
import stat
import uuid
import ctypes

IMAGE='sha256:e8565fa265f973c06f0515fac7aa9d102edae01b5677d69216900b84029c6ad0'
HEAD='affaad6b1a31d680164d9e3d5ef5d2a9d3fce95a'
TREE='2563bcea5ceee3543451e96ac76011ef05e486bf'
HOST_UID=1001
HOST_GID=1002
BUDGET=3900
PODMAN='/usr/bin/podman'

def podman_argv(*args):
    return [PODMAN,'--remote=false','--cgroup-manager=systemd',*args]

def podman_environment():
    # Explicit allowlist: no connection/config/storage overrides or ambient secrets.
    return {'HOME':'/home/ansible-verify','USER':'ansible-verify','LOGNAME':'ansible-verify',
            'XDG_RUNTIME_DIR':'/run/user/1001','PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8'}

def require(value,reason):
    if not value:raise ValueError(reason)

def create_argv(kit,session,name,manifest_sha):
    require(re.fullmatch(r'p1-role-[0-9a-f]{16}',name),'BAD_SESSION_NAME')
    require(re.fullmatch(r'[0-9a-f]{64}',manifest_sha),'BAD_MANIFEST_HASH')
    k=PurePosixPath(kit);s=PurePosixPath(session)
    require(k.is_absolute() and s.is_absolute() and '..' not in k.parts+s.parts,'BAD_PATH')
    require(k.parent==s and k.name=='kit' and str(s).startswith('/home/ansible-verify/p1-role-'),'BAD_SESSION_ROOT')
    return podman_argv('create',
            '--name='+name,'--cidfile='+str(s/'container.cid'),
            '--label=fds.fixture.session='+name,'--label=fds.fixture.manifest='+manifest_sha,
            '--pull=never','--network=none','--ipc=private','--pid=private','--uts=private','--cgroupns=private',
            '--userns=keep-id:uid=0,gid=0','--user=0:0','--cap-drop=ALL',
            '--security-opt=no-new-privileges','--read-only','--read-only-tmpfs=false',
            '--cpus=2','--memory=4g','--memory-swap=4g','--pids-limit=512',
            '--shm-size=64m','--timeout='+str(BUDGET),'--restart=no','--stop-timeout=30',
            '--log-driver=none','--http-proxy=false','--unsetenv-all','--no-hosts',
            '--env=HOME=/scratch/home','--env=PATH=/usr/local/bin:/usr/bin:/bin',
            '--env=LANG=C.UTF-8','--env=LC_ALL=C.UTF-8','--env=TMPDIR=/scratch/tmp',
            '--env=PYTHONDONTWRITEBYTECODE=1','--env=PIP_NO_INDEX=1','--env=PIP_DISABLE_PIP_VERSION_CHECK=1',
            '--env=GIT_OPTIONAL_LOCKS=0','--env=GIT_CONFIG_NOSYSTEM=1','--env=GIT_CONFIG_GLOBAL=/dev/null',
            '--umask=0077','--workdir=/supply/source',
            '--tmpfs=/scratch:rw,exec,nosuid,nodev,size=1536m,mode=0700,U',
            '--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=128m,mode=1777',
            '--tmpfs=/dev/shm:rw,noexec,nosuid,nodev,size=64m,mode=1777',
            '--volume='+str(k)+':/supply:ro,Z,nodev,nosuid',
            '--volume='+str(s/'control')+':/control:ro,Z,nodev,nosuid,noexec',
            '--volume='+str(s/'results')+':/results:rw,Z,nodev,nosuid',
            '--entrypoint=/usr/local/bin/python3',IMAGE,'-I','-B','/supply/container_main.py')

def normalize_id_map(rows):
    require(isinstance(rows,list) and 0<len(rows)<=340,'ID_MAP_SHAPE')
    for row in rows:
        require(isinstance(row,list) and len(row)==3 and all(type(x) is int for x in row),'ID_MAP_ROW')
        a,b,n=row
        require(a>=0 and b>=0 and n>0 and a+n<=4294967295 and b+n<=4294967295,'ID_MAP_RANGE')
    for column in (0,1):
        ordered=sorted(rows,key=lambda r:r[column])
        require(all(x[column]+x[2]<=y[column] for x,y in zip(ordered,ordered[1:])),'ID_MAP_OVERLAP')
    return sorted([row[:] for row in rows])

def rootless_id_maps(value):
    require(isinstance(value,dict) and set(value)=={'uidmap','gidmap'},'OUTER_MAP_SHAPE')
    result={}
    for key,target in (('uidmap',HOST_UID),('gidmap',HOST_GID)):
        rows=value[key]
        require(isinstance(rows,list) and all(isinstance(r,dict) and set(r)=={'container_id','host_id','size'} for r in rows),'OUTER_MAP_ROW')
        rows=normalize_id_map([[r['container_id'],r['host_id'],r['size']] for r in rows])
        require(rows[0]==[0,target,1] and all(r[1]>0 for r in rows),'OUTER_HOST_IDENTITY')
        result[key]=rows
    return result

def inner_to_host_map(inner,outer,target):
    inner=normalize_id_map(inner);outer=normalize_id_map(outer)
    require(outer[0]==[0,target,1] and all(r[1]>0 for r in outer),'OUTER_HOST_IDENTITY')
    if inner==outer:
        return {'mode':'EXACT_OUTER_MAP','host_map':inner}
    require(inner[0]==[0,0,1],'INNER_PARENT_ROOT_IDENTITY')
    composed=[]
    for a,b,n in inner:
        while n:
            matches=[r for r in outer if r[0]<=b<r[0]+r[2]]
            require(len(matches)==1,'INNER_PARENT_RANGE_UNMAPPED')
            x,y,size=matches[0];take=min(n,x+size-b)
            composed.append([a,y+b-x,take]);a+=take;b+=take;n-=take
    composed=normalize_id_map(composed)
    require(composed[0]==[0,target,1],'COMPOSED_HOST_IDENTITY')
    return {'mode':'COMPOSED_PARENT_MAP','host_map':composed}

def assert_bind_witnesses(records,observed,session):
    expected={'/supply':str(PurePosixPath(session)/'kit'),'/control':str(PurePosixPath(session)/'control'),'/results':str(PurePosixPath(session)/'results')}
    require(isinstance(records,dict) and set(records)==set(observed)==set(expected),'BIND_WITNESS_SET')
    for dest,source in expected.items():
        host=records[dest];inside=observed[dest]
        require(host['source']==source and host['uid']==HOST_UID and host['gid']==HOST_GID and host['mode']==0o700,'BIND_HOST_IDENTITY')
        require(type(host['device']) is int and type(host['inode']) is int and host['device']>=0 and host['inode']>0,'BIND_HOST_INODE')
        require(inside['device']==host['device'] and inside['inode']==host['inode'],'BIND_INODE_CHANGED')
        require(inside['uid']==inside['gid']==0 and inside['mode']==0o700,'BIND_INSIDE_IDENTITY')

def assert_owned(value,cid,name,sha):
    require(value['Id']==cid,'CID_MISMATCH')
    require(value['Name']==name,'NAME_MISMATCH')
    require(value['Image'].removeprefix('sha256:')==IMAGE.removeprefix('sha256:'),'IMAGE_MISMATCH')
    labels=value['Config']['Labels']
    require(labels.get('fds.fixture.session')==name and labels.get('fds.fixture.manifest')==sha,'LABEL_MISMATCH')

def read_record(path,*,public_cid=False):
    try:fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    except FileNotFoundError:return None
    with os.fdopen(fd,'rb') as stream:
        s=os.fstat(stream.fileno())
        modes=(0o600,0o644) if public_cid else (0o600,0o400)
        require(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==HOST_UID and s.st_gid==HOST_GID
                and stat.S_IMODE(s.st_mode) in modes and s.st_size<=8192,'RECORD_IDENTITY')
        if public_cid:require(s.st_size==64,'CIDFILE_SIZE')
        raw=stream.read(8193)
        after=os.fstat(stream.fileno())
        fields=('st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_mtime_ns','st_ctime_ns')
        require(all(getattr(s,k)==getattr(after,k) for k in fields),'RECORD_CHANGED')
        require(len(raw)<=8192,'RECORD_SIZE')
        return raw

def read_protected_record(path):
    return read_record(path)

def read_cidfile(root):
    raw=read_record(root/'container.cid',public_cid=True)
    if raw is None:return None
    require(len(raw)==64,'CIDFILE_SIZE')
    cid=raw.decode('ascii')
    require(re.fullmatch(r'[0-9a-f]{64}',cid),'INVALID_CIDFILE')
    return cid

def identity_cid(record,name,sha):
    require(record.get('schema')==1 and record.get('session')==name and record.get('manifest_sha256')==sha
            and record.get('image')==IMAGE,'IDENTITY_BINDING')
    cid=record.get('cid','')
    require(isinstance(cid,str) and re.fullmatch(r'[0-9a-f]{64}',cid),'IDENTITY_CID')
    return cid

def persist_identity(root,value,cid,name,sha):
    assert_owned(value,cid,name,sha)
    record={'schema':1,'cid':cid,'session':name,'image':IMAGE,'manifest_sha256':sha}
    raw=(json.dumps(record,sort_keys=True,indent=2)+'\n').encode('ascii')
    path=root/'OWNED_IDENTITY.json'
    previous=read_protected_record(path)
    if previous is not None:
        require(identity_cid(json.loads(previous),name,sha)==cid,'IDENTITY_CHANGED')
        return
    atomic_record(path,raw)

def atomic_record(path,raw):
    # Atomic, non-overwriting publish; a failed temp is preserved, never a partial final.
    temp=path.parent/('.'+path.name+'.pending-'+uuid.uuid4().hex)
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    rename_noreplace(temp,path)
    parent=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(parent)
    finally:os.close(parent)

def rename_noreplace(source,destination):
    # Linux syscall boundary; unsupported libc/filesystem fails closed with no fallback.
    libc=ctypes.CDLL(None,use_errno=True)
    try:rename=libc.renameat2
    except AttributeError:raise OSError(38,'RENAME_NOREPLACE_UNAVAILABLE')
    rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    rename.restype=ctypes.c_int
    if rename(-100,os.fsencode(source),-100,os.fsencode(destination),1)!=0:
        err=ctypes.get_errno();raise OSError(err,os.strerror(err),str(destination))

def assert_saved_identity(root,cid,name,sha):
    raw=read_protected_record(root/'OWNED_IDENTITY.json')
    if raw is not None:require(identity_cid(json.loads(raw),name,sha)==cid,'IDENTITY_CHANGED')

def resolve_cid(root,name,sha,stdout=None):
    # Independently preserve all sources; any unreadable/conflicting source is a safety stop.
    candidates={};errors=[]
    if stdout:
        if re.fullmatch(r'[0-9a-f]{64}',stdout.strip()):candidates['create_stdout']=stdout.strip()
        else:errors.append('CREATE_STDOUT_INVALID')
    for label,read in (
        ('cidfile',lambda:read_cidfile(root)),
        ('identity',lambda:identity_cid(json.loads(raw),name,sha) if (raw:=read_protected_record(root/'OWNED_IDENTITY.json')) is not None else None)):
        try:
            value=read()
            if value:candidates[label]=value
        except (Exception,KeyboardInterrupt) as exc:errors.append(label+':'+type(exc).__name__+':'+str(exc))
    if len(set(candidates.values()))>1:errors.append('CID_IDENTITY_CONFLICT')
    return {'candidates':candidates,'errors':errors,'cid':next(iter(candidates.values()),None) if not errors else None}

def recover_session_cid(root,name,sha):
    cid=read_cidfile(root)
    raw=read_protected_record(root/'OWNED_IDENTITY.json')
    saved=identity_cid(json.loads(raw),name,sha) if raw is not None else None
    require(cid is not None or saved is not None,'CID_IDENTITY_MISSING_NO_GUESS')
    require(cid is None or saved is None or cid==saved,'CID_IDENTITY_CONFLICT')
    return cid or saved

def assert_created_isolation(value,session):
    config=value['HostConfig']
    require(not config.get('Privileged') and config.get('ReadonlyRootfs') is True,'ROOTFS_OR_PRIVILEGE')
    require(config.get('NetworkMode')=='none' and config.get('PidMode')!='host' and config.get('IpcMode')!='host','HOST_NAMESPACE')
    require(value['Config']['User']=='0:0','CONTAINER_USER')
    expected={str(PurePosixPath(session)/'kit'):'/supply',str(PurePosixPath(session)/'control'):'/control',
              str(PurePosixPath(session)/'results'):'/results'}
    binds=[m for m in value['Mounts'] if m['Type']=='bind']
    require(len(binds)==3 and {m['Source']:m['Destination'] for m in binds}==expected,'UNEXPECTED_BIND_MOUNT')
    for mount in binds:
        options=mount.get('Options',[])
        require(isinstance(options,list) and all(isinstance(o,str) for o in options),'BIND_OPTION_SHAPE')
        require(not any(o=='U' or o.startswith('idmap') for o in options),'BIND_IDMAP_OR_CHOWN')
    require(all(m['RW']==(m['Destination']=='/results') for m in binds),'BIND_WRITE_SCOPE')
    require(not [m for m in value['Mounts'] if m['Type'] not in ('bind','tmpfs')],'UNEXPECTED_VOLUME')

def check_result(kind,data):
    if kind=='mon':
        rows=data.get('cases',[])
        require(data.get('status')=='PASS' and data.get('source_commit')==HEAD and data.get('source_dirty') is False,'MON_IDENTITY_OR_STATUS')
        require(len(rows)==45 and all(x.get('passed') is True for x in rows),'MON_CASE_SET')
    elif kind=='serial':
        require(data.get('passed') is True and data.get('rc')==2,'SERIAL_EXPECTED_FAILURE_NOT_CONFIRMED')
        require(len(data.get('hosts',{}))==5,'SERIAL_HOST_SET')
    elif kind=='transport':
        require(data.get('passed') is True and data.get('total')==2 and data.get('passed_cases')==2,'TRANSPORT_CASE_SET')
    else:
        rows=data.get('results',[])
        require(bool(rows) and len({x['name'] for x in rows})==len(rows),'EMPTY_OR_DUPLICATE_CASES')
        require(data.get('passed')==data.get('total')==len(rows) and all(x.get('passed') is True for x in rows),'CASE_FAILURE')
