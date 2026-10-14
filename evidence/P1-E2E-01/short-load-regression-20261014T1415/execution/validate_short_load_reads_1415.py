from pathlib import Path
import datetime as dt,json,math,sys
R=Path(__file__).resolve().parent/'phase1-short-load-window-20261014-1415'
phase=sys.argv[1]
def j(p):return json.loads(p.read_bytes())
def read(name):
    receipt=j(R/name/'receipt.json');assert receipt['rc']==0,name
    return j(R/name/'stdout.json')
control=read(phase+'-control');mon=read(phase+'-mon')
q={x['kind']:x['items'] for x in control['queries']}
base={x['kind']:x['items'] for x in read('preparation-control')['queries']}
queries={x['name']:json.loads(x['raw']) for x in mon['queries']}
checks={'mon_query_success':all(v['status']=='success' for v in queries.values()),'mon_complete':len(queries)==9,'pf_stopped':mon['forwarder_stopped'] and mon['listener_absent'],'q_range_check':mon['reviewed_q_range_check']['rc']==0,'no_collector_error':not mon['errors']}
expected={'transaction-api':'338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0','fds-engine':'8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d'}
checks['deployment_identity_spec']=len(q['deployments'])==2 and all(any(x['metadata']['uid']==y['metadata']['uid'] and x['spec_sha256']==y['spec_sha256'] for y in base['deployments']) for x in q['deployments'])
checks['replicas3_ready']=all(x['replicas']==3 and x['status']['readyReplicas']==3 and x['status']['updatedReplicas']==3 and x['status']['observedGeneration']==x['metadata']['generation'] for x in q['deployments'])
checks['resources_fixed']=all(c['resources']=={'requests':{'cpu':'250m','memory':'256Mi'},'limits':{'cpu':'500m','memory':'512Mi'}} for x in q['deployments'] for c in x['containers'])
checks['six_pods_ready']=len(q['pods'])==6 and all(x['phase']=='Running' and not x['metadata']['deletionTimestamp'] and all(s['ready'] for s in x['statuses']) for x in q['pods'])
checks['pod_uids_unchanged']={x['metadata']['uid'] for x in q['pods']}=={x['metadata']['uid'] for x in base['pods']}
checks['pod_images']=all(c['imageID'].endswith('@sha256:'+expected[c['name']]) for x in q['pods'] for c in x['statuses'])
checks['restarts_unchanged']=all(any(x['metadata']['uid']==y['metadata']['uid'] and [(s['name'],s['restartCount']) for s in x['statuses']]==[(s['name'],s['restartCount']) for s in y['statuses']] for y in base['pods']) for x in q['pods'])
checks['no_oom']=all(c.get('lastState',{}).get('terminated',{}).get('reason')!='OOMKilled' for x in q['pods'] for c in x['statuses'])
checks['worker_distribution']=all(sorted(x['node'] for x in q['pods'] if any(s['name']==name for s in x['statuses']))==['k8s-worker01','k8s-worker02','k8s-worker03'] for name in expected)
checks['services_unchanged']={x['metadata']['uid']:x['spec'] for x in q['services']}=={x['metadata']['uid']:x['spec'] for x in base['services']}
ips={}
for s in q['endpointslices']:
    for e in s['endpoints']:
        if e.get('targetRef',{}).get('uid'):ips[e['targetRef']['uid']]=e['addresses'][0]
for svc in ['transaction-api-nodeport','fds-engine']:
    eps=[e for s in q['endpointslices'] if s['labels'].get('kubernetes.io/service-name')==svc for e in s['endpoints']]
    checks['endpoints_'+svc]=len(eps)==3 and {e['nodeName'] for e in eps}=={'k8s-worker01','k8s-worker02','k8s-worker03'} and all(e['conditions'].get('ready') and e['conditions'].get('serving') and not e['conditions'].get('terminating') for e in eps)
up=queries['all_up']['data']['result']
checks['all_up23']=len(up)==23 and all(x['value'][1]=='1' for x in up)
expected_targets={(s['name'],ips[p['metadata']['uid']]+(':'+('9090' if s['name']=='fds-engine' else '9091'))) for p in q['pods'] for s in p['statuses']}
actual_targets={(x['metric'].get('job'),x['metric'].get('instance')) for x in up if x['metric'].get('job') in expected}
checks['app_targets_bound']=expected_targets==actual_targets
checks['nodes_ready']=len(control['nodes'])==6 and all(not n['unschedulable'] and any(c['type']=='Ready' and c['status']=='True' for c in n['conditions']) and all(c['status']=='False' for c in n['conditions'] if c['type'] in ['MemoryPressure','DiskPressure','PIDPressure','NetworkUnavailable']) for n in control['nodes'])
values={}
for name in ['Q1','Q2','Q3','Q3_DENOM']:
    rows=queries[name]['data']['result'];values[name]={x['metric']['pod']:float(x['value'][1]) for x in rows}
    checks[name+'_six_pods']=len(rows)==6 and set(values[name])=={p['metadata']['name'] for p in q['pods']}
    checks[name+'_finite']=all(math.isfinite(v) for v in values[name].values())
checks['instant_no_throttle_limit']=all(0<=v<.25 for v in values['Q3'].values())
checks['instant_within_resource_limits']=all(0<=v<=.5 for v in values['Q1'].values()) and all(0<v<512*1048576 for v in values['Q2'].values())
counters={name:float(queries[name]['data']['result'][0]['value'][1]) for name in ['save_success','save_failure','evaluated']}
checks['save_failure_zero']=counters['save_failure']==0
if phase in ['preparation','before','after']:
    edge=read(phase+'-edge')
    checks['http_ready_and_metrics']=all(x['status']==(404 if x['url'].endswith('/metrics') else 200) for x in edge['http'])
    checks['chrony_normal']=all(x['chronyc']['rc']==0 and 'Normal' in x['chronyc']['stdout'] for x in [control,edge])
if phase=='before':
    checks['counters_no_other_writer']=counters['save_success']==23 and counters['evaluated']==23
    checks['fresh_reads']=all(0<=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(j(R/(phase+'-'+role)/'receipt.json')['finished_at_kst'])).total_seconds()<120 for role in ['control','mon','edge'])
result={'phase':phase,'at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'checks':checks,'passed':all(checks.values()),'counters':counters,'max_instant':{name:max(v.values()) for name,v in values.items()},'runtime_load_status':'not inferred from reads'}
(R/(phase+'-validated.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 2)
