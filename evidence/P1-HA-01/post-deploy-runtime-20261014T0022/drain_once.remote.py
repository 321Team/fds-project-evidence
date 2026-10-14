import os,pathlib,json,socket,time,datetime,subprocess,hashlib
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360'
p=pathlib.Path('/var/tmp/p1-ha-20261014-0015');os.umask(0o077)
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf']
def get(args):
 r=subprocess.run(kc+['--request-timeout=10s','get']+args+['-o','json'],capture_output=True,timeout=15)
 assert r.returncode==0,r.stderr.decode()
 return json.loads(r.stdout)
def digest(s):return hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert get(['ns','kube-system'])['metadata']['uid']=='e1669cff-1435-423f-a6c4-28bc44f488de'
nodes=get(['nodes'])['items'];assert len(nodes)==6
for n in nodes:
 conditions={x['type']:x['status'] for x in n['status']['conditions']}
 assert conditions['Ready']=='True' and all(conditions[k]=='False' for k in ('MemoryPressure','DiskPressure','PIDPressure'))
 if n['metadata']['name'].startswith('k8s-worker'):assert not n['spec'].get('unschedulable') and not n['spec'].get('taints')
node=next(n for n in nodes if n['metadata']['name']=='k8s-worker02');assert node['metadata']['uid']=='4c6eec26-153e-4da5-bf8a-f80223ca3c1b'
expected={'transaction-api':('8a2af808-ec33-41f2-80b5-addde4e28910',12,'b6b4048d5288a42ee0be5fa3fdd3f2ef82c7659687c0adb9ed61a19d7b8a563a'),'fds-engine':('bf825dec-465b-4603-8b71-f768d195531c',6,'0a1d36ae1fda7513b69fa3d1df7ca91983c05770f44df0ebc940c516f8d1faf3')}
for d in get(['deployments','-n','fds-app'])['items']:
 assert (d['metadata']['uid'],d['metadata']['generation'],digest(d['spec']))==expected[d['metadata']['name']]
 assert all(d['status'].get(k)==3 for k in ('replicas','readyReplicas','updatedReplicas','availableReplicas'))
pods=get(['pods','-n','fds-app'])['items']
assert {x['metadata']['uid'] for x in pods}=={'9d34d371-5839-429b-b255-a9a4a6ebdd31','da814b7b-1a35-4ce9-8719-eedee3d7936d','4d0b362b-5081-4745-b68a-85636e08dc10','4ab7c0a7-c7aa-4f0c-9a63-642a752dbe51','533caef6-e244-451a-96d1-8d4de9f40983','1b2f1c14-a04f-438c-b051-4d65a0a8a8e7'}
for pod in pods:
 assert not pod['metadata'].get('deletionTimestamp') and pod['status']['phase']=='Running'
 assert all(c['ready'] and c['restartCount']==0 for c in pod['status']['containerStatuses'])
selected=get(['pods','-A','--field-selector=spec.nodeName=k8s-worker02','--selector=app in (transaction-api,fds-engine)'])['items']
assert len(selected)==2 and {x['metadata']['uid'] for x in selected}=={'533caef6-e244-451a-96d1-8d4de9f40983','da814b7b-1a35-4ce9-8719-eedee3d7936d'} and all(x['metadata']['namespace']=='fds-app' for x in selected)
assert not get(['pdb','-n','fds-app'])['items'] and not get(['hpa','-n','fds-app'])['items']
assert any(r['name']=='pods/eviction' and r['kind']=='Eviction' for r in json.loads(subprocess.check_output(kc+['get','--raw=/api/v1']))['resources'])
lines=(p/'timeline.txt').read_text().splitlines();assert len(lines)==1 and lines[0].startswith('baseline_start ')
at=time.time();assert at-float(lines[0].split()[1])>=61
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-13T15:25:00+00:00')
cmd=kc+['drain','k8s-worker02','--pod-selector=app in (transaction-api,fds-engine)','--ignore-daemonsets','--timeout=180s']
receipt={'started_epoch':at,'started_monotonic':time.monotonic(),'command':cmd,'selected_pods':[{'name':x['metadata']['name'],'uid':x['metadata']['uid'],'resourceVersion':x['metadata']['resourceVersion']} for x in selected],'node_uid':node['metadata']['uid'],'run_count':1}
with (p/'drain-intent.json').open('x') as f:json.dump(receipt,f);f.flush();os.fsync(f.fileno())
with (p/'timeline.txt').open('a') as f:f.write('drain_start %.6f\n'%at);f.flush();os.fsync(f.fileno())
try:
 r=subprocess.run(cmd,capture_output=True,timeout=190);receipt.update(rc=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode())
except subprocess.TimeoutExpired as e:
 receipt.update(rc=None,error='TIMEOUT_NO_RETRY',stdout=(e.stdout or b'').decode(),stderr=(e.stderr or b'').decode())
receipt.update(finished_epoch=time.time(),finished_monotonic=time.monotonic())
with (p/'drain-result.json').open('x') as f:json.dump(receipt,f)
print(json.dumps(receipt))
