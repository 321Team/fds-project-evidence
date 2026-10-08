"""One-shot read-only clone check; private Compose renderings stay in /root."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time

BASE = Path('/home/server08/harbor/docker-compose.yml')
BASE_SHA = '0a84f57692268335eeedf45411e025d784e520bf749fa3501a3800cdfcb14ef0'

def require(condition, code):
    if not condition:
        raise RuntimeError(code)

def main():
    require(os.geteuid() == 0, 'ROOT_REQUIRED')
    require(socket.gethostname().split('.')[0] == 'harbor01', 'HOST_MISMATCH')
    share = Path(__file__).resolve().parent
    require(str(share) in ('/mnt/hgfs/HBR_NEXT', '/mnt/hbr-next'), 'SHARE_PATH_MISMATCH')
    manifest = json.loads((share / 'SOURCE.json').read_text())
    require(time.time() < manifest['expires_epoch'], 'TRANSFER_EXPIRED')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'PHYSICAL_NIC_PRESENT')
    for name, digest in manifest['files'].items():
        require(Path(name).name == name, 'BAD_SOURCE_NAME')
        source = share / name
        require(source.is_file() and not source.is_symlink(), 'SOURCE_FILE_INVALID')
        require(hashlib.sha256(source.read_bytes()).hexdigest() == digest, 'SOURCE_HASH_MISMATCH')
    require(BASE.is_file() and not BASE.is_symlink(), 'BASE_INVALID')
    require(hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, 'BASE_HASH_CHANGED')
    os.umask(0o077)
    task = Path(tempfile.mkdtemp(prefix='hbr-clone-a1-', dir='/root'))
    for name in manifest['files']:
        (task / name).write_bytes((share / name).read_bytes())
    result = {'stage': 'A1_READONLY', 'started_epoch': time.time(), 'private_results': str(task),
              'source': manifest, 'base_sha256': BASE_SHA, 'commands': [],
              'RUNTIME_APPLY': 'NOT_RUN', 'DOCKER_RESTART': 'NOT_RUN', 'AUTOSTART': 'NOT_TESTED'}
    def run(name, argv):
        with (task / (name + '.stdout')).open('xb') as out, (task / (name + '.stderr')).open('xb') as err:
            try:
                p = subprocess.run(argv, cwd=BASE.parent, env={'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}, stdout=out, stderr=err, timeout=35)
                rc = p.returncode
            except subprocess.TimeoutExpired:
                rc = 124
        result['commands'].append({'name': name, 'argv': argv, 'rc': rc})
        (task / 'execution.json').write_text(json.dumps(result, indent=2) + '\n')
        require(rc == 0, 'COMMAND_FAILED_' + name)
        return task / (name + '.stdout')
    try:
        common = ['docker', 'compose', '--project-directory', str(BASE.parent), '-f', str(BASE)]
        run('base', common + ['config', '--format', 'json', '--no-env-resolution'])
        run('effective', common + ['-f', str(task / 'override.json'), 'config', '--format', 'json', '--no-env-resolution'])
        checked = run('delta', ['python3', str(task / 'checker.py'), '--base-json', str(task / 'base.stdout'), '--effective-json', str(task / 'effective.stdout')])
        # The approved checker emits fixed error codes and selected safe fields.
        result['delta'] = json.loads(checked.read_text())
        observed = task / 'observer.jsonl'
        run('observe', ['python3', str(task / 'observer.py'), 'collect', '--output', str(observed), '--samples', '1', '--expected-host', 'harbor01'])
        summary = run('summary', ['python3', str(task / 'observer.py'), 'summarize', str(observed)])
        result['observer_summary'] = json.loads(summary.read_text())
        result['observer_records'] = [json.loads(line) for line in observed.read_text().splitlines()]
        require(hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, 'BASE_CHANGED_DURING_CHECK')
        result['status'] = 'A1_COLLECTED_REVIEW_REQUIRED'
    except RuntimeError as exc:
        result['status'] = 'STOP'
        result['error_code'] = str(exc)
    result['finished_epoch'] = time.time()
    (task / 'execution.json').write_text(json.dumps(result, indent=2) + '\n')
    # Never export Compose JSON, stderr or environment data.
    raw = (json.dumps(result, indent=2) + '\n').encode()
    with (share / 'A1_RESULT.json').open('xb') as f:
        f.write(raw)
    with (share / 'A1_RESULT.sha256').open('x') as f:
        f.write(hashlib.sha256(raw).hexdigest() + '  A1_RESULT.json\n')
    print(result['status'] + ' PRIVATE=' + str(task))
    return 0 if result['status'] != 'STOP' else 2

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        print('STOP_PRECHECK_INPUT_OR_IO_ERROR; no restart/apply performed')
        raise SystemExit(2)
