"""Read-only completion checks and derived evidence; never dispatch or POST."""
import base64, concurrent.futures, json, re
import runtime as r

def http(label):
    v=r.load(r.O/label/'stdout.json')
    if 'stdout' in v:
        assert v['rc']==0 and v['pid_before']==v['pid_after'] and v['netns_before']==v['netns_after']
        v=json.loads(v['stdout'])
    return v['requests']

names=['transaction_save_success_total','transaction_save_failure_total','missing_client_ip_total','fds_evaluated_total','fds_evaluation_error_total']
inv=r.load(r.O/'r2-observer-inventory/stdout.json')
pods=[p for p in inv['pods'] if p['namespace']=='fds-app']
assert len(pods)==6
totals={}; times=[]
for sample in ['before','after']:
    reqs=http('r2-'+sample+'-mon'); assert len(reqs)==7
    assert all(v['status']==200 and not v.get('error') and not v['truncated'] for v in reqs)
    totals[sample]={}
    for name in names:
        app='fds-engine' if name=='fds_evaluated_total' else 'transaction-api'
        ids={p['uid'] for p in pods if p['labels'].get('app')==app}
        selected=[x for x in reqs[:6] if x['pod_uid'] in ids]; assert len(selected)==3
        values=[]
        for x in selected:
            text=base64.b64decode(x['body_b64']).decode()
            matches=re.findall(r'^'+name+r'(?:\{[^\n]*\})?\s+([\d.eE+\-]+)(?:\s|$)',text,re.M)
            assert len(matches)==1, (name,len(matches)); values.append(float(matches[0]))
        totals[sample][name]=sum(values)
    up=json.loads(base64.b64decode(reqs[-1]['body_b64']))['data']['result']
    assert len(up)==6 and all(v['value'][1]=='1' for v in up)
    expected={p['ip']+(':'+('9091' if p['labels']['app']=='transaction-api' else '9090')) for p in pods}
    assert {v['metric']['instance'] for v in up}==expected
    if sample=='before':times.extend(x['finished_utc'] for x in reqs)
delta={name:totals['after'][name]-totals['before'][name] for name in names}
assert list(delta.values())==[1,0,0,1,0],delta
for label in ('edge-api','api'):
    reqs=http('r2-before-'+label); assert len(reqs)==9
    assert all(x['status']==(404 if x['path']=='/metrics' else 200) and not x['truncated'] and not x.get('error') for x in reqs)
    times.extend(x['finished_utc'] for x in reqs)
post=r.load(r.O/'r2-post-one/stdout.json');body=json.loads(base64.b64decode(post['body_b64']))
assert post['http']==201 and body['fds_detected'] is False and body['fds_evaluation_skipped'] is False
assert len(body['fds_rules'])==4 and all(v['triggered'] is False and v['detail'] is None for v in body['fds_rules'])
r.save(r.O/'R2_MINIMUM_HTTP_METRICS.json',{'http':201,'transaction_id':body['transaction_id'],'totals':totals,'delta':delta,'prometheus_up':6,'db_row_match':'NOT_COLLECTED','result':'HTTP_AND_COUNTERS_MATCH_DB_NOT_VERIFIED'})
r.save(r.O/'RECOVERY_HTTP_CONFIRMED.json',{'at_utc':r.now().isoformat(),'recovery_observation_upper_utc':max(times),'no_old_pods_source':'R2_CURRENT_PODS.json','direct_business_metrics':{'api_3':404,'engine_3':404},'live_ready_6':200,'dedicated_metrics_6':200,'prometheus_up':6,'clock_error_applied':False,'exact_old_termination':'NOT_MEASURED'})
tasks=[('r2-final-state','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,r.O/'state_read.py',[]),('final-runner','10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,r.B/'round5/runner_activity_read.py',[])]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p: results=list(p.map(r.collect.remote,tasks))
assert all(x['rc']==0 for x in results)
state=r.load(r.O/'r2-final-state/stdout.json'); start=r.load(r.O/'entry-management/stdout.json')
for d in state['deployments']:
    a=next(x for x in start['deployments'] if x['name']==d['name'])
    assert all(a[k]==d[k] for k in ['uid','image','replicas','normalized_spec_sha256'])
    assert all(d['status'][k]==3 for k in ['replicas','updatedReplicas','readyReplicas','availableReplicas'])
assert {p['uid'] for p in state['pods']}=={p['uid'] for p in pods}
assert all(p['deletionTimestamp'] is None and all(c['ready'] and c['restartCount']==0 for c in p['containers']) for p in state['pods'])
assert all(x['name']!='Runner.Worker' for x in r.load(r.O/'final-runner/stdout.json')['processes'])
r.save(r.O/'R2_STABLE_FINAL.json',{'observed_utc':state['finished_at_utc'],'same_current_pod_uids':True,'ready_pods':6,'restarts':0,'unchanged_uid_and_nonimage_spec':True,'runner_worker':0})
r.status('R2 현행 복원 완료: 15:51:34 이전 Pod 전부 부재, 15:51:37까지 직접 업무포트 metrics 6개 404·전용 metrics 6개 200·Prometheus up 6 확인(시계오차 최종 대조 전). R2 최소 입금 1회도 HTTP201·저장/평가 각 +1·오류 증가0, 같은 현행 Pod6/각Ready3·restart0·UID/비이미지 사양 불변. false2/true2·Token2·POST2 소진, 추가 실행 없음. DB 동일 ID 행 검증은 미수집. 임시 공급 파일 정리·발급2건 만료 시각 대조·최종 원본 마감 진행 중이며 아직 창 반환 선언 전.')
print(json.dumps({'delta':delta,'recovery_upper':max(times),'pod6_stable':True,'runner_worker':0},ensure_ascii=False))
