import datetime, hashlib, json, os, socket, subprocess, sys
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert socket.gethostname().split('.')[0]=='k8s-control01' and os.geteuid()==0
r={'started_utc':now(),'hostname':socket.gethostname(),'uid':os.geteuid(),'source_sha256':os.environ['COLLECTOR_SHA256'],'queries':[]}
try:
    import yaml
except ImportError:
    print(json.dumps({'error':'PyYAML unavailable; no config content exported'})); sys.exit(2)

# Only retain explicitly named non-credential configuration fields. Receiver URLs,
# authentication dictionaries and arbitrary labels/annotations are not exported.
def safeconfig(d):
    if isinstance(d,dict):
        allow={'global','scrape_interval','evaluation_interval','scrape_timeout','rule_files','scrape_configs',
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

for name in ('prometheus-config','prometheus-alert-rules','prometheus-alert-rules-optional','prometheus-p0-test-alert','alertmanager-config','__pods__'):
    cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s','-n','monitoring-api','get']+(['pods'] if name=='__pods__' else ['configmap',name])+['-o','json']
    q={'command':cmd,'started_utc':now()}
    try:
        p=subprocess.run(cmd,capture_output=True,timeout=18)
        q.update(rc=p.returncode,stderr=p.stderr.decode(),raw_stdout_sha256=hashlib.sha256(p.stdout).hexdigest())
        if p.returncode==0:
            d=json.loads(p.stdout)
            if name=='__pods__':
                q['items']=[{'name':x['metadata']['name'],'uid':x['metadata']['uid'],
                             'volumes':[{k:v for k,v in vol.items() if k in ('name','configMap')} for vol in x['spec'].get('volumes',[])],
                             'containers':[{'name':c['name'],'config_args':[a for a in c.get('args',[]) if a.startswith(('--config.file=','--web.config.file='))],
                                            'volumeMounts':c.get('volumeMounts',[])} for c in x['spec']['containers']]} for x in d['items']]
            else:
                q['name']=name
                q['resourceVersion']=d['metadata']['resourceVersion']
                q['data']={k:{'sha256':hashlib.sha256(v.encode()).hexdigest(),'projection':safeconfig(yaml.safe_load(v))} for k,v in d.get('data',{}).items()}
    except Exception as e: q.update(rc=12,error=str(e))
    q['finished_utc']=now(); r['queries'].append(q)
r['finished_utc']=now()
print(json.dumps(r,ensure_ascii=False,indent=2))
sys.exit(0 if all(q['rc']==0 for q in r['queries']) else 2)
