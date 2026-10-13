"""Pure read precheck: fixed metadata GETs, no Secret or credential values."""
import datetime, hashlib, json, os, socket, subprocess
if socket.gethostname() != 'k8s-control01' or os.geteuid() != 0:
    raise SystemExit('Unexpected host or uid')
result={'classification':'PURE_READ_PRECHECK','source_sha256':os.environ.get('COLLECTOR_SHA256'),'hostname':socket.gethostname(),'started_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'reads':[]}
def read(label,args,project):
    cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf',*args,'-o','json']
    p=subprocess.run(cmd,capture_output=True,timeout=25)
    entry={'label':label,'command':cmd,'rc':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_bytes':len(p.stderr)}
    if p.returncode: entry['result']='READ_FAILED'; result['reads'].append(entry); return
    entry['projection']=project(json.loads(p.stdout)); result['reads'].append(entry)
def pods(d):
    found=[]
    for p in d.get('items',[]):
        containers=[]
        for c in p['spec']['containers']:
            args=c.get('command',[])+c.get('args',[])
            audit=[]
            for i,a in enumerate(args):
                if a.startswith('--audit-'):
                    audit.append(a if '=' in a else a+' '+(args[i+1] if i+1<len(args) and not args[i+1].startswith('--') else ''))
            containers.append({'name':c['name'],'audit_flags':audit})
        found.append({'name':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec'].get('nodeName'),'phase':p['status'].get('phase'),'containers':containers})
    return found
def deployment(d):
    s=d['spec']['template']['spec']
    return {'name':d['metadata']['name'],'uid':d['metadata']['uid'],'resourceVersion':d['metadata']['resourceVersion'],'serviceAccountName':s.get('serviceAccountName','default'),'hostNetwork':s.get('hostNetwork',False),'replicas':d['spec'].get('replicas'),'readyReplicas':d.get('status',{}).get('readyReplicas'),'containers':[{'name':c['name'],'image':c['image'],'secret_refs':[{'env_name':e['name'],'name':e['valueFrom']['secretKeyRef']['name'],'key':e['valueFrom']['secretKeyRef']['key']} for e in c.get('env',[]) if 'secretKeyRef' in e.get('valueFrom',{})]} for c in s['containers']]}
def services(d):
    return [{'name':x['metadata']['name'],'type':x['spec'].get('type'),'selector':x['spec'].get('selector'),'ports':x['spec'].get('ports')} for x in d.get('items',[]) if 'grafana' in x['metadata']['name'] or x['spec'].get('selector',{}).get('app')=='grafana']
read('apiserver_audit_flags',['-n','kube-system','get','pods','-l','component=kube-apiserver'],pods)
read('grafana_deployment',['-n','monitoring-api','get','deployment','grafana'],deployment)
read('grafana_service_types',['-n','monitoring-api','get','services'],services)
result['finished_kst']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if all(x['rc']==0 for x in result['reads']) else 1)
