"""Single authorized AC09 round; existing frozen production tools and normal paths."""
import concurrent.futures, datetime as dt, hashlib, importlib.util, io, json, pathlib, shlex, subprocess, sys, tarfile, time
O=pathlib.Path(__file__).resolve().parent; B=O.parent; ROOT=B.parents[1]
SOURCE='fddc76e1c261cd938f06211b7ed035fdcb32e606'; SA='8f1ddfef-7bec-4b15-8cb7-c4b1a068a176'
REMOTE='/home/server01_ansible/FDS_CICD_AC09_20261015_1535'
START=dt.datetime.fromisoformat('2026-10-15T15:35:00+09:00'); CUT=START+dt.timedelta(minutes=10); END=START+dt.timedelta(minutes=45)
now=lambda:dt.datetime.now(dt.timezone.utc)
sha=lambda b:hashlib.sha256(b).hexdigest()
encode=lambda x:(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def save(p,x):p.write_bytes(encode(x))
def load(p):return json.loads(p.read_bytes())
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ops=module('ops',ROOT/'deliverables/phase1-deploy-preparation-20261013/remote_ops.py');ops.OUT=O
collect=module('collect',ROOT/'deliverables/phase1-deploy-after-push-20261013-2244/collect.py');collect.OUT=O
def gh(ep,method='GET',obj=None,label=None):
 args=['gh','api',ep]
 if obj is not None:
  assert label;d=O/label;d.mkdir(exist_ok=False);save(d/'request.json',obj);args+=['--method',method,'--input',str(d/'request.json')]
 p=subprocess.run(args,capture_output=True,timeout=25)
 if label:
  if obj is None:d=O/label;d.mkdir(exist_ok=False)
  (d/'response.json').write_bytes(p.stdout);(d/'stderr.txt').write_bytes(p.stderr)
  save(d/'receipt.json',{'at_utc':now().isoformat(),'method':method,'rc':p.returncode,'retry':False})
 assert p.returncode==0,'API_UNCONFIRMED_NO_RETRY'
 return json.loads(p.stdout) if p.stdout.strip() else None
def authorization():
 a=load(ROOT/'deliverables/phase1-central-control-20261015/AC09_USER_AUTHORIZATION_1535.json')
 assert a['approved'] and a['user_answer']=='제시한 실행·복구 범위 승인'
 assert a['card_sha256']==sha((ROOT/'deliverables/phase1-central-control-20261015'/a['card']).read_bytes())
 assert a['detail_card_sha256']==sha((B/'round5/FINAL_OPERATOR_CARD.md').read_bytes())
 assert a['timing_contract_sha256']==sha((B/'round5/TIMING_CONTRACT.md').read_bytes())
 assert a['normal_max_jobs']==4 and a['new_runner_registrations']==0
 assert START<=now()<END
 return a
def status(msg):
 p=ROOT/'deliverables/phase1-central-control-20261015/CICD_STATUS.md'
 p.write_bytes((f'# AC09 실제 회차 — {now().astimezone(dt.timezone(dt.timedelta(hours=9))).isoformat()}\n\n{msg}\n\n---\n'+p.read_text(encoding='utf-8')).encode())
def fresh():
 authorization();assert now()<CUT
 assert gh('repos/321Team/infra-cicd/commits/main')['sha']==SOURCE
 for st in ('queued','in_progress','waiting','requested','pending'):
  x=gh('repos/321Team/infra-cicd/actions/runs?status='+st+'&per_page=100',label='entry-actions-'+st);assert x['total_count']==0
 tasks=[('entry-management','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,B/'round4/management_readonly.py',[]),
        ('entry-runner','10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,B/'round5/runner_activity_read.py',[])]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:r=list(pool.map(collect.remote,tasks))
 assert all(v['rc']==0 for v in r)
 m=load(O/'entry-management/stdout.json');prior=load(B/'round4/management-read-v2/stdout.json')
 for old,new in zip(prior['deployments'],m['deployments']):
  assert all(old[k]==new[k] for k in ('name','uid','image','replicas','normalized_spec_sha256'))
  assert new['status']['readyReplicas']==new['status']['updatedReplicas']==3
 assert all(p['name']!='Runner.Worker' for p in load(O/'entry-runner/stdout.json')['processes'])
 save(O/'ENTRY.json',{'at_utc':now().isoformat(),'result':'PASS','main':SOURCE,'active_runs':0,'nonoverlap':'Central owns window; Harbor/Ansible hold','app_uid_digest_spec_ready':'MATCH'})
 status('사용자 승인 원문·카드 해시 결속 및 실제 진입 읽기 PASS. 승인창15:35~16:20 단일담당 착수. 고정UID/현행digest/spec/각Ready3·Runner Worker0·CICD active5종0 확인. 아직 PATCH/Token/POST0. exact 회차 승인 기록·공급 진행.')
def authorize():
 authorization();assert now()<CUT
 assert load(O/'ENTRY.json')['result']=='PASS'
 assert gh('user')['login']=='GWONUK'
 sys.path.insert(0,str(B/'source'));import deploy_plan
 bindings={}
 for round,phase,expiry in [('R1','r1-restore-previous','2026-10-15T16:00:00+09:00'),('R2','r2-return-current','2026-10-15T16:15:00+09:00')]:
  folder=O/round;folder.mkdir(exist_ok=False)
  plan=(B/(phase+'.plan.candidate.json')).read_bytes()
  placeholder='CODEX_ASSISTED · 중앙 사용자 승인 및 https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186064463 에 결속한 AC09 '+round+' exact approval JSON 생성 중. 최종 바이트 게시/대조 전 실행 없음.'
  comment=gh('repos/321Team/infra-cicd/issues/11/comments','POST',{'body':placeholder},round+'-approval-create')
  a=load(B/(phase+'.approval.TEMPLATE.json'));a.update(template_only=False,reference=comment['html_url'],approved_by='GWONUK',not_before='2026-10-15T15:35:00+09:00',expires_at=expiry)
  raw=encode(a);(folder/'approval.json').write_bytes(raw)
  gh('repos/321Team/infra-cicd/issues/comments/'+str(comment['id']),'PATCH',{'body':raw.decode()},round+'-approval-publish')
  read=gh('repos/321Team/infra-cicd/issues/comments/'+str(comment['id']),label=round+'-approval-readback')
  assert read['body'].encode()==raw and read['user']['login']=='GWONUK'
  push=(B/'references/push-receipt.json').read_bytes()
  result=deploy_plan.validate(plan,raw,push,sha(plan),sha(raw),dict(a['workflow'],run_id=1,attempt=1),now());assert result['binding']=='MATCH'
  record=encode({'schema':'P1-CICD-deploy-inputs-1','plan':plan.decode(),'approval':raw.decode(),'push_receipt':push.decode(),'sa_uid':SA})
  name='deploy-'+json.loads(plan)['request_id']+'.json';(folder/name).write_bytes(record)
  binding={'round':round,'record_name':name,'record_sha256':sha(record),'approval_sha256':sha(raw),'plan_sha256':sha(plan),'comment_id':comment['id'],'reference':comment['html_url'],'expiry':expiry,'source':SOURCE}
  save(folder/'BINDING.json',binding);bindings[round]=binding
 save(O/'AUTHORIZATION_BINDINGS.json',bindings)
 recovery=load(B/'round4/recovery-contract.TEMPLATE.json');recovery.update(template_only=False,approved=True,approved_by='GWONUK',approval_reference='https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186064463',window_start='2026-10-15T15:35:00+09:00',sec_acceptance_expires_at='2026-10-15T16:20:00+09:00',expires_at='2026-10-15T16:35:00+09:00',independent_emergency_recovery_authorized=True)
 save(O/'recovery-contract.json',recovery)
 edge=load(B/'round4/runtime-observation-authorization.TEMPLATE.json');edge.update(template_only=False,runtime_go=True,approved_by='GWONUK',approval_reference=recovery['approval_reference'],window_start=recovery['window_start'],expires_at=recovery['sec_acceptance_expires_at'])
 save(O/'runtime-observation-authorization.json',edge)
 print(json.dumps(bindings),flush=True)
def stage():
 authorization();assert now()<CUT
 archive=io.BytesIO();members={}
 with tarfile.open(fileobj=archive,mode='w') as t:
  for p in sorted((B/'source').glob('*.py'))+[B/'native-source.bundle.json']:
   name='tools/delivery/'+p.name if p.parent.name=='source' else p.name
   raw=p.read_bytes();i=tarfile.TarInfo(name);i.mode=0o600;i.size=len(raw);t.addfile(i,io.BytesIO(raw));members[name]=sha(raw)
 raw=archive.getvalue();(O/'controller.tar').write_bytes(raw);save(O/'CONTROLLER_PACKAGE.json',{'archive_sha256':sha(raw),'members':members})
 script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = ansible01','test "$(id -un)" = server01_ansible','test ! -e '+REMOTE,'test ! -L '+REMOTE,'mkdir -m 700 '+REMOTE,'cd '+REMOTE,'set -C','cat > controller.tar','test "$(sha256sum controller.tar | cut -d " " -f 1)" = '+sha(raw),'tar --no-same-owner --no-same-permissions --keep-old-files -xf controller.tar','find . -type d -exec chmod 700 {} +','find . -type f -exec sha256sum {} +'])
 result=ops.run('stage-controller',script,raw)
 for n,h in members.items():assert (h+'  ./'+n).encode() in result
 for round in ('R1','R2'):
  a=load(O/round/'BINDING.json');raw=(O/round/a['record_name']).read_bytes();path='/home/server01_cicd-runner/FDS_CICD_DeployInputs/'+a['record_name']
  script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = cicd-runner01','test "$(id -un)" = server01_cicd-runner','test "$(id -u)" = 1000','test ! -L /home/server01_cicd-runner/FDS_CICD_DeployInputs','test "$(stat -c %a /home/server01_cicd-runner/FDS_CICD_DeployInputs)" = 700','test ! -e '+path,'test ! -L '+path,'set -C','cat > '+path,'sha256sum '+path,'stat -c "%u|%a|%h" '+path])
  result=ops.run('stage-'+round,script,raw,runner=True);assert result.decode().split()[0]==a['record_sha256'] and '1000|600|1' in result.decode()
 # Exact normal control01 helper/contract supply before any old-image write.
 package=io.BytesIO()
 with tarfile.open(fileobj=package,mode='w') as t:
  for p in [B/'round4/console_restore_current.py',O/'recovery-contract.json']:
   data=p.read_bytes();i=tarfile.TarInfo(p.name);i.mode=0o600;i.size=len(data);t.addfile(i,io.BytesIO(data))
 raw=package.getvalue();dest='/home/server02/FDS_AC09_ConsoleRestore_20261015'
 script='\n'.join(['set -eu','umask 077','test "$(hostname -s)" = k8s-control01','test "$(id -un)" = server02','test ! -e '+dest,'test ! -L '+dest,'mkdir -m 700 '+dest,'cd '+dest,'set -C','cat > recovery.tar','test "$(sha256sum recovery.tar | cut -d " " -f 1)" = '+sha(raw),'tar --no-same-owner --no-same-permissions --keep-old-files -xf recovery.tar','sha256sum console_restore_current.py recovery-contract.json'])
 inner=ops.INNER.copy();inner[inner.index('/home/server01_ansible/.ssh/p1_ansible_ed25519')]='/home/server01_ansible/.ssh/id_ed25519';inner[-1]='server02@10.1.93.102'
 result=ops.run('stage-control01-recovery',shlex.join(inner+[shlex.join(['/bin/sh','-c',script])]),raw)
 for p in [B/'round4/console_restore_current.py',O/'recovery-contract.json']:assert sha(p.read_bytes()).encode() in result
 save(O/'STAGED.json',{'at_utc':now().isoformat(),'controller_members':len(members),'records':2,'recovery_ready':True})
def guard(round,mode):
 authorization();a=load(O/round/'BINDING.json')
 assert now()<(CUT if round=='R1' else dt.datetime.fromisoformat(a['expiry'])-dt.timedelta(seconds=640))
 assert gh('repos/321Team/infra-cicd/commits/main')['sha']==SOURCE
 x=gh('repos/321Team/infra-cicd/issues/comments/'+str(a['comment_id']));assert x['body'].encode()==(O/round/'approval.json').read_bytes() and x['user']['login']=='GWONUK'
 assert (O/'STAGED.json').exists()
 if mode=='true':assert load(O/round/'VALIDATION_PASS.json')['conclusion']=='success'
 return a
def observe(round,run,mode):
 a=load(O/round/'BINDING.json');source=(ROOT/'deliverables/phase1-deploy-preparation-20261013/read_deploy_run.py').read_text(encoding='utf-8')
 for old,new in [('5c2d8367f5b81875693165055234a30e5c69944e345c8ad8c5277ef30ebd8387',a['plan_sha256']),('11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50',a['record_sha256']),('2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7',SOURCE)]:
  assert source.count(old)==1;source=source.replace(old,new)
 path=O/round/'read_run.py'
 if path.exists():assert path.read_bytes()==source.encode()
 else:path.write_bytes(source.encode())
 label=round+'-read-'+str(run)+'-'+now().strftime('%H%M%S%f')
 r=collect.remote((label,'10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519',False,path,[str(run),mode]));assert r['rc']==0
 return label,load(O/label/'stdout.json')
def dispatch(round,mode):
 a=guard(round,mode);d=O/round/('dispatch-'+mode);d.mkdir(exist_ok=False)
 ep='repos/321Team/infra-cicd/actions/workflows/app-deploy.yml/runs?per_page=30'
 before=gh(ep);save(d/'before.json',before);assert all(r['status']=='completed' for r in before['workflow_runs'])
 ids={r['id'] for r in before['workflow_runs']}
 request={'ref':'main','inputs':{'record_name':a['record_name'],'record_sha256':a['record_sha256'],'execute':mode}}
 gh('repos/321Team/infra-cicd/actions/workflows/app-deploy.yml/dispatches','POST',request,round+'-dispatch-'+mode)
 for _ in range(15):
  found=[r for r in gh(ep)['workflow_runs'] if r['id'] not in ids and r['head_sha']==SOURCE and r['actor']['login']=='GWONUK']
  if found:
   assert len(found)==1 and found[0]['run_attempt']==1;save(d/'run.json',found[0]);print(json.dumps({'round':round,'mode':mode,'run':found[0]['id']}),flush=True);return found[0]['id']
  time.sleep(2)
 raise RuntimeError('RUN_UNKNOWN_NO_REDISPATCH')
def validate(round):
 run=dispatch(round,'false')
 for _ in range(25):
  result=gh(f'repos/321Team/infra-cicd/actions/runs/{run}')
  if result['status']=='completed':
   save(O/round/'VALIDATION_PASS.json',result);assert result['conclusion']=='success'
   label,x=observe(round,run,'false');assert len(x['matches'])==1
   actual=x['matches'][0]['files']['result.json']['data'];assert actual['PREFLIGHT']=='SUPPLIED_BYTES_MATCH' and actual['TOKEN_ISSUED'] is False
   print(json.dumps({'round':round,'false':'PASS','run_id':run}),flush=True);return
  time.sleep(2)
 raise RuntimeError('FALSE_NOT_COMPLETED_NO_REPEAT')
def execute(round):
 a=guard(round,'true')
 if round=='R2':assert load(O/'R1_READY_VERIFIED.json')['both_previous_ready'] is True
 run=dispatch(round,'true')
 for _ in range(20):
  label,x=observe(round,run,'true')
  if x['socket']['exists'] and x['matches']:break
  assert gh(f'repos/321Team/infra-cicd/actions/runs/{run}')['status']!='completed'
  time.sleep(2)
 else:raise RuntimeError('SOCKET_NOT_READY_NO_BROKER')
 guard(round,'true');assert x['socket']['is_socket'] and x['socket']['uid']==1000 and x['socket']['mode']=='0o600'
 scope=x['matches'][0]['files']['dispatch.json']['data']['binding']
 assert scope=={'execution':{'repository':'321Team/infra-cicd','ref':'refs/heads/main','workflow_sha':SOURCE,'run_id':run,'attempt':1},'record_sha256':a['record_sha256'],'plan_sha256':a['plan_sha256'],'sa_uid':SA}
 raw=(json.dumps(scope,sort_keys=True,separators=(',',':'))+'\n').encode();path=REMOTE+'/binding-'+str(run)+'.json';(O/round/'scope-binding.json').write_bytes(raw)
 script='\n'.join(['set -eu','umask 077','test ! -e '+path,'test ! -L '+path,'set -C','cat > '+path,'sha256sum '+path])
 assert sha(raw).encode() in ops.run('binding-'+str(run),script,raw)
 args=['/usr/bin/python3','-I','-B','-c','import sys; sys.path.insert(0,"tools/delivery"); import transfer_deploy_credential as t; raise SystemExit(t.main())','--bundle',REMOTE+'/native-source.bundle.json','--bundle-sha256',sha((B/'native-source.bundle.json').read_bytes()),'--source-sha',SOURCE,'--binding',path,'--binding-sha256',sha(raw)]
 result=json.loads(ops.run('broker-local-'+str(run),'cd '+REMOTE+' && '+shlex.join(args),timeout=40));assert result['TOKEN_ISSUED'] is False
 guard(round,'true')
 save(O/round/'BROKER_ATTEMPT.json',{'run':run,'at_utc':now().isoformat(),'max_token_requests':1,'automatic_retry':False})
 args+=['--execute','--authorization-expires',dt.datetime.fromisoformat(a['expiry']).astimezone(dt.timezone.utc).isoformat(),'--cp1-key','/home/server01_ansible/.ssh/id_ed25519','--runner-key','/home/server01_ansible/.ssh/p1_ansible_ed25519']
 status(f'{round} true Run{run}·Attempt1 시작. 기존 nativeRunner 연결·exactscope 확인, broker1회 실행. Token/PATCH/rollout 결과는 원본 대조 전 미확정. 자동재시도 없음.')
 ops.run('broker-execute-'+str(run),'cd '+REMOTE+' && '+shlex.join(args),timeout=90)
 print(json.dumps({'round':round,'broker_returned':True,'run':run,'rollout':'NOT_YET_READ'}),flush=True)
def broker_existing():
 round='R1';run=38693979785
 assert not (O/round/'BROKER_ATTEMPT.json').exists()
 metadata=load(O/'AUTHORIZATION_BINDINGS.json')[round]
 old=(O/round/'BINDING.json').read_bytes()
 assert load(O/round/'BINDING.json')['execution']['run_id']==run
 (O/round/'actual-scope-over-local-metadata.original.json').write_bytes(old)
 save(O/round/'BINDING.json',metadata)
 status('R1 Run38693979785のToken前ガード停止: WindowsのBINDING.json/binding.json衝突を原本保全・AUTHORIZATION_BINDINGS正本から復元。production/plan/approval/remote record不変、Token0/PATCH0。既存Jobのみ再確認し初回broker接続、再dispatchなし。')
 a=guard(round,'true');label,x=observe(round,run,'true')
 assert x['socket']['exists'] and len(x['matches'])==1 and 'result.json' not in x['matches'][0]['files']
 assert gh(f'repos/321Team/infra-cicd/actions/runs/{run}')['status']=='in_progress'
 scope=x['matches'][0]['files']['dispatch.json']['data']['binding'];assert scope==json.loads(old)
 raw=(json.dumps(scope,sort_keys=True,separators=(',',':'))+'\n').encode();path=REMOTE+'/binding-'+str(run)+'.json'
 args=['/usr/bin/python3','-I','-B','-c','import sys; sys.path.insert(0,"tools/delivery"); import transfer_deploy_credential as t; raise SystemExit(t.main())','--bundle',REMOTE+'/native-source.bundle.json','--bundle-sha256',sha((B/'native-source.bundle.json').read_bytes()),'--source-sha',SOURCE,'--binding',path,'--binding-sha256',sha(raw),'--execute','--authorization-expires',dt.datetime.fromisoformat(a['expiry']).astimezone(dt.timezone.utc).isoformat(),'--cp1-key','/home/server01_ansible/.ssh/id_ed25519','--runner-key','/home/server01_ansible/.ssh/p1_ansible_ed25519']
 assert now()<CUT-dt.timedelta(seconds=60)
 save(O/round/'BROKER_ATTEMPT.json',{'run':run,'at_utc':now().isoformat(),'max_token_requests':1,'automatic_retry':False,'continuation':'SAME_JOB_FIRST_TOKEN_AFTER_LOCAL_METADATA_REPAIR'})
 ops.run('broker-execute-'+str(run),'cd '+REMOTE+' && '+shlex.join(args),timeout=90)
if __name__=='__main__':
 action=sys.argv[1]
 if action=='fresh':fresh()
 elif action=='authorize':authorize()
 elif action=='stage':stage()
 elif action=='validate':validate(sys.argv[2])
 elif action=='execute':execute(sys.argv[2])
 elif action=='broker-existing':broker_existing()
 elif action=='observe':
  label,x=observe(sys.argv[2],int(sys.argv[3]),sys.argv[4]);print(json.dumps({'folder':label,'socket':x['socket'],'matches':x['matches']},ensure_ascii=False))
