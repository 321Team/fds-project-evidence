import subprocess,json,socket
assert socket.gethostname()=='k8s-worker01'
p=subprocess.run(['/usr/bin/ctr','images','check','--help'],capture_output=True,text=True,timeout=8)
print(json.dumps({'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}))
