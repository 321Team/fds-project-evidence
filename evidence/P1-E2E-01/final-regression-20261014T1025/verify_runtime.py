"""Offline result/metric/identity verification. Never POST or modify originals."""
from pathlib import Path
import base64,collections,datetime as dt,hashlib,importlib.util,json,sys
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
def j(p):return json.loads((R/p).read_bytes())
def need(ok,msg):
 if not ok:raise AssertionError(msg)
sha='f5dee1069ab96838355cf6269dd6cdff2a08107e880594c5dad98d20424594ed'
tool=R/'remote-originals/supply/rg.py';need(hashlib.sha256(tool.read_bytes()).hexdigest()==sha,'tool bytes')
spec=importlib.util.spec_from_file_location('reviewed_rg',tool);rg=importlib.util.module_from_spec(spec);spec.loader.exec_module(rg)
out=R/'remote-originals/results';meta=rg.load_meta(str(out));got=rg.load_results(str(out),meta,complete=True)
need(meta['run']=='202610141025' and meta['today']=='2026-10-14','actual RUN')
db_before=j('DB_BEFORE_ACCEPTED.json');need(db_before['run_first']<=meta['run']<=db_before['run_last'] and db_before['existing_rows_in_planned_run_window']==0 and db_before['DB_BEFORE_RC']==0,'DB before exact range')
need(j('app-run-once/receipt.json')['rc']==0,'run rc')
counts=collections.Counter();times=[];rules=collections.Counter();responses201=[]
for cid,payload,want in rg.cases(meta['run'],meta['today']):
 r=got[cid];verdict,triggered=rg.judge_one(want,r['http'],r['body']);counts[verdict]+=1;times.append(r['t'])
 if r['http']==201:
  x=json.loads(r['body']);need(x['fds_evaluation_skipped'] is False,'skipped false');responses201.append(x['transaction_id']);rules.update(r['rule_id'] for r in x['fds_rules'] if r['triggered'])
need(dict(counts)=={'PASS':24,'INFO':1},'API24+I01')
need(len(responses201)==23 and len(set(responses201))==23,'unique201')
need(sum(x['http']==422 for x in got.values())==2,'422 negatives')
need(meta['criteria_written_epoch']<=min(times),'criteria written before requests')
for x in times:need('202610141025'<=dt.datetime.fromtimestamp(x,rg.KST).strftime('%Y%m%d%H%M')<='202610141035','time window')
receipt=j('remote-results-receipt/stdout.json')
for f in receipt['files']:
 raw=(R/'remote-originals'/f['relative']).read_bytes();need(raw==base64.b64decode(f['base64']) and hashlib.sha256(raw).hexdigest()==f['sha256'],'remote bytes '+f['relative']);need(f['uid']==1003 and f['mode']=='0o600','private remote file')
for phase in ('before','after'):
 for kind in ('app-state','cluster','edge','mon'):need(j(phase+'-'+kind+'/receipt.json')['rc']==0,phase+' '+kind)
states=[];metrics=[]
for phase in ('before','after'):
 st={x['kind']:x['items'] for x in j(phase+'-app-state/stdout.json')['queries']};states.append(st)
 qs={q['name']:json.loads(q['raw']) for q in j(phase+'-mon/stdout.json')['queries']};need(all(q['status']=='success' for q in qs.values()),'metrics queries')
 up=qs['all_up']['data']['result'];need(len(up)==23 and all(q['value'][1]=='1' for q in up),'MON23 healthy')
 need(sum(q['metric']['job'] in ('transaction-api','fds-engine') for q in up)==6,'app6 healthy')
 vals={n:float(qs[n]['data']['result'][0]['value'][1]) for n in ('save_success','save_failure','missing_client_ip','evaluated','app_up')}
 vals['detected']={q['metric']['rule_id']:float(q['value'][1]) for q in qs['detected']['data']['result']};metrics.append(vals)
 for h in j(phase+'-edge/stdout.json')['http']:need(h['status']==(404 if h['url'].endswith('/metrics') else 200),'edge health/metrics boundary')
 cluster=j(phase+'-cluster/stdout.json');need(cluster['status']=='COLLECTED_REVIEW_REQUIRED','cluster collection')
 for n in next(q['items'] for q in cluster['queries'] if q['name']=='nodes'):
  need(not n['spec']['unschedulable'],'node schedulable')
  need(all(c['status']==('True' if c['type']=='Ready' else 'False') for c in n['status']['conditions'] if c['type'] in ('Ready','MemoryPressure','DiskPressure','PIDPressure','NetworkUnavailable')),'node health')
