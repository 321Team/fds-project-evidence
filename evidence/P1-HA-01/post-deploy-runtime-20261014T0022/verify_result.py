"""Local verification only; runtime originals are never changed."""
from pathlib import Path
import json,hashlib,datetime as dt,subprocess,sys,collections,os
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
def load(p):return json.loads((P/p).read_bytes())
def sha(p):return hashlib.sha256((P/p).read_bytes()).hexdigest()
receipts=[]
for f in sorted(P.glob('*/receipt.json')):
 r=json.loads(f.read_bytes());base=f.parent.relative_to(P)
 assert sha(base/'collector.py')==r['source_sha256'] and sha(base/'stdout.json')==r['stdout_sha256'] and sha(base/'stderr.txt')==r['stderr_sha256'],str(f)
 assert r['rc']==(2 if str(base)=='engine-recovery' else 0),(str(base),r['rc'])
 receipts.append({'step':str(base),'rc':r['rc']})
b=load('READINESS_BINDING.json') if (P/'READINESS_BINDING.json').exists() else json.loads((P.parent/'READINESS_BINDING.json').read_bytes())
probe=load('edge-originals/probe-result.json');assert probe['rc']==0 and probe['child_exited'] and probe['probe_runs']==1
assert dt.datetime.fromisoformat('2026-10-13T15:15:00+00:00').timestamp()<=probe['started_wall']<dt.datetime.fromisoformat('2026-10-13T15:25:00+00:00').timestamp()
assert probe['finished_wall']-probe['started_wall']>=900
assert 'ticks 1801 outstanding 0 saturated False' in (P/'edge-originals/probe.stdout').read_text() and not (P/'edge-originals/probe.stderr').read_bytes()
assert sha('edge-originals/ha-probe.py')=='e2603769cacef36dab6231052104f29f413b105a78d771b4e4c3db3c0a599804'
assert sha('edge-originals/ha-judge.py')=='79f54c955991dacd0767885b0db5001fad39080ea7cf4b7c2a3ea13c6f1a6aad'
rows=[line.split() for line in (P/'edge-originals/probe.log').read_text().splitlines()];assert len(rows)==5403
ticks=collections.defaultdict(list)
for r in rows:assert len(r)==7;ticks[int(r[0])].append(r[3])
assert sorted(ticks)==list(range(1801)) and all(sorted(v)==['10.1.93.105','10.1.93.107','10.1.93.108'] for v in ticks.values())
remote=load('judge-run/stdout.json');assert remote['rc']==0 and remote['timeline_sha256']==sha('control-originals/timeline.txt') and remote['probe_log_sha256']==sha('edge-originals/probe.log')
j=subprocess.run([sys.executable,str(P/'edge-originals/ha-judge.py'),str(P/'edge-originals/probe.log'),str(P/'control-originals/timeline.txt'),'10.1.93.107'],capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
assert j.returncode==remote['rc'] and j.stdout==remote['stdout'] and not j.stderr
drain=load('control-originals/drain-result.json');assert drain['run_count']==1 and drain['rc']==0 and len(drain['selected_pods'])==2
assert {p['uid'] for p in drain['selected_pods']}=={p['metadata']['uid'] for p in b['initial_target_pods']}
uncordon=load('control-originals/uncordon-result.json');assert uncordon['rc']==0 and not uncordon['unschedulable'] and uncordon['readback_uid']==b['target_node']['metadata']['uid']
for app in ('fds-engine','transaction-api'):
 ev=load('control-originals/'+app+'-eviction-result.json');assert ev['eviction_command_invocations']==1 and ev['request']['rc']==0 and ev['guard']=='PASS'
 assert json.loads(ev['request']['stdout'])['status']=='Success' and ev['target']['deleteOptions']['gracePeriodSeconds']==30
 marks=dict(line.split() for line in (P/'control-originals/timeline.txt').read_text().splitlines())
 assert dt.datetime.fromisoformat(ev['dispatch_at_utc']).timestamp()>float(marks['end'])
rec=load('engine-observer-supplement/stdout.json');assert rec['status']=='READY_MON_STABLE' and rec['original_mon_observations']==rec['original_mon_correctly_matched']==29
assert rec['mon_first_valid_epoch']-rec['ready_epoch']<=90
api=load('api-recovery/stdout.json');assert api['status']=='READY_MON_STABLE' and api['mon_epoch']-api['ready_epoch']<=90
for recovery in (rec,api):assert recovery['stability'][-1]['state']['epoch']-recovery['stability'][0]['state']['epoch']>=30
assert dt.datetime.fromisoformat(load('api-eviction/stdout.json')['dispatch_at_utc']).timestamp()>rec['finished_epoch']
aq={q['kind']:q['items'] for q in load('final-app-state/stdout.json')['queries']}
for d in aq['deployments']:
 fixed=next(x for x in b['deployments'] if x['metadata']['name']==d['metadata']['name'])
 assert d['metadata']['uid']==fixed['metadata']['uid'] and d['metadata']['generation']==fixed['metadata']['generation'] and d['spec_sha256']==fixed['spec_sha256']
 assert all(d['status'][k]==3 for k in ('readyReplicas','updatedReplicas','availableReplicas'))
pods=aq['pods'];assert len(pods)==6
for d in b['deployments']:
 rs=next(x['metadata']['uid'] for x in b['active_replica_sets'] if x['metadata']['ownerReferences'][0]['uid']==d['metadata']['uid'])
 pp=[p for p in pods if p['owners'][0]['uid']==rs]
 assert len(pp)==3 and sorted(p['node'] for p in pp)==['k8s-worker01','k8s-worker02','k8s-worker03']
 assert all(not p['metadata']['deletionTimestamp'] and all(c['ready'] and c['restartCount']==0 and c['imageID']==d['image'] for c in p['statuses']) for p in pp)
for e in aq['endpointslices']:
 assert len(e['endpoints'])==3 and all(x['conditions']['ready'] and not x['conditions'].get('terminating') for x in e['endpoints'])
 assert sorted(x['nodeName'] for x in e['endpoints'])==['k8s-worker01','k8s-worker02','k8s-worker03']
c=load('final-cluster/stdout.json');cq={q['name']:q['items'] for q in c['queries']}
assert c['identity_before']==c['identity_after']==b['control_identity'] and cq['cluster'][0]['metadata']['uid']==b['cluster']['uid']
for n in cq['nodes']:
 cond={x['type']:x['status'] for x in n['status']['conditions']};assert cond['Ready']=='True' and all(cond[k]=='False' for k in ('MemoryPressure','DiskPressure','PIDPressure'))
 if n['metadata']['name'].startswith('k8s-worker'):assert not n['spec']['unschedulable'] and not n['spec']['taints']
assert not cq['pdb'] and not cq['hpa']
edge=load('final-edge/stdout.json');assert all(h['status']==(404 if h['url'].endswith('/metrics') else 200) for h in edge['http'])
mon=load('final-mon/stdout.json');assert mon['forwarder_stopped'];up=json.loads(mon['queries'][0]['raw'])['data']['result']
assert len(up)==23 and all(x['value'][1]=='1' for x in up)
expected={(p['metadata']['labels']['app'],p['status']['podIP']+(':'+str(9091 if p['metadata']['labels']['app']=='transaction-api' else 9090))) for p in cq['pods']}
actual={(x['metric']['job'],x['metric']['instance']) for x in up if x['metric']['job'] in ('transaction-api','fds-engine')};assert actual==expected
result={'status':'HA_RUNTIME_PASS_AND_RECOVERY_VERIFIED','judge':remote['stdout'],'probe_seconds':900,'probe_requests':len(rows),'drain_runs':1,'additional_evictions':2,'final_counts':api['final_counts'],'final_mon_up':23,'images_specs_unchanged':True,'node_uncordoned':True,'observer_correction_preserved':True,'receipts':receipts,'runtime_completed_at_kst':dt.datetime.fromtimestamp(probe['finished_wall'],dt.timezone(dt.timedelta(hours=9))).isoformat(),'independent_evidence_review':'PENDING','app_regression':'NOT_RUN','http_probe_fault':'NOT_RUN','db_acceptance':'PENDING_FINAL_APP_REGRESSION','W4':'NOT_MEASURED'}
if len(sys.argv)==1:
 with (P/'VERIFIED_RESULT.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='receipts'},ensure_ascii=False,indent=2))
