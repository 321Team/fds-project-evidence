"""Existing edge/API/MON network paths, pinned live Pod UID/container/PID; GET only."""
import base64,concurrent.futures,json,pathlib,sys
import runtime as r
phase=sys.argv[1];sample=sys.argv[2];assert phase in ('r1','r2') and sample in ('before','after','final')
inv=r.load(r.O/(phase+'-observer-inventory')/'stdout.json')
pods=[p for p in inv['pods'] if p['namespace']=='fds-app'];assert len(pods)==6
assert all(p['deletionTimestamp'] is None and all(c['ready'] for c in p['containers']) for p in pods)
service=next(s for s in inv['services'] if s['name']=='transaction-api-nodeport');assert service['spec']['externalTrafficPolicy']=='Local'
nodeips={'k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
http=(r.O/'http_observation_body.py').read_text()
tasks=[]
if sample in ('before','final'):
 targets=[]
 for pod in pods:
  if pod['labels'].get('app')!='transaction-api':continue
  assert sum(p['labels'].get('app')=='transaction-api' and p['node']==pod['node'] for p in pods)==1
  for path in ['/livez','/readyz','/metrics']:
   targets.append({'host':nodeips[pod['node']],'port':30080,'path':path,'pod_uid':pod['uid'],'pod_ip':pod['ip'],'service_local_endpoint_basis':True})
 source='import os,socket,datetime as dt\nassert socket.gethostname()=="edge01" and os.geteuid()!=0\nassert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat("2026-10-15T16:20:00+09:00")\n'+http.replace('TARGETS',repr(targets))
 p=r.O/(phase+'-'+sample+'-edge-read.py');p.write_bytes(source.encode())
 tasks.append((phase+'-'+sample+'-edge-api','10.1.93.50','svc_ansible','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,p,[]))
for role in (['api','mon'] if sample in ('before','final') else ['mon']):
 sourcepod=next(p for p in inv['pods'] if (p['namespace']=='monitoring-api' if role=='mon' else p['namespace']=='fds-app' and p['labels'].get('app')=='transaction-api' and p['node']=='k8s-worker01'))
 container=next(c for c in sourcepod['containers'] if c['name']==('prometheus' if role=='mon' else 'transaction-api'))
 cid=container['containerID'].removeprefix('containerd://');assert len(cid)==64
 targets=[]
 for pod in pods:
  app=pod['labels'].get('app')
  if role=='api' and app!='fds-engine':continue
  port=(9091 if app=='transaction-api' else 9090) if role=='mon' else 8001
  for path in (['/metrics'] if role=='mon' else ['/livez','/readyz','/metrics']):
   targets.append({'host':pod['ip'],'port':port,'path':path,'pod_uid':pod['uid'],'pod_name':pod['name']})
 if role=='mon':
  targets.append({'host':'127.0.0.1','port':9090,'path':'/api/v1/query?query=up%7Bjob%3D~%22transaction-api%7Cfds-engine%22%7D','source':'PROMETHEUS_LOOPBACK'})
 code=http.replace('TARGETS',repr(targets))
 outer='''import datetime as dt,json,os,socket,subprocess
assert socket.gethostname()==HOST and os.geteuid()==0
assert dt.datetime.now(dt.timezone.utc)<dt.datetime.fromisoformat('2026-10-15T16:20:00+09:00')
cid=CID; uid=UID
def inspect():
 p=subprocess.run(['/usr/bin/crictl','inspect',cid],capture_output=True,timeout=6);assert p.returncode==0
 v=json.loads(p.stdout);assert v['status']['id']==cid and v['status']['state']=='CONTAINER_RUNNING' and v['status']['labels'].get('io.kubernetes.pod.uid')==uid
 return int(v['info']['pid'])
pid=inspect();net=os.readlink('/proc/'+str(pid)+'/ns/net')
p=subprocess.run(['/usr/bin/nsenter','-t',str(pid),'-n','--','/usr/bin/python3','-B','-I','-S','-c',HTTP],capture_output=True,timeout=32)
after=inspect();netafter=os.readlink('/proc/'+str(after)+'/ns/net')
print(json.dumps({'host':socket.gethostname(),'source_uid':uid,'container_id':cid,'pid_before':pid,'pid_after':after,'netns_before':net,'netns_after':netafter,'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'note':'Existing Pod netns only; host Python; no pod exec/PF/config mutation'}))
assert pid==after and net==netafter and p.returncode==0
'''
 for key,value in [('HOST',repr(sourcepod['node'])),('CID',repr(cid)),('UID',repr(sourcepod['uid'])),('HTTP',repr(code))]:outer=outer.replace(key,value)
 p=r.O/(phase+'-'+sample+'-'+role+'-read.py');p.write_bytes(outer.encode());compile(outer,str(p),'exec')
 tasks.append((phase+'-'+sample+'-'+role,nodeips[sourcepod['node']],'svc_ansible','/home/server01_ansible/.ssh/p1_ansible_ed25519',True,p,[]))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(r.collect.remote,tasks))
for item in results:
 print(json.dumps(item),flush=True)
 if item['rc']==0:
  value=r.load(r.O/item['label']/'stdout.json');httpdata=json.loads(value['stdout']) if 'stdout' in value else value
  print(json.dumps({'label':item['label'],'statuses':[(v['path'],v.get('status'),v.get('error')) for v in httpdata['requests']]}),flush=True)
assert all(v['rc']==0 for v in results)
