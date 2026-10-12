import datetime,hashlib,json,os,pathlib,socket,subprocess,tomllib
assert socket.gethostname()=='k8s-worker01' and os.geteuid()==0
out={'host':socket.gethostname(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'daemon config selected snapshotter fields only; no config values or credentials exported','commands':[]}
def query(argv):
 p=subprocess.run(argv,capture_output=True,timeout=8);out['commands'].append({'argv':argv,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()});assert p.returncode==0;return p.stdout
try:
 pid=int(query(['/usr/bin/systemctl','show','containerd','--value','-p','MainPID']).strip());assert pid>1
 argv=pathlib.Path('/proc/'+str(pid)+'/cmdline').read_bytes().decode().strip('\x00').split('\x00')
 config='/etc/containerd/config.toml'
 for i,x in enumerate(argv):
  if x in ['--config','-c']:config=argv[i+1]
  elif x.startswith('--config='):config=x.split('=',1)[1]
 path=pathlib.Path(config);assert path.is_absolute() and path.is_file() and path.stat().st_size<1048576
 raw=path.read_bytes();cfg=tomllib.loads(raw.decode());plugins=cfg.get('plugins',{})
 image=plugins.get('io.containerd.cri.v1.images',{})
 runtime=plugins.get('io.containerd.cri.v1.runtime',{}).get('containerd',{})
 out['config']={'path':config,'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'version':cfg.get('version'),'imports':cfg.get('imports',[]),'image_snapshotter':image.get('snapshotter'),'default_runtime_name':runtime.get('default_runtime_name'),'runtime_snapshotters':{k:v.get('snapshotter') for k,v in runtime.get('runtimes',{}).items()}}
 ctr=['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io']
 text=query(ctr+['plugins','list']).decode();out['plugins_selected_lines']='\n'.join(l for l in text.splitlines() if 'snapshotter' in l or 'io.containerd.cri.' in l)
 rows=query(ctr+['containers','list']).decode().splitlines()[1:];assert rows
 first=rows[0].split()[0];obj=json.loads(query(ctr+['containers','info',first]))
 out['sample_container']={'id':obj.get('ID',obj.get('id')),'snapshotter':obj.get('Snapshotter',obj.get('snapshotter')),'image':obj.get('Image',obj.get('image'))}
 out['status']='COLLECTED_REVIEW_REQUIRED'
except Exception as e:out.update(status='INCOMPLETE',error=type(e).__name__+':'+str(e))
print(json.dumps(out));raise SystemExit(0 if out['status']=='COLLECTED_REVIEW_REQUIRED' else 2)
