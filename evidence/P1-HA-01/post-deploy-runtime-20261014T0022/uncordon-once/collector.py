import os,pathlib,json,socket,time,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
p=pathlib.Path('/var/tmp/p1-ha-20261014-0015');os.umask(0o077)
lines=(p/'timeline.txt').read_text().splitlines();assert len(lines)==3 and lines[-1].startswith('rescheduled_ready ')
assert time.time()-float(lines[-1].split()[1])>=61
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf']
def node():return json.loads(subprocess.check_output(kc+['--request-timeout=8s','get','node','k8s-worker02','-o','json'],timeout=10))
n=node();assert n['metadata']['uid']=='4c6eec26-153e-4da5-bf8a-f80223ca3c1b' and n['spec'].get('unschedulable') is True
assert json.loads((p/'drain-intent.json').read_bytes())['node_uid']==n['metadata']['uid']
cmd=kc+['uncordon','k8s-worker02'];receipt={'command':cmd,'started_epoch':time.time(),'started_monotonic':time.monotonic(),'node_uid':n['metadata']['uid']}
with (p/'uncordon-intent.json').open('x') as f:json.dump(receipt,f);f.flush();os.fsync(f.fileno())
r=subprocess.run(cmd,capture_output=True,timeout=20);receipt.update(rc=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode(),finished_epoch=time.time())
n=node();receipt['unschedulable']=n['spec'].get('unschedulable',False);receipt['readback_uid']=n['metadata']['uid']
if r.returncode==0 and not receipt['unschedulable'] and receipt['readback_uid']==receipt['node_uid']:
 at=time.time()
 with (p/'timeline.txt').open('a') as f:f.write('uncordon %.6f\n'%at);f.flush();os.fsync(f.fileno())
 receipt['mark_epoch']=at
with (p/'uncordon-result.json').open('x') as f:json.dump(receipt,f)
print(json.dumps(receipt))
