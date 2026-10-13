"""Place only the fixed input collectors in a new private ansible01 folder."""
from pathlib import Path
import base64
import datetime as dt
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parent
receipt=root/'auth-stage-receipt.json'
if receipt.exists():raise SystemExit('STOP: stage receipt already exists')
prep=json.loads((root/'auth-preparation.json').read_text())
files={name:base64.b64encode((root/'auth-inputs'/name).read_bytes()).decode() for name in prep['files']}
remote='''import os,socket,json,base64,hashlib
from pathlib import Path
assert socket.gethostname().split('.')[0]=='ansible01'
assert os.geteuid()!=0
os.umask(0o077)
stage=Path(STAGE)
assert stage.parent==Path('/home/server01_ansible')
stage.mkdir(mode=0o700,exist_ok=False)
files=FILES
expected=EXPECTED
actual={}
for name,encoded in files.items():
 p=stage/name
 assert p.is_relative_to(stage) and '..' not in Path(name).parts
 p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(base64.b64decode(encoded))
 actual[name]=hashlib.sha256(p.read_bytes()).hexdigest()
 assert actual[name]==expected[name]
print(json.dumps({'stage':str(stage),'mode':oct(stage.stat().st_mode & 0o777),'hashes':actual,'runtime_collection':'NOT_RUN','policy_or_service_changes':0}))
'''.replace('STAGE',repr(prep['remote_stage'])).replace('FILES',repr(files)).replace('EXPECTED',repr(prep['files']))
p=subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
                  '-o','ConnectTimeout=8','fds-ansible01','/usr/bin/python3','-B','-I','-'],input=remote.encode(),capture_output=True,timeout=25)
row={'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'rc':p.returncode,
     'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'remote_source_sha256':hashlib.sha256(remote.encode()).hexdigest()}
receipt.write_text(json.dumps(row,indent=2)+'\n')
assert p.returncode==0,row['stderr']
data=json.loads(row['stdout']);assert data['hashes']==prep['files']
print(json.dumps({'stage':data['stage'],'mode':data['mode'],'verified_files':len(data['hashes']),'collection':'NOT_RUN'}))
