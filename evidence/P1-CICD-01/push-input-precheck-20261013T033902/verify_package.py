"""Offline verification only; no server calls, writes, credentials or dispatch."""
from pathlib import Path
import hashlib, importlib.util, json, sys
P = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name): return json.loads((P / name).read_bytes())
binding = read('SOURCE_BINDING.json')
for row in binding:
    path = P / 'source' / Path(row['path']).name
    raw = path.read_bytes()
    assert sha(path) == row['sha256']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob']
    assert row['commit'] == '2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
r = read('runtime-read/receipt.json')
assert r['rc'] == 0 and r['read_only'] is True
for name, key in [('stdout.json', 'stdout_sha256'), ('stderr.txt', 'stderr_sha256'), ('collector.py', 'collector_sha256')]:
    assert sha(P / 'runtime-read' / name) == r[key]
assert (P / 'runtime-read/stderr.txt').stat().st_size == 0
observed, draft, verified = read('runtime-read/stdout.json'), read('push.draft.json'), read('VERIFICATION.json')
assert observed['historical_provenance'] == 'PASS' and observed['fresh_scan'] is False
assert observed['credential_access'] is False and observed['registry_access'] is False
assert observed['source'] == draft['source']
assert sha(P / 'push.draft.json') == verified['draft_sha256']
assert draft['app_result_sha256'] == observed['files']['result.json']['sha256']
assert draft['build_scan']['scan_result_sha256'] == observed['files']['build-scan/scan/result.json']['sha256']
assert draft['workflow']['commit'] == observed['context']['workflow_sha']
assert draft['workflow']['run_id'] == int(observed['context']['run_id'])
assert draft['workflow']['run_attempt'] == observed['context']['attempt']
assert draft['build_scan']['input_sha256'] == observed['context']['input_sha256']
for name, row in observed['images'].items():
    for key, value in draft['build_scan']['images'][name].items(): assert row['identity'][key] == value
    assert draft['build_scan']['scan'][name] == row['scan']
assert draft['template_only'] is True and draft['push_authorization']['reference'] is None
assert draft['push_authorization']['expires_at'] is None
spec = importlib.util.spec_from_file_location('gate', P / 'source/delivery_gate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.evaluate(draft, 'pre_push') == verified['static_gate']
assert set(verified['static_gate']['reasons']) == {'TEMPLATE_OR_UNCONFIRMED_INPUT', 'DELIVERY_INPUT_NOT_APPROVED'}
assert {'HARBOR_CI_ROBOT_USERNAME','HARBOR_CI_ROBOT_TOKEN'} <= {x['name'] for x in read('github/secrets.json')['secrets']}
manifest = P / 'SHA256SUMS'
files = 0
if manifest.exists():
    for line in manifest.read_text().splitlines():
        digest, rel = line.split('  ', 1)
        assert '..' not in Path(rel).parts and not Path(rel).is_absolute()
        assert sha(P / rel) == digest, rel
        files += 1
print(json.dumps({'OFFLINE_PACKAGE': 'PASS', 'fixed_source_files': len(binding), 'manifest_files': files,
                  'EXPECTED_GATE_BLOCKS': 2, 'historical_provenance': 'PASS',
                  'adapter_execute_false': 'NOT_RUN', 'PUSH': 'NOT_EXECUTED'}))
