"""Read-only verification of this received readiness collection; no SSH/network."""
from pathlib import Path
import hashlib,json,sys
P=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,rc in [('runner',0),('cluster',0),('runner-auth',0),('cp1-auth',255)]:
 r=read(P/name/'receipt.json');assert r['rc']==rc
 for key,filename in [('source_sha256','collector.py'),('stdout_sha256','stdout.json'),('stderr_sha256','stderr.txt')]:assert r[key]==sha(P/name/filename)
assert b'Permission denied' in (P/'cp1-auth/stderr.txt').read_bytes()
binding=read(P/'SOURCE_BINDING.json')
for row in binding:
 raw=(P/'source'/row['repo']/row['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
observed=read(P/'INPUTS.observed.json');prior=read(P/'prior-app-delivery-preparation.json')
assert observed['template_only'] is True and observed['runtime_authorized'] is False
assert observed['rollback_approved'] is False and observed['new_push_receipt'] is None
r=read(P/'runner/stdout.json');c=read(P/'cluster/stdout.json');tls=read(P/'runner-auth/stdout.json')
supplies=[x for x in r['supply'] if str(x['context']['run_id'])=='37890963668'];assert len(supplies)==1
for svc in ['transaction-api','fds-engine']:
 f=next(x for x in supplies[0]['files'] if x['path'].endswith('/'+svc+'.oci.tar'))
 assert f['sha256']==prior['build_images'][svc]['archive_sha256']==observed['build']['images'][svc]['archive_sha256']
assert tls['ca_sha256']==c['ca_sha256']==observed['kubernetes']['ca_sha256'] and tls['api_tls']['verified']
assert all(q['rc']==0 for q in c['queries'])
assert next(q for q in c['queries'] if q['kind']=='serviceaccount')['items'][0]['metadata']['uid']==observed['kubernetes']['sa_uid']
assert next(q for q in c['queries'] if q['kind']=='deployments')['items']==observed['targets_observed']
for repository in ['infra-cicd','infra-ansible']:
 for state in ['queued','in_progress']:assert read(P/'github'/f'{repository}-{state}.json')['total_count']==0
secret_names=[x['name'] for x in read(P/'github/cicd-secrets.json')['secrets']]
assert all(x not in secret_names for x in ['HARBOR_CI_ROBOT_USERNAME','HARBOR_CI_ROBOT_TOKEN'])
manifest=P/'SHA256SUMS'
count=0
if manifest.exists():
 for line in manifest.read_text().splitlines():
  digest,name=line.split('  ',1);assert sha(P/name)==digest,name;count+=1
print(json.dumps({'status':'PASS_READ_ONLY_PACKAGE','receipt_rc':[0,0,0,255],'source_files':len(binding),'archive_hashes_matched':2,'manifest_files':count,'runtime_go':False,'token_auth_verified':False}))
