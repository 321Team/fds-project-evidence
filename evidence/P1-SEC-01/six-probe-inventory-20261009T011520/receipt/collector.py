"""Read API projections for six existing workloads; no exec or mutations."""
import datetime, hashlib, json, os, socket, subprocess

def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def gate():
    if not ('2026-10-09T00:00:00+09:00' <= now() < '2026-10-09T09:00:00+09:00'):
        raise SystemExit('STOP outside window')
    if socket.gethostname() != 'k8s-control01' or os.geteuid() != 0:
        raise SystemExit('STOP host/euid')

NAMES = ('fds-engine', 'prometheus', 'grafana', 'alertmanager', 'kube-state-metrics', 'node-exporter')
def selected(x):
    name = x.get('metadata', {}).get('name', '')
    return any(name == n or name.startswith(n + '-') for n in NAMES)

def meta(x):
    return {k: x.get('metadata', {}).get(k) for k in ('name','namespace','uid','resourceVersion','generation','creationTimestamp','labels','ownerReferences')}

def probe(p):
    if p is None: return None
    out = {k:p[k] for k in ('initialDelaySeconds','periodSeconds','timeoutSeconds','successThreshold','failureThreshold','terminationGracePeriodSeconds') if k in p}
    if 'httpGet' in p:
        h = p['httpGet']
        out['httpGet'] = {k:h[k] for k in ('port','scheme','host') if k in h}
        out['httpGet']['path'] = h.get('path','').split('?',1)[0]
        out['httpGet']['query_omitted'] = '?' in h.get('path','')
        out['httpGet']['header_count_values_omitted'] = len(h.get('httpHeaders',[]))
    if 'tcpSocket' in p: out['tcpSocket'] = {k:p['tcpSocket'][k] for k in ('port','host') if k in p['tcpSocket']}
    if 'grpc' in p: out['grpc'] = p['grpc']
    if 'exec' in p:
        cmd = p['exec'].get('command',[])
        out['exec'] = {'argument_count':len(cmd),'command_sha256':hashlib.sha256(json.dumps(cmd,separators=(',',':')).encode()).hexdigest(),'command_omitted':True}
    return out

def spec(s):
    out = {k:s.get(k) for k in ('nodeName','hostNetwork','restartPolicy','serviceAccountName','automountServiceAccountToken','terminationGracePeriodSeconds')}
    out['containers'] = []
    for c in s.get('containers',[]):
        out['containers'].append({'name':c['name'],'image':c.get('image'),'ports':c.get('ports',[]), **{k:probe(c.get(k)) for k in ('startupProbe','readinessProbe','livenessProbe')}})
    return out

def project(x,kind):
    out={'metadata':meta(x)}
    s=x.get('spec',{}); st=x.get('status',{})
    if kind=='pods':
        out['spec']=spec(s)
        out['status']={k:st.get(k) for k in ('phase','podIP','hostIP','startTime')}
        out['status']['conditions']=[{k:c.get(k) for k in ('type','status','lastTransitionTime','reason')} for c in st.get('conditions',[])]
        out['status']['containers']=[{k:c.get(k) for k in ('name','image','imageID','containerID','ready','started','restartCount')} for c in st.get('containerStatuses',[])]
    elif kind in ('deployments','daemonsets','statefulsets'):
        out['spec']={'replicas':s.get('replicas'),'selector':s.get('selector'),'template':{'metadata':meta(s.get('template',{})),'spec':spec(s.get('template',{}).get('spec',{}))}}
        out['status']={k:st.get(k) for k in ('observedGeneration','replicas','readyReplicas','availableReplicas','updatedReplicas','currentReplicas','desiredNumberScheduled','currentNumberScheduled','numberReady','numberAvailable','numberUnavailable','updatedNumberScheduled')}
    elif kind=='services':
        out['spec']={k:s.get(k) for k in ('type','clusterIP','ports','selector','publishNotReadyAddresses')}
    elif kind=='endpointslices':
        out.update(addressType=x.get('addressType'),ports=x.get('ports'),endpoints=[{k:e.get(k) for k in ('addresses','conditions','targetRef','nodeName')} for e in x.get('endpoints',[])])
    return out

gate()
out={'schema':'fds.six-workload-probe-inventory.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[],
     'boundary':'GET only. Projection before transfer; no env, command values, Secret/ConfigMap contents, HTTP header values or query string. No direct probe request, fault injection, exec, mutation or restart.'}
for ns in ('fds-app','monitoring-api','monitoring-node'):
    for kind in ('pods','services','endpointslices','deployments','daemonsets','statefulsets'):
        gate()
        prefix='/api/v1' if kind in ('pods','services') else '/apis/discovery.k8s.io/v1' if kind=='endpointslices' else '/apis/apps/v1'
        path=prefix+'/namespaces/'+ns+'/'+kind
        cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
        started=now()
        try:
            p=subprocess.run(cmd,capture_output=True,timeout=15)
            row={'path':path,'command':cmd,'started_at_kst':started,'finished_at_kst':now(),'rc':p.returncode,'api_body_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode(errors='replace'),'items':[]}
            if p.returncode==0:
                data=json.loads(p.stdout);row['list_resourceVersion']=data.get('metadata',{}).get('resourceVersion')
                row['items']=[project(x,kind) for x in data.get('items',[]) if selected(x)]
            out['queries'].append(row)
            if p.returncode: break
        except subprocess.TimeoutExpired:
            out['queries'].append({'path':path,'command':cmd,'started_at_kst':started,'finished_at_kst':now(),'rc':124,'error':'bounded kubectl timeout','items':[]})
            break
out['finished_at_kst']=now()
print(json.dumps(out,ensure_ascii=False))
