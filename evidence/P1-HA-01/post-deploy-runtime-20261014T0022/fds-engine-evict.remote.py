# One native Eviction command after fresh read guards. No loop/retry/force deletion.
import datetime,hashlib,json,os,socket,subprocess,time
BINDING={'status': 'READINESS_OBSERVED_NOT_EXECUTION_AUTHORIZATION', 'at_utc': '2026-10-13T14:51:46.617404+00:00', 'cluster': {'name': 'kube-system', 'namespace': None, 'uid': 'e1669cff-1435-423f-a6c4-28bc44f488de', 'resourceVersion': '4189926', 'generation': None, 'labels': {'kubernetes.io/metadata.name': 'kube-system', 'pod-security.kubernetes.io/audit': 'restricted', 'pod-security.kubernetes.io/audit-version': 'v1.36', 'pod-security.kubernetes.io/enforce': 'privileged', 'pod-security.kubernetes.io/enforce-version': 'v1.36', 'pod-security.kubernetes.io/warn': 'restricted', 'pod-security.kubernetes.io/warn-version': 'v1.36'}}, 'control_identity': {'host': 'k8s-control01', 'uid': 0, 'boot': '2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360', 'product_uuid': '80724d56-7c17-f8a0-b2ea-ece7a154e24b'}, 'deployments': [{'metadata': {'name': 'transaction-api', 'namespace': 'fds-app', 'uid': '8a2af808-ec33-41f2-80b5-addde4e28910', 'resourceVersion': '5417375', 'generation': 12, 'labels': {'app': 'transaction-api'}}, 'spec_sha256': 'b6b4048d5288a42ee0be5fa3fdd3f2ef82c7659687c0adb9ed61a19d7b8a563a', 'image': '10.1.93.54/fds/transaction-api@sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0', 'images': [{'image': '10.1.93.54/fds/transaction-api@sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0'}]}, {'metadata': {'name': 'fds-engine', 'namespace': 'fds-app', 'uid': 'bf825dec-465b-4603-8b71-f768d195531c', 'resourceVersion': '5417639', 'generation': 6, 'labels': {'app': 'fds-engine'}}, 'spec_sha256': '0a1d36ae1fda7513b69fa3d1df7ca91983c05770f44df0ebc940c516f8d1faf3', 'image': '10.1.93.54/fds/fds-engine@sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d', 'images': [{'image': '10.1.93.54/fds/fds-engine@sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d'}]}], 'active_replica_sets': [{'metadata': {'name': 'fds-engine-65479b5bf', 'uid': 'ad644957-7157-4b4a-a342-244bc0ab8483', 'resourceVersion': '5417616', 'ownerReferences': [{'apiVersion': 'apps/v1', 'blockOwnerDeletion': True, 'controller': True, 'kind': 'Deployment', 'name': 'fds-engine', 'uid': 'bf825dec-465b-4603-8b71-f768d195531c'}]}, 'replicas': 3, 'selector': {'matchLabels': {'app': 'fds-engine', 'pod-template-hash': '65479b5bf'}}}, {'metadata': {'name': 'transaction-api-666c98b5f5', 'uid': '7ff3c110-8cca-4b26-abad-fb67baa57baf', 'resourceVersion': '5417345', 'ownerReferences': [{'apiVersion': 'apps/v1', 'blockOwnerDeletion': True, 'controller': True, 'kind': 'Deployment', 'name': 'transaction-api', 'uid': '8a2af808-ec33-41f2-80b5-addde4e28910'}]}, 'replicas': 3, 'selector': {'matchLabels': {'app': 'transaction-api', 'pod-template-hash': '666c98b5f5'}}}], 'target_node': {'metadata': {'name': 'k8s-worker02', 'namespace': None, 'uid': '4c6eec26-153e-4da5-bf8a-f80223ca3c1b', 'resourceVersion': '5421369', 'generation': None, 'labels': {'beta.kubernetes.io/arch': 'amd64', 'beta.kubernetes.io/os': 'linux', 'kubernetes.io/arch': 'amd64', 'kubernetes.io/hostname': 'k8s-worker02', 'kubernetes.io/os': 'linux'}}, 'spec': {'unschedulable': None, 'taints': None, 'podCIDR': '10.244.4.0/24'}, 'status': {'conditions': [{'type': 'NetworkUnavailable', 'status': 'False', 'lastTransitionTime': '2026-10-11T10:20:06Z'}, {'type': 'MemoryPressure', 'status': 'False', 'lastTransitionTime': '2026-10-11T10:19:22Z'}, {'type': 'DiskPressure', 'status': 'False', 'lastTransitionTime': '2026-10-11T10:19:22Z'}, {'type': 'PIDPressure', 'status': 'False', 'lastTransitionTime': '2026-10-11T10:19:22Z'}, {'type': 'Ready', 'status': 'True', 'lastTransitionTime': '2026-10-11T10:19:22Z'}], 'allocatable': {'cpu': '8', 'ephemeral-storage': '67585336823', 'hugepages-1Gi': '0', 'hugepages-2Mi': '0', 'memory': '24207692Ki', 'pods': '110'}, 'nodeInfo': {'kernelVersion': '6.12.0-267.el10.x86_64', 'containerRuntimeVersion': 'containerd://2.3.5', 'kubeletVersion': 'v1.36.4'}}}, 'initial_target_pods': [{'metadata': {'name': 'fds-engine-65479b5bf-4jc8j', 'namespace': 'fds-app', 'uid': '533caef6-e244-451a-96d1-8d4de9f40983', 'resourceVersion': '5417524', 'generation': 1, 'labels': {'app': 'fds-engine', 'pod-template-hash': '65479b5bf'}}, 'imageID': '10.1.93.54/fds/fds-engine@sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d'}, {'metadata': {'name': 'transaction-api-666c98b5f5-9fk6b', 'namespace': 'fds-app', 'uid': 'da814b7b-1a35-4ce9-8719-eedee3d7936d', 'resourceVersion': '5417249', 'generation': 1, 'labels': {'app': 'transaction-api', 'pod-template-hash': '666c98b5f5'}}, 'imageID': '10.1.93.54/fds/transaction-api@sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0'}], 'pod_uids_unchanged_from_deploy': True, 'pdb_count': 0, 'hpa_count': 0, 'worker02_pvc_pods': 0, 'clock_abs_offset_seconds': {'edge01': 0.000314688, 'control01': 0.000330994}, 'api_readyz': 3, 'api_metrics_404': 3, 'edge_readyz': 200, 'mon_up': 23, 'app_mon_up': 6, 'cache_new_digests_all_workers': True, 'ha_mutations': 0, 'app_post': 0, 'db_writes': 0, 'runtime_authorized': False, 'host': 'k8s-control01', 'boot': '2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360', 'cluster_uid': 'e1669cff-1435-423f-a6c4-28bc44f488de', 'observed_pods': [{'metadata': {'deletionTimestamp': None, 'generation': 1, 'name': 'fds-engine-65479b5bf-6qh6s', 'namespace': 'fds-app', 'resourceVersion': '5417611', 'uid': '1b2f1c14-a04f-438c-b051-4d65a0a8a8e7'}}, {'metadata': {'deletionTimestamp': None, 'generation': 1, 'name': 'fds-engine-65479b5bf-d6kkm', 'namespace': 'fds-app', 'resourceVersion': '5427539', 'uid': '6d83bdd9-5cbd-4de4-abb2-8e69b2973b0b'}}, {'metadata': {'deletionTimestamp': None, 'generation': 1, 'name': 'fds-engine-65479b5bf-kmp2t', 'namespace': 'fds-app', 'resourceVersion': '5417439', 'uid': '4ab7c0a7-c7aa-4f0c-9a63-642a752dbe51'}}, {'metadata': {'deletionTimestamp': None, 'generation': 1, 'name': 'transaction-api-666c98b5f5-2v27l', 'namespace': 'fds-app', 'resourceVersion': '5417339', 'uid': '4d0b362b-5081-4745-b68a-85636e08dc10'}}, {'metadata': {'deletionTimestamp': None, 'generation': 1, 'name': 'transaction-api-666c98b5f5-bbx9q', 'namespace': 'fds-app', 'resourceVersion': '5417166', 'uid': '9d34d371-5839-429b-b255-a9a4a6ebdd31'}}, {'metadata': {'deletionTimestamp': None, 'generation': 1, 'name': 'transaction-api-666c98b5f5-lq66r', 'namespace': 'fds-app', 'resourceVersion': '5427540', 'uid': '853a49a2-4a7c-46f1-982a-af3156e9961b'}}]}
APP='fds-engine'
EXPECTED_COUNTS={'transaction-api': {'k8s-worker01': 2, 'k8s-worker02': 0, 'k8s-worker03': 1}, 'fds-engine': {'k8s-worker01': 2, 'k8s-worker02': 0, 'k8s-worker03': 1}}
KC=['/usr/bin/kubectl','--kubeconfig=/etc/kubernetes/admin.conf','--request-timeout=6s']
out={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'app':APP,'queries':[],'eviction_command_invocations':0}
def require(ok,why):
 if not ok:raise RuntimeError(why)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def get(name,args):
 p=subprocess.run(KC+args+['-o','json'],capture_output=True,timeout=8)
 out['queries'].append({'name':name,'argv':KC+args+['-o','json'],'rc':p.returncode,'response_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr':p.stderr.decode(errors='replace')})
 require(p.returncode==0,'GET_FAILED_'+name)
 return json.loads(p.stdout)
