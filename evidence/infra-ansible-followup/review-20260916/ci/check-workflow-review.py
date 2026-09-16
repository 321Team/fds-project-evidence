"""Local model of this template's string conditions; not a GitHub Actions run."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import yaml

repo, out = map(Path, sys.argv[1:])
job = yaml.safe_load((repo / 'docs/ci/ansible-regression.workflow.yml').read_text())['jobs']['regression']
fallback = re.fullmatch(r"\$\{\{ fromJSON\(vars\.ANSIBLE_CI_RUNNER_LABELS \|\| '([^']+)'\) \}\}", job['runs-on']).group(1)
labels = '["self-hosted","linux","ansible-isolated"]'
cases = [
    ('disabled-unset', '', '', 'pull_request', '321Team/infra-ansible', False, False),
    ('enabled-unset', 'true', '', 'pull_request', '321Team/infra-ansible', False, False),
    ('disabled-configured', 'false', labels, 'pull_request', '321Team/infra-ansible', False, False),
    ('same-repo', 'true', labels, 'pull_request', '321Team/infra-ansible', True, False),
    ('fork', 'true', labels, 'pull_request', 'fork/infra-ansible', False, False),
    ('manual', 'true', labels, 'workflow_dispatch', '', True, False),
    ('malformed-labels', 'true', 'not-json', 'pull_request', '321Team/infra-ansible', True, True),
]
results = []
allowed = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.Compare, ast.Eq, ast.NotEq, ast.Constant)
for name, enabled, runner_labels, event, head_repo, expected_gate, expected_error in cases:
    values = {'vars.ANSIBLE_CI_ENABLED': enabled, 'vars.ANSIBLE_CI_RUNNER_LABELS': runner_labels,
              'github.event_name': event, 'github.event.pull_request.head.repo.full_name': head_repo,
              'github.repository': '321Team/infra-ansible'}
    expression = job['if'].replace('&&', 'and').replace('||', 'or')
    expression = re.sub(r'(?:vars|github)(?:\.[A-Za-z_]+)+', lambda m: repr(values[m.group()]), expression)
    tree = ast.parse(expression, mode='eval')
    assert all(isinstance(n, allowed) for n in ast.walk(tree))
    gate = eval(compile(tree, '<workflow condition model>', 'eval'), {'__builtins__': {}})
    error, selector = False, None
    try:
        selector = json.loads(runner_labels or fallback)
    except json.JSONDecodeError:
        error = True
    passed = gate == expected_gate and error == expected_error
    if not error:
        passed = passed and isinstance(selector, list) and bool(selector) and all(isinstance(s, str) and s for s in selector)
    results.append(dict(case=name, expected_gate=expected_gate, model_gate=gate,
                        expected_json_error=expected_error, json_error=error, selector=selector, passed=passed))
record = dict(status='PASS' if all(x['passed'] for x in results) else 'FAIL',
              scope='YAML parse and local string-condition/JSON model; GitHub dispatch/skip/config validation NOT RUN',
              source_commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),
              source_dirty=bool(subprocess.check_output(['git','-C',str(repo),'status','--porcelain'])),
              job_if=job['if'], runs_on=job['runs-on'], cases=results)
out.write_text(json.dumps(record, indent=2)+'\n')
print(record['status'], len(results), record['source_commit'], record['scope'])
sys.exit(0 if record['status']=='PASS' else 1)
