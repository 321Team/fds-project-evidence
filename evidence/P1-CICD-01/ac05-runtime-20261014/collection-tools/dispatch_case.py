"""Dispatch exactly one previously scoped case after fresh, fail-closed checks."""
import datetime, hashlib, importlib.util, json, pathlib, subprocess, sys
OUT=pathlib.Path(__file__).resolve().parent
REPO=OUT.parent.parent/'phase1-work-20261013/cicd-scan-negative-20261014'
SHA='65ae4fd3b274efc04c3cb686b41cc99fb07383b8'
case=sys.argv[1]; assert case in ('vulnerability','scanner-error')
now=lambda:datetime.datetime.now(datetime.timezone.utc)
def api(endpoint):
    p=subprocess.run(['gh','api',endpoint],capture_output=True,timeout=30)
    assert p.returncode==0,(endpoint,p.returncode)
    return json.loads(p.stdout)
def load(name):return json.loads((OUT/name).read_bytes())
def stamp(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
assert not (OUT/(case+'-dispatch-intent.json')).exists(), 'Never repeat an uncertain dispatch'
sp=importlib.util.spec_from_file_location('compare',REPO/'tools/trivy/compare_scan_observations.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
before=load(case+'-before-app/stdout.json');m.identity(before)
runner=load(case+'-before-runner/stdout.json');assert runner['readiness']=='READY'
for label in (case+'-before-app',case+'-before-runner'):
    receipt=load(label+'/receipt.json'); assert receipt['rc']==0
    for f,key in [('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256'),('collector.py','source_sha256')]:
        assert hashlib.sha256((OUT/label/f).read_bytes()).hexdigest()==receipt[key]
assert 0 <= (now()-stamp(before['finished_at_utc'])).total_seconds() < 120
assert 0 <= (now()-stamp(runner['finished_at_utc'])).total_seconds() < 120
release=json.loads((OUT.parent/'p1-runner83-execution-20261014-r2/WINDOW_RELEASE.json').read_bytes())
assert release['host_window_released'] is True and release['ci']=='PASS'
assert release['registered_runners']==release['containers']==0 and not any(release[k] for k in ('process_present','packet_present','incoming_present'))
if case=='scanner-error':
    first=load('VERIFIED-vulnerability.json');assert first['classification']=='EXPECTED_FAILURE_OBSERVED' and first['IMAGE_PRESERVATION']=='OBSERVED_UNCHANGED'
main=api('repos/321Team/infra-cicd/commits/main');assert main['sha']==SHA
pr=api('repos/321Team/infra-cicd/pulls/81');assert pr['merged'] and pr['merge_commit_sha']==SHA
ci=api('repos/321Team/infra-cicd/actions/runs/38529245862');assert ci['head_sha']==SHA and ci['conclusion']=='success'
reviews=api('repos/321Team/infra-cicd/pulls/81/reviews?per_page=100')
assert any(r['state']=='APPROVED' and r['commit_id']=='884c3d99ba865d0e08f58951dbd750cb4e8589c6' and r['user']['login']=='hayeounglee' for r in reviews)
for repo in ('infra-cicd','infra-ansible'):
    for status in ('queued','in_progress'):
        runs=api(f'repos/321Team/{repo}/actions/runs?status={status}&per_page=100')
        assert runs['total_count']==0,(repo,status,runs['total_count'])
runners=api('repos/321Team/infra-cicd/actions/runners')['runners']
selected=[r for r in runners if r['name']=='cicd-runner01'];assert len(selected)==1 and selected[0]['status']=='online' and selected[0]['busy'] is False
endpoint='repos/321Team/infra-cicd/actions/workflows/app-scan-negative.yml'
existing=api(endpoint+'/runs?per_page=100')['workflow_runs']
intent={'started_at_utc':now().isoformat(),'case':case,'workflow_sha':SHA,'attempt':1,
        'prior_run_ids':[r['id'] for r in existing], 'request':{'ref':'main','inputs':{'case':case}},
        'before_app_sha256':hashlib.sha256((OUT/(case+'-before-app/stdout.json')).read_bytes()).hexdigest(),
        'scope':'User AC05 two-case sequential execution after H4 and PR83 host release; no Push/Deploy'}
with (OUT/(case+'-dispatch-intent.json')).open('x',encoding='utf-8') as f:json.dump(intent,f,indent=2)
request=OUT/(case+'-dispatch-request.json');request.write_text(json.dumps(intent['request']),encoding='utf-8')
p=subprocess.run(['gh','api','--method','POST',endpoint+'/dispatches','--input',str(request)],capture_output=True,timeout=30)
(OUT/(case+'-dispatch.stdout')).write_bytes(p.stdout);(OUT/(case+'-dispatch.stderr')).write_bytes(p.stderr)
receipt={'completed_at_utc':now().isoformat(),'rc':p.returncode,'case':case,'workflow_sha':SHA,'automatic_retry':False}
(OUT/(case+'-dispatch-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
assert p.returncode==0,'Dispatch outcome uncertain/failed; inspect before doing anything else'
print(json.dumps(receipt),flush=True)
