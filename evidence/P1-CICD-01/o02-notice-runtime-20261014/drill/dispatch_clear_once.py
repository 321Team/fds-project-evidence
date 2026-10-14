"""Bounded authorized clear observation after the owned trial is terminal."""
import datetime as dt
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prior_ops', HERE.parent/'p1-runner-operations-20261013/ops_api.py')
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)
ops.ROOT = HERE
state = json.loads((HERE/'CURRENT_STATUS.json').read_text('utf-8'))
observed = json.loads((HERE/'LATEST_OBSERVATION.json').read_text('utf-8'))
now = dt.datetime.now(dt.timezone.utc)
assert now < dt.datetime.fromisoformat('2026-10-14T01:35:00+00:00'), 'CLEAR_WINDOW_CLOSED'
assert 0 <= (now-dt.datetime.fromisoformat(observed['at_utc'])).total_seconds() < 60, 'STALE_READ'
assert observed['main_unchanged'] and all(observed['identity'].values())
assert not observed['matching_runner_ids'] and not observed['other_active_regression_ids']
assert not observed['unexpected_regression_execution']
trial = observed['runs']['regression']
assert trial['id'] == 38493795328 and trial['status'] == 'completed' and trial['conclusion'] == 'cancelled'
assert trial['jobs'] and all(j['status']=='completed' for j in trial['jobs'])
assert observed['runs']['warning_notify']['status'] == 'completed'
assert not state['dispatch_state']['clear_notify_requested']
bot = [c for c in observed['new_operator_or_bot_comments'] if c['user']=='github-actions[bot]']
assert bot and bot[-1]['id'] == 6158722178, 'NEW_BOT_RESULT_REQUIRES_REUSE_CHECK'
repo = 'repos/321Team/infra-ansible'
variables = ops.api('clear-variables-before', repo+'/actions/variables?per_page=100')
assert variables['total_count'] == len(variables['variables'])
values = {v['name']:v['value'] for v in variables['variables']}
assert values.get('ANSIBLE_QUEUE_ALERT_ENABLED') == 'true'
assert values.get('ANSIBLE_QUEUE_ALERT_THRESHOLD_MINUTES') == '10'
assert values.get('ANSIBLE_QUEUE_ALERT_RECIPIENTS') == 'supreme33-kr,GWONUK'
before = ops.api('clear-notify-before', repo+'/actions/workflows/ansible-queue-alert.yml/runs?event=workflow_dispatch&per_page=100')
assert before['total_count'] == len(before['workflow_runs'])
assert all(r['status']=='completed' for r in before['workflow_runs'])
assert dt.datetime.now(dt.timezone.utc) < dt.datetime.fromisoformat('2026-10-14T01:35:00+00:00')
claim = {'at_utc':ops.now(),'expected_sha':state['ansible_source_sha'],'purpose':'CLEAR_ONCE',
         'before_ids':[r['id'] for r in before['workflow_runs']],'max_requests':1,
         'terminal_read_prefix':observed['prefix']}
with (HERE/'CLEAR_NOTIFY_DISPATCH.claim.json').open('x',encoding='utf-8') as f:
    json.dump(claim,f,indent=2)
state['dispatch_state']['clear_notify_requested'] = True
state['runtime'] = 'CLEAR_DISPATCH_REQUESTED'
state['updated_at_utc'] = ops.now()
(HERE/'CURRENT_STATUS.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ops.api('clear-notify-dispatch', repo+'/actions/workflows/ansible-queue-alert.yml/dispatches', method='POST',
        body={'ref':'main','inputs':{'notify':True}})
print(json.dumps({'action':'CLEAR_DISPATCH_ACCEPTED','at_utc':ops.now()}))
