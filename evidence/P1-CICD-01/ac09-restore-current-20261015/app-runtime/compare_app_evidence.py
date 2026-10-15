"""Offline independent APP evidence extraction. Never import/execute runtime collectors."""
import base64, datetime as dt, hashlib, json, re, uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=ROOT/'deliverables/p1-cicd-ac09-preparation-20261015/runtime-1535'
SNAP=HERE/'references'
index=[]
API=['transaction_save_success_total','transaction_save_failure_total','missing_client_ip_total','fds_evaluation_error_total']
ENGINE=['fds_evaluated_total']

def sha(b): return hashlib.sha256(b).hexdigest()
def snapshot(rel):
    path=SRC/rel
    if not path.is_file(): return None
    raw=path.read_bytes()
    dest=SNAP/rel; dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        assert dest.read_bytes()==raw, f'Completed source changed; use a new snapshot: {rel}'
    else: dest.write_bytes(raw)
    index.append(dict(source=str(path),local=rel,sha256=sha(raw),bytes=len(raw)))
    return raw

def record(folder):
    if not (SRC/folder/'receipt.json').is_file(): return None
    receipt=json.loads(snapshot(folder+'/receipt.json'))
    raw=snapshot(folder+'/stdout.json'); err=snapshot(folder+'/stderr.txt'); code=snapshot(folder+'/collector.py')
    assert sha(raw)==receipt['stdout_sha256'] and sha(err)==receipt['stderr_sha256']
    assert sha(code)==receipt['source_sha256'] and receipt['rc']==0
    return json.loads(raw),receipt

def requests(obj):
    if 'stdout' in obj:
        assert obj['rc']==0 and obj['pid_before']==obj['pid_after'] and obj['netns_before']==obj['netns_after']
        return json.loads(obj['stdout'])['requests']
    return obj['requests']

def body(row):
    raw=base64.b64decode(row['body_b64'],validate=True)
    assert not row['truncated'] and len(raw)==row['body_bytes'] and sha(raw)==row['body_sha256']
    return raw

def mono(folder):
    item=record(folder)
    if item is None: return None
    obj,receipt=item; pods={};up=None
    for row in requests(obj):
        assert row['status']==200
        raw=body(row)
        if row['path']=='/metrics':
            vals={}
            for line in raw.decode().splitlines():
                m=re.fullmatch(r'([a-zA-Z_:][a-zA-Z0-9_:]*) ([+-]?[0-9.eE+-]+)',line)
                if m: vals[m[1]]=float(m[2])
            service='transaction-api' if row['pod_name'].startswith('transaction-api-') else 'fds-engine'
            names=API if service=='transaction-api' else ENGINE
            for name in names+['process_start_time_seconds']:
                assert name in vals, f'Missing counter is not zero: {row["pod_name"]} {name}'
            pods[row['pod_uid']]=dict(pod=row['pod_name'],uid=row['pod_uid'],ip=row['host'],port=row['port'],
                service=service,started_utc=row['started_utc'],finished_utc=row['finished_utc'],
                process_start=vals['process_start_time_seconds'],
                counters={name:vals[name] for name in names},
                created={name:vals.get(name.removesuffix('_total')+'_created') for name in names})
        else:
            result=json.loads(raw)
            assert result['status']=='success'
            up=result['data']['result']
    assert len(pods)==6 and sum(x['service']=='transaction-api' for x in pods.values())==3
    endpoints={f'{v["ip"]}:{v["port"]}' for v in pods.values()}
    assert up is not None and len(up)==6 and {x['metric']['instance'] for x in up}==endpoints
    assert all(x['value'][1]=='1' for x in up)
    return dict(pods=pods,up_all_6=True,source=folder)

def post(phase):
    item=record(phase+'-post-one')
    if item is None: return None
    obj,receipt=item;response=json.loads(body(obj)); payload=obj['payload']
    assert obj['method']=='POST' and obj['http']==201 and obj['retry'] is False
    assert str(uuid.UUID(response['transaction_id']))==response['transaction_id']
    assert response['fds_detected'] is False and response['fds_evaluation_skipped'] is False
    rules=response['fds_rules']
    assert len(rules)==4 and {x['rule_id'] for x in rules}=={'R01','R02','R04','R07'}
    assert all(x['triggered'] is False and x['detail'] is None for x in rules)
    assert payload['amount']==10000 and payload['currency']=='KRW' and payload['transaction_type']=='deposit'
    assert dt.datetime.fromisoformat(payload['occurred_at']).tzinfo is not None
    return dict(payload=payload,response=response,http=201,source=phase+'-post-one',
                started_utc=obj['started_utc'],finished_utc=obj['finished_utc'],host=obj['host'],url=obj['url'],
                body_sha256=obj['body_sha256'],transport_receipt_classification=receipt['classification'],
                actual_operation='POST_ONE_WRITES_TRANSACTION_NOT_PURE_READ')

