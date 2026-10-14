import datetime,json,os,pathlib,socket,stat
assert socket.gethostname()=='cicd-runner01' and os.getuid()==1000
out=[]
for folder in ('FDS_CICD_AppWorkflow.vej0q8at','FDS_CICD_AppWorkflow.log3xwta'):
    p=pathlib.Path('/home/server01_cicd-runner')/folder/'build-scan/scan/db/cache/db/trivy.db'
    s=p.lstat()
    out.append({'path':str(p),'bytes':s.st_size,'uid':s.st_uid,'nlink':s.st_nlink,'mode':oct(stat.S_IMODE(s.st_mode)),'regular':stat.S_ISREG(s.st_mode),'symlink':p.is_symlink()})
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'read_only':True,'files':out}))
