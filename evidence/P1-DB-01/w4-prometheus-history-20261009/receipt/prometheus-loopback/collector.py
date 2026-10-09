import datetime,hashlib,json,os,socket,subprocess
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
assert socket.gethostname()=='k8s-worker03' and os.geteuid()==0
assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'
uid='265ca811-873c-45e1-8c46-6c1ce034e596'
p=subprocess.run(['crictl','ps','-o','json'],capture_output=True,timeout=10)
assert p.returncode==0
matches=[c for c in json.loads(p.stdout)['containers'] if c.get('labels',{}).get('io.kubernetes.pod.uid')==uid and c.get('metadata',{}).get('name')=='prometheus']
assert len(matches)==1
cid=matches[0]['id']
def inspect():
    p=subprocess.run(['crictl','inspect',cid],capture_output=True,timeout=10)
    assert p.returncode==0
    d=json.loads(p.stdout)
    assert d['status']['labels']['io.kubernetes.pod.uid']==uid and d['status']['state']=='CONTAINER_RUNNING'
    return int(d['info']['pid'])
pid=inspect(); netns=os.readlink('/proc/'+str(pid)+'/ns/net')
code=r'''
import datetime,hashlib,http.client,json,urllib.parse
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
queries=[
('app_counters_raw_5m','{__name__=~"transaction_save_(success|failure)_total|fds_evaluation_error_total"}[5m]','2026-10-08T11:30:00Z'),
('http_metric_names_before','count by (__name__) ({__name__=~".*(http|request).*"})','2026-10-08T11:26:49Z'),
('http_metric_names_after','count by (__name__) ({__name__=~".*(http|request).*"})','2026-10-08T11:27:52Z'),
('scrape_health_raw_5m','up[5m]','2026-10-08T11:30:00Z')]
rows=[]
for label,query,at in queries:
    assert '2026-10-09T00:00:00+09:00'<=now()<'2026-10-09T09:00:00+09:00'
    path='/api/v1/query?'+urllib.parse.urlencode({'query':query,'time':at,'timeout':'5s'})
    row={'label':label,'query':query,'evaluation_time':at,'started_at_kst':now(),'path':path}
    c=http.client.HTTPConnection('127.0.0.1',9090,timeout=8)
    try:
        c.request('GET',path,headers={'Connection':'close'})
        r=c.getresponse();raw=r.read(4*1024*1024+1)
        row.update(http_status=r.status,body_size=len(raw),body_sha256=hashlib.sha256(raw).hexdigest())
        assert r.status==200 and len(raw)<=4*1024*1024
        d=json.loads(raw);row['status']=d.get('status');row['resultType']=d.get('data',{}).get('resultType');row['results']=[]
        items=d.get('data',{}).get('result',[]);row['result_count']=len(items)
        assert d.get('status')=='success' and len(items)<=256
        for x in items:
            metric={k:v for k,v in x.get('metric',{}).items() if k in ('__name__','job','instance','pod','namespace','service','container','status','code','method')}
            row['results'].append({'metric':metric,**{k:x[k] for k in ('value','values') if k in x}})
        row['warnings']=d.get('warnings',[]);row['rc']=0
    except Exception as e:row.update(rc=1,error=type(e).__name__)
    finally:c.close()
    row['finished_at_kst']=now();rows.append(row)
    if row['rc']:break
print(json.dumps({'queries':rows}))
'''
out={'schema':'fds.w4-prometheus-loopback.v1','host':socket.gethostname(),'started_at_kst':now(),'pod_uid':uid,'container_id':cid,'pid':pid,'netns':netns,
     'boundary':'Existing Prometheus network namespace, host Python, historical GET to loopback9090 only; no pod writes, API mutations, app test requests or Harbor access.'}
p=subprocess.run(['nsenter','-t',str(pid),'-n','--','python3','-I','-c',code],capture_output=True,timeout=55)
out['rc']=p.returncode;out['child_stdout_sha256']=hashlib.sha256(p.stdout).hexdigest()
if p.returncode==0:out.update(json.loads(p.stdout))
else:out['stderr']=p.stderr.decode(errors='replace')[:2048]
out['post_pid']=inspect();out['post_netns']=os.readlink('/proc/'+str(pid)+'/ns/net')
assert out['post_pid']==pid and out['post_netns']==netns
out['finished_at_kst']=now();print(json.dumps(out))
