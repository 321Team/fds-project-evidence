"""Read-only 60-second all-target recovery observation; transient localhost PF."""
import datetime,json,os,select,socket,subprocess,time,urllib.request,urllib.parse
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s']
s=socket.socket();s.bind(('127.0.0.1',19095));s.close()
p=subprocess.Popen(kc+['-n','monitoring-api','port-forward','--address=127.0.0.1','svc/prometheus','19095:9090'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
rows=[];first=b'';stable=None;ok=False;started=datetime.datetime.now(datetime.timezone.utc).isoformat()
expected={('fds-engine',ip+':9090') for ip in ('10.244.79.122','10.244.39.217','10.244.69.193')}|{('transaction-api',ip+':9091') for ip in ('10.244.79.121','10.244.39.218','10.244.69.195')}
try:
 assert select.select([p.stdout],[],[],10)[0]
 first=p.stdout.readline();assert first.startswith(b'Forwarding from 127.0.0.1:19095 -> 9090')
 op=urllib.request.build_opener(urllib.request.ProxyHandler({}));end=time.monotonic()+180
 while time.monotonic()<end:
  tick=time.monotonic();row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with op.open('http://127.0.0.1:19095/api/v1/query?query=up',timeout=4) as res:raw=res.read(65537)
   assert len(raw)<=65536;x=json.loads(raw);assert x['status']=='success'
   result=x['data']['result'];apps={(r['metric']['job'],r['metric']['instance']) for r in result if r['metric']['job'] in ('fds-engine','transaction-api')}
   good=len(result)==23 and all(r['value'][1]=='1' for r in result) and apps==expected
   row.update(raw=raw.decode(),all23_app6=good)
  except Exception as e:good=False;row['error']=type(e).__name__+':'+str(e)
  if not good:stable=None
  elif stable is None:stable=tick
  row['stable_seconds']=0 if stable is None else tick-stable;rows.append(row)
  if good and row['stable_seconds']>=60:ok=True;break
  time.sleep(max(0,2-(time.monotonic()-tick)))
finally:
 if p.poll() is None:p.terminate()
 try:stdout,stderr=p.communicate(timeout=3)
 except subprocess.TimeoutExpired:p.kill();stdout,stderr=p.communicate(timeout=2)
 print(json.dumps({'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stable60_pass':ok,'rows':rows,'forwarder_stopped':p.poll() is not None,'forward_stdout':(first+stdout).decode(),'forward_stderr':stderr.decode(),'scope':'READ_ONLY_RECOVERY','review':'NOT PERFORMED (pure validator)'}))
raise SystemExit(0 if ok else 2)
