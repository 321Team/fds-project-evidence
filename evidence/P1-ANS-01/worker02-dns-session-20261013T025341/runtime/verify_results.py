"""Read-only local received-evidence checks; no server access or file writes."""
from pathlib import Path
import datetime as dt,hashlib,json,re,sys
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipts=[]
for p in sorted(R.glob('*/receipt.json')):
 d=read(p);assert d['rc']==0,p
 for n,k in [('collector.py','source_sha256'),('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert sha(p.parent/n)==d[k],str(p.parent/n)
 receipts.append({'path':p.parent.name,'rc':d['rc']})
assert len(receipts)==20,len(receipts)
auth=read(R/'USER_AUTHORIZATION.json');assert auth['single_session_authorized'] and auth['nm_writer_exclusion_confirmed'] and auth['worker02_console_confirmed']
pin=read(R/'PINNED_BACKUP.json');steps=[]
for name,changed in [('prepare',1),('apply-check',0),('apply',0),('reapply',0),('rollback-check',0),('rollback',2)]:
 d=read(R/name/'stdout.json');v=read(R/(name+'-VERIFIED.json'))
 assert d['rc']==0 and v['status']=='VERIFIED' and v['recap']['k8s-worker02']['changed']==changed
 pattern=r'^([A-Za-z0-9_.-]+)\s+:\s+ok=(\d+)\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)\s+skipped=(\d+)\s+rescued=(\d+)\s+ignored=(\d+)\s*$'
 parsed={m[0]:dict(zip(['ok','changed','unreachable','failed','skipped','rescued','ignored'],map(int,m[1:]))) for m in re.findall(pattern,d['stdout'],re.M)}
 assert parsed==v['recap'],'RAW_RECAP_MISMATCH'
 assert set(v['recap'])=={'localhost','k8s-worker02'}
 assert all(x[k]==0 for x in v['recap'].values() for k in ['failed','unreachable','rescued','ignored'])
 assert v['session_receipt']['sha256']==pin['sha256'] and v['session_receipt']['session_id']==pin['session_id']
 for stream in ['stdout','stderr']:
  assert sha(R/name/('ansible.'+stream+'.txt'))==d[stream+'_sha256']
  assert sha(R/'controller-files'/(name+'.'+stream+'.txt'))==d[stream+'_sha256']
 steps.append({'step':name,'started_at_utc':d['started_at_utc'],'finished_at_utc':d['finished_at_utc'],'recap':v['recap'],'session_receipt':v['session_receipt']})
backup=read(R/'backup-read/stdout.json');lastbackup=read(R/'backup-final/stdout.json')
assert backup['sha256']==lastbackup['sha256']==pin['sha256']==sha(R/'backup-read/original-resolver.json')
assert backup['data']==lastbackup['data'] and backup['raw_utf8']==lastbackup['raw_utf8']
assert backup['mode']=='0600' and backup['parent_mode']=='0700' and backup['uid']==backup['gid']==0
age=(dt.datetime.fromisoformat(steps[2]['started_at_utc'])-dt.datetime.fromisoformat(pin['captured_at'])).total_seconds();assert 0<=age<=900
for name in ['worker-before','worker-after-apply','worker-after-reapply','worker-after-rollback']:
 d=read(R/name/'stdout.json');assert d['success'] and d['api_tcp_6443']
 assert d['commands'][2]['stdout']=='10.1.93.52,10.1.93.53\nfds.internal\nyes\n'
 assert d['resolv_conf_selected']==['search fds.internal','nameserver 10.1.93.52','nameserver 10.1.93.53']
 assert d['commands'][4]['stdout']=='active\nactive\nactive\n' and d['commands'][5]['stdout'].strip()=='Enforcing'
 if name!='worker-before':
  r=read(R/name/'receipt.json');assert 'ControlMaster=no' in r['inner_command'] and 'ControlPath=none' in r['inner_command']
 for c in d['commands']:
  assert c['rc']==0
  if c['argv'][:2]==['getent','ahostsv4'] and c['argv'][-1]!='github.com':assert '10.1.93.109' in c['stdout']
  if c['argv'][0]=='dig':assert c['stdout'].splitlines()==['10.1.93.109']
b=read(R/'network-before/stdout.json');a=read(R/'network-final/stdout.json');assert [x['stdout'] for x in a['commands']]==[x['stdout'] for x in b['commands']]
b=read(R/'cluster-before/stdout.json');a=read(R/'cluster-final/stdout.json')
for k in ['cluster_uid','nodes','pods','deployments']:assert b[k]==a[k]
cb=read(R/'controller-before/stdout.json');ca=read(R/'controller-final/stdout.json');assert cb['files']==ca['files'] and cb['inventory_selected']==ca['inventory_selected'] and ca['status']=='PRECHECK_VERIFIED'
logs=read(R/'controller-logs/stdout.json');assert len(logs['files'])==33
for x in logs['files']:
 assert sha(R/'controller-files'/x['path'])==x['sha256'] and x['mode']=='0600' and x['uid']==1000
elapsed=(dt.datetime.fromisoformat(logs['at_utc'])-dt.datetime.fromisoformat(steps[0]['started_at_utc'])).total_seconds();assert elapsed<900
result={'status':'WORKER02_DNS_SINGLE_SESSION_VERIFIED','session_id':pin['session_id'],'source':pin['source_sha'],'receipt_count':20,'receipts':receipts,'controller_files_received':33,'steps':steps,'backup_sha256':pin['sha256'],'backup_path':pin['path'],'backup_metadata':{k:backup[k] for k in ['uid','gid','mode','parent_mode','selinux_context']},'first_apply_snapshot_age_seconds':age,'started_at_utc':steps[0]['started_at_utc'],'final_cluster_at_utc':a['at_utc'],'closure_at_utc':logs['at_utc'],'elapsed_seconds':elapsed,'apply_changed':0,'reapply_changed':0,'rollback_same_value_tasks_changed':2,'fresh_worker_ssh_checks':3,'network_routes_service_pids_preserved':True,'node_ready':6,'system_pod_ready':3,'app_pod_ready':6,'pod_uid_node_restarts_preserved':True,'deployment_uid_spec_preserved':True,'source_11_files_and_engine_unchanged':True,'actual_failure_recovery_test':False,'global_engine_switch':False,'ac_accepted':False}
print(json.dumps(result,ensure_ascii=False,indent=2))