def ready(p):return any(c['type']=='Ready' and c['status']=='True' for c in p.get('status',{}).get('conditions',[]))
try:
 require(os.geteuid()==0 and socket.gethostname()==BINDING['host'],'HOST_OR_UID')
 require(open('/proc/sys/kernel/random/boot_id').read().strip()==BINDING['boot'],'BOOT_CHANGED')
 ns=get('cluster',['get','namespace','kube-system']);require(ns['metadata']['uid']==BINDING['cluster_uid'],'CLUSTER_CHANGED')
 deps=get('deployments',['get','deploy','-n','fds-app','transaction-api','fds-engine'])['items']
 rss=get('rs',['get','rs','-n','fds-app'])['items']
 pods=get('pods',['get','pods','-n','fds-app'])['items']
 nodes=get('nodes',['get','nodes'])['items']
 pdb=get('pdb',['get','pdb','-n','fds-app'])['items']
 hpa=get('hpa',['get','hpa','-n','fds-app'])['items']
 eps=get('endpoints',['get','endpointslices','-n','fds-app'])['items']
 require(not pdb and not hpa,'PDB_OR_HPA_CHANGED')
 require(len(pods)==6 and all(ready(p) and p['status']['phase']=='Running' and not p['metadata'].get('deletionTimestamp') for p in pods),'POD_HEALTH_OR_COUNT')
 require(len(nodes)==6 and all(ready(n) and all(c['status']=='False' for c in n['status']['conditions'] if c['type'].endswith('Pressure')) for n in nodes),'NODE_HEALTH')
 workers=['k8s-worker01','k8s-worker02','k8s-worker03']
 for n in nodes:
  if n['metadata']['name'] in workers:
   require(not n['spec'].get('unschedulable') and not n['spec'].get('taints'),'WORKER_AVAILABILITY')
   require(n['metadata']['labels'].get('kubernetes.io/hostname')==n['metadata']['name'],'DOMAIN_LABEL')
 app_pods={}
 for fixed in BINDING['deployments']:
  name=fixed['metadata']['name'];d=next(x for x in deps if x['metadata']['name']==name)
  require(d['metadata']['uid']==fixed['metadata']['uid'] and digest(d['spec'])==fixed['spec_sha256'],'DEPLOYMENT_CHANGED_'+name)
  require(d['status']['observedGeneration']==d['metadata']['generation'] and d['status']['readyReplicas']==3 and d['status']['updatedReplicas']==3 and d['status']['availableReplicas']==3,'DEPLOYMENT_HEALTH_'+name)
  rfix=next(r for r in BINDING['active_replica_sets'] if any(o['uid']==d['metadata']['uid'] and o.get('controller') for o in r['metadata']['ownerReferences']))
  active=[r for r in rss if r['spec'].get('replicas',0)>0 and any(o['uid']==d['metadata']['uid'] and o.get('controller') for o in r['metadata'].get('ownerReferences',[]))]
  require(len(active)==1 and active[0]['metadata']['uid']==rfix['metadata']['uid'] and active[0]['spec']['replicas']==3,'RS_CHANGED_'+name)
  pp=[p for p in pods if any(o['uid']==rfix['metadata']['uid'] and o.get('controller') for o in p['metadata'].get('ownerReferences',[]))]
  require(len(pp)==3 and all([c['image'] for c in p['spec']['containers']]==[c['image'] for c in fixed['images']] for p in pp),'POD_IMAGE_OR_OWNER_'+name)
  counts={w:sum(p['spec'].get('nodeName')==w for p in pp) for w in workers}
  require(counts==EXPECTED_COUNTS[name],'PLACEMENT_CHANGED_'+name)
  service='transaction-api-nodeport' if name=='transaction-api' else 'fds-engine'
  endpoints=[e for s in eps if s['metadata']['labels'].get('kubernetes.io/service-name')==service for e in s['endpoints']]
  require(len(endpoints)==3 and all(e['conditions'].get('ready') is True and not e['conditions'].get('terminating') for e in endpoints),'ENDPOINT_HEALTH_'+name)
  require({e['targetRef']['uid'] for e in endpoints}=={p['metadata']['uid'] for p in pp},'ENDPOINT_UID_'+name)
  app_pods[name]=pp
 allowed={p['metadata']['uid'] for p in BINDING['observed_pods']}
 choices=[p for p in app_pods[APP] if p['spec']['nodeName']=='k8s-worker01' and p['metadata']['uid']=='6d83bdd9-5cbd-4de4-abb2-8e69b2973b0b' and p['metadata']['uid'] in allowed]
 require(len(choices)==1,'NO_BOUNDED_TARGET')
 target=sorted(choices,key=lambda p:p['metadata']['name'])[0]
 name=target['metadata']['name'];fresh=get('target',['get','pod','-n','fds-app',name])
 require(fresh['metadata']['uid']==target['metadata']['uid'] and ready(fresh) and not fresh['metadata'].get('deletionTimestamp') and fresh['spec']['terminationGracePeriodSeconds']==30,'TARGET_CHANGED')
 eviction={'apiVersion':'policy/v1','kind':'Eviction','metadata':{'name':name,'namespace':'fds-app'},'deleteOptions':{'preconditions':{'uid':fresh['metadata']['uid'],'resourceVersion':fresh['metadata']['resourceVersion']},'gracePeriodSeconds':30}}
 out['target']=eviction;out['pre_placement']=EXPECTED_COUNTS;out['guard']='PASS'
 import pathlib
 path=pathlib.Path('/var/tmp/p1-ha-20261014-0015')
 require(not path.is_symlink() and path.stat().st_uid==0,'CONTROL_DIRECTORY')
 timeline=(path/'timeline.txt').read_text().splitlines()
 require(len(timeline)==5 and timeline[-1].startswith('end '),'W_NOT_ENDED')
 require(datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-13T16:01:00+00:00'),'RECOVERY_BUDGET')
 os.umask(0o077)
 with (path/(APP+'-eviction.json')).open('x') as f:json.dump(eviction,f);f.flush();os.fsync(f.fileno())
 argv=KC[:-1]+['--request-timeout=10s','create','--raw','/api/v1/namespaces/fds-app/pods/'+name+'/eviction','-f',str(path/(APP+'-eviction.json'))]
 out['eviction_command_invocations']=1;out['dispatch_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  p=subprocess.run(argv,capture_output=True,timeout=12)
  out['request']={'argv':argv,'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')}
  out['status']='EVICTION_COMMAND_SUCCEEDED_READBACK_REQUIRED' if p.returncode==0 else 'EVICTION_COMMAND_FAILED_OR_UNCERTAIN_NO_RETRY'
 except subprocess.TimeoutExpired:
  out['status']='EVICTION_COMMAND_TIMEOUT_UNCERTAIN_NO_RETRY'
except Exception as e:
 out['status']='STOP';out['error']=type(e).__name__+':'+str(e)
out['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (path/(APP+'-eviction-result.json')).open('x') as f:json.dump(out,f)
print(json.dumps(out))
raise SystemExit(0 if out['status']=='EVICTION_COMMAND_SUCCEEDED_READBACK_REQUIRED' else 2)
