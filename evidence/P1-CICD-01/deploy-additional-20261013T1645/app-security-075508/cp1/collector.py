import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
args=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw=/apis/apps/v1/namespaces/fds-app/deployments']
r=subprocess.run(args,capture_output=True,timeout=15);assert r.returncode==0
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'mutation':False,'argv':args,'rc':r.returncode,'raw_sha256':hashlib.sha256(r.stdout).hexdigest(),'items':[]}
allowed=('runAsUser','runAsGroup','runAsNonRoot','fsGroup','readOnlyRootFilesystem','allowPrivilegeEscalation')
for x in json.loads(r.stdout)['items']:
    spec=x['spec']['template']['spec'];row={'name':x['metadata']['name'],'uid':x['metadata']['uid'],'generation':x['metadata']['generation'],'pod_security':{k:v for k,v in spec.get('securityContext',{}).items() if k in allowed},'containers':[]}
    for c in spec['containers']:row['containers'].append({'name':c['name'],'security':{k:v for k,v in c.get('securityContext',{}).items() if k in allowed},'mount_paths':[v['mountPath'] for v in c.get('volumeMounts',[])]})
    out['items'].append(row)
print(json.dumps(out,sort_keys=True))
