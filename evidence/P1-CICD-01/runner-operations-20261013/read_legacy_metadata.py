"""Read only the 28 already identified packet paths. Never read file contents."""
import datetime as dt
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
old=json.loads((HERE.parent/'p1-runner81-execution-20261013/ADMIN_PACKET_METADATA.json').read_text())
paths=[r['path'] for r in old['packets']]
assert len(paths)==len(set(paths))==28
script='''import datetime,json,os,pathlib,pwd,socket,stat
paths=TARGET_PATHS
rows=[]
for name in paths:
 p=pathlib.Path(name)
 assert p.parent==pathlib.Path('/home/server01_ansible') and p.name.startswith('ansible-runner-token-') and p.suffix=='.json'
 s=p.lstat()
 rows.append({'path':name,'dev':s.st_dev,'ino':s.st_ino,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),
  'regular':stat.S_ISREG(s.st_mode),'nlink':s.st_nlink,'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,
  'mtime_utc':datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone.utc).isoformat(),
  'ctime_utc':datetime.datetime.fromtimestamp(s.st_ctime,datetime.timezone.utc).isoformat()})
print(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),
 'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'uid':os.getuid(),'user':pwd.getpwuid(os.getuid()).pw_name,
 'scope':'lstat only; no packet contents or token hashes; no mutation','packets':rows}))
'''.replace('TARGET_PATHS',repr(paths))
(HERE/'legacy-metadata-collector.py').write_text(script,encoding='utf-8')
cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8',
     'fds-ansible01','python3 -I -B -']
assert not (HERE/'LEGACY_FRESH_METADATA.json').exists()
started=dt.datetime.now(dt.timezone.utc).isoformat()
p=subprocess.run(cmd,input=script.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40)
(HERE/'legacy-metadata.stderr.txt').write_bytes(p.stderr)
(HERE/'legacy-metadata.receipt.json').write_text(json.dumps({'started_at_utc':started,'rc':p.returncode,'command':cmd,'scope':'read-only metadata'},indent=2)+'\n')
if p.returncode:raise SystemExit('Read failed; see receipt')
new=json.loads(p.stdout)
(HERE/'LEGACY_FRESH_METADATA.json').write_bytes(p.stdout)
assert new['host']=='ansible01' and new['uid']==1000 and new['user']=='server01_ansible'
assert new['boot']=='fbbc1743-871f-44a8-914e-20186ce38d48'
lookup={r['path']:r for r in old['packets']}
for r in new['packets']:
 assert all(r[k]==lookup[r['path']][k] for k in ('uid','mode','regular','mtime_utc','ctime_utc'))
 assert r['nlink']==1
print(json.dumps({'status':'28_PATHS_METADATA_UNCHANGED','observed_at_utc':new['observed_at_utc'],'host':new['host'],'deleted':0}))
