"""Fixed Grafana reference metadata GETs. Never emit credential values."""
import datetime, json, os, socket, subprocess, urllib.parse

def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def gate():
    if not '2026-10-09T09:10:00+09:00' <= now() < '2026-10-09T12:00:00+09:00':
        raise RuntimeError('outside authorized window')
    if socket.gethostname() != 'k8s-control01' or os.geteuid() != 0:
        raise RuntimeError('host/euid mismatch')

def meta(obj):
    return {k:obj.get('metadata',{}).get(k) for k in ('name','namespace','uid','resourceVersion','generation','ownerReferences')}

def reference(v):
    out={}
    for kind in ('secretKeyRef','configMapKeyRef'):
        if kind in v:
            out[kind]={k:v[kind].get(k) for k in ('name','key','optional')}
    for kind in ('fieldRef','resourceFieldRef'):
        if kind in v: out[kind]={'present':True,'details_omitted':True}
    return out

def spec(s):
    out={'serviceAccountName':s.get('serviceAccountName'),'containers':[], 'volumes':[]}
    for group in ('containers','initContainers','ephemeralContainers'):
        for c in s.get(group,[]):
            row={'group':group,'name':c['name'],'image':c.get('image'),'admin_env':[], 'envFrom':[], 'volumeMounts':[],
                 'command_arguments_not_collected':True}
            for e in c.get('env',[]):
                if e.get('name','').startswith('GF_SECURITY_ADMIN_'):
                    row['admin_env'].append({'name':e['name'],'literal_present_value_omitted':'value' in e,
                                            'valueFrom':reference(e.get('valueFrom',{}))})
            for e in c.get('envFrom',[]):
                row['envFrom'].append({k:{f:e[k].get(f) for f in ('name','optional')}
                                       for k in ('secretRef','configMapRef') if k in e})
            for m in c.get('volumeMounts',[]):
                row['volumeMounts'].append({k:m.get(k) for k in ('name','mountPath','readOnly')})
            out['containers'].append(row)
    for v in s.get('volumes',[]):
        row={'name':v['name'],'types':[k for k in v if k!='name']}
        if 'secret' in v: row['secret']={k:v['secret'].get(k) for k in ('secretName','optional')}
        if 'configMap' in v: row['configMap']={k:v['configMap'].get(k) for k in ('name','optional')}
        if 'projected' in v:
            row['sources']=[]
            for src in v['projected'].get('sources',[]):
                row['sources'].append({k:({f:src[k].get(f) for f in ('name','optional')} if k in ('secret','configMap') else {'details_omitted':True}) for k in src})
        out['volumes'].append(row)
    return out

def query(path, rows):
    gate()
    cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
    start=now()
    p=subprocess.run(cmd,capture_output=True,timeout=15)
    row={'path':path,'command':cmd,'started_at_kst':start,'finished_at_kst':now(),'rc':p.returncode,
         'response_bytes':len(p.stdout),'stderr_bytes':len(p.stderr),'raw_response_not_preserved':True}
    rows.append(row)
    if p.returncode or p.stderr or len(p.stdout)>2*1024*1024: raise RuntimeError('query failed or exceeded bounds; response omitted')
    return json.loads(p.stdout),row

def main():
    gate()
    out={'schema':'fds.grafana-credential-reference.v1','host':socket.gethostname(),'started_at_kst':now(), 'queries':[],
         'boundary':'GET Deployment and selected Pods only. No Secret/ConfigMap GET, exec, PF, credential values, value hashes, annotations or commands. API response is projected in memory before transfer.'}
    path='/apis/apps/v1/namespaces/monitoring-api/deployments/grafana'
    d,q=query(path,out['queries'])
    assert d['metadata']['name']=='grafana' and d['metadata']['namespace']=='monitoring-api'
    q['projection']={'metadata':meta(d),'spec':spec(d['spec']['template']['spec'])}
    sel=d['spec']['selector']
    assert not sel.get('matchExpressions') and sel.get('matchLabels')
    selector=','.join(k+'='+v for k,v in sorted(sel['matchLabels'].items()))
    p,q=query('/api/v1/namespaces/monitoring-api/pods?limit=10&labelSelector='+urllib.parse.quote(selector,safe=''),out['queries'])
    assert not p.get('metadata',{}).get('continue') and 1<=len(p['items'])<=10
    q['projection']={'items':[{'metadata':meta(x),'spec':spec(x['spec']),
        'status':{'phase':x.get('status',{}).get('phase'),'containers':[{k:c.get(k) for k in ('name','imageID','ready','restartCount')} for c in x.get('status',{}).get('containerStatuses',[])]}} for x in p['items']]}
    d2,q=query(path,out['queries'])
    q['projection']={'metadata':meta(d2),'spec':spec(d2['spec']['template']['spec'])}
    out['deployment_unchanged']=meta(d)==meta(d2) and spec(d['spec']['template']['spec'])==spec(d2['spec']['template']['spec'])
    out['finished_at_kst']=now()
    out['status']='COLLECTED' if out['deployment_unchanged'] else 'DRIFT_STOP'
    print(json.dumps(out,ensure_ascii=False))

if __name__=='__main__': main()
