"""GET-only exact-target preflight. Token issuance is a later shell step."""
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


class Stop(Exception):
    pass


def require(ok, code):
    if not ok:
        raise Stop(code)


def exact_int(value, expected):
    return type(value) is int and value == expected


def unique_object(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'DUPLICATE_JSON_KEY')
        result[k] = v
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def validate(e, pr, run, jobs, queued, active):
    require(exact_int(pr['number'], e['pr']) and pr['state'] == 'open' and pr['draft'] is True
            and pr['head']['sha'] == e['source'] and pr['head']['ref'] == e['branch']
            and pr['head']['repo']['full_name'] == e['repository']
            and pr['base']['ref'] == 'main' and pr['base']['repo']['full_name'] == e['repository'], 'PR_CHANGED')
    require(exact_int(run['id'], e['run']) and exact_int(run['run_attempt'], e['attempt'])
            and run['repository']['full_name'] == e['repository']
            and run['head_repository']['full_name'] == e['repository']
            and run['head_sha'] == e['source'] and run['head_branch'] == e['branch']
            and run['event'] == 'pull_request' and run['path'] == e['workflow_path']
            and run['status'] == 'queued' and run['conclusion'] is None, 'RUN_CHANGED')
    require(type(jobs['jobs']) is list and exact_int(jobs['total_count'], 1) and len(jobs['jobs']) == 1,
            'JOBS_INCOMPLETE_OR_CHANGED')
    job = jobs['jobs'][0]
    require(exact_int(job['id'], e['job']) and exact_int(job['run_id'], e['run'])
            and exact_int(job['run_attempt'], e['attempt']) and job['head_sha'] == e['source']
            and job['head_branch'] == e['branch'] and job['name'] == 'regression'
            and job['status'] == 'queued' and job['conclusion'] is None
            and job['check_run_url'] == 'https://api.github.com/repos/' + e['repository'] + '/check-runs/' + str(e['job'])
            and (job['runner_id'] is None or exact_int(job['runner_id'], 0))
            and job['runner_name'] in (None, '') and type(job['labels']) is list
            and len(job['labels']) == len(e['labels']) and set(job['labels']) == set(e['labels']), 'JOB_CHANGED')
    require(type(queued['workflow_runs']) is list and exact_int(queued['total_count'], 1)
            and len(queued['workflow_runs']) == 1, 'COMPETING_OR_INCOMPLETE_QUEUED')
    q = queued['workflow_runs'][0]
    require(exact_int(q['id'], e['run']) and exact_int(q['run_attempt'], e['attempt'])
            and q['head_sha'] == e['source'] and q['head_branch'] == e['branch']
            and q['status'] == 'queued' and q['conclusion'] is None, 'QUEUED_TARGET_CHANGED')
    require(exact_int(active['total_count'], 0) and active['workflow_runs'] == [], 'COMPETING_OR_INCOMPLETE_ACTIVE')


def collect(e, folder):
    gh = shutil.which('gh')
    require(gh is not None, 'GH_MISSING')
    base = 'repos/' + e['repository']
    paths = [('pr', base + '/pulls/' + str(e['pr'])),
             ('run', base + '/actions/runs/' + str(e['run'])),
             ('jobs', base + '/actions/runs/' + str(e['run']) + '/attempts/' + str(e['attempt']) + '/jobs?per_page=100'),
             ('queued', base + '/actions/runs?status=queued&per_page=100'),
             ('active', base + '/actions/runs?status=in_progress&per_page=100')]
    env = os.environ.copy()
    for key in ('GH_DEBUG', 'GH_FORCE_TTY'):
        env.pop(key, None)
    env.update(GH_PROMPT_DISABLED='1', GH_PAGER='cat', LC_ALL='C')
    values = []
    for name, endpoint in paths:
        result = subprocess.run([gh, 'api', '--hostname', 'github.com', '--method', 'GET',
                                 '-H', 'Accept: application/vnd.github+json',
                                 '-H', 'X-GitHub-Api-Version: 2022-11-28', endpoint],
                                stdin=subprocess.DEVNULL, capture_output=True, timeout=60, env=env)
        require(result.returncode == 0, 'GET_' + name.upper() + '_FAILED')
        require(len(result.stdout) <= 4 * 1024 * 1024, 'GET_RESPONSE_TOO_LARGE')
        value = decode(result.stdout)
        require(type(value) is dict, 'GET_OBJECT_REQUIRED')
        (folder / (name + '.json')).write_bytes(result.stdout)
        values.append(value)
    validate(e, *values)


def main():
    folder = Path(sys.argv[1])
    expected = decode((Path(__file__).resolve().parent / 'EXPECTED.json').read_bytes())
    report = {'status': 'FAIL_PREFLIGHT', 'run': expected['run'], 'attempt': expected['attempt'],
              'job': expected['job'], 'source': expected['source'], 'token_issuance_started_by_preflight': False,
              'started_at': dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        collect(expected, folder)
        report['status'] = 'PASS_EXPORT_FIX_QUEUED_SOURCE'
    except Stop as exc:
        report['error'] = str(exc)
    except Exception as exc:
        report['error_type'] = type(exc).__name__
    report['finished_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    (folder / 'PREFLIGHT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('STATUS=' + report['status'])
    if report['status'] != 'PASS_EXPORT_FIX_QUEUED_SOURCE':
        print('STOP: target changed, incomplete query, or competing run; do not issue token', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
