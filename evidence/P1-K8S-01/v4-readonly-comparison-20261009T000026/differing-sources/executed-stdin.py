
import base64,datetime,hashlib,json,os,pathlib,socket,stat
expected={'/opt/fds/P1-K8S-01-v4/code/audit-window.py': '75ea9962b84c064ad04a301a8086ecc7ab21c201ec86749a888715cf45a8a80b', '/opt/fds/P1-K8S-01-v4/code/cluster-change.py': '07696cee257fde462f193d95f17c26415b10628e4aa2b58f6f3920a46cc18ff6', '/opt/fds/P1-K8S-01-v4/code/node-evidence.py': '318ac4b28c398de46dad6a7049400d75ac211f06fe5a2cfc88c4e64300039023', '/opt/fds/P1-K8S-01-v4/code/render.py': 'fe0a99f364f7eaca6f726a4d280c8ff38c7a06652db809edaf3e8499adb5b71b'}
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
