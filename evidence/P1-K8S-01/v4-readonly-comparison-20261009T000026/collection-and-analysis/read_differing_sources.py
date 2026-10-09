import base64,datetime,hashlib,json,pathlib,shlex,subprocess
R=pathlib.Path(__file__).resolve().parent
folder=sorted((R/'private').glob('k8s-readonly-*'))[-1]
comparison=json.loads((folder/'COMPARISON.json').read_text())
node=next(x for x in comparison['node_code_comparison'] if x['host']=='k8s-control03')
expected={r['path']:r['observed_sha256'] for r in node['files'] if r['status']=='DIFFERENT'}
code=r'''
import base64,datetime,hashlib,json,os,pathlib,socket,stat
expected=EXPECTED
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
assert '2026-10-09T00:00:00+09:00'<=now.isoformat()<'2026-10-09T09:00:00+09:00'
assert socket.gethostname()=='k8s-control03' and os.geteuid()==0
out={'host':socket.gethostname(),'started_at_kst':now.isoformat(),'files':[],'operational_write':False}
for path,digest in expected.items():
    p=pathlib.Path(path);assert p.resolve()==p and p.is_file()
    with p.open('rb') as f:
        a=os.fstat(f.fileno());assert a.st_size<200000
        b=f.read(200000);c=os.fstat(f.fileno())
    assert (a.st_mtime_ns,a.st_ino,a.st_size)==(c.st_mtime_ns,c.st_ino,c.st_size)
    assert hashlib.sha256(b).hexdigest()==digest
    out['files'].append({'path':path,'sha256':digest,'size':len(b),'content_base64':base64.b64encode(b).decode()})
out['finished_at_kst']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
print(json.dumps(out))
'''.replace('EXPECTED',repr(expected))
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
assert '2026-10-09T00:00:00+09:00'<=now.isoformat()<'2026-10-09T09:00:00+09:00'
out=folder/'differing-sources';out.mkdir(exist_ok=False)
(out/'collector.py').write_text(code,encoding='utf-8')
inner=['ssh','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','-o','ConnectTimeout=8','svc_ansible@10.1.93.104','sudo -n python3 -']
cmd=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','fds-ansible01',shlex.join(inner)]
p=subprocess.run(cmd,input=code.encode(),capture_output=True,timeout=60)
(out/'receipt.stdout.json').write_bytes(p.stdout);(out/'receipt.stderr').write_bytes(p.stderr)
(out/'invocation.json').write_text(json.dumps({'command':cmd,'started_at_kst':now.isoformat(),'collector_sha256':hashlib.sha256(code.encode()).hexdigest(),'rc':p.returncode},indent=2)+'\n',encoding='utf-8')
assert p.returncode==0,p.stderr.decode(errors='replace')
for row in json.loads(p.stdout)['files']:
    raw=base64.b64decode(row['content_base64']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
    (out/pathlib.PurePosixPath(row['path']).name).write_bytes(raw)
print('received_differing_source_files',len(expected))
