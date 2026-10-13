from pathlib import Path
import datetime as dt,importlib.util,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
now=dt.datetime.now(dt.timezone.utc)
assert dt.datetime.fromisoformat('2026-10-13T15:15:00+00:00')<=now<dt.datetime.fromisoformat('2026-10-13T15:25:00+00:00')
assert json.loads((OUT/'ENTRY_VALIDATED.json').read_bytes())['status']=='ENTRY_READS_AND_STAGING_COMPLETE'
authorization={'recorded_at_utc':now.isoformat(),'instruction':'착수','console_nonoverlap_reply':'01:05까지 콘솔 대기·비중첩 확보','scope':'PR220 exactly: probe900s once; worker02 selected two apps drain once; uncordon; optional max one eviction per app engine then API outside W; no other runtime scope','not_before':'2026-10-14T00:15:00+09:00','start_deadline':'2026-10-14T00:25:00+09:00','finish_deadline':'2026-10-14T01:05:00+09:00','reviewed_head':'0340ce3feaf22dcf25d736e1b3ee8f537de54d06','merged_sha':'9a0d320f3440bd7a244f1ecdc702ebac64409769'}
with (OUT/'AUTHORIZATION.json').open('x',encoding='utf-8') as f:json.dump(authorization,f,ensure_ascii=False,indent=2)
source='''import os,pathlib,json,hashlib,socket,datetime,time,subprocess,signal
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
'''
receipt=t.run('probe-run','10.1.93.50',source,timeout=960,as_root=False)
assert receipt['rc']==0