def state(folder):
    item=record(folder)
    if item is None:return None
    obj,_=item
    return dict(source=folder,started_utc=obj.get('started_at_utc'),finished_utc=obj.get('finished_at_utc'),
                pods=obj.get('pods'),deployments=obj.get('deployments'))

phases={}
for phase in ['r1','r2']:
    before=mono(phase+'-before-mon'); after=mono(phase+'-after-mon'); transaction=post(phase)
    runraw=snapshot(phase.upper()+'/run-final.json')
    run=None
    if runraw:
        x=json.loads(runraw); run={k:x[k] for k in ['id','status','conclusion','head_sha','run_attempt','html_url','updated_at']}
    row=dict(run=run,post=transaction,metrics_before=before,metrics_after=after,
             database_same_transaction_id='NOT_COLLECTED',database_before_zero_rows='NOT_COLLECTED_IN_REVIEWED_INPUTS')
    attempt_raw=snapshot(phase+'-post-attempt.json')
    if attempt_raw:
        attempt=json.loads(attempt_raw)
        row['database_before_zero_rows']=attempt.get('db_before','NOT_RECORDED')
    if before and after:
        assert set(before['pods'])==set(after['pods'])
        perpod=[];totals={name:0.0 for name in API+ENGINE}
        for uid,b in before['pods'].items():
            a=after['pods'][uid]
            assert (b['pod'],b['ip'],b['service'],b['process_start'],b['created'])==(a['pod'],a['ip'],a['service'],a['process_start'],a['created'])
            delta={name:a['counters'][name]-val for name,val in b['counters'].items()}
            assert all(v>=0 for v in delta.values())
            for name,val in delta.items():totals[name]+=val
            perpod.append(dict(pod=b['pod'],uid=uid,process_start_same=True,created_same=True,delta=delta))
        expected={name:(1.0 if name in ['transaction_save_success_total','fds_evaluated_total'] else 0.0) for name in API+ENGINE}
        row.update(same_six_pods=True,same_process_starts=True,per_pod_delta=perpod,
                   aggregate_delta=totals,counter_expected_match=totals==expected)
        assert transaction is not None and totals==expected
    health=[]
    for suffix in ['-before-api','-before-edge-api']:
        item=record(phase+suffix)
        if item:
            for obs in requests(item[0]):
                if 'body_b64' in obs: body(obs)
                health.append({k:obs[k] for k in ['host','port','path','status','error','pod_name','pod_uid','started_utc','finished_utc'] if k in obs})
    row['health_and_route_observations']=health
    if phase=='r1':
        s0=state('r1-state-1544');s1=state('r1-stable-before-r2')
        assert s0 is not None and s1 is not None
        p0={p['uid']:p for p in s0['pods']};p1={p['uid']:p for p in s1['pods']}
        assert set(p0)==set(p1)==set(before['pods'])
        assert all(p['deletionTimestamp'] is None and all(c['ready'] and c['restartCount']==0 for c in p['containers']) for p in list(p0.values())+list(p1.values()))
        assert all(p0[u]['containers']==p1[u]['containers'] for u in p0)
        row.update(pod_state_before=s0,pod_state_after=s1,observed_restarts_0_to_0=True)
    else:
        s0=state('r2-observer-inventory');s1=state('r2-final-state')
        if s0 and s1 and before:
            p0={p['uid']:p for p in s0['pods'] if p['uid'] in before['pods']}
            p1={p['uid']:p for p in s1['pods']}
            assert set(p0)==set(p1)==set(before['pods'])
            assert all(p['deletionTimestamp'] is None and all(c['ready'] and c['restartCount']==0 for c in p['containers']) for p in list(p0.values())+list(p1.values()))
            def selected_containers(p):
                return [{k:c[k] for k in ['name','imageID','ready','restartCount']} for c in p['containers']]
            assert all(selected_containers(p0[u])==selected_containers(p1[u]) for u in p0)
            row.update(pod_state_before=s0,pod_state_after=s1,observed_restarts_0_to_0=True)
    phases[phase]=row
result=dict(at_kst=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds'),
    stage='LOCAL_COMPARISON_OF_EXECUTOR_EVIDENCE',phases=phases,
    phase_metrics_subtracted_across_rollout=False,source_files_verified=len(index),
    new_remote_operations=0,new_post=0,new_database_query=0,ac09_final_acceptance='NOT_DECLARED')
(HERE/'APP_RUNTIME_COMPARISON.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'SOURCE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(at_kst=result['at_kst'],source_files_verified=len(index),phases={p:dict(run=r['run'],post_id=r['post']['response']['transaction_id'] if r['post'] else None,delta=r.get('aggregate_delta'),db=r['database_same_transaction_id']) for p,r in phases.items()}),ensure_ascii=False))
