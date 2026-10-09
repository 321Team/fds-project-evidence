"""Receive fixed bytes/metadata on PC; no writes on source servers."""
import base64,datetime,hashlib,json,pathlib,shlex,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
NODES={'k8s-control01':'10.1.93.102','k8s-control03':'10.1.93.104','k8s-worker01':'10.1.93.105','k8s-worker02':'10.1.93.107','k8s-worker03':'10.1.93.108'}
def now(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(raw): return hashlib.sha256(raw).hexdigest()
def gate():
    if not '2026-10-09T09:10:00+09:00'<=now()<'2026-10-09T12:00:00+09:00': raise SystemExit('STOP outside window')
gate()
plan_path=ROOT/'k8s-tool-reconciliation/ops/p1-k8s-01-v4/reconciliation/manifest-20261009.json'
plan_raw=plan_path.read_bytes();plan=json.loads(plan_raw)
template=(ROOT/'k8s-backup-readonly-template.py').read_text(encoding='utf-8')
out=ROOT/'private'/('k8s-backup-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S'))
out.mkdir(parents=True,exist_ok=False)
(out/'plan.json').write_bytes(plan_raw)
for host,addr in NODES.items():
    gate();folder=out/host;folder.mkdir()
    changes={r['path']:r for r in plan['changes'] if r['host']==host}
    spec={'host':host,'files':[{'path':r['deployed_path'],'export':r['deployed_path'] in changes,
           'expected_sha256':changes[r['deployed_path']]['observed_sha256'] if r['deployed_path'] in changes else r['sha256']}
           for r in plan['reference_files']]}
    raw=template.replace('__SPEC__',repr(spec)).encode()
    compile(raw,'collector.py','exec');(folder/'collector.py').write_bytes(raw)
    inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','svc_ansible@'+addr,'sudo -n /usr/bin/python3 -B -']
    cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
    start=now()
    try: p=subprocess.run(cmd,input=raw,capture_output=True,timeout=50);rc=p.returncode;stdout=p.stdout;stderr=p.stderr
    except subprocess.TimeoutExpired as exc: rc=124;stdout=exc.stdout or b'';stderr=exc.stderr or b''
    (folder/'stdout.json').write_bytes(stdout);(folder/'stderr.txt').write_bytes(stderr)
    receipt=dict(command=cmd,started_at_kst=start,finished_at_kst=now(),rc=rc,collector_sha256=sha(raw),stdout_sha256=sha(stdout),plan_sha256=sha(plan_raw))
    (folder/'invocation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if rc or stderr: print('STOP',host,rc,'receipt='+str(folder));sys.exit(2)
    data=json.loads(stdout)
    assert data['status']=='COLLECTED' and data['host']==host and len(data['files'])==9
    backup=folder/'bytes';backup.mkdir()
    for row in data['files']:
        for attr in row['xattrs'].values():
            value=base64.b64decode(attr['content_base64'],validate=True)
            assert len(value)==attr['size'] and sha(value)==attr['sha256']
        if row['exported']:
            value=base64.b64decode(row['content_base64'],validate=True)
            assert len(value)==row['metadata']['size'] and sha(value)==row['sha256']==changes[row['path']]['observed_sha256']
            compile(value,row['path'],'exec')
            (backup/pathlib.PurePosixPath(row['path']).name).write_bytes(value)
    assert len(list(backup.iterdir()))==len(changes)
    print(host,'files=9','exported='+str(len(changes)),'receipt='+str(folder),flush=True)
print('RECEIPT_ROOT='+str(out))
