from pathlib import Path
import collections,datetime as dt,json,math,re
R=Path(__file__).resolve().parent/'phase1-short-load-window-20261014-1415'
def j(p):return json.loads(p.read_bytes())
e=R/'edge-originals/results';c=R/'control-originals'
stages=(e/'stages.log').read_text()
times={}
for stage in ['B','P']:
    s=re.findall(r'^\S+ START '+stage+r' (\d+) rps (\d+) s ([0-9.]+)$',stages,re.M)
    f=re.findall(r'^\S+ END '+stage+r' sent (\d+) ([0-9.]+)$',stages,re.M)
    assert len(s)==len(f)==1,'missing/duplicate stage start/end'
    times[stage]={'target_rps':int(s[0][0]),'planned_seconds':int(s[0][1]),'start':float(s[0][2]),'sent_log':int(f[0][0]),'end':float(f[0][1])}
idle=re.findall(r'^\S+ IDLE END ([0-9.]+) codes ',stages,re.M);assert len(idle)==1
idle_end=float(idle[0]);rows=[]
for line in (e/'requests.log').read_text().splitlines():
    x=line.split();assert len(x)==6
    rows.append({'epoch':float(x[0]),'stage':x[1],'target':x[2],'kind':x[3],'code':int(x[4]),'ms':float(x[5])})
completion=j(e/'completion.json');attempt=j(e/'regression-attempt.json')
checks={'generator_rc0':completion['generator_rc']==0 and not completion['supervisor_timeout'],'done_no_outstanding':bool(re.search(r'^\S+ DONE outstanding 0 codes ',stages,re.M)) and not re.search(r'^\S+ (STOP|FAIL) ',stages,re.M),'planned_profile':attempt['profile']=='regression' and attempt['planned_requests']==8400 and attempt['stages']==[['B',20,120],['P',50,120]],'actual8400':len(rows)==8400,'non201_zero':all(x['code']==201 for x in rows)}
stats={}
def percentile(values,p):return sorted(values)[max(0,math.ceil(len(values)*p)-1)]
for stage in ['B','P']:
    part=sorted((x for x in rows if x['stage']==stage),key=lambda x:x['epoch']);t=times[stage]
    starts=[x['epoch'] for x in part];lat=[x['ms'] for x in part]
    persecond=collections.Counter(math.floor(x-t['start']) for x in starts)
    delays=[(x-(t['start']+i/t['target_rps']))*1000 for i,x in enumerate(starts)]
    stats[stage]={'actual':len(part),'sent_log':t['sent_log'],'observed_seconds':t['end']-t['start'],'achieved_start_rps':len(part)/(t['end']-t['start']),'reference98pct_rps':t['target_rps']*.98,'reference98pct_met':len(part)/(t['end']-t['start'])>=t['target_rps']*.98,'codes':dict(collections.Counter(str(x['code']) for x in part)),'max_1sec_start_count':max(persecond.values()),'launch_delay_max_ms':max(delays),'latency_ms_nearest_rank':{'p50':percentile(lat,.5),'p95':percentile(lat,.95),'p99':percentile(lat,.99),'max':max(lat)}}
    checks[stage+'_planned_count']=len(part)==t['sent_log']==t['target_rps']*t['planned_seconds']
    checks[stage+'_completed_duration']=t['end']-t['start']>=t['planned_seconds']-.01
queries={name:j(c/(name+'.json')) for name in ['q1','q2','q3']};denom=j(c/'q3-denominator.json')
receipt=j(c/'range-receipt.json')
checks['range_success']=all(x.get('status')=='success' for x in list(queries.values())+[denom]) and receipt['q_range']['rc']==0 and not receipt['errors']
checks['range_binding']=receipt['start']==times['B']['start']-60 and receipt['end']==idle_end and receipt['step']==15
checks['range_pf_clean']=receipt['pf_stopped'] and receipt['listener_absent']
pre=j(R/'before-control/stdout.json');preq={q['kind']:q['items'] for q in pre['queries']}
podnames={x['metadata']['name'] for x in preq['pods']}
denoms={(x['metric']['pod'],float(t)):float(v) for x in denom['data']['result'] for t,v in x['values']}
series={};missing={};nan_zero=[];bad=[]
for name,data in queries.items():
    items=data['data']['result'];checks[name+'_current6pods']=len(items)==6 and {x['metric']['pod'] for x in items}==podnames
    series[name]={}
    grid=[receipt['start']+i*15 for i in range(math.floor((receipt['end']-receipt['start'])/15)+1)]
    for x in items:
        pod=x['metric']['pod'];values=[];actual=set()
        for stamp,value in x['values']:
            stamp=float(stamp);v=float(value);actual.add(round(stamp,3))
            if math.isnan(v) and name=='q3' and denoms.get((pod,stamp))==0:
                v=0.;nan_zero.append({'pod':pod,'timestamp':stamp})
            if not math.isfinite(v):bad.append({'query':name,'pod':pod,'time':stamp,'value':value});continue
            values.append((stamp,v))
        series[name][pod]=values
        missing[name+'/'+pod]=sum(round(t,3) not in actual for t in grid)
