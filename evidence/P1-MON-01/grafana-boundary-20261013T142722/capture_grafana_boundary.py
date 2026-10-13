import datetime, hashlib, json, pathlib, subprocess
out=pathlib.Path(__file__).parent
source=(out/'collect_grafana_boundary.py').read_bytes()
sha=hashlib.sha256(source).hexdigest()
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',f"ssh -i /home/server01_ansible/.ssh/p1_ansible_ed25519 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 svc_ansible@10.1.93.102 'sudo -n env COLLECTOR_SHA256={sha} python3 -'"]
receipt={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':sha,'command':cmd,'classification':'PURE_READ_PRECHECK','review':'NOT PERFORMED (Pre-check)'}
p=subprocess.run(cmd,input=source,capture_output=True,timeout=100)
(out/'grafana-boundary.json').write_bytes(p.stdout)
(out/'grafana-boundary.stderr').write_bytes(p.stderr)
receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rc=p.returncode,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
(out/'grafana-capture-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
if p.returncode==0: print(p.stdout.decode('utf-8'))
else: print('Read failed; raw output preserved locally.')
