from pathlib import Path
import base64,datetime as dt,hashlib,io,json,re,subprocess,sys,tarfile
root=Path(__file__).resolve().parent
action=sys.argv[1];assert action in ['pre','start','fetch']
receipt=root/('field-'+action+'-receipt.json');assert not receipt.exists()
host_code='''from pathlib import Path
import base64,json,datetime as dt,os
d=Path(STAGE);f=d/'field';action=ACTION
assert d.parent==Path('/tmp') and d.name.startswith('if06b-field.') and d.stat().st_uid==os.geteuid()
out={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
if action=='pre':
 assert (f/'READY').is_file() and not (f/'GO').exists()
 assert (f/'pre.rc').read_text().strip()=='0'
 out['ready']=(f/'READY').read_text()
 out['pre']=base64.b64encode((f/'pre.tar.gz').read_bytes()).decode()
elif action=='start':
 assert (f/'READY').is_file() and not (f/'GO').exists()
 age=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat((f/'READY').read_text().strip())).total_seconds()
 assert 0<=age<240,'AUTH_READY_TOO_OLD'
 with (f/'GO').open('x') as x:x.write(out['at_utc']+'\\n')
 out['capture_start_requested']=True
else:
 assert (d/'capture.tar.gz').is_file()
 out['archive']=base64.b64encode((d/'capture.tar.gz').read_bytes()).decode()
 out['sha256sum']=(d/'capture.tar.gz.sha256').read_text()
print(json.dumps(out))
'''
bridge='''from pathlib import Path
import json,subprocess
base=Path('/home/server01_ansible/if06b-field-auth-20261012T2220')
source=SOURCE;action=ACTION;result={}
for role,target in [('gateway','server01_mgmt-gw@10.1.93.58'),('monitor','server01_monitor@10.250.10.30')]:
 stage=(base/role/'remote-stage.txt').read_text().strip()
 code=source.replace('STAGE',repr(stage)).replace('ACTION',repr(action)).encode()
 ssh=['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=5','-o','ControlPath='+str(base/role/'ssh-control'),target,'python3','-B','-I','-']
 if action=='fetch':
  # The interactive capture wrapper closes its ControlMaster after exporting.
  d=base/role
  import base64
  out={'archive':base64.b64encode((d/'capture.tar.gz').read_bytes()).decode(),'sha256sum':(d/'capture.tar.gz.sha256').read_text()}
  result[role]=out;continue
 p=subprocess.run(ssh,input=code,capture_output=True,timeout=20)
 assert p.returncode==0,role+':'+p.stderr.decode()
 result[role]=json.loads(p.stdout)
print(json.dumps(result))
'''.replace('source=SOURCE;action=ACTION;', 'source='+repr(host_code)+';action='+repr(action)+';')
compile(bridge, '<field-bridge>', 'exec')
p=subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01','python3','-B','-I','-'],input=bridge.encode(),capture_output=True,timeout=50)
row={'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'rc':p.returncode,'source_sha256':hashlib.sha256(bridge.encode()).hexdigest(),'stderr':p.stderr.decode()}
assert p.returncode==0,row
data=json.loads(p.stdout)
for role,r in data.items():
 if action in ['pre','fetch']:
  value=base64.b64decode(r.pop('pre' if action=='pre' else 'archive'))
  dest=root/(role+'-'+action+'.tar.gz');assert not dest.exists();dest.write_bytes(value)
  r['sha256']=hashlib.sha256(value).hexdigest()
  if action=='fetch':assert r['sha256']==r['sha256sum'].split()[0]
row['results']=data
receipt.write_text(json.dumps(row,indent=2)+'\n')
print(json.dumps(row))
