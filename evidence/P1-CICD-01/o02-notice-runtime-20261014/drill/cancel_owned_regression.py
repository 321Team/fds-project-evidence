"""Normal cancellation of the single already-authorized O02 trial Run only."""
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
rid = state['regression']['id']
assert rid == 38493795328 and rid in state['dispatch_state']['owned_run_ids']
assert state['execution_authorization'] == 'AUTHORIZED_ONCE_BY_USER'
prefix = 'precancel-' + dt.datetime.now(dt.timezone.utc).strftime('%H%M%S%f')
endpoint = f'repos/321Team/infra-ansible/actions/runs/{rid}'
run = ops.api(prefix+'-run', endpoint)
jobs = ops.api(prefix+'-jobs', endpoint+'/attempts/1/jobs?per_page=100')
assert (run['id'] == rid and run['run_attempt'] == 1 and run['actor']['login'] == 'GWONUK'
        and run['event'] == 'workflow_dispatch' and run['path'] == '.github/workflows/ansible-regression.yml'
        and run['head_sha'] == state['ansible_source_sha'])
assert jobs['total_count'] == len(jobs['jobs'])
if run['status'] == 'completed':
    print(json.dumps({'action':'ALREADY_TERMINAL','run_id':rid,'conclusion':run['conclusion']}))
else:
    claim = {'at_utc':ops.now(),'run_id':rid,'attempt':1,'expected_sha':run['head_sha'],
             'action':'NORMAL_CANCEL','max_requests':1,'pre_read_prefix':prefix}
    with (HERE/'REGRESSION_CANCEL.claim.json').open('x',encoding='utf-8') as f:
        json.dump(claim,f,indent=2)
    state['regression_cancel'] = claim | {'status':'REQUEST_INTENT_SAVED'}
    state['runtime'] = 'REGRESSION_CANCEL_REQUESTED'
    state['updated_at_utc'] = ops.now()
    (HERE/'CURRENT_STATUS.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ops.api('regression-cancel', endpoint+'/cancel', method='POST')
    state['regression_cancel']['status'] = 'ACCEPTED_TERMINAL_NOT_YET_CONFIRMED'
    state['updated_at_utc'] = ops.now()
    (HERE/'CURRENT_STATUS.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'action':'CANCEL_ACCEPTED','run_id':rid,'at_utc':ops.now()}))
