import datetime,hashlib,json,pathlib,shlex,subprocess
r=pathlib.Path(__file__).resolve().parent;out=r/'private/runner-trivy-hash-20261009';out.mkdir(parents=True,exist_ok=False)
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
started=now();assert started<'2026-10-09T09:00:00+09:00'
raw=(r/'runner-trivy-hash-readonly.py').read_bytes();compile(raw,'collector','exec');(out/'collector.py').write_bytes(raw)
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','server01_cicd-runner@10.250.10.20','/usr/bin/python3 -B -']
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
p=subprocess.run(cmd,input=raw,capture_output=True,timeout=60)
(out/'stdout.json').write_bytes(p.stdout);(out/'stderr.txt').write_bytes(p.stderr)
meta={'started_at_kst':started,'finished_at_kst':now(),'command':cmd,'rc':p.returncode,'collector_sha256':hashlib.sha256(raw).hexdigest(),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest()}
(out/'invocation.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print(json.dumps(meta,indent=2))
if p.returncode:print(p.stderr.decode(errors='replace'));raise SystemExit(p.returncode)
print(p.stdout.decode())
