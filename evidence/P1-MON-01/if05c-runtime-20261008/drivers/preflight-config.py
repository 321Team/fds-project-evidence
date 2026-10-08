import datetime,hashlib,json,os,re,select,socket,subprocess,urllib.request,yaml
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='k8s-control01'
r={'host':socket.gethostname(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':os.environ['COLLECTOR_SHA256']}
cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s','-n','monitoring-api','get','configmap','prometheus-p0-test-alert','-o','json']
p=subprocess.run(cmd,capture_output=True,timeout=18);assert p.returncode==0,p.stderr.decode()
d=json.loads(p.stdout);text=d['data']['p0-test-alert.yml'];sha=hashlib.sha256(text.encode()).hexdigest()
assert sha=='c97c60256c4caa64cd9699539eccbb5d60f18907b1c8190cea280e0d7e8fb22c','RULE_CHANGED_STOP'
r['configmap']={'command':cmd,'rc':p.returncode,'raw_stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'metadata':{k:d['metadata'][k] for k in ('name','namespace','uid','resourceVersion')},'rule_text':text,'rule_sha256':sha}
cmd=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=12s','-n','monitoring-api','port-forward','--address=127.0.0.1','service/alertmanager','0:9093']
r['forward_command']=cmd;p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
try:
 ready,_,_=select.select([p.stdout],[],[],15);assert ready
 line=p.stdout.readline();m=re.search(r'Forwarding from 127\.0\.0\.1:(\d+)',line);assert m,line
 with urllib.request.urlopen('http://127.0.0.1:'+m.group(1)+'/api/v2/status',timeout=12) as resp:raw=resp.read()
 status=json.loads(raw);cfg=yaml.safe_load(status['config']['original'])
 r['alertmanager']={'route':'/api/v2/status','raw_response_sha256':hashlib.sha256(raw).hexdigest(),'version':status.get('versionInfo'),'uptime':status.get('uptime'),'route_config':cfg.get('route'),'receivers':[{'name':x.get('name'),'discord_configs':[{'send_resolved':z.get('send_resolved')} for z in x.get('discord_configs',[])]} for x in cfg.get('receivers',[])]}
except Exception as e:r['error']=str(e)
finally:
 p.terminate()
 try:tail=p.communicate(timeout=8)[0]
 except subprocess.TimeoutExpired:p.kill();tail=p.communicate(timeout=3)[0]
 r.update(forward_reaped=p.poll() is not None,forward_exit=p.returncode,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
print(json.dumps(r,indent=2));raise SystemExit(2 if 'error' in r else 0)
