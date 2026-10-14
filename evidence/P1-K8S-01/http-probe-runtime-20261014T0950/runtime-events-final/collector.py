import pathlib,json,socket,os,datetime,subprocess
assert socket.gethostname()=='k8s-worker02' and os.geteuid()==0
p=pathlib.Path('/var/tmp/p1-http-probe-20261014-0945')
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'files':{}}
for name in ('input.json','events.jsonl'):
 f=p/name
 out['files'][name]={'text':f.read_text(),'uid':f.stat().st_uid,'mode':oct(f.stat().st_mode&0o777)}
cmd=['/usr/bin/journalctl','-u','kubelet','--since','2026-10-14 09:45:00','--no-pager','-o','short-iso-precise','--grep=e349b045-870f-4061-a677-3007efe479e9|fds-engine-65479b5bf-4gfgq']
r=subprocess.run(cmd,capture_output=True,text=True,timeout=8)
out['journal']={'argv':cmd,'rc':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
print(json.dumps(out))
