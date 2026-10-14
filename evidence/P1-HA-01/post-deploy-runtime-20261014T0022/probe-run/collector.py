import os,pathlib,json,hashlib,socket,datetime,time,subprocess,signal
assert socket.gethostname()=='edge01' and os.geteuid()==1003
now=datetime.datetime.now(datetime.timezone.utc)
assert datetime.datetime.fromisoformat('2026-10-13T15:15:00+00:00')<=now<datetime.datetime.fromisoformat('2026-10-13T15:25:00+00:00')
p=pathlib.Path('/home/svc_ansible/p1-ha-20261014-0015')
assert p.is_dir() and not p.is_symlink() and p.stat().st_uid==1003 and p.stat().st_mode & 0o777==0o700
assert hashlib.sha256((p/'ha-probe.py').read_bytes()).hexdigest()=='e2603769cacef36dab6231052104f29f413b105a78d771b4e4c3db3c0a599804'
assert not os.path.lexists(p/'probe.log') and not os.path.lexists(p/'probe-start.json')
os.umask(0o077)
cmd=['/usr/bin/python3',str(p/'ha-probe.py'),str(p/'probe.log'),'900','10.1.93.105,10.1.93.107,10.1.93.108','30080','24']
receipt={'started_wall':time.time(),'started_monotonic':time.monotonic(),'command':cmd,'probe_runs':1,'ha_mutations':0}
with (p/'probe.stdout').open('xb') as out,(p/'probe.stderr').open('xb') as err:
 proc=subprocess.Popen(cmd,stdout=out,stderr=err,start_new_session=True)
 receipt['pid']=proc.pid
 with (p/'probe-start.json').open('x') as f:json.dump(receipt,f)
 try:receipt['rc']=proc.wait(timeout=925)
 except subprocess.TimeoutExpired:
  receipt['error']='PROBE_WATCHDOG_TIMEOUT_NO_RETRY';os.killpg(proc.pid,signal.SIGTERM)
  try:receipt['rc']=proc.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);receipt['rc']=proc.wait(timeout=5)
receipt.update(finished_wall=time.time(),finished_monotonic=time.monotonic(),child_exited=proc.poll() is not None)
for name in ('probe.log','probe.stdout','probe.stderr'):receipt[name+'_sha256']=hashlib.sha256((p/name).read_bytes()).hexdigest()
with (p/'probe-result.json').open('x') as f:json.dump(receipt,f)
print(json.dumps(receipt))
