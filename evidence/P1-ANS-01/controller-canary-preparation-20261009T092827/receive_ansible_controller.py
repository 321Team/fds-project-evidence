import datetime,hashlib,json,pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parent
now=lambda:datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
if not '2026-10-09T09:10:00+09:00'<=now()<'2026-10-09T12:00:00+09:00':raise SystemExit('STOP window')
raw=(r/'ansible-controller-readonly.py').read_bytes();compile(raw,'collector.py','exec')
d=r/'private'/('ansible-controller-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S'));d.mkdir(parents=True)
(d/'collector.py').write_bytes(raw)
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01','/usr/bin/python3 -B -']
start=now()
try:p=subprocess.run(cmd,input=raw,capture_output=True,timeout=55);rc=p.returncode;stdout=p.stdout;stderr=p.stderr
except subprocess.TimeoutExpired as exc:rc=124;stdout=exc.stdout or b'';stderr=exc.stderr or b''
(d/'stdout.json').write_bytes(stdout);(d/'stderr.txt').write_bytes(stderr)
(d/'invocation.json').write_text(json.dumps(dict(command=cmd,started_at_kst=start,finished_at_kst=now(),rc=rc,
 collector_sha256=hashlib.sha256(raw).hexdigest(),stdout_sha256=hashlib.sha256(stdout).hexdigest()),indent=2)+'\n',encoding='utf-8')
print('receipt='+str(d),'rc='+str(rc),'stderr_bytes='+str(len(stderr)))
if not rc:
 data=json.loads(stdout);print('status='+data['status'])
 for entry in data['checkouts']: print(entry['path'],entry['queries'][0]['stdout'].strip(),'matched_inputs='+str(sum(x.get('matches_checkout_commit',False) for x in entry['inputs'])))
sys.exit(rc)
