"""Local orchestration of the explicitly authorized single Push. No automatic retry."""
import concurrent.futures, datetime as dt, hashlib, importlib.util, json, pathlib, subprocess, sys
P=pathlib.Path(__file__).resolve().parent
E=P.parent/'phase1-push-execution-20261013-2220'
E.mkdir(exist_ok=True)
REPO='321Team/infra-cicd'
SHA='147f760298dd4a683ea58f2a887483769352b97d'
HEAD='e8f130eb44677b390ab5e8e0d46805f31399d4c5'
HASH='8b7b4f4e64c271b54167bc768e4e3afc1b2326c480683aaaf4aa0ff3e18c2b06'
NAME='push-tbs38395350748-window0030.json'
COL=P.parent.parent/'phase1-work-20261013/tbs-inspect-evidence-2010/evidence/P1-CICD-01/push-readiness-38395350748-20261013'
spec=importlib.util.spec_from_file_location('transport',P.parent/'phase1-tbs-id-fix-20261013-2110/tbs_control.py')
transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport);transport.OUT=E
now=lambda:dt.datetime.now(dt.timezone.utc)
def save(name,data):
 with (E/name).open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def api(path):
 p=subprocess.run(['gh','api',path],capture_output=True,timeout=35);assert p.returncode==0,'API_READ_FAILED '+path;return json.loads(p.stdout)
