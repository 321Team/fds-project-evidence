"""One dispatch after exact approval, source CI, and bounded fresh read checks."""
import base64, datetime as dt, hashlib, json, pathlib, subprocess, sys
OUT = pathlib.Path(__file__).parent
ROOT = OUT.parent.parent
REPO = '321Team/infra-cicd'
SHA = '7171b0a3d636c3a15c78131b89bec4739cb6f49b'
HEAD = 'd0031e183406104368f4fd7855ec0453d1063ad4'
WF = 'app-unit-negative.yml'
TREE = ROOT/'phase1-work-20261013/cicd-unit-negative-20261014'
def now(): return dt.datetime.now(dt.timezone.utc)
def save(name, data):
    with (OUT/name).open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
def api(path):
    return json.loads(subprocess.check_output(['gh','api',path],timeout=35))
def digest(raw): return hashlib.sha256(raw).hexdigest()
def load(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def check():
    main = api('repos/'+REPO+'/commits/main'); assert main['sha'] == SHA, 'MAIN_CHANGED'
    pr = api('repos/'+REPO+'/pulls/79')
    assert pr['merged'] and pr['head']['sha'] == HEAD and pr['merge_commit_sha'] == SHA
    reviews = api('repos/'+REPO+'/pulls/79/reviews')
    latest = {}
    for r in reviews: latest[r['user']['login']] = r
    assert latest['hayeounglee']['state'] == 'APPROVED' and latest['hayeounglee']['commit_id'] == HEAD
    ci = api('repos/'+REPO+'/actions/runs/38489765233')
    assert ci['head_sha'] == SHA and ci['status'] == 'completed' and ci['conclusion'] == 'success'
    runners = api('repos/'+REPO+'/actions/runners')['runners']
    runner, = [r for r in runners if r['name'] == 'cicd-runner01']
    assert runner['status'] == 'online' and runner['busy'] is False
    assert {'self-hosted','Linux','X64','p1-cicd','onprem','podman'} <= {l['name'] for l in runner['labels']}
    runs = api('repos/'+REPO+'/actions/runs?per_page=100')['workflow_runs']
    assert all(r['status'] == 'completed' for r in runs), 'ACTIVE_RUN'
    negative = api('repos/'+REPO+'/actions/workflows/'+WF+'/runs?per_page=100')['workflow_runs']
    secret = api('repos/'+REPO+'/actions/secrets/CICD_APP_SOURCE_READ_TOKEN')
    assert secret['updated_at'] == '2026-10-13T11:03:38Z'
    for path in ('config/app-build-scan.json', '.github/workflows/'+WF):
        obj = api('repos/'+REPO+'/contents/'+path+'?ref='+SHA)
        # Git bytes, not Windows worktree newline conversion.
        local = subprocess.check_output(['git','-C',str(TREE),'show',HEAD+':'+path])
        assert base64.b64decode(obj['content']) == local
        if path.startswith('config/'):
            assert digest(local) == '72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3'
    return {'as_of_utc':now().isoformat(),'main':main,'pr79':pr,'reviews':reviews,'source_ci':ci,'runner':runner,'recent_runs':runs,'prior_negative_run_ids':[r['id'] for r in negative], 'source_secret_metadata':secret}
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'prepare':
        save('USER_AUTHORIZATION.json', {'recorded_at_utc':now().isoformat(),'user_request':'리뷰 확인 후 차단사항 없으면 병합하고 착수','context':'PR79 독립 리뷰/CI 후 병합 및 고정 Unit 실패 시험 새 1회','workflow_sha':SHA,'max_new_runs':1,'push_deploy_authorized':False,'new_token_authorized':False,'observation':'Workflow 30 minute timeout; immediate result and app post-state collection; no rerun'})
        for attempt in (1,2):
            data = api('repos/'+REPO+'/actions/runs/38489765233/attempts/'+str(attempt))
            save('main-ci-attempt'+str(attempt)+'.json',data)
            p = subprocess.run(['gh','run','view','38489765233','--repo',REPO,'--attempt',str(attempt),'--log'],capture_output=True,timeout=45)
            assert p.returncode == 0
            (OUT/('main-ci-attempt'+str(attempt)+'.log')).write_bytes(p.stdout)
        save('MERGE_REVIEW_CHECK.json', check())
        print('PREPARED')
    elif mode == 'dispatch':
        assert not (OUT/'DISPATCH_INTENT_NO_RETRY.json').exists(), 'RUN_QUOTA_CONSUMED'
        auth = load('USER_AUTHORIZATION.json')
        assert auth['workflow_sha'] == SHA and auth['max_new_runs'] == 1 and auth['push_deploy_authorized'] is False
        assert load('builder-read/stdout.json')['python313_present_executable'] is True
        app = load('pre-app/stdout.json')
        assert (now()-dt.datetime.fromisoformat(app['finished_at_utc'])).total_seconds() < 600, 'APP_PRESTATE_STALE'
        deployments = next(q for q in app['queries'] if q['kind'] == 'deployments')['items']
        for item in deployments:
            name = item['metadata']['name']
            if name not in ('fds-engine','transaction-api'): continue
            expected = {'fds-engine':'0a1d36ae1fda7513b69fa3d1df7ca91983c05770f44df0ebc940c516f8d1faf3','transaction-api':'b6b4048d5288a42ee0be5fa3fdd3f2ef82c7659687c0adb9ed61a19d7b8a563a'}[name]
            assert item['spec_sha256'] == expected and item['replicas'] == 3 and item['status']['readyReplicas'] == 3
        assert {d['metadata']['name'] for d in deployments} == {'fds-engine','transaction-api'}
        runner = load('pre-runner/stdout.json')
        assert runner['worker_count'] == 0 and runner['harbor']['tls_verified'] and runner['harbor']['status'] == 'healthy'
        data = check(); save('DISPATCH_GITHUB_CHECK.json',data)
        subprocess.run([sys.executable,'-B',str(OUT/'collect.py'),'fresh','dispatch-runner'],check=True,timeout=60)
        state = load('dispatch-runner/stdout.json')
        assert state['ready'] and (now()-dt.datetime.fromisoformat(state['finished_at_utc'])).total_seconds() < 150
        assert api('repos/'+REPO+'/commits/main')['sha'] == SHA
        runs = api('repos/'+REPO+'/actions/runs?per_page=100')['workflow_runs']
        assert all(r['status'] == 'completed' for r in runs)
        save('DISPATCH_INTENT_NO_RETRY.json', {'at_utc':now().isoformat(),'sha':SHA,'workflow':WF,'quota_consumed_on_attempt':True,'prior_run_ids':data['prior_negative_run_ids']})
        p = subprocess.run(['gh','workflow','run',WF,'--repo',REPO,'--ref','main'],capture_output=True,timeout=35)
        response = {'at_utc':now().isoformat(),'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
        save('DISPATCH_RESPONSE.json',response); print(json.dumps(response))
    else: raise SystemExit('Unsupported mode')
