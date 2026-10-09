"""Bounded historical Prometheus GETs through the existing Kubernetes API."""
import datetime,hashlib,json,os,socket,subprocess,urllib.parse
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def gate():
    assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'
gate()
base='/api/v1/namespaces/monitoring-api/services/prometheus:9090/proxy/api/v1/query'
queries=[
 ('app_counters_raw_5m','{__name__=~"transaction_save_(success|failure)_total|fds_evaluation_error_total"}[5m]','2026-10-08T11:30:00Z'),
 ('http_metric_names_before','count by (__name__) ({__name__=~".*(http|request).*"})','2026-10-08T11:26:49Z'),
 ('http_metric_names_after','count by (__name__) ({__name__=~".*(http|request).*"})','2026-10-08T11:27:52Z'),
 ('scrape_health_raw_5m','up[5m]','2026-10-08T11:30:00Z'),
]
out={'schema':'fds.w4-prometheus-history.v1','host':socket.gethostname(),'started_at_kst':now(),'queries':[],
     'boundary':'Historical GET only. No test request, scrape/config change, deployment or Harbor access. Only metric names and bounded label allowlist exported.'}
for label,query,at in queries:
    gate(); path=base+'?'+urllib.parse.urlencode({'query':query,'time':at,'timeout':'5s'})
    cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','get','--raw='+path]
    started=now()
    p=subprocess.run(cmd,capture_output=True,timeout=15)
    row={'label':label,'command':cmd,'started_at_kst':started,'finished_at_kst':now(),'rc':p.returncode,'body_sha256':hashlib.sha256(p.stdout).hexdigest(),'body_size':len(p.stdout)}
    if p.returncode==0 and len(p.stdout)<=4*1024*1024:
        data=json.loads(p.stdout);row['status']=data.get('status');row['resultType']=data.get('data',{}).get('resultType');row['results']=[]
        for x in data.get('data',{}).get('result',[])[:256]:
            metric={k:v for k,v in x.get('metric',{}).items() if k in ('__name__','job','instance','pod','namespace','service','container','status','code','method')}
            row['results'].append({'metric':metric,**{k:x[k] for k in ('value','values') if k in x}})
        row['result_count']=len(data.get('data',{}).get('result',[]));row['warnings']=data.get('warnings',[])
    else:row['error']='GET failed or response cap exceeded';row['stderr']=p.stderr.decode(errors='replace')[:2048]
    out['queries'].append(row)
    if p.returncode:break
out['finished_at_kst']=now();print(json.dumps(out))
