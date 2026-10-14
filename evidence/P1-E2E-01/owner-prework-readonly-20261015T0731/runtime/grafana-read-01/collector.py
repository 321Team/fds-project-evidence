MODE='grafana'
EXPECTED='k8s-control01'

import datetime as dt, glob, hashlib, json, os, pathlib, pwd, re, socket, subprocess
now=lambda: dt.datetime.now(dt.timezone.utc).isoformat()
out={'started_at_utc':now(),'host':socket.gethostname().split('.')[0],'uid':os.geteuid(),'scope':MODE,'commands':[],'status':'STARTED'}
def run(argv, allowed=(0,)):
 p=subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,timeout=18)
 if len(p.stdout)>8*1024*1024: raise RuntimeError('OUTPUT_LIMIT')
 out['commands'].append({'argv':argv,'rc':p.returncode,'stdout_bytes':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_bytes':len(p.stderr),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'at_utc':now()})
 if p.returncode not in allowed: raise RuntimeError('READ_COMMAND_FAILED: '+argv[0]+' rc='+str(p.returncode))
 return p.stdout.decode('utf-8')
def meta(p, content=False):
 p=pathlib.Path(p)
 if not p.exists(): return {'path':str(p),'exists':False}
 s=p.stat(); d={'path':str(p),'exists':True,'mode':oct(s.st_mode&0o7777),'uid':s.st_uid,'gid':s.st_gid,'size':s.st_size,'mtime_ns':s.st_mtime_ns}
 if content:
  if not p.is_file() or s.st_size>1024*1024: raise RuntimeError('UNEXPECTED_FILE')
  d['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 return d
assert out['host']==EXPECTED, 'HOST_MISMATCH'
assert (MODE=='edge' and pwd.getpwuid(os.geteuid()).pw_name=='svc_ansible') or (MODE!='edge' and out['uid']==0), 'ACCOUNT_MISMATCH'
out['boot_id']=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()

try:

 K=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=15s']
 def get(*args): return json.loads(run(K+list(args)+['-o','json']))
 out['credential_files']=[meta('/etc/kubernetes/admin.conf'),meta('/etc/kubernetes/super-admin.conf')]
 d=get('-n','monitoring-api','get','deployment','grafana')
 out['grafana']={'uid':d['metadata']['uid'],'resourceVersion':d['metadata']['resourceVersion'],'generation':d['metadata'].get('generation'),'status':d.get('status'),'serviceAccount':d['spec']['template']['spec'].get('serviceAccountName'),'secret_refs':[]}
 for c in d['spec']['template']['spec']['containers']:
  for e in c.get('env',[]):
   if e['name'] in ['GF_SECURITY_ADMIN_USER','GF_SECURITY_ADMIN_PASSWORD']:
    out['grafana']['secret_refs'].append({'container':c['name'],'env_name':e['name'],'secretKeyRef':e.get('valueFrom',{}).get('secretKeyRef'),'literal_value_present':'value' in e})
 out['human_receipt_revocation']='REQUIRES_CUSTODIAN_STATEMENT_NO_SECRET_VALUE'

 out['status']='READ_COMPLETE_REVIEW_REQUIRED'

except Exception as e:
 out['status']='READ_FAILED'; out['error_type']=type(e).__name__; out['error']=str(e)
out['ended_at_utc']=now()
print(json.dumps(out,ensure_ascii=False))
raise SystemExit(0 if out['status']=='READ_COMPLETE_REVIEW_REQUIRED' else 2)
