MODE='runtime'

import base64,datetime as dt,hashlib,json,os,pathlib,socket,stat,subprocess
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
home=pathlib.Path('/home/server01_cicd-runner')
names=['FDS_D03_Supply_202610150030','FDS_D03_SupplyValidation_202610150030'] if MODE=='supply' else ['FDS_D03_202610150030','FDS_D03_RuntimeInvocation_202610150030']
out={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':MODE,'read_only':True,'files':[]};total=0
def get(root,rel,expected=None):
    global total
    q=pathlib.PurePosixPath(rel)
    assert not q.is_absolute() and '..' not in q.parts and q.name not in ('db.env','api.env'),'FORBIDDEN_EVIDENCE_PATH'
    p=root.joinpath(*q.parts);s=p.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid==1000 and p.resolve().is_relative_to(root) and s.st_size<10*1024*1024
    for parent in p.parents:
        assert not parent.is_symlink()
        if parent==root:break
    raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert expected is None or expected==digest
    total+=len(raw);assert total<50*1024*1024
    out['files'].append({'path':root.name+'/'+rel,'sha256':digest,'base64':base64.b64encode(raw).decode()})
for name in names:
    root=home/name;assert root.exists() and not root.is_symlink()
    listed=set()
    for line in (root/'SHA256SUMS').read_text().splitlines():
        digest,rel=line.split('  ',1);assert rel not in listed;listed.add(rel);get(root,rel,digest)
    get(root,'SHA256SUMS')
decisions=home/'FDS_D03_Decisions_202610150030'
for name in ('plan.json','authorization.json'):get(decisions,name)
if MODE=='runtime':
    get(home/'FDS_D03_Claims','202610150030.json')
    runtime=home/'FDS_D03_202610150030'
    out['credential_files_absent']=all(not (runtime/name).exists() for name in ('db.env','api.env'))
    out['containers']=json.loads(subprocess.check_output(['podman','ps','-a','--format','json'],timeout=10))
    out['runner_worker_pids']=[]
    for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
        try:
            if p.read_text().strip()=='Runner.Worker':out['runner_worker_pids'].append(int(p.parent.name))
        except (FileNotFoundError,ProcessLookupError):pass
out['total_bytes']=total
print(json.dumps(out))
