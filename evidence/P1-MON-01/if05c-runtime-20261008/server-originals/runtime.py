import datetime,fcntl,hashlib,json,os,pathlib,re,select,signal,socket,subprocess,sys,time,urllib.parse,urllib.request
from guard import patch_for
K=['kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=10s','-n','monitoring-api']
NAME='FDSMonitoringPipelineTest';CM='prometheus-p0-test-alert';KEY='p0-test-alert.yml'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
class Session:
 def __init__(self,root,mode):
  self.root=pathlib.Path(root).resolve();assert self.root.parent==pathlib.Path('/root') and self.root.name.startswith('if05c-')
  assert os.geteuid()==0 and socket.gethostname().split('.')[0]=='k8s-control01'
  self.mode=mode;self.pfs={};self.input=json.loads((self.root/'input.json').read_text());self.events=open(self.root/(mode+'-events.jsonl'),'a',buffering=1)
  self.log('start',{'host':socket.gethostname(),'source_sha256':sha(pathlib.Path(__file__).read_bytes())})
 def log(self,kind,data):
  self.events.write(json.dumps({'utc':now(),'kind':kind,'data':data},ensure_ascii=False)+'\n');self.events.flush();os.fsync(self.events.fileno())
 def save(self,name,data):
  p=self.root/(name+'.tmp');p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');os.replace(p,self.root/name)
 def cmd(self,args,input=None):
  p=subprocess.run(args,input=input,capture_output=True,timeout=16)
  self.log('command',{'argv':args,'rc':p.returncode,'stdout_sha256':sha(p.stdout),'stderr':p.stderr.decode(errors='replace')})
  assert p.returncode==0,'COMMAND_FAILED';return p.stdout
 def cm(self):
  d=json.loads(self.cmd(K+['get','configmap',CM,'-o','json']))
  return {'metadata':{k:d['metadata'][k] for k in ('name','namespace','uid','resourceVersion')},'data':d['data']}
 def pods(self):
  for p in self.input['pods']:
   d=json.loads(self.cmd(K+['get','pod',p['name'],'-o','json']))
   assert d['metadata']['uid']==p['uid'] and d['status']['podIP']==p['ip'],'POD_CHANGED'
   assert any(c['type']=='Ready' and c['status']=='True' for c in d['status']['conditions']),'POD_NOT_READY'
   actual=[{k:c.get(k) for k in ('name','imageID','restartCount','ready')} for c in d['status']['containerStatuses']]
   assert actual==p['containers'],'CONTAINER_CHANGED'
 def pf(self,app):
  if app in self.pfs:return self.pfs[app][1]
  pod=next(x for x in self.input['pods'] if x['app']==app);port=9090 if app=='prometheus' else 9093
  cmd=K+['port-forward','--address=127.0.0.1','pod/'+pod['name'],'0:'+str(port)]
  p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  self.pfs[app]=(p,None)
  ready,_,_=select.select([p.stdout],[],[],15);assert ready,'PF_TIMEOUT';line=p.stdout.readline()
  m=re.search(r'Forwarding from 127\.0\.0\.1:(\d+)',line);assert m,line
  base='http://127.0.0.1:'+m.group(1);self.pfs[app]=(p,base);self.log('port_forward',{'command':cmd,'pid':p.pid,'ready':line});return base
 def http(self,app,route,post=False):
  request=urllib.request.Request(self.pf(app)+route,data=b'' if post else None,method='POST' if post else 'GET')
  with urllib.request.urlopen(request,timeout=10) as response:raw=response.read();status=response.status
  self.log('http',{'app':app,'route':route,'method':request.method,'status':status,'raw_sha256':sha(raw)})
  return raw
 def api(self,route):
  d=json.loads(self.http('prometheus',route));assert d['status']=='success';return d['data']
 def query(self,q):return self.api('/api/v1/query?'+urllib.parse.urlencode({'query':q}))['result']
 def metrics(self):
  text=self.http('alertmanager','/metrics').decode()
  return [l for l in text.splitlines() if l.startswith(('alertmanager_notifications_total{','alertmanager_notifications_failed_total{'))]
 def snap(self,tag):
  groups=self.api('/api/v1/rules?type=alert')['groups'];rules=[r for g in groups for r in g['rules']]
  target=[r for r in rules if r.get('name')==NAME];assert len(target)==1
  others=[{k:r.get(k) for k in ('name','query','duration','labels','annotations')} for r in rules if r.get('name')!=NAME]
  alerts=json.loads(self.http('alertmanager','/api/v2/alerts'))
  d={'tag':tag,'utc':now(),'rule':target[0],'other_rules_sha256':sha(json.dumps(others,sort_keys=True).encode()),'prom_alerts':self.query('ALERTS{alertname="'+NAME+'"}'),'am_alerts':[a for a in alerts if a.get('labels',{}).get('alertname')==NAME],'other_am_alert_count':sum(a.get('labels',{}).get('alertname')!=NAME for a in alerts),'notification_metrics':self.metrics()}
  self.log('snapshot',d);return d
 def projected(self):
  pod=next(x for x in self.input['pods'] if x['app']=='prometheus')
  raw=self.cmd(K+['exec',pod['name'],'--','cat','/etc/prometheus/rules-p0/'+KEY]);return sha(raw)
 def wait_projection(self,expected,seconds=170):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   self.pods();actual=self.projected();self.log('projection',{'expected':expected,'actual':actual})
   if actual==expected:return
   time.sleep(5)
  raise RuntimeError('PROJECTION_TIMEOUT')
 def patch(self,ops,dry=False):
  if not ops:return
  args=K+['patch','configmap',CM,'--type=json','-p',json.dumps(ops),'-o','json']
  if dry:args.append('--dry-run=server')
  d=json.loads(self.cmd(args));self.log('patch_result',{'dry_run':dry,'metadata':{k:d['metadata'][k] for k in ('uid','resourceVersion')},'data_sha256':sha(d['data'][KEY].encode())})
 def health(self):
  self.pods();up=self.query('count(up)');down=self.query('count(up == 0)')
  self.log('health',{'up':up,'down':down});assert len(up)==1 and up[0]['value'][1]=='23' and down==[],'TARGET_HEALTH'
 def close(self):
  for app,(p,base) in self.pfs.items():
   p.terminate()
   try:tail=p.communicate(timeout=5)[0]
   except subprocess.TimeoutExpired:p.kill();tail=p.communicate(timeout=3)[0]
   self.log('pf_closed',{'app':app,'pid':p.pid,'rc':p.returncode,'reaped':p.poll() is not None})
  self.events.close()
 def restore(self):
  with open(self.root/'recovery.lock','a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   original=json.loads((self.root/'original.json').read_text());candidate=json.loads((self.root/'candidate.json').read_text())
   current=self.cm();ops=patch_for(original,current,candidate,True)
   self.patch(ops);self.wait_projection(sha(original['data'][KEY].encode()))
   self.http('prometheus','/-/reload',True)
   deadline=time.monotonic()+45
   while time.monotonic()<deadline:
    s=self.snap('restore-check')
    if s['rule']['query']=='vector(1) == 0' and s['rule']['state']=='inactive' and s['rule']['health']=='ok':
     assert self.cm()['data']==original['data'];self.health();self.save('restore-confirmed.json',{'utc':now(),'mode':self.mode,'snapshot':s,'original_sha256':sha(original['data'][KEY].encode())});return s
    time.sleep(5)
   raise RuntimeError('RESTORE_NOT_CONFIRMED')
def notified(snapshot):
 return sum(float(l.rsplit(' ',1)[1]) for l in snapshot['notification_metrics'] if l.startswith('alertmanager_notifications_total{') and 'integration="discord"' in l)
def main(mode,root):
 os.umask(0o077);s=Session(root,mode);rc=0
 if mode=='recover':
  try:s.restore()
  except Exception as e:s.log('recovery_error',{'type':type(e).__name__,'error':str(e)});rc=2
  finally:s.save('watchdog-result.json',{'rc':rc,'utc':now()});s.close()
  return rc
 lock=open('/run/lock/fds-if05c-test.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 mutated=False;armed=False;baseline=None;status={'started_utc':now(),'apply':'NOT_RUN','restore':'NOT_NEEDED','external_channel_read':'NOT_VERIFIED'}
 unit='if05c-recover-'+s.root.name.replace('if05c-','')
 def stop(signum,frame):raise RuntimeError('SIGNAL_'+str(signum))
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  s.health();original=s.cm();assert original['metadata']['uid']==s.input['cm_uid'];assert sha(original['data'][KEY].encode())==s.input['original_sha256'];assert set(original['data'])=={KEY}
  assert s.projected()==s.input['original_sha256'];baseline=s.snap('before');assert baseline['rule']['query']=='vector(1) == 0' and baseline['rule']['state']=='inactive' and baseline['rule']['health']=='ok';assert not baseline['am_alerts'],'EXISTING_TEST_ALERT'
  flags=s.api('/api/v1/status/flags');assert flags.get('web.enable-lifecycle')=='true'
  import yaml
  am=json.loads(s.http('alertmanager','/api/v2/status'));cfg=yaml.safe_load(am['config']['original'])
  assert cfg['route']==s.input['am_route'],'ROUTE_CHANGED'
  receiver=next(x for x in cfg['receivers'] if x['name']=='discord-notifications');assert len(receiver['discord_configs'])==1 and receiver['discord_configs'][0]['send_resolved'] is True
  candidate={KEY:original['data'][KEY].replace('expr: vector(1) == 0','expr: vector(1) == 1')};assert candidate!=original['data']
  s.save('original.json',original);s.save('candidate.json',candidate)
  s.patch(patch_for(original,original,candidate),dry=True)
  if mode=='check':status['preflight']='READY';return 0
  s.cmd(['systemd-run','--unit='+unit,'--on-active=360s','--timer-property=AccuracySec=1s','--property=Type=oneshot','--property=TimeoutStartSec=240s',sys.executable,str(pathlib.Path(__file__).resolve()),'recover',str(s.root)])
  armed=True;s.cmd(['systemctl','is-active',unit+'.timer']);s.log('recovery_timer_armed',{'unit':unit,'after_seconds':360})
  mutated=True;s.patch(patch_for(original,s.cm(),candidate));status['apply']='APPLIED'
  s.wait_projection(sha(candidate[KEY].encode()));s.http('prometheus','/-/reload',True)
  deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   snap=s.snap('firing-observe')
   if snap['rule']['state']=='firing' and snap['am_alerts'] and notified(snap)>notified(baseline):
    status['firing_observed']=True;s.save('firing.json',snap);break
   time.sleep(5)
  else:raise RuntimeError('FIRING_OR_SENDER_NOTIFICATION_TIMEOUT')
 except Exception as e:status['error']={'type':type(e).__name__,'detail':str(e)};s.log('error',status['error']);rc=2
 finally:
  signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
  if mutated:
   try:
    snap=s.restore();status['restore']='CONFIRMED'
    if armed:s.cmd(['systemctl','stop',unit+'.timer',unit+'.service']);armed=False
    deadline=time.monotonic()+60
    firing=json.loads((s.root/'firing.json').read_text()) if (s.root/'firing.json').exists() else None
    while time.monotonic()<deadline:
     snap=s.snap('resolved-observe')
     if firing and not snap['am_alerts'] and notified(snap)>notified(firing):status['resolved_observed']=True;s.save('resolved.json',snap);break
     time.sleep(5)
    status['other_rules_unchanged']=baseline is not None and snap['other_rules_sha256']==baseline['other_rules_sha256'];assert status['other_rules_unchanged']
    if not status.get('resolved_observed'):status['resolved_observed']=False;rc=2
   except Exception as e:status['restore_error']={'type':type(e).__name__,'detail':str(e)};s.log('restore_error',status['restore_error']);rc=3
  elif armed:
   s.cmd(['systemctl','stop',unit+'.timer']);armed=False
  status.update(rc=rc,recovery_timer_left_armed=armed,finished_utc=now());s.save('status.json',status);s.close();lock.close()
 return rc
if __name__=='__main__':raise SystemExit(main(sys.argv[1],sys.argv[2]))
