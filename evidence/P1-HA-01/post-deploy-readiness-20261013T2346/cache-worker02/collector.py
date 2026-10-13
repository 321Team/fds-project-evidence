"""Fixed CRI image metadata read; no pulls, exports, cleanup or pod operations."""
import datetime,hashlib,json,os,socket,subprocess
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert socket.gethostname() in ('k8s-worker01','k8s-worker02','k8s-worker03') and os.geteuid()==0
argv=['/usr/bin/crictl','--runtime-endpoint','unix:///run/containerd/containerd.sock','--image-endpoint','unix:///run/containerd/containerd.sock','images','--output','json']
out={'started_at_utc':now(),'host':socket.gethostname(),'argv':argv,'mutation':False,'image_pull':False,'registry_authentication':False}
r=subprocess.run(argv,capture_output=True,timeout=15)
out.update(rc=r.returncode,stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest(),stderr_bytes=len(r.stderr))
assert r.returncode==0 and len(r.stdout)<8*1024*1024
images=json.loads(r.stdout)['images']
out['selected_images']=[{k:x.get(k) for k in ('id','repoTags','repoDigests','size','pinned')} for x in images if any(s.startswith(('10.1.93.54/fds/fds-engine','10.1.93.54/fds/transaction-api')) for s in (x.get('repoTags',[])+x.get('repoDigests',[])))]
out['finished_at_utc']=now()
out['limit']='CRI metadata presence only; layer bytes, registry re-pull and rollback execution are not verified.'
print(json.dumps(out,sort_keys=True))
