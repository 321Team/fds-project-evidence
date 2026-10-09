"""Export completed recovery files only; no Docker/service/network queries."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import time

SHARE = Path('/mnt/hbr-recovery-result')
SOURCE = '2178a40b948ccc87ee00b3aad29f0b6c4b7054ac4485f0cd588d75d46b46cb0c'
EXPECTED_WORK = '/root/hbr-app-recovery-ik0dm4a1'
SAFE_NAMES = {'state', 'selinux', 'docker-unit', 'guard-active', 'ac04', 'profile-engine',
              'profile-compose', 'profile-security', 'profile-enforcing', 'profile-labels', 'volume'}
APPS = {'postgresql', 'redis', 'registry', 'registryctl', 'core', 'portal', 'jobservice', 'trivy-adapter', 'proxy'}


def require(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    for parent in path.parents:
        st = parent.lstat()
        require(stat.S_ISDIR(st.st_mode) and st.st_uid == 0 and not st.st_mode & 0o022, 'UNTRUSTED_PARENT')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        st = os.fstat(stream.fileno())
        require(stat.S_ISREG(st.st_mode) and st.st_uid == 0 and not st.st_mode & 0o022
                and st.st_size < 32 * 1024 * 1024, 'UNTRUSTED_FILE')
        return stream.read()


def inventory(work):
    metadata = []
    for path in sorted(work.iterdir()):
        # The reviewed runner imports trial.py with bytecode caching enabled.
        # Only this derived, non-symlink directory is excluded; originals stay strict.
        if path.name == '__pycache__' and path.is_dir() and not path.is_symlink():
            metadata.append({'file': path.name, 'status': 'EXCLUDED_DERIVED_PYTHON_CACHE'})
            continue
        require(path.is_file() and not path.is_symlink(), 'UNEXPECTED_WORK_ENTRY')
        data = read(path)
        metadata.append({'file': path.name, 'bytes': len(data), 'sha256': sha(data)})
    return metadata


def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_USER')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'VM_UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_PRESENT')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-recovery-export-local-'), 'LOCAL_PATH')
    require(time.time() < int(read(local / 'expires-epoch.txt')), 'HANDOFF_EXPIRED')
    require(SHARE.is_mount() and not SHARE.is_symlink(), 'SHARE_NOT_MOUNTED')
    os.umask(0o077)
    fd = os.open('/root/hbr-a3-driver.lock', os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        claim_raw = read(Path('/root/hbr-a3-app-recovery.claim'))
        claim = json.loads(claim_raw)
        require(claim['source_sha256'] == SOURCE and claim['work'] == EXPECTED_WORK, 'CLAIM_MISMATCH')
        work = Path(claim['work'])
        raw = read(work / 'result.json')
        result = json.loads(raw)
        require(result['source_sha256'] == SOURCE and
                result['status'] == 'MANUAL_RECOVERY_HEALTHY_REVIEW_REQUIRED' and
                isinstance(result.get('finished_epoch'), (float, int)), 'NOT_FINISHED_EXPECTED_RESULT')
        files = {'result.json': raw, 'app-recovery.claim': claim_raw}
        metadata = inventory(work)
        for cmd in result['commands']:
            output = cmd['stdout_file']
            require(re.fullmatch(r'\d+-[a-z0-9-]+\.stdout', output), 'OUTPUT_PATH')
            if cmd['name'] in SAFE_NAMES or cmd['name'] in {'start-' + s for s in APPS}:
                files[output] = read(work / output)
        originals = {
            'original-a3-result.json': ('/root/hbr-a3-joz3x6ya/result.json', '5df896fd9f501cbac82e1091c6368160d79dbca34baf651681f766f331102fa7'),
            'original-a3.claim': ('/root/hbr-a3-docker-restart.claim', 'fc00ce44c9aaa35b3cb15d150db208a560f0873532736fb4daafe870c3afa175'),
        }
        for name, (path, expected) in originals.items():
            data = read(Path(path))
            require(sha(data) == expected, 'ORIGINAL_A3_CHANGED')
            files[name] = data
        files['PRIVATE_FILE_METADATA.json'] = (json.dumps(metadata, indent=2) + '\n').encode()
        receipt = {'collected_epoch': time.time(), 'source_work': str(work),
                   'collector_sha256': sha(read(Path(__file__))), 'result_sha256': sha(raw),
                   'status_reported': result['status'], 'scope': 'EXISTING_FILES_ONLY',
                   'private_file_count': sum('sha256' in row for row in metadata),
                   'excluded_derived_directories': [row['file'] for row in metadata if 'status' in row],
                   'raw_stderr_and_app_errors': 'RETAINED_GUEST_PRIVATE',
                   'fresh_docker_queries': 'NOT_RUN', 'new_start_restart_restore': 'NOT_RUN',
                   'AUTOSTART': result['AUTOSTART'], 'SYSLOG_INGESTION': result['SYSLOG_INGESTION'],
                   'AC_CLOSE': result['AC_CLOSE']}
        files['RECEIPT.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
        target = SHARE / 'RECOVERY_RESULT'
        target.mkdir(exist_ok=False)
        for name, data in files.items():
            with (target / name).open('xb') as stream:
                stream.write(data)
        manifest = ''.join(f'{sha(data)}  {name}\n' for name, data in sorted(files.items())).encode()
        with (target / 'SHA256SUMS').open('xb') as stream:
            stream.write(manifest)
        with (SHARE / 'EXPORT_DONE').open('x') as stream:
            stream.write(sha(manifest) + '\n')
        print('APP_RECOVERY_EXPORTED STATUS=' + result['status'])
        print('Existing files only. No start, restart, restore or fresh Docker queries.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        text = str(exc)
        print('RECOVERY_EXPORT_STOP ' + (text if re.fullmatch('[A-Z_]+', text) else type(exc).__name__))
        raise SystemExit(2)
