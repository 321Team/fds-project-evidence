import base64,datetime,hashlib,json,pathlib,re,subprocess
OUT=pathlib.Path(__file__).parent
def load(p):return json.loads((OUT/p).read_bytes())
def save(p,data):(OUT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=load('current-cluster/stdout.json');q={x['name']:x['items'] for x in c['queries']}
edge=load('current-edge/stdout.json');mon=load('current-mon/stdout.json')
final=json.loads((OUT.parent/'phase1-deploy-after-push-20261013-2244/execution/final/VERIFIED_RESULT.json').read_bytes())
assert c['status']=='COLLECTED_REVIEW_REQUIRED' and all(x['rc']==0 for x in c['queries'])
assert len(q['pods'])==6 and not q['pdb'] and not q['hpa']
for d in q['deployments']:
 name=d['metadata']['name'];f=final['post_targets'][name]
 assert d['metadata']['uid']==f['uid'] and d['metadata']['generation']==f['generation']
 assert all(d['status'][k]==3 for k in ('replicas','readyReplicas','updatedReplicas','availableReplicas'))
 pods=[p for p in q['pods'] if p['metadata']['labels']['app']==name]
 assert sorted(p['spec']['nodeName'] for p in pods)==['k8s-worker01','k8s-worker02','k8s-worker03']
 assert {p['metadata']['uid'] for p in pods}==set(f['pod_uids'])
 assert all(p['containers'][0]['ready'] and p['containers'][0]['restartCount']==0 and p['containers'][0]['imageID']==f['image'] for p in pods)
 assert all(not p['spec']['storage'] for p in pods)
 assert d['template']['topologySpreadConstraints'][0]['nodeTaintsPolicy']=='Honor'
for n in q['nodes']:
 assert any(x['type']=='Ready' and x['status']=='True' for x in n['status']['conditions'])
 if n['metadata']['name'].startswith('k8s-worker'):assert not n['spec']['taints'] and not n['spec']['unschedulable']
selected=[p for p in q['worker02pods'] if (p['metadata'].get('labels') or {}).get('app') in ('transaction-api','fds-engine')]
assert len(selected)==2 and all(p['metadata']['namespace']=='fds-app' for p in selected)
for label in ['worker01','worker02','worker03']:
 cache=load('cache-'+label+'/stdout.json')
 assert cache['rc']==0
 present={digest for x in cache['selected_images'] for digest in x['repoDigests']}
 assert all(f['image'] in present for f in final['post_targets'].values())
offsets={}
for host,doc in [('edge01',edge),('control01',c)]:
 t=doc['chronyc'];assert t['rc']==0 and 'Leap status     : Normal' in t['stdout']
 offsets[host]=float(re.search(r'System time\s*:\s*([0-9.]+)',t['stdout'])[1]);assert offsets[host]<=.25
assert all(x['status']==(404 if x['url'].endswith('/metrics') else 200) for x in edge['http'])
up=json.loads(mon['queries'][0]['raw'])['data']['result'];assert len(up)==23 and all(x['value'][1]=='1' for x in up)
assert len([x for x in up if x['metric']['job'] in ('transaction-api','fds-engine')])==6
tools=[];supply=OUT/'supply';supply.mkdir(exist_ok=False)
for name,repo,path,sha in [('ha-probe.py','infra-kubernetes','ops/p1-ha-01-availability/probe.py','e2603769cacef36dab6231052104f29f413b105a78d771b4e4c3db3c0a599804'),('ha-judge.py','infra-kubernetes','ops/p1-ha-01-availability/judge.py','79f54c955991dacd0767885b0db5001fad39080ea7cf4b7c2a3ea13c6f1a6aad'),('rg.py','fds-msa','tools/regression/rg.py','f5dee1069ab96838355cf6269dd6cdff2a08107e880594c5dad98d20424594ed')]:
 raw=(OUT.parent/'p1-parallel-until-0900-20261013/final-test-supply'/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
 head=json.loads(subprocess.check_output(['gh','api',f'repos/321Team/{repo}/commits/main']))['sha']
 doc=json.loads(subprocess.check_output(['gh','api',f'repos/321Team/{repo}/contents/{path}?ref={head}']))
 assert base64.b64decode(doc['content'])==raw
 (supply/name).write_bytes(raw);tools.append({'file':name,'repo':repo,'ref':head,'git_blob':doc['sha'],'sha256':sha,'bytes':len(raw),'current_main_bytes_match':True})
save('TOOL_BINDING.json',tools)
binding={'status':'READINESS_OBSERVED_NOT_EXECUTION_AUTHORIZATION','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cluster':q['cluster'][0]['metadata'],'control_identity':c['identity_before'],'deployments':[dict(metadata=d['metadata'],spec_sha256=final['post_targets'][d['metadata']['name']].get('spec_sha256'),image=final['post_targets'][d['metadata']['name']]['image']) for d in q['deployments']],'active_replica_sets':next(x['items'] for x in load('current-capacity/stdout.json')['queries'] if x['name']=='rs'),'target_node':next(x for x in q['nodes'] if x['metadata']['name']=='k8s-worker02'),'initial_target_pods':[{'metadata':p['metadata'],'imageID':p['containers'][0]['imageID']} for p in selected],'pod_uids_unchanged_from_deploy':True,'pdb_count':0,'hpa_count':0,'worker02_pvc_pods':sum(any(v.get('persistentVolumeClaim') for v in p['spec']['storage']) for p in q['worker02pods']),'clock_abs_offset_seconds':offsets,'api_readyz':3,'api_metrics_404':3,'edge_readyz':200,'mon_up':len(up),'app_mon_up':6,'cache_new_digests_all_workers':True,'ha_mutations':0,'app_post':0,'db_writes':0,'runtime_authorized':False}
# Deployment spec hashes were sealed in the Deploy result's runtime inputs.
for d in binding['deployments']:
 d['spec_sha256']={'transaction-api':'b6b4048d5288a42ee0be5fa3fdd3f2ef82c7659687c0adb9ed61a19d7b8a563a','fds-engine':'0a1d36ae1fda7513b69fa3d1df7ca91983c05770f44df0ebc940c516f8d1faf3'}[d['metadata']['name']]
save('READINESS_BINDING.json',binding)
plan={'id':'p1-ha-20261014-0015','status':'PROPOSED_NOT_AUTHORIZED','not_before':'2026-10-13T15:15:00+00:00','start_deadline':'2026-10-13T15:25:00+00:00','finish_deadline':'2026-10-13T16:05:00+00:00','target_node':'k8s-worker02','namespace':'fds-app','selector':'app in (transaction-api,fds-engine)','probe_seconds':900,'probe_requests_per_second':6,'probe_max_requests':5403,'drain_runs':1,'drain_timeout_seconds':180,'post_drain_ready_timeout_seconds':120,'observation_phase_seconds':61,'conditional_rebalance_evictions_per_app':1,'rebalance_order':['fds-engine','transaction-api'],'rebalance_per_app_ready_seconds':120,'rebalance_per_app_mon_seconds':90,'rebalance_per_app_stability_seconds':30,'automatic_retries':0,'db_writes':False,'image_change':False,'reboot':False,'probe_failure_injection':False,'app_regression':False,'edge_directory':'/home/svc_ansible/p1-ha-20261014-0015','control_directory':'/var/tmp/p1-ha-20261014-0015','requires':['independent input delta review','explicit window console and nonoverlap decision','fresh identity/health/matching selector/clock/capacity guards']}
save('EXECUTION_PROPOSAL.json',plan)
print(json.dumps({'readiness':'PASS_FOR_PREPARATION','tools':len(tools),'mon_up':len(up),'target_pods':[p['metadata']['name'] for p in selected],'clock_abs_offset_seconds':offsets,'runtime_authorized':False},ensure_ascii=False))
