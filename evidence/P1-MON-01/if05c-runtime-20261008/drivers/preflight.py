import datetime,hashlib,json,os,socket,subprocess
assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='k8s-control01'
K=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','-n','monitoring-api']
def run(args):
 p=subprocess.run(K+args,capture_output=True,timeout=15);assert p.returncode==0,p.stderr.decode()
 return p.stdout
r={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':os.environ['COLLECTOR_SHA256'],'pods':[]}
for app in ('prometheus','alertmanager'):
 d=json.loads(run(['get','pods','-l','app='+app,'-o','json']))['items'];assert len(d)==1
 p=d[0];assert p['status']['phase']=='Running' and any(c['type']=='Ready' and c['status']=='True' for c in p['status']['conditions'])
 row={'app':app,'name':p['metadata']['name'],'uid':p['metadata']['uid'],'node':p['spec']['nodeName'],'ip':p['status']['podIP'],'containers':[{k:c.get(k) for k in ('name','imageID','restartCount','ready')} for c in p['status']['containerStatuses']]}
 if app=='prometheus':
  b=run(['exec',row['name'],'--','cat','/etc/prometheus/rules-p0/p0-test-alert.yml']);row['projected_rule_sha256']=hashlib.sha256(b).hexdigest();assert row['projected_rule_sha256']=='c97c60256c4caa64cd9699539eccbb5d60f18907b1c8190cea280e0d7e8fb22c'
 r['pods'].append(row)
r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps(r,indent=2))
