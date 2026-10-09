import datetime,hashlib,json,os,socket,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert '2026-10-09T19:00:00+09:00' <= now() < '2026-10-09T22:00:00+09:00'
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
out={'schema':'fds.delivery.readonly-projection.v1','started_at_kst':now(),'host':socket.gethostname(),'euid':os.geteuid(),'queries':[],'write_operations':False,'token_issued':False,'harbor_contact':False,'projection':'Selected identity/image/health fields only; no env, commands, annotations, Secret or kubeconfig contents transmitted.'}
paths=[('deployments','/apis/apps/v1/namespaces/fds-app/deployments'),('pods','/api/v1/namespaces/fds-app/pods'),('serviceaccount','/api/v1/namespaces/ci-cd/serviceaccounts/cicd-runner-sa')]
for kind,path in paths:
 cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=15s','get','--raw='+path]
 p=subprocess.run(cmd,capture_output=True,timeout=25)
 q={'kind':kind,'command':cmd,'rc':p.returncode,'observed_at_kst':now(),'raw_stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'items':[]}
 if p.returncode==0:
  obj=json.loads(p.stdout)
  for x in obj.get('items',[obj]):
   m=x.get('metadata',{});s=x.get('spec',{});status=x.get('status',{})
   if kind=='deployments' and m.get('name') not in {'transaction-api','fds-engine'}:continue
   row={'metadata':{k:m.get(k) for k in ['name','namespace','uid','resourceVersion','generation','creationTimestamp']}}
   if kind=='serviceaccount':row['automountServiceAccountToken']=x.get('automountServiceAccountToken')
   else:
    spec=s.get('template',{}).get('spec',{}) if kind=='deployments' else s
    row['containers']=[{k:c.get(k) for k in ['name','image','imagePullPolicy']} for c in spec.get('containers',[])]
    row['serviceAccountName']=spec.get('serviceAccountName','default')
    if kind=='deployments':
     row['replicas']=s.get('replicas');row['strategy']=s.get('strategy');row['status']={k:status.get(k) for k in ['observedGeneration','replicas','updatedReplicas','readyReplicas','availableReplicas']}
    else:
     row['nodeName']=s.get('nodeName');row['phase']=status.get('phase')
     row['containerStatuses']=[{k:c.get(k) for k in ['name','ready','restartCount','image','imageID']} for c in status.get('containerStatuses',[])]
     row['owners']=[{k:o.get(k) for k in ['kind','name','uid']} for o in m.get('ownerReferences',[])]
   q['items'].append(row)
 out['queries'].append(q)
out['finished_at_kst']=now()
print(json.dumps(out,ensure_ascii=False))
