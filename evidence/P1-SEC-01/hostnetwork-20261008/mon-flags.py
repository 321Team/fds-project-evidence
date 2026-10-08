import datetime,hashlib,json,os,re,select,socket,subprocess,urllib.parse,urllib.request
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
r={'host':socket.gethostname(),'started_utc':now(),'source_sha256':os.environ['COLLECTOR_SHA256'],'scope':'read-only Prometheus GET; no rule change, alert injection or external message','queries':[]}
cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s','-n','monitoring-api','port-forward','--address=127.0.0.1','service/prometheus','0:9090']
r['forward_command']=cmd;p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
try:
 ready,_,_=select.select([p.stdout],[],[],15);assert ready,'FORWARD_NOT_READY'
 line=p.stdout.readline();m=re.search(r'Forwarding from 127\.0\.0\.1:(\d+)',line);assert m,line
 r['forward_first_line']=line;base='http://127.0.0.1:'+m.group(1)
 routes=[('/api/v1/status/flags','flags')]
 for route,kind in routes:
  q={'route':route,'started_utc':now()}
  try:
   with urllib.request.urlopen(base+route,timeout=15) as resp:raw=resp.read()
   data=json.loads(raw);q.update(rc=0,api_status=data.get('status'),raw_response_sha256=hashlib.sha256(raw).hexdigest())
   if kind=='flags':q['data']={k:data['data'][k] for k in ('web.enable-lifecycle','config.file','web.listen-address') if k in data['data']}
   elif kind=='runtime':q['data']={k:data['data'][k] for k in ('startTime','serverTime','reloadConfigSuccess','lastConfigTime','storageRetention') if k in data['data']}
   elif kind=='rules':q['data']=[{k:x.get(k) for k in ('name','query','duration','state','health','lastError')} for g in data['data']['groups'] for x in g['rules'] if x.get('name')=='FDSMonitoringPipelineTest']
   else:q['data']=data.get('data')
  except Exception as e:q.update(rc=2,error=str(e))
  q['finished_utc']=now();r['queries'].append(q)
except Exception as e:r['error']=str(e)
finally:
 p.terminate()
 try:tail=p.communicate(timeout=8)[0]
 except subprocess.TimeoutExpired:p.kill();tail=p.communicate(timeout=3)[0]
 r.update(forward_tail=tail,forward_exit=p.returncode,forward_reaped=p.poll() is not None,finished_utc=now())
print(json.dumps(r,indent=2));raise SystemExit(0 if 'error' not in r and all(q['rc']==0 and q.get('api_status')=='success' for q in r['queries']) else 2)
