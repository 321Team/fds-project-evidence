from pathlib import Path
import subprocess,json,datetime,hashlib,sys
ROOT=Path(__file__).resolve().parent
label=sys.argv[1] if len(sys.argv)>1 else 'observer'
raw=(ROOT/('http_observe.py' if label=='worker-http' else 'observe.py')).read_bytes()
inner=['/usr/bin/ssh','-T','-i','/home/server01_ansible/.ssh/p1_ansible_ed25519','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/server01_ansible/.ssh/known_hosts','-o','IdentitiesOnly=yes','svc_ansible@10.1.93.102','sudo','-n','/usr/bin/python3','-B','-I','-']
if label=='worker-http':inner[inner.index('svc_ansible@10.1.93.102')]='svc_ansible@10.1.93.107'
bridge=('import subprocess,sys\np=subprocess.Popen('+repr(inner)+',stdin=subprocess.PIPE)\np.communicate(input='+repr(raw)+',timeout=620)\nsys.exit(p.returncode)\n').encode()
cmd=['C:/Windows/System32/OpenSSH/ssh.exe','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','fds-ansible01','/usr/bin/python3','-B','-I','-']
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (ROOT/(label+'.jsonl')).open('xb') as f,(ROOT/(label+'.stderr')).open('xb') as err:
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
 p.stdin.write(bridge);p.stdin.close()
 for line in p.stdout:
  f.write(line);f.flush()
  try:
   x=json.loads(line);target=[a for a in x.get('queries',{}).get('pods',{}).get('items',[]) if a['uid']=='e349b045-870f-4061-a677-3007efe479e9']
   if label=='worker-http':
    if x['tick']%5==0:print(json.dumps(x),flush=True)
   elif x['tick']%5==0 or x.get('error') or not x.get('other_workloads_healthy') or not x.get('nodes_healthy'):
    print(json.dumps({'tick':x['tick'],'utc':x['utc'],'error':x.get('error'),'other_ok':x.get('other_workloads_healthy'),'nodes_ok':x.get('nodes_healthy'),'target':[(c['ready'],c['restartCount'],c.get('containerID')) for a in target for c in (a['containers'] or [])],'http':x.get('http')}),flush=True)
  except Exception as e:print(type(e).__name__,flush=True)
 rc=p.wait(timeout=10)
(ROOT/(label+'.receipt.json')).write_text(json.dumps({'start_utc':start,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rc':rc,'source_sha256':hashlib.sha256(raw).hexdigest(),'stdout_sha256':hashlib.sha256((ROOT/(label+'.jsonl')).read_bytes()).hexdigest(),'review':'NOT PERFORMED (pure read-only observer)','command':cmd,'inner':inner},indent=2))
