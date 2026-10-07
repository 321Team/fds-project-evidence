import json,pathlib
root=pathlib.Path(__file__).resolve().parent
policy=json.loads((root/'policy.json').read_text())
pods={x['metadata']['uid']:x for q in policy['queries'] if q['projection']=='pod' for x in q['items']}
dns=next(x['spec']['clusterIP'] for q in policy['queries'] if q['command'][4]=='services' for x in q['items'] if x['metadata']['name']=='kube-dns')
engines=sorted([x['status']['podIP'] for x in pods.values() if x['metadata'].get('labels',{}).get('app')=='fds-engine'])
child=r'''import datetime,json,socket,struct,sys,time
c=json.loads(sys.argv[1]); t=time.monotonic(); out={'case':c,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM if c['protocol']=='UDP' else socket.SOCK_STREAM);s.settimeout(3)
try:
 s.bind((c['source_ip'],c['source_port']));out['bound']=list(s.getsockname())
 if c['protocol']=='TCP':s.connect((c['destination'],c['port']));out['actual']='CONNECTED'
 else:
  ident=0x53a1;qname=c.get('qname','kubernetes.default.svc.cluster.local');wire=b''.join(bytes([len(x)])+x.encode('ascii') for x in qname.split('.'))+b'\x00'
  packet=struct.pack('!HHHHHH',ident,0x0100,1,0,0,0)+wire+struct.pack('!HH',1,1)
  s.connect((c['destination'],53));s.send(packet);reply=s.recv(4096)
  xid,flags,qd,an,ns,ar=struct.unpack('!HHHHHH',reply[:12]);assert xid==ident and flags&0x8000 and qd==1
  out.update(actual='DNS_REPLY',rcode=flags&15,answers=an,reply_bytes=len(reply),qname=qname)
except socket.timeout:out['actual']='TIMEOUT'
except ConnectionRefusedError:out['actual']='REFUSED'
except Exception as e:out.update(actual='ERROR',error=type(e).__name__+':'+str(e))
finally:s.close()
out.update(elapsed_seconds=round(time.monotonic()-t,3),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());print(json.dumps(out))
sys.exit(0 if out['actual']==c['expect'] and (out['actual']!='DNS_REPLY' or out['rcode']==0) else 3)
'''
runner=r'''import datetime,hashlib,json,os,pathlib,socket,subprocess,sys,time
CONFIG=__CONFIG__
CHILD=__CHILD__
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
'''
def make(node,selector,cases,name):
 inv=json.loads((root/('node'+node+'-inventory.json')).read_text())
 entries=[]
 for p in inv['pods']:
  if not selector(p):continue
  k=pods[p['metadata']['uid']];assert k['metadata']['name']==p['metadata']['name']
  assert k['status']['phase']=='Running' and any(c['type']=='Ready' and c['status']=='True' for c in k['status']['conditions'])
  entries.append({'pin':p,'api_pod':k,'cases':cases(k)})
 assert entries
 config={'host':inv['host'],'sources':entries}
 source=runner.replace('__CONFIG__',repr(config)).replace('__CHILD__',repr(child))
 compile(source,name,'exec');(root/name).write_text(source,encoding='utf-8',newline='\n')
def tcp(k,ip,port,expect,n):return {'protocol':'TCP','source_ip':k['status']['podIP'],'source_port':55801+n,'destination':ip,'port':port,'expect':expect}
make('108',lambda p:p['metadata']['name'].startswith('transaction-api'),lambda k:[tcp(k,ip,8001,'CONNECTED',n) for n,ip in enumerate(engines)],'if03-positive.py')
make('102',lambda p:p['metadata']['name']=='coredns-589f44dc88-f8l54',lambda k:[tcp(k,ip,8001,'TIMEOUT',n) for n,ip in enumerate(engines)],'if03-negative.py')
print('Pinned 3 positive and 3 negative TCP connects; no payload; no policy writes.')
def udp(k,ip,expect,n,qname):return {'protocol':'UDP','source_ip':k['status']['podIP'],'source_port':55901+n,'destination':ip,'port':53,'expect':expect,'qname':qname}
def dns_cases(k):
 return [udp(k,dns,'DNS_REPLY',0,'kubernetes.default.svc.cluster.local'),udp(k,'8.8.8.8','TIMEOUT',1,'example.com')]+([tcp(k,'1.1.1.1',443,'TIMEOUT',10)] if k['metadata'].get('labels',{}).get('app')!='fds-engine' else [])
for node in ('105','107','108'):
 make(node,lambda p:p['metadata']['namespace'] in ('fds-app','monitoring-api'),dns_cases,'if13-node'+node+'.py')
make('102',lambda p:p['metadata']['name']=='coredns-589f44dc88-f8l54',lambda k:[udp(k,'8.8.8.8','DNS_REPLY',2,'example.com')],'if13-control.py')
