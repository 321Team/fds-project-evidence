"""Offline AC07 evidence consistency; no network or token operations."""
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):ROOT=Path('\\\\?\\'+str(ROOT))
R=ROOT/'raw'
HEAD='db8230d7580820c55ab388680a1e87fc3e45db0a'
MERGE='9fb2e2dcac8682a89c4b7c267c833ae8d9aaeb18'
SA='8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'
CA='5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c'
def j(p):return json.loads(p.read_bytes())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def t(v):return dt.datetime.fromisoformat(v.replace('Z','+00:00'))
def need(ok,msg):
    if not ok:raise ValueError(msg)

def expected_permissions():
    rows=[]
    def add(allow,group,resource,verb,namespace=None,name=None,subresource=None):
        a={'group':group,'resource':resource,'verb':verb,'version':'v1'}
        for k,v in [('namespace',namespace),('name',name),('subresource',subresource)]:
            if v is not None:a[k]=v
        rows.append({'attributes':a,'expected':allow,'allowed':allow})
    for name in ['transaction-api','fds-engine']:
        for verb in ['get','update','patch']:add(True,'apps','deployments',verb,'fds-app',name)
    add(False,'apps','deployments','create','fds-app')
    add(False,'apps','deployments','delete','fds-app','transaction-api')
    add(False,'apps','deployments','patch','fds-app','unapproved-probe')
    add(False,'apps','deployments','patch','default','transaction-api')
    add(False,'','secrets','get','fds-app')
    add(False,'','pods','list','fds-app')
    add(False,'authentication.k8s.io','tokenreviews','create')
    g='rbac.authorization.k8s.io'
    add(False,g,'roles','create','fds-app')
    for v in ['patch','bind','escalate']:add(False,g,'roles',v,'fds-app','cicd-deploy-updater')
    add(False,g,'rolebindings','create','fds-app')
    add(False,g,'rolebindings','patch','fds-app','cicd-deploy-updater-binding')
    add(False,g,'clusterroles','create')
    for v in ['bind','escalate']:add(False,g,'clusterroles',v,name='cluster-admin')
    add(False,g,'clusterrolebindings','create')
    for v in ['get','create']:add(False,'','pods',v,'fds-app',subresource='exec')
    return rows

