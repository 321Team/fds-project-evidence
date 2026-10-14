import pathlib,hashlib,base64,json,datetime,socket,os,subprocess
assert socket.gethostname()=='k8s-worker02' and os.geteuid()==0
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'files':[]}
for path in ['/var/tmp/p1-http-probe-20261014-0945/input.json','/var/tmp/p1-http-probe-20261014-0945/events.jsonl','/var/tmp/p1-http-probe-source-20261014-0945/engine_stop.py','/var/tmp/p1-http-probe-source-20261014-0945/observed-binding.json']:
 p=pathlib.Path(path);raw=p.read_bytes();assert len(raw)<20000
 out['files'].append({'path':path,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode(),'mode':oct(p.stat().st_mode&0o777),'uid':p.stat().st_uid})
cmd=['/usr/bin/crictl','--runtime-endpoint','unix:///run/containerd/containerd.sock','inspect','737b90c6597c5ed6ae4a74b2d68e066cb928efcca8f5ed564b1b11fa51dc8e31']
p=subprocess.run(cmd,capture_output=True,timeout=8);assert p.returncode==0;x=json.loads(p.stdout);out['new_container']={'status':{k:x['status'].get(k) for k in ['id','state','labels','imageRef','createdAt','startedAt']},'pid':x['info']['pid']}
print(json.dumps(out))
