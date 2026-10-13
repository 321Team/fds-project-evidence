"""Fixed, read-only MON input collection through the existing strict SSH route.

No credentials exported, files placed, API writes or trial traffic. Saves local receipts only.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
SESSION = '20261012T2220-mon02'
BASE = '/var/lib/fds-change/if06b-' + SESSION
KC = ['/usr/bin/kubectl', '--kubeconfig=/etc/kubernetes/admin.conf', '--request-timeout=6s']
commands = {
    'control01': [
        ('cluster_uid', KC + ['get', 'namespace', 'kube-system', '-o', 'jsonpath={.metadata.uid}']),
        ('monitoring_namespace', KC + ['get', 'namespace', 'monitoring-api', '-o', 'jsonpath={.metadata.uid}']),
        ('guardian_sa', KC + ['get', 'sa', '-n', 'monitoring-api', 'p1-mon-if06b-guardian', '-o', 'json']),
        ('guardian_role', KC + ['get', 'clusterrole', 'p1-mon-if06b-guardian', '-o', 'json']),
        ('guardian_binding', KC + ['get', 'clusterrolebinding', 'p1-mon-if06b-guardian', '-o', 'json']),
        ('canary', KC + ['get', '--raw=/apis/crd.projectcalico.org/v1/globalnetworkpolicies/p1-mon-if06b-worker03-to-monitor01-canary']),
        ('prometheus_service', KC + ['get', 'svc', '-n', 'monitoring-api', 'prometheus', '-o', 'json']),
        ('mon_pods_public', KC + ['get', 'pods', '-n', 'monitoring-api', '-o', 'wide']),
        ('paths', ['/usr/bin/python3', '-B', '-I', '-c',
          'import os,json; print(json.dumps({p:os.path.lexists(p) for p in '+repr([BASE, '/var/lib/fds-change/if06b-survival-'+SESSION, '/run/fds-if06b-'+SESSION])+'}))']),
    ],
    'worker03': [
        ('route', ['/usr/sbin/ip', '-4', 'route', 'get', '10.250.10.30']),
        ('addresses', ['/usr/sbin/ip', '-br', 'addr']),
        ('ports', ['/usr/sbin/ss', '-tan', '( sport = :45143 or sport = :45843 )']),
        ('ephemeral_range', ['/usr/bin/cat', '/proc/sys/net/ipv4/ip_local_port_range']),
        ('curl_version', ['/usr/bin/curl', '--version']),
        ('capture_version', ['/usr/sbin/tcpdump', '--version']),
        ('known_public_ca_paths', ['/usr/bin/python3', '-B', '-I', '-c',
          "import os,json,hashlib; paths=['/home/server07/fds-root-ca.crt','/etc/pki/ca-trust/source/anchors/fds-root-ca.crt']; print(json.dumps([{ 'path':p, 'exists':os.path.isfile(p), 'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest() if os.path.isfile(p) else None} for p in paths]))"]),
    ],
}

def collect(name, ip, host, command_timeout=8):
    receipt = OUT / (name + '-remaining-read.json')
    if receipt.exists():
        raise RuntimeError('RECEIPT_EXISTS_NO_RETRY')
    source = '''import os,socket,subprocess,json,time,datetime as dt,hashlib
expected=EXPECTED
commands=COMMANDS
def identity():
 return {'host':socket.gethostname(),'uid':os.geteuid(),'boot':open('/proc/sys/kernel/random/boot_id').read().strip(),'product_uuid':open('/sys/class/dmi/id/product_uuid').read().strip()}
before=identity()
if before['host']!=expected or before['uid']!=0:
 print(json.dumps({'status':'STOP_HOST_IDENTITY','identity':before}));raise SystemExit(2)
rows=[];end=time.monotonic()+70
for name,argv in commands:
 row={'name':name,'argv':argv,'at':dt.datetime.now(dt.timezone.utc).isoformat()}
 if time.monotonic()>=end:row['error']='BUDGET_EXHAUSTED';rows.append(row);break
 try:
  p=subprocess.run(argv,capture_output=True,timeout=min(COMMAND_TIMEOUT,end-time.monotonic()),env=dict(os.environ,LC_ALL='C',SYSTEMD_PAGER='cat'))
  row.update(rc=p.returncode,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
  if len(p.stdout)+len(p.stderr)>262144:row['error']='OUTPUT_LIMIT'
  else:row.update(stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
 except (OSError,subprocess.TimeoutExpired) as exc:row['error']=type(exc).__name__
 rows.append(row)
after=identity()
print(json.dumps({'scope':'MON_RUNTIME_READ_ONLY_INPUTS','identity_before':before,'identity_after':after,'identity_unchanged':before==after,'commands':rows,'deliberate_guest_writes':0,'credential_exports':0,'api_mutations':0,'canary_trial_requests':0}))
'''.replace('EXPECTED', repr(host)).replace('COMMANDS', repr(commands[name])).replace('COMMAND_TIMEOUT', repr(command_timeout)).encode()
    ssh = ['/usr/bin/ssh', '-T', '-i', '/home/server01_ansible/.ssh/p1_ansible_ed25519',
           '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
           '-o', 'UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts', '-o', 'IdentitiesOnly=yes',
           'svc_ansible@'+ip, 'sudo', '-n', '/usr/bin/python3', '-B', '-I', '-']
    bridge = ('import subprocess,sys\np=subprocess.run('+repr(ssh)+',input='+repr(source)+',capture_output=True,timeout=80)\n'
              'sys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    row = dict(at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),
               source_sha256=hashlib.sha256(source).hexdigest(), route='fds-ansible01 -> svc_ansible@'+ip,
               strict_host_key=True, batch_mode=True)
    p = subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe', '-T', '-o', 'BatchMode=yes',
                        '-o', 'ConnectTimeout=8', '-o', 'StrictHostKeyChecking=yes',
                        'fds-ansible01', '/usr/bin/python3', '-B', '-I', '-'],
                       input=bridge,capture_output=True,timeout=90)
    row.update(rc=p.returncode,stderr=p.stderr.decode('utf-8','replace'),stdout_sha256=hashlib.sha256(p.stdout).hexdigest())
    try: row['observation']=json.loads(p.stdout)
    except ValueError: row['error']='INVALID_RESPONSE_NO_RETRY'
    receipt.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'host':name,'ssh_rc':p.returncode,'commands':[
        {'name':r['name'],'rc':r.get('rc'),'error':r.get('error')} for r in row.get('observation',{}).get('commands',[])],
        'error':row.get('error')},ensure_ascii=False))

if __name__ == '__main__':
    collect('control01','10.1.93.102','k8s-control01')
    collect('worker03','10.1.93.108','k8s-worker03')
