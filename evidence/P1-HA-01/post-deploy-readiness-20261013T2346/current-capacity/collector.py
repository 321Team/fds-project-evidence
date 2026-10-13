import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':[],'mutation':False}
for name,args in [('capacity',['describe','node','k8s-worker01','k8s-worker03']),('drain-help',['drain','--help']),('rs',['get','rs','-n','fds-app','-o','json'])]:
 p=subprocess.run(kc+args,capture_output=True,timeout=15)
 item={'name':name,'argv':kc+args,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()}
 if name=='rs' and p.returncode==0:
  item['items']=[{'metadata':{k:r['metadata'].get(k) for k in ('name','uid','resourceVersion','ownerReferences')},'replicas':r['spec'].get('replicas'),'selector':r['spec'].get('selector')} for r in json.loads(p.stdout)['items'] if r['spec'].get('replicas',0)>0]
 else:item['stdout']=p.stdout.decode()
 out['queries'].append(item)
print(json.dumps(out))