before,after=states
for kind in ('deployments','pods','services'):
 a={p['metadata']['uid']:p for p in before[kind]};b={p['metadata']['uid']:p for p in after[kind]};need(a.keys()==b.keys(),'identities '+kind)
 for uid,p in b.items():
  if kind=='pods':need(p['statuses']==a[uid]['statuses'] and p['node']==a[uid]['node'] and not p['metadata']['deletionTimestamp'] and all(c['ready'] for c in p['statuses']),'Pod unchanged')
  elif kind=='deployments':need(p['spec_sha256']==a[uid]['spec_sha256'] and p['metadata']['generation']==a[uid]['metadata']['generation'] and p['status']['readyReplicas']==3,'Deployment unchanged')
  else:need(p['spec']==a[uid]['spec'],'Service unchanged')
delta={k:metrics[1][k]-metrics[0][k] for k in ('save_success','save_failure','missing_client_ip','evaluated')}
need(delta=={'save_success':23,'save_failure':0,'missing_client_ip':0,'evaluated':23},'metric deltas')
# Missing pre-rule children were established with metric definition/healthy targets/evaluated0.
need(metrics[0]['detected']=={} and metrics[0]['evaluated']==0 and metrics[0]['app_up']==6,'empty-rule baseline meaning')
detected_delta={k:metrics[1]['detected'].get(k,0)-metrics[0]['detected'].get(k,0) for k in ('R01','R02','R04','R07')}
need(detected_delta==dict(rules)=={'R01':1,'R02':1,'R04':1,'R07':1},'Rule deltas')
need(j('n08-control01/stdout.json')['all_code_000'],'N08 control01 code000')
dbfile=R/'db-after-user-transcript.txt';db_status='PENDING_USER_CONSOLE_OUTPUT';db_lines=[];db_times={}
if dbfile.exists():
 text=dbfile.read_text(encoding='utf-8');need('DB_AFTER_RC=0' in text and 'fdsdb|postgres|' in text,'DB after receipt')
 rc=rg.crosscheck(str(out),str(dbfile),emit=db_lines.append);need(rc==0,'DB crosscheck');need(len(rg.parse_db_log(str(dbfile)))==23,'DB23rows');db_status='23_ROWS_23_RESPONSES_MISMATCH0_USER_CONSOLE'
 dbrows=rg.parse_db_log(str(dbfile))
 for cid,payload,want in rg.cases(meta['run'],meta['today']):
  if 'occurred_at' not in payload or got[cid]['http']!=201:continue
  tid=json.loads(got[cid]['body'])['transaction_id'];have=dbrows[tid][7];db_times[cid]={'input':payload['occurred_at'],'db_display':have,'classification':'INFO' if cid=='I01' else 'EXPLICIT_OFFSET_MATCH'}
  if cid!='I01':need(dt.datetime.fromisoformat(have)==dt.datetime.fromisoformat(payload['occurred_at']),'explicit offset timestamp '+cid)
result={'status':'APP_API_METRICS_PASS_DB_PENDING' if not dbfile.exists() else 'APP_REGRESSION_RUNTIME_PASS','run':meta['run'],'tool_sha256':sha,'criteria_sha256':meta['criteria_sha256'],'first_request_kst':dt.datetime.fromtimestamp(min(times),rg.KST).isoformat(),'last_request_kst':dt.datetime.fromtimestamp(max(times),rg.KST).isoformat(),'requests':25,'HTTP201':23,'HTTP422':2,'api_counts':dict(counts),'run_rc':0,'metric_delta':delta,'detected_delta':detected_delta,'I01':{'http':got['I01']['http'],'body':json.loads(got['I01']['body']),'verdict':'INFO'},'images_specs_pod_uids_restarts_unchanged':True,'MON_up':23,'app_up':6,'N08':'3_WORKER_CODE000_FROM_CONTROL01_NO_RULE_ATTRIBUTION','db_before':'0_ROWS_USER_CONSOLE_102030','db_after':db_status,'db_crosscheck_lines':db_lines,'review':'NEW_EVIDENCE_INDEPENDENT_REVIEW_PENDING','DB11_acceptance':'AWAITING_USER_DECISION_AFTER_FINAL_REGRESSION','W4':'NOT_MEASURED'}
result['explicit_timestamp_observations']=db_times
print(json.dumps(result,ensure_ascii=False,indent=2))
