"""Read sealed A3 files only. No Docker/service commands or source modification."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import time

WORK = Path('/root/hbr-a3-joz3x6ya')
SHARE = Path('/mnt/hbr-a3-result')
SOURCE = 'b006ea6740435a4ce77a871dad20db2ac86d73f02ba90c3feccc79a668439321'
HINTS = ('permission denied', 'connection refused', 'failed to initialize logging driver',
         'address already in use', 'no such file or directory', 'no such container',
         'context deadline exceeded', 'timed out', 'failed to start container',
         'invalid argument', 'invalid boot', 'cannot assign requested address')
SAFE_COMMANDS = {'candidate-check', 'live-restore-before', 'unit-before', 'state-immediate',
                 'unit-immediate', 'unit-after', 'state-after', 'profile-engine-after',
                 'profile-compose-after', 'profile-security-after', 'profile-enforcing-after',
                 'profile-labels-after', 'listener-after', 'live-restore-after'}

def require(ok, code):
    if not ok:
        raise ValueError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size < 32*1024*1024,
            'UNSAFE_OR_OVERSIZED_FILE')
    return path.read_bytes()

def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_USER')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_PRESENT')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink(), 'SHARE_NOT_MOUNTED')
    require(not WORK.is_symlink() and WORK.is_dir(), 'WORK_PATH')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-a3-export-local-'), 'LOCAL_PATH')
    require(time.time() < int(read(local/'expires-epoch.txt')), 'HANDOFF_EXPIRED')
    os.umask(0o077)
    # Hold the same lock as the driver; never inspect an actively running A3 session.
    fd = os.open('/root/hbr-a3-driver.lock', os.O_RDWR | os.O_NOFOLLOW)
    with os.fdopen(fd, 'r+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raw = read(WORK/'result.json')
        result = json.loads(raw)
        require(result['source_sha256'] == SOURCE, 'SOURCE_MISMATCH')
        require(result['status'] == 'STOP_RECOVERY_REQUIRED' and 'finished_epoch' in result, 'NOT_FINISHED_STOP')
        files = {'result.json': raw}
        missing = []
        for name in ('candidate-check-result.json', 'observation.jsonl', 'trial.py', 'observer.py'):
            path = WORK/name
            if path.exists():
                files[name] = read(path)
            else:
                missing.append(name)
        claim = Path('/root/hbr-a3-docker-restart.claim')
        if claim.exists():
            files['docker-restart.claim'] = read(claim)
        else:
            missing.append('docker-restart.claim')
        metadata = []
        # Hash every bounded regular file. Raw journal/observer stderr/command stderr stay in guest.
        for path in sorted(WORK.iterdir()):
            if path.is_dir() and not path.is_symlink():
                continue
            try:
                data = read(path)
                row = {'file': path.name, 'bytes': len(data), 'sha256': sha(data)}
                if path.suffix == '.stderr' or 'journal' in path.name:
                    text = data.decode('utf8', errors='replace').lower()
                    row['fixed_hints'] = {hint: text.count(hint) for hint in HINTS if hint in text}
                metadata.append(row)
            except ValueError:
                metadata.append({'file': path.name, 'status': 'NOT_READ_UNSAFE_OR_OVERSIZED'})
        for cmd in result['commands']:
            name, output = cmd['name'], cmd['stdout_file']
            require(re.fullmatch(r'\d+-[a-z0-9-]+\.stdout', output), 'OUTPUT_PATH')
            if name in SAFE_COMMANDS or re.fullmatch(r'volume-[a-f0-9]{64}', name):
                if (WORK/output).exists():
                    files[output] = read(WORK/output)
                else:
                    missing.append(output)
        files['PRIVATE_FILE_METADATA.json'] = (json.dumps(metadata, indent=2)+'\n').encode()
        receipt = {'collected_epoch': time.time(), 'source_work': str(WORK),
                   'collector_sha256': sha(read(Path(__file__))), 'result_sha256': sha(raw),
                   'scope': 'READ_EXISTING_FILES_ONLY', 'missing_files': missing,
                   'new_restart': 'NOT_RUN', 'restore': 'NOT_RUN', 'fresh_queries': 'NOT_RUN',
                   'raw_journal_and_stderr': 'RETAINED_GUEST_PRIVATE', 'AUTOSTART': 'NOT_EVALUATED'}
        files['RECEIPT.json'] = (json.dumps(receipt, indent=2)+'\n').encode()
        destination = SHARE/'A3_STOP'
        destination.mkdir(exist_ok=False)
        for name, data in files.items():
            with (destination/name).open('xb') as out:
                out.write(data)
        manifest = ''.join(sha(data)+'  '+name+'\n' for name, data in sorted(files.items())).encode()
        with (destination/'SHA256SUMS').open('xb') as out:
            out.write(manifest)
        with (SHARE/'EXPORT_DONE').open('x') as out:
            out.write(sha(manifest)+'\n')
        print('A3_STOP_EXPORTED STATUS='+result['status'])
        print('No restart, restore, retry or fresh Docker queries performed.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        code = str(exc)
        print('EXPORT_STOP '+(code if re.fullmatch('[A-Z_]+', code) else 'PRIVATE_REVIEW_REQUIRED'))
        raise SystemExit(2)
