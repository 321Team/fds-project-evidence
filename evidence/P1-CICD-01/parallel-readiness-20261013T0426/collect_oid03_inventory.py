from pathlib import Path
import datetime,hashlib,json,subprocess,shlex
P=Path(__file__).resolve().parent
raw=(P/'read_oid03_inventory.py').read_bytes();compile(raw,'read_oid03_inventory.py','exec')
for host,ip in [('control01','102'),('control02','103'),('control03','104'),('worker01','105'),('worker02','107'),('worker03','108')]:
    D=P/('oid03-inventory-'+host);D.mkdir(exist_ok=False)
    inner=['/usr/bin/ssh','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519',
        '-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes',
        '-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes',
        '-o','ForwardAgent=no','-o','ClearAllForwardings=yes','svc_ansible@10.1.93.'+ip,
        shlex.join(['sudo','-n','/usr/bin/python3','-B','-I','-S','-'])]
    bridge=('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(raw)+',capture_output=True,timeout=55)\n'
        'sys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    outer=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8',
        '-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-S','-']
    receipt={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'outer_argv':outer,
        'inner_argv':inner,'source_sha256':hashlib.sha256(raw).hexdigest(),'read_only':True}
    try:
        r=subprocess.run(outer,input=bridge,capture_output=True,timeout=65);a,b,rc=r.stdout,r.stderr,r.returncode
    except subprocess.TimeoutExpired as e:
        a,b,rc=e.stdout or b'',e.stderr or b'',None
    (D/'stdout.json').write_bytes(a);(D/'stderr.txt').write_bytes(b)
    receipt.update(rc=rc,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        stdout_sha256=hashlib.sha256(a).hexdigest(),stderr_sha256=hashlib.sha256(b).hexdigest())
    (D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'host':host,'rc':rc,'bytes':len(a)}),flush=True)
    if rc!=0:break
