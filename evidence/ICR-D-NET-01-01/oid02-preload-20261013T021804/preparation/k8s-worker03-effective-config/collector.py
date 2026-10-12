import datetime,hashlib,json,os,pathlib,socket,subprocess,tomllib
assert socket.gethostname()=='k8s-worker03' and os.geteuid()==0
out={'host':socket.gethostname(),'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'existing daemon executable config dump, imports resolved; only snapshotter fields output; no restart or config write','commands':[]}
try:
 p=subprocess.run(['/usr/bin/systemctl','show','containerd','--value','-p','MainPID'],capture_output=True,timeout=5);assert p.returncode==0
 pid=int(p.stdout.strip());assert pid>1
 exe=os.readlink('/proc/'+str(pid)+'/exe');assert exe=='/usr/bin/containerd'
 cfgpath='/etc/containerd/config.toml';cfg=pathlib.Path(cfgpath);assert hashlib.sha256(cfg.read_bytes()).hexdigest()=='4220b27d8c9302397969a0afad7caaa4ea35bef69dcd6a54a293563835c037b5'
 argv=[exe,'--config',cfgpath,'config','dump']
 p=subprocess.run(argv,capture_output=True,timeout=8);out['commands'].append({'argv':argv,'rc':p.returncode,'stdout_size':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_size':len(p.stderr),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()})
 assert p.returncode==0 and len(p.stdout)<1048576 and len(p.stderr)<65536
 data=tomllib.loads(p.stdout.decode());pl=data.get('plugins',{});im=pl.get('io.containerd.cri.v1.images',{});rt=pl.get('io.containerd.cri.v1.runtime',{}).get('containerd',{})
 out['effective_snapshotter']=im.get('snapshotter');out['runtime_snapshotters']={k:v.get('snapshotter') for k,v in rt.get('runtimes',{}).items()};out['binary_sha256']=hashlib.sha256(pathlib.Path(exe).read_bytes()).hexdigest();out['status']='COLLECTED_REVIEW_REQUIRED'
except Exception as e:out.update(status='INCOMPLETE',error=type(e).__name__+':'+str(e))
print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
