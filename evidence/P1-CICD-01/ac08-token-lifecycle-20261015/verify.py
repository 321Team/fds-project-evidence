"""Offline AC08 receipt consistency only; no network, token issuance or raw execution."""
import datetime as dt,hashlib,importlib.util,json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):ROOT=Path('\\\\?\\'+str(ROOT))
R=ROOT/'raw';REF=ROOT/'references'
HEAD='4043d975fdcd72aa38e2dca5e57e00ebc7ecbd70'
MERGE='c373f1d7a8e6e84548180839098c34e9a1262eef'
SA='8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'
CA='5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c'
NAMES={'deploy_token_lifecycle.py','deploy_native_probe.py','deploy_cp1_access.py','deploy_binding.py',
       'deploy_credential.py','deploy_transport.py','deploy_adapter.py','delivery_gate.py'}
def j(p):return json.loads(p.read_bytes())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def t(v):return dt.datetime.fromisoformat(v.replace('Z','+00:00'))
def need(ok,code):
    if not ok:raise ValueError(code)

def main():
    listed={}
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        need(re.fullmatch('[0-9a-f]{64}',digest) and name not in listed and not Path(name).is_absolute() and '..' not in Path(name).parts,'MANIFEST_ENTRY')
        need(h(ROOT/name)==digest,'MANIFEST_HASH');listed[name]=digest
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
    need(actual==set(listed),'MANIFEST_COVERAGE')
    binding=j(R/'SOURCE_BINDING.json');bundle=j(R/'lifecycle-source.json')
    need(binding['reviewed_head']==HEAD and binding['merge']==MERGE and bundle['source_sha']==MERGE,'SOURCE_SHA')
    need(bundle['schema']=='P1-CICD-token-lifecycle-source-1' and set(bundle['files'])==NAMES,'SOURCE_SCHEMA')
    need(binding['bundle_sha256']==h(R/'lifecycle-source.json'),'BUNDLE_HASH')
    need({x['name'] for x in binding['files']}==NAMES|{'transfer_native_probe.py'} and len(binding['files'])==9,'SOURCE_COUNT')
    for row in binding['files']:
        raw=(R/'source'/row['name']).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'] and blob==row['git_blob'] and row['reviewed_head_bytes_equal'] is True,'SOURCE_BYTES')
        if row['name'] in NAMES:
            need(bundle['files'][row['name']]=={'git_blob':blob,'content':raw.decode()},'BUNDLE_BYTES')
    pr=j(REF/'pr83.json');reviews=j(REF/'reviews83.json')
    need(pr['merged'] and pr['head']['sha']==HEAD and pr['merge_commit_sha']==MERGE,'MERGE')
    need(any(x['id']==5526395946 and x['commit_id']==HEAD and x['state']=='APPROVED' and x['user']['login']=='hayeounglee' for x in reviews),'REVIEW')
    for name,sha in [('pr-ci',HEAD),('merge-ci',MERGE)]:
        ci=j(REF/(name+'.json'));need(ci['status']=='completed' and ci['conclusion']=='success' and ci['head_sha']==sha,'CI')
    for row in j(REF/'REFERENCE_BINDING.json'):
        need(h(REF/Path(row['path']).name)==row['sha256'] and row['commit']==MERGE,'REFERENCE_HASH')
    expected_reads={'app-before','runner-before','rbac-before','cp1-auth-before','runner-auth-before',
                    'clock-cp1','clock-runner','app-fresh','runner-fresh','rbac-fresh',
                    'app-after','runner-after','rbac-after','cp1-auth-after','cleanup-cp1','cleanup-runner'}
    expected_commands={'ansible-identity','mkdir-public','copy-public','public-hashes','native-preflight','native-execute','cleanup-ansible'}
    need({p.parent.name for p in R.glob('*/receipt.json')}==expected_reads,'READ_RECEIPT_COVERAGE')
    need({p.name.removesuffix('.receipt.json') for p in R.glob('*.receipt.json')}==expected_commands,'COMMAND_RECEIPT_COVERAGE')
    receipts=0
    for p in R.glob('*/receipt.json'):
        obj=j(p);folder=p.parent
        need(obj['rc']==0 and h(folder/'stdout.json')==obj['stdout_sha256'] and h(folder/'stderr.txt')==obj['stderr_sha256']
             and h(folder/'collector.py')==obj['source_sha256'] and not (folder/'stderr.txt').read_bytes(),'READ_RECEIPT');receipts+=1
    for p in R.glob('*.receipt.json'):
        obj=j(p);stem=p.name.removesuffix('.receipt.json')
        need(obj['rc']==0 and h(R/(stem+'.stdout'))==obj['stdout_sha256'] and h(R/(stem+'.stderr'))==obj['stderr_sha256'],'COMMAND_RECEIPT');receipts+=1
    pre=j(R/'native-preflight.stdout');run=j(R/'native-execute.stdout')
    need(pre['PREFLIGHT']=='PASS' and pre['TOKEN_REQUEST_COMMANDS']==0 and pre['TOKEN_LIFECYCLE']=='NOT_EXECUTED','PREFLIGHT')
    need(run['TOKEN_LIFECYCLE']=='PASS' and run['TOKEN_REQUEST_COMMANDS']==2,'LIFECYCLE')
    need(run['ENDPOINT_CLEANUP']=='ACK_AND_PROCESS_EXIT' and run['GLOBAL_LOG_ARTIFACT_RESIDUE']=='REQUIRES_POSTCOLLECTION','SCOPE_RECEIPT')
    for data in (pre,run):
        need(data['source_sha']==MERGE and data['bundle_sha256']==binding['bundle_sha256'],'RESULT_SOURCE')
        for source in data['sources']:
            need(source['source_sha']==MERGE and source['ca_sha256']==CA,'ENDPOINT_SOURCE_CA')
            if source['role']=='cp1':need(source['sa_uid']==SA,'SA_UID')
    need(len(pre['sources'])==2 and [x['role'] for x in run['sources']]==['cp1','runner','cp1'],'ENDPOINT_SEQUENCE')
    need(len(run['credentials'])==len(run['cp1_credentials'])==2,'TOKEN_COUNT')
    for i,c in enumerate(run['credentials']):
        need(c['service_account_uid']==SA and c['subject']=='system:serviceaccount:ci-cd:cicd-runner-sa'
             and c['audience']=='https://kubernetes.default.svc.cluster.local','TOKEN_IDENTITY')
        need((t(c['expires_at'])-t(c['issued_at'])).total_seconds()==900 and c['token_request_expires_at']==c['expires_at'],'TOKEN_TTL')
        need(c['authentication_basis']=='CALLER_AUTHENTICATED_FRESH_TOKEN_REVIEW' and c['local_credential_cleanup']=='LOCAL_REFERENCE_DROPPED','TOKEN_REVIEW_CLEANUP')
        cp=run['cp1_credentials'][i]
        for key in ('issued_at','expires_at','token_request_expires_at','service_account_uid','local_credential_cleanup'):
            need(c[key]==cp[key],'TOKEN_RECEIPTS')
    first,second=run['credentials']
    need(t(second['issued_at'])>t(first['expires_at']),'FRESH_RECOVERY_TOKEN')
    rows=run['observations'];need(len(rows)==3,'OBSERVATION_COUNT')
    for row,phase,status in zip(rows,('valid','expired','recovery'),(200,401,200)):
        need(set(row)=={'phase','method','path','http_status','server_date','observed_at','deployment_uid'},'OBSERVATION_FIELDS')
        need(row['phase']==phase and row['http_status']==status and row['method']=='GET'
             and row['path']=='/apis/apps/v1/namespaces/fds-app/deployments/transaction-api','HTTP_SEQUENCE')
        need(abs((t(row['server_date'])-t(row['observed_at'])).total_seconds())<=20,'HTTP_CLOCK')
    need(t(rows[0]['server_date'])<t(first['expires_at']) and t(rows[2]['server_date'])<t(second['expires_at']),'LIVE_200')
    need((t(rows[1]['server_date'])-t(first['expires_at'])).total_seconds()>=60 and rows[1]['deployment_uid'] is None,'EXPIRED_401')
    need(t(rows[0]['observed_at'])<t(rows[1]['observed_at'])<t(rows[2]['observed_at']),'TIME_SEQUENCE')
    authority=j(R/'EXECUTION_AUTHORITY.json');intent=j(R/'EXECUTE_INTENT.json');receipt=j(R/'native-execute.receipt.json')
    need(authority['maximum_token_request_commands']==intent['maximum_token_request_commands']==2 and authority['source_sha']==intent['source_sha']==MERGE,'ATTEMPT_BOUND')
    need(authority['runtime']=='GO' and authority['fresh_prechecks']=='PASS'
         and 0<=(t(receipt['started_at_utc'])-t(authority['checked_at_utc'])).total_seconds()<120,'FRESH_AUTHORITY')
    need('--token-lifecycle' in receipt['argv'][-1] and '--execute --max-token-requests 2 --authorization-expires 2026-10-15T01:05:00+00:00' in receipt['argv'][-1],'EXECUTE_COMMAND')
    need(t(receipt['finished_at_utc'])<t(authority['authorization_expires']),'WINDOW')
    s=importlib.util.spec_from_file_location('compare',REF/'compare_scan_observations.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    before=j(R/'app-fresh/stdout.json');after=j(R/'app-after/stdout.json');a,b=m.identity(before),m.identity(after)
    need(a==b,'APP_DRIFT')
    need(rows[0]['deployment_uid']==rows[2]['deployment_uid']==b['deployments']['transaction-api']['identity']['uid'],'DEPLOYMENT_UID')
    need(0<=(t(receipt['started_at_utc'])-t(before['finished_at_utc'])).total_seconds()<300,'APP_BEFORE_FRESH')
    need(0<=(t(after['started_at_utc'])-t(receipt['finished_at_utc'])).total_seconds()<300,'APP_AFTER_FRESH')
    rb,ra=j(R/'rbac-fresh/stdout.json'),j(R/'rbac-after/stdout.json')
    for key in ('bindings','roles','rolebindings_examined','clusterrolebindings_examined','subject','groups'):need(rb[key]==ra[key],'RBAC_DRIFT')
    need(j(R/'cp1-auth-after/stdout.json')['api_get']['metadata']['uid']==SA,'SA_AFTER')
    expected={x['name']:x['sha256'] for x in binding['files'] if x['name'] in NAMES}
    staging={'transfer_native_probe.py':h(R/'source/transfer_native_probe.py'),'lifecycle-source.json':binding['bundle_sha256']}
    expected_dirs={'ansible01':[pre['local_source_workdir'],run['local_source_workdir'],j(R/'PUBLIC_STAGING.json')['remote_directory']],
                   'k8s-control01':[x['workdir'] for data in (pre,run) for x in data['sources'] if x['role']=='cp1'],
                   'cicd-runner01':[x['workdir'] for data in (pre,run) for x in data['sources'] if x['role']=='runner']}
    dirs=files=0
    for data in (j(R/'cleanup-ansible.stdout'),j(R/'cleanup-cp1/stdout.json'),j(R/'cleanup-runner/stdout.json')):
        need(not data['active_probe_processes'] and not data['unreadable_same_uid_python'] and not data['unclassified_python'],'RESIDUAL_PROCESS')
        need([d['path'] for d in data['directories']]==expected_dirs[data['host']],'CLEANUP_PATHS')
        for d in data['directories']:
            want=staging if '/FDS_AC08_20261015.' in d['path'] else expected
            need(d['mode']=='0o700' and {f['name']:f['sha256'] for f in d['files']}==want
                 and all(f['mode']=='0o600' and f['secret_pattern_hits']==0 for f in d['files']),'PUBLIC_SOURCE_CLEANUP')
            dirs+=1;files+=len(d['files'])
    need(dirs==8 and files==58,'CLEANUP_COUNT')
    for name in ('runner-fresh','runner-after'):
        data=j(R/name/'stdout.json');need(data['readiness']=='READY' and not any(v for k,v in data['process_counts'].items() if k!='Runner.Listener'),'RUNNER_BUSY')
    for data in (run,j(R/'POSTCHECK_SUMMARY.json')):
        need(data['DEPLOY']=='NOT_EXECUTED' and data['DELIVERY_GATE']=='NOT_VERIFIED' and data['server_revocation']=='NOT_PERFORMED','SCOPE')
    post=j(R/'POSTCHECK_SUMMARY.json');release=j(R/'WINDOW_RELEASE.json')
    need(post['TOKEN_LIFECYCLE']=='PASS' and post['probe_processes_remaining']==0 and post['secret_pattern_hits']==0
         and post['public_source_and_staging_dirs']==dirs and post['public_files_hash_match']==files,'POSTCHECK_SUMMARY')
    need(release['postcheck']=='PASS' and release['runtime_complete'] is True and release['token_reference_retained'] is False
         and release['remaining_active_probe_processes']==0 and release['natural_token_expiry_utc']==[first['expires_at'],second['expires_at']],'RELEASE_SCOPE')
    secret=re.compile(rb'eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]+|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|Authorization: Bearer [A-Za-z0-9_-]{20,}')
    for name in actual:need(not secret.search((ROOT/name).read_bytes()),'SECRET_PATTERN')
    print(json.dumps({'OFFLINE_CONSISTENCY':'PASS','manifest_files':len(listed),'receipts':receipts,'source_files':9,
          'http_statuses':[200,401,200],'token_request_commands':2,'token_ttl_seconds':[900,900],
          'ReadyPods':6,'public_directories':dirs,'public_files':files,'AC08':'RUNTIME_OBSERVED_EVIDENCE_REVIEW_PENDING'}))
if __name__=='__main__':main()
