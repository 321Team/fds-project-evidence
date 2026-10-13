"""Attribute the authorized single dispatch and read its current GitHub state."""
import datetime as dt
import json
import pathlib
import subprocess
import tbs_control as control

out=pathlib.Path(__file__).parent
intent=json.loads((out/'DISPATCH_INTENT_NO_RETRY.json').read_text())
auth=json.loads((out/'USER_AUTHORIZATION.json').read_text())
stamp=control.now().strftime('%Y%m%dT%H%M%SZ')
start_file=out/'RUN_START.json'
if start_file.exists():
    run_id=json.loads(start_file.read_text())['run']['id']
    run=control.api(f'repos/{control.REPO}/actions/runs/{run_id}')
else:
    runs=control.api(f'repos/{control.REPO}/actions/workflows/{control.WF}/runs?per_page=10')['workflow_runs']
    new=[r for r in runs if r['id'] not in intent['prior_run_ids']]
    assert len(new)<=1, 'Multiple new runs: attribution required; no retry'
    if not new:
        print(json.dumps({'state':'RUN_NOT_YET_VISIBLE','no_retry':True}));raise SystemExit(0)
    run=new[0];run_id=run['id']
    assert run['event']=='workflow_dispatch' and run['head_branch']=='main'
    assert dt.datetime.fromisoformat(run['created_at'])>=dt.datetime.fromisoformat(intent['at_utc']).replace(microsecond=0)
assert run['head_sha']==auth['workflow_sha'] and run['run_attempt']==1
jobs=control.api(f'repos/{control.REPO}/actions/runs/{run_id}/jobs')
snapshot={'at_utc':control.now().isoformat(),'run':run,'jobs':jobs}
control.save(f'github-snapshot-{stamp}.json',snapshot)
assert len(jobs['jobs'])<=1, 'Unexpected job count'
job=jobs['jobs'][0] if jobs['jobs'] else None
deadline=dt.datetime.fromisoformat(auth['job_start_deadline_kst'])
started=job and job.get('started_at') and job.get('runner_name')=='cicd-runner01' and job.get('status')!='queued'
if started:
    actual=dt.datetime.fromisoformat(job['started_at'])
    within=dt.datetime.fromisoformat(auth['window_start_kst'])<=actual<=deadline
    if not within and run['status']!='completed':
        subprocess.run(['gh','run','cancel',str(run_id),'--repo',control.REPO],check=True)
    assert within, 'Job started outside approved window; no second dispatch'
    if not start_file.exists():control.save('RUN_START.json',snapshot)
elif control.now()>=deadline and run['status']!='completed':
    subprocess.run(['gh','run','cancel',str(run_id),'--repo',control.REPO],check=True)
    print(json.dumps({'run_id':run_id,'state':'START_DEADLINE_CANCELLED','no_retry':True}));raise SystemExit(0)
print(json.dumps({'run_id':run_id,'attempt':run['run_attempt'],'head':run['head_sha'],'status':run['status'],'conclusion':run['conclusion'],'job':None if not job else {'id':job['id'],'status':job['status'],'conclusion':job['conclusion'],'started_at':job['started_at'],'completed_at':job['completed_at']},'url':run['html_url']}))
