import os,pathlib,json,socket,time,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
p=pathlib.Path('/var/tmp/p1-ha-20261014-0015');os.umask(0o077)
lines=(p/'timeline.txt').read_text().splitlines();assert len(lines)==4 and lines[-1].startswith('uncordon ')
assert time.time()-float(lines[-1].split()[1])>=61
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=8s']
n=json.loads(subprocess.check_output(kc+['get','node','k8s-worker02','-o','json'],timeout=10))
assert n['metadata']['uid']=='4c6eec26-153e-4da5-bf8a-f80223ca3c1b' and not n['spec'].get('unschedulable',False)
at=time.time()
with (p/'timeline.txt').open('a') as f:f.write('end %.6f\n'%at);f.flush();os.fsync(f.fileno())
print(json.dumps({'mark':'end','epoch':at,'timeline':(p/'timeline.txt').read_text(),'unschedulable':n['spec'].get('unschedulable',False)}))
