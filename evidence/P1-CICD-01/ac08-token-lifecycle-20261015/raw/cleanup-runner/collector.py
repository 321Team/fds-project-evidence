"""Pure read: scoped public files and same-UID diagnostic process metadata."""
import datetime as dt,hashlib,json,os,pwd,re,socket,stat,sys
from pathlib import Path
SHA='c373f1d7a8e6e84548180839098c34e9a1262eef'
FILES={'deploy_token_lifecycle.py','deploy_native_probe.py','deploy_cp1_access.py','deploy_binding.py',
       'deploy_credential.py','deploy_transport.py','deploy_adapter.py','delivery_gate.py'}
allowed={'ansible01':'server01_ansible','k8s-control01':'server02','cicd-runner01':'server01_cicd-runner'}
host=socket.gethostname();assert host in allowed and pwd.getpwuid(os.getuid()).pw_name==allowed[host]
assert 1<=len(sys.argv[1:])<=4
out={'host':host,'uid':os.getuid(),'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
     'classification':'PURE_READ_POSTCHECK','mutation':False,'directories':[],
     'active_probe_processes':[],'unreadable_same_uid_python':[],'unclassified_python':[]}
secret=re.compile(rb'eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]+|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|Authorization: Bearer [A-Za-z0-9_-]{20,}')
for value in sys.argv[1:]:
    path=Path(value);assert path.parent==Path.home()
    source=bool(re.fullmatch(r'FDS_NativeProbeSource\.[a-z0-9_]{8}',path.name))
    staging=host=='ansible01' and bool(re.fullmatch(r'FDS_AC08_20261015\.[A-Za-z0-9]{8}',path.name))
    assert source or staging
    meta=path.lstat();assert stat.S_ISDIR(meta.st_mode) and meta.st_uid==os.getuid() and stat.S_IMODE(meta.st_mode)==0o700
    names=FILES if source else {'transfer_native_probe.py','lifecycle-source.json'}
    assert {p.name for p in path.iterdir()}==names
    row={'path':value,'mode':'0o700','files':[]}
    for name in sorted(names):
        p=path/name;s=p.lstat()
        assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size<1024*1024
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as f:
            a=os.fstat(f.fileno());raw=f.read(1024*1024);b=os.fstat(f.fileno())
        assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns)
        hits=len(secret.findall(raw))
        row['files'].append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'mode':'0o600','secret_pattern_hits':hits})
        raw=None
    out['directories'].append(row)
for p in Path('/proc').iterdir():
    if not p.name.isdecimal() or int(p.name)==os.getpid():continue
    try:
        comm=(p/'comm').read_text().strip()
        if 'python' not in comm:continue
        try:status=(p/'status').read_text()
        except PermissionError:
            out['unclassified_python'].append(int(p.name));continue
        ids=re.search(r'^Uid:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',status,re.M)
        if not ids or os.getuid() not in map(int,ids.groups()):continue
        try:args=(p/'cmdline').read_bytes()
        except PermissionError:
            out['unreadable_same_uid_python'].append(int(p.name));continue
        if (SHA.encode() in args and b'deploy_token_lifecycle' in args) or b'FDS_AC08_20261015.' in args:
            out['active_probe_processes'].append({'pid':int(p.name),'comm':comm})
        args=None
    except (FileNotFoundError,ProcessLookupError):continue
print(json.dumps(out,sort_keys=True))
