"""Record bounded GitHub operations; never read credentials into output."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import io
import zipfile

ROOT = Path(__file__).resolve().parent
REPO = '321Team/infra-ansible'
EXPECTED = 'ec15dcbd022942add199a8f4718c0f88105e880e'

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def api(name, endpoint, *, method='GET', body=None):
    dest = ROOT / (name + '.response.json')
    if dest.exists():
        raise RuntimeError('Receipt already exists: ' + name)
    cmd = ['gh', 'api', '--method', method, endpoint]
    if body is not None:
        request = ROOT / (name + '.request.json')
        request.write_text(json.dumps(body, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        cmd += ['--input', str(request)]
    started = now()
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    dest.write_bytes(p.stdout)
    (ROOT / (name+'.stderr.txt')).write_bytes(p.stderr)
    (ROOT / (name+'.receipt.json')).write_text(json.dumps({
        'started_at_utc': started, 'ended_at_utc': now(), 'method': method,
        'endpoint': endpoint, 'rc': p.returncode,
        'response_sha256': hashlib.sha256(p.stdout).hexdigest()}, indent=2)+'\n', encoding='utf-8')
    if p.returncode:
        raise RuntimeError('GitHub request failed; inspect receipt: '+name)
    return json.loads(p.stdout) if p.stdout.strip() else None

def prepare():
    head = api('prepare-main', f'repos/{REPO}/git/ref/heads/main')['object']['sha']
    if head != EXPECTED:
        raise RuntimeError('Main changed')
    existing = api('variables-before', f'repos/{REPO}/actions/variables?per_page=100')
    if existing['total_count'] > len(existing['variables']):
        raise RuntimeError('Incomplete variables list')
    current = {v['name']:v['value'] for v in existing['variables']}
    target = {
        'ANSIBLE_QUEUE_ALERT_ENABLED': 'false',
        'ANSIBLE_QUEUE_ALERT_THRESHOLD_MINUTES': '10',
        'ANSIBLE_QUEUE_ALERT_RECIPIENTS': 'supreme33-kr,GWONUK',
    }
    for key, value in target.items():
        endpoint = f'repos/{REPO}/actions/variables'
        method = 'POST'
        if key in current:
            endpoint += '/' + key
            method = 'PATCH'
        api('prepare-'+key, endpoint, method=method, body={'name':key, 'value':value})
    observed = api('variables-disabled-readback', f'repos/{REPO}/actions/variables?per_page=100')
    values = {v['name']:v['value'] for v in observed['variables']}
    if not all(values.get(k)==v for k,v in target.items()):
        raise RuntimeError('Variable readback mismatch')
    prior = api('dry-runs-before', f'repos/{REPO}/actions/workflows/ansible-queue-alert.yml/runs?event=workflow_dispatch&per_page=30')
    if any(r['status'] != 'completed' for r in prior['workflow_runs']):
        raise RuntimeError('Existing manual alert observation still active')
    api('dispatch-dry-read', f'repos/{REPO}/actions/workflows/ansible-queue-alert.yml/dispatches',
        method='POST', body={'ref':'main','inputs':{'notify':False}})
    print(json.dumps({'status':'DISPATCHED_DRY_READ','head':head,'variables':target}))

def poll(label):
    r = api(label, f'repos/{REPO}/actions/workflows/ansible-queue-alert.yml/runs?event=workflow_dispatch&per_page=30')
    before = json.loads((ROOT/'dry-runs-before.response.json').read_text())
    ids = {x['id'] for x in before['workflow_runs']}
    started = json.loads((ROOT/'dispatch-dry-read.receipt.json').read_text())['started_at_utc']
    cutoff = dt.datetime.fromisoformat(started) - dt.timedelta(seconds=2)
    hits = [x for x in r['workflow_runs'] if x['id'] not in ids and x['head_sha']==EXPECTED
            and x['event']=='workflow_dispatch' and dt.datetime.fromisoformat(x['created_at'].replace('Z','+00:00'))>=cutoff]
    if len(hits)!=1:
        print(json.dumps({'status':'NOT_UNIQUELY_IDENTIFIED','hits':len(hits)}))
        return
    run = hits[0]
    (ROOT/'DRY_RUN_ID.json').write_text(json.dumps({k:run[k] for k in ('id','head_sha','run_attempt','html_url')}, indent=2)+'\n')
    print(json.dumps({k:run[k] for k in ('id','status','conclusion','head_sha','created_at','html_url')}))
    if run['status']=='completed':
        jobs = api(label+'-jobs', f'repos/{REPO}/actions/runs/{run["id"]}/attempts/1/jobs?per_page=100')
        artifacts = api(label+'-artifacts', f'repos/{REPO}/actions/runs/{run["id"]}/artifacts?per_page=100')
        print(json.dumps({'jobs':[{k:x.get(k) for k in ('id','name','conclusion','started_at','completed_at')} for x in jobs['jobs']],
                          'artifacts':[{k:x.get(k) for k in ('id','name','digest','size_in_bytes')} for x in artifacts['artifacts']]}))

def verify_dry():
    run = json.loads((ROOT/'DRY_RUN_ID.json').read_text())
    jobs = json.loads((ROOT/'dry-poll-2-jobs.response.json').read_text())['jobs']
    assert len(jobs)==2 and {x['name']:x['conclusion'] for x in jobs}=={'dry-read':'success','notify':'skipped'}
    artifacts = json.loads((ROOT/'dry-poll-2-artifacts.response.json').read_text())['artifacts']
    assert len(artifacts)==1
    a=artifacts[0]
    assert a['name']==f'queue-observation-{run["id"]}-1' and not a['expired']
    dest=ROOT/'dry-observation.zip'
    assert not dest.exists()
    p=subprocess.run(['gh','api',f'repos/{REPO}/actions/artifacts/{a["id"]}/zip'],capture_output=True,timeout=90)
    dest.write_bytes(p.stdout)
    assert p.returncode==0
    digest=hashlib.sha256(p.stdout).hexdigest()
    assert a['digest']=='sha256:'+digest
    with zipfile.ZipFile(io.BytesIO(p.stdout)) as z:
        assert sorted(z.namelist())==['queue-observation.json','queue-observation.json.sha256']
        raw=z.read('queue-observation.json')
        sha=z.read('queue-observation.json.sha256')
        assert sha.decode().split()[0]==hashlib.sha256(raw).hexdigest()
        for name,data in [('queue-observation.json',raw),('queue-observation.json.sha256',sha)]:
            with (ROOT/name).open('xb') as f: f.write(data)
    observation=json.loads(raw)
    assert observation['repository']==REPO and observation['threshold_minutes']==10
    assert observation['notification']['status']=='DRY_RUN_NO_COMMENT' and observation['state']!='READ_ERROR'
    result={'verified_at_utc':now(),'run':run,'job_results':{x['name']:x['conclusion'] for x in jobs},
            'artifact_id':a['id'],'archive_sha256':digest,'json_sha256':hashlib.sha256(raw).hexdigest(),
            'observation':observation,'actual_comment_delivery':'NOT_TESTED','human_receipt':'NOT_CONFIRMED'}
    (ROOT/'DRY_VERIFIED.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True))

def activate():
    verified=json.loads((ROOT/'DRY_VERIFIED.json').read_text())
    assert verified['observation']['notification']['status']=='DRY_RUN_NO_COMMENT'
    adopted=json.loads((ROOT/'ADOPTED_INPUTS.json').read_text(encoding='utf-8'))
    assert adopted['other_ci_reserve_minutes']==500 and adopted['approval_source']=='user reply in current chat'
    head=api('activation-main',f'repos/{REPO}/git/ref/heads/main')['object']['sha']
    assert head==EXPECTED
    variables=api('activation-variables-before',f'repos/{REPO}/actions/variables?per_page=100')
    values={v['name']:v['value'] for v in variables['variables']}
    assert values['ANSIBLE_QUEUE_ALERT_ENABLED']=='false'
    assert values['ANSIBLE_QUEUE_ALERT_THRESHOLD_MINUTES']=='10'
    assert values['ANSIBLE_QUEUE_ALERT_RECIPIENTS']=='supreme33-kr,GWONUK'
    api('activate-enabled',f'repos/{REPO}/actions/variables/ANSIBLE_QUEUE_ALERT_ENABLED',method='PATCH',
        body={'name':'ANSIBLE_QUEUE_ALERT_ENABLED','value':'true'})
    after=api('activation-variables-readback',f'repos/{REPO}/actions/variables?per_page=100')
    observed={v['name']:v['value'] for v in after['variables']}
    target=dict(values);target['ANSIBLE_QUEUE_ALERT_ENABLED']='true'
    assert observed==target
    result={'observed_at_utc':now(),'head':head,'enabled':True,'threshold_minutes':10,
            'recipients':['supreme33-kr','GWONUK'],'schedule_kst':'09:07-23:37 every 30 minutes',
            'reserve_minutes':500,'reserve_enforcement':'manual billing read and stop; not an automatic GitHub minute limit',
            'actual_notice_and_receipt':'PENDING_NEXT_BUSINESS_NEEDED_QUEUE','o02':'PRACTICAL_COMPONENT_MET_ALERT_ACCEPTANCE_PENDING'}
    (ROOT/'ACTIVATION_RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))

if __name__ == '__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='poll': poll(sys.argv[2])
    elif sys.argv[1]=='verify-dry': verify_dry()
    elif sys.argv[1]=='activate': activate()
    else: raise SystemExit('Unknown operation')
