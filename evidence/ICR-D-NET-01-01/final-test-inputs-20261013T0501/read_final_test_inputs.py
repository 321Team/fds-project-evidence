"""Read policy and workload metadata only; never captures Secret/env values."""
import datetime as dt,hashlib,json,os,socket,subprocess
from pathlib import Path
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def meta(x):
    m=x.get('metadata',{})
    return {k:m.get(k) for k in ('name','namespace','uid','resourceVersion','generation')}
def containers(spec):
    out=[]
    for c in spec.get('containers',[]):
        row={k:c.get(k) for k in ('name','image','imagePullPolicy')}
        for p in ('readinessProbe','livenessProbe','startupProbe'):
            if p in c:
                v=c[p];row[p]={k:v[k] for k in ('initialDelaySeconds','periodSeconds','timeoutSeconds','failureThreshold','successThreshold','terminationGracePeriodSeconds') if k in v}
                if 'httpGet' in v:row[p]['httpGet']={k:v['httpGet'].get(k) for k in ('path','port','scheme')}
                if 'tcpSocket' in v:row[p]['tcpSocket']={k:v['tcpSocket'].get(k) for k in ('port',)}
                if 'exec' in v:row[p]['exec']='PRESENT_COMMAND_NOT_CAPTURED'
        out.append(row)
    return out
queries=[('namespace','/api/v1/namespaces/kube-system'),
 ('gnp','/apis/crd.projectcalico.org/v1/globalnetworkpolicies'),
 ('hep','/apis/crd.projectcalico.org/v1/hostendpoints'),
 ('felix','/apis/crd.projectcalico.org/v1/felixconfigurations'),
 ('nodes','/api/v1/nodes'),('pods','/api/v1/pods'),
 ('deployments','/apis/apps/v1/deployments'),('statefulsets','/apis/apps/v1/statefulsets'),
 ('pdb','/apis/policy/v1/poddisruptionbudgets'),('pv','/api/v1/persistentvolumes'),
 ('pvc','/api/v1/persistentvolumeclaims')]
out={'started_at_utc':now(),'host':socket.gethostname(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
     'mutation':False,'secret_or_env_values_collected':False,'queries':[]}
for kind,path in queries:
    argv=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
    p=subprocess.run(argv,capture_output=True,timeout=15)
    q={'kind':kind,'argv':argv,'rc':p.returncode,'at_utc':now(),'raw_stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
       'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'items':[]}
    if p.returncode==0:
        assert len(p.stdout)<=4*1024*1024
        d=json.loads(p.stdout);items=d.get('items',[d]);assert len(items)<=500
        for x in items:
            r={'metadata':meta(x)};s=x.get('spec',{});st=x.get('status',{})
            if kind in ('gnp','hep','felix','pdb'):
                r['spec']=s;r['labels']=x.get('metadata',{}).get('labels',{})
                if kind=='pdb':r['status']={k:st.get(k) for k in ('disruptionsAllowed','currentHealthy','desiredHealthy','expectedPods','observedGeneration')}
            elif kind=='nodes':
                r['spec']={k:s.get(k) for k in ('unschedulable','taints','podCIDRs')}
                r['labels']=x.get('metadata',{}).get('labels',{})
                r['nodeInfo']=st.get('nodeInfo',{})
                r['ready']=[c for c in st.get('conditions',[]) if c.get('type')=='Ready']
            elif kind in ('pods','deployments','statefulsets'):
                ps=s if kind=='pods' else s.get('template',{}).get('spec',{})
                r['pod_spec']={k:ps.get(k) for k in ('nodeName','nodeSelector','affinity','tolerations','hostNetwork','terminationGracePeriodSeconds')}
                r['containers']=containers(ps)
                r['volumes']=[{'name':v.get('name'),**{k:v[k] for k in ('persistentVolumeClaim','emptyDir','hostPath') if k in v}} for v in ps.get('volumes',[]) if any(k in v for k in ('persistentVolumeClaim','emptyDir','hostPath'))]
                r['owners']=x.get('metadata',{}).get('ownerReferences',[])
                if kind=='pods':
                    r['phase']=st.get('phase');r['ready']=[c for c in st.get('conditions',[]) if c.get('type')=='Ready']
                    r['containers_status']=[{k:c.get(k) for k in ('name','ready','restartCount','imageID')} for c in st.get('containerStatuses',[])]
                else:r['replicas']=s.get('replicas');r['status']={k:st.get(k) for k in ('observedGeneration','readyReplicas','availableReplicas','updatedReplicas')}
            elif kind=='pv':r['spec']={k:s.get(k) for k in ('storageClassName','capacity','accessModes','persistentVolumeReclaimPolicy','claimRef','local','hostPath','nodeAffinity')};r['phase']=st.get('phase')
            elif kind=='pvc':r['spec']={k:s.get(k) for k in ('volumeName','storageClassName','accessModes','resources')};r['phase']=st.get('phase')
            q['items'].append(r)
    out['queries'].append(q)
    if p.returncode!=0:break
out['finished_at_utc']=now();out['status']='READ_COMPLETE' if len(out['queries'])==len(queries) and all(q['rc']==0 for q in out['queries']) else 'READ_INCOMPLETE'
print(json.dumps(out))
