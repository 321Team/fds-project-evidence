from pathlib import Path
import hashlib, importlib.util, json

P = Path(__file__).resolve().parent
def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(name, obj): (P / name).write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode())
receipt = json.loads((P / 'runtime-read/receipt.json').read_bytes())
raw = (P / 'runtime-read/stdout.json').read_bytes()
assert receipt['rc'] == 0 and sha(raw) == receipt['stdout_sha256']
assert sha((P / 'runtime-read/collector.py').read_bytes()) == receipt['collector_sha256']
assert sha((P / 'runtime-read/stderr.txt').read_bytes()) == receipt['stderr_sha256']
r = json.loads(raw)
assert r['historical_provenance'] == r['installed_scanner_identity'] == 'PASS'
previous = json.loads((P.parent / 'p1-delivery-runner-20261013/INPUTS.observed.json').read_bytes())
for name, expected in previous['build']['result_hashes'].items():
    if name.endswith('.oci.tar'):
        service = Path(name).name.removesuffix('.oci.tar')
        assert r['images'][service]['identity']['archive_sha256'] == expected
    else:
        assert r['files'][name]['sha256'] == expected
secrets = json.loads((P / 'github/secrets.json').read_bytes())
names = {v['name'] for v in secrets['secrets']}
assert {'HARBOR_CI_ROBOT_USERNAME', 'HARBOR_CI_ROBOT_TOKEN'} <= names
ctx = r['context']
record = {
    'schema': 'P1-CICD-delivery-gate-1', 'template_only': True,
    'status': 'PENDING_EXACT_INPUT_REVIEW_AND_NEW_PUSH_AUTHORIZATION',
    'source': r['source'],
    'workflow': {'repository': '321Team/infra-cicd', 'ref': 'refs/heads/main',
                 'commit': ctx['workflow_sha'], 'run_id': int(ctx['run_id']), 'run_attempt': ctx['attempt']},
    'build_scan': {'result': 'PASS', 'source_commit': r['source']['commit'],
                   'workflow_commit': ctx['workflow_sha'], 'run_id': int(ctx['run_id']),
                   'run_attempt': ctx['attempt'], 'input_sha256': ctx['input_sha256'],
                   'scan_result_sha256': r['files']['build-scan/scan/result.json']['sha256'],
                   'images': {n: {k: row['identity'][k] for k in ('archive_sha256', 'manifest_digest', 'config_digest')}
                              for n, row in r['images'].items()},
                   'scan': {n: row['scan'] for n, row in r['images'].items()}},
    'harbor': {'endpoint': 'https://10.1.93.54', 'runner_tls_trust': 'PASS', 'if09_ac02': 'PASS',
               'handoff_reference': 'https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947371286',
               'credential_reference': 'actions-secret:HARBOR_CI_ROBOT_USERNAME/HARBOR_CI_ROBOT_TOKEN',
               'repositories': {n: '10.1.93.54/fds/' + n for n in r['images']}},
    'app_result_sha256': r['files']['result.json']['sha256'],
    'source_evidence_directory': 'FDS_CICD_AppWorkflow.57rithja',
    'push_authorization': {'workflow_sha': r['code_commit'], 'reference': None, 'expires_at': None}
}
save('push.draft.json', record)
spec = importlib.util.spec_from_file_location('approved_delivery_gate', P / 'source/delivery_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
verdict = gate.evaluate(record, 'pre_push')
assert verdict['decision'] == 'BLOCK'
assert set(verdict['reasons']) == {'TEMPLATE_OR_UNCONFIRMED_INPUT', 'DELIVERY_INPUT_NOT_APPROVED'}
verification = {
    'result': 'PROVENANCE_VERIFIED_EXPECTED_APPROVAL_BLOCK',
    'draft_sha256': sha((P / 'push.draft.json').read_bytes()),
    'runtime_read': {'rc': 0, 'started_at_utc': r['started_at_utc'], 'finished_at_utc': r['finished_at_utc'],
                     'archive_count': 2, 'report_count': 2, 'receipt_count': 3,
                     'historical_provenance': 'PASS', 'installed_scanner_identity': 'PASS'},
    'static_gate': verdict,
    'current_workflow_commit': r['code_commit'],
    'secret_names_present': sorted(names),
    'robot': {'name': 'robot$push', 'basis': 'USER_REPORTED_IN_THIS_CHAT',
              'valid_token_possession': 'USER_REPORTED', 'secret_content_read': False,
              'current_permissions': 'NOT_OBSERVED', 'current_disabled': 'NOT_OBSERVED', 'current_expiry': None,
              'historical_expiry_hint_only': '2026-10-18T17:16:00+09:00'},
    'harbor_basis': {
        'if09_ac02': {'basis': 'HISTORICAL_HARBOR_AC02_PASS_NOT_FRESH_ROBOT_OR_SEC_ACCEPTANCE',
                     'reference': record['harbor']['handoff_reference'], 'at_kst': '2026-10-02T16:10:00+09:00'},
        'runner_tls_trust': {'basis': 'REUSED_20261013_0143_PYTHON_HTTPS_NOT_SKOPEO_AUTH',
                             'reference': 'https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6128729026'}},
    'authority': {'requested': 'NEW_PUSH_INPUT_PREPARATION_AND_PRECHECK',
                  'actual_push_authorized': False, 'lead_reply_is_required_gate': False},
    'adapter_execute_false': 'NOT_RUN_REQUIRES_APPROVED_EXACT_RECORD',
    'runner_record_placed': False, 'fresh_scan': 'NOT_RUN', 'push': 'NOT_EXECUTED',
    'deploy': 'NOT_EXECUTED', 'delivery_gate': 'NOT_VERIFIED', 'phase2': False
}
save('VERIFICATION.json', verification)
save('DISPATCH.pending.json', {'ref': 'main', 'inputs': {'record_name': None, 'record_sha256': None, 'execute': False},
                              'dispatchable': False, 'reason': 'APPROVED_EXACT_RECORD_NOT_YET_FINALIZED'})
print(json.dumps({'draft_sha256': verification['draft_sha256'], 'gate': verdict['reasons'],
                  'historical_provenance': 'PASS', 'adapter_validation': 'NOT_RUN'}))
