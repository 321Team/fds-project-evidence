import os,socket,subprocess,json,hashlib,datetime
from pathlib import Path
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
out={'started_at_utc':now(),'host':socket.gethostname(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'mutation':False,'token_issued':False,'queries':[],'ca_sha256':hashlib.sha256(Path('/etc/kubernetes/pki/ca.crt').read_bytes()).hexdigest()}
queries=[('serviceaccount','/api/v1/namespaces/ci-cd/serviceaccounts/cicd-runner-sa'),('deployments','/apis/apps/v1/namespaces/fds-app/deployments'),('rolebindings','/apis/rbac.authorization.k8s.io/v1/namespaces/fds-app/rolebindings'),('roles','/apis/rbac.authorization.k8s.io/v1/namespaces/fds-app/roles'),('hpa','/apis/autoscaling/v2/namespaces/fds-app/horizontalpodautoscalers')]
for kind,path in queries:
 argv=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
 p=subprocess.run(argv,capture_output=True,timeout=20)
 q={'kind':kind,'argv':argv,'rc':p.returncode,'at_utc':now(),'raw_stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'items':[]}
 if p.returncode==0:
  doc=json.loads(p.stdout)
  for x in doc.get('items',[doc]):
   m=x.get('metadata',{});s=x.get('spec',{})
   if kind=='deployments' and m.get('name') not in ['transaction-api','fds-engine']:continue
   row={'metadata':{k:m.get(k) for k in ['name','namespace','uid','resourceVersion','generation']}}
   if kind=='serviceaccount':row['automountServiceAccountToken']=x.get('automountServiceAccountToken')
   elif kind=='deployments':
    row['spec_sha256']=hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    row['containers']=[{k:c.get(k) for k in ['name','image','imagePullPolicy']} for c in s.get('template',{}).get('spec',{}).get('containers',[])]
    row['replicas']=s.get('replicas');row['status']={k:x.get('status',{}).get(k) for k in ['observedGeneration','readyReplicas','availableReplicas','updatedReplicas']}
   elif kind=='roles':row['rules']=x.get('rules',[])
   elif kind=='rolebindings':row.update(roleRef=x.get('roleRef'),subjects=x.get('subjects',[]))
   else:row['spec']=s
   q['items'].append(row)
 out['queries'].append(q)
out['finished_at_utc']=now();print(json.dumps(out))
