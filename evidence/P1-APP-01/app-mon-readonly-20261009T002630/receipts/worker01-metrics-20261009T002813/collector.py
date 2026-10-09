
import datetime,hashlib,json,os,pathlib,socket,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
if not ('2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'):raise SystemExit('STOP window')
if socket.gethostname()!='k8s-worker01' or os.geteuid()!=0:raise SystemExit('STOP host/euid')
out={'schema':'fds.app-metrics.readonly.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[],'files':[],'containers':[],'no_config_change':True}

entries=[{'app': 'transaction-api', 'pod': 'transaction-api-54984f6ddd-lrpp4', 'uid': '62536b32-28d4-413e-902f-7df0e4efc9bd', 'id': '69b05e1235edccea6e5cd8cca64c5bc13541d844698139c25d9d49c52d19671c', 'imageID': '10.1.93.54/fds/transaction-api@sha256:a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33'}, {'app': 'fds-engine', 'pod': 'fds-engine-66b8c565c4-vzgm6', 'uid': 'bf576dfc-f6a4-4ee4-90e6-1ab90fb5d370', 'id': '28fcdf7034971897f4da2514defaa49b824475005d08e7ad347f19dea596a952', 'imageID': '10.1.93.54/fds/fds-engine@sha256:5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369'}]
http_code="\nimport datetime,hashlib,http.client,json,socket,time\ntargets=TARGETS\nrows=[]\nfor host,port,path in targets:\n t=time.monotonic();row={'target':host,'port':port,'path':path,'method':'GET','started_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'proxy_used':False,'redirect_followed':False}\n c=http.client.HTTPConnection(host,port,timeout=4)\n try:\n  c.request('GET',path,headers={'User-Agent':'fds-readonly-evidence/20261009','Connection':'close'})\n  r=c.getresponse();body=r.read(262145)\n  row.update(status=r.status,content_type=r.getheader('Content-Type'),body_bytes_read=len(body),truncated=len(body)>262144,body_sha256=hashlib.sha256(body).hexdigest(),help_lines=sum(line.startswith(b'# HELP ') for line in body.splitlines()),type_lines=sum(line.startswith(b'# TYPE ') for line in body.splitlines()))\n except Exception as e:row.update(error=type(e).__name__+': '+str(e))\n finally:c.close()\n row['elapsed_seconds']=round(time.monotonic()-t,6);rows.append(row)\nprint(json.dumps({'requests':rows}))\n"

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
