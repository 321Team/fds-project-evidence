from pathlib import Path
import importlib.util,json,base64,hashlib,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
mode=sys.argv[1];assert mode in ('edge','control')
if mode=='edge':
 ip,host,uid,path,root='50','edge01',1003,'/home/svc_ansible/p1-ha-20261014-0015',False
 names=['ha-probe.py','ha-judge.py','probe.log','probe.stdout','probe.stderr','probe-start.json','probe-result.json']
else:
 ip,host,uid,path,root='102','k8s-control01',0,'/var/tmp/p1-ha-20261014-0015',True
 names=['timeline.txt','drain-intent.json','drain-result.json','rescheduled-ready-result.json','uncordon-intent.json','uncordon-result.json','fds-engine-eviction.json','fds-engine-eviction-result.json','fds-engine-recovery.json','fds-engine-recovery-supplement.json','transaction-api-eviction.json','transaction-api-eviction-result.json','transaction-api-recovery.json']
source='''import os,pathlib,socket,json,hashlib,base64,stat,time
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
   args=(proc/'cmdline').read_bytes().split(b'\\0')
   if str(p/'ha-probe.py').encode() in args:active.append(int(proc.name))
  except (OSError,PermissionError):pass
 out['active_probe_pids']=active;assert not active
print(json.dumps(out))
'''
code='HOST='+repr(host)+'\nUID='+repr(uid)+'\nTARGET='+repr(path)+'\nNAMES='+repr(names)+'\n'+source
r=t.run('receive-'+mode,'10.1.93.'+ip,code,90,root);assert r['rc']==0
doc=json.loads((OUT/('receive-'+mode)/'stdout.json').read_bytes());dest=OUT/(mode+'-originals');dest.mkdir(exist_ok=False)
for item in doc['files']:
 raw=base64.b64decode(item['base64']);assert hashlib.sha256(raw).hexdigest()==item['sha256'] and len(raw)==item['size']
 with (dest/item['name']).open('xb') as f:f.write(raw)
print(json.dumps({'received':mode,'files':len(doc['files']),'all_remote_hashes_match':True}))
