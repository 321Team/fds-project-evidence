import datetime,hashlib,json,os,pathlib,socket,subprocess,sys,time
CONFIG={'host': 'k8s-worker01', 'pin': {'metadata': {'name': 'node-exporter-4gtms', 'namespace': 'monitoring-node', 'uid': 'c4dcab33-df59-4812-96ad-3ca14e4b9fce'}, 'sandbox_id': '13c23705eab693ad7ffb9b2cb082750baf130f929daf52aec99dcac72a317544', 'pid': 4409, 'starttime': '46184', 'netns': 'net:[4026531840]', 'cgroup': '0::/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podc4dcab33_df59_4812_96ad_3ca14e4b9fce.slice/cri-containerd-13c23705eab693ad7ffb9b2cb082750baf130f929daf52aec99dcac72a317544.scope\n', 'host_netns': 'net:[4026531840]'}, 'api_pod': {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': 'node-exporter-4gtms', 'namespace': 'monitoring-node', 'uid': 'c4dcab33-df59-4812-96ad-3ca14e4b9fce', 'resourceVersion': '4371572', 'generation': 1, 'labels': {'app': 'node-exporter', 'controller-revision-hash': '7f89794f85', 'pod-template-generation': '9'}}, 'spec': {'nodeName': 'k8s-worker01', 'hostNetwork': True, 'serviceAccountName': 'node-exporter-sa', 'dnsPolicy': 'ClusterFirst'}, 'containers': [{'name': 'node-exporter', 'image': '10.1.93.54/fds/node-exporter@sha256:4d5c92fcbea9fd5f2769a13192885366f6d348443ea6b48783590c9d9be43318', 'ports': [{'containerPort': 9100, 'hostPort': 9100, 'protocol': 'TCP'}]}], 'status': {'phase': 'Running', 'podIP': '10.1.93.105', 'hostIP': '10.1.93.105', 'conditions': [{'lastProbeTime': None, 'lastTransitionTime': '2026-10-05T13:35:47Z', 'observedGeneration': 1, 'status': 'True', 'type': 'PodReadyToStartContainers'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-10-01T06:47:40Z', 'observedGeneration': 1, 'status': 'True', 'type': 'Initialized'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-10-05T13:35:48Z', 'observedGeneration': 1, 'status': 'True', 'type': 'Ready'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-10-05T13:35:48Z', 'observedGeneration': 1, 'status': 'True', 'type': 'ContainersReady'}, {'lastProbeTime': None, 'lastTransitionTime': '2026-10-01T06:47:40Z', 'observedGeneration': 1, 'status': 'True', 'type': 'PodScheduled'}]}}, 'host_network': True, 'egress_chain': 'cali-po-_IZ_dpYgvbSNCZTvi1r-', 'cases': [{'protocol': 'UDP', 'source_ip': '10.1.93.105', 'source_port': 56101, 'destination': '10.1.93.52', 'port': 53, 'expect': 'DNS_REPLY', 'qname': 'example.com'}, {'protocol': 'UDP', 'source_ip': '10.1.93.105', 'source_port': 56102, 'destination': '10.1.93.53', 'port': 53, 'expect': 'DNS_REPLY', 'qname': 'example.com'}, {'protocol': 'TCP', 'source_ip': '10.1.93.105', 'source_port': 56103, 'destination': '10.1.93.52', 'port': 53, 'expect': 'CONNECTED', 'qname': 'example.com'}, {'protocol': 'TCP', 'source_ip': '10.1.93.105', 'source_port': 56104, 'destination': '10.1.93.53', 'port': 53, 'expect': 'CONNECTED', 'qname': 'example.com'}, {'protocol': 'UDP', 'source_ip': '10.1.93.105', 'source_port': 56105, 'destination': '8.8.8.8', 'port': 53, 'expect': 'TIMEOUT', 'qname': 'example.com'}, {'protocol': 'TCP', 'source_ip': '10.1.93.105', 'source_port': 56106, 'destination': '1.1.1.1', 'port': 443, 'expect': 'TIMEOUT', 'qname': 'example.com'}]}
CHILD="import datetime,json,socket,struct,sys,time\nc=json.loads(sys.argv[1]); t=time.monotonic(); out={'case':c,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}\ns=socket.socket(socket.AF_INET,socket.SOCK_DGRAM if c['protocol']=='UDP' else socket.SOCK_STREAM);s.settimeout(3)\ntry:\n s.bind((c['source_ip'],c['source_port']));out['bound']=list(s.getsockname())\n if c['protocol']=='TCP':s.connect((c['destination'],c['port']));out['actual']='CONNECTED'\n else:\n  ident=0x53a1;qname=c.get('qname','kubernetes.default.svc.cluster.local');wire=b''.join(bytes([len(x)])+x.encode('ascii') for x in qname.split('.'))+b'\\x00'\n  packet=struct.pack('!HHHHHH',ident,0x0100,1,0,0,0)+wire+struct.pack('!HH',1,1)\n  s.connect((c['destination'],53));s.send(packet);reply=s.recv(4096)\n  xid,flags,qd,an,ns,ar=struct.unpack('!HHHHHH',reply[:12]);assert xid==ident and flags&0x8000 and qd==1\n  out.update(actual='DNS_REPLY',rcode=flags&15,answers=an,reply_bytes=len(reply),qname=qname)\nexcept socket.timeout:out['actual']='TIMEOUT'\nexcept ConnectionRefusedError:out['actual']='REFUSED'\nexcept Exception as e:out.update(actual='ERROR',error=type(e).__name__+':'+str(e))\nfinally:s.close()\nout.update(elapsed_seconds=round(time.monotonic()-t,3),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());print(json.dumps(out))\nsys.exit(0 if out['actual']==c['expect'] and (out['actual']!='DNS_REPLY' or out['rcode']==0) else 3)\n"
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity():
 p=CONFIG['pin'];v=pathlib.Path('/proc')/str(p['pid'])
 assert v.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]==p['starttime'],'PID_CHANGED'
 assert os.readlink(v/'ns/net')==p['netns'],'NETNS_CHANGED'
 assert v.joinpath('cgroup').read_text()==p['cgroup'],'CGROUP_CHANGED'
 assert (p['netns']==os.readlink('/proc/1/ns/net'))==CONFIG['host_network'],'NETWORK_KIND_CHANGED'
