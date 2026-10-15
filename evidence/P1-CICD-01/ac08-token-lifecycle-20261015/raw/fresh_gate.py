"""Fresh read-only checks plus local Lead authorization record; no token issuance."""
import concurrent.futures,datetime as dt,importlib.util,json,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent
SHA='c373f1d7a8e6e84548180839098c34e9a1262eef'
def read(p):return json.loads((O/p).read_bytes())
def save(p,v):(O/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=importlib.util.spec_from_file_location('collect',O.parent/'phase1-deploy-after-push-20261013-2244/collect.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=O
key='/home/server01_ansible/.ssh/p1_ansible_ed25519'
tasks=[('app-fresh','10.1.93.102','svc_ansible',key,True,O/'app-before/collector.py',[]),
       ('runner-fresh','10.250.10.20','server01_cicd-runner',key,False,O/'runner-before/collector.py',[]),
       ('rbac-fresh','10.1.93.102','svc_ansible',key,True,O/'rbac-before/collector.py',[])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(m.remote,tasks))
assert all(x['rc']==0 and not x['stderr_bytes'] for x in results)
runner=read('runner-fresh/stdout.json');assert runner['readiness']=='READY'
assert not any(v for k,v in runner['process_counts'].items() if k!='Runner.Listener')
app=read('app-fresh/stdout.json');assert all(q['rc']==0 for q in app['queries'])
deps=next(q['items'] for q in app['queries'] if q['kind']=='deployments')
pods=next(q['items'] for q in app['queries'] if q['kind']=='pods')
assert len(deps)==2 and len(pods)==6
assert all(d['replicas']==3 and d['status']['readyReplicas']==3 for d in deps)
assert all(p['phase']=='Running' and all(c['ready'] for c in p['statuses']) for p in pods)
old,new=read('rbac-before/stdout.json'),read('rbac-fresh/stdout.json')
for field in ('bindings','roles','rolebindings_examined','clusterrolebindings_examined','subject','groups'):assert old[field]==new[field]
assert all(q['rc']==0 for q in new['queries'])
for repo in ('infra-cicd','infra-ansible'):
    raw=subprocess.check_output(['gh','api',f'repos/321Team/{repo}/actions/runs?per_page=100'])
    (O/(repo+'-fresh-runs.json')).write_bytes(raw)
    active=[x for x in json.loads(raw)['workflow_runs'] if x['status']!='completed']
    if repo=='infra-cicd':assert not active,[(x['id'],x['status']) for x in active]
    else:assert all(x['id'] in (38592590915,38579563887) and x['status']=='queued' for x in active)
    rr=subprocess.check_output(['gh','api',f'repos/321Team/{repo}/actions/runners'])
    (O/(repo+'-fresh-runners.json')).write_bytes(rr)
    regs=json.loads(rr)
    assert not any(r['busy'] for r in regs['runners'])
    if repo=='infra-ansible':assert regs['total_count']==0
raw=subprocess.check_output(['gh','api','repos/321Team/infra-cicd/pulls/83'])
(O/'pr83-fresh.json').write_bytes(raw);pr=json.loads(raw)
assert pr['merged'] and pr['merge_commit_sha']==SHA and pr['head']['sha']=='4043d975fdcd72aa38e2dca5e57e00ebc7ecbd70'
pre=read('native-preflight.stdout')
assert pre['PREFLIGHT']=='PASS' and pre['TOKEN_REQUEST_COMMANDS']==0 and pre['source_sha']==SHA
assert pre['sources'][0]['sa_uid']=='8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'
assert (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(pre['checked_at'])).total_seconds()<600
assert read('CLOCK_VERSION_CHECK.json')['cp1']['api_version']['gitVersion']=='v1.36.4'
record={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'runtime':'GO','fresh_prechecks':'PASS',
 'maximum_token_request_commands':2,'source_sha':SHA,'reviewed_head':'4043d975fdcd72aa38e2dca5e57e00ebc7ecbd70',
 'bundle_sha256':read('SOURCE_BINDING.json')['bundle_sha256'],
 'review_url':'https://github.com/321Team/infra-cicd/pull/83#pullrequestreview-5526395946',
 'authority':'User/Lead 이권욱: 서버 실행 가능; PR83 리뷰 후 병합; 병합 뒤 AC08 착수 요청',
 'independent_review_scope':'Code only. Runtime decision follows current user/Lead instruction.',
 'window_kst':'2026-10-15 09:35–10:05; start before09:45',
 'authorization_expires':'2026-10-15T01:05:00+00:00',
 'coordination':read('COORDINATION_FINAL.json'),
 'targets':['ansible01/server01_ansible','k8s-control01/server02','cicd-runner01/server01_cicd-runner'],
 'scope':'One lifecycle attempt, maximum2 TokenRequest commands <=900s each, fixed GET200/expired401/fresh200; no deploy/exec/RBAC/Harbor mutation.',
 'stop_recovery':'Any mismatch/time/CA/UID/cleanup failure stops; attempt consumed, no retry. Own process/reference cleanup and natural expiry; no revocation or host shutdown.',
 'precheck_results':results}
save('EXECUTION_AUTHORITY.json',record)
print('FRESH_GATE_PASS_AUTHORITY_RECORDED')
