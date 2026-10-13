"""Read-only verification of the approved window amendment and exact input delta."""
from pathlib import Path
from datetime import datetime
import hashlib, json, sys
P=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
OLD=Path(sys.argv[2]) if len(sys.argv)>2 else P.parent/'p1-push-final-input-20261013'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
w=read(P/'WINDOW_CHANGE.json'); p=read(P/'push.pending.json'); a=read(P/'ACTIVATION_PLAN.json')
old=read(OLD/'push.pending.json'); oa=read(OLD/'ACTIVATION_PLAN.json')
assert sha(OLD/'push.pending.json')==w['previous_pending_sha256']
expected=json.loads(json.dumps(old))
expected['push_authorization']['reference']=w['user_authorization_reference']
expected['push_authorization']['expires_at']='2026-10-13T12:00:00+09:00'
assert p==expected
assert a['changes_after_independent_review_only']==oa['changes_after_independent_review_only']
assert a['workflow_sha']==oa['workflow_sha']
assert sha(P/'push.pending.json')==a['pending_sha256']
assert p['template_only'] is True and p['status'].startswith('PENDING_')
assert a['latest_execution_job_start']==w['latest_execution_job_start']=='2026-10-13T10:00:00+09:00'
assert a['expires_at']==w['expires_at']==p['push_authorization']['expires_at']=='2026-10-13T12:00:00+09:00'
assert (datetime.fromisoformat(a['expires_at'])-datetime.fromisoformat(a['latest_execution_job_start'])).total_seconds()==7200
assert sha(P/'EXECUTION_SCOPE.md')==w['execution_scope_sha256']
c=read(P/'WINDOW_DECISION_COMMENT.json')
assert c['html_url']==a['user_execution_authorization']==w['user_authorization_reference'] and c['user']['login']=='GWONUK'
target=json.loads(json.dumps(p))
for x in a['changes_after_independent_review_only']:
    key=x['pointer'][1:]; assert target[key]==x['before']; target[key]=x['after']
raw=(json.dumps(target,ensure_ascii=False,indent=2)+'\n').encode()
assert hashlib.sha256(raw).hexdigest()==a['target_sha256']==w['target_sha256']=='13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89'
for filename,mode in [('DISPATCH.validate.json',False),('DISPATCH.execute.json',True)]:
    assert read(P/filename)=={'ref':'main','inputs':{'record_name':'push-20261013-window1200.json','record_sha256':a['target_sha256'],'execute':mode}}
assert a['target_file_materialized'] is False and a['runner_record_placed'] is False
count=0
if (P/'SHA256SUMS').exists():
    for line in (P/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert '..' not in Path(name).parts and not Path(name).is_absolute()
        assert sha(P/name)==digest
        count+=1
print(json.dumps({'STATIC':'PASS','input_delta':'authorization reference and expiry only','target_sha256':a['target_sha256'],
    'latest_start':'10:00 KST','expiry':'12:00 KST','job_budget_minutes':90,'cleanup_margin_minutes':30,
    'sealed_files':count,'input_review':'PENDING','runtime':'NOT_RUN'}))
