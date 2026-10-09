import datetime,hashlib,json,pathlib,re,subprocess,zipfile
root=pathlib.Path(__file__).resolve().parent/'private/candidate-37803786426'
root.mkdir(parents=True,exist_ok=False)
def api(path):return subprocess.check_output(['gh','api',path])
run=api('repos/321Team/fds-msa/actions/runs/37803786426');(root/'run.json').write_bytes(run)
art=api('repos/321Team/fds-msa/actions/artifacts/11561454052');(root/'artifact.json').write_bytes(art)
meta=json.loads(art);d=json.loads(run)
assert d['head_sha']=='aeb9995d626ffdc24454477038eb82d5d9e4744e' and d['run_attempt']==1 and d['conclusion']=='success'
raw=api('repos/321Team/fds-msa/actions/artifacts/11561454052/zip')
digest=hashlib.sha256(raw).hexdigest();assert 'sha256:'+digest==meta['digest']
(root/'artifact.zip').write_bytes(raw)
target=root/'original';target.mkdir()
with zipfile.ZipFile(root/'artifact.zip') as z:
 for info in z.infolist():
  path=pathlib.PurePosixPath(info.filename)
  assert not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename and ':' not in info.filename
  assert info.file_size<10000000 and (info.external_attr>>16)&0o170000!=0o120000
  p=target.joinpath(*path.parts)
  if info.is_dir():p.mkdir(parents=True,exist_ok=True)
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
verified=[]
for line in (target/'SHA256SUMS').read_text().splitlines():
 h,name=line.split(None,1);name=name.strip().removeprefix('./');p=target/name
 assert '..' not in pathlib.PurePosixPath(name).parts and not pathlib.PurePosixPath(name).is_absolute()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h;verified.append(name)
assert set(verified)=={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
prov=json.loads((target/'PROVENANCE.json').read_bytes());assert prov['source_sha']==d['head_sha']
summaries={}
for service in ('transaction-api','fds-engine'):
 report=json.loads((target/(service+'-report.json')).read_bytes());s=json.loads((target/(service+'-summary.json')).read_bytes())
 vulnerabilities=[v for r in report.get('Results',[]) for v in r.get('Vulnerabilities',[]) if v['Severity'] in ('HIGH','CRITICAL')]
 assert not vulnerabilities and s['counts']=={'HIGH':0,'CRITICAL':0}
 inspect=json.loads((target/(service+'-inspect.json')).read_bytes())[0]
 summaries[service]={'scan_counts':s['counts'],'image_config_digest':inspect['Id'],'repo_digests':inspect.get('RepoDigests',[]),'user':inspect['Config']['User'],'livez':(target/(service+'-livez.txt')).read_text().strip()}
log=subprocess.check_output(['gh','run','view','37803786426','--repo','321Team/fds-msa','--log']);(root/'run.log').write_bytes(log)
receipt={'schema':'fds.candidate-artifact-receipt.v1','received_at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'run_id':d['id'],'run_attempt':d['run_attempt'],'source_sha':d['head_sha'],'artifact_id':meta['id'],'zip_sha256':digest,'zip_api_digest_match':True,'zip_size':len(raw),'manifest_files_verified':len(verified),'coverage_all_original_files':True,'applications':summaries,'scope':'GITHUB_HOSTED_CANDIDATE_ONLY','harbor_push':'NOT_EXECUTED','cluster_deploy':'NOT_EXECUTED'}
(root/'receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps(receipt,indent=2))
