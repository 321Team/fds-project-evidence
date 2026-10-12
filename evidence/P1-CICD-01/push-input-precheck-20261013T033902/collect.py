from pathlib import Path
import base64, datetime, hashlib, json, shlex, subprocess
P = Path(__file__).resolve().parent
D = P / 'runtime-read'
D.mkdir(exist_ok=False)
sources = {name: (P / 'source' / (name + '.py')).read_bytes()
           for name in ('verify_runner', 'prepare_db', 'oci_archive', 'scan_images')}
hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in sources.items()}
source = 'import types,sys,base64,hashlib\n'
for name, raw in sources.items():
    compile(raw, name, 'exec')
    source += ('raw=base64.b64decode(' + repr(base64.b64encode(raw).decode()) + ')\n'
               'assert hashlib.sha256(raw).hexdigest()==' + repr(hashes[name]) + '\n'
               'module=types.ModuleType(' + repr(name) + ')\n'
               'module.__file__=' + repr('/reviewed-in-memory/' + name + '.py') + '\n'
               'sys.modules[' + repr(name) + ']=module\n'
               'exec(compile(raw,module.__file__,"exec"),module.__dict__)\n')
source += 'MODULE_HASHES=' + repr(hashes) + '\n'
source += (P / 'runner_read.py').read_text()
raw = source.encode()
compile(raw, 'remote_read', 'exec')
(D / 'collector.py').write_bytes(raw)
inner = ['/usr/bin/ssh', '-T', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519',
         '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
         '-o', 'UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts', '-o', 'IdentitiesOnly=yes',
         'server01_cicd-runner@10.250.10.20', '/usr/bin/python3 -B -I -S -']
bridge = ('import subprocess,sys\np=subprocess.run(' + repr(inner) + ',input=' + repr(raw) +
          ',capture_output=True,timeout=100)\nsys.stdout.buffer.write(p.stdout)\n'
          'sys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
argv = ['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
        '-o', 'StrictHostKeyChecking=yes', 'fds-ansible01', '/usr/bin/python3', '-B', '-I', '-S', '-']
receipt = {'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'argv': argv, 'inner_argv': inner, 'collector_sha256': hashlib.sha256(raw).hexdigest(),
           'read_only': True, 'network_destination': 'existing SSH path; no registry connection'}
try:
    result = subprocess.run(argv, input=bridge, capture_output=True, timeout=115)
    stdout, stderr = result.stdout, result.stderr
    receipt['rc'] = result.returncode
except subprocess.TimeoutExpired as exc:
    stdout, stderr = exc.stdout or b'', exc.stderr or b''
    receipt.update(rc=None, error='TIMEOUT_NO_RETRY')
(D / 'stdout.json').write_bytes(stdout)
(D / 'stderr.txt').write_bytes(stderr)
receipt.update(finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               stdout_sha256=hashlib.sha256(stdout).hexdigest(), stderr_sha256=hashlib.sha256(stderr).hexdigest())
(D / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'rc': receipt['rc'], 'stdout_bytes': len(stdout), 'stderr_bytes': len(stderr)}))
if receipt['rc'] != 0: print(stderr.decode(errors='replace')[:1600])
