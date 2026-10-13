import datetime,hashlib,json,os,pathlib,pwd,socket,stat
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
expected={'/home/server01_cicd-runner/FDS_CICD_DeployInputs/deploy-37a528cd-184a-4e0f-8f17-62416ca2e4e4.json': 'fb8b603e6e9ee4449767d74a5d22fb864c1ef7a0a11d75e1eef0c3144d1c58db'}
rows=[]
for name,digest in expected.items():
 p=pathlib.Path(name)
 for parent in p.parents:
  s=parent.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid in (0,1000) and not s.st_mode&0o022
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==1000 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,"rb") as f:raw=f.read(1048577)
 assert len(raw)<=1048576 and hashlib.sha256(raw).hexdigest()==digest
 rows.append({"path":name,"sha256":digest,"uid":s.st_uid,"mode":oct(stat.S_IMODE(s.st_mode)),"regular":True,"nlink":s.st_nlink})
print(json.dumps({"at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"read_only":True,"files":rows}))
