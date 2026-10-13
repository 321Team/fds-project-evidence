from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parent

def stamp():
    return datetime.now(timezone.utc).isoformat()

def save(name, value):
    with (ROOT / name).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def get(path):
    r = subprocess.run(['gh', 'api', path], capture_output=True, check=True, timeout=40)
    return json.loads(r.stdout)

def remote(name, raw, timeout=90):
    out = ROOT / name
    out.mkdir(exist_ok=False)
    if isinstance(raw, str): raw = raw.encode()
    compile(raw, 'remote-card', 'exec')
    (out / 'card.py').write_bytes(raw)
    inner = ['/usr/bin/ssh', '-T', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519',
             '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
             '-o', 'UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts', '-o', 'IdentitiesOnly=yes',
             'server01_cicd-runner@10.250.10.20', '/usr/bin/python3 -B -I -S -']
    bridge = ('import subprocess,sys\np=subprocess.run(' + repr(inner) + ',input=' + repr(raw) +
              ',capture_output=True,timeout=' + str(timeout-10) + ')\nsys.stdout.buffer.write(p.stdout)\n'
              'sys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    argv = ['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
            '-o', 'StrictHostKeyChecking=yes', 'fds-ansible01', '/usr/bin/python3', '-B', '-I', '-S', '-']
    receipt = dict(started_at_utc=stamp(), argv=argv, inner_argv=inner,
                   card_sha256=hashlib.sha256(raw).hexdigest())
    try:
        p = subprocess.run(argv, input=bridge, capture_output=True, timeout=timeout)
        stdout, stderr = p.stdout, p.stderr
        receipt['rc'] = p.returncode
    except subprocess.TimeoutExpired as e:
        stdout, stderr = e.stdout or b'', e.stderr or b''
        receipt.update(rc=None, error='TIMEOUT_NO_AUTOMATIC_RETRY')
    (out / 'stdout.json').write_bytes(stdout)
    (out / 'stderr.txt').write_bytes(stderr)
    receipt.update(finished_at_utc=stamp(), stdout_sha256=hashlib.sha256(stdout).hexdigest(),
                   stderr_sha256=hashlib.sha256(stderr).hexdigest())
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(name=name, rc=receipt['rc'], stdout_bytes=len(stdout), stderr_bytes=len(stderr))))
    return receipt
