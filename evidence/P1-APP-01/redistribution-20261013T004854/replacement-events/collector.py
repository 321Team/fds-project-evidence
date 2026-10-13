import datetime,hashlib,json,os,socket,subprocess
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
uids=['072f5760-ac0c-479c-84da-54211a8a2ea6', '8e92a558-d243-4f92-8f58-34d10e32b663', 'e7e7992e-959c-4fb2-a36a-ea2d5a5f1354', '3f8b99ac-fe41-4032-8179-e206c75e96ec']
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'queries':[],'scope':'new four Pods event reads; no mutation'}
for uid in uids:
 cmd=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s','get','events','-n','fds-app','--field-selector=involvedObject.uid='+uid,'-o','json']
 p=subprocess.run(cmd,capture_output=True,timeout=8)
 row={'uid':uid,'argv':cmd,'rc':p.returncode,'stderr':p.stderr.decode(),'response_sha256':hashlib.sha256(p.stdout).hexdigest()}
 if p.returncode==0:
  row['events']=[{k:e.get(k) for k in ['reason','message','type','firstTimestamp','lastTimestamp','count','source','involvedObject']} for e in json.loads(p.stdout)['items']]
 out['queries'].append(row)
out['status']='READ_COMPLETE' if all(x['rc']==0 for x in out['queries']) else 'INCOMPLETE';print(json.dumps(out))
