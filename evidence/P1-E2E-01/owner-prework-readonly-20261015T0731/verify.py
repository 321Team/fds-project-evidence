"""Offline receipt/integrity and recorded-observation checks; no network/server access."""
import ast,hashlib,json,pathlib,sys
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def verify():
 manifest=R/'SHA256SUMS'
 covered=set()
 for line in manifest.read_text(encoding='utf-8').splitlines():
  digest,name=line.split('  ',1);p=(R/name).resolve()
  assert p.is_relative_to(R) and p.is_file(),('MANIFEST_PATH',name)
  assert sha(p)==digest,('HASH',name);covered.add(name)
 actual={p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS'}
 assert covered==actual,('MANIFEST_COVERAGE',actual-covered,covered-actual)
 commands=0;success=0
 for d in sorted((R/'runtime').iterdir()):
  receipt=read(d/'receipt.json')
  assert sha(d/'collector.py')==receipt['collector_sha256']
  assert sha(d/'bridge.py')==receipt['bridge_sha256']
  assert sha(d/'stdout.json')==receipt['stdout_sha256']
  assert sha(d/'stderr.txt')==receipt['stderr_sha256']
  ast.parse((d/'collector.py').read_bytes());ast.parse((d/'bridge.py').read_bytes())
  if d.name=='edge-read-01':
   assert receipt['rc']==1 and not (d/'stdout.json').read_bytes()
   continue
  assert receipt['rc']==0 and not (d/'stderr.txt').read_bytes()
  data=read(d/'stdout.json');assert data['status']=='READ_COMPLETE_REVIEW_REQUIRED'
  assert data['host']==receipt['target']
  assert all(c['rc']==0 for c in data['commands'])
  for c in data['commands']:
   argv=c['argv']
   if argv[0].endswith('kubectl'):assert 'get' in argv and not {'secret','secrets','exec','apply','patch','delete'}&set(argv)
   elif argv[0].endswith('systemctl'):assert argv[1] in ['show','list-unit-files']
   else:assert argv[:3]==['/usr/sbin/ss','-H','-ltn']
  commands+=len(data['commands']);success+=1
 assert success==9 and commands==41,(success,commands)
 comparison=read(R/'COMPARISON.json');assert all(comparison['checks'].values())
 edge=read(R/'runtime/edge-read-02/stdout.json')
 conf=next(x for x in edge['files'] if x['path']=='/etc/nginx/conf.d/fds.conf')
 assert conf['sha256']==sha(R/'reference/169-upstream-file.after')==comparison['fds_conf_sha256']
 g=read(R/'runtime/grafana-read-01/stdout.json')
 assert all('sha256' not in x for x in g['credential_files'])
 assert all(not x['literal_value_present'] for x in g['grafana']['secret_refs'])
 assert len(comparison['boots'])==6
 return {'status':'FILE_INTEGRITY_AND_RECORDED_OBSERVATIONS_PASS','files':len(covered),'successful_collections':success,'failed_precollection':1,'recorded_read_commands':commands,'new_transaction_test':False,'independent_review':'NOT_PERFORMED','ac_acceptance':'NOT_PERFORMED'}
if __name__=='__main__':
 try:print(json.dumps(verify(),ensure_ascii=False))
 except Exception as e:print(json.dumps({'status':'FAIL','reason':str(e)},ensure_ascii=False));sys.exit(1)
