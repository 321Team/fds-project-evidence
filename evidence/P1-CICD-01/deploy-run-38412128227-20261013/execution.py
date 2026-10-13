"""One approved Deploy round, using unchanged reviewed tools and fixed inputs."""
import datetime,hashlib,importlib.util,json,pathlib,shlex,subprocess,sys,time
BASE=pathlib.Path(__file__).parent.resolve();AUTH=BASE/'authorization';OUT=BASE/'execution';OUT.mkdir(exist_ok=True)
A=json.loads((AUTH/'AUTHORIZATION_BINDING.json').read_bytes())
SOURCE='147f760298dd4a683ea58f2a887483769352b97d'
HEAD='3351c6a14505fdc3947948bd68f677e52ef15e47'
PLAN='ed7787673f5b8f8f1f97e49e78a9359ec1c09f8835acda19cc93d7e130ee2ad4'
RECORD='fb8b603e6e9ee4449767d74a5d22fb864c1ef7a0a11d75e1eef0c3144d1c58db'
NAME='deploy-37a528cd-184a-4e0f-8f17-62416ca2e4e4.json'
ROOT='/home/server01_ansible/FDS_CICD_DeployController.37a528cd-184a-4e0f-8f17-62416ca2e4e4'
now=lambda:datetime.datetime.now(datetime.timezone.utc)
START=datetime.datetime.fromisoformat(A['not_before_kst']);CUT=datetime.datetime.fromisoformat(A['actual_start_deadline_kst']);END=datetime.datetime.fromisoformat(A['finish_kst'])
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,x):p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
def gh(endpoint):
 p=subprocess.run(['gh','api',endpoint],capture_output=True,timeout=25);assert p.returncode==0,'READ_FAILED';return json.loads(p.stdout)
