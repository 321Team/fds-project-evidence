import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='80724d56-7c17-f8a0-b2ea-ece7a154e24b'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
import base64,hashlib,io,tarfile
ses=Path('/var/lib/fds-change/if06b-20261012T2220-mon02');tok=Path('/run/fds-if06b-20261012T2220-mon02')
assert not tok.exists(),'TOKEN_STILL_PRESENT'
files={}
for folder in ['results','journal','evidence']:
 for p in sorted((ses/folder).rglob('*')):
  assert not p.is_symlink()
  if p.is_file():
   assert p.stat().st_size<2097152
   files[p.relative_to(ses).as_posix()]=p.read_bytes()
files['input.json']=(ses/'input.json').read_bytes()
assert any(n.startswith('journal/') for n in files) and 'evidence/supervisor.jsonl' in files
hashes={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}
files['EXPORT_SHA256SUMS']=''.join(h+'  '+n+'\n' for n,h in sorted(hashes.items())).encode()
stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for n,v in files.items():
  info=tarfile.TarInfo(n);info.size=len(v);info.mode=0o600;tar.addfile(info,io.BytesIO(v))
data=stream.getvalue()
print(json.dumps({'archive_base64':base64.b64encode(data).decode(),'archive_sha256':hashlib.sha256(data).hexdigest(),'files':hashes,'excluded':'token file was deleted; no credentials included'}))
