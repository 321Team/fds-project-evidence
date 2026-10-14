"""Verify this sealed round from the original receipts, not only its summary."""
import hashlib, json, pathlib, re
root = pathlib.Path(__file__).resolve().parent
if str(root).startswith(('C:', 'c:')): root = pathlib.Path('\\\\?\\'+str(root))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(path): return json.loads((root/path).read_text(encoding='utf-8'))
count = 0
for row in (root/'SHA256SUMS').read_text().splitlines():
    h, name = row.split('  ',1)
    assert re.fullmatch('[0-9a-f]{64}',h) and not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts
    assert sha(root/name) == h, name
    count += 1
metadata = load('COLLECTION_METADATA.json')
assert len(metadata['files']) == 66
for name,item in metadata['files'].items():
    p = root/'originals'/name
    assert sha(p) == item['sha256'] and p.stat().st_size == item['bytes']
app = load('originals/result.json'); build = load('originals/build-scan/result.json')
assert app['build_result_sha256'] == sha(root/'originals/build-scan/result.json')
assert app['handoff_sha256'] == sha(root/'originals/handoff.json')
for folder,receipt in (('',app),('build-scan/',build)):
    assert (root/'originals'/folder/'SHA256SUMS').read_text().strip() == sha(root/'originals'/folder/'result.json')+'  result.json'
    for step in receipt['steps']: assert sha(root/'originals'/folder/(step['name']+'.log')) == step['log_sha256']
assert app['context']['run_id'] == '38490368352' and app['context']['attempt'] == 1
assert app['context']['workflow_sha'] == '7171b0a3d636c3a15c78131b89bec4739cb6f49b'
assert app['APP_WORKFLOW'] == build['BUILD_SCAN'] == 'FAIL'
assert app['NEGATIVE_UNIT_PROBE'] == build['NEGATIVE_UNIT_PROBE'] == 'EXPECTED_FAILURE_OBSERVED'
assert next(x for x in build['steps'] if x['name'] == 'unit-negative-start')['exit_code'] == 1
assert next(x for x in build['steps'] if x['name'] == 'fds-engine-unit-0')['exit_code'] == 0
assert re.search(r'\b16 passed in [0-9.]+s\b',(root/'originals/build-scan/fds-engine-unit-0.log').read_text())
failure = (root/'originals/build-scan/unit-negative-start.log').read_text()
assert all(x in failure for x in ('P1_CICD_INTENTIONAL_UNIT_FAILURE','Ran 1 test','FAILED (failures=1)'))
assert not any('-contract-' in x['name'] or x['name'].endswith(('-build','-save')) for x in build['steps'])
assert build['images'] == {} and build['unit_negative']['cleanup'] == 'REMOVED'
assert all(metadata['absence'].values()) and metadata['workers'] == []
cid = build['unit_negative']['container_id']
for name in ('identity','cleanup-identity'):
    identity = load('originals/build-scan/unit-negative-'+name+'.log')
    assert identity['id'] == cid and identity['name'] == identity['owner']
for name in ('create','remove'): assert (root/('originals/build-scan/unit-negative-'+name+'.log')).read_text().strip() == cid
assert not (root/'originals/build-scan/unit-negative-removed.log').read_bytes().strip()
def items(data,kind): return {i['metadata']['name']:i for q in data['queries'] if q['kind'] == kind for i in q['items']}
pre = load('collection/pre-app/stdout.json'); post = load('collection/post-app/stdout.json')
for kind in ('deployments','pods','services','endpointslices'):
    before, after = items(pre,kind), items(post,kind)
    assert set(before) == set(after)
    for name,a in before.items():
        b = after[name]
        if kind == 'deployments':
            assert all(a[k] == b[k] for k in ('spec_sha256','replicas','containers','status'))
            assert all(a['metadata'][k] == b['metadata'][k] for k in ('uid','generation'))
            assert a['status']['readyReplicas'] == 3
        elif kind == 'pods':
            assert a['metadata']['uid'] == b['metadata']['uid'] and a['statuses'] == b['statuses'] and all(c['ready'] for c in b['statuses'])
        else: assert a == b
assert len(items(pre,'deployments')) == 2 and len(items(pre,'pods')) == 6
run = load('github/run.json')
assert run['id'] == 38490368352 and run['run_attempt'] == 1 and run['head_sha'] == app['context']['workflow_sha'] and run['conclusion'] == 'failure'
print(json.dumps({'manifest_files':count,'original_files':66,'runtime':'EXPECTED_FAILURE_OBSERVED','deployments_unchanged':2,'pods_unchanged':6,'independent_review':'NOT_PERFORMED_BY_THIS_SCRIPT'}))
