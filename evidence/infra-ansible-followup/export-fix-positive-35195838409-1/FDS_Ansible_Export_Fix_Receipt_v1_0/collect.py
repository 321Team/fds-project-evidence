"""Fixed-target, read-only receipt collection. No token issuance or server change."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import socket
import stat
import subprocess
import sys
import tarfile
import tempfile

REPO = '321Team/infra-ansible'
SOURCE = '31895081e30e27481e7c17407047c9454e3b247a'
RUN, ATTEMPT, JOB, RUNNER = 35195838409, 1, 105118736321, 26
RUNNER_NAME = 'ansible-ci-a6b75591ba3d4d38b5a3c3797afd8d37'
PR = 22
BRANCH = 'test/issue-5-export-fix-positive-20260917'
SESSION_END = '2026-09-17T08:24:06.420838+00:00'
LABELS = {'self-hosted', 'Linux', 'X64', 'fds-ci', 'ansible-isolated'}
ARCHIVE_NAME = 'ansible-export-fix-receipt.tar.gz'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')


def check_home(account, host):
    uid = os.getuid()
    if uid < 1000 or os.geteuid() != uid or pwd.getpwuid(uid).pw_name != account:
        raise ValueError('WRONG_LOGIN')
    if socket.gethostname().split('.')[0] != host:
        raise ValueError('WRONG_HOST')
    home = Path(pwd.getpwuid(uid).pw_dir)
    if home != Path('/home') / account:
        raise ValueError('HOME_MISMATCH')
    for p in (home, *home.parents):
        s = p.lstat()
        if not stat.S_ISDIR(s.st_mode) or s.st_uid not in (0, uid) or s.st_mode & 0o022:
            raise ValueError('UNSAFE_HOME')
    if home.stat().st_uid != uid or not os.access(home, os.W_OK | os.X_OK):
        raise ValueError('HOME_NOT_WRITABLE_SEARCHABLE')
    return home


def api(gh, endpoint, path, commands, paginate=False):
    # Call sites supply constants; do not accept arbitrary endpoints or methods.
    command = [gh, 'api', '--hostname', 'github.com', '--method', 'GET',
               '-H', 'Accept: application/vnd.github+json',
               '-H', 'X-GitHub-Api-Version: 2022-11-28', endpoint]
    if paginate:
        command += ['--paginate', '--slurp']
    env = os.environ.copy()
    for k in ('GH_DEBUG', 'GH_FORCE_TTY', 'DEBUG'):
        env.pop(k, None)
    env.update(GH_PROMPT_DISABLED='1', GH_PAGER='cat', LC_ALL='C', NO_COLOR='1')
    item = {'command': command, 'started_at_utc': now(), 'rc': None, 'timed_out': False}
    commands.append(item)
    try:
        with path.open('xb') as out:
            result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=out,
                                    stderr=subprocess.PIPE, timeout=180, env=env)
        item['rc'] = result.returncode
        if result.returncode != 0:
            item['error_code'] = 'GET_FAILED'
            return False
        if path.stat().st_size > 8 * 1024**2:
            item['error_code'] = 'RESPONSE_TOO_LARGE'
            return False
        return True
    except subprocess.TimeoutExpired:
        item.update(timed_out=True, error_code='GET_TIMEOUT')
        return False
    except OSError:
        item['error_code'] = 'GET_IO_ERROR'
        return False
    finally:
        item['ended_at_utc'] = now()
    # No raw stderr, authentication data or temporary redirect URL is exported.


def bind_execution(run, jobs, check):
    try:
        if not (run['id'] == RUN and run['run_attempt'] == ATTEMPT and run['head_sha'] == SOURCE
                and run['repository']['full_name'] == REPO and run['event'] == 'pull_request'
                and run['status'] == 'completed' and run['conclusion'] == 'success'):
            return False
        if not (jobs['total_count'] == len(jobs['jobs']) == 1):
            return False
        j = jobs['jobs'][0]
        if not (j['id'] == JOB and j['run_id'] == RUN and j['run_attempt'] == ATTEMPT
                and j['head_sha'] == SOURCE and j['name'] == 'regression'
                and j['status'] == 'completed' and j['conclusion'] == 'success'
                and j['runner_id'] == RUNNER and j['runner_name'] == RUNNER_NAME
                and set(j['labels']) == LABELS):
            return False
        steps = {s['name']: s for s in j['steps']}
        required = ('Checkout exact source', 'Syntax and both pinned engines',
                    'Preserve result and original logs on success or failure')
        if not all(n in steps and steps[n]['status'] == 'completed'
                   and steps[n]['conclusion'] == 'success' for n in required):
            return False
        return (check['id'] == JOB and check['head_sha'] == SOURCE and check['name'] == 'regression'
                and check['status'] == 'completed' and check['conclusion'] == 'success'
                and check['check_suite']['id'] == run['check_suite_id']
                and check['app']['slug'] == 'github-actions')
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def bind_pr(pr):
    try:
        return (pr['number'] == PR and pr['state'] == 'open' and pr['draft'] is True
                and pr['head']['sha'] == SOURCE and pr['head']['ref'] == BRANCH
                and pr['head']['repo']['full_name'] == REPO
                and pr['base']['repo']['full_name'] == REPO and pr['base']['ref'] == 'main')
    except (KeyError, TypeError, AttributeError):
        return False


def absence(pages):
    try:
        if not isinstance(pages, list) or not pages:
            return {'complete_query': False, 'absent': None}
        if not all(isinstance(p, dict) and type(p.get('total_count')) is int
                   and p['total_count'] >= 0 and isinstance(p.get('runners'), list) for p in pages):
            return {'complete_query': False, 'absent': None}
        rows = [r for p in pages for r in p['runners']]
        if not all(isinstance(r, dict) and type(r.get('id')) is int and r['id'] > 0
                   and isinstance(r.get('name'), str) and r['name'] for r in rows):
            return {'complete_query': False, 'absent': None}
        if len({r['id'] for r in rows}) != len(rows) or not all(p['total_count'] == len(rows) for p in pages):
            return {'complete_query': False, 'absent': None}
        matches = sum(r['id'] == RUNNER or r['name'] == RUNNER_NAME for r in rows)
        return {'complete_query': True, 'absent': matches == 0, 'matching_count': matches,
                'runner_id': RUNNER, 'runner_name': RUNNER_NAME, 'deletion_performed': False}
    except (KeyError, TypeError):
        return {'complete_query': False, 'absent': None}


def collect(home, gh):
    root = Path(tempfile.mkdtemp(prefix='ansible-export-fix-receipt.', dir=home))
    evidence = root / 'evidence'
    evidence.mkdir(mode=0o700)
    record = {'schema': 1, 'started_at_utc': now(), 'hostname': socket.gethostname(),
              'uid': os.getuid(), 'script_sha256': sha(__file__), 'repository': REPO,
              'run_id': RUN, 'attempt': ATTEMPT, 'job_id': JOB, 'source': SOURCE,
              'status': 'COLLECTION_INCOMPLETE', 'commands': [], 'errors': [],
              'token_issuance': False, 'rerun': False, 'server_changes': False,
              'host_cleanup': 'NOT_VERIFIED_BY_MANAGEMENT_COLLECTOR',
              'artifact_download': False, 'artifact_review': 'SEPARATE_EXISTING_REVIEW',
              'independent_approval': 'NOT_GRANTED', 'session_ended_at_utc': SESSION_END}
    definitions = (
        ('pr.json', f'pulls/{PR}', False),
        ('run-attempt1.json', f'actions/runs/{RUN}/attempts/{ATTEMPT}', False),
        ('jobs-attempt1.json', f'actions/runs/{RUN}/attempts/{ATTEMPT}/jobs?per_page=100', False),
        ('check.json', f'check-runs/{JOB}', False),
        ('runner-pages.json', 'actions/runners?per_page=100', True),
    )
    values = {}
    try:
        for name, endpoint, paginate in definitions:
            path = evidence / name
            if api(gh, 'repos/' + REPO + '/' + endpoint, path, record['commands'], paginate):
                try:
                    values[name] = json.loads(path.read_bytes())
                except (ValueError, UnicodeError):
                    record['errors'].append('INVALID_JSON:' + name)
            else:
                record['errors'].append('READ_FAILED:' + name)
        record['execution_bound'] = bind_execution(values.get('run-attempt1.json', {}),
                                                   values.get('jobs-attempt1.json', {}), values.get('check.json', {}))
        record['current_pr_bound'] = bind_pr(values.get('pr.json', {}))
        record['runner_absence'] = absence(values.get('runner-pages.json'))
        record['query_after_session'] = (dt.datetime.fromisoformat(record['started_at_utc'])
                                          >= dt.datetime.fromisoformat(SESSION_END))
        if (not record['errors'] and record['execution_bound'] and record['current_pr_bound']
                and record['query_after_session']
                and record['runner_absence'].get('absent') is True):
            record['status'] = 'COLLECTED_BOUND_REVIEW_REQUIRED'
    except (Exception, KeyboardInterrupt):
        record['errors'].append('COLLECTION_INTERRUPTED_OR_FAILED')
    record['ended_at_utc'] = now()
    rc = 0 if record['status'] == 'COLLECTED_BOUND_REVIEW_REQUIRED' else 1
    write(evidence / 'RESULT.json', record)
    (evidence / 'execution.rc').write_text(str(rc) + '\n')
    paths = sorted(p for p in evidence.iterdir() if p.is_file())
    (evidence / 'SHA256SUMS').write_text(''.join(sha(p) + '  ' + p.name + '\n' for p in paths))
    archive = root / ARCHIVE_NAME
    with tarfile.open(archive, 'w:gz') as t:
        for p in sorted(evidence.iterdir()):
            t.add(p, arcname='evidence/' + p.name, recursive=False)
    Path(str(archive)+'.sha256').write_text(sha(archive) + '  ' + archive.name + '\n')
    print('STATUS=' + record['status'])
    print('HOME_EVIDENCE=' + str(archive))
    print('SCOPE=EXACT_CHECK_AND_RUNNER_REGISTRATION_READ_ONLY')
    return rc


def main():
    os.umask(0o077)
    try:
        if len(sys.argv) != 1:
            raise ValueError('NO_ARGUMENTS_ALLOWED')
        home = check_home('server01_ansible', 'ansible01')
        gh = shutil.which('gh')
        if gh is None:
            raise ValueError('GH_NOT_FOUND')
        return collect(home, gh)
    except (Exception, KeyboardInterrupt):
        # Do not echo input/environment/raw exception data.
        print('STATUS=STOP_LOCAL_PREREQUISITE_OR_EVIDENCE_WRITE_ERROR')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
