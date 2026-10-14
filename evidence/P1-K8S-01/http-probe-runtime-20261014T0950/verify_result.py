"""Read existing originals only; reproduce the bounded HTTP Probe result."""
from pathlib import Path
import base64,datetime as dt,hashlib,json,sys
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
UID='e349b045-870f-4061-a677-3007efe479e9'
OLD='containerd://7b24cf1f8132da141a186eb00d7cbd02e30b9d1e28a2dfdb1147376caf544a45'
NEW='containerd://737b90c6597c5ed6ae4a74b2d68e066cb928efcca8f5ed564b1b11fa51dc8e31'
def read(p):return json.loads((R/p).read_bytes())
def stamp(x):return dt.datetime.fromisoformat(x.replace('Z','+00:00'))
def kst(x):return stamp(x).astimezone(dt.timezone(dt.timedelta(hours=9))).isoformat()
def rows(p):return [json.loads(line) for line in (R/p).read_bytes().splitlines()]
def req(ok,msg):
 if not ok:raise AssertionError(msg)
for name in ('app-state','cluster','edge','mon','process','event-baseline','target-http','stage-reviewed-source','apply-once','remote-originals-receipt','mon-stable','http-recovery','final-app-state','final-target-http','recovery-edge'):
 req(read(name+'/receipt.json')['rc']==0,name+' receipt')
receipt=read('remote-originals-receipt/stdout.json');remote={Path(f['path']).name:f for f in receipt['files']}
for name,f in remote.items():
 raw=base64.b64decode(f['base64']);req(hashlib.sha256(raw).hexdigest()==f['sha256'],name+' hash');req(f['uid']==0 and f['mode']=='0o600',name+' permissions')
req(remote['engine_stop.py']['sha256']=='8b9fe37dd0bcdbd09e0c7d5e7fb41eaa9e25d47fb56223bbab6273081251cc32','reviewed source')
events=[json.loads(x) for x in base64.b64decode(remote['events.jsonl']['base64']).splitlines()]
names=[e['event'] for e in events]
req(names==['STOP_INTENT','STOP_SENT','ORIGINAL_EXIT_OBSERVED_NOT_PROBE_PASS','ORIGINAL_EXITED_NO_CONT','FINAL_ORIGINAL_EXIT'],'one STOP/original exited/no CONT')
start=events[1]['utc'];end=events[2]['utc'];req(0<(stamp(end)-stamp(start)).total_seconds()<150,'hold bound')
obs=rows('observer.jsonl');http=rows('worker-http.jsonl')
before={x['kind']:x['items'] for x in read('app-state/stdout.json')['queries']};after={x['kind']:x['items'] for x in read('final-app-state/stdout.json')['queries']}
prev={p['metadata']['uid']:p for p in before['pods']};final={p['metadata']['uid']:p for p in after['pods']}
req(prev.keys()==final.keys() and len(final)==6,'all six Pod identities unchanged')
for uid,p in final.items():
 req(p['node']==prev[uid]['node'] and not p['metadata']['deletionTimestamp'],'placement/deletion')
 for c,old in zip(p['statuses'],prev[uid]['statuses']):
  req(c['ready'] and c['imageID']==old['imageID'],'Ready/image')
  req(c['restartCount']==old['restartCount']+(1 if uid==UID else 0),'expected restart only')
  req(c['containerID']==(NEW if uid==UID else old['containerID']),'container transition')
for d in after['deployments']:
 old=next(x for x in before['deployments'] if x['metadata']['uid']==d['metadata']['uid'])
 req(d['spec_sha256']==old['spec_sha256'] and d['metadata']['generation']==old['metadata']['generation'] and d['status']['readyReplicas']==3,'deployment unchanged/ready')
