from pathlib import Path
import datetime as dt,hashlib,json
P=Path(__file__).resolve().parent
def read(name):return json.loads((P/name).read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipts=[]
for p in P.glob('*/receipt.json'):
 r=json.loads(p.read_bytes())
 for f,k in [('collector.py','source_sha256'),('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert sha(p.parent/f)==r[k]
 receipts.append({'path':p.parent.name,'rc':r['rc'],'status':json.loads((p.parent/'stdout.json').read_bytes())['status']})
assert len(receipts)==21
assert [r['path'] for r in receipts if r['rc']!=0]==['k8s-control01-cache']
sch=read('k8s-control01-scheduling/stdout.json')
query={next(x for x in c['argv'] if x in ['nodes','deployments','pods','kube-system']):c['items'] for c in sch['commands'] if 'items' in c}
assert query['kube-system'][0]['metadata']['uid']=='e1669cff-1435-423f-a6c4-28bc44f488de'
nodes=query['nodes'];deps=query['deployments'];pods=query['pods'];assert len(nodes)==6 and len(deps)==2 and len(pods)==3
for n in nodes:
 assert n['metadata']['labels']['kubernetes.io/os']=='linux' and n['metadata']['labels']['kubernetes.io/arch']=='amd64'
 assert not n['spec'].get('unschedulable') and any(c['type']=='Ready' and c['status']=='True' for c in n['conditions'])
def tolerates(t,taint):
 return t.get('effect') in [None,'',taint.get('effect')] and (t.get('operator','Equal')=='Exists' and (not t.get('key') or t['key']==taint['key']) or t.get('operator','Equal')=='Equal' and t.get('key')==taint['key'] and t.get('value','')==taint.get('value',''))
targets=[];matrix=[]
supply=read('OBSERVED_SUPPLY.json')
for im in supply['images']:
 dep=next(d for d in deps if d['metadata']['name']==('calico-kube-controllers' if im['name']=='kube-controllers' else 'coredns'))
 s=dep['scheduling'];assert s['nodeSelector']=={'kubernetes.io/os':'linux'}
 assert not (s.get('affinity') or {}).get('nodeAffinity') and not (s.get('affinity') or {}).get('podAffinity')
 assert not ((s.get('affinity') or {}).get('podAntiAffinity') or {}).get('requiredDuringSchedulingIgnoredDuringExecution')
 assert len(dep['containers'])==1 and dep['containers'][0]['imagePullPolicy']=='IfNotPresent'
 ref=dep['containers'][0]['image']
 for n in nodes:
  host=n['metadata']['name'];assert all(any(tolerates(t,tnt) for t in s['tolerations']) for tnt in n['spec'].get('taints',[]) if tnt['effect'] in ['NoSchedule','NoExecute'])
  cache=read(host+'-cache/stdout.json');assert cache['host']==host
  ls=next(c for c in cache['commands'] if c['argv'][-2:]==['images','list'])
  lines=[l.split() for l in ls['stdout_selected_lines'].splitlines()[1:] if l.strip()]
  matches=[l for l in lines if l[0]==ref];assert len(matches)<=1
  if matches:assert matches[0][2]==im['approved_top_digest']
  check=next(c for c in cache['commands'] if c['argv'][-1]=='name=='+ref)
  check_rows=[l.split() for l in check['stdout_selected_lines'].splitlines()[1:] if l.strip()]
  if matches:assert len(check_rows)==1 and check_rows[0][0]==ref and check_rows[0][-1]=='true' and 'complete' in check_rows[0]
  else:assert not check_rows
  row={'host':host,'image':im['name'],'workload_ref':ref,'expected_top_digest':im['approved_top_digest'],'eligible_by_observed_hard_constraints':True,'scheduling_capacity_guaranteed':False,'ref_present':bool(matches),'complete_and_unpacked':True if matches else None,'all_content_absent_claimed':False}
  matrix.append(row)
  if not matches:targets.append(row)
assert len(targets)==8
assert all(p['node']=='k8s-control01' for p in pods)
assert all(any(c['type']=='Ready' and c['status']=='True' for c in p['conditions']) for p in pods)
snapshotters=[]
for n in nodes:
 snap=read(n['metadata']['name']+'-snapshotter/stdout.json')
 assert snap['status']=='COLLECTED_REVIEW_REQUIRED' and snap['sample_container']['snapshotter']=='overlayfs'
 assert snap['config']['image_snapshotter']=='overlayfs'
 assert any('overlayfs' in l and l.split()[-1]=='ok' for l in snap['plugins_selected_lines'].splitlines())
 effective=read(n['metadata']['name']+'-effective-config/stdout.json')
 assert effective['status']=='COLLECTED_REVIEW_REQUIRED' and effective['effective_snapshotter']=='overlayfs'
 assert all(v in [None,'','overlayfs'] for v in effective['runtime_snapshotters'].values())
 snapshotters.append({'host':snap['host'],'observed_container_snapshotter':'overlayfs','config':snap['config'],'imports_fully_resolved':True,'effective_snapshotter':effective['effective_snapshotter']})
result={'status':'OID02_SCOPE_READY_RUNTIME_NOT_EXECUTED','at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'source_observation_at_utc':sch['finished_at_utc'],'receipts':receipts,'receipt_count':21,'node_count':6,'system_pods_ready':3,'system_pod_locations':[{'name':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['node']} for p in pods],'deployments':deps,'matrix':matrix,'targets':targets,'snapshotters':snapshotters,'image_node_gaps':8,'export_executed':False,'import_executed':False,'archive_created':False,'current_cache_as_recovery_source_adopted':False,'original_provenance_verified':False,'ac_accepted':False,'cri_binary_discovery':'Absent from root PATH and seven conventional paths on control01; absence everywhere not proved; no new installation','initial_read_failure':'crictl hardcoded path missing after ctr reads succeeded; retained; only missing CLI/space/service reads supplemented'}
(P/'ANALYSIS.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({k:result[k] for k in ['status','receipt_count','node_count','system_pods_ready','image_node_gaps','export_executed','import_executed']},ensure_ascii=False))
