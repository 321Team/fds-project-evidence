"""Local read-only readiness decision; does not send requests or execute rg.py."""
from pathlib import Path
import datetime as dt,json
R=Path(__file__).resolve().parent;W=R.parent.parent
def j(p):return json.loads(p.read_bytes())
def read(n):return j(R/n/'stdout.json')
for n in ('before-app-state','before-cluster','before-mon','before-edge'):
 q=j(R/n/'receipt.json');assert q['rc']==0,n
 age=dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(q['finished_at_kst']);assert dt.timedelta()<=age<=dt.timedelta(minutes=2),n+' stale'
current={x['kind']:x['items'] for x in read('before-app-state')['queries']}
previous={x['kind']:x['items'] for x in j(W/'deliverables/phase1-probe-app-20261014-0945/final-app-state/stdout.json')['queries']}
for kind in ('deployments','pods'):
 now={x['metadata']['uid']:x for x in current[kind]};old={x['metadata']['uid']:x for x in previous[kind]};assert now.keys()==old.keys()
 for uid,x in now.items():
  if kind=='deployments':assert x['spec_sha256']==old[uid]['spec_sha256'] and x['metadata']['generation']==old[uid]['metadata']['generation'] and x['status']['readyReplicas']==3
  else:assert x['statuses']==old[uid]['statuses'] and x['node']==old[uid]['node'] and not x['metadata']['deletionTimestamp'] and all(c['ready'] for c in x['statuses'])
pods=current['pods'];assert len(pods)==6
svcs={s['metadata']['uid']:s['spec'] for s in current['services']}
assert svcs=={s['metadata']['uid']:s['spec'] for s in previous['services']}
for svc in ('transaction-api-nodeport','fds-engine'):
 ep=[e for s in current['endpointslices'] if s['labels'].get('kubernetes.io/service-name')==svc for e in s['endpoints']]
 assert len(ep)==3 and {e['nodeName'] for e in ep}=={'k8s-worker01','k8s-worker02','k8s-worker03'}
 assert all(e['conditions']['ready'] and e['conditions']['serving'] and not e['conditions']['terminating'] for e in ep)
cluster=read('before-cluster');assert cluster['status']=='COLLECTED_REVIEW_REQUIRED'
nodes=next(q['items'] for q in cluster['queries'] if q['name']=='nodes');assert len(nodes)==6
for n in nodes:
 assert not n['spec']['unschedulable']
 assert all(c['status']==('True' if c['type']=='Ready' else 'False') for c in n['status']['conditions'] if c['type'] in ('Ready','MemoryPressure','DiskPressure','PIDPressure','NetworkUnavailable'))
q={x['name']:json.loads(x['raw']) for x in read('before-mon')['queries']};assert all(x['status']=='success' for x in q.values())
up=q['all_up']['data']['result'];assert len(up)==23 and all(x['value'][1]=='1' for x in up)
endpoints=current['endpointslices'];ips={}
for s in endpoints:
 for e in s['endpoints']:
  if e.get('targetRef',{}).get('uid') in {p['metadata']['uid'] for p in pods}:ips[e['targetRef']['uid']]=e['addresses'][0]
expected={(p['statuses'][0]['name'],ips[p['metadata']['uid']]+(':'+('9090' if p['statuses'][0]['name']=='fds-engine' else '9091'))) for p in pods}
actual={(x['metric']['job'],x['metric']['instance']) for x in up if x['metric']['job'] in ('fds-engine','transaction-api')};assert expected==actual
for name in ('save_success','save_failure','missing_client_ip','evaluated'):
 assert len(q[name]['data']['result'])==1 and q[name]['data']['result'][0]['value'][1]=='0',name+' changed since no-other-writer confirmation'
assert q['detected']['data']['result']==[]
for x in read('before-edge')['http']:assert x['status']==(404 if x['url'].endswith('/metrics') else 200)
db=j(R/'DB_BEFORE_ACCEPTED.json');assert db['existing_rows_in_planned_run_window']==0 and db['DB_BEFORE_RC']==0 and db['run_first']=='202610141025' and db['run_last']=='202610141035'
result={'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'status':'ENTRY_CHECKS_PASS','writer_exclusion':'user confirmed through11:15','APP_requests':0,'DB_before':db,'tool_sha256':'f5dee1069ab96838355cf6269dd6cdff2a08107e880594c5dad98d20424594ed','source_review_sha':'61fbf0bf1ace1fa3a5eb983c002de2a0ddac856a','window_start':'2026-10-14T10:25:00+09:00','latest_start':'2026-10-14T10:35:00+09:00','finish_by':'2026-10-14T11:15:00+09:00'}
(R/'ENTRY_VALIDATED.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
