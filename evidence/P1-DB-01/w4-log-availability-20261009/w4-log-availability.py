"""Read retained transaction-api CRI log timestamps only. Never export payloads."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import time

KST = dt.timezone(dt.timedelta(hours=9))
START = dt.datetime.fromisoformat('2026-10-08T20:26:49+09:00')
END = dt.datetime.fromisoformat('2026-10-08T20:27:52+09:00')
PREFIX = re.compile(rb'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)) (stdout|stderr) ([FP]) ')

def now():
    return dt.datetime.now(KST).isoformat()

def gate():
    if socket.gethostname() not in ('k8s-worker01', 'k8s-worker02', 'k8s-worker03') or os.geteuid() != 0:
        raise SystemExit('STOP host/euid')
    if not '2026-10-09T00:00:00+09:00' <= now() < '2026-10-09T09:00:00+09:00':
        raise SystemExit('STOP outside window')

def scan(path, allowance, deadline):
    row = {'path': str(path), 'status': 'UNREAD', 'payload_exported': False}
    if path.is_symlink() or not path.is_file():
        row['status'] = 'SKIPPED_NONREGULAR'
        return row, 0
    if path.suffix == '.gz':
        row['status'] = 'SKIPPED_COMPRESSED'
        return row, 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        before = os.fstat(f.fileno())
        if not stat.S_ISREG(before.st_mode):
            row['status'] = 'SKIPPED_NONREGULAR'
            return row, 0
        count = 0
        rawhash = hashlib.sha256()
        first = last = None
        in_window = valid = invalid = 0
        cap = min(8 * 1024 * 1024, allowance)
        exhausted = False
        while count < cap and time.monotonic() < deadline:
            # Bounded readline also bounds memory for malformed multi-megabyte lines.
            line = f.readline(min(65536, cap - count))
            if not line:
                exhausted = True
                break
            count += len(line)
            rawhash.update(line)
            match = PREFIX.match(line)
            if match:
                try:
                    stamp = dt.datetime.fromisoformat(match[1].decode().replace('Z', '+00:00'))
                except ValueError:
                    invalid += 1
                    continue
                valid += 1
                first = stamp if first is None else min(first, stamp)
                last = stamp if last is None else max(last, stamp)
                in_window += START <= stamp <= END
            else:
                invalid += 1
        after = os.fstat(f.fileno())
    stable = (before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    complete = exhausted or count == before.st_size == after.st_size
    row.update(status='COMPLETE' if complete and stable else 'PARTIAL_OR_CHANGED',
               size_before=before.st_size, size_after=after.st_size,
               mtime_ns_before=before.st_mtime_ns, mtime_ns_after=after.st_mtime_ns,
               inode=before.st_ino, dev=before.st_dev, read_bytes=count,
               read_bytes_sha256=rawhash.hexdigest(), stable_during_read=stable,
               valid_cri_prefixes=valid, unparsed_chunks=invalid,
               earliest_record_kst=first.astimezone(KST).isoformat() if first else None,
               latest_record_kst=last.astimezone(KST).isoformat() if last else None,
               records_in_w4_interval=in_window)
    return row, count

def main():
    gate()
    out = {'schema': 'fds.w4-log-availability.v1', 'host': socket.gethostname(),
           'started_at_kst': now(), 'interval_start_kst': START.isoformat(), 'interval_end_kst': END.isoformat(),
           'boundary': 'Read-only CRI timestamps under /var/log/pods/fds-app_transaction-api-*. No payload, credentials, network request, service change or test traffic. No 5xx verdict.',
           'files': [], 'http_5xx_status': 'NOT_MEASURED', 'errors': []}
    deadline = time.monotonic() + 60
    allowance = 32 * 1024 * 1024
    root = Path('/var/log/pods')
    dirs = sorted(p for p in root.glob('fds-app_transaction-api-*') if p.is_dir() and not p.is_symlink())
    out['retained_pod_directories'] = [p.name for p in dirs]
    paths = sorted(p for d in dirs for c in d.iterdir() if c.is_dir() and not c.is_symlink() for p in c.iterdir())
    out['discovered_file_count'] = len(paths)
    for p in paths[:64]:
        gate()
        if allowance <= 0 or time.monotonic() >= deadline:
            out['errors'].append('STOP byte/time budget')
            break
        try:
            row, used = scan(p, allowance, deadline)
            out['files'].append(row)
            allowance -= used
        except OSError as e:
            out['files'].append({'path': str(p), 'status': 'READ_ERROR', 'errno': e.errno})
    if len(paths) > 64:
        out['errors'].append('STOP file count budget')
    out['finished_at_kst'] = now()
    print(json.dumps(out, ensure_ascii=False))

if __name__ == '__main__':
    main()
