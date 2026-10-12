"""Local receipt/result verification; does not connect or apply anything."""
from pathlib import Path
import datetime,hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
mapping=json.loads((P/'COLLECTION_PATHS.json').read_bytes()) if (P/'COLLECTION_PATHS.json').exists() else {}
def resolve(path):
 path=Path(path);parts=path.parts
 if parts and parts[0] in mapping:return P/mapping[parts[0]]/Path(*parts[1:])
 return P/path
def read(path):return json.loads(resolve(path).read_bytes())
def sha(path):return hashlib.sha256(resolve(path).read_bytes()).hexdigest()
def queries(label):return {q['name']:q['items'] for q in read(label+'-cluster/stdout.json')['queries']}
receipts=[]
for f in sorted(P.glob('*/receipt.json')):
 r=json.loads(f.read_bytes());base=f.parent.relative_to(P)
 assert sha(base/'collector.py')==r['source_sha256'],str(f)
 assert sha(base/'stdout.json')==r['stdout_sha256'],str(f)
 assert sha(base/'stderr.txt')==r['stderr_sha256'],str(f)
 receipts.append({'path':base.as_posix(),'rc':r['rc']})
fixed=read('APP_BINDING.json');initial=queries('before');final=queries('final')
steps=[];watch_total=0;latencies=[];deleted=set()
for name,app in [('engine-1','fds-engine'),('engine-2','fds-engine'),('api-1','transaction-api'),('api-2','transaction-api')]:
 x=read(name+'/stdout.json');assert x['eviction_command_invocations']==1 and x['guard']=='PASS' and x['request']['rc']==0
 status=json.loads(x['request']['stdout']);assert status['kind']=='Status' and status['status']=='Success'
 target=x['target'];uid=target['deleteOptions']['preconditions']['uid'];assert uid not in deleted;deleted.add(uid)
 original=next(p for p in fixed['observed_pods'] if p['metadata']['uid']==uid)
 assert original['node']=='k8s-worker02' and original['metadata']['labels']['app']==app
 assert target['deleteOptions']['gracePeriodSeconds']==30
 w=read(name+'-edge-watch/stdout.json');assert w['status']=='ALL_200' and len(w['requests'])==90
 assert all(r['rc']==0 and r['http_code']=='200' for r in w['requests'])
 dispatch=datetime.datetime.fromisoformat(x['dispatch_at_utc'])
 assert datetime.datetime.fromisoformat(w['requests'][0]['at_utc'])<dispatch<datetime.datetime.fromisoformat(w['requests'][-1]['at_utc'])
 watch_total+=len(w['requests']);latencies.extend(r['elapsed_ms'] for r in w['requests'])
 steps.append({'step':name,'app':app,'old_pod':target['metadata']['name'],'old_uid':uid,'dispatch_at_utc':x['dispatch_at_utc'],'edge_200':90})
for d in final['deployments']:
 old=next(x for x in fixed['deployments'] if x['metadata']['name']==d['metadata']['name'])
 assert d['metadata']['uid']==old['metadata']['uid'] and d['spec_sha256']==old['spec_sha256'] and d['template_sha256']==old['template_sha256']
for name in ['fds-engine','transaction-api']:
 pp=[p for p in final['pods'] if p['metadata']['labels']['app']==name]
 assert len(pp)==3 and all(p['ready'] and not p['metadata']['deletionTimestamp'] for p in pp)
 assert {p['node'] for p in pp}=={'k8s-worker01','k8s-worker02','k8s-worker03'}
assert not deleted & {p['metadata']['uid'] for p in final['pods']}
kept={p['metadata']['uid'] for p in fixed['observed_pods']}-deleted
assert len(kept)==2 and kept <= {p['metadata']['uid'] for p in final['pods']}
assert read('final-analysis.json')['status']=='OBSERVATION_STABLE'
assert all(any(c['type']=='Ready' and c['status']=='True' for c in n['conditions']) for n in final['nodes'])
assert not final['pdb'] and not final['hpa']
assert final['cluster'][0]['metadata']['uid']==fixed['cluster_uid']
fw=read('final-edge-watch/stdout.json');assert fw['status']=='ALL_200' and len(fw['requests'])==60 and all(r['rc']==0 and r['http_code']=='200' for r in fw['requests'])
watch_total+=len(fw['requests']);latencies.extend(r['elapsed_ms'] for r in fw['requests'])
layers=read('control01-oid-layer-bytes/stdout.json')
assert len(layers['layers'])==15 and layers['status']=='LAYER_BYTES_VERIFIED'
for x in layers['layers']:assert x['verified'] and x['rc']==0 and x['digest']==x['observed_digest'] and x['expected_size']==x['observed_size']
k=read('K8S_EXECUTION_INPUT.json');assert k['replacement_count']==17 and k['preserve_count']==28
for x in k['supply']:assert sha('k8s-supply/'+x['file'])==x['sha256']
result={'status':'VERIFIED_LOCAL_RECEIPTS_AND_LIMITED_RUNTIME_RESULTS','receipt_count':len(receipts),'receipts':receipts,'evictions':steps,'edge_get_count':watch_total,'edge_failed_count':0,'edge_max_elapsed_ms':max(latencies),'final_counts':read('final-analysis.json')['counts'],'final_deployment_specs_unchanged':True,'old_pods_preserved':sorted(kept),'oid_layer_bytes_verified':layers['verified_bytes'],'oid_layer_count':15,'k8s_supply_files':4,'k8s_install_executed':False,'ha_ac_or_final_e2e_accepted':False,'independent_review_complete':False}
# Publication mode is read-only, so verification does not rewrite sealed artifacts.
if not mapping:(P/'VERIFICATION.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in result.items() if k not in ['receipts','evictions']},ensure_ascii=False))
