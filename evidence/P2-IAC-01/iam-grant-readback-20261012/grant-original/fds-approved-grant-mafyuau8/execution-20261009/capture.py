from pathlib import Path
import json,hashlib,subprocess,datetime,os,re,zipfile
os.umask(0o077)
BASE=Path('/home/cloudshell-user/fds-approved-grant-mafyuau8')
OUT=BASE/'execution-20261009'
G=json.loads((BASE/'iam/grant-plan-20261009/grant-plan.json').read_text())
assert hashlib.sha256(Path('/home/cloudshell-user/iam-approved-grant-5fb64bd.zip').read_bytes()).hexdigest()=='403d2ad1c9a6391c9d3e1211962604f769041116b4481427adcd57223c6d2dee'
with zipfile.ZipFile('/home/cloudshell-user/iam-approved-grant-5fb64bd.zip') as z:
    assert all((BASE/n).read_bytes()==z.read(n) for n in z.namelist())
assert not any(k.startswith('AWS_ENDPOINT_URL') or k in ('AWS_CA_BUNDLE','AWS_DATA_PATH') for k in os.environ)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,data): (OUT/name).write_text(json.dumps(data,indent=2))
def call(name,*args):
    assert re.fullmatch('[a-zA-Z0-9_-]+',name)
    (OUT/(name+'.pending')).open('x').close()
    cmd=['aws',*args,'--region','ap-northeast-2','--output','json','--no-cli-pager','--cli-connect-timeout','10','--cli-read-timeout','30']
    meta={'argv':cmd,'started_utc':now(),'exit_code':None,'timeout':False}
    if '--cli-input-json' in args:
        f=Path(args[args.index('--cli-input-json')+1].removeprefix('file://')); meta['input_sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
    save(name+'.receipt.json',meta)
    try:
        r=subprocess.run(cmd,capture_output=True,timeout=50)
        stdout,stderr=r.stdout,r.stderr; meta['exit_code']=r.returncode
    except subprocess.TimeoutExpired as e:
        stdout,stderr=e.stdout or b'',e.stderr or b''; meta['timeout']=True
    finally:
        meta['finished_utc']=now()
    (OUT/(name+'.stdout')).write_bytes(stdout); (OUT/(name+'.stderr')).write_bytes(stderr)
    meta.update(stdout_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest())
    save(name+'.receipt.json',meta)
    if meta['exit_code']!=0: raise RuntimeError(name+' FAILED or UNKNOWN; STOP, inspect raw receipt before retry')
    print(name,'RC0',flush=True)
    return json.loads(stdout) if stdout.strip() else {}
def mutate(i):
    assert 1<=i<=10
    o=G['ordered_operations'][i-1]; op=o['operation']; f=BASE/'requests'/f'{i:02d}-{op}.json'; d=json.loads(f.read_text())
    tags=[{'Key':k,'Value':v} for k,v in G['tags'].items()]
    if op=='CreatePolicy': expected={'PolicyName':o['policy_name'],'Path':o['path'],'PolicyDocument':(BASE/o['policy_file']).read_text(),'Tags':tags}
    elif op=='CreateRole': expected={'RoleName':o['role_name'],'Path':o['path'],'AssumeRolePolicyDocument':(BASE/o['trust_file']).read_text(),'MaxSessionDuration':3600,'Tags':tags}
    elif op=='AttachRolePolicy': expected={'RoleName':o['role_name'],'PolicyArn':o['policy_arn']}
    else:
        assert json.loads((OUT/'activation-gate.json').read_text())['status']=='PASS_CLOSED_READBACK'
        expected={'RoleName':o['role_name'],'PolicyDocument':(BASE/o['trust_file']).read_text()}
    assert d==expected
    api={'CreatePolicy':'create-policy','CreateRole':'create-role','AttachRolePolicy':'attach-role-policy','UpdateAssumeRolePolicy':'update-assume-role-policy'}[op]
    return call(f'mutate-{i:02d}','iam',api,'--cli-input-json','file://'+str(f))
