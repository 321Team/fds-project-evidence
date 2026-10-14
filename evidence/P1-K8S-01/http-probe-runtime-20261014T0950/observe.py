"""Read-only observer: no remote files, configuration changes or signals."""
import concurrent.futures,datetime,json,os,socket,subprocess,time,urllib.request,urllib.error,urllib.parse
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
UID='e349b045-870f-4061-a677-3007efe479e9'
KC=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=4s']
OP=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def query(pair):
 name,path=pair
 p=subprocess.run(KC+['get','--raw='+path],capture_output=True,timeout=6)
 if p.returncode:raise RuntimeError(name+'_RC_'+str(p.returncode))
 x=json.loads(p.stdout);items=x['items']
 if name=='pods':
  data=[{'name':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec']['nodeName'],'deleted':p['metadata'].get('deletionTimestamp'),'ip':p['status'].get('podIP'),'conditions':p['status'].get('conditions'),'containers':p['status'].get('containerStatuses')} for p in items]
 elif name=='nodes':
  data=[{'name':p['metadata']['name'],'uid':p['metadata']['uid'],'unschedulable':p['spec'].get('unschedulable',False),'conditions':p['status']['conditions']} for p in items]
 elif name=='endpoints':
  data=[{'name':p['metadata']['name'],'uid':p['metadata']['uid'],'rv':p['metadata']['resourceVersion'],'labels':p['metadata'].get('labels'),'endpoints':p['endpoints']} for p in items]
 else:data=items
 return name,{'utc':now(),'resourceVersion':x['metadata'].get('resourceVersion'),'items':data}
def http(path):
 start=now()
 try:
  with OP.open('http://10.244.69.193:8001/'+path,timeout=.8) as p: code=p.status;p.read(1024)
  return path,{'started_utc':start,'ended_utc':now(),'code':code}
 except Exception as e:return path,{'started_utc':start,'ended_utc':now(),'code':getattr(e,'code',0),'error':type(e).__name__}
paths=[('pods','/api/v1/namespaces/fds-app/pods'),('endpoints','/apis/discovery.k8s.io/v1/namespaces/fds-app/endpointslices'),('nodes','/api/v1/nodes'),('events','/api/v1/namespaces/fds-app/events?fieldSelector='+urllib.parse.quote('involvedObject.uid='+UID,safe=''))]
end=time.monotonic()+600;tick=0
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 while time.monotonic()<end:
  at=time.monotonic();row={'tick':tick,'utc':now(),'scope':'READ_ONLY_RUNTIME_OBSERVATION','queries':{},'http':{}}
  fs=[pool.submit(query,p) for p in paths];hs=[pool.submit(http,p) for p in ('readyz','livez')]
  try:
   row['queries']=dict(f.result() for f in fs);row['http']=dict(f.result() for f in hs)
   pods=row['queries']['pods']['items'];others=[p for p in pods if p['uid']!=UID]
   nodes=row['queries']['nodes']['items']
   row['other_workloads_healthy']=len(pods)==6 and len(others)==5 and all(not p['deleted'] and all(c['ready'] and c['restartCount']==0 for c in (p['containers'] or [])) and bool(p['containers']) for p in others)
   row['nodes_healthy']=all(not n['unschedulable'] and all(c['status']==('True' if c['type']=='Ready' else 'False') for c in n['conditions'] if c['type'] in ('Ready','MemoryPressure','DiskPressure','PIDPressure','NetworkUnavailable')) for n in nodes)
  except Exception as e:row['error']=type(e).__name__+':'+str(e)
  print(json.dumps(row),flush=True);tick+=1;time.sleep(max(0,2-(time.monotonic()-at)))
