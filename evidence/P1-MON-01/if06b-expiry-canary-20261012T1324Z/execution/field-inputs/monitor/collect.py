#!/usr/bin/env python3
"""One-shot monitor01 input reads. No policy/service changes or trial traffic."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.parse import quote


def main():
    if socket.gethostname().split('.')[0] != 'monitor01' or os.geteuid() != 0:
        raise SystemExit('STOP: monitor01 and existing root privilege required')
    os.umask(0o077)
    os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin', LC_ALL='C')
    out = Path(tempfile.mkdtemp(prefix='if06b-mon-inputs-', dir='/root'))
    print('OUT=' + str(out), flush=True)
    commands = [
        ('addresses', ['ip', '-j', 'address', 'show']),
        ('route-worker03', ['ip', '-4', 'route', 'get', '10.1.93.108']),
        ('listeners', ['ss', '-H', '-lntp']),
        ('firewalld-state', ['firewall-cmd', '--state']),
        ('active-zones', ['firewall-cmd', '--get-active-zones']),
        ('runtime-zones', ['firewall-cmd', '--list-all-zones']),
        ('permanent-zones', ['firewall-cmd', '--permanent', '--list-all-zones']),
        ('capture-version', ['tcpdump', '--version']),
    ]
    curl = ['curl', '--disable', '--noproxy', '*', '--silent', '--show-error', '--fail',
            '--connect-timeout', '2', '--max-time', '5', '--retry', '0']
    base = 'http://127.0.0.1:19090/api/v1/'
    commands += [
        ('heartbeat-age', curl + [base + 'query?query=' + quote('time()-timestamp(fds_monitoring_heartbeat)', safe='')]),
        ('watchdog-alerts', curl + [base + 'alerts']),
        ('lb-probe', curl + [base + 'query?query=' + quote('probe_success{instance="10.1.93.109:6443"}', safe='')]),
    ]
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    rows = []
    deadline = time.monotonic() + 120
    for name, argv in commands:
        row = {'name': name, 'argv': argv, 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        left = deadline - time.monotonic()
        stdout, stderr, rc = b'', b'Collection budget exhausted', 124
        if left > 0:
            try:
                p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=min(10, left))
                stdout, stderr, rc = p.stdout, p.stderr, p.returncode
            except subprocess.TimeoutExpired as exc:
                stdout, stderr = exc.stdout or b'', exc.stderr or b''
            except OSError as exc:
                stderr, rc = str(exc).encode(), 127
        for suffix, data in [('stdout', stdout), ('stderr', stderr), ('rc', (str(rc)+'\n').encode())]:
            (out / (name+'.'+suffix)).write_bytes(data)
        row.update(rc=rc, finished_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        rows.append(row)
    stable = boot == Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    rc = 0 if stable and all(r['rc'] == 0 for r in rows) else 2
    receipt = {'schema': 'if06b-monitor-input-read/v1', 'hostname': socket.gethostname(),
               'boot_id': boot, 'boot_unchanged': stable, 'uid': os.geteuid(),
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'collection_rc': rc, 'queries': rows, 'baseline_verdict': 'PENDING_REVIEW',
               'canary_trial_requests': 0, 'policy_or_service_changes': 0}
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
                                       for p in sorted(out.iterdir()) if p.is_file()))
    print('COLLECTION_RC='+str(rc)+' OUT='+str(out), flush=True)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
