import sys,time
import control_runtime as r
action=sys.argv[1];assert action in ['run-watch','gate443','gate8443','complete','abort','state']
body='''import signal,time
ses=Path(SES);tok=Path(TOK);action=ACTION
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
'''.replace('Path(SES)','Path('+repr(r.SES)+')').replace('Path(TOK)','Path('+repr(r.TOK)+')').replace('action=ACTION','action='+repr(action))
r.run('control01-canary-'+action+('-'+str(time.time_ns()) if action in ['gate443','gate8443','state'] else ''),body,timeout=240 if action=='run-watch' else 35)
