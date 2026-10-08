import datetime,hashlib,json,pathlib,shlex,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
source,node,name=sys.argv[1:]
assert node in ('102','105','107','108') and name.replace('-','').isalnum()
payload=(root/source).read_bytes(); sha=hashlib.sha256(payload).hexdigest()
remote='sudo -n env COLLECTOR_SHA256='+sha+' python3 -'
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.'+node,remote]
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
with (root/(name+'.json')).open('xb') as f:
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p=subprocess.run(cmd,input=payload,capture_output=True,timeout=180)
    f.write(p.stdout)
(root/(name+'.stderr')).write_bytes(p.stderr)
(root/(name+'-invocation.json')).write_text(json.dumps({'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'source':source,'source_sha256':sha,'rc':p.returncode},indent=2)+'\n',encoding='utf-8')
print(name,'rc',p.returncode,'bytes',len(p.stdout)); print(p.stderr.decode(errors='replace')[:2000])
raise SystemExit(p.returncode)
