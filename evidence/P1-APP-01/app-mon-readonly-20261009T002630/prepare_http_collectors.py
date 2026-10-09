import json,pathlib
root=pathlib.Path(__file__).resolve().parent
d=json.loads((root/'private/app-mon-inventory-20261009T002630/stdout.json').read_bytes())
pods=next(q['items'] for q in d['queries'] if q['path']=='/api/v1/pods')
http=r'''
import datetime,hashlib,http.client,json,socket,time
targets=TARGETS
rows=[]
for host,port,path in targets:
 t=time.monotonic();row={'target':host,'port':port,'path':path,'method':'GET','started_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'proxy_used':False,'redirect_followed':False}
 c=http.client.HTTPConnection(host,port,timeout=4)
 try:
  c.request('GET',path,headers={'User-Agent':'fds-readonly-evidence/20261009','Connection':'close'})
  r=c.getresponse();body=r.read(262145)
  row.update(status=r.status,content_type=r.getheader('Content-Type'),body_bytes_read=len(body),truncated=len(body)>262144,body_sha256=hashlib.sha256(body).hexdigest(),help_lines=sum(line.startswith(b'# HELP ') for line in body.splitlines()),type_lines=sum(line.startswith(b'# TYPE ') for line in body.splitlines()))
 except Exception as e:row.update(error=type(e).__name__+': '+str(e))
 finally:c.close()
 row['elapsed_seconds']=round(time.monotonic()-t,6);rows.append(row)
print(json.dumps({'requests':rows}))
'''
header=r'''
import datetime,hashlib,json,os,pathlib,socket,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
if not ('2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'):raise SystemExit('STOP window')
if socket.gethostname()!=HOST or os.geteuid()!=0:raise SystemExit('STOP host/euid')
out={'schema':'fds.app-metrics.readonly.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[],'files':[],'containers':[],'no_config_change':True}
'''
edge=header.replace('HOST',repr('edge01'))
edge+= '\ncode='+repr(http.replace('TARGETS',repr([(ip,30080,path) for ip in ('10.1.93.105','10.1.93.107','10.1.93.108') for path in ('/metrics','/readyz')]+[('10.1.93.50',80,'/metrics'),('10.1.93.50',80,'/readyz')])) )
edge+="\np=subprocess.run(['python3','-I','-c',code],capture_output=True,timeout=60)\nout['queries'].append({'label':'edge-direct-and-nginx','command':['python3','-I','-c',code],'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})\nout['finished_at_kst']=now();print(json.dumps(out))\n"
(root/'edge-metrics-readonly.py').write_bytes(edge.encode())
for node,apps in [('k8s-worker01',('transaction-api','fds-engine')),('k8s-worker03',('prometheus',))]:
 entries=[]
 for app in apps:
  p=next(p for p in pods if p['spec']['nodeName']==node and p['metadata']['labels'].get('app')==app)
  c=next(c for c in p['status']['containerStatuses'] if c['name']==app)
  entries.append({'app':app,'pod':p['metadata']['name'],'uid':p['metadata']['uid'],'id':c['containerID'].split('://')[1],'imageID':c['imageID']})
 code=header.replace('HOST',repr(node))+'\nentries='+repr(entries)+'\nhttp_code='+repr(http)+'\n'
 code+=r'''
for e in entries:
 p=subprocess.run(['crictl','inspect',e['id']],capture_output=True,timeout=15)
 if p.returncode:raise SystemExit('STOP inspect failed')
 obj=json.loads(p.stdout);status=obj['status'];pid=int(obj['info']['pid'])
 if status['id']!=e['id'] or status['state']!='CONTAINER_RUNNING' or status['labels'].get('io.kubernetes.pod.uid')!=e['uid']:raise SystemExit('STOP container identity/state')
 e.update(pid=pid,netns=os.readlink('/proc/'+str(pid)+'/ns/net'));out['containers'].append(e)
 if e['app'] in ('transaction-api','fds-engine'):
  for path in ('/app/run.py','/app/app/main.py'):
   f=pathlib.Path('/proc')/str(pid)/'root'/path.lstrip('/')
   raw=f.read_bytes()
   if len(raw)>1000000:raise SystemExit('STOP unexpected source size')
   out['files'].append({'containerID':e['id'],'pod_uid':e['uid'],'app':e['app'],'path':path,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 targets=[]
 if e['app']=='transaction-api':targets=[('10.97.246.223',8001,'/metrics')]
 elif e['app']=='prometheus':targets=[('10.97.246.223',9090,'/metrics'),('10.106.27.47',9091,'/metrics')]
 if targets:
  cmd=['nsenter','-t',str(pid),'-n','--','python3','-I','-c',http_code.replace('TARGETS',repr(targets))]
  p=subprocess.run(cmd,capture_output=True,timeout=25)
  out['queries'].append({'label':e['app']+'-network-namespace','command':cmd,'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'source_pod_uid':e['uid'],'netns_before':e['netns'],'netns_after':os.readlink('/proc/'+str(pid)+'/ns/net'),'source_note':'Existing pod netns only; host Python, fixed Service IP, no pod DNS test, no pod file writes'})
 p=subprocess.run(['crictl','inspect',e['id']],capture_output=True,timeout=15)
 final=json.loads(p.stdout);e['post_pid']=final['info']['pid'];e['post_state']=final['status']['state']
 if int(e['post_pid'])!=pid or e['post_state']!='CONTAINER_RUNNING':raise SystemExit('STOP container changed')
out['finished_at_kst']=now();print(json.dumps(out))
'''
 (root/(node+'-metrics-readonly.py')).write_bytes(code.encode())
for p in (root/'edge-metrics-readonly.py',root/'k8s-worker01-metrics-readonly.py',root/'k8s-worker03-metrics-readonly.py'):compile(p.read_bytes(),str(p),'exec')
print('3 bounded collectors compiled; no application/config writes')
