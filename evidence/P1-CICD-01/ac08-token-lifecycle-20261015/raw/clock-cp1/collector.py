"""Read current UTC, kernel clock sync indicator, and pinned API version only."""
import datetime as dt,hashlib,json,os,pwd,socket,subprocess,time
from pathlib import Path
host=socket.gethostname();assert host in ('k8s-control01','cicd-runner01','ansible01')
expected={'k8s-control01':'server02','cicd-runner01':'server01_cicd-runner','ansible01':'server01_ansible'}[host]
assert pwd.getpwuid(os.getuid()).pw_name==expected
out={'host':host,'user':expected,'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'monotonic':time.monotonic(),'mutation':False}
p=subprocess.run(['/usr/bin/timedatectl','show','--property=NTPSynchronized','--value'],capture_output=True,timeout=5)
out['ntp_synchronized']={'rc':p.returncode,'value':p.stdout.decode().strip() if p.stdout.strip() in (b'yes',b'no') else 'UNCONFIRMED'}
if host=='k8s-control01':
    argv=['/usr/bin/kubectl','--kubeconfig=/home/server02/.kube/config','--server=https://10.1.93.109:6443',
          '--certificate-authority=/home/server02/FDS_CICD_PublicCA.uua3ecs6/kubernetes-ca.pem','--request-timeout=5s','get','--raw=/version']
    p=subprocess.run(argv,capture_output=True,timeout=7)
    out['api_version']={'rc':p.returncode,'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
    if p.returncode==0:out['api_version']['gitVersion']=json.loads(p.stdout)['gitVersion']
print(json.dumps(out))
