from pathlib import Path
import datetime as dt,hashlib,json,subprocess
R=Path(__file__).resolve().parent
def run(name,source,timeout=100):
 folder=R/name;folder.mkdir(exist_ok=False);raw=source.encode();compile(source,'controller','exec');(folder/'collector.py').write_bytes(raw)
 cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-']
 d={'started_at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'command':cmd,'source_sha256':hashlib.sha256(raw).hexdigest()}
 try:
  p=subprocess.run(cmd,input=raw,capture_output=True,timeout=timeout);stdout,stderr=p.stdout,p.stderr;d['rc']=p.returncode
 except subprocess.TimeoutExpired as e:stdout,stderr=e.stdout or b'',e.stderr or b'';d.update(rc=None,error='TRANSPORT_TIMEOUT_NO_RETRY')
 (folder/'stdout.json').write_bytes(stdout);(folder/'stderr.txt').write_bytes(stderr)
 d.update(finished_at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),stdout_sha256=hashlib.sha256(stdout).hexdigest(),stderr_sha256=hashlib.sha256(stderr).hexdigest());(folder/'receipt.json').write_bytes((json.dumps(d,indent=2)+'\n').encode())
 print(json.dumps({'name':name,'rc':d['rc'],'bytes':len(stdout)}));return d
