import concurrent.futures,datetime,hashlib,json,pathlib,shlex,subprocess
OUT=pathlib.Path(__file__).parent
raw=(OUT/'rollback_cache_read.py').read_bytes();compile(raw,'rollback_cache_read.py','exec')
def run(item):
    name,ip=item;d=OUT/('cache-'+name);d.mkdir(exist_ok=False)
    (d/'collector.py').write_bytes(raw)
    inner=['/usr/bin/ssh','-F','/dev/null','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no','-o','ControlPath=none','-o','UpdateHostKeys=no','svc_ansible@10.1.93.'+ip,'sudo -n /usr/bin/python3 -B -I -S -']
    bridge=('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(raw)+',capture_output=True,timeout=30)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    outer=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-S','-']
    receipt={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'outer_argv':outer,'inner_argv':inner,'source_sha256':hashlib.sha256(raw).hexdigest(),'classification':'PURE_READ_PRECHECK','review':'NOT PERFORMED (Pre-check)','server_files_written':False}
    r=subprocess.run(outer,input=bridge,capture_output=True,timeout=40)
    (d/'stdout.json').write_bytes(r.stdout);(d/'stderr.txt').write_bytes(r.stderr)
    receipt.update(rc=r.returncode,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
    (d/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return {'host':name,'rc':r.returncode,'stdout_bytes':len(r.stdout),'stderr_bytes':len(r.stderr)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for r in pool.map(run,[('worker01','105'),('worker02','107'),('worker03','108')]):print(json.dumps(r))
