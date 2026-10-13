import os,pathlib,json,socket,time,hashlib
assert socket.gethostname()=='edge01' and os.geteuid()==1003
p=pathlib.Path('/home/svc_ansible/p1-ha-20261014-0015')
start=json.loads((p/'probe-start.json').read_bytes())
raw=(p/'probe.log').read_bytes()
rows=[line.split() for line in raw.decode().splitlines()]
assert rows and all(len(r)==7 for r in rows)
out={'at_epoch':time.time(),'start':start,'rows':len(rows),'first_sched':min(float(r[1]) for r in rows),'last_sched':max(float(r[1]) for r in rows),'non200':sum(r[4]!='200' for r in rows),'max_late':max(float(r[2])-float(r[1]) for r in rows),'stdout':(p/'probe.stdout').read_text(),'stderr':(p/'probe.stderr').read_text(),'probe_log':raw.decode(),'probe_log_sha256':hashlib.sha256(raw).hexdigest(),'result':json.loads((p/'probe-result.json').read_bytes()) if (p/'probe-result.json').exists() else None}
try:os.kill(start['pid'],0);out['process_exists']=True
except ProcessLookupError:out['process_exists']=False
print(json.dumps(out))
