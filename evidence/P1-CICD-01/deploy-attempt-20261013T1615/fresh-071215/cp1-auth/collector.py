import os,stat,socket,pwd,json,hashlib,subprocess,datetime,ssl,sys
from pathlib import Path
role=sys.argv[1];now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert role in ('runner','cp1')
host,user,ca_path=('cicd-runner01','server01_cicd-runner','/home/server01_cicd-runner/runner-tls-a9c89a77-20261006/kubernetes-ca.pem') if role=='runner' else ('k8s-control01','server02','/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem')
assert socket.gethostname()==host and pwd.getpwuid(os.getuid()).pw_name==user and os.getuid()==1000
out={'started_at_utc':now(),'host':host,'user':user,'uid':os.getuid(),'token_issued':False,'credential_content_exported':False,'mutation':False,'paths':[]}
ca=Path(ca_path)
for p in [ca,*ca.parents]:
 s=p.lstat();out['paths'].append({'path':str(p),'uid':s.st_uid,'mode':oct(stat.S_IMODE(s.st_mode)),'symlink':p.is_symlink()})
 assert not p.is_symlink() and s.st_uid in (0,os.getuid()) and not stat.S_IMODE(s.st_mode)&0o022
raw=ca.read_bytes();out['ca_sha256']=hashlib.sha256(raw).hexdigest();assert out['ca_sha256']=='5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c'
if role=='runner':
 ctx=ssl.create_default_context(cafile=str(ca));assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
 with socket.create_connection(('10.1.93.109',6443),timeout=8) as s:
  with ctx.wrap_socket(s,server_hostname='10.1.93.109') as tls:
   out['api_tls']={'verified':True,'tls_version':tls.version(),'leaf_der_sha256':hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest(),'api_authentication':'NOT_TESTED'}
else:
 config=Path('/home/server02/.kube/config');s=config.lstat()
 out['config_metadata']={'path':str(config),'uid':s.st_uid,'mode':oct(stat.S_IMODE(s.st_mode)),'symlink':config.is_symlink()}
 assert not config.is_symlink() and s.st_uid==os.getuid() and not stat.S_IMODE(s.st_mode)&0o077
 argv=['/usr/bin/kubectl','--kubeconfig='+str(config),'--server=https://10.1.93.109:6443','--certificate-authority='+str(ca),'--request-timeout=10s','get','--raw=/api/v1/namespaces/ci-cd/serviceaccounts/cicd-runner-sa']
 p=subprocess.run(argv,capture_output=True,timeout=20)
 out['api_get']={'argv':argv,'rc':p.returncode,'raw_stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
 if p.returncode==0:
  d=json.loads(p.stdout);out['api_get']['metadata']={k:d['metadata'].get(k) for k in ['name','namespace','uid']}
out['finished_at_utc']=now();print(json.dumps(out))
