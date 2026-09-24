"""Local-only diagnostic driver; calls the candidate's unchanged syntax_gate."""
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'source'
SHA = 'c6ba5f87711acc3eeeba12c13c72cedd09d178f8'
WHEELS = Path('/workspace/scratch/d7770f5e34f6/ansible-ci-linux-1/wheels')
OUT = BASE / 'results'
RUNTIME = BASE / 'runtime'

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def verify_source(root, selected):
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    expected = {e['path'] for e in selected['files']}
    assert actual == expected
    for entry in selected['files']:
        p = root / entry['path']
        assert not p.is_symlink()
        raw = p.read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == entry['sha']
        assert p.stat().st_mode & 0o777 == int(entry['mode'][-3:], 8)

def main():
    selected = json.loads((BASE / 'selected-tree.json').read_text())
    assert selected['source_commit'] == SHA
    verify_source(SOURCE, selected)
    OUT.mkdir(exist_ok=False)
    RUNTIME.mkdir(exist_ok=False)
    shutil.copytree(SOURCE, RUNTIME / 'repo')
    verify_source(RUNTIME / 'repo', selected)
    spec = importlib.util.spec_from_file_location('candidate_ci', SOURCE / 'tools/run-ansible-ci.py')
    ci = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ci)
    kit = ci.kit
    kit.target_host()
    lock = kit.lock_data((SOURCE / kit.LOCK).read_bytes())
    record = {'schema_version': 1, 'status': 'FAIL', 'scope': 'LOCAL_STATIC_SYNTAX_ONLY',
              'source_commit': SHA, 'source_snapshot': 'selected 54 files verified against GitHub tree; not a full Git checkout',
              'syntax_gate_blob': '8eb183d2080ba37d1f266b29ae45d0b20a14d55d',
              'started_at': now(), 'python': sys.version, 'platform': platform.platform(),
              'syntax': [], 'production_apply': False, 'operational_engine_transition': False,
              'github_actions_executed': False, 'fixture_tests_executed': False}
    try:
        kit.verify_wheels(lock, WHEELS)
        record['wheels_verified'] = len(lock['wheels'])
        definition = ci.plan(SOURCE, SHA)
        record['plan'] = definition
        (OUT / 'PLAN.json').write_bytes(kit.encoded(definition))
        env = kit.environment()
        for engine, pins in lock['engines'].items():
            venv = RUNTIME / ('venv-' + engine)
            kit.logged([sys.executable, '-I', '-m', 'venv', venv], BASE, env, OUT / ('install-' + engine + '-venv'))
            python = venv / 'bin/python'
            installer = OUT / ('installer-' + engine + '.lock')
            requirements = OUT / ('requirements-' + engine + '.lock')
            installer.write_bytes(kit.lock_text(lock, lock['installer']))
            requirements.write_bytes(kit.lock_text(lock, pins))
            command = [python, '-I', '-m', 'pip', '--isolated', 'install', '--no-user', '--prefix', venv,
                       '--no-index', '--no-cache-dir', '--only-binary=:all:', '--require-hashes', '--find-links', WHEELS]
            kit.logged([*command, '--no-deps', '-r', installer], BASE, env, OUT / ('install-' + engine + '-pip'))
            kit.logged([*command, '-r', requirements], BASE, env, OUT / ('install-' + engine + '-packages'))
            kit.logged([python, '-I', '-m', 'pip', 'check'], BASE, env, OUT / ('install-' + engine + '-check'))
            kit.logged([python.parent / 'ansible-playbook', '--version'], BASE, env, OUT / ('engine-' + engine + '-version'))
        ci.syntax_gate(RUNTIME, OUT, definition['syntax_playbooks'], definition['engines'], record['syntax'])
        expected = {(e, p) for e in definition['engines'] for p in definition['syntax_playbooks']}
        actual = {(r['engine'], r['playbook']) for r in record['syntax']}
        assert len(record['syntax']) == len(expected) and actual == expected
        verify_source(SOURCE, selected)
        verify_source(RUNTIME / 'repo', selected)
        record['status'] = 'PASS_LOCAL_SYNTAX'
        record['source_unchanged_after'] = True
    except Exception as exc:
        record['error_type'] = type(exc).__name__
        record['error'] = str(exc)
    finally:
        record['finished_at'] = now()
        (OUT / 'LOCAL_SYNTAX_RESULT.json').write_bytes(kit.encoded(record))
        files = [p for p in sorted(OUT.rglob('*')) if p.is_file()]
        (OUT / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(OUT).as_posix() + '\n' for p in files))
    print(json.dumps({'status': record['status'], 'syntax_count': len(record['syntax']),
                      'wheels_verified': record.get('wheels_verified'), 'error': record.get('error')}, indent=2), flush=True)
    return 0 if record['status'] == 'PASS_LOCAL_SYNTAX' else 1

if __name__ == '__main__':
    raise SystemExit(main())
