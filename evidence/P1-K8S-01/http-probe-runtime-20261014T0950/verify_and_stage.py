from pathlib import Path
import json,hashlib,datetime,importlib.util,subprocess
R=Path(__file__).resolve().parent;W=R.parent.parent
def read(n):return json.loads((R/n/'stdout.json').read_bytes())
for n in ('app-state','cluster','edge','mon','process','event-baseline','target-http'):
 assert json.loads((R/n/'receipt.json').read_bytes())['rc']==0,n
a=read('app-state');aq={x['kind']:x['items'] for x in a['queries']}
old=json.loads((W/'deliverables/phase1-probe-app-20261014-0740/app-state/stdout.json').read_bytes());oq={x['kind']:x['items'] for x in old['queries']}
for k in ('deployments','pods'):
 curr={x['metadata']['uid']:x for x in aq[k]};prev={x['metadata']['uid']:x for x in oq[k]};assert curr.keys()==prev.keys()
 for uid,x in curr.items():
  if k=='deployments':assert x['spec_sha256']==prev[uid]['spec_sha256'] and x['status']['readyReplicas']==3
  else:assert x['node']==prev[uid]['node'] and not x['metadata']['deletionTimestamp'] and x['statuses']==prev[uid]['statuses'] and all(c['ready'] and c['restartCount']==0 for c in x['statuses'])
c=read('cluster');cq={x['name']:x['items'] for x in c['queries']}
assert cq['cluster'][0]['metadata']['uid']=='e1669cff-1435-423f-a6c4-28bc44f488de'
assert not cq['pdb'] and not cq['hpa']
for n in cq['nodes']:
 assert not n['spec']['unschedulable']
 for q in n['status']['conditions']:
  if q['type'] in ('Ready','DiskPressure','MemoryPressure','PIDPressure','NetworkUnavailable'):assert q['status']==('True' if q['type']=='Ready' else 'False')
for x in read('edge')['http']:assert x['status']==(404 if x['url'].endswith('/metrics') else 200)
m={x['name']:json.loads(x['raw']) for x in read('mon')['queries']};assert all(x['status']=='success' for x in m.values())
up=m['all_up']['data']['result'];assert len(up)==23 and all(x['value'][1]=='1' for x in up)
assert sum(x['metric']['job'] in ('fds-engine','transaction-api') for x in up)==6
for x in read('target-http')['rows']:assert x['status']==x['expected']
b=json.loads((W/'phase1-work-20261014-probe/ops/p1-http-probe/observed-binding.json').read_bytes());p=read('process')
for key in ('host','boot_id','container_id','pid','start_ticks','cgroup','pid_namespace'):assert p[key]==b[key],key
assert p['container_status']['imageRef']==b['image_ref'] and p['process']['State'].startswith('S') and p['pidfd_open_ok'] and not p['pidfd_exited']
obs=json.loads((R/'observer.jsonl').read_bytes().splitlines()[-1]);assert obs['other_workloads_healthy'] and obs['nodes_healthy']
http=json.loads((R/'worker-http.jsonl').read_bytes().splitlines()[-1]);assert all(x['code']==200 for x in http['http'].values())
assert datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(http['utc'])<datetime.timedelta(seconds=10)
assert datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(obs['utc'])<datetime.timedelta(seconds=10)
record={'at_kst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'user_instruction':'221, 86 차단사항 없으면 병합 후 착수','field_confirmation':'11:15까지 세 조건 모두 확보','source_head':'d53ce00f318785b97577d41c07d8309ff581c2a8','merge':'e60e022333a51a9a1690649ef170c0bda92ad9b9','evidence_merge':'851c3827f69160a6299c859f2cca3a32dab41054','reviewer':'supreme33-kr','preflight':'PASS','runtime':'NOT_YET_STARTED','window':{'start':'2026-10-14T09:45:00+09:00','latest':'2026-10-14T09:55:00+09:00','end':'2026-10-14T10:20:00+09:00'},'APP':'10:25-10:35 start;11:15 end; fresh DB zero pending'}
(R/'ENTRY_VALIDATED.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
repo=W/'phase1-work-20261014-probe';files={}
for name in ('engine_stop.py','observed-binding.json'):
 raw=subprocess.check_output(['git','-C',str(repo),'show','d53ce00f318785b97577d41c07d8309ff581c2a8:ops/p1-http-probe/'+name])
 local=(repo/'ops/p1-http-probe'/name).read_bytes()
 if name=='engine_stop.py':assert raw==local
 else:assert json.loads(raw)==json.loads(local) # Stage exact Git blob, not CRLF checkout.
 files[name]=raw
assert hashlib.sha256(files['engine_stop.py']).hexdigest()=='8b9fe37dd0bcdbd09e0c7d5e7fb41eaa9e25d47fb56223bbab6273081251cc32'
# Only deliver the two reviewed blobs to the private, new supply directory.
source='import os,socket,pathlib,hashlib,json\nassert socket.gethostname()=="k8s-worker02" and os.geteuid()==0\nos.umask(0o077)\np=pathlib.Path("/var/tmp/p1-http-probe-source-20261014-0945")\np.mkdir(mode=0o700,exist_ok=False)\nfiles='+repr(files)+'\nrows=[]\nfor name,raw in files.items():\n f=p/name\n with f.open("xb") as h: h.write(raw);h.flush();os.fsync(h.fileno())\n assert f.read_bytes()==raw\n rows.append({"path":str(f),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"mode":oct(f.stat().st_mode&0o777),"uid":f.stat().st_uid})\nprint(json.dumps({"files":rows,"directory_mode":oct(p.stat().st_mode&0o777)}))\n'
spec=importlib.util.spec_from_file_location('t',W/'deliverables/p1-redistribution-20261013/read_transport.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=R
r=t.run('stage-reviewed-source','10.1.93.107',source);assert r['rc']==0
