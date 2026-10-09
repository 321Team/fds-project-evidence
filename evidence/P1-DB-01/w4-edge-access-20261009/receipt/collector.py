"""Receipt only, run after operator confirms COLLECTION_FINISHED."""
import datetime,hashlib,json,os,pathlib,pwd,socket,stat,sys
assert socket.gethostname()=='edge01' and pwd.getpwuid(os.geteuid()).pw_name=='svc_ansible'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert '2026-10-09T00:00:00+09:00'<=now<'2026-10-09T09:00:00+09:00'
root=pathlib.Path('/home/svc_ansible/w4-edge-readonly.ucyh6e81')
assert hashlib.sha256((root/'collector.py').read_bytes()).hexdigest()=='cd2205c11461f4c12258ecae62d64051c6f458e41cdd50e1bac1920131f8b750'
p=root/'result.json';s=p.lstat()
assert stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o600 and s.st_size<=2*1024*1024
raw=p.read_bytes();d=json.loads(raw)
assert d['schema']=='fds.edge-w4-access-projection.v1' and d['host']=='edge01'
assert d['collector_sha256']=='cd2205c11461f4c12258ecae62d64051c6f458e41cdd50e1bac1920131f8b750'
sys.stdout.buffer.write(raw)
