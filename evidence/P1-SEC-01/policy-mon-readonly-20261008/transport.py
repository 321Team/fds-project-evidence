import hashlib, pathlib, shlex, subprocess, sys
root=pathlib.Path(__file__).resolve().parent
stage=sys.argv[1]
source=root/({'mon-config':'collect-mon.py','mon-live':'collect-mon-live.py'}.get(stage,'collect.py'))
payload=source.read_bytes()
sha=hashlib.sha256(payload).hexdigest()
remote='sudo -n env COLLECTOR_SHA256='+sha+' python3 - '+shlex.quote(stage)
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.102',remote]
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
p=subprocess.run(cmd,input=payload,capture_output=True,timeout=230)
for suffix,data in [('json',p.stdout),('stderr',p.stderr),('rc',str(p.returncode).encode()+b'\n')]:
    (root/(stage+'.'+suffix)).write_bytes(data)
print('stage',stage,'rc',p.returncode,'bytes',len(p.stdout),'source_sha256',sha)
print(p.stderr.decode(errors='replace'))
