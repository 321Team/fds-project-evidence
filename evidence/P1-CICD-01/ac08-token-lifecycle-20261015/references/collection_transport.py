"""Fresh bounded read-only inputs; all new files stay on this workstation."""
import concurrent.futures, datetime, hashlib, json, pathlib, shlex, subprocess
OUT = pathlib.Path(__file__).parent
ROOT = OUT.parent.parent
OLD = OUT.parent / 'phase1-deploy-preparation-20261013'
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def gh(item):
    name, endpoint = item
    p = subprocess.run(['gh','api',endpoint], capture_output=True, timeout=30)
    (OUT/(name+'.json')).write_bytes(p.stdout)
    assert p.returncode == 0, (name,p.returncode)
    data=json.loads(p.stdout)
    if name in ('harbor62','baseline13'):
        repo='infra-harbor-trivy' if name=='harbor62' else 'fds-project-baseline'
        num=62 if name=='harbor62' else 13
        page=max(1,(data['comments']+99)//100)
        gh((name+'-latest-comments',f'repos/321Team/{repo}/issues/{num}/comments?per_page=100&page={page}'))
    return {'name':name,'rc':0,'at_utc':now()}
def remote(item):
    label,host,user,key,sudo,source,args=item
    d=OUT/label;d.mkdir(exist_ok=False)
    raw=source.read_bytes();compile(raw,str(source),'exec');(d/'collector.py').write_bytes(raw)
    command=(['sudo','-n'] if sudo else [])+['/usr/bin/python3','-B','-I','-S','-',*args]
    inner=['/usr/bin/ssh','-F','/dev/null','-T','-i',key,'-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','ControlMaster=no','-o','ControlPath=none','-o','UpdateHostKeys=no',user+'@'+host,shlex.join(command)]
    bridge=('import subprocess,sys\np=subprocess.run('+repr(inner)+',input='+repr(raw)+',capture_output=True,timeout=45)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n').encode()
    outer=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-S','-']
    receipt={'started_at_utc':now(),'outer_argv':outer,'inner_argv':inner,'source_sha256':hashlib.sha256(raw).hexdigest(),'classification':'PURE_READ_PRECHECK','review':'NOT PERFORMED (Pre-check)','token_issued':False,'server_files_written':False}
    try:
        p=subprocess.run(outer,input=bridge,capture_output=True,timeout=55);a,b,rc=p.stdout,p.stderr,p.returncode
    except subprocess.TimeoutExpired as e:a,b,rc=e.stdout or b'',e.stderr or b'',None
    (d/'stdout.json').write_bytes(a);(d/'stderr.txt').write_bytes(b)
    receipt.update(rc=rc,finished_at_utc=now(),stdout_sha256=hashlib.sha256(a).hexdigest(),stderr_sha256=hashlib.sha256(b).hexdigest())
    save(d/'receipt.json',receipt)
    return {'label':label,'rc':rc,'bytes':len(a),'stderr_bytes':len(b)}
if __name__=='__main__':
    key='/home/server01_ansible/.ssh/p1_ansible_ed25519'
    cpkey='/home/server01_ansible/.ssh/id_ed25519'
    original=OUT.parent/'p1-delivery-runner-20261013'
    tasks=[('cluster','10.1.93.102','svc_ansible',key,True,original/'cluster_read.py',[]),('cp1-auth','10.1.93.102','server02',cpkey,False,original/'auth_path_read.py',['cp1']),('runner-auth','10.250.10.20','server01_cicd-runner',key,False,original/'auth_path_read.py',['runner']),('app-state','10.1.93.102','svc_ansible',key,True,OLD/'app_state_read.py',[]),('app-security','10.1.93.102','svc_ansible',key,True,OLD/'app_security_read.py',[]),('runner-health','10.250.10.20','server01_cicd-runner',key,False,OUT.parent/'phase1-push-followup-20261013/runner_push_read.py',[])]
    tasks += [('cache-'+n,'10.1.93.'+ip,'svc_ansible',key,True,OLD/'rollback_cache_read.py',[]) for n,ip in [('worker01','105'),('worker02','107'),('worker03','108')]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for x in pool.map(remote,tasks):print(json.dumps(x),flush=True)
    endpoints=[('pr218','repos/321Team/fds-project-evidence/pulls/218'),('reviews218','repos/321Team/fds-project-evidence/pulls/218/reviews'),('checks218','repos/321Team/fds-project-evidence/commits/9647a83724dea442c9e8238e60d68bfe2602dc8d/check-runs'),('main','repos/321Team/infra-cicd/commits/main'),('harbor62','repos/321Team/infra-harbor-trivy/pulls/62'),('baseline13','repos/321Team/fds-project-baseline/issues/13'),('active-runs','repos/321Team/infra-cicd/actions/runs?per_page=30'),('push-run','repos/321Team/infra-cicd/actions/runs/38404449622')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for x in pool.map(gh,endpoints):print(json.dumps(x),flush=True)