false_ready=[];false_endpoint=[];recovered=[];kill=[];live=[]
for row in obs:
 req('error' not in row and row['other_workloads_healthy'] and row['nodes_healthy'],'observer/other workloads/node health')
 ps=row['queries']['pods']['items'];req({p['uid'] for p in ps}==prev.keys(),'observed Pod identity')
 for p in ps:
  if p['uid']==UID:continue
  req(all(c['containerID']==o['containerID'] and c['imageID']==o['imageID'] and c['ready'] and c['restartCount']==0 for c,o in zip(p['containers'],prev[p['uid']]['statuses'])),'non-target unchanged')
 target=next(p for p in ps if p['uid']==UID);c=target['containers'][0]
 ep=[e for s in row['queries']['endpoints']['items'] if s['labels'].get('kubernetes.io/service-name')=='fds-engine' for e in s['endpoints'] if e.get('targetRef',{}).get('uid')==UID]
 req(len(ep)==1,'same target endpoint')
 if not c['ready']:false_ready.append(row['utc'])
 if not ep[0]['conditions']['ready']:false_endpoint.append(row['utc'])
 if c['containerID']==NEW and c['restartCount']==1 and c['ready'] and ep[0]['conditions']['ready']:recovered.append(row['utc'])
 for e in row['queries']['events']['items']:
  req(e['involvedObject']['uid']==UID,'event target')
  if e['reason']=='Killing' and 'failed liveness probe' in e['message']:kill.append(e)
  if e['reason']=='Unhealthy' and e['message'].startswith('Liveness probe failed:'):live.append(e)
req(false_ready and false_endpoint and recovered and kill and live,'all probe transitions')
req(stamp(start)<stamp(kill[-1]['lastTimestamp'])<stamp(end),'kubelet kill time bound')
req(stamp(recovered[-1])-stamp(recovered[0])>=dt.timedelta(seconds=60),'Ready endpoint recovered 60s')
http_failed=[x for x in http if all(q['code']==0 for q in x['http'].values()) and isinstance(x['original_pid'],dict) and x['original_pid']['state']=='T' and x['original_pid']['start_ticks']=='19229699']
req(http_failed,'actual HTTP timeout while exact original stopped')
req(read('worker-http.receipt.json')['rc']==1 and 'ProcessLookupError' in (R/'worker-http.stderr').read_text(),'preserved proc-race failure')
recovery=read('http-recovery/stdout.json');req(recovery['stable60_pass'] and recovery['signals']==0 and recovery['rows'][-1]['elapsed']>=60,'supplemental HTTP recovery')
mon=read('mon-stable/stdout.json');req(mon['stable60_pass'] and mon['forwarder_stopped'] and mon['rows'][-1]['stable_seconds']>=60,'MON 60 seconds')
down=json.loads(read('mon-during/stdout.json')['queries'][0]['raw'])['data']['result']
req([(x['metric']['job'],x['metric']['instance']) for x in down if x['value'][1]!='1']==[('fds-engine','10.244.69.193:9090')],'intended MON-only impact')
for row in read('recovery-edge/stdout.json')['http']:req(row['status']==(404 if row['url'].endswith('/metrics') else 200),'edge recovery')
for row in read('final-target-http/stdout.json')['rows']:req(row['status']==row['expected'],'target listeners')
counts={}
for p in final.values():
 app=p['statuses'][0]['name'];counts.setdefault(app,{});counts[app][p['node']]=counts[app].get(p['node'],0)+1
req(all(v=={'k8s-worker01':1,'k8s-worker02':1,'k8s-worker03':1} for v in counts.values()),'1/1/1 each')
result={'status':'HTTP_PROBE_RUNTIME_PASS_WITH_RECORDED_OBSERVATION_LIMITS','source_head':'d53ce00f318785b97577d41c07d8309ff581c2a8','start_kst':kst(start),'original_exit_kst':kst(end),'hold_seconds':(stamp(end)-stamp(start)).total_seconds(),'stop_count':1,'cont_count':0,'kubelet_killing_kst':kst(kill[-1]['lastTimestamp']),'first_ready_false_observed_kst':kst(false_ready[0]),'first_endpoint_false_observed_kst':kst(false_endpoint[0]),'first_ready_endpoint_recovered_observed_kst':kst(recovered[0]),'new_container_id':NEW,'target_restart':1,'same_pod_uid':UID,'other_restarts':0,'images_specs_unchanged':True,'placement':counts,'http_recovery_60s':True,'mon_recovery_60s':True,'observations':len(obs),'observer_errors':0,'limits':['Control01 direct Pod HTTP failed before injection; use worker02 HTTP and CP1 API observations.','Worker HTTP/process observer ended on original PID exit (ProcessLookupError); first exact HTTP recovery instant is not captured. Separate 60-second HTTP recovery collected.','Kubelet journal returned no entries; UID-bound Kubernetes kubelet liveness/Killing events prove cause.','Pure observers/recovery supplements were not independently code-reviewed; no additional injection.'],'independent_evidence_review':'PENDING','final_APP_regression':'NOT_RUN','DB_acceptance':'PENDING_FINAL_APP_REGRESSION','W4':'NOT_MEASURED'}
print(json.dumps(result,ensure_ascii=False,indent=2))
