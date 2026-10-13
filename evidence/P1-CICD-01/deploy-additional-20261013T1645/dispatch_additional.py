"""One explicit Actions dispatch only; an ambiguous response is never resent."""
import datetime,json,pathlib,subprocess,sys,time

decision=json.loads((pathlib.Path(__file__).parent/'START_CUTOFF_AUTHORIZED.json').read_bytes())
assert decision['user_decision']=='시작 마감 16:45로 변경·17:00 종료 유지'
assert decision['additional_true_runs_allowed']==1 and decision['end_kst']=='2026-10-13T17:00:00+09:00'

BASE=pathlib.Path(__file__).parent
mode=sys.argv[1];assert mode in ('false','true')
suffix=sys.argv[2] if len(sys.argv)>2 else ''
assert mode=='true' and suffix=='-additional'
OUT=BASE/('dispatch-'+mode+suffix);OUT.mkdir(exist_ok=False)
def gh(endpoint):return json.loads(subprocess.check_output(['gh','api',endpoint],encoding='utf-8'))
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
source='2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
now=datetime.datetime.now(datetime.timezone.utc)
assert datetime.datetime.fromisoformat('2026-10-13T16:15:00+09:00')<=now<datetime.datetime.fromisoformat('2026-10-13T16:45:00+09:00')
assert gh('repos/321Team/infra-cicd/commits/main')['sha']==source
approval=gh('repos/321Team/infra-cicd/issues/comments/6140076685')
assert approval['body'].encode()==(BASE/'authorization-20261013T1554/approval.json').read_bytes() and approval['user']['login']=='GWONUK'
endpoint='repos/321Team/infra-cicd/actions/workflows/app-deploy.yml/runs?per_page=20'
before=gh(endpoint);save('runs-before.json',before)
assert not any(x['status']!='completed' for x in before['workflow_runs'])
before_ids={x['id'] for x in before['workflow_runs']}
request={'ref':'main','inputs':{'record_name':'deploy-2fb09791-d0ca-443f-9c1b-77747c3f3a73.json','record_sha256':'11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50','execute':mode}}
save('request.json',request)
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-13T16:45:00+09:00'),'START_CUTOFF_PASSED_NO_DISPATCH'
r=subprocess.run(['gh','api','repos/321Team/infra-cicd/actions/workflows/app-deploy.yml/dispatches','--method','POST','--input',str(OUT/'request.json')],capture_output=True,timeout=30)
(OUT/'response.stdout').write_bytes(r.stdout);(OUT/'response.stderr').write_bytes(r.stderr)
save('dispatch-receipt.json',{'sent_at_utc':now.isoformat(),'mode':mode,'rc':r.returncode,'automatic_retry':False})
assert r.returncode==0,'DISPATCH_UNCONFIRMED_NO_RETRY'
for attempt in range(15):
    after=gh(endpoint)
    found=[x for x in after['workflow_runs'] if x['id'] not in before_ids and x['head_sha']==source and x['event']=='workflow_dispatch' and x['actor']['login']=='GWONUK']
    if found:
        assert len(found)==1 and found[0]['run_attempt']==1
        save('run.json',found[0]);print(json.dumps({k:found[0][k] for k in ('id','html_url','status','conclusion','head_sha','run_attempt')},ensure_ascii=False));break
    time.sleep(2)
else:raise SystemExit('RUN_DISCOVERY_UNCONFIRMED_NO_REDISPATCH')
