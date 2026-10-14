
import datetime as dt,json,os,pathlib,socket,subprocess
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
image='quay.io/sclorg/postgresql-16-c9s@sha256:d33717fd33c1a4b11afef94568d0c20812a19d62fb8c633fadee1e491e2edd4a'
p=subprocess.run(['podman','image','inspect',image],capture_output=True,text=True,timeout=12)
out={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'read_only':True,'inspect_rc':p.returncode}
if p.returncode==0:
    obj=json.loads(p.stdout)[0];out['image']={k:obj.get(k) for k in ('Id','RepoDigests','Architecture','Os','Digest','Names')};out['image']['User']=obj.get('Config',{}).get('User')
out['containers']=json.loads(subprocess.check_output(['podman','ps','-a','--format','json'],timeout=10))
out['runtime_claim_exists']=pathlib.Path('/home/server01_cicd-runner/FDS_D03_Claims/202610142110.json').exists()
print(json.dumps(out))
