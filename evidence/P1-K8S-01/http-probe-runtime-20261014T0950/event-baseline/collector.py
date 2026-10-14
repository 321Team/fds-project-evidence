"""Pure pre-check: event baseline for the fixed Pod; no injection or staging."""
import datetime,hashlib,json,os,socket,subprocess,urllib.parse
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
uid='e349b045-870f-4061-a677-3007efe479e9'
pod='fds-engine-65479b5bf-4gfgq'
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=5s']
rows=[]
queries=[('pod','/api/v1/namespaces/fds-app/pods/'+pod),('events','/api/v1/namespaces/fds-app/events?fieldSelector='+urllib.parse.quote('involvedObject.uid='+uid,safe=''))]
for name,path in queries:
 p=subprocess.run(kc+['get','--raw='+path],capture_output=True,timeout=8)
 assert p.returncode==0 and len(p.stdout)<2*1024*1024
 x=json.loads(p.stdout)
 if name=='pod':
  assert x['metadata']['uid']==uid and x['spec']['nodeName']=='k8s-worker02'
  data={'metadata':{k:x['metadata'].get(k) for k in ('name','uid','resourceVersion','deletionTimestamp')},'probes':[{k:c.get(k) for k in ('name','livenessProbe','readinessProbe','startupProbe')} for c in x['spec']['containers']],'status':x['status']}
 else:
  data={'resourceVersion':x['metadata']['resourceVersion'],'events':[{'metadata':{k:e['metadata'].get(k) for k in ('uid','resourceVersion','creationTimestamp')},**{k:e.get(k) for k in ('involvedObject','reason','message','type','count','firstTimestamp','lastTimestamp','eventTime','series','source','reportingComponent')}} for e in x['items']]}
 rows.append({'kind':name,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':kc+['get','--raw='+path],'rc':0,'raw_sha256':hashlib.sha256(p.stdout).hexdigest(),'data':data})
print(json.dumps({'scope':'READ_ONLY_PRECHECK','signals':0,'queries':rows}))
