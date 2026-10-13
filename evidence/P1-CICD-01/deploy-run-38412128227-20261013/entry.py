"""Fresh, nonmutating entry checks. Does not grant execution authority."""
import concurrent.futures,datetime,importlib.util,json,pathlib,sys
BASE=pathlib.Path(__file__).parent.resolve()
spec=importlib.util.spec_from_file_location('execution_read',BASE/'execution.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
stamp=e.now().strftime('%H%M%S');OUT=e.OUT/('entry-'+stamp);OUT.mkdir(exist_ok=False);e.collect.OUT=OUT
key='/home/server01_ansible/.ssh/p1_ansible_ed25519';cpkey='/home/server01_ansible/.ssh/id_ed25519';original=BASE.parent/'p1-delivery-runner-20261013';old=BASE.parent/'phase1-deploy-preparation-20261013'
tasks=[('cluster','10.1.93.102','svc_ansible',key,True,original/'cluster_read.py',[]),('app-state','10.1.93.102','svc_ansible',key,True,old/'app_state_read.py',[]),('cp1-auth','10.1.93.102','server02',cpkey,False,original/'auth_path_read.py',['cp1']),('cp1-preissue','10.1.93.102','server02',cpkey,False,old/'cp1_preissue_diagnosis.py',[]),('runner-auth','10.250.10.20','server01_cicd-runner',key,False,original/'auth_path_read.py',['runner']),('runner-health','10.250.10.20','server01_cicd-runner',key,False,BASE.parent/'phase1-push-followup-20261013/runner_push_read.py',[])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(e.collect.remote,tasks))
assert all(r['rc']==0 for r in results)
read=lambda root,name:json.loads((root/name/'stdout.json').read_bytes())
before=read(BASE,'cluster');after=read(OUT,'cluster');assert before['ca_sha256']==after['ca_sha256']
assert all(q['rc']==0 for q in after['queries'])
oldq={q['kind']:q['items'] for q in before['queries']};newq={q['kind']:q['items'] for q in after['queries']}
assert oldq==newq,'CLUSTER_BASELINE_DRIFT'
app=read(OUT,'app-state');pods=next(q['items'] for q in app['queries'] if q['kind']=='pods')
assert len(pods)==6 and all(p['phase']=='Running' and p['metadata']['deletionTimestamp'] is None and all(c['ready'] for c in p['statuses']) for p in pods)
priorpods={p['metadata']['uid']:p for q in read(BASE,'app-state')['queries'] if q['kind']=='pods' for p in q['items']}
for p in pods:
 assert p['metadata']['uid'] in priorpods
 assert p['statuses']==priorpods[p['metadata']['uid']]['statuses'],'POD_CONTAINER_STATE_DRIFT'
cp1=read(OUT,'cp1-auth');runner=read(OUT,'runner-auth');pre=read(OUT,'cp1-preissue');health=read(OUT,'runner-health')
assert cp1['api_get']['rc']==0 and cp1['api_get']['metadata']['uid']==e.A['sa_uid']
assert cp1['ca_sha256']==runner['ca_sha256']==after['ca_sha256']
assert pre['result']=='PREISSUE_PREFLIGHT_PASS' and pre['sa_uid']==e.A['sa_uid'] and not pre['token_request_called'] and not pre['token_review_called']
assert runner['api_tls']['verified'] and health['worker_count']==0
assert health['harbor']['tls_verified'] and health['harbor']['status']=='healthy'
assert e.gh('repos/321Team/infra-cicd/commits/main')['sha']==e.SOURCE
active={}
for status in ('in_progress','queued','waiting','pending','requested'):
 runs=e.gh('repos/321Team/infra-cicd/actions/runs?status='+status+'&per_page=100');active[status]=runs['total_count'];assert runs['total_count']==0
 e.save(OUT/('actions-'+status+'.json'),runs)
pr=e.gh('repos/321Team/infra-harbor-trivy/pulls/62');e.save(OUT/'harbor62.json',pr)
comments=e.gh('repos/321Team/infra-harbor-trivy/issues/62/comments?per_page=100&page='+str(max(1,(pr['comments']+99)//100)));e.save(OUT/'harbor62-comments.json',comments)
result={'result':'PASS','at_utc':e.now().isoformat(),'directory':str(OUT),'cluster_metadata_equal_to_2245':True,'pods_same_uid_imageid_restartcounts':True,'cp1_preissue':'PASS_NO_TOKEN','runner_worker_count':0,'harbor_tls_health':'PASS','active_actions':active,'source':e.SOURCE,'user_nonoverlap':e.A['nonoverlap'],'user_console':e.A['console'],'scope':'Read-only pre-entry; no dispatch/staging/token/deploy','review_independent':'CHECKED_SEPARATELY_BEFORE_STAGE'}
e.save(e.OUT/'ENTRY_READINESS.json',result);print(json.dumps(result,ensure_ascii=False))
