import json,subprocess,datetime,socket
cmd=['/usr/bin/journalctl','-u','kubelet','--since','2026-10-14 00:45:00 UTC','--no-pager','-o','short-iso-precise','--grep=e349b045-870f-4061-a677-3007efe479e9|fds-engine-65479b5bf-4gfgq']
p=subprocess.run(cmd,capture_output=True,text=True,timeout=8)
print(json.dumps({'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}))
