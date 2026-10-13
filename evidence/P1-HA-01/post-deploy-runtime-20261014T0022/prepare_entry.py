"""Stage only approved tool bytes in new exclusive directories; no probe or HA action."""
from pathlib import Path
import importlib.util,json,hashlib,base64
OUT=Path(__file__).resolve().parent; ROOT=OUT.parent
spec=importlib.util.spec_from_file_location('transport',ROOT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
receipt=t.run('app-state','10.1.93.102',(ROOT.parent/'phase1-deploy-preparation-20261013/app_state_read.py').read_bytes(),90,True)
assert receipt['rc']==0
def load(p):return json.loads((OUT/p).read_bytes())
b=json.loads((ROOT/'READINESS_BINDING.json').read_bytes())
c=load('current-cluster/stdout.json');q={x['name']:x['items'] for x in c['queries']}
assert c['identity_before']==c['identity_after']==b['control_identity']
assert q['cluster'][0]['metadata']['uid']==b['cluster']['uid']
assert next(n for n in q['nodes'] if n['metadata']['name']=='k8s-worker02')['metadata']['uid']==b['target_node']['metadata']['uid']
assert len(q['nodes'])==6
for node in q['nodes']:
 conditions={x['type']:x['status'] for x in node['status']['conditions']}
 assert conditions['Ready']=='True' and all(conditions[k]=='False' for k in ('MemoryPressure','DiskPressure','PIDPressure'))
aq={x['kind']:x['items'] for x in load('app-state/stdout.json')['queries']}
for d in aq['deployments']:
 wanted=next(x for x in b['deployments'] if x['metadata']['name']==d['metadata']['name'])
 assert d['spec_sha256']==wanted['spec_sha256'] and d['metadata']['uid']==wanted['metadata']['uid'] and d['metadata']['generation']==wanted['metadata']['generation']
 assert not d['metadata']['deletionTimestamp']
assert len(aq['pods'])==6 and all(not p['metadata']['deletionTimestamp'] for p in aq['pods'])
for es in aq['endpointslices']:
 assert len(es['endpoints'])==3 and all(e['conditions'].get('ready') is True and not e['conditions'].get('terminating',False) for e in es['endpoints'])
 assert sorted(e['nodeName'] for e in es['endpoints'])==['k8s-worker01','k8s-worker02','k8s-worker03']
assert next(x for x in aq['services'] if x['metadata']['name']=='transaction-api-nodeport')['spec']['externalTrafficPolicy']=='Local'
# Reuse the existing collection validation exactly, with current local inputs and the same sealed Deploy result.
source=(ROOT/'prepare_card.py').read_text(encoding='utf-8').split('tools=[];supply=')[0]
source=source.replace('OUT=pathlib.Path(__file__).parent','OUT=pathlib.Path('+repr(str(OUT))+')')
source=source.replace("OUT.parent/'phase1-deploy-after-push-20261013-2244", "OUT.parent.parent/'phase1-deploy-after-push-20261013-2244")
exec(compile(source,'reused-readiness-validation','exec'),{})
files={}
for name,expected in [('ha-probe.py','e2603769cacef36dab6231052104f29f413b105a78d771b4e4c3db3c0a599804'),('ha-judge.py','79f54c955991dacd0767885b0db5001fad39080ea7cf4b7c2a3ea13c6f1a6aad')]:
 raw=(ROOT/'supply'/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
 files[name]={'content':base64.b64encode(raw).decode(),'sha256':expected}
for label,ip,host,uid,path,payload,root in [('stage-edge','50','edge01',1003,'/home/svc_ansible/p1-ha-20261014-0015',files,False),('stage-control','102','k8s-control01',0,'/var/tmp/p1-ha-20261014-0015',{},True)]:
 remote='''import os,pathlib,stat,socket,json,hashlib,base64,datetime
assert socket.gethostname()==HOST and os.geteuid()==UID
p=pathlib.Path(TARGET)
assert p.parent.is_dir() and not p.parent.is_symlink() and not os.path.lexists(p)
os.umask(0o077);p.mkdir(mode=0o700)
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'directory':str(p),'files':[],'probe_runs':0,'ha_mutations':0}
assert stat.S_IMODE(p.stat().st_mode)==0o700 and p.stat().st_uid==UID
for name,item in FILES.items():
 raw=base64.b64decode(item['content']);assert hashlib.sha256(raw).hexdigest()==item['sha256']
 f=p/name;fd=os.open(f,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 assert f.stat().st_uid==UID and stat.S_IMODE(f.stat().st_mode)==0o600 and hashlib.sha256(f.read_bytes()).hexdigest()==item['sha256']
 out['files'].append({'name':name,'sha256':item['sha256'],'uid':f.stat().st_uid,'mode':'0600'})
print(json.dumps(out))
'''
 code='HOST='+repr(host)+'\nUID='+repr(uid)+'\nTARGET='+repr(path)+'\nFILES='+repr(payload)+'\n'+remote
 result=t.run(label,'10.1.93.'+ip,code,60,root);assert result['rc']==0
(OUT/'ENTRY_VALIDATED.json').write_text(json.dumps({'status':'ENTRY_READS_AND_STAGING_COMPLETE','probe_runs':0,'ha_mutations':0,'console_nonoverlap':'PENDING'},indent=2)+'\n',encoding='utf-8')
print('ENTRY_READS_AND_STAGING_COMPLETE; HA/PROBE=0')
