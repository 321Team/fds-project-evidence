"""Read-only verification of this evidence package; no server/API calls."""
from pathlib import Path
import ast,base64,collections,hashlib,json,re
R=Path(__file__).resolve().parent.parent
P={'HA':R/'evidence/P1-HA-01/current-shape-20261013T000109','K8S':R/'evidence/P1-K8S-01/v4-current-metadata-20261013T000252','OID':R/'evidence/ICR-D-NET-01-01/oid02-metadata-20261013T000721','ANSIBLE':R/'evidence/P1-ANS-01/worker02-readiness-20261013','RUNNER':R/'evidence/P1-CICD-01/runner-readiness-20261013T001403'}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={};files=0;receipts=0
for key,root in P.items():
 for line in (root/'SHA256SUMS').read_text().splitlines():
  digest,name=line.split('  ',1);p=root/name;assert p.is_relative_to(root) and p.is_file();assert sha(p)==digest,(key,name);files+=1
 for p in (root/'receipts').glob('*/receipt.json'):
  r=load(p);d=p.parent
  assert sha(d/'collector.py')==r['source_sha256'];ast.parse((d/'collector.py').read_bytes())
  for name,field in [('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert sha(d/name)==r.get(field,r.get(name+'_sha256'))
  assert r['rc']==(2 if d.name=='ansible-controller' else 0);receipts+=1
 for p in root.rglob('*'):
  if p.is_file():
   raw=p.read_bytes()
   assert not re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}',raw),str(p)
assert receipts==10
checks['receipt_source_output_hashes']=receipts
m=load(P['K8S']/'reference/manifest-20261009.json');expected={(x['host'],x['path']):x['observed_sha256'] for x in m['changes']};expected.update({(x['host'],x['path']):x['sha256'] for x in m['preserve_matches']})
target={x['deployed_path']:x['sha256'] for x in m['reference_files']};rows=[]
for p in (P['K8S']/'receipts').glob('*/stdout.json'):
 d=load(p);assert d['identity_unchanged'] and not d['errors'];assert d['selinux_enforce']=='1'
 for f in d['files']:
  assert f['stable_during_read'] and f['sha256']==expected[(d['identity_before']['host'],f['path'])]
  rows.append(f)
assert len(rows)==45 and sum(x['sha256']==target[x['path']] for x in rows)==28
assert load(P['K8S']/'K8S_ANALYSIS.json')['counts']=={'files':45,'unchanged_from_previous':45,'target_matches':28,'planned_replacements':17}
source=load(P['K8S']/'K8S_SOURCE_BINDING.json');by_source={x['source_path']:x for x in m['reference_files']}
assert len(source['files'])==18 and source['approved_source']==m['approved_source_commit']
for f in source['files']:assert f['sha256']==by_source[f['path']]['sha256'] and f['size']==by_source[f['path']]['size']
checks['k8s']='45 unchanged, 28 target matches, 17 replacements; 18 Git blob metadata bindings'
d=load(P['HA']/'receipts/ha-current-control01/stdout.json');q={x['name']:x['items'] for x in d['queries']};assert all(x['rc']==0 for x in d['queries']) and d['identity_unchanged']
assert len(q['pods'])==6 and all(x['spec']['nodeName']=='k8s-worker02' for x in q['pods'])
assert all(any(c['type']=='Ready' and c['status']=='True' for c in x['status']['conditions']) for x in q['pods'])
assert len(q['nodes'])==6 and all(any(c['type']=='Ready' and c['status']=='True' for c in x['status']['conditions']) for x in q['nodes'])
assert all(len(x['endpoints'])==3 and all(e['nodeName']=='k8s-worker02' and e['conditions']['ready'] for e in x['endpoints']) for x in q['endpoints'])
ha=load(P['HA']/'HA_ANALYSIS.json');historical=R/'evidence/P1-APP-01/topology-spread-apply-supplement-20261007T0729Z/control01/p65-apply-20261007/apply/post-deploy.yaml';assert sha(historical)==ha['historical_post_deploy_sha256']
checks['ha']='6 ready Pods and 5x3 ready endpoints all on worker02; historical source hash verified (projection comparison in analysis)'
d=load(P['OID']/'receipts/oid-control01/stdout.json');assert d['status']=='MANIFEST_METADATA_VERIFIED_REVIEW_REQUIRED' and all(x['returncode']==0 for x in d['commands'])
source=P['OID']/'source/oid02-cache-metadata-readonly.py';assert sha(source)==d['collector_sha256']
tree=ast.parse((P['OID']/'receipts/oid-control01/collector.py').read_bytes())
assignment=next(x for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='source')
assert base64.b64decode(ast.literal_eval(assignment.value.args[0]))==source.read_bytes()
assert len(d['images'])==2 and all(not x['layer_bytes_verified'] and not x['original_supply_provenance_verified'] and x['archive_size_bytes'] is None for x in d['images'])
checks['oid']='exact reviewed source embedded; both metadata verified; layer/provenance/archive not claimed'
d=load(P['ANSIBLE']/'receipts/ansible-engine-utf8/stdout.json');assert d['commands'][0]['stdout'].strip()=='UTF-8' and all(c['rc']==0 for c in d['commands'])
assert all('[core 2.21.3]' in c['stdout'].splitlines()[0] for c in d['commands'][1:])
d=load(P['ANSIBLE']/'receipts/ansible-worker02/stdout.json');assert d['success'];assert d['resolv_conf_selected']==['search fds.internal','nameserver 10.1.93.52','nameserver 10.1.93.53']
checks['ansible']='DNS current target; affected 4 CLI reads succeed after process UTF-8 correction; failed record retained'
assert all(q['rc']==0 and q['total_count']==0 for q in load(P['RUNNER']/'RUNNER_READINESS.json')['queries'])
checks['runner']='queued/in_progress/registered 0 snapshot only'
print(json.dumps({'status':'PASS','manifest_files':files,'checks':checks,'scope':'local receipt integrity and derivation checks; not independent review or runtime mutation/AC'},ensure_ascii=False,indent=2))
