import datetime as dt, hashlib, importlib.util, json, shlex, subprocess
from pathlib import Path
O=Path(__file__).resolve().parent
def read(p):return json.loads((O/p).read_bytes())
def save(p,v):(O/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
run=read('native-execute.stdout');pre=read('native-preflight.stdout')
source=(O/'read_cleanup.py').read_bytes()
argv=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01',shlex.join(['/usr/bin/python3','-I','-B','-S','-',pre['local_source_workdir'],run['local_source_workdir']])]
start=dt.datetime.now(dt.timezone.utc).isoformat()
p=subprocess.run(argv,input=source,capture_output=True,timeout=30)
(O/'cleanup-ansible.stdout').write_bytes(p.stdout);(O/'cleanup-ansible.stderr').write_bytes(p.stderr)
save('cleanup-ansible.receipt.json',{'started_at_utc':start,'finished_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'argv':argv,'rc':p.returncode,'source_sha256':hashlib.sha256(source).hexdigest(),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'classification':'PURE_READ_POSTCHECK'})
assert p.returncode==0 and not p.stderr
s=importlib.util.spec_from_file_location('compare',O.parent.parent/'phase1-work-20261013/cicd-ac07-rbac-20261014/tools/trivy/compare_scan_observations.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert m.identity(read('app-fresh/stdout.json'))==m.identity(read('app-after/stdout.json'))
before,after=read('rbac-before-r2/stdout.json'),read('rbac-after/stdout.json')
for key in ['bindings','roles','rolebindings_examined','clusterrolebindings_examined','subject','groups']:assert before[key]==after[key],key
assert all(q['rc']==0 for q in after['queries'])
expected={x['name']:x['sha256'] for x in read('SOURCE_BINDING.json')['files'] if x['name']!='transfer_native_probe.py'}
for data in [json.loads(p.stdout),read('cleanup-cp1/stdout.json'),read('cleanup-runner/stdout.json')]:
    assert not data['active_probe_processes']
    for d in data['directories']:
        assert {f['name']:f['sha256'] for f in d['files']}==expected
permissions=run['runner_observation']['permissions']
assert len(permissions)==25 and sum(x['allowed'] is True for x in permissions)==6 and all(x['allowed']==x['expected'] for x in permissions)
assert run['runner_observation']['RUNNER_TOKEN_AUTH']==run['runner_observation']['EFFECTIVE_RBAC_CHECK']=='PASS'
assert len(run['runner_observation']['deployments'])==2
for d in run['runner_observation']['deployments']:
    expected_uid=m.identity(read('app-after/stdout.json'))['deployments'][d['name']]['identity']['uid']
    assert d['uid']==expected_uid
c=run['cp1_credential'];ttl=(dt.datetime.fromisoformat(c['expires_at'])-dt.datetime.fromisoformat(c['issued_at'])).total_seconds();assert ttl==900
summary={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'NATIVE_AUTH_PROBE':'PASS','permission_total':25,'allow':6,'deny':19,'deployment_gets':2,'token_ttl_seconds':ttl,'expires_at_utc':c['expires_at'],'app_identity_spec_imageID_ready_restart_unchanged':True,'deployments':2,'pods_ready':6,'rbac_relevant_bindings_unchanged':len(after['bindings']),'rbac_roles_unchanged':len(after['roles']),'all_rolebindings_examined':after['rolebindings_examined'],'all_clusterrolebindings_examined':after['clusterrolebindings_examined'],'probe_processes_remaining':0,'public_source_dirs':6,'public_source_files_sha256_match':42,'cleanup_scope':'Process termination and public-source directory allowlist only; credential local references dropped by broker; no physical memory erasure claim','revocation':'NOT_PERFORMED; natural expiry, no token-retaining expiry test','rbac_limit':'Fixed 25 SSAR plus enumerated RBAC grants, not exhaustive authorization-system proof','AC07':'RUNTIME_OBSERVED_EVIDENCE_REVIEW_PENDING','AC08':'NOT_EXECUTED','DEPLOY':'NOT_EXECUTED','DELIVERY_GATE':'NOT_VERIFIED'}
save('POSTCHECK_SUMMARY.json',summary)
save('WINDOW_RELEASE.json',{'at_utc':summary['at_utc'],'runtime_complete':True,'postcheck':'PASS','remaining_active_probe_processes':0,'window':'21:50-22:10 KST','natural_token_expiry_kst':'2026-10-14 22:10:58','token_reference_retained':False,'server_revocation':'NOT_PERFORMED'})
print(json.dumps(summary,ensure_ascii=False))
