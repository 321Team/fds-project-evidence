"""Read-only Kubernetes evidence; no exec, apply, Secret or credential retrieval."""
import datetime, hashlib, json, os, socket, subprocess, sys

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def meta(x):
    m = x.get('metadata', {})
    return {k: m[k] for k in ('name','namespace','uid','resourceVersion','generation','labels') if k in m}

def project(x, mode):
    result = {'apiVersion': x.get('apiVersion'), 'kind': x.get('kind'), 'metadata': meta(x)}
    if mode == 'pod':
        s = x.get('spec', {})
        result['spec'] = {k: s[k] for k in ('nodeName','hostNetwork','serviceAccountName','dnsPolicy') if k in s}
        result['containers'] = [{k:c[k] for k in ('name','image','ports') if k in c} for c in s.get('containers',[])]
        result['status'] = {k:x.get('status',{}).get(k) for k in ('phase','podIP','hostIP','conditions')}
    elif mode == 'config':
        result['data_sha256'] = {k:hashlib.sha256(v.encode()).hexdigest() for k,v in x.get('data',{}).items()}
        result['binaryData_keys'] = sorted(x.get('binaryData',{}))
    elif mode == 'node':
        result['conditions'] = x.get('status',{}).get('conditions',[])
    elif mode == 'spec':
        result['spec'] = x.get('spec',{})
    elif mode == 'endpoint':
        for k in ('addressType','endpoints','ports'): result[k] = x.get(k)
    return result

assert socket.gethostname().split('.')[0] == 'k8s-control01'
assert os.geteuid() == 0
stage = sys.argv[1]
queries = {
    'policy': [('nodes','node',False),('namespaces','meta',False),('pods','pod',True),
               ('networkpolicies.networking.k8s.io','spec',True),
               ('globalnetworkpolicies.crd.projectcalico.org','spec',False),
               ('networkpolicies.crd.projectcalico.org','spec',True),
               ('hostendpoints.crd.projectcalico.org','spec',False),
               ('services','spec',True),('endpointslices.discovery.k8s.io','endpoint',True)],
    'mon': [('configmaps','config',True),('prometheusrules.monitoring.coreos.com','spec',True),
            ('servicemonitors.monitoring.coreos.com','meta',True),
            ('podmonitors.monitoring.coreos.com','meta',True)]
}[stage]
report = {'stage':stage,'hostname':socket.gethostname(),'uid':os.geteuid(),'started_utc':now(),
          'source_sha256':os.environ['COLLECTOR_SHA256'],
          'scope':'API get only; projected output, raw stdout hash; no traffic tests or configuration writes', 'queries':[]}
for resource,mode,allns in queries:
    cmd = ['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s','get',resource]
    if allns: cmd.append('-A')
    cmd += ['-o','json']
    q = {'command':cmd,'started_utc':now(),'projection':mode}
    try:
        p = subprocess.run(cmd,capture_output=True,timeout=18)
        q.update(rc=p.returncode,stderr=p.stderr.decode(errors='replace'),raw_stdout_sha256=hashlib.sha256(p.stdout).hexdigest())
        if p.returncode == 0:
            data=json.loads(p.stdout)
            q['list_metadata']=data.get('metadata',{})
            q['items']=[project(x,mode) for x in data.get('items',[])]
    except Exception as e:
        q.update(rc=124 if isinstance(e,subprocess.TimeoutExpired) else 12,error=str(e))
    q['finished_utc']=now()
    report['queries'].append(q)
report['finished_utc']=now()
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if all(q['rc']==0 for q in report['queries']) else 2)
