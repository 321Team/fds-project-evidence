#!/usr/bin/env python3
"""Materialize exact fetched Git blobs; execute local-only existing tests."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
REPO = BASE / 'candidate'
RESULTS = BASE / 'results'
PYTHON = sys.executable

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify():
    rows = []
    data = json.loads((BASE / 'source-input.json').read_text())
    for entry in data['entries']:
        p = REPO / entry['path']
        b = p.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
        mode = '100755' if p.stat().st_mode & 0o111 else '100644'
        assert blob == entry['sha'] and mode == entry['mode'], entry['path']
        rows.append({'path':entry['path'], 'git_blob':blob, 'mode':mode, 'sha256':digest(b)})
    return rows

def materialize():
    REPO.mkdir(mode=0o700)
    RESULTS.mkdir(mode=0o700)
    data = json.loads((BASE / 'source-input.json').read_text())
    for entry in data['entries']:
        relative = Path(entry['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        b = entry['content'].encode()
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == entry['sha'], entry['path']
        p = REPO / relative
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(b)
        p.chmod(0o755 if entry['mode'] == '100755' else 0o644)
    report = {'heads':data['heads'], 'files':verify(), 'active_workflows':list(map(str,REPO.glob('.github/workflows/*')))}
    (RESULTS/'SOURCE_BINDING.json').write_text(json.dumps(report,indent=2)+'\n')

def environment():
    # No inherited GitHub, cloud, proxy, Python or Ansible credentials/settings.
    tmp = BASE/'temporary'
    tmp.mkdir(exist_ok=True,mode=0o700)
    return {'PATH':os.environ['PATH'], 'LANG':'C.UTF-8', 'LC_ALL':'C.UTF-8',
            'TMPDIR':str(tmp), 'GIT_CONFIG_NOSYSTEM':'1', 'GIT_CONFIG_GLOBAL':'/dev/null',
            'GIT_TERMINAL_PROMPT':'0', 'PYTHONDONTWRITEBYTECODE':'1'}

def run_one(item):
    label, path, expected = item
    cmd = [PYTHON,'-I','-B',str(BASE/'offline_suite.py'),str(REPO),path]
    start = time.monotonic()
    p = subprocess.run(cmd,cwd=REPO,env=environment(),capture_output=True,timeout=120)
    (RESULTS/(label+'.stdout.log')).write_bytes(p.stdout)
    (RESULTS/(label+'.stderr.log')).write_bytes(p.stderr)
    found = re.search(rb'Ran (\d+) tests?',p.stderr)
    return {'suite':label,'path':path,'expected_tests':expected,'observed_tests':int(found[1]) if found else None,
            'rc':p.returncode,'seconds':round(time.monotonic()-start,4),
            'passed':p.returncode == 0 and found is not None and int(found[1]) == expected}

if __name__ == '__main__':
    materialize()
    suites=[('ci-57','DISCOVER',57),('runner-37','tools/ansible-runner/test-kit.py',37),
            ('registration-13','tools/ansible-runner/test-registration.py',13),
            ('ipc-7','tools/ansible-runner/test-ipc.py',7),
            ('admin-22','tools/ansible-admin-token/test-admin-token.py',22),
            ('input-20','tools/ansible-runner-input/test_safe_input.py',20)]
    # Isolated interpreters prevent identically-named common/container modules colliding.
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        result=list(pool.map(run_one,suites))
    verify()
    (RESULTS/'EXISTING_SUITES.json').write_text(json.dumps({'suites':result,'source_unchanged':True,
        'scope':'local unit/subprocess/mock only; no Ansible engine/Podman/GitHub execution'},indent=2)+'\n')
    print(json.dumps(result,indent=2))

