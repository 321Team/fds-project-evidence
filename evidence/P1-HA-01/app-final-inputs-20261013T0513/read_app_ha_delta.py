"""Only the APP placement/service metadata missing from the 05:01 read."""
import datetime as dt,hashlib,json,os,socket,subprocess
from pathlib import Path
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def meta(x):return {k:x.get('metadata',{}).get(k) for k in ('name','namespace','uid','resourceVersion','generation')}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
queries=[('cluster','/api/v1/namespaces/kube-system'),('engine','/apis/apps/v1/namespaces/fds-app/deployments/fds-engine'),('api','/apis/apps/v1/namespaces/fds-app/deployments/transaction-api'),('services','/api/v1/namespaces/fds-app/services'),('endpointslices','/apis/discovery.k8s.io/v1/namespaces/fds-app/endpointslices'),('hpa','/apis/autoscaling/v2/namespaces/fds-app/horizontalpodautoscalers')]
out={'started_at_utc':now(),'host':socket.gethostname(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'mutation':False,'secret_or_env_values_collected':False,'queries':[]}
for kind,path in queries:
 argv=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
 p=subprocess.run(argv,capture_output=True,timeout=15)
 q={'kind':kind,'argv':argv,'rc':p.returncode,'at_utc':now(),'raw_stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'items':[]}
 if p.returncode==0:
  assert len(p.stdout)<2*1024*1024
  d=json.loads(p.stdout);items=d.get('items',[d]);assert len(items)<=100
  for x in items:
   r={'metadata':meta(x)};s=x.get('spec',{})
   if kind in ('engine','api'):
    ps=s.get('template',{}).get('spec',{})
    r.update({'spec_sha256':digest(s),'template_sha256':digest(s.get('template',{})),'replicas':s.get('replicas'),'strategy':s.get('strategy'),'selector':s.get('selector'),'spread':ps.get('topologySpreadConstraints'),'affinity':ps.get('affinity'),'nodeSelector':ps.get('nodeSelector'),'tolerations':ps.get('tolerations'),'images':[{k:c.get(k) for k in ('name','image','imagePullPolicy','resources')} for c in ps.get('containers',[])],'status':{k:x.get('status',{}).get(k) for k in ('observedGeneration','readyReplicas','updatedReplicas','availableReplicas')}})
   elif kind=='services':r.update({'spec':{k:s.get(k) for k in ('type','selector','clusterIP','ports','externalTrafficPolicy','internalTrafficPolicy','sessionAffinity')},'spec_sha256':digest(s)})
   elif kind=='endpointslices':r.update({'labels':x.get('metadata',{}).get('labels',{}),'ports':x.get('ports'),'addressType':x.get('addressType'),'endpoints':[{k:e.get(k) for k in ('addresses','conditions','nodeName','targetRef')} for e in x.get('endpoints',[])]})
   elif kind=='hpa':r['spec']={k:s.get(k) for k in ('scaleTargetRef','minReplicas','maxReplicas')}
   q['items'].append(r)
 out['queries'].append(q)
 if p.returncode!=0:break
out['finished_at_utc']=now();out['status']='READ_COMPLETE' if len(out['queries'])==len(queries) and all(q['rc']==0 for q in out['queries']) else 'READ_INCOMPLETE'
print(json.dumps(out))
