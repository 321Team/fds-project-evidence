"""Read-only GitHub observation for the authorized O02 round; no dispatch/cancel."""
import concurrent.futures
import datetime as dt
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('existing_ops', HERE.parent / 'p1-runner-operations-20261013/ops_api.py')
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)
ops.ROOT = HERE
state = json.loads((HERE / 'CURRENT_STATUS.json').read_text('utf-8'))
prefix = 'observe-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
repo = 'repos/321Team/infra-ansible'
paths = {'main': repo + '/commits/main', 'runners': repo + '/actions/runners?per_page=100',
         'issue': repo + '/issues/61', 'comments': repo + '/issues/61/comments?per_page=100'}
for status in ('queued', 'in_progress', 'requested', 'waiting', 'pending'):
    paths['active-' + status] = repo + '/actions/workflows/ansible-regression.yml/runs?status=' + status + '&per_page=100'
for kind in ('regression', 'warning_notify', 'clear_notify'):
    item = state.get(kind)
    if item:
        rid = item['id']
        paths[kind] = repo + f'/actions/runs/{rid}'
        paths[kind + '-jobs'] = repo + f'/actions/runs/{rid}/attempts/1/jobs?per_page=100'
values = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(ops.api, prefix + '-' + k, path): k for k, path in paths.items()}
    for future in concurrent.futures.as_completed(futures):
        values[futures[future]] = future.result()
assert values['runners']['total_count'] == len(values['runners']['runners']), 'INCOMPLETE_RUNNERS'
assert values['issue']['comments'] == len(values['comments']), 'INCOMPLETE_COMMENTS'
active = {}
for status in ('queued', 'in_progress', 'requested', 'waiting', 'pending'):
    obj = values['active-' + status]
    assert obj['total_count'] == len(obj['workflow_runs']), 'INCOMPLETE_ACTIVE_RUNS'
    for run in obj['workflow_runs']:
        active[run['id']] = run
identity = {}
runs = {}
for kind in ('regression', 'warning_notify', 'clear_notify'):
    if kind not in values:
        continue
    run, obj = values[kind], values[kind + '-jobs']
    assert obj['total_count'] == len(obj['jobs']), 'INCOMPLETE_JOBS'
    expected_path = '.github/workflows/ansible-regression.yml' if kind == 'regression' else '.github/workflows/ansible-queue-alert.yml'
    identity[kind] = (run['id'] == state[kind]['id'] and run['run_attempt'] == 1
                      and run['head_sha'] == state['ansible_source_sha'] and run['event'] == 'workflow_dispatch'
                      and run['actor']['login'] == 'GWONUK' and run['path'] == expected_path)
    runs[kind] = {k: run[k] for k in ('id', 'status', 'conclusion', 'created_at', 'head_sha', 'html_url')}
    runs[kind]['jobs'] = [{k: j.get(k) for k in ('id', 'name', 'status', 'conclusion', 'created_at', 'started_at', 'completed_at', 'runner_id', 'runner_name', 'labels')} for j in obj['jobs']]
owned = state.get('regression', {}).get('id')
cutoff = '2026-10-14T01:00:00Z'
comments = [{k: c[k] for k in ('id', 'created_at', 'html_url', 'body')} | {'user': c['user']['login']}
            for c in values['comments'] if c['created_at'] >= cutoff and c['user']['login'] in ('supreme33-kr', 'github-actions[bot]')]
labels = {'self-hosted', 'Linux', 'X64', 'fds-ci', 'ansible-isolated'}
matching = [r['id'] for r in values['runners']['runners'] if labels <= {x['name'] for x in r['labels']}]
jobs = runs.get('regression', {}).get('jobs', [])
unexpected = any(j['status'] == 'in_progress' or j.get('runner_id') not in (None, 0) for j in jobs)
result = {'at_utc': ops.now(), 'prefix': prefix, 'main_unchanged': values['main']['sha'] == state['ansible_source_sha'],
          'identity': identity, 'runs': runs, 'matching_runner_ids': matching,
          'other_active_regression_ids': [rid for rid in active if rid != owned],
          'unexpected_regression_execution': unexpected, 'new_operator_or_bot_comments': comments}
for filename in (prefix + '-summary.json', 'LATEST_OBSERVATION.json'):
    (HERE / filename).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
