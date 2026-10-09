
import base64,datetime,hashlib,json,os,pathlib,socket,stat,subprocess,sys
expected='k8s-worker02'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
if not ('2026-10-09T00:00:00+09:00'<=now.isoformat()<'2026-10-09T09:00:00+09:00'):
    raise SystemExit('STOP: outside window')
if socket.gethostname()!=expected or os.geteuid()!=0: raise SystemExit('STOP: host/euid')
result={'schema':'fds.k8s-v4-readonly.v1','host':socket.gethostname(),'started_at_kst':now.isoformat(),'euid':os.geteuid(),'files':[],'queries':[],'remote_write':False}
package=pathlib.Path('/opt/fds/P1-K8S-01-v4')
paths=[package/'RUNBOOK_FINAL.md',package/'SHA256SUMS',package/'SCRIPT_SHA256SUMS',package/'config/runtime-input.json',pathlib.Path('/var/lib/fds/P1-K8S-01/gate2-state.json')]
if (package/'code').is_dir(): paths+=sorted((package/'code').glob('*.py'))+sorted((package/'code').glob('*.sh'))
if expected=='k8s-control01':
    bundle=pathlib.Path('/root/generated-gate2-attempt01')
    paths += [bundle/'config.lock.json',bundle/'SHA256SUMS']
    for kind in ('gnp','hep','felix'):
        paths+=sorted((bundle/kind).glob('*.yaml'))+sorted((bundle/kind).glob('*.json'))
for p in paths:
    row={'path':str(p)}
    try:
        if p.resolve()!=p: raise ValueError('symlink: no traversal')
        with p.open('rb') as f:
            a=os.fstat(f.fileno())
            if not stat.S_ISREG(a.st_mode) or a.st_size>2000000: raise ValueError('type/size')
            raw=f.read(2000001); b=os.fstat(f.fileno())
        if (a.st_ino,a.st_mtime_ns,a.st_size)!=(b.st_ino,b.st_mtime_ns,b.st_size): raise ValueError('changed during read')
        row.update(sha256=hashlib.sha256(raw).hexdigest(),size=len(raw),uid=a.st_uid,gid=a.st_gid,mode=oct(stat.S_IMODE(a.st_mode)),mtime_ns=a.st_mtime_ns)
        # Only non-secret generated Calico bundle definitions are transferred.
        if str(p).startswith('/root/generated-gate2-attempt01/'):
            row['content_base64']=base64.b64encode(raw).decode()
    except Exception as e: row['error']=type(e).__name__+': '+str(e)
    result['files'].append(row)
commands=[['systemctl','show','firewalld','-p','ActiveState','-p','UnitFileState'],['ip','-j','-4','address','show']]
if expected=='k8s-control01':
    # Raw GET avoids discovery-cache writes; these are known read-only API paths.
    for api in ('/api/v1/nodes','/apis/crd.projectcalico.org/v1/hostendpoints','/apis/crd.projectcalico.org/v1/globalnetworkpolicies','/apis/crd.projectcalico.org/v1/felixconfigurations'):
        commands.append(['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=15s','get','--raw='+api])
for cmd in commands:
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=25,universal_newlines=True)
        # API objects are kept as received. No Secret/kubeconfig bodies queried.
        result['queries'].append({'command':cmd,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    except subprocess.TimeoutExpired: result['queries'].append({'command':cmd,'rc':124,'error':'timeout'})
result['finished_at_kst']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
print(json.dumps(result))
