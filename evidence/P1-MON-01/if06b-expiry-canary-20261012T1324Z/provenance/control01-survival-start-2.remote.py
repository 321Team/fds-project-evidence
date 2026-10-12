import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='80724d56-7c17-f8a0-b2ea-ece7a154e24b'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
ses=Path('/var/lib/fds-change/if06b-20261012T2110-mon01');surv=Path('/var/lib/fds-change/if06b-survival-20261012T2110-mon01')
before=subprocess.run(['loginctl','list-sessions','--no-legend'],capture_output=True,text=True)
identity=subprocess.run(['loginctl','show-session','self','-p','Id','-p','Name','-p','State'],capture_output=True,text=True)
surv.mkdir(mode=0o700,exist_ok=False)
record=['env','IF06B_RESULTS='+str(ses/'results'),'/bin/sh',str(ses/'aux/tools/record.sh')]
command=record+['4-1-survival-launch','/usr/bin/python3.12','-B',str(ses/'supply/guardian.py'),'survival-check','--evidence-dir',str(surv),'--seconds','300','--interval-seconds','5']
p=subprocess.run(command,capture_output=True,text=True,timeout=20)
output=(ses/'results/4-1-survival-launch.out').read_text()
rows=[json.loads(line) for line in output.splitlines()]
assert p.returncode==0 and len(rows)==1 and rows[0]['step']=='ARMED'
result={'step':'SURVIVAL_ARMED','dedicated_ssh_session_ends_after_this_command':True,'launch':rows,
 'session_identity':{'rc':identity.returncode,'out':identity.stdout,'err':identity.stderr},
 'sessions_before':before.stdout,'shell_environment_session_id':os.environ.get('XDG_SESSION_ID'),
 'armed_observed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'command':command,'launcher_rc':p.returncode,
 'credential_used':False,'api_calls':0,'canary_created':0}
(ses/'results/survival-launch-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
