import datetime,json,os,socket,subprocess
assert os.geteuid()==0
p=subprocess.run(['ip','-j','route','show'],capture_output=True,timeout=10)
print(json.dumps({'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':os.environ['COLLECTOR_SHA256'],'command':['ip','-j','route','show'],'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()},indent=2))
raise SystemExit(p.returncode)
