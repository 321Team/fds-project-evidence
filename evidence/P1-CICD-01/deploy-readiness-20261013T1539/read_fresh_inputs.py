"""Reuse fixed read-only collectors; write receipts only on this workstation."""
import concurrent.futures,datetime,hashlib,json,pathlib,shlex,subprocess
OUT=pathlib.Path(__file__).parent
OLD=OUT.parent/'p1-delivery-runner-20261013'
def run(item):
    name,host,user,key,sudo,source,args=item
    d=OUT/name;d.mkdir(exist_ok=False)
    raw=(OLD/source).read_bytes();compile(raw,source,'exec');(d/'collector.py').write_bytes(raw)
    remote=(['sudo','-n'] if sudo else [])+['/usr/bin/python3','-B','-I','-S','-',*args]
    inner=['/usr/bin/ssh','-F','/dev/null','-T','-i',key,'-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no','-o','ControlPath=none','-o','UpdateHostKeys=no',user+'@'+host,shlex.join(remote)]
    bridge=('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(raw)+',capture_output=True,timeout=100)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    outer=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-S','-']
    receipt={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'outer_argv':outer,'inner_argv':inner,'source_sha256':hashlib.sha256(raw).hexdigest(),'classification':'PURE_READ_PRECHECK','review':'NOT PERFORMED (Pre-check)','token_issued':False,'server_files_written':False}
    try:
        p=subprocess.run(outer,input=bridge,capture_output=True,timeout=110);stdout,stderr=p.stdout,p.stderr;receipt['rc']=p.returncode
    except subprocess.TimeoutExpired as e:
        stdout,stderr=e.stdout or b'',e.stderr or b'';receipt.update(rc=None,error='TIMEOUT_NO_RETRY')
    (d/'stdout.json').write_bytes(stdout);(d/'stderr.txt').write_bytes(stderr)
    receipt.update(finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdout_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest())
    (d/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return {'name':name,'rc':receipt['rc'],'stdout_bytes':len(stdout),'stderr_bytes':len(stderr)}
targets=[('cluster','10.1.93.102','svc_ansible','/home/server01_ansible/.ssh/p1_ansible_ed25519',True,'cluster_read.py',[]),('cp1-auth','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,'auth_path_read.py',['cp1']),('runner-auth','10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,'auth_path_read.py',['runner'])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for result in pool.map(run,targets):print(json.dumps(result),flush=True)
