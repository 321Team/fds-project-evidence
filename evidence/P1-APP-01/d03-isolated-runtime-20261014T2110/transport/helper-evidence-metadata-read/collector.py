
import base64,hashlib,json,os,pathlib,socket,stat,datetime as dt,subprocess
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
root=pathlib.Path('/home/server01_cicd-runner/FDS_D03_Precheck.ezn5ka16')
allowed={'started_at.txt','hostname.txt','identity.txt','command.json','stdout.txt','stderr.txt','rc.txt','finished_at.txt','result.json'}
manifest=(root/'SHA256SUMS').read_bytes(); result={'at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'read_only':True,'precheck_directory':str(root),'files':[]}
listed=set()
for line in manifest.decode().splitlines():
    digest,name=line.split('  ',1)
    assert name in allowed and name not in listed
    listed.add(name);p=root/name;st=p.lstat()
    assert stat.S_ISREG(st.st_mode) and st.st_uid==1000 and st.st_size<50000
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    result['files'].append({'name':name,'sha256':digest,'base64':base64.b64encode(raw).decode()})
assert listed==allowed
result['files'].append({'name':'SHA256SUMS','sha256':hashlib.sha256(manifest).hexdigest(),'base64':base64.b64encode(manifest).decode()})
image='quay.io/sclorg/postgresql-16-c9s@sha256:d33717fd33c1a4b11afef94568d0c20812a19d62fb8c633fadee1e491e2edd4a'
result['db_metadata']={}
for mode in ('--raw','--config'):
    argv=['/usr/bin/skopeo','inspect','--no-creds','--tls-verify=true',mode,'docker://'+image]
    p=subprocess.run(argv,capture_output=True,timeout=18)
    row={'argv':argv,'rc':p.returncode,'stderr':p.stderr.decode(),'raw_sha256':hashlib.sha256(p.stdout).hexdigest()}
    if p.returncode==0:
        obj=json.loads(p.stdout)
        row['metadata']=obj if mode=='--raw' else {k:obj.get(k) for k in ('created','architecture','os')}
        if mode=='--config':row['metadata']['config']={k:obj.get('config',{}).get(k) for k in ('User','Entrypoint','Cmd')}
    result['db_metadata'][mode]=row
result['finished_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
print(json.dumps(result))
