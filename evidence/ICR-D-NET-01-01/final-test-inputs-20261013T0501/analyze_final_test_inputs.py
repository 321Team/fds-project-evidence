from pathlib import Path
import hashlib,json,sys
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'static-validation-libs'))
import yaml
D=W/'final-test-inputs-control01'
raw=(D/'stdout.json').read_bytes();r=json.loads((D/'receipt.json').read_text())
assert r['rc']==0 and r['stdout_sha256']==hashlib.sha256(raw).hexdigest()
d=json.loads(raw);assert d['status']=='READ_COMPLETE' and not d['mutation']
q={x['kind']:x['items'] for x in d['queries']};assert all(x['rc']==0 for x in d['queries'])
def differences(a,b,path=''):
    if a==b:return []
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for k in sorted(set(a)|set(b)):out+=differences(a.get(k,'<MISSING>'),b.get(k,'<MISSING>'),path+'/'+k)
        return out
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return sum((differences(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [{'path':path,'old':a,'current':b}]
oldroot=W.parents[1]/'phase1-work-20261013/independent-evidence/evidence/P1-K8S-01/icr39-verification-20260927'
policy=[]
for name in ('worker01','worker02','worker03'):
    p=oldroot/('k8s-'+name+'.gnp.yaml');old=yaml.safe_load(p.read_bytes())
    live=[x for x in q['gnp'] if x['metadata']['name']==old['metadata']['name']]
    assert len(live)==1
    delta=differences(old['spec'],live[0]['spec'])
    policy.append({'name':old['metadata']['name'],'historical_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                   'current_generation':live[0]['metadata']['generation'],'identical_spec':not delta,'differences':delta})
nodes=[]
for n in q['nodes']:
    name=n['metadata']['name'];pods=[p for p in q['pods'] if p['pod_spec']['nodeName']==name]
    nodes.append({'name':name,'ready':[x['status'] for x in n['ready']],
                  'pod_count':len(pods),'pvc_pods':[p['metadata'] for p in pods if any('persistentVolumeClaim' in v for v in p['volumes'])],
                  'app_pods':[p['metadata']['name'] for p in pods if p['metadata']['namespace']=='fds-app'],
                  'system_deployment_pods':[p['metadata']['name'] for p in pods if p['metadata']['namespace'] in ('kube-system','calico-system') and any(o.get('kind')=='ReplicaSet' for o in p['owners'])]})
result={'observed_at_utc':d['finished_at_utc'],'source_stdout_sha256':hashlib.sha256(raw).hexdigest(),
        'queries':len(q),'cluster_namespace_uid':q['namespace'][0]['metadata']['uid'],
        'counts':{k:len(v) for k,v in q.items()},'worker_policy_delta_from_20260927':policy,
        'nodes':nodes,'pv':q['pv'],'pdb':q['pdb'],
        'app_deployments':[x for x in q['deployments'] if x['metadata']['namespace']=='fds-app'],
        'reboot_executed':False,'drain_executed':False,'ac_decision':'NOT_PERFORMED'}
(W/'FINAL_TEST_INPUTS_ANALYSIS.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False))
