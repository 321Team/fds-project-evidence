"""Fixed-path readiness observations only; no Podman info/load, scan or credentials."""
import datetime,hashlib,json,os,pathlib,pwd,shutil,socket,stat,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def gate():
    assert socket.gethostname().split('.')[0]=='cicd-runner01' and os.getuid()==os.geteuid()==1000
    assert pwd.getpwuid(os.getuid()).pw_name=='server01_cicd-runner'
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00','STOP window'
gate();home=pathlib.Path(pwd.getpwuid(1000).pw_dir);assert home==pathlib.Path('/home/server01_cicd-runner')
out={'schema':'fds.runner-readiness-observation.v1','host':socket.gethostname(),'uid':os.getuid(),'account':pwd.getpwuid(1000).pw_name,'started_at_kst':now(),'paths':[],'versions':[]}
def item(p,content=False,limit=2*1024*1024):
    gate();row={'path':str(p)}
    try:
        a=p.lstat();row.update(uid=a.st_uid,gid=a.st_gid,mode=oct(stat.S_IMODE(a.st_mode)),size=a.st_size,symlink=stat.S_ISLNK(a.st_mode),regular=stat.S_ISREG(a.st_mode),directory=stat.S_ISDIR(a.st_mode))
        if content:
            assert stat.S_ISREG(a.st_mode) and a.st_size<=limit and p.resolve()==p
            raw=p.read_bytes();b=p.stat();row.update(sha256=hashlib.sha256(raw).hexdigest(),stable=(a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns))
            if p.name=='SUPPLY_MANIFEST.json':
                d=json.loads(raw);row.update(source_commit=d['source']['commit'],supply_tool_commit=d['supply_tool']['commit'])
        row['status']='OBSERVED'
    except FileNotFoundError:row['status']='ABSENT'
    except (OSError,AssertionError,KeyError,ValueError) as e:row.update(status='INCOMPLETE',error_type=type(e).__name__,errno=getattr(e,'errno',None))
    out['paths'].append(row)
item(home);item(home/'FDS_CICD_Runtime')
old=home/'FDS_CICD_Runtime/FDS_CICD_ApkoSupply.adc90410f99cb.f4d55db6ecbe';item(old);item(old/'SUPPLY_MANIFEST.json',True)
out['filesystem']={'path':str(home),'free_bytes':shutil.disk_usage(home).free,'readonly':bool(os.statvfs(home).f_flag & os.ST_RDONLY)}
for command in (['/usr/bin/python3','--version'],['/usr/bin/git','--version'],['/usr/bin/podman','--version']):
    gate()
    try:
        p=subprocess.run(command,capture_output=True,timeout=3);out['versions'].append({'command':command,'rc':p.returncode,'stdout':p.stdout[:1024].decode(errors='replace'),'stderr':p.stderr[:1024].decode(errors='replace')})
    except (OSError,subprocess.TimeoutExpired) as e:out['versions'].append({'command':command,'status':'INCOMPLETE','error_type':type(e).__name__})
item(pathlib.Path('/usr/local/bin/trivy'),True,64*1024*1024)
out['subordinate_ids']={}
for name in ('subuid','subgid'):
    try:
        p=pathlib.Path('/etc')/name;assert p.stat().st_size<1024*1024
        out['subordinate_ids'][name]=[line for line in p.read_text().splitlines() if line.split(':',1)[0]=='server01_cicd-runner']
    except (OSError,AssertionError) as e:out['subordinate_ids'][name]={'error_type':type(e).__name__}
try:out['selinux_enforce']=pathlib.Path('/sys/fs/selinux/enforce').read_text().strip()
except OSError as e:out['selinux_enforce']={'error_errno':e.errno}
out.update(finished_at_kst=now(),readiness_gate='NOT_EVALUATED',runner_registration='NOT_QUERIED',concurrent_execution_exclusion='NOT_ESTABLISHED',
           trivy_db_freshness='NOT_QUERIED',candidate_supply_transfer='NOT_RUN',rootless_runtime='NOT_RUN',runtime_apply='NOT_RUN')
print(json.dumps(out,indent=2))
