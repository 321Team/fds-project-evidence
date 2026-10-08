import base64,datetime,hashlib,json,os,pathlib,subprocess
root=pathlib.Path('/root/sec01-probe-20261008-98hudpso')
assert json.loads((root/'run.result.json').read_text())['rc']==3
K=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
for args in [['-n','fds-app','get','events','--field-selector','involvedObject.uid=0c0491c7-fd89-45b4-b677-44dfc6f4bd9c','-o','json'],['-n','fds-app','get','pod,svc','-l','sec01-probe-test=1008001645-22503-9859','-o','json'],['get','nodes','-o','json']]:
 q=subprocess.run(K+args,capture_output=True,timeout=15);result['commands'].append({'argv':q.args,'rc':q.returncode,'stdout':q.stdout.decode(),'stderr':q.stderr.decode()})
(root/'post-readonly.json').write_text(json.dumps(result,indent=2)+'\n')
files={}
for f in root.rglob('*'):
 if f.is_file() and not f.is_symlink():
  data=f.read_bytes();files[f.relative_to(root).as_posix()]={'base64':base64.b64encode(data).decode(),'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'mode':oct(f.stat().st_mode&0o777)}
print(json.dumps({'root':str(root),'files':files}))
