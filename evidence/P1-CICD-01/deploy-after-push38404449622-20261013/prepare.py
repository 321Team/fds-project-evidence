"""Local exact plan/source preparation. No approval, dispatch, or server write."""
import ast, dataclasses, datetime, hashlib, io, json, pathlib, subprocess, sys, tarfile, uuid
OUT=pathlib.Path(__file__).parent.resolve();ROOT=OUT.parent.parent
C=ROOT/'phase1-work-20261013/cicd-inspect-field-2015'
SHA='147f760298dd4a683ea58f2a887483769352b97d';OLD='2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7'
sha=lambda x:hashlib.sha256(x).hexdigest()
def rawjson(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def save(name,x):
 raw=rawjson(x);(OUT/name).write_bytes(raw);return raw
def git(*a):return subprocess.check_output(['git',*a],cwd=C)
assert json.loads((OUT/'main.json').read_bytes())['sha']==SHA
assert git('rev-parse',SHA+'^{commit}').decode().strip()==SHA
source=OUT/'source';source.mkdir(exist_ok=False)
files={};manifest=[]
for line in git('ls-tree','-r',SHA,'tools/delivery').decode().splitlines():
 mode,kind,blob,path=line.replace('\t',' ').split(' ',3)
 if not path.endswith('.py') or pathlib.Path(path).name.startswith('test_'):continue
 assert kind=='blob' and mode in ('100644','100755')
 raw=git('show',SHA+':'+path);ast.parse(raw,path)
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
 files[path]=raw;(source/pathlib.Path(path).name).write_bytes(raw)
 manifest.append({'path':path,'git_blob':blob,'sha256':sha(raw),'bytes':len(raw)})
remote_names=['deploy_native_probe','deploy_cp1_access','deploy_binding','deploy_credential','deploy_transport','deploy_adapter','delivery_gate']
selected=set(remote_names+['transfer_native_probe','transfer_deploy_credential']);pending=list(selected)
modules={pathlib.Path(p).stem:p for p in files}
while pending:
 n=pending.pop();imports=set()
 for x in ast.walk(ast.parse(files[modules[n]])):
  if isinstance(x,ast.Import):imports.update(a.name.split('.')[0] for a in x.names)
  if isinstance(x,ast.ImportFrom) and x.module:imports.add(x.module.split('.')[0])
 for dep in imports-set(sys.stdlib_module_names)-{'__future__'}:
  assert dep in modules
  if dep not in selected:selected.add(dep);pending.append(dep)
unchanged={p:sha(raw)==sha(git('show',OLD+':'+p)) for p,raw in files.items() if pathlib.Path(p).stem in selected or pathlib.Path(p).name.startswith('deploy_')}
unchanged['.github/workflows/app-deploy.yml']=git('show',SHA+':.github/workflows/app-deploy.yml')==git('show',OLD+':.github/workflows/app-deploy.yml')
assert all(unchanged.values())
bundle={'schema':'P1-CICD-native-probe-source-1','source_sha':SHA,'files':{}}
for n in remote_names:
 p=modules[n];m=next(x for x in manifest if x['path']==p)
 bundle['files'][n+'.py']={'git_blob':m['git_blob'],'content':files[p].decode()}
bundle_raw=(json.dumps(bundle,ensure_ascii=True,sort_keys=True,separators=(',',':'))+'\n').encode()
assert len(bundle_raw)<1024*1024 and bundle_raw.count(b'\n')==1
(OUT/'native-source-147f760.json').write_bytes(bundle_raw)
package={p:raw for p,raw in files.items() if pathlib.Path(p).stem in selected}
metadata={'schema':'p1-reviewed-controller-source-1','source_commit':SHA,'files':[x for x in manifest if x['path'] in package],'remote_bundle_sha256':sha(bundle_raw),'local_module_imports_checked':True,'runtime':'NOT_EXECUTED','token_issued':False,'credentials_included':False,'git_checkout':False}
package['native-source-147f760.json']=bundle_raw;package['MANIFEST.json']=rawjson(metadata)
tarpath=OUT/'deploy-controller-147f760.tar'
with tarfile.open(tarpath,'x',format=tarfile.USTAR_FORMAT) as t:
 for p,raw in sorted(package.items()):
  info=tarfile.TarInfo('deploy-controller-147f760/'+p);info.mode=0o600;info.size=len(raw);info.mtime=0;info.uid=info.gid=0;t.addfile(info,io.BytesIO(raw))
with tarfile.open(tarpath,'r:') as t:
 assert len(t.getmembers())==len(package)
 for m in t.getmembers():
  assert m.isfile() and m.mode==0o600 and '..' not in pathlib.PurePosixPath(m.name).parts
  assert t.extractfile(m).read()==package[m.name.removeprefix('deploy-controller-147f760/')]
metadata.update(archive=tarpath.name,archive_sha256=sha(tarpath.read_bytes()),archive_bytes=tarpath.stat().st_size,members=len(package),status='LOCAL_PACKAGE_VERIFIED',unchanged_from_previous_deploy=unchanged)
save('DEPLOY_CONTROLLER_PACKAGE.json',metadata)
(OUT/(tarpath.name+'.sha256')).write_bytes((metadata['archive_sha256']+'  '+tarpath.name+'\n').encode())
sys.path.insert(0,str(source));sys.dont_write_bytecode=True
import deploy_plan as p,deploy_binding as b,delivery_gate as gate
previous=ROOT/'deliverables/phase1-push-execution-20261013-2220'
push_raw=(previous/'execute-originals/result.json').read_bytes()
assert sha(push_raw)=='8be5cef6cc47e0afcd5236f031bc7c180cdec40ba34039729741114c46f38276'
delivery_raw=(previous/'push-tbs38395350748-window0030.json').read_bytes()
assert sha(delivery_raw)=='8b7b4f4e64c271b54167bc768e4e3afc1b2326c480683aaaf4aa0ff3e18c2b06'
(OUT/'push-result.original.json').write_bytes(push_raw);(OUT/'push-input.original.json').write_bytes(delivery_raw)
cluster=json.loads((OUT/'cluster/stdout.json').read_bytes());assert all(q['rc']==0 for q in cluster['queries'])
qs={q['kind']:q['items'] for q in cluster['queries']};assert not qs['hpa']
for d in qs['deployments']:
 assert d['replicas']==3 and d['status']==dict(observedGeneration=d['metadata']['generation'],readyReplicas=3,availableReplicas=3,updatedReplicas=3)
 for node in ('worker01','worker02','worker03'):
  cache=json.loads((OUT/('cache-'+node)/'stdout.json').read_bytes())
  assert any(d['containers'][0]['image'] in x['repoDigests'] for x in cache['selected_images'])
plan={'schema':'P1-CICD-deploy-plan-2','template_only':False,'request_id':str(uuid.uuid4()),'workflow':{'repository':'321Team/infra-cicd','ref':'refs/heads/main','workflow_sha':SHA},'delivery':json.loads(delivery_raw),'push_execution':{'workflow_sha':SHA,'run_id':'38404449622','attempt':1},'push_receipt_sha256':sha(push_raw),'kubernetes':{'api_server':gate.KUBERNETES_API,'service_account':gate.SERVICE_ACCOUNT,'token_audience':b.AUDIENCE,'token_ttl_seconds':gate.TOKEN_REQUEST_SECONDS,'token_policy_reference':gate.TOKEN_POLICY_REFERENCE},'targets':{d['metadata']['name']:{'namespace':d['metadata']['namespace'],'deployment':d['metadata']['name'],'container':d['containers'][0]['name'],'uid':d['metadata']['uid'],'previous_image':d['containers'][0]['image']} for d in qs['deployments']}}
plan_raw=save('deploy-plan.unapproved.json',plan)
assert set(plan)==p.PLAN_FIELDS and p.workflow(plan['workflow'])==plan['workflow']
assert set(plan['kubernetes'])==p.KUBERNETES_FIELDS and all(set(x)==p.TARGET_FIELDS for x in plan['targets'].values())
build,targets=b.payload_checked(plan,push_raw,{'run_id':1})
save('PLAN_VALIDATION.json',{'classification':'STATIC_INPUT_BINDING_ONLY','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime_authorized':False,'approval_created':False,'dispatch_performed':False,'token_issued':False,'plan_sha256':sha(plan_raw),'request_id':plan['request_id'],'source_commit':SHA,'sa_uid':qs['serviceaccount'][0]['metadata']['uid'],'push_receipt_sha256':sha(push_raw),'targets':[dataclasses.asdict(t) for t in targets],'checks':{'pure_payload':'PASS','schema_fields':'PASS','schema_context':'Run1 is in-memory STATIC sentinel, not actual Deploy Run','fresh_target_ready_and_cached_rollback':'PASS_METADATA_ONLY','deploy_code_unchanged':all(unchanged.values()),'full_detached_approval':'NOT_RUN_PENDING_USER_DECISION','registry_repull_rollback':'NOT_VERIFIED','runtime':'NOT_EXECUTED'}})
save('EXECUTION_PROPOSAL.json',{'status':'PROPOSED_NOT_AUTHORIZED','plan_sha256':sha(plan_raw),'request_id':plan['request_id'],'not_before_kst':'2026-10-13T23:15:00+09:00','actual_start_deadline_kst':'2026-10-13T23:25:00+09:00','finish_kst':'2026-10-14T00:15:00+09:00','broker_authorization_expires_utc':'2026-10-13T15:15:00+00:00','validation_runs':1,'deploy_runs':1,'token_requests':1,'automatic_reruns':0,'allow_rollback_proposed':True,'pending':['USER_WINDOW_AND_SCOPE','CONSOLE_AND_NONOVERLAP','INDEPENDENT_EXACT_INPUT_REVIEW'],'excluded':['Push','drain','reboot','HA','Probe fault','business POST','DB writes','final acceptance']})
print(json.dumps({'plan_sha256':sha(plan_raw),'request_id':plan['request_id'],'package_sha256':metadata['archive_sha256'],'package_members':len(package),'unchanged_files':len(unchanged),'binding':'PASS_STATIC'},ensure_ascii=False))
