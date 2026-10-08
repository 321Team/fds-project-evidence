import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

root = Path(__file__).resolve().parent
base = root/'a3-stop-received'
for line in (base/'SHA256SUMS').read_text().splitlines():
    expected, name = line.split('  ', 1)
    assert hashlib.sha256((base/name).read_bytes()).hexdigest() == expected
r = json.loads((base/'result.json').read_bytes())
p = json.loads((base/'candidate-check-result.json').read_bytes())
obs = [json.loads(line) for line in (base/'observation.jsonl').read_text().splitlines()]
samples = [row for row in obs if row['kind'] == 'sample']
assert len(samples) == 37 and [s['index'] for s in samples] == list(range(37))
assert obs[-1]['kind'] == 'footer' and obs[-1]['samples'] == 37
tz = timezone(timedelta(hours=9))
kst = lambda epoch: datetime.fromtimestamp(epoch, tz).isoformat()
diffs = []
for name, before in p['current'].items():
    after = r['after'][name]
    for key in ('id', 'name', 'service', 'project', 'image', 'restart', 'ports', 'logging', 'mounts'):
        old, new = before[key], after[key]
        if key == 'mounts':
            old, new = [sorted(v, key=lambda x: (x['Destination'], x['Source'])) for v in (old,new)]
        if old != new:
            diffs.append({'service': name, 'field': key})
timeline = []
for sample in samples:
    docker = sample['docker']
    timeline.append({'index': sample['index'], 'kst': sample['observed_at_kst'],
        'docker_error': docker.get('error'), 'listener': sample['listener'].get('value'),
        'running': [row['name'] for row in docker.get('value', []) if row['status']=='running'],
        'healthy': [row['name'] for row in docker.get('value', []) if row['health']=='healthy'],
        'exited': [row['name'] for row in docker.get('value', []) if row['status']=='exited']})
summary = {'source_result_sha256': hashlib.sha256((base/'result.json').read_bytes()).hexdigest(),
    'started_kst': kst(r['started_epoch']), 'finished_kst': kst(r['finished_epoch']),
    't0_kst': kst(r['t0']['epoch']), 'restart_commands': [dict(name=c['name'],rc=c['rc'],started_kst=kst(c['started_epoch']),finished_kst=kst(c['finished_epoch'])) for c in r['commands'] if c['name']=='restart-once'],
    'same_boot': r['boot_before']==r['boot_after'],
    'changed_docker_invocation': r['unit_before']['InvocationID']!=r['unit_after']['InvocationID'],
    'sample_count':len(samples), 'errors':r['errors'], 'postcheck_errors':r['postcheck_errors'],
    'capture_status_counts': {state:sum(v['status']==state for v in r['postcheck_capture'].values()) for state in ('COLLECTED','ERROR')},
    'metadata_difference_excluding_health_status':diffs,
    'all_ten_autostart_within_observed_window':'NOT_ACHIEVED',
    'root_cause':'UNCONFIRMED_PENDING_JOURNAL_AND_STATE_ERROR',
    'timeline':timeline, 'original_status':'STOP_RECOVERY_REQUIRED_UNCHANGED'}
(root/'a3-stop-analysis.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k!='timeline'},indent=2))
print(json.dumps([s for s in timeline if s['index'] in (0,1,2,3,8,36)],indent=2))
