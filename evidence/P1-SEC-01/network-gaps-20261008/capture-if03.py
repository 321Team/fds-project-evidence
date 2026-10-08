import datetime,json,os,socket,subprocess,time
assert os.geteuid()==0 and socket.gethostname().split('.')[0] in ('k8s-worker01','k8s-worker02','k8s-worker03')
def rules():
 p=subprocess.run(['iptables-save','-c','-t','filter'],capture_output=True,timeout=10)
 return {'rc':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}
r={'host':socket.gethostname(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':os.environ['COLLECTOR_SHA256'],'before':rules()}
assert r['before']['rc']==0
cmd=['tcpdump','-i','any','-n','-l','-tttt','-s','80','-c','24','tcp and src host 10.244.246.121 and dst port 8001 and src portrange 55801-55803']
p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
time.sleep(1)
assert p.poll() is None,'CAPTURE_FAILED'
print('CAPTURE_READY',flush=True)
try:out,err=p.communicate(timeout=24)
except subprocess.TimeoutExpired:
 p.terminate();out,err=p.communicate(timeout=5)
r.update(command=cmd,stdout=out.decode(),stderr=err.decode(),rc=p.returncode,after=rules(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
print(json.dumps(r,indent=2))
