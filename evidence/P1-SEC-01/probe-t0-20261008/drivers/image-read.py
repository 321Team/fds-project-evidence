import datetime, hashlib, json, os, pathlib, socket, subprocess
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='k8s-worker01'
def run(args):
 p=subprocess.run(args,capture_output=True,timeout=12); assert p.returncode==0,p.stderr.decode(); return p.stdout
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'containers':[]}
for line in run(['ctr','-n','k8s.io','tasks','list']).decode().splitlines()[1:]:
 fields=line.split()
 if len(fields)<3 or fields[2]!='RUNNING':continue
 cid,pid=fields[:2];raw=run(['ctr','-n','k8s.io','containers','info',cid]);d=json.loads(raw);labels=d.get('Labels',{})
 if labels.get('io.kubernetes.pod.namespace')!='fds-app' or labels.get('io.kubernetes.container.name')!='transaction-api':continue
 proc=pathlib.Path('/proc')/pid;start=(proc/'stat').read_text().rsplit(')',1)[1].split()[19]
 spec=d.get('Spec',{});entry={'container_id':cid,'pid':int(pid),'pod':labels.get('io.kubernetes.pod.name'),'pod_uid':labels.get('io.kubernetes.pod.uid'),'image':d.get('Image'),'process_args':spec.get('process',{}).get('args'),'running_exe':os.readlink(proc/'exe'),'info_sha256':hashlib.sha256(raw).hexdigest(),'candidates':{}}
 for name in ['/venv/bin/python3','/usr/bin/python3','/usr/bin/python3.13','/usr/local/bin/python3','/usr/local/bin/python3.13']:
  f=proc/'root'/name.lstrip('/');entry['candidates'][name]={'lexists':os.path.lexists(f),'symlink_target':os.readlink(f) if f.is_symlink() else None}
 assert (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==start
 r['containers'].append(entry)
assert len(r['containers'])==1,r
print(json.dumps(r,indent=2))
