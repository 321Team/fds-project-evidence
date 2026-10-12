import datetime, hashlib, json, shlex, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
raw = (P/'read_broker_key_metadata.py').read_bytes()
compile(raw, 'read_broker_key_metadata.py', 'exec')
base = ['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
        '-o', 'StrictHostKeyChecking=yes', 'fds-ansible01', '/usr/bin/python3', '-B', '-I', '-S', '-']
for role in ('controller', 'cp1'):
    d = P/('broker-key-metadata-'+role)
    d.mkdir(exist_ok=False)
    if role == 'controller':
        argv = ['/usr/bin/python3', '-B', '-I', '-S', '-', role]
    else:
        previous = json.loads((P/'broker-key-metadata-controller/stdout.json').read_text())
        source_address = previous['route_to_cp1'][0]['prefsrc']
        argv = ['/usr/bin/ssh', '-T', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519',
            '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts', '-o', 'IdentitiesOnly=yes',
            'svc_ansible@10.1.93.102', shlex.join(['sudo','-n','/usr/bin/python3','-B','-I','-S','-',role,source_address])]
    bridge = ('import subprocess,sys\np=subprocess.run('+repr(argv)+',input='+repr(raw)+',capture_output=True,timeout=35)\n'
              'sys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    receipt = {'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'outer_argv':base, 'inner_argv':argv,'source_sha256':hashlib.sha256(raw).hexdigest(), 'read_only':True}
    r = subprocess.run(base, input=bridge, capture_output=True, timeout=45)
    (d/'stdout.json').write_bytes(r.stdout); (d/'stderr.txt').write_bytes(r.stderr)
    receipt.update(rc=r.returncode,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
    (d/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'role':role,'rc':r.returncode,'bytes':len(r.stdout)}))
    if r.returncode:
        break
