import subprocess,json,datetime
cmds=[['/usr/bin/systemctl','show','kubelet','--property=ActiveState,FragmentPath,StandardOutput,StandardError'],['/usr/bin/journalctl','-u','kubelet','--since=@1791938700','--no-pager','-o','short-iso-precise','-n','30']]
rows=[]
for cmd in cmds:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=8);rows.append({'argv':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queries':rows}))
