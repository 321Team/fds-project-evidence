import datetime,hashlib,json,os,pathlib,socket,stat,subprocess,time
assert os.geteuid()==0 and socket.gethostname()=='k8s-control01','HOST_OR_PRIVILEGE'
started=time.monotonic()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
out={'host':socket.gethostname(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'started_at_utc':now(),'scope':'read only OID scheduling/cache/CLI prerequisites; no export/import/retag/pull/unpack/pod/reboot','commands':[]}
def query(argv,limit=8):
 assert time.monotonic()-started<65,'READ_BUDGET'
 row={'argv':argv,'started_at_utc':now()}
 try:
  p=subprocess.run(argv,capture_output=True,timeout=limit,env=dict(os.environ,LC_ALL='C'))
  row.update(rc=p.returncode,stdout_bytes=len(p.stdout),stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_bytes=len(p.stderr),stderr_sha256=hashlib.sha256(p.stderr).hexdigest(),stderr=p.stderr.decode(errors='replace'),finished_at_utc=now())
  assert len(p.stdout)<4*1024*1024 and len(p.stderr)<65536,'OUTPUT_BOUND'
  out['commands'].append(row);return row,p.stdout
 except subprocess.TimeoutExpired:
  row.update(rc=None,error='READ_TIMEOUT_NO_RETRY',finished_at_utc=now());out['commands'].append(row);raise
try:
 ip,raw=query(['/usr/sbin/ip','-j','-4','address','show']);assert ip['rc']==0
 addresses=[x['local'] for y in json.loads(raw) for x in y.get('addr_info',[]) if x.get('family')=='inet'];assert '10.1.93.102' in addresses
 ip['addresses']=addresses
 kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s']
 def meta(x):return {k:x.get('metadata',{}).get(k) for k in ['name','namespace','uid','resourceVersion','generation','deletionTimestamp','ownerReferences','labels']}
 for kind,args in [('nodes',['get','nodes','-o','json']),('deployments',['get','deployments','-A','-o','json']),('pods',['get','pods','-A','-o','json']),('cluster',['get','namespace','kube-system','-o','json'])]:
  row,raw=query(kc+args);assert row['rc']==0
  d=json.loads(raw);items=[]
  for x in d.get('items',[d]):
   if kind in ['pods','deployments'] and not (x['metadata']['name'].startswith('calico-kube-controllers') or x['metadata']['name'].startswith('coredns-') or x['metadata']['name']=='coredns'):continue
   s=x.get('spec',{});st=x.get('status',{});item={'metadata':meta(x)}
   if kind=='nodes':item.update(spec=s,conditions=[{k:c.get(k) for k in ['type','status','lastTransitionTime']} for c in st.get('conditions',[])],allocatable=st.get('allocatable'),nodeInfo=st.get('nodeInfo'),addresses=st.get('addresses'))
   elif kind=='deployments':
    ps=s['template']['spec'];item.update(spec_sha256=hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest(),replicas=s.get('replicas'),status=st,selector=s.get('selector'),scheduling={k:ps.get(k) for k in ['nodeSelector','affinity','tolerations','topologySpreadConstraints','schedulerName','priorityClassName','runtimeClassName']},containers=[{k:c.get(k) for k in ['name','image','imagePullPolicy','resources']} for c in ps.get('containers',[])])
   elif kind=='pods':item.update(node=s.get('nodeName'),images=[{k:c.get(k) for k in ['name','image','imagePullPolicy']} for c in s.get('containers',[])],phase=st.get('phase'),conditions=st.get('conditions'),containerStatuses=[{k:c.get(k) for k in ['name','ready','restartCount','image','imageID','containerID','state']} for c in st.get('containerStatuses',[])])
   items.append(item)
  row['items']=items
 out['status']='COLLECTED_REVIEW_REQUIRED'
except Exception as e:out.update(status='INCOMPLETE',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
