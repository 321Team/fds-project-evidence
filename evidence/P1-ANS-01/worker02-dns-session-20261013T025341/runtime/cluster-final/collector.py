EXPECTED={'kube-system/calico-kube-controllers': {'uid': 'cd1095ef-053f-47a6-b4c6-4ff9aa353ab8', 'spec_sha256': 'efbc909b652d366a99240a87e9309100f128c88c9bd9c21e83cc88ba5ac9a847'}, 'kube-system/coredns': {'uid': '529b998a-0ff9-46cc-ad5d-991fe0fb9a63', 'spec_sha256': '65de094015f21aca231bc47d879ea044362b2d55e189fc6edc55284cfcf429a9'}, 'fds-app/transaction-api': {'uid': '8a2af808-ec33-41f2-80b5-addde4e28910', 'spec_sha256': '07cdf04742aa5be6ef220071232ad1f863e87f1033210269e2cc0dbc18949a9e'}, 'fds-app/fds-engine': {'uid': 'bf825dec-465b-4603-8b71-f768d195531c', 'spec_sha256': 'e091caa8a78d8a90211a7db9e2f9a5137e319056b14b1b9106e96c85f676f15c'}}
SYSTEM_PODS=[{'name': 'calico-kube-controllers-74f76ddbd-jbpm9', 'uid': 'e6828576-98e3-4c2f-a0f7-f204460f6d48', 'node': 'k8s-control01'}, {'name': 'coredns-589f44dc88-f8l54', 'uid': 'b177ca1d-d26a-4e55-acc6-2cc384e6d281', 'node': 'k8s-control01'}, {'name': 'coredns-589f44dc88-qkcws', 'uid': '11b524dc-b4de-4ce1-9cb0-8d3856f45b75', 'node': 'k8s-control01'}]

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
