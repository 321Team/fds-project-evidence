from pathlib import Path
import os, subprocess, json, hashlib, datetime, tempfile, tarfile
os.umask(0o077)
E=Path(tempfile.mkdtemp(prefix='fds-u1-scope-'))
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
records=[]
def call(name,args):
    argv=['aws',*args,'--region','ap-northeast-2','--output','json','--no-cli-pager','--cli-connect-timeout','10','--cli-read-timeout','20']
    start=now()
    r=subprocess.run(argv,capture_output=True,timeout=45)
    (E/(name+'.stdout')).write_bytes(r.stdout); (E/(name+'.stderr')).write_bytes(r.stderr)
    records.append(dict(name=name,argv=argv,started_utc=start,finished_utc=now(),rc=r.returncode))
    print(name,'RC',r.returncode,flush=True)
    return json.loads(r.stdout) if r.returncode==0 else None
summary={'started_utc':now(),'mode':'READ_ONLY_AND_SIMULATION','writes':'NOT_RUN','resource_policy_simulation':'NOT_SUPPORTED_FOR_ROLE'}
try:
    ident=call('caller',['sts','get-caller-identity'])
    assert ident['Arn']=='arn:aws:iam::774055931866:user/321team-gwonuk'
    role=call('role',['iam','get-role','--role-name','FDS-IaC-Operator'])
    assert role['Role']['RoleId']=='AROA3IOKUF7NEM6P7ZKPK'
    attached=call('attached',['iam','list-attached-role-policies','--role-name','FDS-IaC-Operator'])
    call('inline',['iam','list-role-policies','--role-name','FDS-IaC-Operator'])
    for p in attached['AttachedPolicies']:
        meta=call(p['PolicyName']+'-meta',['iam','get-policy','--policy-arn',p['PolicyArn']])
        if meta: call(p['PolicyName']+'-version',['iam','get-policy-version','--policy-arn',p['PolicyArn'],'--version-id',meta['Policy']['DefaultVersionId']])
    bucket='fds-tfstate-774055931866-ap-northeast-2'
    bp=call('bucket-policy',['s3api','get-bucket-policy','--bucket',bucket,'--expected-bucket-owner','774055931866'])
    if bp:
        doc=json.loads(bp['Policy']); summary['bucket_policy_statements']=doc['Statement']
    call('bucket-ownership',['s3api','get-bucket-ownership-controls','--bucket',bucket,'--expected-bucket-owner','774055931866'])
    call('bucket-public-access',['s3api','get-public-access-block','--bucket',bucket,'--expected-bucket-owner','774055931866'])
    context=[{'ContextKeyName':'aws:RequestedRegion','ContextKeyValues':['ap-northeast-2'],'ContextKeyType':'string'}, {'ContextKeyName':'aws:SecureTransport','ContextKeyValues':['true'],'ContextKeyType':'boolean'}, {'ContextKeyName':'aws:PrincipalArn','ContextKeyValues':['arn:aws:iam::774055931866:role/FDS-IaC-Operator'],'ContextKeyType':'string'}]
    sim=call('simulate-state-scope',['iam','simulate-principal-policy','--policy-source-arn','arn:aws:iam::774055931866:role/FDS-IaC-Operator','--action-names','s3:GetObject','s3:PutObject','--resource-arns','arn:aws:s3:::'+bucket+'/phase2/network/terraform.tfstate','arn:aws:s3:::'+bucket+'/phase2/u1-other/terraform.tfstate','--context-entries',json.dumps(context)])
    if sim:
        summary['simulation']=[{k:x.get(k) for k in ['EvalActionName','EvalResourceName','EvalDecision','MissingContextValues','PermissionsBoundaryDecisionDetail','OrganizationsDecisionDetail']} for x in sim['EvaluationResults']]
    summary['status']='READBACK_FINISHED'
except Exception as e:
    summary['status']='STOPPED'; summary['error']=str(e)
finally:
    summary['finished_utc']=now()
    (E/'runner.py').write_bytes(Path(__file__).read_bytes())
    (E/'execution-records.json').write_text(json.dumps(records,indent=2)+'\n')
    (E/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    files=sorted(E.iterdir())
    (E/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
    archive=E.with_suffix('.tar.gz')
    with tarfile.open(archive,'w:gz') as t: t.add(E,arcname='u1-scope')
    print('RESULT',json.dumps(summary),flush=True)
    print('ARCHIVE',archive,'BYTES',archive.stat().st_size,'SHA256',hashlib.sha256(archive.read_bytes()).hexdigest(),flush=True)
    print('U1_SCOPE_READBACK_DONE',flush=True)
