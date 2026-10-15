"""Read clock originals once; no server file, clock, service or API mutation."""
import base64
import datetime as dt
import hashlib
import json
import os
import pwd
import socket
import subprocess
import sys
import time
from pathlib import Path


def stamp():
    ns = time.time_ns()
    return {'unix_ns': ns, 'utc': dt.datetime.fromtimestamp(ns / 1e9, dt.timezone.utc).isoformat(),
            'monotonic_raw_ns': time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)}


def capture(argv):
    before = stamp()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=5, env={**os.environ, 'LC_ALL': 'C'})
        rc, out, err = p.returncode, p.stdout, p.stderr
        error = None
    except subprocess.TimeoutExpired as e:
        rc, out, err, error = None, e.stdout or b'', e.stderr or b'', 'TIMEOUT'
    except OSError as e:
        rc, out, err, error = None, b'', b'', type(e).__name__
    return {'argv': argv, 'started': before, 'finished': stamp(), 'rc': rc, 'error': error,
            'stdout_b64': base64.b64encode(out).decode(), 'stderr_b64': base64.b64encode(err).decode(),
            'stdout_sha256': hashlib.sha256(out).hexdigest(), 'stderr_sha256': hashlib.sha256(err).hexdigest()}


def main():
    expected_host, expected_user, phase, round_label = sys.argv[1:]
    if phase not in ('PREPARATION', 'BEFORE_R1', 'AFTER_FINISH'):
        raise ValueError('PHASE_INVALID')
    if socket.gethostname() != expected_host or pwd.getpwuid(os.getuid()).pw_name != expected_user:
        raise ValueError('HOST_OR_ACCOUNT_MISMATCH')
    out = {'schema': 'AC09-CLOCK-RAW-1', 'classification': phase, 'round_label': round_label,
           'host': socket.gethostname(), 'user': expected_user, 'uid': os.getuid(),
           'started': stamp(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
           'mutation': False, 'interval_accuracy_proven': False, 'commands': []}
    for argv in (
        ['/usr/bin/chronyc', '-n', 'tracking'],
        ['/usr/bin/chronyc', '-n', 'sources', '-v'],
        ['/usr/bin/systemctl', 'show', 'chronyd.service', 'chrony.service', '--no-pager',
         '--property=Id,ActiveState,SubState,MainPID,ExecMainStartTimestamp,ExecMainStartTimestampMonotonic'],
    ):
        out['commands'].append(capture(argv))
    out['finished'] = stamp()
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
