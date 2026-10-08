import ast,hashlib,json,pathlib,sys
r=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(r/'deps'))
import yaml
repo=r.parent/'sec19-backup-evidence'
d=json.loads((r/'policy.json').read_text(encoding='utf8'))
queries={q['command'][4]:q for q in d['queries']}
pods=queries['pods']['items']; policies=queries['networkpolicies.networking.k8s.io']['items']
app=[p for p in pods if p['metadata'].get('namespace')=='fds-app']
namespaces={n['metadata']['name']:n['metadata'].get('labels',{}) for n in queries['namespaces']['items']}
summary={'nodes_ready':sum(any(c['type']=='Ready' and c['status']=='True' for c in x['conditions']) for x in queries['nodes']['items']),
         'app_pods':[{'name':p['metadata']['name'],'labels':p['metadata'].get('labels',{}),'node':p['spec'].get('nodeName'),'hostNetwork':p['spec'].get('hostNetwork',False)} for p in app],
         'namespace_labels':{k:v for k,v in namespaces.items() if k in ('fds-app','kube-system','monitoring-api','monitoring-node')},
         'hostNetwork_monitoring':[p['metadata']['name'] for p in pods if p['metadata'].get('namespace','').startswith('monitoring') and p['spec'].get('hostNetwork')],
         'nodeport_32085':[s['metadata'] for s in queries['services']['items'] if any(p.get('nodePort')==32085 for p in s['spec'].get('ports',[]))],
         'edge_service':[s for s in queries['services']['items'] if s['metadata'].get('namespace')=='fds-app' and s['metadata']['name']=='transaction-api-nodeport'],
         'edge_endpoints':[s for s in queries['endpointslices.discovery.k8s.io']['items'] if s['metadata'].get('namespace')=='fds-app' and s['metadata'].get('labels',{}).get('kubernetes.io/service-name')=='transaction-api-nodeport']}
historical=repo/'evidence/P1-MON-01/received-20260930T0633Z/control01/networkpolicy.yaml'
summary['mon_policy_comparison']=[]
for doc in yaml.safe_load_all(historical.read_text(encoding='utf8')):
    if not isinstance(doc,dict) or doc.get('kind')!='NetworkPolicy': continue
    match=[p for p in policies if p['metadata']['name']==doc['metadata']['name'] and p['metadata'].get('namespace')==doc['metadata'].get('namespace')]
    summary['mon_policy_comparison'].append({'name':doc['metadata']['name'],'present':bool(match),'spec_equal':bool(match) and match[0]['spec']==doc['spec']})
src=(r/'collect-mon.py').read_text(); fn=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name=='safeconfig')
scope={};exec(ast.get_source_segment(src,fn),scope)
masked=repo/'evidence/P1-MON-01/received-20261002T0601Z/control01/p1-mon-psa-rbac-20261002T150142/alertmanager-config.masked.yml'
old=yaml.safe_load(masked.read_text(encoding='utf8'))
cur=next(q for q in json.loads((r/'mon-config.json').read_text(encoding='utf8'))['queries'] if q.get('name')=='alertmanager-config')['data']['alertmanager.yml']['projection']
summary['receiver_comparison']={'path':masked.relative_to(repo).as_posix(),'historical_projection':scope['safeconfig'](old),'current_projection':cur,'projection_equal':scope['safeconfig'](old)==cur,'limitation':'Credential fields and unlisted keys omitted; not full config equality'}
(r/'analysis.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
