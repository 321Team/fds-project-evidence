from pathlib import Path
import json,sys
from read_transport import run
R=Path(__file__).resolve().parent;P=R.parent
analysis=json.loads((P/'ANALYSIS.json').read_bytes());app=json.loads((P.parent/'p1-redistribution-20261013/APP_BINDING.json').read_bytes())
expected={x['metadata']['namespace']+'/'+x['metadata']['name']:{'uid':x['metadata']['uid'],'spec_sha256':x['spec_sha256']} for x in analysis['deployments']+app['deployments']}
source='EXPECTED='+repr(expected)+'\nSYSTEM_PODS='+repr(analysis['system_pod_locations'])+'\n'+'''
import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s']
def query(args):
 p=subprocess.run(kc+args,capture_output=True,timeout=8);out['commands'].append({'argv':kc+args,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()});assert p.returncode==0;return json.loads(p.stdout)
def ready(x):return not x['metadata'].get('deletionTimestamp') and any(c['type']=='Ready' and c['status']=='True' for c in x.get('status',{}).get('conditions',[]))
try:
 ns=query(['get','namespace','kube-system','-o','json']);out['cluster_uid']=ns['metadata']['uid'];assert out['cluster_uid']=='e1669cff-1435-423f-a6c4-28bc44f488de'
 nodes=query(['get','nodes','-o','json'])['items'];out['nodes']=[{'name':x['metadata']['name'],'uid':x['metadata']['uid'],'ready':ready(x)} for x in nodes];assert len(nodes)==6 and all(ready(x) for x in nodes)
 dep=query(['get','deployments','-A','-o','json'])['items'];out['deployments']=[]
 for x in dep:
  k=x['metadata']['namespace']+'/'+x['metadata']['name']
  if k not in EXPECTED:continue
  d={'key':k,'uid':x['metadata']['uid'],'spec_sha256':hashlib.sha256(json.dumps(x['spec'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'ready':x['status'].get('readyReplicas',0),'desired':x['spec']['replicas']};out['deployments'].append(d)
  assert d['uid']==EXPECTED[k]['uid'] and d['spec_sha256']==EXPECTED[k]['spec_sha256'] and d['ready']==d['desired']
 assert len(out['deployments'])==4
 pods=query(['get','pods','-A','-o','json'])['items'];out['pods']=[]
 sysnames={x['name']:x for x in SYSTEM_PODS}
 for x in pods:
  n=x['metadata']['name'];ns=x['metadata']['namespace'];a=x['metadata'].get('labels',{}).get('app')
  if n not in sysnames and not(ns=='fds-app' and a in ['transaction-api','fds-engine']):continue
  d={'name':n,'namespace':ns,'uid':x['metadata']['uid'],'node':x['spec']['nodeName'],'ready':ready(x),'app':a,'restarts':{c['name']:c['restartCount'] for c in x['status'].get('containerStatuses',[])}};out['pods'].append(d);assert d['ready']
  if n in sysnames:assert d['uid']==sysnames[n]['uid'] and d['node']==sysnames[n]['node']
 assert len(out['pods'])==9 and len([x for x in out['pods'] if x['name'] in sysnames])==3
 for a in ['transaction-api','fds-engine']:assert sorted(x['node'] for x in out['pods'] if x['app']==a)==['k8s-worker01','k8s-worker02','k8s-worker03']
 out['status']='CLUSTER_BINDING_VERIFIED'
except Exception as e:out.update(status='STOP',error=type(e).__name__+':'+str(e))
print(json.dumps(out));raise SystemExit(0 if out['status']=='CLUSTER_BINDING_VERIFIED' else 2)
'''
r=run('cluster-'+sys.argv[1],'10.1.93.102',source,timeout=60)
if r['rc']!=0:raise SystemExit(2)
if sys.argv[1]!='before':
 before=json.loads((R/'cluster-before/stdout.json').read_bytes());after=json.loads((R/('cluster-'+sys.argv[1])/'stdout.json').read_bytes())
 assert sorted(before['pods'],key=lambda x:x['uid'])==sorted(after['pods'],key=lambda x:x['uid']),'POD_DRIFT'
print('CLUSTER_PRESERVATION_VERIFIED')
