QUERIES = {'Q1': 'sum by (pod) (rate(container_cpu_usage_seconds_total{job="kubelet-cadvisor",namespace="fds-app",container=~"transaction-api|fds-engine"}[1m]))', 'Q2': 'sum by (pod) (container_memory_working_set_bytes{job="kubelet-cadvisor",namespace="fds-app",container=~"transaction-api|fds-engine"})', 'Q3': 'sum by (pod) (rate(container_cpu_cfs_throttled_periods_total{job="kubelet-cadvisor",namespace="fds-app",container=~"transaction-api|fds-engine"}[1m])) / sum by (pod) (rate(container_cpu_cfs_periods_total{job="kubelet-cadvisor",namespace="fds-app",container=~"transaction-api|fds-engine"}[1m]))', 'up': 'up', 'save_success': 'sum(transaction_save_success_total)', 'save_failure': 'sum(transaction_save_failure_total)', 'evaluated': 'sum(fds_evaluated_total)', 'Q3_DENOM': 'sum by (pod) (rate(container_cpu_cfs_periods_total{job="kubelet-cadvisor",namespace="fds-app",container=~"transaction-api|fds-engine"}[1m]))'}
import datetime,hashlib,json,os,socket,subprocess,urllib.parse
assert socket.gethostname()=='k8s-control01' and os.geteuid()==0
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
kc=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s']
out={'host':socket.gethostname(),'started_at_utc':now(),'scope':'READ_ONLY_API_PROXY_PREFLIGHT_NO_PF_NO_LOAD','queries':[],'mutation':False}
p=subprocess.run(kc+['get','pods','-n','fds-app','-o','json'],capture_output=True,timeout=15)
assert p.returncode==0 and len(p.stdout)<2*1024*1024
out['pods']=[{'name':x['metadata']['name'],'uid':x['metadata']['uid'],'ip':x['status'].get('podIP'),'node':x['spec'].get('nodeName'),'deleting':x['metadata'].get('deletionTimestamp'),'containers':[{'name':v['name'],'imageID':v.get('imageID'),'restartCount':v.get('restartCount'),'ready':v.get('ready')} for v in x['status'].get('containerStatuses',[])]} for x in json.loads(p.stdout)['items']]
for name,query in QUERIES.items():
    path='/api/v1/namespaces/monitoring-api/services/prometheus:9090/proxy/api/v1/query?'+urllib.parse.urlencode({'query':query})
    argv=kc+['get','--raw='+path]
    p=subprocess.run(argv,capture_output=True,timeout=15)
    assert len(p.stdout)<2*1024*1024 and len(p.stderr)<65536
    out['queries'].append({'name':name,'query':query,'utc':now(),'argv':argv,'rc':p.returncode,'raw':p.stdout.decode(),'stderr':p.stderr.decode(),'sha256':hashlib.sha256(p.stdout).hexdigest()})
out['finished_at_utc']=now()
print(json.dumps(out,sort_keys=True))
raise SystemExit(0 if all(x['rc']==0 for x in out['queries']) else 2)
