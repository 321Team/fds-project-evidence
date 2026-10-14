import os,pathlib,json,socket,time
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
p=pathlib.Path('/var/tmp/p1-ha-20261014-0015')
assert not p.is_symlink() and p.stat().st_mode & 0o777==0o700
os.umask(0o077)
at=time.time()
with (p/'timeline.txt').open('x') as f:f.write('baseline_start %.6f\n'%at);f.flush();os.fsync(f.fileno())
print(json.dumps({'mark':'baseline_start','epoch':at,'monotonic':time.monotonic(),'timeline':(p/'timeline.txt').read_text()}))
