"""Fixed private relay, no shell interpolation or credentials copied."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent;mode=sys.argv[1]
assert mode in ['source-to-relay','relay-to-target']
images={n:json.loads((R/('export-k8s-control01-'+n)/'stdout.json').read_bytes())['archive'] for n in ['kube-controllers','coredns']}
addresses={'k8s-control02':'10.1.93.103','k8s-control03':'10.1.93.104','k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
cfg={'mode':mode,'images':images,'relay':'/home/server01_ansible/p1-oid02-relay-20261013-r1','root':'/root/p1-oid02-20261013-r1'}
if mode=='relay-to-target':
 host,im=sys.argv[2:];assert host in addresses and im in images
 assert 'worker' in host or im=='kube-controllers'
 cfg.update(host=host,ip=addresses[host],image=im)
name=mode+('-'+cfg['host']+'-'+cfg['image'] if mode=='relay-to-target' else '')
folder=R/name;folder.mkdir(exist_ok=False)
source='CFG='+repr(cfg)+'\n'+'''
import datetime,hashlib,json,os,pathlib,subprocess
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
out={'started_at_utc':now(),'action':CFG['mode'],'commands':[]}
base=['/usr/bin/ssh','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes']
relay=pathlib.Path(CFG['relay'])
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
try:
 assert pathlib.Path.home()==pathlib.Path('/home/server01_ansible')
 if CFG['mode']=='source-to-relay':
  os.umask(0o077);relay.mkdir(mode=0o700)
  for n,im in CFG['images'].items():
   filename=n+'-linux-amd64.oci.tar';path=relay/filename
   argv=base+['svc_ansible@10.1.93.102','sudo','-n','/usr/bin/cat',CFG['root']+'/'+filename]
   row={'argv':argv,'started_at_utc':now()};out['commands'].append(row)
   fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as f:p=subprocess.run(argv,stdout=f,stderr=subprocess.PIPE,timeout=90);f.flush();os.fsync(f.fileno())
   row.update(rc=p.returncode,stderr=p.stderr.decode(),finished_at_utc=now(),size=path.stat().st_size,sha256=digest(path),path=str(path))
   assert p.returncode==0 and row['size']==im['archive_size_bytes'] and row['sha256']==im['archive_sha256'],'RELAY_MISMATCH'
 else:
  im=CFG['images'][CFG['image']];filename=CFG['image']+'-linux-amd64.oci.tar';path=relay/filename
  assert relay.stat().st_mode&0o777==0o700 and path.stat().st_mode&0o777==0o600 and not path.is_symlink()
  assert path.stat().st_size==im['archive_size_bytes'] and digest(path)==im['archive_sha256'],'RELAY_DRIFT'
  argv=base+['svc_ansible@'+CFG['ip'],'sudo','-n','/usr/bin/python3','-B','-I',CFG['root']+'/receive.py',filename,im['archive_sha256'],str(im['archive_size_bytes'])]
  row={'argv':argv,'started_at_utc':now()};out['commands'].append(row)
  with path.open('rb') as f:p=subprocess.run(argv,stdin=f,capture_output=True,timeout=90)
  row.update(rc=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode(),finished_at_utc=now());assert p.returncode==0
  d=json.loads(p.stdout);assert d['status']=='RECEIVED_HASH_VERIFIED' and d['sha256']==im['archive_sha256'] and d['size']==im['archive_size_bytes']
 out['status']='TRANSFER_VERIFIED'
except Exception as e:out.update(status='STOP_NO_RETRY',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='TRANSFER_VERIFIED' else 2)
'''
compile(source,'relay','exec');raw=source.encode();(folder/'collector.py').write_bytes(raw)
cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-']
receipt={'started_at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'command':cmd,'source_sha256':hashlib.sha256(raw).hexdigest()}
try:p=subprocess.run(cmd,input=raw,capture_output=True,timeout=220);stdout,stderr=p.stdout,p.stderr;receipt['rc']=p.returncode
except subprocess.TimeoutExpired as e:stdout,stderr=e.stdout or b'',e.stderr or b'';receipt.update(rc=None,error='TIMEOUT_NO_RETRY')
(folder/'stdout.json').write_bytes(stdout);(folder/'stderr.txt').write_bytes(stderr)
receipt.update(finished_at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),stdout_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest());(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'step':name,'rc':receipt['rc'],'stdout_bytes':len(stdout)}));raise SystemExit(0 if receipt['rc']==0 else 2)
