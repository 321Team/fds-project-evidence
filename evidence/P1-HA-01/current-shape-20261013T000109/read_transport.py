"""Existing strict SSH route; new local receipts only, no remote staging."""
from pathlib import Path
import datetime as dt, hashlib, json, subprocess
OUT=Path(__file__).resolve().parent
PY='C:/Users/soldesk/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
def run(name,ip,source,timeout=90):
    target=OUT/name
    target.mkdir(exist_ok=False)
    raw=source if isinstance(source,bytes) else source.encode()
    (target/'collector.py').write_bytes(raw)
    inner=['/usr/bin/ssh','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','svc_ansible@'+ip,'sudo','-n','/usr/bin/python3','-B','-I','-']
    bridge=('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(raw)+',capture_output=True,timeout='+str(timeout-10)+')\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-']
    receipt={'started_at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'route':'fds-ansible01 -> svc_ansible@'+ip,'source_sha256':hashlib.sha256(raw).hexdigest(),'strict_host_key':True,'batch_mode':True,'command':cmd,'inner_command':inner}
    try:
        p=subprocess.run(cmd,input=bridge,capture_output=True,timeout=timeout)
        stdout,stderr=p.stdout,p.stderr;receipt['rc']=p.returncode
    except subprocess.TimeoutExpired as e:
        stdout,stderr=e.stdout or b'',e.stderr or b'';receipt.update(rc=None,error='SSH_TIMEOUT_NO_AUTOMATIC_RETRY')
    (target/'stdout.json').write_bytes(stdout);(target/'stderr.txt').write_bytes(stderr)
    receipt.update(finished_at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),stdout_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest())
    (target/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result={'name':name,'rc':receipt['rc'],'bytes':len(stdout),'stderr_bytes':len(stderr)}
    try: result['status']=json.loads(stdout).get('status')
    except ValueError:result['json']='INVALID_OR_EMPTY'
    print(json.dumps(result));return receipt
