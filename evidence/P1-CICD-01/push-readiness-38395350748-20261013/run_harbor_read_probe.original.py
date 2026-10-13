"""Existing strict-key route, bounded read-only source; no guest files written."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

source_path, receipt_path = map(Path, sys.argv[1:])
assert not receipt_path.exists()
source = source_path.read_bytes()
argv = ['/usr/bin/ssh', '-T', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519',
        '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts', '-o', 'IdentitiesOnly=yes',
        'svc_ansible@10.1.93.54', 'sudo', '-n', '/usr/bin/python3', '-B', '-I', '-']
controller = ('import subprocess,sys\np=subprocess.run(' + repr(argv) + ',input=' + repr(source) +
              ',capture_output=True,timeout=70)\nsys.stdout.buffer.write(p.stdout)\n'
              'sys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
p = subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes',
                    '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
                    'fds-ansible01', '/usr/bin/python3', '-B', '-I', '-'],
                   input=controller, capture_output=True, timeout=80)
result = dict(at=dt.datetime.now(dt.timezone.utc).isoformat(), source_sha256=hashlib.sha256(source).hexdigest(),
              rc=p.returncode, stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
if p.returncode == 0:
    result['observation'] = json.loads(p.stdout)
else:
    result['stdout_sha256'] = hashlib.sha256(p.stdout).hexdigest()
receipt_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
