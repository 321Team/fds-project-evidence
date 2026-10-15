"""Read-only readiness for two fixed scan cases; no environment/credential output."""
import datetime, hashlib, json, os, pathlib, pwd, shutil, socket, stat, sys

now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
assert socket.gethostname() == 'cicd-runner01'
assert os.getuid() == 1000 and pwd.getpwuid(os.getuid()).pw_name == 'server01_cicd-runner'
home = pathlib.Path('/home/server01_cicd-runner')
out = {'started_at_utc': now(), 'hostname': socket.gethostname(), 'uid': os.getuid(),
       'python': list(sys.version_info[:3]), 'mutation': False, 'files': [], 'process_counts': {}}
out['home_mode'] = oct(stat.S_IMODE(home.lstat().st_mode))
out['free_bytes'] = shutil.disk_usage(home).free
inputs = [(home/'FDS_CICD_AppWorkflow.log3xwta/build-scan/transaction-api.oci.tar', 93404160,
           '218c57b0613dc37e9628745d3ae580886543902714bbb9ab6249b5ac90d1266f', 1000),
          (home/'FDS_CICD_AppWorkflow.log3xwta/build-scan/fds-engine.oci.tar', 74496512,
           'a8895e245ea2a2f30aa106524bf858020fccc65a12fc543d26f3c09a87f04d1c', 1000),
          (pathlib.Path('/usr/local/bin/trivy'), None,
           'd89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791', 0)]
for p, size, expected, uid in inputs:
    for parent in [p, *p.parents]:
        s = parent.lstat()
        assert not stat.S_ISLNK(s.st_mode) and s.st_uid in (0,1000) and not s.st_mode & 0o022
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid == uid and s.st_nlink == 1 and s.st_size < 256*1024*1024
    if size is not None: assert s.st_size == size
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        before = os.fstat(f.fileno()); h = hashlib.file_digest(f, 'sha256').hexdigest(); after = os.fstat(f.fileno())
    assert (s.st_ino,s.st_size,s.st_mtime_ns) == (before.st_ino,before.st_size,before.st_mtime_ns)
    assert (before.st_ino,before.st_size,before.st_mtime_ns) == (after.st_ino,after.st_size,after.st_mtime_ns)
    out['files'].append({'path':str(p),'bytes':s.st_size,'sha256':h,'matches':h==expected,
                         'uid':s.st_uid,'mode':oct(stat.S_IMODE(s.st_mode))})
for p in pathlib.Path('/proc').iterdir():
    if not p.name.isdecimal(): continue
    try: name=(p/'comm').read_text().strip()
    except (OSError,UnicodeError): continue
    if name in ('Runner.Worker','Runner.Listener','trivy','ansible-playboo','podman'):
        out['process_counts'][name] = out['process_counts'].get(name,0)+1
out['scan_claims'] = sorted(p.name for p in home.glob('FDS_CICD_ScanNegative-*.claim'))
out['scan_folders'] = sorted(p.name for p in home.glob('FDS_CICD_ScanNegative.*'))
out['readiness'] = ('READY' if out['home_mode']=='0o700' and out['free_bytes']>=4*1024**3
                    and tuple(out['python']) >= (3,11,0) and all(f['matches'] for f in out['files'])
                    and out['process_counts'].get('Runner.Worker',0)==0
                    and out['process_counts'].get('trivy',0)==0 else 'HOLD')
out['finished_at_utc'] = now()
print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
