"""Supplement the sealed STOP using bounded read-only journal and inspect queries."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time

WORK = Path('/root/hbr-a3-joz3x6ya')
RESULT_SHA = '5df896fd9f501cbac82e1091c6368160d79dbca34baf651681f766f331102fa7'
SHARE = Path('/mnt/hbr-a3-diag')
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LC_ALL': 'C'}
HINTS = ('failed to add match', 'failed to parse boot', 'invalid argument', 'permission denied',
         'failed to initialize logging driver', 'failed to start container', 'connection refused',
         'dial tcp', '127.0.0.1:1514', '[::1]:1514', 'address already in use',
         'failed to start daemon', 'daemon has completed initialization', 'api listen on',
         'starting up', 'error waiting for container', 'failed to load container')

def require(ok, code):
    if not ok:
        raise ValueError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    require(not path.is_symlink() and path.is_file() and path.stat().st_size < 32*1024*1024, 'INVALID_FILE')
    return path.read_bytes()

def hints(text):
    text = text.lower()
    return {hint: text.count(hint) for hint in HINTS if hint in text}

def main():
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'harbor01', 'HOST_OR_USER')
    require(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() in
            ('564d9e38-f024-efe2-b68f-137a5047788a', '389e4d56-24f0-e2ef-b68f-137a5047788a'), 'UUID')
    require(not any(p.exists() for p in Path('/sys/class/net').glob('*/device')), 'NIC_PRESENT')
    require(os.path.ismount(SHARE) and not SHARE.is_symlink() and not WORK.is_symlink(), 'PATH')
    local = Path(__file__).resolve().parent
    require(local.parent == Path('/root') and local.name.startswith('hbr-a3-diag-local-'), 'LOCAL_PATH')
    require(time.time() < int(read(local/'expires-epoch.txt')), 'HANDOFF_EXPIRED')
    os.umask(0o077)
    with os.fdopen(os.open('/root/hbr-a3-driver.lock', os.O_RDWR | os.O_NOFOLLOW), 'r+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raw = read(WORK/'result.json')
        require(sha(raw) == RESULT_SHA, 'SEALED_RESULT_CHANGED')
        original = json.loads(raw)
        boot = original['boot_before']
        require(re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', boot), 'BOOT_FORMAT')
        require(Path('/proc/sys/kernel/random/boot_id').read_text().strip() == boot, 'BOOT_CHANGED')
        ids = {row['id']: row['name'] for row in original['after'].values()}
        require(len(ids) == 10 and all(re.fullmatch('[0-9a-f]{64}', key) for key in ids), 'ID_SET')
        private = Path(tempfile.mkdtemp(prefix='hbr-a3-diagnostic-', dir='/root'))
        result = {'collected_epoch': time.time(), 'source_work': str(WORK), 'source_result_sha256': RESULT_SHA,
                  'collector_sha256': sha(read(Path(__file__))), 'private': str(private),
                  'scope': 'BOUNDED_READ_ONLY_SUPPLEMENT_NOT_ORIGINAL_RUNTIME', 'commands': [],
                  'restart': 'NOT_RUN', 'restore': 'NOT_RUN', 'AUTOSTART': 'NOT_EVALUATED'}
        old_error = read(WORK/'24-docker-journal-private.stderr')
        result['original_journal_error'] = {'sha256': sha(old_error), 'bytes': len(old_error),
                                           'fixed_hints': hints(old_error.decode(errors='replace'))}
        def query(name, argv):
            began = time.time()
            outpath, errpath = private/(name+'.stdout'), private/(name+'.stderr')
            with outpath.open('xb') as out, errpath.open('xb') as err:
                try:
                    rc = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                        env=ENV, timeout=30).returncode
                except subprocess.TimeoutExpired:
                    rc = 124
                except OSError:
                    rc = 127
            stdout, stderr = read(outpath), read(errpath)
            result['commands'].append({'name': name, 'argv': argv, 'rc': rc, 'started_epoch': began,
                                       'finished_epoch': time.time(), 'stdout_sha256': sha(stdout),
                                       'stdout_bytes': len(stdout), 'stderr_sha256': sha(stderr),
                                       'stderr_bytes': len(stderr), 'stderr_fixed_hints': hints(stderr.decode(errors='replace'))})
            return rc, stdout
        query('journal-version', ['journalctl', '--version'])
        window = original['journal_window']
        rc, rawjournal = query('same-window-journal', ['journalctl', '--no-pager', '-u', 'docker.service',
             '_BOOT_ID='+boot.replace('-', ''), '--since', '@'+str(window['since_epoch_floor']),
             '--until', '@'+str(window['until_epoch']), '-o', 'json'])
        events, invalid = [], 0
        for line in rawjournal.decode(errors='replace').splitlines():
            try:
                row = json.loads(line)
                message = row.get('MESSAGE', '')
                require(isinstance(message, str) and row.get('_BOOT_ID') == boot.replace('-', ''), 'JOURNAL_ROW')
                timestamp = row['__REALTIME_TIMESTAMP']
                require(isinstance(timestamp, str) and timestamp.isdigit(), 'JOURNAL_TIMESTAMP')
                events.append({'realtime_us': timestamp, 'message_sha256': sha(message.encode()),
                    'fixed_hints': hints(message),
                    'matching_containers': [name for cid, name in ids.items() if cid in message or cid[:12] in message]})
            except (ValueError, KeyError, TypeError):
                invalid += 1
        result['journal'] = {'rc': rc, 'parsed_rows': len(events), 'invalid_rows': invalid,
                             'status': 'COLLECTED' if rc == 0 and events and invalid == 0 else 'INCOMPLETE', 'events': events}
        fmt = '{"id":{{json .Id}},"status":{{json .State.Status}},"error":{{json .State.Error}}}'
        rc, states = query('current-state-errors', ['docker', '--host=unix:///var/run/docker.sock',
                             'inspect', '--type', 'container', '--format', fmt, *sorted(ids)])
        selected, invalid = [], 0
        for line in states.decode(errors='replace').splitlines():
            try:
                row = json.loads(line)
                require(row['id'] in ids and row['status'] in ('running','exited','created','restarting','paused','dead','removing') and isinstance(row['error'], str), 'STATE_ROW')
                selected.append({'id': row['id'], 'name': ids[row['id']], 'status': row['status'],
                                 'error_sha256': sha(row['error'].encode()), 'error_bytes': len(row['error'].encode()),
                                 'fixed_hints': hints(row['error'])})
            except (ValueError, KeyError, TypeError):
                invalid += 1
        result['current_state'] = {'rc': rc, 'invalid_rows': invalid, 'rows': selected,
            'status': 'COLLECTED' if rc == 0 and invalid == 0 and len(selected) == 10 and len({r['id'] for r in selected}) == 10 else 'INCOMPLETE'}
        result['finished_epoch'] = time.time()
        data = (json.dumps(result, indent=2)+'\n').encode()
        (private/'SUMMARY.json').write_bytes(data)
        dest = SHARE/'A3_DIAGNOSTIC'
        dest.mkdir(exist_ok=False)
        (dest/'SUMMARY.json').write_bytes(data)
        manifest = (sha(data)+'  SUMMARY.json\n').encode()
        (dest/'SHA256SUMS').write_bytes(manifest)
        with (SHARE/'EXPORT_DONE').open('x') as out:
            out.write(sha(manifest)+'\n')
        print('A3_DIAGNOSTIC_EXPORTED JOURNAL='+result['journal']['status']+' STATE='+result['current_state']['status'])
        print('Read-only supplement. No restart, restore, retry or configuration change.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        code = str(exc)
        print('DIAGNOSTIC_STOP '+(code if re.fullmatch('[A-Z_]+', code) else 'PRIVATE_REVIEW_REQUIRED'))
        raise SystemExit(2)
