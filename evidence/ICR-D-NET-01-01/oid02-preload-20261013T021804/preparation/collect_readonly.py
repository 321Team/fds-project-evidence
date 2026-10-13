"""Read only current OID scheduling/cache/installed CLI prerequisites, no writes."""
from pathlib import Path
import sys
from read_transport import run
P=Path(__file__).resolve().parent
kind,host=sys.argv[1:]
addresses={'k8s-control01':'10.1.93.102','k8s-control02':'10.1.93.103','k8s-control03':'10.1.93.104','k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
assert kind in ['scheduling','cache','cachecli'] and host in addresses
base="""import datetime,hashlib,json,os,pathlib,socket,stat,subprocess,time
assert os.geteuid()==0 and socket.gethostname()==__HOST__,'HOST_OR_PRIVILEGE'
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
 addresses=[x['local'] for y in json.loads(raw) for x in y.get('addr_info',[]) if x.get('family')=='inet'];assert __IP__ in addresses
 ip['addresses']=addresses
 __BODY__
 out['status']='COLLECTED_REVIEW_REQUIRED'
except Exception as e:out.update(status='INCOMPLETE',error=type(e).__name__+':'+str(e))
out['finished_at_utc']=now();print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
"""
scheduling="""kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s']
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
  row['items']=items"""
cache="""assert stat.S_ISSOCK(os.stat('/run/containerd/containerd.sock').st_mode)
 ctr=['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io']
 needles=['quay.io/calico/kube-controllers','registry.k8s.io/coredns/coredns','df00967cbd6d88e1ff3123e1598895845622e2987928b4ebd9d8ac49aefe00c3','e7e6440cfd1e919280958f5b5a6ab2b184d385bba774c12ad2a9e1e4183f90d9']
 refs=['quay.io/calico/kube-controllers@sha256:'+needles[2],'registry.k8s.io/coredns/coredns:v1.14.2','registry.k8s.io/coredns/coredns@sha256:'+needles[3]]
 for args in [['version'],['images','list']]+[['images','check','name=='+ref] for ref in refs]:
  row,raw=query(ctr+args,10);assert row['rc']==0
  txt=raw.decode(errors='replace')
  row['stdout_selected_lines']='\\n'.join(line for i,line in enumerate(txt.splitlines()) if args!=['images','list'] or i==0 or any(s in line for s in needles))
  row['selection']='all output' if args!=['images','list'] else 'header plus fixed image reference/digest rows only'
 for path in ['/usr/bin/ctr']+[p for p in ['/usr/bin/crictl','/usr/local/bin/crictl'] if pathlib.Path(p).is_file()]:
  p=pathlib.Path(path);raw=p.read_bytes();out.setdefault('binaries',[]).append({'path':path,'resolved':str(p.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)})
 for path in ['/root','/var/lib/containerd']:
  s=os.statvfs(path);out.setdefault('space',[]).append({'path':path,'free_bytes':s.f_bavail*s.f_frsize,'free_inodes':s.f_favail})
 row,raw=query(['/usr/bin/systemctl','is-active','containerd','kubelet']);row['stdout']=raw.decode();assert row['rc']==0
 row,raw=query(['/usr/sbin/getenforce']);row['stdout']=raw.decode();assert row['rc']==0
 if socket.gethostname()=='k8s-control01':
  for args in [['images','export','--help'],['images','import','--help'],['images','tag','--help'],['images','remove','--help']]:
   row,raw=query(ctr+args);row['stdout']=raw.decode();assert row['rc']==0"""
if kind=='scheduling':assert host=='k8s-control01'
if kind=='cachecli':
 assert host=='k8s-control01'
 cache=cache[:cache.index(' for args in')]+cache[cache.index(" for path in ['/usr/bin/ctr']"):]
source=base.replace('__HOST__',repr(host)).replace('__IP__',repr(addresses[host])).replace('__BODY__',scheduling if kind=='scheduling' else cache)
compile(source,'oid_readonly','exec')
r=run(host+'-'+kind,addresses[host],source,timeout=85)
raise SystemExit(0 if r['rc']==0 else 2)
