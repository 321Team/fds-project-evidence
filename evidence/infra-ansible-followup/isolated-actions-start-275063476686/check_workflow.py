"""Local security-contract checks; not the GitHub scheduler or runtime."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'ansible-ci-activation-review'
sys.path.insert(0, str(SOURCE / 'tests'))
spec = importlib.util.spec_from_file_location('existing_gate_model', SOURCE / 'tests/test_ci_regression.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
data = yaml.load((ROOT / 'ansible-isolated-acceptance.yml').read_text(), Loader=yaml.BaseLoader)
template = yaml.load((SOURCE / 'docs/ci/ansible-regression.workflow.yml').read_text(), Loader=yaml.BaseLoader)
REPO = '321Team/infra-ansible'
POS = 'test/issue-5-isolated-positive-20260917'
NEG = 'test/issue-5-isolated-negative-20260917'
values = {'github.event_name': 'pull_request', 'github.repository': REPO,
          'github.event.pull_request.head.repo.full_name': REPO,
          'github.event.pull_request.base.ref': 'main', 'github.event.pull_request.head.ref': POS}
cases = [('positive', {}, True), ('negative', {'github.event.pull_request.head.ref': NEG}, True)]
for event in ['push', 'pull_request_target', 'workflow_dispatch', 'workflow_call', 'unknown', '']:
    cases.append(('event-' + event, {'github.event_name': event}, False))
for name, key, value in [
        ('fork', 'github.event.pull_request.head.repo.full_name', 'other/infra-ansible'),
        ('missing-head-repo', 'github.event.pull_request.head.repo.full_name', ''),
        ('other-repository', 'github.repository', '321Team/infra-cicd'),
        ('other-base', 'github.event.pull_request.base.ref', 'develop'),
        ('missing-base', 'github.event.pull_request.base.ref', ''),
        ('ordinary-pr', 'github.event.pull_request.head.ref', 'fix/issue-5-ci-regression'),
        ('similar-name', 'github.event.pull_request.head.ref', POS + '-other'),
        ('old-window', 'github.event.pull_request.head.ref', POS.replace('20260917', '20260916')),
        ('missing-ref', 'github.event.pull_request.head.ref', '')]:
    cases.append((name, {key: value}, False))
cases.append(('case-insensitive', {k: v.upper() for k, v in values.items()}, True))

def validate(workflow):
    assert workflow['on'] == {'pull_request': {'branches': ['main']}}
    assert workflow['permissions'] == {'contents': 'read'}
    assert workflow['concurrency']['cancel-in-progress'] == 'true'
    assert set(workflow['jobs']) == {'regression'}
    job = workflow['jobs']['regression']
    assert job['runs-on'] == ['self-hosted', 'Linux', 'X64', 'fds-ci', 'ansible-isolated']
    assert job['timeout-minutes'] == '30'
    assert set(job) == {'if', 'runs-on', 'timeout-minutes', 'env', 'steps'}
    assert job['env'] == {**template['jobs']['regression']['env'], 'CI_WHEEL_DIR': ''}
    assert job['steps'] == template['jobs']['regression']['steps']
    for name, delta, expected in cases:
        assert model.workflow_gate_model(job['if'], values | delta) == expected, name

validate(data)
mutations = []
for name in ['allow-any-ref', 'allow-fork', 'drop-isolation-label', 'write-token', 'manual-trigger']:
    altered = copy.deepcopy(data)
    job = altered['jobs']['regression']
    if name == 'allow-any-ref':
        job['if'] = "github.event_name == 'pull_request'"
    elif name == 'allow-fork':
        job['if'] = job['if'].replace("github.event.pull_request.head.repo.full_name == '321Team/infra-ansible' &&", '')
    elif name == 'drop-isolation-label':
        job['runs-on'].remove('ansible-isolated')
    elif name == 'write-token':
        altered['permissions']['contents'] = 'write'
    else:
        altered['on']['workflow_dispatch'] = None
    try:
        validate(altered)
    except AssertionError:
        mutations.append({'mutation': name, 'rejected': True})
    else:
        raise AssertionError('Mutation survived: ' + name)
record = {'status': 'PASS_LOCAL_CONTRACT', 'scope': 'static YAML and local condition model only',
          'cases': [{'case': name, 'expected': expected,
                     'observed': model.workflow_gate_model(data['jobs']['regression']['if'], values | delta)}
                    for name, delta, expected in cases],
          'mutations': mutations, 'unchanged_execution_steps': True,
          'github_actions': 'NOT_RUN at validation time'}
(ROOT / 'workflow-validation.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': record['status'], 'scenarios': len(cases), 'mutations_rejected': len(mutations)}))
