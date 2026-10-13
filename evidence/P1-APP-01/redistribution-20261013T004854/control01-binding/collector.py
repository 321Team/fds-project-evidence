import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s']
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def meta(x):return {k:x.get('metadata',{}).get(k) for k in ['name','namespace','uid','resourceVersion','generation','creationTimestamp','deletionTimestamp','ownerReferences','labels']}
queries=[('cluster',['get','namespace','kube-system','-o','json']),('deployments',['get','deploy','-n','fds-app','transaction-api','fds-engine','-o','json']),('rs',['get','rs','-n','fds-app','-o','json']),('pods',['get','pods','-n','fds-app','-o','json']),('nodes',['get','nodes','-o','json']),('pdb',['get','pdb','-n','fds-app','-o','json']),('hpa',['get','hpa','-n','fds-app','-o','json']),('endpoints',['get','endpointslices','-n','fds-app','-o','json'])]
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'boot':open('/proc/sys/kernel/random/boot_id').read().strip(),'scope':'source-of-truth binding for bounded redistribution plan, no mutation','queries':[]}
for kind,args in queries:
 p=subprocess.run(kc+args,capture_output=True,timeout=8);row={'name':kind,'argv':kc+args,'rc':p.returncode,'raw_response_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode(errors='replace')};items=[]
 if p.returncode==0:
  data=json.loads(p.stdout)
  for x in data.get('items',[data]):
   s=x.get('spec',{});st=x.get('status',{});r={'metadata':meta(x)}
   if kind=='deployments':
    pod=s['template']['spec'];r.update(spec_sha256=digest(s),template_sha256=digest(s['template']),replicas=s.get('replicas'),paused=s.get('paused',False),strategy=s.get('strategy'),minReadySeconds=s.get('minReadySeconds'),progressDeadlineSeconds=s.get('progressDeadlineSeconds'),selector=s.get('selector'),images=[{'name':c['name'],'image':c['image'],'imagePullPolicy':c.get('imagePullPolicy')} for c in pod.get('containers',[])],spread=pod.get('topologySpreadConstraints'),resources=[c.get('resources') for c in pod.get('containers',[])],status={k:st.get(k) for k in ['observedGeneration','replicas','readyReplicas','updatedReplicas','availableReplicas','unavailableReplicas']})
   elif kind=='rs':r.update(replicas=s.get('replicas'),status={k:st.get(k) for k in ['replicas','readyReplicas','availableReplicas','observedGeneration']})
   elif kind=='pods':r.update(node=s.get('nodeName'),images=[c['image'] for c in s.get('containers',[])],phase=st.get('phase'),conditions=[{k:c.get(k) for k in ['type','status','lastTransitionTime']} for c in st.get('conditions',[])],ready=any(c['type']=='Ready' and c['status']=='True' for c in st.get('conditions',[])),grace=s.get('terminationGracePeriodSeconds'),restarts=[{'name':c['name'],'restartCount':c['restartCount']} for c in st.get('containerStatuses',[])])
   elif kind=='nodes':r.update(taints=s.get('taints'),unschedulable=s.get('unschedulable',False),allocatable=st.get('allocatable'),conditions=[{k:c.get(k) for k in ['type','status','lastTransitionTime']} for c in st.get('conditions',[])])
   elif kind=='endpoints':r.update(endpoints=x.get('endpoints'),ports=x.get('ports'))
   elif kind in ['pdb','hpa']:r.update(spec=s,status=st)
   items.append(r)
  row['items']=items
 out['queries'].append(row)
out['status']='COLLECTED' if all(x['rc']==0 for x in out['queries']) else 'INCOMPLETE';print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED' else 2)
