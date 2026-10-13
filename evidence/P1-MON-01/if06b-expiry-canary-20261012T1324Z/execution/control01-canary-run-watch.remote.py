import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='80724d56-7c17-f8a0-b2ea-ece7a154e24b'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
import signal,time
ses=Path('/var/lib/fds-change/if06b-20261012T2220-mon02');tok=Path('/run/fds-if06b-20261012T2220-mon02');action='run-watch'
res=ses/'results';aux=ses/'aux';py='/usr/bin/python3.12'
record=['env','IF06B_RESULTS='+str(res),'/bin/sh',str(aux/'tools/record.sh')]
def rec(name,argv,timeout=20):
 p=subprocess.run(record+[name]+argv,capture_output=True,text=True,timeout=timeout)
 return {'rc':p.returncode,'out':(res/(name+'.out')).read_text(),'err':(res/(name+'.err')).read_text()}
if action=='run-watch':
 owners=json.loads((res/'owned-rbac-through-crb.json').read_text())
 claim=rec('7-0-token-claims',[py,'-B',str(aux/'tools/tokeninfo.py'),str(tok/'token'),'system:serviceaccount:monitoring-api:p1-mon-if06b-guardian',owners['sa']['uid'],'900','210'])
 assert claim['rc']==0
 launch=rec('7-1-run-launch',[py,'-B',str(ses/'supply/guardian.py'),'run','--config',str(ses/'input.json')])
 assert launch['rc']==0 and any(json.loads(line).get('step')=='ARMED' for line in launch['out'].splitlines()),'NOT_ARMED'
 with (res/'watch-transport-pid').open('x') as f:f.write(str(os.getpid()))
 watch=rec('7-2-watch',[py,'-B',str(ses/'supply/guardian.py'),'watch','--journal-dir',str(ses/'journal'),'--poll-seconds','2','--window-seconds','200'],timeout=210)
 print(json.dumps({'launch':launch,'watch':watch}))
elif action.startswith('gate'):
 assert not (res/'7-2-watch.rc').exists(),'WATCH_RETURNED'
 assert not (res/'7-4-abort.time').exists(),'ABORT_ALREADY_REQUESTED'
 pid=int((res/'watch-transport-pid').read_text());assert Path('/proc',str(pid)).exists(),'WATCH_TRANSPORT_GONE'
 gate=rec('7-3-'+action+'-'+str(time.time_ns()),[py,'-B',str(aux/'tools/gate.py'),str(ses/'input.json'),str(ses/'evidence/supervisor.jsonl'),'40' if action=='gate443' else '28'])
 print(json.dumps(gate))
elif action in ['complete','abort']:
 ident=rec('7-4-'+action+'-ident',[py,'-B',str(aux/'tools/ident.py'),str(ses/'input.json'),str(ses/'evidence/supervisor.jsonl')])
 assert ident['rc']==0 and ident['out'].startswith('GUARDIAN_ALIVE pid=')
 pid=int(ident['out'].split('pid=')[1].strip())
 sent=rec('7-4-'+action,['/bin/kill','-USR2' if action=='complete' else '-USR1',str(pid)])
 print(json.dumps({'ident':ident,'signal':sent}))
else:
 rows=[json.loads(line) for line in (ses/'evidence/supervisor.jsonl').read_text().splitlines()]
 watch_rc=(res/'7-2-watch.rc').read_text() if (res/'7-2-watch.rc').exists() else None
 print(json.dumps({'rows':rows,'watch_rc':watch_rc,'watch_out':(res/'7-2-watch.out').read_text() if (res/'7-2-watch.out').exists() else None}))
