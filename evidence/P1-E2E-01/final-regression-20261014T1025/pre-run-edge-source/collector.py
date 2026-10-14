import datetime,hashlib,json,os,pathlib,socket
p=pathlib.Path('/home/svc_ansible/p1-app-20261014-1025/supply/rg.py');out=p.parent.parent/'results'
print(json.dumps({'host':socket.gethostname(),'uid':os.geteuid(),'now_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'tool_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'results_exists':out.exists(),'results_entries':[x.name for x in out.iterdir()] if out.exists() else []}))
