import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
receipts=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'private'
def read(folder):return json.loads((receipts/folder/'stdout.json').read_bytes())
d=read('app-mon-inventory-20261009T002630');qs={q['path'].split('/')[-1]:q['items'] for q in d['queries']}
roles={(x['metadata'].get('namespace'),x['metadata']['name']):x for x in qs['roles']};cr={x['metadata']['name']:x for x in qs['clusterroles']}
rbac=[]
for b in qs['rolebindings']+qs['clusterrolebindings']:
 ns=b['metadata'].get('namespace');rr=b['roleRef'];r=cr.get(rr['name']) if rr['kind']=='ClusterRole' else roles.get((ns,rr['name']))
 if ns not in (None,'monitoring-api') or r is None:continue
 hits=[x for x in r['rules'] if any(v in x.get('verbs',[]) for v in ('create','get','*')) and any(v in x.get('apiGroups',[]) for v in ('','*')) and any(v in x.get('resources',[]) for v in ('pods/portforward','pods/*','*'))]
 if hits:rbac.append({'binding':b,'matchingRules':hits,'classification':'CREATE_OR_WILDCARD' if any(any(v in x['verbs'] for v in ('create','*')) for x in hits) else 'GET_ONLY_CANDIDATE_NOT_RUNTIME_TESTED'})
repo=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else root.parent/'sec19-app-logging-code';refs={}
for ref in ('adc90410','8eac4c982076e3c219840a13686b15c46879981f'):
 refs[ref]=subprocess.check_output(['git','-C',str(repo),'rev-parse',ref]).decode().strip()
source=[]
for f in read('worker01-metrics-20261009T002813')['files']:
 row=dict(f);row['references']=[]
 for sha in refs.values():
  path=f['app']+'/'+f['path'].removeprefix('/app/')
  raw=subprocess.check_output(['git','-C',str(repo),'show',sha+':'+path]);digest=hashlib.sha256(raw).hexdigest()
  row['references'].append({'commit':sha,'path':path,'sha256':digest,'matches':digest==f['sha256']})
 source.append(row)
summary={'schema':'fds.app-mon.analysis.v1','rbac_matching_bindings':rbac,'rbac_limit':'Static stored RBAC rules; not SubjectAccessReview, identity/group enumeration, authentication or actual port-forward trial. GET-only candidates are not asserted usable.','runtime_source_comparison':source,'http':[]}
for folder in ('edge-metrics-20261009T002837','worker01-metrics-20261009T002813','worker03-metrics-20261009T002814'):
 x=read(folder)
 for q in x['queries']:
  summary['http'].append({'source_host':x['host'],'source_context':q['label'],'receipt':folder,'requests':json.loads(q['stdout'])['requests']})
output=pathlib.Path(sys.argv[3]) if len(sys.argv)>3 else root/'app-mon-analysis.json'
output.write_bytes((json.dumps(summary,indent=2,ensure_ascii=False)+'\n').encode())
for f in source:print(f['app'],f['path'],[(v['commit'][:8],v['matches']) for v in f['references']])
print('RBAC candidates',[(b['binding']['metadata']['name'],b['classification']) for b in rbac])
