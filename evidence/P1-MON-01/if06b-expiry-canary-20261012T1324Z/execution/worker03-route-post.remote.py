import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-worker03' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='a3394d56-a6ae-2f0f-c17d-c6dc9dff8548'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='f0c48106-f753-4ab7-bacd-660c126fca2f'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
import hashlib
base=Path('/home/svc_ansible/if06b-20261012T2220-mon02/worker')
p=subprocess.run(['ip','-4','route','get','10.250.10.30'],capture_output=True,text=True)
assert p.returncode==0
with (base/'route-post.txt').open('x') as f:f.write(p.stdout)
print(json.dumps({'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'rc':p.returncode,'route':p.stdout,'matches_pre':p.stdout==(base/'route-pre.out').read_text(),'sha256':hashlib.sha256(p.stdout.encode()).hexdigest()}))
