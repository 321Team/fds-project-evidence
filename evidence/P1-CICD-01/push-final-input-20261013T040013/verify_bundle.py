"""Read-only local consistency check. Never activates input or contacts a host."""
from pathlib import Path
import base64, hashlib, json, sys
P = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n): return json.loads((P / n).read_bytes())
plan, pending, auth = read('ACTIVATION_PLAN.json'), read('push.pending.json'), read('USER_AUTHORIZATION.json')
assert sha(P / 'EXECUTION_SCOPE.md') == auth['execution_scope_sha256']
assert auth['reply'] == '일괄 허용 — 해당 창·동시 변경 배제·Secret 2개 회수'
assert sha(P / 'push.pending.json') == plan['pending_sha256']
assert pending['template_only'] is True
assert pending['status'] == 'PENDING_EXACT_INPUT_REVIEW_AND_NEW_PUSH_AUTHORIZATION'
comment = read('USER_DECISION_COMMENT.json')
assert pending['push_authorization']['reference'] == plan['user_execution_authorization'] == comment['html_url']
assert comment['user']['login'] == 'GWONUK'
assert pending['push_authorization']['expires_at'] == auth['expires_at'] == '2026-10-13T09:00:00+09:00'
assert plan['latest_execution_job_start'] == '2026-10-13T07:15:00+09:00'
assert plan['target_file_materialized'] is False and plan['runner_record_placed'] is False
changes = plan['changes_after_independent_review_only']
assert [x['pointer'] for x in changes] == ['/template_only','/status']
target = json.loads(json.dumps(pending))
for row in changes:
    key = row['pointer'][1:]
    assert target[key] == row['before']
    target[key] = row['after']
raw = (json.dumps(target,ensure_ascii=False,indent=2)+'\n').encode()
assert hashlib.sha256(raw).hexdigest() == plan['target_sha256'] == '28ae13b5dee1f16c1fb866eeaaf7984cc4e8286739d7f8da255ab8f02aef665d'
old = read('previous-draft.json')
expected = json.loads(json.dumps(old))
expected['push_authorization']['reference'] = comment['html_url']
expected['push_authorization']['expires_at'] = auth['expires_at']
assert pending == expected
assert sha(P / 'previous-draft.json') == 'a00999626803967016ec5a6f35b0283b88465d86d223d16e28e5e68f3c7e4141'
receipt = read('robot-metadata/receipt.json')
assert receipt['rc'] == receipt['observation']['rc'] == 0
assert sha(P / 'robot-metadata/robot_metadata_read.py') == receipt['source_sha256']
assert receipt['observation']['read_only'] is True and receipt['observation']['credential_fields_selected'] is False
assert receipt['observation']['before'] == receipt['observation']['after']
for row in read('GITHUB_RECEIPTS.json'):
    assert sha(P / 'github' / (row['name']+'.json')) == row['sha256']
    if row['name'].startswith('workflow-'):
        item = read('github/' + row['name'] + '.json')
        b = base64.b64decode(item['content'])
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == item['sha']
for name, mode in [('DISPATCH.validate.json',False),('DISPATCH.execute.json',True)]:
    d = read(name)
    assert d == {'ref':'main','inputs':{'record_name':plan['target_filename'],'record_sha256':plan['target_sha256'],'execute':mode}}
sealed = 0
if (P / 'SHA256SUMS').exists():
    for row in (P/'SHA256SUMS').read_text().splitlines():
        digest, name = row.split('  ',1)
        assert '..' not in Path(name).parts and not Path(name).is_absolute()
        assert sha(P/name) == digest
        sealed += 1
print(json.dumps({'STATIC':'PASS','target_sha256':plan['target_sha256'],'sealed_files':sealed,
    'USER_AUTHORIZATION':'RECEIVED','INDEPENDENT_INPUT_REVIEW':'PENDING','RUNTIME':'NOT_RUN'}))
