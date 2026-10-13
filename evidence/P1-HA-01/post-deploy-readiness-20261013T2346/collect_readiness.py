"""Read-only next-step preparation; no staging, workload change, token or DB write."""
import concurrent.futures,importlib.util,pathlib,json
OUT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('transport',OUT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
source=(OUT.parent/'p1-independent-work-20261012/ha_read.remote.py').read_text(encoding='utf-8')
source=source.replace("('pv',KC+['get','pv','-o','json'])]", "('pv',KC+['get','pv','-o','json']),('hpa',KC+['get','hpa','-n','fds-app','-o','json']),('worker02pods',KC+['get','pods','-A','--field-selector=spec.nodeName=k8s-worker02','-o','json'])]")
source=source.replace("elif kind=='pods':", "elif kind in ('pods','worker02pods'):")
source=source.replace("out.update(identity_after=identity()", "p=subprocess.run(['/usr/bin/chronyc','tracking'],capture_output=True,timeout=5);out['chronyc']={'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}\nout.update(identity_after=identity()")
edge='''import datetime,json,os,platform,socket,subprocess,urllib.request,hashlib
assert socket.gethostname()=='edge01'
out={'host':socket.gethostname(),'uid':os.geteuid(),'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':platform.python_version(),'api_mutations':0,'db_writes':0,'http':[]}
p=subprocess.run(['/usr/bin/chronyc','tracking'],capture_output=True,timeout=5);out['chronyc']={'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}
for host,port,path in [(h,30080,p) for h in ('10.1.93.105','10.1.93.107','10.1.93.108') for p in ('/readyz','/metrics')]+[('127.0.0.1',80,'/readyz')]:
 u='http://%s:%s%s'%(host,port,path)
 row={'url':u,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(u,timeout=3) as r:body=r.read(10240);row.update(status=r.status,body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest())
 except urllib.error.HTTPError as e:body=e.read(10240);row.update(status=e.code,body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest())
 except Exception as e:row.update(status=None,error=type(e).__name__)
 out['http'].append(row)
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps(out))
'''
mon=(OUT.parent/'p1-redistribution-20261013/control01-mon-target-labels/collector.py').read_bytes()
tasks=[('current-cluster','10.1.93.102',source,True),('current-edge','10.1.93.50',edge,False),('current-mon','10.1.93.102',mon,True)]
def run(a):
 name,ip,code,root=a;compile(code,name,'exec');return t.run(name,ip,code,timeout=90,as_root=root)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,tasks))