checks['no_invalid_points']=not bad
workloads={}
for workload in ['transaction-api','fds-engine']:
    names=sorted(x for x in podnames if x.startswith(workload+'-'));assert len(names)==3
    summary={'cpu_m':{},'throttle_ratio':{},'valid_points':{},'memory_max_mib':None}
    for stage in ['B','P']:
        lo=times[stage]['start']+60;hi=times[stage]['end']
        for query,label,mult in [('q1','cpu_m',1000),('q3','throttle_ratio',1)]:
            perpod={pod:[v*mult for t,v in series[query].get(pod,[]) if lo<=t<=hi] for pod in names}
            counts={pod:len(v) for pod,v in perpod.items()};summary['valid_points'][query+'_'+stage]=counts
            checks[workload+'_'+query+'_'+stage+'_valid_every_pod']=all(counts.values())
            summary[label][stage]=max((max(v) for v in perpod.values() if v),default=None)
    mem={pod:[v/1048576 for t,v in series['q2'].get(pod,[]) if times['B']['start']<=t<=idle_end] for pod in names}
    summary['valid_points']['q2_all']={pod:len(v) for pod,v in mem.items()}
    checks[workload+'_q2_valid_every_pod']=all(mem.values())
    summary['memory_max_mib']=max((max(v) for v in mem.values() if v),default=None)
    if all(v is not None for v in [summary['cpu_m']['B'],summary['cpu_m']['P'],summary['memory_max_mib']]):
        alarms={'cpu_request_m':max(100,math.ceil(summary['cpu_m']['B']*1.5/50)*50),'cpu_limit_m':math.ceil(summary['cpu_m']['P']*2/100)*100,'memory_request_mib':math.ceil(summary['memory_max_mib']*1.2/64)*64}
        alarms['memory_limit_mib']=alarms['memory_request_mib']*2;summary['section6_alarm_only']=alarms
        checks[workload+'_resource_alarm_within_current']=alarms['cpu_request_m']<=250 and alarms['cpu_limit_m']<=500 and alarms['memory_request_mib']<=256 and alarms['memory_limit_mib']<=512
    checks[workload+'_throttle_under25pct']=all(v is not None and 0<=v<.25 for v in summary['throttle_ratio'].values())
    workloads[workload]=summary
after=j(R/'after-validated.json');checks['post_observation']=after['passed']
before=j(R/'before-validated.json')
deltas={name:after['counters'][name]-before['counters'][name] for name in before['counters']}
checks['save_eval_delta']=deltas['save_success']==deltas['evaluated']==len(rows) and deltas['save_failure']==0
dbpath=R/'DB_AFTER_ACCEPTED.json';db=j(dbpath) if dbpath.exists() else None
if db:
    checks['db_count_match']=db['run']=='202610141415' and db['rc']==0 and db['stored_rows']==db['distinct_accounts']==db['distinct_transactions']==len(rows)
    checks['db_type_counts_match']=db['types']==dict(collections.Counter(x['kind'] for x in rows))
    checks['db_no_skipped_or_detection']=db['skipped']==0 and db['detected']==0
    checks['db_after_transmission']=dt.datetime.fromisoformat(db['db_timestamp']).timestamp()>=times['P']['end']
result={'run':'202610141415','at_kst':dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),'status':('RUNTIME_GATE_CHECKS_PASS_PENDING_INDEPENDENT_REVIEW' if all(checks.values()) and db else 'HTTP_METRICS_CHECKS_PASS_DB_PENDING' if all(checks.values()) else 'RUNTIME_FINDINGS_REQUIRE_REVIEW'),'checks':checks,'times':times,'idle_end':idle_end,'request_count':len(rows),'requests_by_worker':dict(collections.Counter(x['target'] for x in rows)),'requests_by_type':dict(collections.Counter(x['kind'] for x in rows)),'stage_stats':stats,'workloads':workloads,'missing_range_points':missing,'nan_with_exact_denominator0':nan_zero,'invalid_points':bad,'metric_deltas':deltas,'db':db,'limits':['2min memory does not prove10min trend','NodePort path from edge; not new Client->edge ingress POST','request log does not capture response transaction IDs','formula output is alarm only; no Resource recalculation','independent evidence review/APP E2E acceptance separate']}
(R/'RUNTIME_ANALYSIS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['run','status','checks','stage_stats','workloads','metric_deltas','db']},ensure_ascii=False))
