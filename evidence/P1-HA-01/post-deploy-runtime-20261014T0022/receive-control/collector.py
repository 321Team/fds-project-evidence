HOST='k8s-control01'
UID=0
TARGET='/var/tmp/p1-ha-20261014-0015'
NAMES=['timeline.txt', 'drain-intent.json', 'drain-result.json', 'rescheduled-ready-result.json', 'uncordon-intent.json', 'uncordon-result.json', 'fds-engine-eviction.json', 'fds-engine-eviction-result.json', 'fds-engine-recovery.json', 'fds-engine-recovery-supplement.json', 'transaction-api-eviction.json', 'transaction-api-eviction-result.json', 'transaction-api-recovery.json']
import os,pathlib,socket,json,hashlib,base64,stat,time
assert socket.gethostname()==HOST and os.geteuid()==UID
p=pathlib.Path(TARGET);assert p.is_dir() and not p.is_symlink()
out={'host':HOST,'epoch':time.time(),'path':TARGET,'files':[]}
for name in NAMES:
 f=p/name;assert not f.is_symlink() and f.is_file() and f.stat().st_uid==UID and stat.S_IMODE(f.stat().st_mode)==0o600
 raw=f.read_bytes();assert len(raw)<2*1024*1024
 out['files'].append({'name':name,'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'mode':'0600','uid':UID,'base64':base64.b64encode(raw).decode()})
if HOST=='edge01':
 result=json.loads((p/'probe-result.json').read_bytes());assert result['child_exited'] and result['rc']==0
 active=[]
 for proc in pathlib.Path('/proc').glob('[0-9]*'):
  try:
   args=(proc/'cmdline').read_bytes().split(b'\0')
   if str(p/'ha-probe.py').encode() in args:active.append(int(proc.name))
  except (OSError,PermissionError):pass
 out['active_probe_pids']=active;assert not active
print(json.dumps(out))
