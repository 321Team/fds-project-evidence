import concurrent.futures,importlib.util,pathlib
OUT=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('transport',OUT.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT
capacity='''import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':[],'mutation':False}
for name,args in [('capacity',['describe','node','k8s-worker01','k8s-worker03']),('drain-help',['drain','--help']),('rs',['get','rs','-n','fds-app','-o','json'])]:
 p=subprocess.run(kc+args,capture_output=True,timeout=15)
 item={'name':name,'argv':kc+args,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode()}
 if name=='rs' and p.returncode==0:
  item['items']=[{'metadata':{k:r['metadata'].get(k) for k in ('name','uid','resourceVersion','ownerReferences')},'replicas':r['spec'].get('replicas'),'selector':r['spec'].get('selector')} for r in json.loads(p.stdout)['items'] if r['spec'].get('replicas',0)>0]
 else:item['stdout']=p.stdout.decode()
 out['queries'].append(item)
print(json.dumps(out))
'''
identity='''import datetime,json,os,pathlib,socket,shutil
assert socket.gethostname()=='edge01'
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.geteuid(),'gid':os.getegid(),'home':str(pathlib.Path.home()),'home_writable':os.access(pathlib.Path.home(),os.W_OK),'python3':shutil.which('python3'),'pwd':os.getcwd(),'writes':0}))
'''
cache=(OUT.parent/'phase1-deploy-preparation-20261013/rollback_cache_read.py').read_bytes()
tasks=[('current-capacity','10.1.93.102',capacity,True),('edge-identity','10.1.93.50',identity,False)]+[('cache-'+name,'10.1.93.'+ip,cache,True) for name,ip in [('worker01','105'),('worker02','107'),('worker03','108')]]
def run(a):name,ip,code,root=a;compile(code,name,'exec');return t.run(name,ip,code,timeout=60,as_root=root)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:list(p.map(run,tasks))
