TIMELINE='YmFzZWxpbmVfc3RhcnQgMTc5MTkwNDk4MC40ODI3NTYKZHJhaW5fc3RhcnQgMTc5MTkwNTA2Mi4wNjMxOTEKcmVzY2hlZHVsZWRfcmVhZHkgMTc5MTkwNTA5OS43MjI5MjEKdW5jb3Jkb24gMTc5MTkwNTE3Ny45ODQ2NzMKZW5kIDE3OTE5MDUyNjguMTM2MjA1Cg=='
SHA='050bb8899236d42d3929b8ff22b2296f77a1e7401bd90e6cfa924bfc3c9333d2'
import os,pathlib,socket,json,hashlib,base64,subprocess,time
assert socket.gethostname()=='edge01' and os.geteuid()==1003
p=pathlib.Path('/home/svc_ansible/p1-ha-20261014-0015');os.umask(0o077)
result=json.loads((p/'probe-result.json').read_bytes());assert result['rc']==0 and result['child_exited']
assert hashlib.sha256((p/'ha-judge.py').read_bytes()).hexdigest()=='79f54c955991dacd0767885b0db5001fad39080ea7cf4b7c2a3ea13c6f1a6aad'
raw=base64.b64decode(TIMELINE);assert hashlib.sha256(raw).hexdigest()==SHA
with (p/'timeline.txt').open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
cmd=['/usr/bin/python3',str(p/'ha-judge.py'),str(p/'probe.log'),str(p/'timeline.txt'),'10.1.93.107']
r=subprocess.run(cmd,capture_output=True,timeout=15)
for name,data in [('judge.stdout',r.stdout),('judge.stderr',r.stderr)]:
 with (p/name).open('xb') as f:f.write(data)
receipt={'epoch':time.time(),'command':cmd,'rc':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode(),'timeline_sha256':SHA,'probe_log_sha256':hashlib.sha256((p/'probe.log').read_bytes()).hexdigest()}
with (p/'judge-result.json').open('x') as f:json.dump(receipt,f)
print(json.dumps(receipt))
