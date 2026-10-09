import datetime,hashlib,json,os,pathlib,socket,stat,subprocess
def now(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
if not ('2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'): raise SystemExit('STOP window')
if socket.gethostname()!='k8s-control01' or os.geteuid()!=0: raise SystemExit('STOP host/euid')
out={'schema':'fds.app-mon.readonly-inventory.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[],'projection_notice':'API bodies projected before transfer; env, commands, annotations, Secret and ConfigMap contents excluded.'}
def meta(x):
    m=x.get('metadata',{});return {k:m.get(k) for k in ('name','namespace','uid','resourceVersion','labels','creationTimestamp')}
paths=['/api/v1/namespaces','/api/v1/pods','/api/v1/services','/apis/discovery.k8s.io/v1/endpointslices','/apis/networking.k8s.io/v1/networkpolicies','/apis/networking.k8s.io/v1/ingresses','/apis/rbac.authorization.k8s.io/v1/roles','/apis/rbac.authorization.k8s.io/v1/rolebindings','/apis/rbac.authorization.k8s.io/v1/clusterroles','/apis/rbac.authorization.k8s.io/v1/clusterrolebindings']
for path in paths:
    cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=15s','get','--raw='+path]
    p=subprocess.run(cmd,capture_output=True,timeout=25)
    row={'path':path,'command':cmd,'rc':p.returncode,'stdout_sha256_before_projection':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode(errors='replace'),'items':[]}
    if p.returncode==0:
        for x in json.loads(p.stdout).get('items',[]):
            m=meta(x);s=x.get('spec',{});kind=path.rsplit('/',1)[-1]
            if kind=='pods':
                if not any(t in str(m).lower() for t in ('transaction-api','fds-engine','grafana','prometheus')): continue
                item={'metadata':m,'spec':{k:s.get(k) for k in ('nodeName','serviceAccountName','hostNetwork')},'containers':[{k:c.get(k) for k in ('name','image','ports','readinessProbe','livenessProbe')} for c in s.get('containers',[])],'status':{k:x.get('status',{}).get(k) for k in ('phase','podIP','hostIP','containerStatuses','conditions')}}
            elif kind in ('roles','clusterroles'): item={'metadata':m,'rules':x.get('rules',[]),'aggregationRule':x.get('aggregationRule')}
            elif kind in ('rolebindings','clusterrolebindings'): item={'metadata':m,'subjects':x.get('subjects',[]),'roleRef':x.get('roleRef')}
            elif kind=='endpointslices': item={'metadata':m,'addressType':x.get('addressType'),'ports':x.get('ports'),'endpoints':x.get('endpoints')}
            elif kind=='namespaces': item={'metadata':m}
            else: item={'metadata':m,'spec':s}
            row['items'].append(item)
    out['queries'].append(row)
out['kubeconfig_metadata']=[]
for name in ('admin.conf','super-admin.conf'):
    f=pathlib.Path('/etc/kubernetes')/name
    try:
        s=f.stat();out['kubeconfig_metadata'].append({'path':str(f),'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'size':s.st_size,'content_read':False})
    except OSError as e: out['kubeconfig_metadata'].append({'path':str(f),'error':str(e)})
out['finished_at_kst']=now();print(json.dumps(out))
