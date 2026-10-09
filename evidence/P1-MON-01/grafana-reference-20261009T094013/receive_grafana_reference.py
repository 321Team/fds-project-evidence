import datetime,hashlib,json,pathlib,shlex,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(x):return hashlib.sha256(x).hexdigest()
assert '2026-10-09T09:10:00+09:00'<=now()<'2026-10-09T12:00:00+09:00'
raw=(ROOT/'grafana-reference-readonly.py').read_bytes();compile(raw,'collector.py','exec')
out=ROOT/'private'/('grafana-reference-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S'));out.mkdir(parents=True)
(out/'collector.py').write_bytes(raw)
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.102','sudo -n /usr/bin/python3 -B -']
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
start=now()
try:p=subprocess.run(cmd,input=raw,capture_output=True,timeout=60);rc=p.returncode;stdout=p.stdout;stderr=p.stderr
except subprocess.TimeoutExpired as e:rc=124;stdout=e.stdout or b'';stderr=e.stderr or b''
(out/'stdout.json').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
(out/'invocation.json').write_text(json.dumps(dict(command=cmd,started_at_kst=start,finished_at_kst=now(),rc=rc,collector_sha256=sha(raw),stdout_sha256=sha(stdout)),indent=2)+'\n',encoding='utf-8')
print('RECEIPT='+str(out),'RC='+str(rc),'STDERR_BYTES='+str(len(stderr)))
assert rc==0 and not stderr
data=json.loads(stdout);assert data['status']=='COLLECTED'
print(json.dumps(data,ensure_ascii=False,indent=2))
