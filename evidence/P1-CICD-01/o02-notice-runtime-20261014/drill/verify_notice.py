"""Preserve and verify one actual O02 notice artifact; read-only remote access."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prior_ops', HERE.parent/'p1-runner-operations-20261013/ops_api.py')
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)
ops.ROOT = HERE
state = json.loads((HERE/'CURRENT_STATUS.json').read_text('utf-8'))
kind = sys.argv[1]
assert kind in ('warning_notify', 'clear_notify')
runid = state[kind]['id']
folder = HERE / f'{kind}-{runid}-attempt-1'
folder.mkdir()
ops.ROOT = folder
repo = 'repos/321Team/infra-ansible'
run = ops.api('run', repo+f'/actions/runs/{runid}')
jobs = ops.api('jobs', repo+f'/actions/runs/{runid}/attempts/1/jobs?per_page=100')
artifacts = ops.api('artifacts', repo+f'/actions/runs/{runid}/artifacts?per_page=100')
assert run['status'] == 'completed', 'WAIT_FOR_COMPLETION'
assert artifacts['total_count'] == len(artifacts['artifacts'])
items = [a for a in artifacts['artifacts'] if a['name'] == f'queue-observation-{runid}-1']
assert len(items) == 1
artifact = items[0]
assert not artifact['expired'] and 0 < artifact['size_in_bytes'] < 5*1024*1024
started = ops.now()
cmd = ['gh', 'api', repo+f'/actions/artifacts/{artifact["id"]}/zip']
p = subprocess.run(cmd, capture_output=True, timeout=30)
(folder/'observation.zip').write_bytes(p.stdout)
(folder/'download.stderr.txt').write_bytes(p.stderr)
ziphash = hashlib.sha256(p.stdout).hexdigest()
(folder/'download.receipt.json').write_text(json.dumps({'started_at_utc':started,'ended_at_utc':ops.now(),'command':cmd,'rc':p.returncode,'zip_sha256':ziphash},indent=2)+'\n',encoding='utf-8')
assert p.returncode == 0
assert artifact['digest'] == 'sha256:'+ziphash, 'API_DIGEST_MISMATCH'
with zipfile.ZipFile(io.BytesIO(p.stdout)) as z:
    assert sorted(z.namelist()) == ['queue-observation.json', 'queue-observation.json.sha256']
    assert all(i.file_size < 1024*1024 for i in z.infolist())
    raw = z.read('queue-observation.json')
    sidecar = z.read('queue-observation.json.sha256')
jsonhash = hashlib.sha256(raw).hexdigest()
assert sidecar.decode('utf-8').split() == [jsonhash, 'queue-observation.json'], 'SIDECAR_MISMATCH'
(folder/'queue-observation.json').write_bytes(raw)
(folder/'queue-observation.json.sha256').write_bytes(sidecar)
obs = json.loads(raw)
checks = {'head':run['head_sha']==state['ansible_source_sha'], 'attempt':run['run_attempt']==1,
          'event':run['event']=='workflow_dispatch', 'path':run['path']=='.github/workflows/ansible-queue-alert.yml',
          'run_success':run['conclusion']=='success', 'jobs_complete':jobs['total_count']==len(jobs['jobs']),
          'jobs_expected':{j['name']:j['conclusion'] for j in jobs['jobs']}=={'dry-read':'skipped','notify':'success'},
          'repository':obs['repository']=='321Team/infra-ansible', 'threshold':obs['threshold_minutes']==10,
          'api_digest':True, 'json_sidecar':True}
if kind == 'warning_notify':
    alerts = obs.get('alerts', [])
    checks['expected_warning'] = (obs.get('state')=='ATTENTION' and len(alerts)==1
        and alerts[0]['run_id']==state['regression']['id']
        and alerts[0]['job_id']==state['regression']['job']['id']
        and alerts[0]['reason']=='QUEUED_THRESHOLD_EXCEEDED')
else:
    checks['clear_observation'] = obs.get('state')=='NO_ALERT' and obs.get('alerts')==[]
url = obs.get('notification',{}).get('comment_url')
if url:
    prefix = 'https://github.com/321Team/infra-ansible/issues/61#issuecomment-'
    assert url.startswith(prefix) and url.removeprefix(prefix).isdigit()
    comment = ops.api('bot-comment', repo+'/issues/comments/'+url.removeprefix(prefix))
    checks['bot_identity'] = comment['user']['login']=='github-actions[bot]' and comment['user']['type']=='Bot'
    checks['state_marker'] = comment['body'].startswith('<!-- p1-ansible-queue-alert:v1:'+obs['notification']['state_sha256']+' -->\n')
    checks['recipients'] = '@supreme33-kr' in comment['body'] and '@GWONUK' in comment['body']
result = {'at_utc':ops.now(),'kind':kind,'run_id':runid,'artifact_id':artifact['id'],'zip_sha256':ziphash,
          'json_sha256':jsonhash,'checks':checks,'all_checks_pass':all(checks.values()),
          'observation':obs,'human_receipt':'NOT_INFERRED'}
(folder/'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
