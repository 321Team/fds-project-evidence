from pathlib import Path
import datetime,json,sys
P=Path(__file__).resolve().parent;label=sys.argv[1]
def read(s):return json.loads((P/s/'stdout.json').read_bytes())
c=read(label+'-cluster');q={r['name']:r for r in c['queries']};errors=[]
if c['status']!='COLLECTED':errors.append('COLLECT_INCOMPLETE')
pods=q['pods']['items'];counts={};mon_expected={}
for name,port in [('fds-engine',9090),('transaction-api',9091)]:
 pp=[p for p in pods if p['metadata']['labels'].get('app')==name]
 counts[name]={w:sum(p['node']==w for p in pp) for w in ['k8s-worker01','k8s-worker02','k8s-worker03']}
 if len(pp)!=3 or any(not p['ready'] or p['metadata']['deletionTimestamp'] for p in pp):errors.append(name+'_PODS_NOT_STABLE')
 now=datetime.datetime.fromisoformat(c['at_utc'])
 for pod in pp:
  condition=next((x for x in pod['conditions'] if x['type']=='Ready'),{})
  transition=condition.get('lastTransitionTime')
  if not transition or (now-datetime.datetime.fromisoformat(transition.replace('Z','+00:00'))).total_seconds()<30:errors.append(name+'_READY_30S_WAIT')
 mon_expected[name]={p['pod_ip']+':'+str(port) for p in pp if p.get('pod_ip')}
 for svc in ([name,'fds-engine-metrics'] if name=='fds-engine' else [name,'transaction-api-nodeport','transaction-api-metrics']):
  ee=[e for s in q['endpoints']['items'] if s['metadata']['labels'].get('kubernetes.io/service-name')==svc for e in s['endpoints']]
  if len(ee)!=3 or any(e['conditions'].get('ready') is not True or e['conditions'].get('terminating') for e in ee) or {e['targetRef']['uid'] for e in ee}!={p['metadata']['uid'] for p in pp}:errors.append(svc+'_ENDPOINTS_NOT_STABLE')
m=read(label+'-mon');baseline=read('before-mon')
try:
 current=json.loads(m['queries'][0]['raw'])['data']['result'];old=json.loads(baseline['queries'][0]['raw'])['data']['result']
 for app,expected in mon_expected.items():
  actual=[r for r in current if r['metric'].get('job')==app]
  if {r['metric']['instance'] for r in actual}!=expected or any(r['value'][1]!='1' for r in actual):errors.append(app+'_MON_WAIT')
 def other(rows):return {(r['metric'].get('job'),r['metric'].get('instance')):r['value'][1] for r in rows if r['metric'].get('job') not in mon_expected}
 if other(current)!=other(old) or len(other(current))!=17:errors.append('OTHER_MON_CHANGED')
 if not m['forwarder_stopped']:errors.append('FORWARDER_NOT_STOPPED')
 rw=json.loads(m['queries'][1]['raw'])['data']['result']
 if len(rw)!=1 or float(rw[0]['value'][1])!=0:errors.append('RW_FAILURES_CHANGED')
except Exception as e:errors.append('MON_READ_ERROR:'+str(e))
e=read(label+'-edge')
if e['requests'][0]['rc']!=0 or e['requests'][0]['http_code']!='200':errors.append('EDGE_READYZ_FAILED')
for row,node in zip(e['requests'][1:],['k8s-worker01','k8s-worker02','k8s-worker03']):
 if counts['transaction-api'][node]>0 and (row['rc']!=0 or row['http_code']!='200'):errors.append(node+'_NODEPORT_FAILED')
fixed=json.loads((P/'APP_BINDING.json').read_bytes())
for d in q['deployments']['items']:
 f=next(x for x in fixed['deployments'] if x['metadata']['name']==d['metadata']['name'])
 if d['metadata']['uid']!=f['metadata']['uid'] or d['spec_sha256']!=f['spec_sha256']:errors.append('DEPLOYMENT_CHANGED')
result={'label':label,'at_utc':c['at_utc'],'counts':counts,'pods':[{'name':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['node'],'ready':p['ready']} for p in pods],'errors':errors,'status':'OBSERVATION_STABLE' if not errors else 'NOT_STABLE'}
(P/(label+'-analysis.json')).write_bytes((json.dumps(result,indent=2)+'\n').encode())
if not errors:(P/(label+'-counts.json')).write_bytes((json.dumps(counts,indent=2)+'\n').encode())
print(json.dumps(result));raise SystemExit(0 if not errors else 2)
