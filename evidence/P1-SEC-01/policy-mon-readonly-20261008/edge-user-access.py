import datetime,json,pathlib,shlex,subprocess
r=pathlib.Path(__file__).resolve().parent
remote="python3 -c "+shlex.quote("import json,os,socket,shutil; print(json.dumps({'hostname':socket.gethostname(),'uid':os.geteuid(),'curl':shutil.which('curl')}))")
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=6','svc_ansible@10.1.93.50',remote]
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01',shlex.join(inner)]
q={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd}
p=subprocess.run(cmd,capture_output=True,timeout=20)
q.update(rc=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(r/'edge-user-access.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(q,ensure_ascii=False))
