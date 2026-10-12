import os,socket,json,subprocess,datetime as dt
from pathlib import Path
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip()=='80724d56-7c17-f8a0-b2ea-ece7a154e24b'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
os.umask(0o077)
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin',LC_ALL='C',SYSTEMD_PAGER='cat')
ses=Path('/var/lib/fds-change/if06b-20261012T2110-mon01');surv=Path('/var/lib/fds-change/if06b-survival-20261012T2110-mon01')
sessions=subprocess.run(['loginctl','list-sessions','--no-legend'],capture_output=True,text=True)
session24=subprocess.run(['loginctl','show-session','24','-p','Id','-p','Name','-p','State'],capture_output=True,text=True)
raw=(surv/'survival.jsonl').read_text()
rows=[json.loads(line) for line in raw.splitlines()]
beat=[row for row in rows if row['step']=='BEAT'];final=[row for row in rows if row['step']=='FINAL']
result={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'rows':len(rows),'beats':len(beat),
 'first':rows[0],'last':rows[-1],'final':final,'sessions_now':sessions.stdout,
 'launched_session_24':{'rc':session24.returncode,'out':session24.stdout,'err':session24.stderr},
 'raw':raw}
if 'final-2'.startswith('final'):
 result['survived']=len(final)==1 and final[0].get('disposition')=='SURVIVED_REQUESTED_DURATION' and final[0].get('evidence_complete_before_write') is True and len(beat)>0
print(json.dumps(result))
