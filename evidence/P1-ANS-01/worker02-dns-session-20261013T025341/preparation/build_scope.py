from pathlib import Path
import datetime as dt,hashlib,json,secrets,subprocess
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_bytes())
def put(n,s):(P/n).write_bytes(s.encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
worker=read('worker02-fresh-read/stdout.json');controller=read('controller-fresh-read/stdout.json');cluster=read('cluster-before/stdout.json');binding=read('SOURCE_BINDING.json')
assert worker['success'] and controller['status']=='PRECHECK_VERIFIED' and cluster['status']=='CLUSTER_BINDING_VERIFIED'
assert worker['commands'][2]['stdout']=='10.1.93.52,10.1.93.53\nfds.internal\nyes\n'
assert worker['resolv_conf_selected']==['search fds.internal','nameserver 10.1.93.52','nameserver 10.1.93.53']
for c in worker['commands']:
 assert c['rc']==0
 if c['argv'][:2]==['getent','ahostsv4'] and c['argv'][-1]!='github.com':assert '10.1.93.109' in c['stdout']
 if c['argv'][0]=='dig':assert c['stdout'].splitlines()==['10.1.93.109']
for n in ['worker02-fresh-read','controller-fresh-read','cluster-before','worker02-network-before']:
 r=read(n+'/receipt.json');assert r['rc']==0
 for name,key in [('collector.py','source_sha256'),('stdout.json','stdout_sha256'),('stderr.txt','stderr_sha256')]:assert sha(P/n/name)==r[key]
for n,h in binding['hashes'].items():assert sha(P/'approved-source'/n)==h
refs={}
for name,path in [('pr76','repos/321Team/infra-ansible/pulls/76'),('reviews76','repos/321Team/infra-ansible/pulls/76/reviews'),('checks76','repos/321Team/infra-ansible/commits/'+binding['head']+'/check-runs')]:
 r=subprocess.run(['gh','api',path],capture_output=True,check=True);(P/(name+'.json')).write_bytes(r.stdout);refs[name]=json.loads(r.stdout)
assert refs['pr76']['merged'] and refs['pr76']['head']['sha']==binding['head']
assert any(r['user']['login']=='hayeounglee' and r['state']=='APPROVED' and r['commit_id']==binding['head'] for r in refs['reviews76'])
assert any(c['name']=='regression' and c['conclusion']=='success' for c in refs['checks76']['check_runs'])
kst=dt.timezone(dt.timedelta(hours=9));now=dt.datetime.now(kst);sid='w02-'+now.strftime('%Y%m%dT%H%M%S')+'-'+secrets.token_hex(4)
plan={'prepared_at_kst':now.isoformat(),'session_id':sid,'source_sha':binding['head'],'source_root':controller['root'],'engine':controller['engine'],'engine_version':'2.21.3','host':'k8s-worker02','endpoint':'10.1.93.107','interface':worker['interface'],'connection':worker['connection'],'boot':worker['boot'],'dns':['10.1.93.52','10.1.93.53'],'search':['fds.internal'],'ignore_auto_dns':True,'controller_evidence_root':'/home/server01_ansible/p1-worker02-dns-20261013-r1','remote_backup':'/var/lib/fds-change/CR-P1-ANS-01-01/worker02-sessions/'+sid+'/original-resolver.json','snapshot_sha256':None,'actions':['prepare','apply-check','apply','reapply','rollback-check','rollback','fresh-read'],'runtime_started':False,'nm_writer_exclusion_confirmed':False,'console_confirmed_for_dns_round':False,'new_lead_implementation_go_required':False,'per_step_timeout_seconds':180,'first_apply_max_snapshot_age_seconds':900,'maximum_session_minutes':15,'artificial_drift':False,'global_engine_switch':False,'ac_accepted':False}
put('EXECUTION_INPUT.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
scope=f'''# worker02 DNS 후보 엔진 한정 회차 — 실행 범위

2026-10-13 / 이권욱 / CODEX_ASSISTED. 상태: **실행 준비·읽기 검증 완료, 새 백업/prepare/apply/reapply/rollback 미실행**. 이번 사용자 “착수”에 따라 기존 권장 순서의 다음 항목을 구체화했다. Phase1이며 신규 Lead 구현 GO나 반복 독립 코드 리뷰는 추가하지 않는다.

## 현재 확인

- 02:42 KST worker02 `ens160` / `fds-k8s-worker02`, DNS `.52,.53`, search `fds.internal`, ignore-auto-dns=yes. live resolver도 동일하다. 내부 FQDN/short-name→`.109`, DNS2대 직접 질의, 외부 github.com 해석, `.109:6443` TCP 정상.
- NetworkManager/kubelet/containerd active, SELinux Enforcing. Node6·시스템Pod3·앱Pod6 Ready, 앱별 Worker3대1/1/1. 대상 연결 UUID·주소/경로 및 서비스 PID/진입시각을 별도 보존했다. 이후 시점은 실행 직전 재대조한다.
- [PR76](https://github.com/321Team/infra-ansible/pull/76) HEAD `{binding['head']}`의 이하영 독립 코드 승인·병합·[CI SUCCESS](https://github.com/321Team/infra-ansible/actions/runs/37895578228/job/113706062449) 확인. ansible01의 기존 고정 checkout이 이 HEAD, tracked 변경0·실행경로 untracked0·필수11파일 SHA 일치. 명시적 후보 CLI4종 모두2.21.3.
- 기존 소스의 rollback은 **현재값=원본이어도 `connection modify`와 `device reapply`를 실행**한다. PR76의 알려진 비차단 의견이며 새 발견/새 차단으로 반복 리뷰하지 않는다. 동일값 복구 실행을 실제 장애 복원 성공으로 표기하지 않는다.

## 이번 실행 범위

1. 기존 ansible01/server01_ansible → worker02/svc_ansible+sudo, pinned SSH 키·host-key와 승인 source/2.21.3 절대경로를 사용한다. 새 credential·RPM·전역 PATH/엔진 변경 없음.
2. 새 회차 `{sid}`를 사용한다. controller 새0700 `{plan['controller_evidence_root']}`에 로그, worker02 새 root0700 회차 경로에0600 `original-resolver.json`을 독점 생성한다. 기존 최초 CR 백업·다른 회차를 덮어쓰지 않는다.
3. **prepare → apply check-mode → apply → reapply → rollback check-mode → rollback → 신규 SSH/사후 확인**, 각 단계 성공을 확인하고 순차 실행한다. prepare가 반환한 백업 SHA를 외부 보존·고정하고 이후 호출마다 같은 값을 전달한다. 최초 apply는 백업 생성15분 이내다.
4. 현재 사전값=목표값이므로 apply/reapply의 DNS 변경0이 예상된다. 달라지면 계획 밖 drift로 중단한다. **고의 DNS 장애·drift를 만들지 않는다.** 마지막 rollback은 검증된 동일 원본값을 다시 설정·연결 재적용하는 실제 명령 경로1회로 분류한다. `down/up`, 노드 재부팅, Pod/정책/서비스 변경·전체 Worker 실행은 없다.
5. 사후 persistent/live DNS·내부/외부 해석·직접 DNS2대/API·신규 SSH, NM/kubelet/containerd·주소/경로·Pod/Deployment 보존을 확인한다. 성공하면 기존 PR208에 증적을 합치고 기존 리뷰어를 유지한다. AC/엔진 전체 전환/티켓 종결은 자동 완료하지 않는다.

## 현장 조건·영향·중단

필수 현장 조건은 **worker02 NetworkManager/DNS 동시 변경 배제와 해당 콘솔 복구 인수 가용성**이다. 앞선 이미지 import와 K8S 파일 호출 배제는 이 NM 변경 배제의 증거로 전용하지 않는다. Harbor 변경·사후 관측과는 실제 시작 직전에 다시 비중첩을 확인한다. 이는 새 Lead 판단을 요구하는 절차가 아니다.

동일값이라도 device reapply는 실노드의 네트워크 관리 명령이므로 연결/해석의 일시 영향 가능성을0으로 단정하지 않는다. 새 백업과 현재 상태를 콘솔에서 비교할 수 있어야 한다. 단계당180초, 전체15분 한도이며 timeout/실패/unreachable/예상외changed/소스·연결·값 drift/백업 불일치면 다음 단계0, 자동 재시도0. timeout은 원격 실행 종료나 원복 완료의 증거가 아니므로 진행 프로세스와 실제 상태부터 읽는다.

적용 중 실패하면 기존 role의 해당 호출 사전값 rescue 결과를 확인한다. 수동 복구는 검증된 회차 백업으로 현재값이 원본/목표 중 하나이고 동일 interface/connection일 때만 허용된다. 다른 drift나 연결 손실은 콘솔 인수로 넘긴다. 키 제한·SELinux·방화벽을 해제하거나 원본을 삭제/교체하지 않는다. 같은 값의 rollback 성공은 실패상태 복구/엔진 전체 호환/HA 인수를 증명하지 않는다.

[고정 입력](EXECUTION_INPUT.json), [명령 카드](RUNBOOK.md), [준비 검증](PREPARATION_VERIFICATION.json). 사용자의 현장 조건 확인 전에는 prepare의15분 유효시간을 시작하지 않는다.
'''
put('EXECUTION_SCOPE.md',scope)
runbook=f'''# DNS 한정 회차 명령 카드

실행 위치: ansible01 / server01_ansible. 본문 값을 통째로 붙여 넣어 일괄 실행하지 않고 각 행위의 rc/원 로그/백업 SHA를 확인한 뒤 진행한다. 준비 단계에는 아래 명령을 실행하지 않았다. 현장 NM 작성자 배제·콘솔·Harbor 비중첩을 확인해야 한다.

```bash
cd '{controller['root']}'
export LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1
export FDS_ANSIBLE_ENGINE_DIR='{controller['engine']}'
export FDS_ANSIBLE_ENGINE_VERSION=2.21.3
export ANSIBLE_PRIVATE_KEY_FILE=/home/server01_ansible/.ssh/p1_ansible_ed25519
export CR_CHANGE_APPROVED=CR-P1-ANS-01-01
export CR_DNS_SOURCE_SHA={binding['head']}
export CR_EVIDENCE_DIR='{plan['controller_evidence_root']}/logs'
session_id='{sid}'
```

외부 controller evidence parent는 **없음을 확인한 새0700 경로만** 만든다. 기존 경로면 덮어쓰거나 권한을 바꾸지 않고 중단한다. wrapper는 prepare를 포함해 각 호출의 별도 로그를 남긴다. rc0 외에 worker02 단독·failed/unreachable0·백업 영수증까지 확인한다.

```bash
CR_DNS_SESSION_APPROVED="$session_id:prepare" CR_DNS_CHECK_ONLY=0 bash scripts/cr-p1-ans-01-01-run.sh worker02-session prepare "$session_id"
```

prepare의 `snapshot_written=true`·회차/source/path/sha256을 수신한다. 출력과0600 실제 백업을 읽어 SHA를 대조하고 외부 영수증에 저장한 **그 SHA**를 `snapshot_sha`에 넣는다. 나중에 재계산한 값을 자동채택하지 않는다. source code의 파일 생성 changed1은 DNS 변경1이 아니다.

```bash
snapshot_sha='<prepare에서 외부 보존한 64자리 SHA>'
CR_DNS_SESSION_APPROVED="$session_id:apply" CR_DNS_CHECK_ONLY=1 bash scripts/cr-p1-ans-01-01-run.sh worker02-session apply "$session_id" "$snapshot_sha"
```

check 결과 drift=false·관리 변경0·failed/unreachable0과 현재 원본 유지가 확인됐을 때만 아래 **한 행씩** 진행한다. 최초 apply가15분 유효시간을 넘으면 같은 회차를 강행하지 않는다.

```bash
CR_DNS_SESSION_APPROVED="$session_id:apply" CR_DNS_CHECK_ONLY=0 bash scripts/cr-p1-ans-01-01-run.sh worker02-session apply "$session_id" "$snapshot_sha"
CR_DNS_SESSION_APPROVED="$session_id:reapply" CR_DNS_CHECK_ONLY=0 bash scripts/cr-p1-ans-01-01-run.sh worker02-session reapply "$session_id" "$snapshot_sha"
CR_DNS_SESSION_APPROVED="$session_id:rollback" CR_DNS_CHECK_ONLY=1 bash scripts/cr-p1-ans-01-01-run.sh worker02-session rollback "$session_id" "$snapshot_sha"
CR_DNS_SESSION_APPROVED="$session_id:rollback" CR_DNS_CHECK_ONLY=0 bash scripts/cr-p1-ans-01-01-run.sh worker02-session rollback "$session_id" "$snapshot_sha"
```

apply/reapply는 관리 변경0 예상. rollback의 modify/reapply 태스크는 동일 원본값에도changed로 보고되며 **무변경 재적용과 구분**한다. check-only rollback은 바인딩 검증일 뿐 복구 성공이 아니다. 실패면 다음 행위를 실행하지 않는다. 자동rescue가 이미 진행됐다면 결과를 먼저 확인하고 중복 복구하지 않는다.

사후 수집: 새 strict SSH 연결로 worker02 DNS/주소·경로/서비스 및 이름 해석/API TCP를 재조회하고 control01에서 Node6/시스템Pod3/앱Pod6·배치/UID/spec/restart를 대조한다. 기존 조회 collector와 새receipt를 사용하며 이전영수증을 덮어쓰지 않는다. source·명령·rc·시각·원로그·SHA를 보존한다. timeout/연결손실이면 결과불명 상태로 콘솔 인수하고 자동재시도하지 않는다. 회차 backup과로그는 보존한다.
'''
put('RUNBOOK.md',runbook)
verification={'status':'READY_FOR_FIELD_CONDITION_CONFIRMATION','read_receipts':4,'source_files_verified':len(binding['hashes']),'source':binding['head'],'review':'PR76 APPROVED hayeounglee exact head','ci':'PR76 regression success','dns_values_already_target':True,'node_ready':6,'system_pod_ready':3,'app_pod_ready':6,'dns_write_or_session_prepare_executed':False,'console_and_nm_writer_exclusion_for_this_round':'NOT_CONFIRMED','scope_sha256':sha(P/'EXECUTION_SCOPE.md'),'runbook_sha256':sha(P/'RUNBOOK.md')}
put('PREPARATION_VERIFICATION.json',json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
put('CURRENT_EXECUTION_STATUS.md',f'# {now.isoformat()} — DNS 실제 회차 준비 완료\n\nworker02·controller·cluster·네트워크 보존4읽기 rc0. 승인source11파일/2.21.3/PR76승인·CI 확인. 현재=목표 DNS. 새백업/prepare/변경0. 이번 회차 NM동시변경배제·콘솔 확인 대기.\n')
print(json.dumps(verification,ensure_ascii=False))