def check(label):
 auth=json.loads((P/'USER_AUTHORIZATION.json').read_bytes())
 assert auth['max_validate_runs']==auth['max_execute_runs']==1 and not auth['deploy_authorized']
 assert auth['target_sha256']==HASH and auth['non_overlap_user_confirmed'] and auth['exclusive_secret_use_user_confirmed']
 assert now()<dt.datetime.fromisoformat(auth['actual_push_job_start_deadline_kst']),'START_WINDOW_EXPIRED'
 paths={'main':f'repos/{REPO}/commits/main','runner':f'repos/{REPO}/actions/runners','secrets':f'repos/{REPO}/actions/secrets','pr':'repos/321Team/fds-project-evidence/pulls/218','reviews':'repos/321Team/fds-project-evidence/pulls/218/reviews','push_runs':f'repos/{REPO}/actions/workflows/app-push.yml/runs?per_page=100','recent':f'repos/{REPO}/actions/runs?per_page=100'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:d=dict(zip(paths,pool.map(api,paths.values())))
 d['at_utc']=now().isoformat();save(label+'.json',d)
 assert d['main']['sha']==SHA and d['pr']['head']['sha']==HEAD,'SOURCE_CHANGED'
 reviews=[r for r in d['reviews'] if r['user']['login']=='supreme33-kr' and r['commit_id']==HEAD]
 assert reviews and reviews[-1]['state']=='APPROVED' and HASH in reviews[-1]['body'],'EXACT_INPUT_REVIEW_REQUIRED'
 assert not any(r['state']=='CHANGES_REQUESTED' for r in d['reviews']),'CHANGES_REQUESTED'
 assert len(d['runner']['runners'])==1
 r=d['runner']['runners'][0];assert r['name']=='cicd-runner01' and r['status']=='online' and not r['busy'],'RUNNER_NOT_IDLE'
 assert {'self-hosted','Linux','X64','p1-cicd','onprem','podman'} <= {x['name'] for x in r['labels']}
 assert all(r['status']=='completed' for r in d['recent']['workflow_runs']),'ACTIVE_WORKFLOW'
 registered=json.loads((P/'SECRET_REGISTRATION_CONFIRMED.json').read_bytes())['secrets']
 expected={x['name']:x for x in registered}
 actual={x['name']:x for x in d['secrets']['secrets']}
 for n in ['HARBOR_CI_ROBOT_USERNAME','HARBOR_CI_ROBOT_TOKEN','CICD_APP_SOURCE_READ_TOKEN']:
  assert n in actual and actual[n]==expected[n],'SECRET_METADATA_CHANGED '+n
 return d
def stage():
 assert not (E/'STAGE_INTENT.json').exists(),'STAGE_ALREADY_ATTEMPTED'
 d=check('github-before-stage')
 original=transport.remote('evidence-before-stage',(P.parent/'phase1-tbs-id-fix-20261013-2110/runner_evidence_verify.py').read_bytes())
 assert original['verdict']['EVIDENCE_CHECK']=='PASS' and original['verdict']['RAW_PAYLOAD_CHECK']=='LOCAL_BYTES'
 current=transport.remote('runner-before-stage',(P/'runner_push_read.py').read_bytes())
 assert current['worker_count']==0 and current['harbor']['tls_verified'] and current['harbor']['status']=='healthy'
 pending=json.loads((COL/'push.pending.json').read_bytes());assert hashlib.sha256((COL/'push.pending.json').read_bytes()).hexdigest()=='f20a5f5d7ad031271ccc6ac03456b88b5bb398a3222b426ef13409b99cb5b6ef'
 pending['template_only']=False;pending['status']='APPROVED_FOR_DELIVERY'
 raw=(json.dumps(pending,ensure_ascii=False,indent=2)+'\n').encode();assert hashlib.sha256(raw).hexdigest()==HASH
 with (E/NAME).open('xb') as f:f.write(raw)
 old=(P.parent/'p1-push-execution-20261013/stage-input/card.py').read_text(encoding='utf-8')
 tail=old[old.index('\nfrom pathlib import Path'):]
 tail=tail.replace('2026-10-13T10:00:00+09:00','2026-10-13T22:30:00+09:00').replace('push-20261013-window1200.json',NAME).replace('13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89',HASH)
 code=('RAW='+repr(raw)+'\n'+tail).encode();compile(code,'stage-reviewed-procedure','exec')
 save('STAGE_INTENT.json',{'at_utc':now().isoformat(),'target':NAME,'sha256':HASH,'authorization':json.loads((P/'AUTHORIZATION_COMMENT.json').read_bytes())['html_url'],'review_url':d['reviews'][-1]['html_url'],'no_automatic_retry':True})
 r=transport.remote('stage-input',code);assert r['sha256']==HASH and r['status']=='STAGED';save('ACTIVATION_RECEIPT.json',r);print(json.dumps(r))
def dispatch(mode):
 assert mode in ['false','true']
 assert dt.datetime.fromisoformat('2026-10-13T22:20:00+09:00')<=now()<dt.datetime.fromisoformat('2026-10-13T22:30:00+09:00'),'OUTSIDE_APPROVED_START_WINDOW'
 label='validate' if mode=='false' else 'execute';assert not (E/(label+'-DISPATCH_INTENT.json')).exists(),'QUOTA_CONSUMED'
 assert json.loads((E/'ACTIVATION_RECEIPT.json').read_bytes())['sha256']==HASH
 if mode=='true':
  validation=json.loads((E/'VALIDATION_VERIFIED.json').read_bytes());assert validation['VALIDATION']=='PASS' and validation['PUSH']=='NOT_EXECUTED'
  assert dt.datetime.fromisoformat('2026-10-13T22:20:00+09:00')<=now()<dt.datetime.fromisoformat('2026-10-13T22:30:00+09:00'),'OUTSIDE_ACTUAL_PUSH_START_WINDOW'
 d=check('github-before-'+label)
 if mode=='true':
  r=transport.remote('runner-before-execute',(P/'runner_push_read.py').read_bytes());assert r['worker_count']==0 and r['harbor']['tls_verified'] and r['harbor']['status']=='healthy'
  assert HASH+'.json' not in {x['name'] for x in r['previous_claims']},'CLAIM_ALREADY_CONSUMED'
  assert now()<dt.datetime.fromisoformat('2026-10-13T22:30:00+09:00')
 payload={'ref':'main','inputs':{'record_name':NAME,'record_sha256':HASH,'execute':mode=='true'}}
 save(label+'-dispatch.json',payload)
 save(label+'-DISPATCH_INTENT.json',{'at_utc':now().isoformat(),'prior_run_ids':[r['id'] for r in d['push_runs']['workflow_runs']],'sha':SHA,'input_sha256':HASH,'mode':mode,'quota_consumed_on_attempt':True})
 p=subprocess.run(['gh','api','--method','POST',f'repos/{REPO}/actions/workflows/app-push.yml/dispatches','--input',str(E/(label+'-dispatch.json'))],capture_output=True,timeout=35)
 save(label+'-DISPATCH_RESPONSE.json',{'at_utc':now().isoformat(),'rc':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')});print(json.dumps({'mode':mode,'rc':p.returncode,'retry':'FORBIDDEN'}))
if __name__=='__main__':
 if sys.argv[1]=='stage':stage()
 elif sys.argv[1]=='dispatch':dispatch(sys.argv[2])
 elif sys.argv[1]=='check':print(json.dumps({'at_utc':check(sys.argv[2])['at_utc'],'status':'PASS'}))
 else:raise SystemExit('Unsupported mode')
