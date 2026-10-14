import os,pathlib,json,socket,time,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
p=pathlib.Path('/var/tmp/p1-ha-20261014-0015');os.umask(0o077)
d=json.loads((p/'drain-result.json').read_bytes());assert d['rc']==0
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=8s']
images={'transaction-api':'10.1.93.54/fds/transaction-api@sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0','fds-engine':'10.1.93.54/fds/fds-engine@sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d'}
rs={'transaction-api':'7ff3c110-8cca-4b26-abad-fb67baa57baf','fds-engine':'ad644957-7157-4b4a-a342-244bc0ab8483'}
observations=[];ready=False;deadline=d['finished_epoch']+120
while time.time()<deadline:
 r=subprocess.run(kc+['get','pods','-n','fds-app','-o','json'],capture_output=True,timeout=10);assert r.returncode==0
 pods=json.loads(r.stdout)['items'];snapshot=[]
 for x in pods:
  app=x['metadata']['labels']['app'];assert x['metadata']['ownerReferences'][0]['uid']==rs[app]
  statuses=x['status'].get('containerStatuses',[])
  assert all(c.get('imageID') in ('',None,images[app]) for c in statuses)
  snapshot.append({'app':app,'name':x['metadata']['name'],'uid':x['metadata']['uid'],'rv':x['metadata']['resourceVersion'],'node':x['spec'].get('nodeName'),'deleting':x['metadata'].get('deletionTimestamp'),'ready':bool(statuses) and all(c['ready'] and c['restartCount']==0 and c['imageID']==images[app] for c in statuses),'phase':x['status']['phase'],'owners':x['metadata']['ownerReferences']})
 ready=len(snapshot)==6 and all(sum(x['app']==a for x in snapshot)==3 for a in images) and all(x['ready'] and not x['deleting'] and x['node']!='k8s-worker02' for x in snapshot)
 observations.append({'epoch':time.time(),'ready':ready,'pods':snapshot})
 if ready:break
 time.sleep(3)
result={'ready':ready,'observations':observations,'deadline':deadline,'finished_epoch':time.time()}
if ready:
 lines=(p/'timeline.txt').read_text().splitlines();assert len(lines)==2
 at=time.time()
 with (p/'timeline.txt').open('a') as f:f.write('rescheduled_ready %.6f\n'%at);f.flush();os.fsync(f.fileno())
 result['mark_epoch']=at
with (p/'rescheduled-ready-result.json').open('x') as f:json.dump(result,f)
print(json.dumps(result))
