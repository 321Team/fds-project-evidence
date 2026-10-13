"""Read-only verification of preserved local receipts and server projections."""
from pathlib import Path
import base64,hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
def read(path):return json.loads((P/path).read_bytes())
def sha(path):return hashlib.sha256((P/path).read_bytes()).hexdigest()
def compatible(row):return {k:row[k] for k in ['sha256','acl','xattrs']}|{'metadata':{k:row['metadata'][k] for k in ['uid','gid','mode','size','nlink','mtime_ns']}}
plan=read('INPUT.json');all_rows=[];hosts=[];receipt_count=0
for receipt in P.glob('*/receipt.json'):
 r=json.loads(receipt.read_bytes());folder=receipt.parent.relative_to(P)
 for name,key in [('collector.py','source_sha256'),('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert sha(folder/name)==r[key]
 assert r['rc']==0;receipt_count+=1
for host in plan['host_order']:
 pre=read(host+'-prepare/stdout.json');post=read(host+'-apply/stdout.json');ind=read(host+'-independent/stdout.json')
 assert pre['status']=='BACKUP_RESTORE_AND_CANDIDATE_VERIFIED' and post['status']=='APPLIED_AND_VERIFIED'
 assert post['identity_before']==post['identity_after']==pre['identity_before']==ind['identity_before']==ind['identity_after']
 assert pre['prepared']['input_sha256']==sha('INPUT.json')
 assert ind['status']=='COLLECTED_REVIEW_REQUIRED' and ind['selinux_enforce']=='1' and not ind['matching_process_snapshot']
 entries=[r for r in plan['files'] if r['host']==host];assert len(entries)==9
 changed={r['path'] for r in entries if r['action']=='REPLACE'};assert set(post['changed'])==changed and not post['restored']
 for r in entries:
  initial=pre['prepared']['files'][r['path']];actual=post['after'][r['path']];independent=next(x for x in ind['files'] if x['path']==r['path'])
  assert independent['sha256']==actual['sha256']==r['target_sha256']
  assert independent['stable_during_read'] and independent['acl']['rc']==0
  assert independent['metadata']['uid']==0 and independent['metadata']['gid']==0 and independent['metadata']['mode']=='0o750'
  assert independent['acl']['stdout'].strip()==r['acl'].strip()
  target_context='system_u:object_r:usr_t:s0' if r['action']=='REPLACE' else r['selinux']
  assert independent['xattrs']['security.selinux']['value']==target_context
  assert set(independent['xattrs'])=={'security.selinux'}
  if r['action']=='PRESERVE':assert actual==initial
  else:
   item=next(x for x in pre['prepared']['replacements'] if x['path']==r['path'])
   assert compatible(item['backup'])==compatible(item['restore_trial'])==compatible(initial)
   assert compatible(actual)==compatible(item['candidate'])
  all_rows.append({'host':host,'path':r['path'],'action':r['action'],'before_sha256':r['sha256'],'after_sha256':independent['sha256'],'selinux':target_context,'independent_read_match':True,'backup_restore_trial_verified':r['action']=='REPLACE'})
 hosts.append({'host':host,'prepared_at_utc':pre['finished_at_utc'],'applied_at_utc':post['finished_at_utc'],'independent_read_at_utc':ind['finished_at_utc'],'identity':post['identity_after'],'server_backup':post['backup_root'],'prepared_sha256':pre['prepared_sha256'],'server_result_sha256':post['server_result_sha256'],'changed_count':len(changed)})
assert len(all_rows)==45 and sum(r['action']=='REPLACE' for r in all_rows)==17
result={'status':'K8S17_APPLIED_VERIFIED','source':plan['approved_source'],'receipt_count':receipt_count,'target_files':17,'preserved_files':28,'hosts':hosts,'files':all_rows,'independent_human_review':False,'operating_tool_invocation':False,'policy_service_dns_app_change':False,'ac_accepted':False}
if len(sys.argv)==1:(P/'VERIFICATION.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