def table():
 p=subprocess.run(['iptables-save','-c','-t','filter'],capture_output=True,timeout=8)
 assert p.returncode==0,p.stderr.decode(errors='replace')
 return p.stdout.decode()
def chain_snapshot():
 raw=table();chain=CONFIG['egress_chain']
 return {'utc':now(),'raw_filter_sha256':hashlib.sha256(raw.encode()).hexdigest(),'chain':chain,'lines':[l for l in raw.splitlines() if '-A '+chain+' ' in l] if chain else []}
r={'host':socket.gethostname(),'source_sha256':os.environ['COLLECTOR_SHA256'],'started_utc':now(),'config':CONFIG,'cases':[]};rc=0;fd=None;begin=time.monotonic()
try:
 assert os.geteuid()==0 and socket.gethostname().split('.')[0]==CONFIG['host'];identity()
 r['filter_before']=table()
 if CONFIG['egress_chain']:assert 'GlobalNetworkPolicy fds-k8s-host-'+CONFIG['host']+' egress' in r['filter_before']
 fd=os.open('/proc/%d/ns/net'%CONFIG['pin']['pid'],os.O_RDONLY);assert os.readlink('/proc/self/fd/%d'%fd)==CONFIG['pin']['netns'];identity()
 for c in CONFIG['cases']:
  assert time.monotonic()-begin<90,'TIME_BUDGET';identity();before=chain_snapshot()
  cmd=['nsenter','--net=/proc/self/fd/%d'%fd,'--','python3','-I','-B','-c',CHILD,json.dumps(c)]
  p=subprocess.run(cmd,capture_output=True,timeout=7,pass_fds=(fd,))
  r['cases'].append({'command':cmd,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace'),'before':before,'after':chain_snapshot()})
  identity();assert p.returncode==0,'UNEXPECTED_RESULT_STOP'
except Exception as e:r['stop']=type(e).__name__+':'+str(e);rc=2
finally:
 if fd is not None:os.close(fd)
 try:r['filter_after']=table()
 except Exception as e:r['post_error']=str(e);rc=2
 r['finished_utc']=now();r['rc']=rc;print(json.dumps(r,indent=2))
sys.exit(rc)
