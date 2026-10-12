"""Receipt-preserving transport for the approved, fixed MON control01 commands."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parent
S='20261012T2220-mon02'
SES='/var/lib/fds-change/if06b-'+S
SURV='/var/lib/fds-change/if06b-survival-'+S
TOK='/run/fds-if06b-'+S
IN='/home/svc_ansible/if06b-in-'+S
KC=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']

def run(name,body,timeout=80,tty=False,target='control'):
    receipt=ROOT/(name+'.json')
    if receipt.exists():raise RuntimeError('RECEIPT_EXISTS: '+name)
    prefix='''import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='80724d56-7c17-f8a0-b2ea-ece7a154e24b'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
'''
    source=(prefix+body).encode()
    if target=='worker':
        source=source.replace(b'k8s-control01',b'k8s-worker03').replace(b'80724d56-7c17-f8a0-b2ea-ece7a154e24b',b'a3394d56-a6ae-2f0f-c17d-c6dc9dff8548').replace(b'2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360',b'f0c48106-f753-4ab7-bacd-660c126fca2f')
    else:assert target=='control'
    compile(source, '<fixed-remote-command>', 'exec')
    ssh=['/usr/bin/ssh','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes',
         '-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts',
         '-o','IdentitiesOnly=yes','svc_ansible@10.1.93.102','sudo','-n','/usr/bin/python3','-B','-I','-']
    if target=='worker':ssh=[x.replace('svc_ansible@10.1.93.102','svc_ansible@10.1.93.108') for x in ssh]
    bridge=('import subprocess,sys\np=subprocess.run('+repr(ssh)+',input='+repr(source)+',capture_output=True,timeout='+str(timeout)+')\n'
            'sys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    started=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
    p=subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
                      '-o','ConnectTimeout=8','fds-ansible01','python3','-B','-I','-'],input=bridge,capture_output=True,timeout=timeout+10)
    row={'started_kst':started,'finished_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),
         'source_sha256':hashlib.sha256(source).hexdigest(),'route':'fds-ansible01 -> svc_ansible@'+('10.1.93.108' if target=='worker' else '10.1.93.102')+' -> sudo',
         'rc':p.returncode,'stdout':p.stdout.decode('utf-8','replace'),'stderr':p.stderr.decode('utf-8','replace')}
    receipt.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Source is fixed and has no secret. Token-bearing commands must never print it.
    (ROOT/(name+'.remote.py')).write_bytes(source)
    print(json.dumps({'name':name,'rc':p.returncode,'stdout':row['stdout'],'stderr':row['stderr']},ensure_ascii=False))
    return row