def main():
    listed={}
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        need(re.fullmatch('[0-9a-f]{64}',digest) and name not in listed and not Path(name).is_absolute() and '..' not in Path(name).parts,'MANIFEST_ENTRY')
        need(h(ROOT/name)==digest,'HASH '+name);listed[name]=digest
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
    need(actual==set(listed),'MANIFEST_COVERAGE')
    binding=j(R/'SOURCE_BINDING.json');bundle=j(R/'native-source.json')
    need(binding['reviewed_head']==HEAD and binding['merge']==MERGE and bundle['source_sha']==MERGE,'SOURCE_SHA')
    need(binding['bundle_sha256']==h(R/'native-source.json'),'BUNDLE_HASH')
    need(len(binding['files'])==8 and len(bundle['files'])==7,'SOURCE_COUNT')
    for f in binding['files']:
        raw=(R/'source'/f['name']).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(hashlib.sha256(raw).hexdigest()==f['sha256'] and blob==f['git_blob'] and f['reviewed_head_bytes_equal'] is True,'SOURCE_BINDING')
        if f['name'] in bundle['files']:
            b=bundle['files'][f['name']];need(b['git_blob']==blob and b['content'].encode()==raw,'BUNDLE_BYTES')
    refs=ROOT/'references'
    pr=j(refs/'pr82.json');reviews=j(refs/'pr82-reviews.json')
    need(pr['merged'] and pr['head']['sha']==HEAD and pr['merge_commit_sha']==MERGE,'MERGE')
    need(any(x['user']['login']=='hayeounglee' and x['state']=='APPROVED' and x['commit_id']==HEAD for x in reviews),'EXACT_REVIEW')
    for name,sha in [('AC07_LINUX_CI.json',HEAD),('merge-ci.json',MERGE)]:
        ci=j(refs/name);need(ci['head_sha']==sha and ci['conclusion']=='success','CI')
    need(h(refs/'REVIEW_AUTHORITY_POLICY.current.md')=='3f08642d16ecc9fc3a3b548dc5f5a1c5f4a922d7028ca997c3907cb88c818e81','POLICY')
    for f in j(refs/'REFERENCE_BINDING.json'):need(h(refs/Path(f['path']).name)==f['sha256'],'REFERENCE_HASH')
    receipts=0
    for path in R.rglob('receipt.json'):
        obj=j(path);folder=path.parent
        need(h(folder/'stdout.json')==obj['stdout_sha256'] and h(folder/'stderr.txt')==obj['stderr_sha256'] and h(folder/'collector.py')==obj['source_sha256'],'READ_RECEIPT')
        expected_rc=1 if folder.name=='rbac-before' else 0
        need(obj['rc']==expected_rc,'READ_RC');receipts+=1
    for path in R.glob('*.receipt.json'):
        obj=j(path);stem=path.name.removesuffix('.receipt.json')
        need(obj['rc']==0 and h(R/(stem+'.stdout'))==obj['stdout_sha256'] and h(R/(stem+'.stderr'))==obj['stderr_sha256'],'COMMAND_RECEIPT');receipts+=1
    pre=j(R/'native-preflight.stdout');run=j(R/'native-execute.stdout');obs=run['runner_observation']
    need(pre['PREFLIGHT']=='PASS' and pre['TOKEN_ISSUED'] is False,'PREFLIGHT')
    need(run['NATIVE_AUTH_PROBE']=='PASS' and run['TOKEN_ISSUED'] is True and obs['RUNNER_TOKEN_AUTH']==obs['EFFECTIVE_RBAC_CHECK']=='PASS','PROBE')
    need(obs['permissions']==expected_permissions(),'PERMISSION_MATRIX')
    for result in [pre,run]:
        need(result['source_sha']==MERGE and result['bundle_sha256']==binding['bundle_sha256'],'RESULT_SOURCE')
        need(result['cp1']['sa_uid']==SA and result['cp1']['ca_sha256']==result['runner']['ca_sha256']==CA,'CA_SA')
    for c in [run['cp1_credential'],obs['credential']]:
        need(c['service_account_uid']==SA and c['subject']=='system:serviceaccount:ci-cd:cicd-runner-sa' and c['audience']=='https://kubernetes.default.svc.cluster.local','CREDENTIAL_IDENTITY')
        need((t(c['expires_at'])-t(c['issued_at'])).total_seconds()==900 and c['token_request_expires_at']==c['expires_at'],'TTL')
        need(c['authentication_basis']=='CALLER_AUTHENTICATED_FRESH_TOKEN_REVIEW' and c['local_credential_cleanup']=='LOCAL_REFERENCE_DROPPED','TOKEN_REVIEW_CLEANUP')
    need(run['DEPLOY']=='NOT_EXECUTED' and run['DELIVERY_GATE']=='NOT_VERIFIED' and run['server_revocation']=='NOT_PERFORMED','SCOPE')
    authority=j(R/'EXECUTION_AUTHORITY.json');intent=j(R/'EXECUTE_INTENT.json');receipt=j(R/'native-execute.receipt.json')
    need(authority['source_sha']==intent['source_sha']==MERGE and authority['maximum_token_request_commands']==intent['maximum_token_request_commands']==1,'ONE_ATTEMPT')
    need(authority['runtime']=='GO' and authority['fresh_prechecks']=='PASS' and 0<=(t(receipt['started_at_utc'])-t(authority['checked_at_utc'])).total_seconds()<120,'FRESH_GO')
    need('--execute --authorization-expires 2026-10-14T13:10:00+00:00' in receipt['argv'][-1],'EXECUTE_COMMAND')
    for name in ['infra-cicd','infra-ansible']:need(all(r['status']=='completed' for r in j(R/(name+'-fresh-runs.json'))['workflow_runs']),'ACTIVE_RUN')
    s=importlib.util.spec_from_file_location('app_compare',refs/'compare_scan_observations.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    before=j(R/'app-fresh/stdout.json');after=j(R/'app-after/stdout.json')
    a,b=m.identity(before),m.identity(after);need(a==b,'APP_DRIFT')
    need(0<=(t(receipt['started_at_utc'])-t(before['finished_at_utc'])).total_seconds()<300,'FRESH_APP_BEFORE')
    need(0<=(t(after['started_at_utc'])-t(receipt['finished_at_utc'])).total_seconds()<300,'FRESH_APP_AFTER')
    need(len(obs['deployments'])==2 and {x['name']:x['uid'] for x in obs['deployments']}=={k:v['identity']['uid'] for k,v in b['deployments'].items()},'DEPLOYMENT_UID')
    first,last=j(R/'rbac-before-r2/stdout.json'),j(R/'rbac-after/stdout.json')
    for k in ['bindings','roles','rolebindings_examined','clusterrolebindings_examined','subject','groups']:need(first[k]==last[k],'RBAC_DRIFT')
    need(len(last['bindings'])==len(last['roles'])==5 and last['rolebindings_examined']==13 and last['clusterrolebindings_examined']==64,'RBAC_COUNTS')
    for name in ['runner-fresh','runner-after']:
        data=j(R/name/'stdout.json');need(data['readiness']=='READY' and not any(v for k,v in data['process_counts'].items() if k!='Runner.Listener'),'RUNNER_BUSY')
    expected={f['name']:f['sha256'] for f in binding['files'] if f['name']!='transfer_native_probe.py'}
    for data in [j(R/'cleanup-ansible.stdout'),j(R/'cleanup-cp1/stdout.json'),j(R/'cleanup-runner/stdout.json')]:
        need(not data['active_probe_processes'] and len(data['directories'])==2,'PROCESS_CLEANUP')
        for d in data['directories']:need(d['mode']=='0o700' and {f['name']:f['sha256'] for f in d['files']}==expected and all(f['mode']=='0o600' for f in d['files']),'PUBLIC_FILES')
    # Do not print matched data on a failure.
    for name in actual:
        content=(ROOT/name).read_bytes()
        need(not re.search(rb'eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}',content),'JWT_PATTERN '+name)
        need(not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',content),'PRIVATE_KEY '+name)
    print(json.dumps({'OFFLINE_CONSISTENCY':'PASS','manifest_files':len(listed),'receipts':receipts,'source_files':8,'SSAR':25,'allow':6,'deny':19,'GET':2,'ReadyPods':6,'token_ttl_seconds':900,'AC07':'RUNTIME_OBSERVED_EVIDENCE_REVIEW_PENDING','AC08':'NOT_EXECUTED'},ensure_ascii=False))

if __name__=='__main__':main()
