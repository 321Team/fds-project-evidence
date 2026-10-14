import concurrent.futures, datetime as dt, importlib.util, json, subprocess
from pathlib import Path
O=Path(__file__).resolve().parent
R=O.parent.parent
s=importlib.util.spec_from_file_location('collect',O.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=O
key='/home/server01_ansible/.ssh/p1_ansible_ed25519'
tasks=[('app-fresh','10.1.93.102','svc_ansible',key,True,O/'app-before/collector.py',[]),('runner-fresh','10.250.10.20','server01_cicd-runner',key,False,O/'runner-before/collector.py',[])]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(m.remote,tasks))
assert all(x['rc']==0 and x['stderr_bytes']==0 for x in results),results
runner=json.loads((O/'runner-fresh/stdout.json').read_bytes())
assert runner['readiness']=='READY'
assert not any(v for k,v in runner['process_counts'].items() if k!='Runner.Listener')
app=json.loads((O/'app-fresh/stdout.json').read_bytes())
assert all(q['rc']==0 for q in app['queries'])
deps=next(q['items'] for q in app['queries'] if q['kind']=='deployments')
pods=next(q['items'] for q in app['queries'] if q['kind']=='pods')
assert len(deps)==2 and len(pods)==6
assert all(d['replicas']==3 and d['status']['readyReplicas']==3 for d in deps)
assert all(p['phase']=='Running' and all(c['ready'] for c in p['statuses']) for p in pods)
for repo in ['infra-cicd','infra-ansible']:
    p=subprocess.run(['gh','api',f'repos/321Team/{repo}/actions/runs?per_page=100'],capture_output=True,check=True)
    (O/(repo+'-fresh-runs.json')).write_bytes(p.stdout)
    active=[x for x in json.loads(p.stdout)['workflow_runs'] if x['status']!='completed']
    assert not active,[(x['id'],x['status']) for x in active]
pr=json.loads((O/'pr82-after.json').read_bytes())
pre=json.loads((O/'native-preflight.stdout').read_bytes())
assert pre['PREFLIGHT']=='PASS' and pre['TOKEN_ISSUED'] is False
assert (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(pre['checked_at'])).total_seconds()<300
record={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'runtime':'GO','fresh_prechecks':'PASS','maximum_token_request_commands':1,'source_sha':'9fb2e2dcac8682a89c4b7c267c833ae8d9aaeb18','reviewed_head':'db8230d7580820c55ab388680a1e87fc3e45db0a','review_url':'https://github.com/321Team/infra-cicd/pull/82#pullrequestreview-5518054443','ci':'https://github.com/321Team/infra-cicd/actions/runs/38564435253','merge_ci':'https://github.com/321Team/infra-cicd/actions/runs/38566564766','authority':'User/Lead 이권욱: 리뷰 체크 후 차단 사항 없으면 병합 후 착수','policy_sha256':'3f08642d16ecc9fc3a3b548dc5f5a1c5f4a922d7028ca997c3907cb88c818e81','independent_review_scope':'code only; Runtime decision recorded separately by Lead authorization','window_kst':'2026-10-14 21:50–22:10; start before 22:00','coordination':{'harbor':'Acknowledged idle; hold until release','ansible':'Acknowledged idle; hold until release','d03':'Acknowledged 21:50–22:10 reserved; D03 runtime deferred, PR35/230 local/review work only'},'targets':['ansible01','k8s-control01','cicd-runner01'],'scope':'One <=900s SA token command, fresh TokenReview, Runner 25 SSAR (6 allow/19 deny) and 2 fixed deployment GETs. No deploy/PATCH/exec/RBAC mutation/Secret GET. No AC08 old/new-token experiment.','stop_recovery':'Any binding/CA/identity/response mismatch stops. Preserve result and issuance attempt; no automatic retry. No service/config mutation. Private subprocess/reference cleanup; token natural expiry, no SA deletion/revocation.','precheck_results':results}
(O/'EXECUTION_AUTHORITY.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('FRESH_GATE_PASS_AUTHORITY_RECORDED')
