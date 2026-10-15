"""Read-only final absence/current state checks; record this executor's return."""
import concurrent.futures,contextlib,io,json,shlex
import runtime as r
assert r.now()>r.now().fromisoformat('2026-10-15T16:04:25+09:00')
assert (r.O/'EXACT_CLEANUP_RECEIPT.json').exists()
bundle=r.load(r.B/'native-source.bundle.json')['files']
hashes={n:r.sha(v['content'].encode()) for n,v in bundle.items()}
tasks=[]
for role in ['ansible','control01','runner']:
 inv=r.load(r.O/'cleanup-inventory-ansible.json') if role=='ansible' else r.load(r.O/('cleanup-inventory-'+role)/'stdout.json')
 for d in inv['public_source_dirs_retained']:
  assert {x['path'].split('/')[-1]:x['sha256'] for x in d['files']}==hashes
 code='''import datetime as dt,hashlib,json,os,pathlib,pwd,socket
v=INV;expected=HASHES
assert socket.gethostname()==v['host'] and pwd.getpwuid(os.getuid()).pw_name==v['user']
now=dt.datetime.now(dt.timezone.utc)
assert now>dt.datetime.fromisoformat('2026-10-15T16:04:25+09:00')
assert all(not pathlib.Path(x).exists() and not pathlib.Path(x).is_symlink() for x in v['roots'])
public=[]
for d in v['public_source_dirs_retained']:
 p=pathlib.Path(d['root']['path']);assert not p.is_symlink() and p.is_dir()
 assert {x.name for x in p.iterdir()}==set(expected)
 for x in p.iterdir():assert not x.is_symlink() and hashlib.sha256(x.read_bytes()).hexdigest()==expected[x.name]
 public.append(str(p))
workers=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  if (p/'comm').read_text().strip()=='Runner.Worker':workers.append(int(p.name))
 except (FileNotFoundError,PermissionError):pass
assert not workers
sockets={}
if v['host']=='cicd-runner01':
 sockets={str(n):(pathlib.Path.home()/'FDS_DeploySockets'/('r'+str(n)+'.sock')).exists() for n in [38693979785,38694721511]};assert not any(sockets.values())
print(json.dumps({'host':v['host'],'at_utc':now.isoformat(),'supplied_roots_absent':True,'public_source_dirs_retained_hash_matched':public,'runner_worker':workers,'sockets':sockets,'token_expiration_timestamp_passed':True,'expired_token_auth_test':'NOT_EXECUTED','revocation':'NOT_PERFORMED'}))
'''.replace('INV',repr(inv)).replace('HASHES',repr(hashes))
 p=r.O/('return-'+role+'.py');p.write_bytes(code.encode());compile(code,str(p),'exec')
 if role=='ansible':
  with contextlib.redirect_stdout(io.StringIO()):raw=r.ops.run('return-read-ansible',shlex.join(['/usr/bin/python3','-B','-I','-S','-']),code.encode())
  r.save(r.O/'return-ansible.json',json.loads(raw))
 else:
  host,user,key=('10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519') if role=='control01' else ('10.250.10.20','server01_cicd-runner','/home/server01_ansible/.ssh/p1_ansible_ed25519')
  tasks.append(('return-'+role,host,user,key,False,p,[]))
tasks.append(('return-current-state','10.1.93.102','server02','/home/server01_ansible/.ssh/id_ed25519',False,r.O/'state_read.py',[]))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:results=list(p.map(r.collect.remote,tasks))
assert all(x['rc']==0 for x in results)
state=r.load(r.O/'return-current-state/stdout.json');prior=r.load(r.O/'r2-final-state/stdout.json')
for a,b in zip(state['deployments'],prior['deployments']):
 assert all(a[k]==b[k] for k in ['name','uid','generation','image','normalized_spec_sha256'])
 assert all(a['status'][k]==3 for k in ['replicas','updatedReplicas','readyReplicas','availableReplicas'])
assert len(state['pods'])==6 and {p['uid'] for p in state['pods']}=={p['uid'] for p in prior['pods']}
assert all(p['deletionTimestamp'] is None and all(c['ready'] and c['restartCount']==0 for c in p['containers']) for p in state['pods'])
current=r.gh('repos/321Team/infra-cicd/actions/runs?per_page=30',label='return-recent-runs')
active=[{'id':x['id'],'status':x['status']} for x in current['workflow_runs'] if x['status']!='completed']
assert not active,active
at=r.now().astimezone(r.START.tzinfo).isoformat()
result={'returned_at_kst':at,'scope':'CICD_AC09_SINGLE_EXECUTOR','runtime_complete':True,'acceptance_complete':False,'current_ready':{'transaction-api':3,'fds-engine':3},'old_pods':0,'restart_count':0,'runner_worker':0,'own_sockets':0,'latest30_runs_active':active,'supplied_roots_absent':True,'token_expiry_timestamps_passed':True,'token_live_auth_expiry_test':'NOT_EXECUTED','server_revocation':'NOT_PERFORMED','counts':{'false_jobs':2,'true_jobs':2,'new_runner':0,'token_requests':2,'deposit_posts':2,'edge_extra_gets':4,'manual_recovery_patch':0},'remaining':['DB same-ID row verification NOT_COLLECTED','Timing strict interval proof pending SEC post-review','Independent evidence review / AC09 acceptance'],'next_runtime_owner':'CENTRAL_MUST_ASSIGN; this record does not dispatch other work'}
r.save(r.O/'WINDOW_RETURN.json',result)
r.status(f'**CICD AC09 단독 실행 종료·창 반환 가능 — {at}.** R1/R2 및 false2/true2 모두 success. 현행 각Ready3/동일Pod6·restart0·이전Pod0, Runner Worker0·해당 소켓0·최근30Run active0 재확인. 이번 공급 경로·입력 파일은 원본/해시 보존 후 제거했고, 공개 native source8경로·claim/checkpoint는 증적으로 유지했다. 토큰 명시 만료15:58:14/16:04:25 경과 확인(강제폐기/만료인증시험 아님). 두 최소POST HTTP201·계수각+1/오류0. 추가Runtime 없이 중앙에 반환한다. **AC09 최종 인수 미완료:** DB 동일ID행 미수집, 엄격 시한 입증은 SEC 사후검토. 원시 관측은 첫현행PATCH상한 P+371.114초/복원관측상한 P+500.490초이나 회차전체시계오차 E는UNPROVEN. [결과](../p1-cicd-ac09-preparation-20261015/runtime-1535/RUNTIME_RESULT.md) / [반환영수증](../p1-cicd-ac09-preparation-20261015/runtime-1535/WINDOW_RETURN.json). 중앙 공통대장·다른담당 파일 수정0, 타세션에 실행지시 메시지0.')
print(json.dumps(result,ensure_ascii=False))
