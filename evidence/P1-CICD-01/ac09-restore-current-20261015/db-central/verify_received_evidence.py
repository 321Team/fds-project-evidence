"""Local verification of the user's console transcript against fixed AC09 evidence."""
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / 'deliverables/p1-cicd-ac09-preparation-20261015/runtime-1535'
APP = ROOT / 'deliverables/phase1-ac09-app-evidence-20261015/runtime-1535'
sha = lambda data: hashlib.sha256(data).hexdigest()
when = lambda text: dt.datetime.fromisoformat(text.replace('Z', '+00:00'))
lines = (HERE / 'USER_CONSOLE_OUTPUT.txt').read_text(encoding='utf-8').splitlines()
assert len(lines) == 16 and lines[0] == 'AC09_DB_AFTER_RC=0'
assert lines[1:3] == ['db01', 'server08'] and lines[7] == '0'
hashes = dict((line.split('  ', 1)[1], line.split('  ', 1)[0]) for line in lines[9:])
sql = (APP / 'DB_POST_READONLY_PREPARED.sql').read_bytes()
content = {
    'DB_POST_READONLY.sql': sql,
    'host.txt': ('\n'.join(lines[1:3]) + '\n').encode(),
    'start.txt': (lines[3] + '\n').encode(),
    'db-after.jsonl': ('\n'.join(lines[4:7]) + '\n').encode(),
    'db-after.stderr': b'',
    'db-after.rc': (lines[7] + '\n').encode(),
    'end.txt': (lines[8] + '\n').encode(),
}
integrity = {name: {'expected': hashes[name], 'actual': sha(data), 'match': sha(data) == hashes[name]}
             for name, data in content.items()}
assert all(item['match'] for item in integrity.values()), integrity
reconstructed = HERE / 'reconstructed-console-files'
reconstructed.mkdir(exist_ok=False)
for name, data in content.items():
    (reconstructed / name).write_bytes(data)
identity, *phases = [json.loads(line) for line in lines[4:7]]
assert identity['database'] == 'fdsdb' and identity['user'] == 'postgres'
assert identity['transaction_read_only'] == 'on' and identity['timezone'] == 'Asia/Seoul'
assert [p['phase'] for p in phases] == ['R1', 'R2']
fields = {'transaction_id', 'account_id', 'amount', 'currency', 'transaction_type',
          'source_ip', 'occurred_at', 'received_at', 'fds_detected', 'fds_rules',
          'fds_evaluation_skipped'}
results = []
sources = {}
for phase in phases:
    file = RUN / (phase['phase'].lower() + '-post-one/stdout.json')
    raw = file.read_bytes()
    post = json.loads(raw)
    body = base64.b64decode(post['body_b64'], validate=True)
    assert sha(body) == post['body_sha256'] and len(body) == post['body_bytes']
    response = json.loads(body)
    assert post['method'] == 'POST' and post['http'] == 201 and not post['retry']
    assert phase['matched_rows'] == len(phase['rows']) == 1
    row = phase['rows'][0]
    assert set(row) == fields
    checks = {}
    for key in ('account_id', 'amount', 'currency', 'transaction_type', 'source_ip'):
        checks[key] = row[key] == post['payload'][key]
    checks['occurred_at'] = when(row['occurred_at']) == when(post['payload']['occurred_at'])
    for key in ('transaction_id', 'fds_detected', 'fds_evaluation_skipped'):
        checks[key] = type(row[key]) is type(response[key]) and row[key] == response[key]
    canonical_rules = lambda values: sorted(values, key=lambda x: x['rule_id'])
    checks['fds_rules'] = canonical_rules(row['fds_rules']) == canonical_rules(response['fds_rules'])
    assert len(row['fds_rules']) == len({r['rule_id'] for r in row['fds_rules']}) == 4
    assert phase['expected_transaction_id'] == response['transaction_id']
    assert phase['expected_account_id'] == post['payload']['account_id']
    assert all(checks.values()), checks
    received = when(row['received_at'])
    # received_at is DB-only, so report its observation instead of claiming API field equality.
    received_between = when(post['started_utc']) <= received <= when(post['finished_utc'])
    assert received.tzinfo is not None
    results.append({
        'phase': phase['phase'], 'matched_rows': 1,
        'transaction_id': row['transaction_id'], 'input_and_response_fields': checks,
        'received_at': row['received_at'],
        'received_at_within_observed_http_interval': received_between,
        'received_at_basis': 'DB_ONLY_FIELD; interval observation is descriptive, not a new clock or latency criterion',
        'result': 'SAME_ID_DB_ROW_CONTENT_MATCH',
    })
    sources[str(file.relative_to(ROOT)).replace('\\', '/')] = sha(raw)
result = {
    'verified_at_kst': dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),
    'provenance': 'USER_SUPPLIED_DB01_CONSOLE_TRANSCRIPT; LF file reconstruction matches all 7 reported SHA256 values; no new DB connection or SQL execution',
    'console_identity': ['db01', 'server08'], 'database_identity': identity,
    'command_rc': 0, 'stderr_empty_sha_verified': True, 'integrity': integrity,
    'rows': results, 'api_sources_sha256': sources,
    'result': 'DB_POST_ROWS_VERIFIED',
    'db_pre_zero_rows': 'NOT_COLLECTED_NOT_RETROACTIVELY_PROVEN',
    'security_timing': 'UNCHANGED_UNPROVEN_SEC_POST_REVIEW',
    'ac09_acceptance': 'NOT_COMPLETE',
}
(HERE / 'VERIFICATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'result': result['result'], 'hashes_matched': len(integrity), 'rows': results}, ensure_ascii=False))