def import_file(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ops=import_file('safe_transport',BASE.parent/'phase1-deploy-preparation-20261013/remote_ops.py');ops.OUT=OUT;ops.ROOT=ROOT
collect=import_file('fresh_collect',BASE/'collect.py');collect.OUT=OUT
def static():
 assert sha((BASE/'deploy-plan.unapproved.json').read_bytes())==PLAN
 assert sha((AUTH/NAME).read_bytes())==RECORD and A['record_sha256']==RECORD
 assert A['source_commit']==SOURCE and A['plan_sha256']==PLAN
 assert A['false_runs_allowed']==A['true_runs_allowed']==A['token_requests_allowed']==1 and A['automatic_reruns_allowed']==0
 assert END==datetime.datetime.fromisoformat(A['broker_authorization_expires_utc'])
 meta=json.loads((BASE/'DEPLOY_CONTROLLER_PACKAGE.json').read_bytes())
 assert sha((BASE/meta['archive']).read_bytes())==meta['archive_sha256']=='92b5a57bf9f0030db1c7b0e74276cc645e6041f6eec18257285ee8d6a4d02f0f'
 assert sha((BASE/'native-source-147f760.json').read_bytes())==meta['remote_bundle_sha256']
 assert all(meta['unchanged_from_previous_deploy'].values())
 return meta
def guard(label):
 assert START<=now()<CUT,'OUTSIDE_APPROVED_START_WINDOW'
 assert gh('repos/321Team/infra-cicd/commits/main')['sha']==SOURCE
 approval=gh('repos/321Team/infra-cicd/issues/comments/'+str(A['comment_id']))
 assert approval['body'].encode()==(AUTH/'approval.json').read_bytes() and approval['user']['login']=='GWONUK'
 pr=gh('repos/321Team/fds-project-evidence/pulls/219');assert pr['head']['sha']==HEAD
 reviews=gh('repos/321Team/fds-project-evidence/pulls/219/reviews')
 selected=[r for r in reviews if r['user']['login']=='supreme33-kr' and r['state'] not in ('COMMENTED','PENDING')]
 assert selected and selected[-1]['state']=='APPROVED' and selected[-1]['commit_id']==HEAD,'EXACT_INPUT_REVIEW_REQUIRED'
 checks=gh('repos/321Team/fds-project-evidence/commits/'+HEAD+'/check-runs')
 assert checks['total_count']>0 and all(c['conclusion']=='success' for c in checks['check_runs'])
 save(OUT/(label+'-guard.json'),{'at_utc':now().isoformat(),'head':HEAD,'review_url':selected[-1]['html_url'],'review_body':selected[-1]['body'],'record_sha256':RECORD,'approval_exact':True,'source':SOURCE,'ci':'SUCCESS','user_decision':A['decision_source'],'console':A['console'],'nonoverlap':A['nonoverlap']})
 return selected[-1]
def stage():
 meta=static();guard('stage')
 pre=json.loads((OUT/'ENTRY_READINESS.json').read_bytes())
 assert pre['result']=='PASS' and (now()-datetime.datetime.fromisoformat(pre['at_utc'])).total_seconds()<180
 script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = ansible01','test "$(id -un)" = server01_ansible','test ! -L /home/server01_ansible','test "$(stat -c %a /home/server01_ansible)" = 700','test "$(stat -c %u /home/server01_ansible)" = "$(id -u)"','test ! -e '+ROOT,'test ! -L '+ROOT,'mkdir -m 700 -- '+ROOT,'cd '+ROOT,'set -C','cat > '+meta['archive'],'test "$(sha256sum '+meta['archive']+' | cut -d " " -f 1)" = '+meta['archive_sha256'],'tar --no-same-owner --no-same-permissions --keep-old-files -xf '+meta['archive']+' -C '+ROOT,'find '+ROOT+' -type f -exec sha256sum {} +','find '+ROOT+' -exec stat -c "%n|%u|%a|%F|%h" {} +'])
 result=ops.run('stage-controller',script,(BASE/meta['archive']).read_bytes())
 hashes={line.split('  ',1)[1]:line.split('  ',1)[0] for line in result.decode().splitlines() if '  '+ROOT+'/' in line}
 import tarfile
 with tarfile.open(BASE/meta['archive'],'r:') as tf:
  for member in tf.getmembers():assert hashes[ROOT+'/'+member.name]==sha(tf.extractfile(member).read())
 assert hashes[ROOT+'/'+meta['archive']]==meta['archive_sha256']
 parent='/home/server01_cicd-runner/FDS_CICD_DeployInputs';path=parent+'/'+NAME
 script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = cicd-runner01','test "$(id -un)" = server01_cicd-runner','test "$(id -u)" = 1000','test ! -L /home/server01_cicd-runner','test "$(stat -c %a /home/server01_cicd-runner)" = 700','if test ! -e '+parent+'; then mkdir -m 700 -- '+parent+'; fi','test ! -L '+parent,'test "$(stat -c %u '+parent+')" = 1000','test "$(stat -c %a '+parent+')" = 700','test ! -e '+path,'test ! -L '+path,'set -C','cat > '+path,'sha256sum '+path,'stat -c "%n|%u|%a|%F|%h" '+path])
 result=ops.run('stage-runner',script,(AUTH/NAME).read_bytes(),runner=True)
 assert result.decode().split()[0]==RECORD and '|1000|600|regular file|1' in result.decode()
 save(OUT/'STAGED.json',{'at_utc':now().isoformat(),'record_sha256':RECORD,'archive_sha256':meta['archive_sha256'],'members_verified':13,'server_staging':'PASS','dispatch':'NOT_PERFORMED'})
def observe(run,mode):
 source=(BASE.parent/'phase1-deploy-preparation-20261013/read_deploy_run.py').read_text(encoding='utf-8')
 for old,new in [('5c2d8367f5b81875693165055234a30e5c69944e345c8ad8c5277ef30ebd8387',PLAN),('11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50',RECORD),('2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7',SOURCE)]:
  assert source.count(old)==1;source=source.replace(old,new)
 path=OUT/'read-current-run.py'
 if path.exists():assert path.read_bytes()==source.encode()
 else:path.write_bytes(source.encode())
 label='read-'+str(run)+'-'+now().strftime('%H%M%S%f')
 receipt=collect.remote((label,'10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,path,[str(run),mode]))
 assert receipt['rc']==0
 x=json.loads((OUT/label/'stdout.json').read_bytes());return label,x
def dispatch(mode):
 static();guard('dispatch-'+mode)
 assert json.loads((OUT/'STAGED.json').read_bytes())['record_sha256']==RECORD
 if mode=='true':
  v=json.loads((OUT/'VALIDATION_PASS.json').read_bytes());assert v['PREFLIGHT']=='SUPPLIED_BYTES_MATCH' and v['TOKEN_ISSUED'] is False and v['DEPLOY']=='NOT_EXECUTED'
 d=OUT/('dispatch-'+mode);d.mkdir(exist_ok=False)
 endpoint='repos/321Team/infra-cicd/actions/workflows/app-deploy.yml/runs?per_page=30'
 before=gh(endpoint);save(d/'runs-before.json',before);assert all(x['status']=='completed' for x in before['workflow_runs'])
 ids={x['id'] for x in before['workflow_runs']}
 request={'ref':'main','inputs':{'record_name':NAME,'record_sha256':RECORD,'execute':mode}};save(d/'request.json',request)
 assert START<=now()<CUT
 sent=now().isoformat();r=subprocess.run(['gh','api','repos/321Team/infra-cicd/actions/workflows/app-deploy.yml/dispatches','--method','POST','--input',str(d/'request.json')],capture_output=True,timeout=25)
 (d/'response.stdout').write_bytes(r.stdout);(d/'response.stderr').write_bytes(r.stderr);save(d/'dispatch-receipt.json',{'sent_at_utc':sent,'mode':mode,'rc':r.returncode,'automatic_retry':False})
 assert r.returncode==0,'DISPATCH_UNCONFIRMED_NO_RETRY'
 for attempt in range(15):
  after=gh(endpoint);found=[x for x in after['workflow_runs'] if x['id'] not in ids and x['head_sha']==SOURCE and x['event']=='workflow_dispatch' and x['actor']['login']=='GWONUK']
  if found:
   assert len(found)==1 and found[0]['run_attempt']==1
   save(d/'run.json',found[0]);print(json.dumps({k:found[0][k] for k in ('id','html_url','status','conclusion')}),flush=True);return found[0]['id']
  time.sleep(2)
 raise RuntimeError('RUN_DISCOVERY_UNCONFIRMED_NO_REDISPATCH')
def job_started(run):
 jobs=gh(f'repos/321Team/infra-cicd/actions/runs/{run}/jobs')['jobs']
 assert len(jobs)<=1
 if not jobs or not jobs[0].get('started_at') or jobs[0]['status']=='queued':return None
 job=jobs[0];stamp=datetime.datetime.fromisoformat(job['started_at'].replace('Z','+00:00'))
 save(OUT/('job-'+str(run)+'.json'),job)
 if not START<=stamp<CUT:
  cancel_own_run(run,'ACTUAL_JOB_OUTSIDE_START_WINDOW_NO_BROKER')
  raise RuntimeError('ACTUAL_JOB_OUTSIDE_START_WINDOW_NO_BROKER')
 return job
def cancel_own_run(run,reason):
 d=OUT/('cancel-'+str(run));d.mkdir(exist_ok=False)
 current=gh(f'repos/321Team/infra-cicd/actions/runs/{run}');save(d/'before.json',current)
 assert current['head_sha']==SOURCE and current['run_attempt']==1 and current['actor']['login']=='GWONUK'
 if current['status']=='completed':save(d/'decision.json',{'reason':reason,'action':'ALREADY_COMPLETED_NO_CANCEL'});return
 p=subprocess.run(['gh','api',f'repos/321Team/infra-cicd/actions/runs/{run}/cancel','--method','POST'],capture_output=True,timeout=25)
 (d/'stdout.txt').write_bytes(p.stdout);(d/'stderr.txt').write_bytes(p.stderr)
 save(d/'decision.json',{'reason':reason,'action':'CANCEL_REQUESTED_ONCE','rc':p.returncode,'automatic_retry':False})
def validate():
 run=dispatch('false')
 for _ in range(25):
  r=gh(f'repos/321Team/infra-cicd/actions/runs/{run}');job_started(run)
  if r['status']=='completed':
   save(OUT/'validate-run-final.json',r);assert r['conclusion']=='success'
   label,x=observe(run,'false');assert len(x['matches'])==1
   result=x['matches'][0]['files']['result.json']['data'];assert result['PREFLIGHT']=='SUPPLIED_BYTES_MATCH' and result['TOKEN_ISSUED'] is False and result['DEPLOY']=='NOT_EXECUTED'
   save(OUT/'VALIDATION_PASS.json',dict(result,run_id=run,observation=label));print(json.dumps({'validation':'PASS','run_id':run}),flush=True);return
  if now()>=CUT:cancel_own_run(run,'START_CUTOFF_PASSED_NO_TRUE_RUN');raise RuntimeError('START_CUTOFF_PASSED_NO_TRUE_RUN')
  time.sleep(2)
 raise RuntimeError('VALIDATION_PENDING_NO_AUTOMATIC_RETRY')
def execute():
 run=dispatch('true')
 for _ in range(25):
  job=job_started(run)
  if job:
   label,x=observe(run,'true')
   if x['socket']['exists'] and x['matches']:break
   assert job['status']!='completed','TRUE_RUN_FINISHED_WITHOUT_BROKER'
  if now()>=CUT:cancel_own_run(run,'START_CUTOFF_PASSED_NO_BROKER');raise RuntimeError('START_CUTOFF_PASSED_NO_BROKER')
  time.sleep(2)
 else:raise RuntimeError('SOCKET_NOT_READY_NO_BROKER')
 assert START<=now()<CUT and x['socket']['is_socket'] and x['socket']['uid']==1000 and x['socket']['mode']=='0o600'
 scope=x['matches'][0]['files']['dispatch.json']['data']['binding']
 assert scope=={'execution':{'repository':'321Team/infra-cicd','ref':'refs/heads/main','workflow_sha':SOURCE,'run_id':run,'attempt':1},'record_sha256':RECORD,'plan_sha256':PLAN,'sa_uid':A['sa_uid']}
 raw=(json.dumps(scope,sort_keys=True,separators=(',',':'))+'\n').encode();digest=sha(raw);save(OUT/('scope-'+str(run)+'.json'),scope)
 path=ROOT+'/binding-'+str(run)+'.json';(OUT/('binding-'+str(run)+'.json')).write_bytes(raw)
 script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = ansible01','test "$(id -un)" = server01_ansible','test ! -e '+path,'test ! -L '+path,'set -C','cat > '+path,'sha256sum '+path,'stat -c "%n|%u|%a|%F|%h" '+path])
 result=ops.run('binding-'+str(run),script,raw);assert result.decode().split()[0]==digest
 meta=static();root=ROOT+'/deploy-controller-147f760'
 args=['/usr/bin/python3','-I','-B','-c','import sys; sys.path.insert(0,"tools/delivery"); import transfer_deploy_credential as t; raise SystemExit(t.main())','--bundle',root+'/native-source-147f760.json','--bundle-sha256',meta['remote_bundle_sha256'],'--source-sha',SOURCE,'--binding',path,'--binding-sha256',digest]
 local=json.loads(ops.run('broker-local-'+str(run),'cd '+shlex.quote(root)+' && '+shlex.join(args),timeout=40));assert local=={'HANDOFF':'LOCAL_INPUTS_VALIDATED','TOKEN_ISSUED':False,'DEPLOY':'NOT_EXECUTED'}
 assert START<=now()<CUT
 args+=['--execute','--authorization-expires',A['broker_authorization_expires_utc'],'--cp1-key','/home/server01_ansible/.ssh/id_ed25519','--runner-key','/home/server01_ansible/.ssh/p1_ansible_ed25519']
 save(OUT/'BROKER_ATTEMPT.json',{'run_id':run,'at_utc':now().isoformat(),'maximum_token_requests':1,'automatic_retry':False,'authorization_expires_utc':A['broker_authorization_expires_utc']})
 ops.run('broker-execute-'+str(run),'cd '+shlex.quote(root)+' && '+shlex.join(args),timeout=90)
 print(json.dumps({'broker_finished':True,'run_id':run,'rollout':'MUST_READ_RESULT'}),flush=True)
if __name__=='__main__':
 action=sys.argv[1]
 if action=='static':print(json.dumps({'static':'PASS','bundle_sha256':static()['remote_bundle_sha256'],'utc_end':END.isoformat()}))
 elif action=='stage':stage()
 elif action=='validate':validate()
 elif action=='execute':execute()
 elif action=='observe':
  label,x=observe(int(sys.argv[2]),sys.argv[3]);print(json.dumps({'folder':label,'matches':len(x['matches']),'socket':x['socket'],'results':[m['files'].get('result.json',{}).get('data') for m in x['matches']],'claim_files':len(x.get('claim_files',{}))},ensure_ascii=False))
 else:raise SystemExit('UNKNOWN_MODE')
