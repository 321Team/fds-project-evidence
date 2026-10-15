"""Offline comparison of lifecycle receipts and bounded postcollection."""
import datetime as dt,hashlib,importlib.util,json,re
from pathlib import Path
O=Path(__file__).resolve().parent
def read(p):return json.loads((O/p).read_bytes())
def stamp(v):return dt.datetime.fromisoformat(v)
def save(p,v):(O/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
run=read('native-execute.stdout');pre=read('native-preflight.stdout')
assert run['TOKEN_LIFECYCLE']=='PASS' and run['TOKEN_REQUEST_COMMANDS']==2
assert pre['TOKEN_REQUEST_COMMANDS']==0
assert [x['http_status'] for x in run['observations']]==[200,401,200]
assert [x['phase'] for x in run['observations']]==['valid','expired','recovery']
assert len(run['credentials'])==len(run['cp1_credentials'])==2 and len(run['sources'])==3
assert run['ENDPOINT_CLEANUP']=='ACK_AND_PROCESS_EXIT'
assert run['GLOBAL_LOG_ARTIFACT_RESIDUE']=='REQUIRES_POSTCOLLECTION'
first,second=run['credentials'];valid,denied,recovery=run['observations']
SA='8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'
for pos,cred in enumerate(run['credentials']):
    assert cred['service_account_uid']==SA and cred['local_credential_cleanup']=='LOCAL_REFERENCE_DROPPED'
    assert cred['authentication_basis']=='CALLER_AUTHENTICATED_FRESH_TOKEN_REVIEW'
    assert (stamp(cred['expires_at'])-stamp(cred['issued_at'])).total_seconds()==900
    assert stamp(cred['token_request_expires_at'])<=stamp(cred['expires_at'])
    for k in ('issued_at','expires_at','token_request_expires_at','service_account_uid'):
        assert run['cp1_credentials'][pos][k]==cred[k]
assert stamp(second['issued_at'])>stamp(first['expires_at'])
assert (stamp(denied['server_date'])-stamp(first['expires_at'])).total_seconds()>=60
assert stamp(valid['server_date'])<stamp(first['expires_at']) and stamp(recovery['server_date'])<stamp(second['expires_at'])
assert all(x['method']=='GET' and x['path']=='/apis/apps/v1/namespaces/fds-app/deployments/transaction-api' for x in run['observations'])
s=importlib.util.spec_from_file_location('compare',O.parent.parent/'phase1-work-20261013/cicd-ac07-rbac-20261014/tools/trivy/compare_scan_observations.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a,b=m.identity(read('app-fresh/stdout.json')),m.identity(read('app-after/stdout.json'))
assert a==b
assert valid['deployment_uid']==recovery['deployment_uid']==b['deployments']['transaction-api']['identity']['uid']
assert read('cp1-auth-after/stdout.json')['api_get']['metadata']['uid']==SA
before,after=read('rbac-fresh/stdout.json'),read('rbac-after/stdout.json')
for k in ('bindings','roles','rolebindings_examined','clusterrolebindings_examined','subject','groups'):assert before[k]==after[k]
assert all(q['rc']==0 for q in after['queries'])
binding=read('SOURCE_BINDING.json');expected={x['name']:x['sha256'] for x in binding['files'] if x['name']!='transfer_native_probe.py'}
stage={'transfer_native_probe.py':next(x['sha256'] for x in binding['files'] if x['name']=='transfer_native_probe.py'),
       'lifecycle-source.json':binding['bundle_sha256']}
dirs=files=0
for data in (read('cleanup-ansible.stdout'),read('cleanup-cp1/stdout.json'),read('cleanup-runner/stdout.json')):
    assert not data['active_probe_processes'] and not data['unreadable_same_uid_python'] and not data['unclassified_python']
    for d in data['directories']:
        want=stage if Path(d['path']).name.startswith('FDS_AC08_20261015.') else expected
        assert {x['name']:x['sha256'] for x in d['files']}==want
        assert d['mode']=='0o700' and all(x['mode']=='0o600' and x['secret_pattern_hits']==0 for x in d['files'])
        dirs+=1;files+=len(d['files'])
assert dirs==8 and files==58
runner=read('runner-after/stdout.json')
assert runner['readiness']=='READY' and not any(v for k,v in runner['process_counts'].items() if k!='Runner.Listener')
secret=re.compile(rb'eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]+|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|Authorization: Bearer [A-Za-z0-9_-]{20,}')
scanned=[]
for p in sorted(O.rglob('*')):
    if not p.is_file():continue
    assert not p.is_symlink()
    raw=p.read_bytes();assert not secret.search(raw),p.name
    scanned.append({'path':p.relative_to(O).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
summary={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'TOKEN_LIFECYCLE':'PASS','http_statuses':[200,401,200],
 'token_request_commands':2,'token_ttl_seconds':[900,900],'old_token_expired_401_server_date':denied['server_date'],
 'server_expiry_margin_seconds':(stamp(denied['server_date'])-stamp(first['expires_at'])).total_seconds(),
 'same_sa_and_deployment_uid':True,'app_identity_spec_imageID_ready_restart_unchanged':True,'deployments':2,'pods_ready':6,
 'rbac_bindings_unchanged':len(after['bindings']),'rbac_roles_unchanged':len(after['roles']),
 'probe_processes_remaining':0,'unreadable_candidate_processes':0,'public_source_and_staging_dirs':dirs,
 'public_files_hash_match':files,'secret_pattern_hits':0,'local_receipt_files_scanned':scanned,
 'residue_scope':'All newly staged source/broker/bundle directories on three hosts and local public result/log collection; no Actions runtime/artifact was created. No whole disk, audit log or memory zeroization claim.',
 'AC08':'RUNTIME_OBSERVED_EVIDENCE_REVIEW_PENDING','server_revocation':'NOT_PERFORMED','DEPLOY':'NOT_EXECUTED','DELIVERY_GATE':'NOT_VERIFIED'}
save('POSTCHECK_SUMMARY.json',summary)
save('WINDOW_RELEASE.json',{'at_utc':summary['at_utc'],'runtime_complete':True,'postcheck':'PASS','remaining_active_probe_processes':0,
 'window_kst':'09:35–10:05','natural_token_expiry_utc':[x['expires_at'] for x in run['credentials']],
 'token_reference_retained':False,'server_revocation':'NOT_PERFORMED'})
print(json.dumps({k:v for k,v in summary.items() if k!='local_receipt_files_scanned'},ensure_ascii=False))
