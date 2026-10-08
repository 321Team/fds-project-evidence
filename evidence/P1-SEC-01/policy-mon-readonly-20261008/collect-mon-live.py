def safeconfig(d):
    if isinstance(d,dict):
        allow={'global','scrape_interval','evaluation_interval','scrape_timeout','rule_files','scrape_configs','dns_sd_configs','type','port','refresh_interval',
               'job_name','scheme','metrics_path','static_configs','targets','kubernetes_sd_configs','role',
               'namespaces','names','relabel_configs','metric_relabel_configs','source_labels','target_label',
               'regex','replacement','action','separator','modulus','alerting','alertmanagers','api_version',
               'path_prefix','timeout','groups','name','rules','alert','record','expr','for','keep_firing_for',
               'route','receiver','group_by','group_wait','group_interval','repeat_interval','routes',
               'match','match_re','matchers','continue','receivers','send_resolved','webhook_configs',
               'discord_configs','http_config','proxy_url','url_file','webhook_url_file','remote_write',
               'write_relabel_configs','queue_config','capacity','max_shards','min_shards',
               'bearer_token_file','ca_file','cert_file','key_file','tls_config','insecure_skip_verify'}
        return {k:safeconfig(v) for k,v in d.items() if k in allow}
    if isinstance(d,list): return [safeconfig(v) for v in d]
    if isinstance(d,str) and ('hooks/' in d or 'webhooks/' in d or '://' in d and '@' in d): return '[OMITTED_CREDENTIAL_URL]'
    return d
import datetime,hashlib,json,os,select,socket,subprocess,sys,time,urllib.request,urllib.parse,yaml
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
result={'hostname':socket.gethostname(),'uid':os.geteuid(),'started_utc':now(),'source_sha256':os.environ['COLLECTOR_SHA256'],'queries':[]}
cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s','-n','monitoring-api','port-forward','--address=127.0.0.1','service/prometheus','0:9090']
result['forward_command']=cmd
p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
result['forward_pid']=p.pid
try:
    ready,_,_=select.select([p.stdout],[],[],15)
    if not ready: raise RuntimeError('forward not ready in 15 seconds')
    line=p.stdout.readline(); result['forward_first_line']=line
    import re
    match=re.search(r'Forwarding from 127\.0\.0\.1:(\d+)',line)
    if not match: raise RuntimeError('forward ready line missing')
    base='http://127.0.0.1:'+match.group(1)
    for route in ['/api/v1/status/config','/api/v1/rules?type=alert','/api/v1/query?query='+urllib.parse.quote('count by (job) (up)'),'/api/v1/query?query='+urllib.parse.quote('count(up == 0)')]:
        q={'route':route,'started_utc':now()}
        try:
            with urllib.request.urlopen(base+route,timeout=10) as response: body=response.read()
            d=json.loads(body)
            q.update(rc=0,api_status=d.get('status'),raw_response_sha256=hashlib.sha256(body).hexdigest())
            if 'status/config' in route:
                value=d['data']['yaml']; q['config_sha256']=hashlib.sha256(value.encode()).hexdigest()
                q['config_projection']=safeconfig(yaml.safe_load(value))
            elif '/rules' in route:
                q['groups']=[{'name':g.get('name'),'file':g.get('file'),'rules':[{k:r[k] for k in ('name','query','duration','state','health','lastError','lastEvaluation') if k in r} for r in g.get('rules',[])]} for g in d['data'].get('groups',[])]
            else: q['data']=d.get('data')
        except Exception as e: q.update(rc=2,error=str(e))
        q['finished_utc']=now(); result['queries'].append(q)
except Exception as e: result['error']=str(e)
finally:
    p.terminate()
    try: remainder=p.communicate(timeout=8)[0]
    except subprocess.TimeoutExpired:
        p.kill(); remainder=p.communicate(timeout=3)[0]
    result['forward_tail']=remainder
    result['forward_exit']=p.returncode
    result['forward_reaped']=p.poll() is not None
result['finished_utc']=now()
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if 'error' not in result and all(q['rc']==0 and q.get('api_status')=='success' for q in result['queries']) else 2)
