"""Evaluate collected originals; no network and no state changes outside local output."""
import datetime,hashlib,json,pathlib
BASE=pathlib.Path(__file__).parent.resolve();F=BASE/'execution/final'
data=json.loads((F/'RUN_RESULTS.json').read_bytes());v,t=data
assert v['mode']=='false' and t['mode']=='true'
assert v['conclusion']=='success' and v['result']['TOKEN_ISSUED'] is False and v['result']['DEPLOY']=='NOT_EXECUTED'
plan=json.loads((BASE/'deploy-plan.unapproved.json').read_bytes());validation=json.loads((BASE/'PLAN_VALIDATION.json').read_bytes())
auth=json.loads((BASE/'authorization/AUTHORIZATION_BINDING.json').read_bytes())
for r in data:
 stamp=datetime.datetime.fromisoformat(r['job_started_at'].replace('Z','+00:00'))
 assert datetime.datetime.fromisoformat(auth['not_before_kst'])<=stamp<datetime.datetime.fromisoformat(auth['actual_start_deadline_kst'])
result=t['result'];receipt=result.get('execution_receipt') or {}
cluster=json.loads((F/'cluster/stdout.json').read_bytes());q={x['kind']:x['items'] for x in cluster['queries']};assert all(x['rc']==0 for x in cluster['queries'])
app=json.loads((F/'app-state/stdout.json').read_bytes());pods=next(x['items'] for x in app['queries'] if x['kind']=='pods')
health=json.loads((F/'runner-health/stdout.json').read_bytes())
out={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'validation_run':v['run_id'],'deploy_run':t['run_id'],'job_id':t['job_id'],'job_started_at':t['job_started_at'],'job_completed_at':t['job_completed_at'],'conclusion':t['conclusion'],'plan_sha256':validation['plan_sha256'],'record_sha256':auth['record_sha256'],'source_commit':auth['source_commit'],'runner_directory':t['runner_directory'],'result_sha256':t['result_sha256'],'session':result.get('status'),'ROLLOUT':receipt.get('ROLLOUT','NOT_CONFIRMED'),'ROLLBACK':receipt.get('ROLLBACK','NOT_CONFIRMED'),'error_code':result.get('error_code'),'socket_absent':not t['socket']['exists'],'claim_files':t['claim_files'],'checkpoint_close':result.get('checkpoint_close'),'credential':result.get('credential'),'worker_count':health['worker_count'],'harbor':health['harbor'],'post_targets':{},'RUNTIME':'NOT_CONFIRMED','HEALTH_E2E':'NOT_VERIFIED','HA':'NOT_EXECUTED','APP_REGRESSION':'NOT_EXECUTED','DB_ACCEPTANCE':'DEFERRED_UNTIL_FINAL_APP_REGRESSION','DELIVERY_GATE':result.get('DELIVERY_GATE','NOT_VERIFIED')}
if t['conclusion']=='success' and receipt.get('ROLLOUT')=='READY' and result.get('error_code')=='NONE':
 assert result['status']=='EXECUTION_RETURNED' and receipt['plan_sha256']==auth['plan_sha256'] and receipt['approval_sha256']==auth['approval_sha256']
 credential=result['credential'];assert credential['local_credential_cleanup']=='LOCAL_REFERENCE_DROPPED' and credential['server_revocation']=='NOT_PERFORMED'
 assert credential['service_account_uid']==auth['sa_uid'] and result['handoff_socket_cleanup']=='OWNED_SOCKET_CLOSED_OR_NOT_CREATED'
 assert result['workflow_input_reference_cleanup']=='LOCAL_REFERENCE_DROPPED'
 issued=datetime.datetime.fromisoformat(credential['issued_at']);expired=datetime.datetime.fromisoformat(credential['token_request_expires_at'])
 assert 0<(expired-issued).total_seconds()<=900
 assert datetime.datetime.fromisoformat(auth['not_before_kst'])<=issued<datetime.datetime.fromisoformat(auth['actual_start_deadline_kst'])
 assert receipt['push_receipt_sha256']==plan['push_receipt_sha256'] and receipt['execution']['run_id']==t['run_id'] and receipt['execution']['attempt']==1
 assert not q['hpa'] and len(pods)==6 and not t['socket']['exists'] and t['claim_files']>1 and result['checkpoint_close']=='CLOSED'
 for target in validation['targets']:
  name=target['service'];dep=next(d for d in q['deployments'] if d['metadata']['name']==name)
  assert dep['metadata']['uid']==target['uid'] and dep['containers'][0]['image']==target['image'] and dep['replicas']==3
  assert all(dep['status'][k]==3 for k in ('readyReplicas','updatedReplicas','availableReplicas'))
  assert dep['spec_sha256']==receipt['images'][name]['ready']['spec_sha256']
  ps=[p for p in pods if p['metadata']['name'].startswith(name+'-')];assert len(ps)==3
  assert all(p['phase']=='Running' and p['metadata']['deletionTimestamp'] is None and len(p['statuses'])==1 and p['statuses'][0]['ready'] and p['statuses'][0]['imageID']==target['image'] and p['statuses'][0]['restartCount']==0 for p in ps)
  slices=[s for x in app['queries'] if x['kind']=='endpointslices' for s in x['items'] if s['labels'].get('kubernetes.io/service-name')==name]
  endpoints=[p for s in slices for p in s['endpoints']]
  assert len(endpoints)==3 and {p['targetRef']['uid'] for p in endpoints}=={p['metadata']['uid'] for p in ps}
  assert all(p['conditions'].get('ready') and p['conditions'].get('serving') and not p['conditions'].get('terminating') for p in endpoints)
  out['post_targets'][name]={'image':target['image'],'uid':target['uid'],'generation':dep['metadata']['generation'],'ready':3,'pod_uids':[p['metadata']['uid'] for p in ps],'nodes':[p['node'] for p in ps],'restart_counts':[p['statuses'][0]['restartCount'] for p in ps],'endpoint_count':3}
 assert health['worker_count']==0 and health['harbor']['tls_verified'] and health['harbor']['status']=='healthy'
 out['RUNTIME']='DEPLOY_AND_POD_DIGEST_READY_VERIFIED'
else:
 out['post_targets']={d['metadata']['name']:{'image':d['containers'][0]['image'],'uid':d['metadata']['uid'],'status':d['status']} for d in q['deployments']}
 out['RUNTIME']='FAILED_OR_UNCONFIRMED_PRESERVE_RESULTS'
(F/'VERIFIED_RESULT.json').write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(out,ensure_ascii=False))
