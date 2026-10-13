"""Local unapproved plan construction; no dispatch, approval or remote writes."""
import base64, concurrent.futures, dataclasses, datetime, hashlib, json, pathlib, subprocess, sys, uuid
OUT=pathlib.Path(__file__).parent
ROOT=OUT.parent.parent
E=ROOT/'phase1-work-20261013/db-policy-evidence/evidence/P1-CICD-01/app-push-runtime-20261013T0751'
C=ROOT/'deliverables/p1-preapply-until-0930-20261012/other-work/checkouts/infra-cicd'
sys.dont_write_bytecode=True
sys.path.insert(0,str(C/'tools/delivery'))
import deploy_plan as p
import deploy_binding as b
import delivery_gate as gate
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,obj):
    raw=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
    (OUT/name).write_bytes(raw)
    return raw
def gh(endpoint):
    x=subprocess.run(['gh','api',endpoint],capture_output=True,check=True,encoding='utf-8')
    return json.loads(x.stdout)
def fetch(item):
    name,endpoint=item
    data=gh(endpoint);save(name+'.json',data)
    return name,data
items=[(f'issue-{n}',f'repos/321Team/fds-project-baseline/issues/{n}') for n in (16,17,19,24,30)]
items += [('cicd11','repos/321Team/infra-cicd/issues/11'),('main','repos/321Team/infra-cicd/commits/main'),('pr212','repos/321Team/fds-project-evidence/pulls/212')]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    data=dict(pool.map(fetch,items))
source='2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
assert data['main']['sha']==source
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=C,text=True).strip()==source
assert not subprocess.check_output(['git','status','--porcelain'],cwd=C,text=True).strip()
delivery_raw=(E/'push-20261013-window1200.json').read_bytes()
assert sha(delivery_raw)=='13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89'
delivery=b.read(delivery_raw)
envelope=json.loads((E/'execution-result/stdout.json').read_bytes())
receipt=envelope['files']['result.json']
push_raw=base64.b64decode(receipt['raw_b64'],validate=True)
assert sha(push_raw)==receipt['sha256']=='012545c60017ab1120ab9b61459451a794c67b7a0a803d4f079798b5ed97f905'
(OUT/'push-result.original.json').write_bytes(push_raw)
cluster=json.loads((OUT/'cluster/stdout.json').read_bytes())
assert all(q['rc']==0 for q in cluster['queries'])
queries={q['kind']:q['items'] for q in cluster['queries']}
old=json.loads((OUT.parent/'p1-parallel-until-0900-20261013/DEPLOY_PREPARATION.after-push.pending.json').read_bytes())
assert queries['deployments']==old['targets_observed']
assert cluster['ca_sha256']==old['cp1_existing_auth']['ca_sha256']
sa=queries['serviceaccount'][0]
assert sa['metadata']['uid']==old['cp1_existing_auth']['sa_uid'] and sa['automountServiceAccountToken'] is False
plan_path=OUT/'deploy-plan.unapproved.json'
request=json.loads(plan_path.read_bytes())['request_id'] if plan_path.exists() else str(uuid.uuid4())
plan={'schema':'P1-CICD-deploy-plan-2','template_only':False,'request_id':request,
 'workflow':{'repository':'321Team/infra-cicd','ref':'refs/heads/main','workflow_sha':source},
 'delivery':delivery,'push_execution':{'workflow_sha':source,'run_id':'38318968352','attempt':1},
 'push_receipt_sha256':sha(push_raw),
 'kubernetes':{'api_server':gate.KUBERNETES_API,'service_account':gate.SERVICE_ACCOUNT,'token_audience':b.AUDIENCE,'token_ttl_seconds':gate.TOKEN_REQUEST_SECONDS,'token_policy_reference':gate.TOKEN_POLICY_REFERENCE},
 'targets':{x['metadata']['name']:{'namespace':x['metadata']['namespace'],'deployment':x['metadata']['name'],'container':x['containers'][0]['name'],'uid':x['metadata']['uid'],'previous_image':x['containers'][0]['image']} for x in queries['deployments']}}
raw=save('deploy-plan.unapproved.json',plan)
assert set(plan)==p.PLAN_FIELDS and p.workflow(plan['workflow'])==plan['workflow']
assert set(plan['kubernetes'])==p.KUBERNETES_FIELDS
assert all(set(t)==p.TARGET_FIELDS for t in plan['targets'].values())
# Existing pure payload validator needs a non-Build/non-Push Run identifier.
# 1 is an in-memory STATIC sentinel, never a claimed or written actual Deploy Run.
build,targets=b.payload_checked(plan,push_raw,{'run_id':1})
checks={}
for name,expected in [('deploy-controller-2d8a14c.tar','67df6be5d7f935f2618e55365b7c3f0250bea99b771a579873e7961f9061f261'),('native-source-2d8a14c.json','8cfdcce5e4b5eb95001d27e35606e5121edf77d8c2c1f5f481016c79933baa5c')]:
    actual=sha((OUT.parent/'p1-parallel-until-0900-20261013'/name).read_bytes());assert actual==expected;checks[name]=actual
result={'schema':'P1-CICD-local-plan-readiness-1','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime_authorized':False,'approval_created':False,'record_created':False,'dispatch_performed':False,'token_issued':False,'plan_sha256':sha(raw),'request_id':request,'push_sha256':sha(push_raw),'source_commit':source,'sa_uid':sa['metadata']['uid'],'targets':[dataclasses.asdict(t) for t in targets],'source_packages':checks,'checks':{'pure_payload':'PASS','payload_context':'STATIC sentinel Run 1 only, no actual Deploy Run claimed','schema_fields':'PASS','target_snapshot_matches_previous':'PASS','sa_ca_match':'PASS','remote_main_matches_local_clean_checkout':'PASS','actual_deploy_context':'NOT_CREATED','full_detached_approval_validation':'NOT_RUN','rollback_registry_availability':'NOT_VERIFIED'},'limitations':['Plan template_only=false means concrete input, not runtime authorization.','Historical Push authorization expired; it is not Deploy authorization.','Fresh metadata does not prove business health, packet policy, or exclusive access.','No native TokenRequest/TokenReview, server staging or Deploy was performed.']}
save('PLAN_VALIDATION.json',result)
for name,obj in data.items():
    if name.startswith('issue-') or name=='cicd11':
        print(name,obj['updated_at'],*[l for l in obj['body'].splitlines() if l.startswith('- **잔여·경계:**')],sep='\n')
print(json.dumps({'request_id':request,'plan_sha256':sha(raw),'pr212_merge':data['pr212']['merge_commit_sha'],'merged_at':data['pr212']['merged_at']},ensure_ascii=False))
