"""Bounded SSH stdin collector runner; existing credentials only."""
import datetime,hashlib,json,pathlib,shlex,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
source=pathlib.Path(sys.argv[1]); addr=sys.argv[2]; label=sys.argv[3]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
if not ('2026-10-09T00:00:00+09:00'<=now.isoformat()<'2026-10-09T09:00:00+09:00'): raise SystemExit('STOP outside window')
out=ROOT/'private'/(label+'-'+now.strftime('%Y%m%dT%H%M%S'));out.mkdir(parents=True,exist_ok=False)
raw=source.read_bytes();compile(raw,str(source),'exec');(out/'collector.py').write_bytes(raw)
remote='python3 -' if sys.argv[4:]==['--unprivileged'] else 'sudo -n python3 -'
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@'+addr,remote]
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
p=subprocess.run(cmd,input=raw,capture_output=True,timeout=240)
(out/'stdout.json').write_bytes(p.stdout);(out/'stderr.txt').write_bytes(p.stderr)
meta={'started_at_kst':now.isoformat(),'finished_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'command':cmd,'rc':p.returncode,'collector_sha256':hashlib.sha256(raw).hexdigest(),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest()}
(out/'invocation.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
print(out, 'rc='+str(p.returncode))
if p.returncode: print(p.stderr.decode(errors='replace'));sys.exit(p.returncode)
data=json.loads(p.stdout)
print(json.dumps({'host':data.get('host'),'queries':[(x.get('path',x.get('label')),x.get('rc')) for x in data.get('queries',[])]}))
