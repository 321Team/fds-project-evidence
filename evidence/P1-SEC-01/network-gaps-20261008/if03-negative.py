import datetime,hashlib,json,os,pathlib,socket,subprocess,sys,time
CONFIG={'host': 'k8s-control01', 'sources': [{'pin': {'metadata': {'name': 'coredns-589f44dc88-f8l54', 'namespace': 'kube-system', 'uid': 'b177ca1d-d26a-4e55-acc6-2cc384e6d281'}, 'sandbox_id': '8157cecba4610d144ced5b4b8eebb9cc691c292eae4843c9e96045cc8c8ed1e3', 'pid': 5896, 'starttime': '13990', 'netns': 'net:[4026533097]', 'cgroup': '0::/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podb177ca1d_d26a_4e55_acc6_2cc384e6d281.slice/cri-containerd-8157cecba4610d144ced5b4b8eebb9cc691c292eae4843c9e96045cc8c8ed1e3.scope\n', 'host_netns': 'net:[4026531840]'}, 'api_pod': {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': 'coredns-589f44dc88-f8l54', 'namespace': 'kube-system', 'uid': 'b177ca1d-d26a-4e55-acc6-2cc384e6d281', 'resourceVersion': '3992780', 'generation': 1, 'labels': {'k8s-app': 'kube-dns', 'pod-template-hash': '589f44dc88'}}, 'spec': {'nodeName': 'k8s-control01', 'serviceAccountName': 'coredns', 'dnsPolicy': 'Default'}, 'containers': [{'name': 'coredns', 'image': 'registry.k8s.io/coredns/coredns:v1.14.2', 'ports': [{'containerPort': 53, 'name': 'dns', 'protocol': 'UDP'}, {'containerPort': 53, 'name': 'dns-tcp', 'protocol': 'TCP'}, {'containerPort': 9153, 'name': 'metrics', 'protocol': 'TCP'}, {'containerPort': 8080, 'name': 'liveness-probe', 'protocol': 'TCP'}, {'containerPort': 8181, 'name': 'readiness-probe', 'protocol': 'TCP'}]}], 'status': {'phase': 'Running', 'podIP': '10.244.246.121', 'hostIP': '10.1.93.102', 'conditions': [{'lastProbeTime': None, 'lastTransitionTime': '2026-10-05T13:36:38Z', 'observedGeneration': 1, 'status': 'True', 'type': 'PodReadyToStartContainers'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-09-09T12:36:39Z', 'observedGeneration': 1, 'status': 'True', 'type': 'Initialized'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-10-05T13:36:38Z', 'observedGeneration': 1, 'status': 'True', 'type': 'Ready'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-10-05T13:36:38Z', 'observedGeneration': 1, 'status': 'True', 'type': 'ContainersReady'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-09-09T12:36:39Z', 'observedGeneration': 1, 'status': 'True', 'type': 'PodScheduled'}]}}, 'cases': [{'protocol': 'TCP', 'source_ip': '10.244.246.121', 'source_port': 55801, 'destination': '10.244.39.209', 'port': 8001, 'expect': 'TIMEOUT'}, {'protocol': 'TCP', 'source_ip': '10.244.246.121', 'source_port': 55802, 'destination': '10.244.69.237', 'port': 8001, 'expect': 'TIMEOUT'}, {'protocol': 'TCP', 'source_ip': '10.244.246.121', 'source_port': 55803, 'destination': '10.244.79.113', 'port': 8001, 'expect': 'TIMEOUT'}]}]}
CHILD="import datetime,json,socket,struct,sys,time\nc=json.loads(sys.argv[1]); t=time.monotonic(); out={'case':c,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}\ns=socket.socket(socket.AF_INET,socket.SOCK_DGRAM if c['protocol']=='UDP' else socket.SOCK_STREAM);s.settimeout(3)\ntry:\n s.bind((c['source_ip'],c['source_port']));out['bound']=list(s.getsockname())\n if c['protocol']=='TCP':s.connect((c['destination'],c['port']));out['actual']='CONNECTED'\n else:\n  ident=0x53a1;qname=c.get('qname','kubernetes.default.svc.cluster.local');wire=b''.join(bytes([len(x)])+x.encode('ascii') for x in qname.split('.'))+b'\\x00'\n  packet=struct.pack('!HHHHHH',ident,0x0100,1,0,0,0)+wire+struct.pack('!HH',1,1)\n  s.connect((c['destination'],53));s.send(packet);reply=s.recv(4096)\n  xid,flags,qd,an,ns,ar=struct.unpack('!HHHHHH',reply[:12]);assert xid==ident and flags&0x8000 and qd==1\n  out.update(actual='DNS_REPLY',rcode=flags&15,answers=an,reply_bytes=len(reply),qname=qname)\nexcept socket.timeout:out['actual']='TIMEOUT'\nexcept ConnectionRefusedError:out['actual']='REFUSED'\nexcept Exception as e:out.update(actual='ERROR',error=type(e).__name__+':'+str(e))\nfinally:s.close()\nout.update(elapsed_seconds=round(time.monotonic()-t,3),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());print(json.dumps(out))\nsys.exit(0 if out['actual']==c['expect'] and (out['actual']!='DNS_REPLY' or out['rcode']==0) else 3)\n"
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity(p):
 pid=p['pid'];v=pathlib.Path('/proc')/str(pid)
 assert v.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]==p['starttime'],'PID_REPLACED'
 assert os.readlink(v/'ns/net')==p['netns'] and p['netns']!=os.readlink('/proc/1/ns/net'),'NETNS_CHANGED_OR_HOST'
 assert v.joinpath('cgroup').read_text()==p['cgroup'],'CGROUP_CHANGED'
def iptables():
 p=subprocess.run(['iptables-save','-c','-t','filter'],capture_output=True,timeout=10)
 return {'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
r={'started_utc':stamp(),'host':socket.gethostname(),'source_sha256':os.environ['COLLECTOR_SHA256'],'scope':'host Python in pinned existing Pod network namespace only; no mount/pid/user namespace entry; no policy/Pod/file changes; no application request','config':CONFIG,'cases':[]}
rc=0;start=time.monotonic()
try:
 assert os.geteuid()==0 and socket.gethostname().split('.')[0]==CONFIG['host']
 r['iptables_before']=iptables();assert r['iptables_before']['rc']==0
 for entry in CONFIG['sources']:
  p=entry['pin'];identity(p);fd=os.open('/proc/%d/ns/net'%p['pid'],os.O_RDONLY)
  try:
   assert os.readlink('/proc/self/fd/%d'%fd)==p['netns'];identity(p)
   for case in entry['cases']:
    assert time.monotonic()-start<100,'BUDGET';identity(p)
    command=['nsenter','--net=/proc/self/fd/%d'%fd,'--','python3','-I','-B','-c',CHILD,json.dumps(case)]
    q=subprocess.run(command,capture_output=True,timeout=7,pass_fds=(fd,))
    r['cases'].append({'pod_uid':p['metadata']['uid'],'command':command,'rc':q.returncode,'stdout':q.stdout.decode(errors='replace'),'stderr':q.stderr.decode(errors='replace')})
    identity(p)
    assert q.returncode==0,'UNEXPECTED_RESULT_STOP'
  finally:os.close(fd)
except Exception as e:r['stop']=type(e).__name__+':'+str(e);rc=2
finally:
 r['iptables_after']=iptables();r['finished_utc']=stamp();r['rc']=rc;print(json.dumps(r,indent=2))
sys.exit(rc)
