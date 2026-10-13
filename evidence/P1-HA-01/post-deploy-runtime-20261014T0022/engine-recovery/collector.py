import os,pathlib,socket,json,time,datetime,subprocess
APP='fds-engine';MON_SOURCE=b"import subprocess,socket,time,json,urllib.request,urllib.parse,select\nkc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']\n# Fail if occupied; the bind in kubectl still arbitrates any intervening race.\ns=socket.socket();s.bind(('127.0.0.1',19095));s.close()\np=subprocess.Popen(kc+['-n','monitoring-api','port-forward','--address=127.0.0.1','svc/prometheus','19095:9090'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)\nrows=[];ready=False;first=b''\ntry:\n deadline=time.monotonic()+10\n while time.monotonic()<deadline and p.poll() is None:\n  if select.select([p.stdout],[],[],.2)[0]:\n   first=p.stdout.readline()\n   ready=first.startswith(b'Forwarding from 127.0.0.1:19095 -> 9090')\n   break\n if not ready:raise RuntimeError('PORT_FORWARD_NOT_READY')\n opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))\n for name,query in [('all_up','up')]:\n  url='http://127.0.0.1:19095/api/v1/query?query='+urllib.parse.quote(query,safe='')\n  try:\n   with opener.open(url,timeout=5) as res: data=res.read(65537)\n   if len(data)>65536:raise RuntimeError('OUTPUT_LIMIT')\n   rows.append({'name':name,'query':query,'raw':data.decode()})\n  except Exception as e:rows.append({'name':name,'error':type(e).__name__+':'+str(e)})\nfinally:\n if p.poll() is None:p.terminate()\n try:stdout,stderr=p.communicate(timeout=3)\n except subprocess.TimeoutExpired:p.kill();stdout,stderr=p.communicate(timeout=2)\n print(json.dumps({'queries':rows,'forwarder_pid':p.pid,'forwarder_stopped':p.poll() is not None,'forward_stdout':(first+stdout).decode(),'forward_stderr':stderr.decode(),'scope':'baseline API read only; not IF06B network-path evidence'}))\n"
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
P=pathlib.Path('/var/tmp/p1-ha-20261014-0015');os.umask(0o077)
ev=json.loads((P/(APP+'-eviction-result.json')).read_bytes());assert ev['request']['rc']==0
out={'app':APP,'started_epoch':time.time(),'readiness':[],'monitoring':[],'stability':[],'status':'OBSERVING','mutations':0}
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=8s']
images={'transaction-api':'10.1.93.54/fds/transaction-api@sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0','fds-engine':'10.1.93.54/fds/fds-engine@sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d'}
rs={'transaction-api':'7ff3c110-8cca-4b26-abad-fb67baa57baf','fds-engine':'ad644957-7157-4b4a-a342-244bc0ab8483'}
def snap():
 raw=subprocess.check_output(kc+['get','pods','-n','fds-app','-o','json'],timeout=10);items=json.loads(raw)['items'];rows=[]
 for x in items:
  app=x['metadata']['labels']['app'];assert x['metadata']['ownerReferences'][0]['uid']==rs[app]
  cs=x['status'].get('containerStatuses',[])
  assert all(c.get('imageID') in ('',None,images[app]) for c in cs)
  rows.append({'app':app,'name':x['metadata']['name'],'uid':x['metadata']['uid'],'node':x['spec'].get('nodeName'),'ip':x['status'].get('podIP'),'deleting':x['metadata'].get('deletionTimestamp'),'ready':bool(cs) and all(c['ready'] and c['restartCount']==0 and c['imageID']==images[app] for c in cs)})
 counts={a:{n:sum(r['app']==a and r['node']==n for r in rows) for n in ('k8s-worker01','k8s-worker02','k8s-worker03')} for a in images}
 expected=ev['pre_placement'].copy();expected[APP]={n:1 for n in ('k8s-worker01','k8s-worker02','k8s-worker03')}
 good=len(rows)==6 and all(r['ready'] and not r['deleting'] for r in rows) and counts==expected and ev['target']['deleteOptions']['preconditions']['uid'] not in {r['uid'] for r in rows}
 return {'epoch':time.time(),'ready':good,'pods':rows,'counts':counts}
def mon(pods):
 r=subprocess.run(['/usr/bin/python3','-B','-I','-'],input=MON_SOURCE,capture_output=True,timeout=20);assert r.returncode==0
 d=json.loads(r.stdout);assert d['forwarder_stopped']
 up=json.loads(d['queries'][0]['raw'])['data']['result']
 apps=[x for x in up if x['metric'].get('job') in images]
 good=len(up)==23 and all(x['value'][1]=='1' for x in up) and len(apps)==6 and {x['metric'].get('pod') for x in apps}=={p['name'] for p in pods}
 return {'epoch':time.time(),'healthy':good,'raw':d}
try:
 deadline=datetime.datetime.fromisoformat(ev['finished_at_utc']).timestamp()+120
 while time.time()<deadline:
  s=snap();out['readiness'].append(s)
  if s['ready']:break
  time.sleep(3)
 assert out['readiness'] and out['readiness'][-1]['ready'],'READY_TIMEOUT'
 out['ready_epoch']=time.time();deadline=out['ready_epoch']+90
 while time.time()<deadline:
  m=mon(s['pods']);out['monitoring'].append(m)
  if m['healthy']:break
  time.sleep(3)
 assert out['monitoring'][-1]['healthy'],'MON_TIMEOUT'
 out['mon_epoch']=time.time();until=time.monotonic()+30;uids={x['uid'] for x in s['pods']}
 while True:
  s=snap();m=mon(s['pods']);out['stability'].append({'state':s,'monitoring':m})
  assert s['ready'] and m['healthy'] and {x['uid'] for x in s['pods']}==uids,'STABILITY_FAILED'
  if time.monotonic()>=until:break
  time.sleep(5)
 out['status']='READY_MON_STABLE';out['final_counts']=s['counts']
except Exception as e:out['status']='STOP';out['error']=type(e).__name__+':'+str(e)
out['finished_epoch']=time.time()
with (P/(APP+'-recovery.json')).open('x') as f:json.dump(out,f)
print(json.dumps(out))
raise SystemExit(0 if out['status']=='READY_MON_STABLE' else 2)
