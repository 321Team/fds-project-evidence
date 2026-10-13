"""Verify the existing key selected by matching public fingerprints. GET only."""
from pathlib import Path
import datetime, hashlib, json, shlex, subprocess
P = Path(__file__).resolve().parent
controller = json.loads((P/'broker-key-metadata-controller/stdout.json').read_text())
cp1 = json.loads((P/'broker-key-metadata-cp1/stdout.json').read_text())
allowed = {f['fingerprint'] for item in cp1['files'] for f in item.get('fingerprints', [])}
matched = [x for x in controller['files'] if any(f['fingerprint'] in allowed for f in x.get('fingerprints', []))]
assert len(matched) == 1
key = matched[0]['corresponding_private_metadata']
assert key['path'] == '/home/server01_ansible/.ssh/id_ed25519' and key['mode'] == '0o600' and key['uid'] == 1000
raw = (P.parent/'p1-delivery-runner-20261013/auth_path_read.py').read_bytes()
compile(raw, 'auth_path_read.py', 'exec')
D = P/'cp1-existing-auth'; D.mkdir(exist_ok=False)
(D/'collector.py').write_bytes(raw)
inner = ['/usr/bin/ssh','-F','/dev/null','-T','-i',key['path'],'-o','BatchMode=yes',
    '-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts',
    '-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no',
    '-o','ControlPath=none','-o','UpdateHostKeys=no','server02@10.1.93.102','/usr/bin/python3 -B -I -S - cp1']
bridge = ('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(raw)+',capture_output=True,timeout=35)\n'
    'sys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
outer = ['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8',
    '-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-S','-']
receipt = {'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'outer_argv':outer,
    'inner_argv':inner,'read_only':True,'source_sha256':hashlib.sha256(raw).hexdigest(),
    'key_selection_basis':'existing .pub fingerprint equals existing server02 authorized_keys; no key or trust change'}
r = subprocess.run(outer,input=bridge,capture_output=True,timeout=45)
(D/'stdout.json').write_bytes(r.stdout); (D/'stderr.txt').write_bytes(r.stderr)
receipt.update(rc=r.returncode,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rc':r.returncode,'stdout_bytes':len(r.stdout),'stderr_bytes':len(r.stderr)}))
