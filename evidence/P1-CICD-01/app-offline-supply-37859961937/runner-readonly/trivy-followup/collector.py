"""Follow-up for observed 168456354-byte binary; read/hash only, no execution."""
import datetime,hashlib,json,os,pathlib,pwd,socket,stat
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert socket.gethostname().split('.')[0]=='cicd-runner01' and os.getuid()==os.geteuid()==1000 and pwd.getpwuid(1000).pw_name=='server01_cicd-runner'
assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'
start=now();path=pathlib.Path('/usr/local/bin/trivy');assert path.resolve()==path
fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
with os.fdopen(fd,'rb') as f:
    a=os.fstat(f.fileno());assert stat.S_ISREG(a.st_mode) and a.st_size==168456354 and a.st_size<192*1024*1024
    h=hashlib.sha256();total=0
    while chunk:=f.read(1024*1024):
        total+=len(chunk);assert total<=192*1024*1024;h.update(chunk)
    b=os.fstat(f.fileno());c=path.lstat()
sig=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
assert sig(a)==sig(b)==sig(c) and total==a.st_size
expected='d89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791'
print(json.dumps({'schema':'fds.runner-trivy-hash.v1','host':socket.gethostname(),'account':pwd.getpwuid(1000).pw_name,'started_at_kst':start,'finished_at_kst':now(),'path':str(path),'size':a.st_size,'uid':a.st_uid,'gid':a.st_gid,'mode':oct(stat.S_IMODE(a.st_mode)),'stable':True,'sha256':h.hexdigest(),'expected_sha256':expected,'matches_consumer_pin':h.hexdigest()==expected,'binary_execution':'NOT_RUN','db_freshness':'NOT_QUERIED'},indent=2))
