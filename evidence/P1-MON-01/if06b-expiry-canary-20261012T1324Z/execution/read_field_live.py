from pathlib import Path
import datetime as dt
import json
import subprocess
import sys

root=Path(__file__).resolve().parent
label=sys.argv[1]
assert label.replace('-','').isalnum()
receipt=root/('field-live-'+label+'.json')
assert not receipt.exists()
host_source='''from pathlib import Path
import json,subprocess,datetime as dt
field=Path(FIELD)
result={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'field':str(field),'files':{}}
if field.is_dir():
 for p in field.rglob('*'):
  if p.is_file() and p.suffix not in ['.gz'] and p.stat().st_size<500000:
   result['files'][p.relative_to(field).as_posix()]=p.read_text(errors='replace')[-65000:]
if ROLE=='monitor':
 curl=['curl','--disable','--noproxy','*','--silent','--show-error','--fail','--connect-timeout','2','--max-time','5','--retry','0']
 queries={}
 for name,url in [('hb','http://127.0.0.1:19090/api/v1/query?query=time%28%29-timestamp%28fds_monitoring_heartbeat%29'),('alerts','http://127.0.0.1:19090/api/v1/alerts')]:
  p=subprocess.run(curl+[url],capture_output=True,text=True,timeout=7)
  queries[name]={'rc':p.returncode,'out':p.stdout,'err':p.stderr}
 result['queries']=queries
print(json.dumps(result))
'''
bridge='''from pathlib import Path
import json,subprocess
base=Path('/home/server01_ansible/if06b-field-auth-20261012T2220')
source=SOURCE
result={}
for role,target in [('gateway','server01_mgmt-gw@10.1.93.58'),('monitor','server01_monitor@10.250.10.30')]:
 stage=base/role/'remote-stage.txt'
 if not stage.exists():result[role]={'status':'AUTH_NOT_READY'};continue
 remote=stage.read_text().strip()
 assert remote.startswith('/tmp/if06b-field.') and len(remote.split('/'))==3
 code=source.replace('FIELD',repr(remote+'/field')).replace('ROLE',repr(role)).encode()
 args=['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=5',
       '-o','ControlPath='+str(base/role/'ssh-control'),target,'python3','-B','-I','-']
 p=subprocess.run(args,input=code,capture_output=True,timeout=25)
 if p.returncode:result[role]={'rc':p.returncode,'stderr':p.stderr.decode()}
 else:result[role]=json.loads(p.stdout)
print(json.dumps(result))
'''.replace('SOURCE',repr(host_source))
p=subprocess.run(['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','fds-ansible01','python3','-B','-I','-'],input=bridge.encode(),capture_output=True,timeout=55)
row={'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}
receipt.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if p.returncode:print(row)
else:
 for role,data in json.loads(row['stdout']).items():
  print(json.dumps({'role':role,'status':data.get('status'),'stderr':data.get('stderr'),
     'captures':{k:v for k,v in data.get('files',{}).items() if k.endswith(('cap-start.txt','cap-stats.txt','cap-rc.txt','pre.rc','READY','GO','completed.time'))},
     'queries':data.get('queries')},ensure_ascii=False))
