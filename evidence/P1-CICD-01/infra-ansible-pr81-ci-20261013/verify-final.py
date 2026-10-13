import pathlib,subprocess,json,hashlib,zipfile,tarfile,io,posixpath,collections,datetime
P=pathlib.Path(__file__).resolve().parent
REPO='321Team/infra-ansible';RUN=38330170015;JOB=115077894860;HEAD='874dc8bb052cfe3295fb79038872c785bbcc2592'
def api(path):return json.loads(subprocess.run(['gh','api','repos/'+REPO+'/'+path],check=True,stdout=subprocess.PIPE).stdout)
def digest(b):return hashlib.sha256(b).hexdigest()
def manifest_tar(t,name):
 rows=t.extractfile(name).read().decode().splitlines()
 for line in rows:
  h,f=line.split('  ',1);assert digest(t.extractfile(posixpath.join(posixpath.dirname(name),f)).read())==h,f
 return len(rows)
def main():
 j=api('actions/jobs/'+str(JOB));assert j['status']=='completed' and j['conclusion']=='success',j['status']
 assert j['head_sha']==HEAD and j['runner_id']>0
 a=api('actions/runs/'+str(RUN)+'/artifacts');assert a['total_count']==1
 a=a['artifacts'][0];assert not a['expired'] and a['workflow_run']['head_sha']==HEAD
 raw=subprocess.run(['gh','api','repos/'+REPO+'/actions/artifacts/'+str(a['id'])+'/zip'],check=True,stdout=subprocess.PIPE).stdout
 assert 'sha256:'+digest(raw)==a['digest']
 (P/('ci-artifact-'+str(a['id'])+'.zip')).write_bytes(raw)
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  excluded={v['path']:v['sha256'] for v in json.loads(z.read('ARTIFACT_SCOPE.json'))['excluded_cache_files']};counts={}
  for n in ['SHA256SUMS','fixtures/SHA256SUMS']:
   verified=0;omitted={}
   for line in z.read(n).decode().splitlines():
    h,f=line.split('  ',1);name=posixpath.join(posixpath.dirname(n),f)
    if name not in z.namelist():assert excluded.get(name)==h,name;omitted[name]=h
    else:assert digest(z.read(name))==h,name;verified+=1
   counts[n]={'verified':verified,'explicit_cache_exclusions':len(omitted)}
   if n.startswith('fixtures/'):assert omitted==excluded
  c=json.loads(z.read('CI_RESULT.json'));assert c['source_commit']==HEAD and c['status']=='PASS'
  assert all(v['rc']==0 for v in c['syntax']) and all(v['rc']==0 for v in c['fixtures']['steps'])
  ci={'artifact_id':a['id'],'artifact_sha256':digest(raw),'status':c['status'],'source_commit':c['source_commit'],'syntax_counts':dict(collections.Counter(v['engine'] for v in c['syntax'])),'fixture_steps':c['fixtures']['steps'],'manifests':counts,'production_apply':c['production_apply'],'operational_engine_transition':c['operational_engine_transition'],'scope':c['scope']}
 archive=P/'ansible-actions-runner-evidence.tar.gz';h=digest(archive.read_bytes());assert h==pathlib.Path(str(archive)+'.sha256').read_text().split()[0]
 with tarfile.open(archive) as t:
  outer=manifest_tar(t,'evidence/SHA256SUMS');home=json.loads(t.extractfile('evidence/HOME_RUN_RESULT.json').read());b=t.extractfile('evidence/original/ansible-actions-runner-evidence.tar.gz').read();assert digest(b)==t.extractfile('evidence/original/ansible-actions-runner-evidence.tar.gz.sha256').read().decode().split()[0]
  with tarfile.open(fileobj=io.BytesIO(b)) as inner:
   nested=manifest_tar(inner,'evidence/SHA256SUMS');host=json.loads(inner.extractfile('evidence/HOST_RUN_RESULT.json').read());container=json.loads(inner.extractfile('evidence/CONTAINER_RESULT.json').read());cleanup=json.loads(inner.extractfile('evidence/CLEANUP.json').read())
 assert home['host_rc']==0 and host['container_cleanup']=='REMOVED'
 assert all(cleanup[v]=='REMOVED' for v in ['runner','proxy','workspace'])
 assert container['runner']['agentId']==j['runner_id'] and container['runner']['agentName']==j['runner_name'] and container['reported_job_result']=='Succeeded'
 snapshots={name:api(path) for name,path in [('pr81','pulls/81'),('reviews','pulls/81/reviews'),('runners','actions/runners'),('run','actions/runs/'+str(RUN))]}
 assert snapshots['runners']['total_count']==0
 for name,value in {**snapshots,'job':j,'artifact':a}.items():(P/(name+'-final.json')).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
 result={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ci':ci,'host_archive_sha256':h,'host_manifest_files':outer,'nested_host_manifest_files':nested,'host':host,'container':container,'cleanup':cleanup,'head_unchanged':snapshots['pr81']['head']['sha']==HEAD}
 (P/'VERIFIED_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('verified_at','ci','host_archive_sha256','host_manifest_files','nested_host_manifest_files','cleanup','head_unchanged')},indent=2))
if __name__=='__main__':main()
