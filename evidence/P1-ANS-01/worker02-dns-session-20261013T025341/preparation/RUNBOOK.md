# DNS 한정 회차 명령 카드

실행 위치: ansible01 / server01_ansible. 본문 값을 통째로 붙여 넣어 일괄 실행하지 않고 각 행위의 rc/원 로그/백업 SHA를 확인한 뒤 진행한다. 준비 단계에는 아래 명령을 실행하지 않았다. 현장 NM 작성자 배제·콘솔·Harbor 비중첩을 확인해야 한다.

```bash
cd '/home/server01_ansible/worker02-session-plan-3hetha3t/source'
export LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1
export FDS_ANSIBLE_ENGINE_DIR='/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin'
export FDS_ANSIBLE_ENGINE_VERSION=2.21.3
export ANSIBLE_PRIVATE_KEY_FILE=/home/server01_ansible/.ssh/p1_ansible_ed25519
export CR_CHANGE_APPROVED=CR-P1-ANS-01-01
export CR_DNS_SOURCE_SHA=0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea
export CR_EVIDENCE_DIR='/home/server01_ansible/p1-worker02-dns-20261013-r1/logs'
session_id='w02-20261013T024523-85942d67'
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
