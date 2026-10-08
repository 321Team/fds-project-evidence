# Issue9 후속 — 실제 후보 엔진 MON verify

CODEX_ASSISTED · 2026-10-08 KST. evidence148의 제어 서버 구문 증적을 인수·병합한 뒤, 독립적으로 실행 가능한 기존 MON 읽기 검증을 수행했다.

## 기준과 실제 결과

- source: infra-ansible `da4e273e7e26a9a0b51211e5146066960df072b5`, 기존 승인·병합된 wrapper/helper. 실제 wrapper header의 commit/tree=clean을 확인했다.
- 명령: 정상 ansible01/server01_ansible, 기존 candidate2.21.3, `scripts/cr-p1-mon-01-01-run.sh verify`. 운영 wrapper/role을 수정하지 않았다. `invoked-command.sh`는 실행에 사용한 셸 명령 보존본이며 새 승인 실행기가 아니다.
- inventory graph는 egress-proxy01 한 대(10.1.93.56), playbook의 localhost는 빈 inventory 차단용 guard다. worker01/control-plane 실행은 없다.
- 서버 원문 run_id `20261008T005332+0900_14923`, 실행 header00:53:34 / footer00:53:41 KST. local invocation 시각00:53:31.279~00:53:40.428은 별도 시계이며 서버 시각으로 덮어쓰지 않았다. 작은 시계 차이를 0으로 보정하지 않는다.
- egress-proxy01 recap ok26/changed0/unreachable0/failed0/skipped28/rescued0/ignored0, localhost ok1/changed0. 서버 footer rc0 및 별도 operator.rc0.
- Squid loaded/active, 현재 실행 내 및 기존 저장 baseline 대비 kubelet 회귀 없음, discord.com HTTPS proxy HTTP200, example.com CONNECT403 assert 통과.
- baseline 파일 존재(root:root0600,777bytes)는 사전 stat으로 확인했고 실제 내용/host/change/kubelet 조건은 기존 verify task에서 확인했다. 사전 stat만으로 적합성을 인정하지 않았다.
- write/설치/방화벽 추가/서비스 시작·reload는 `cr_mon_phase == 'apply'`에 한정되는 소스를 실행 전 대조했다. 이번 phase=verify에서 해당 분기는 skip이다. changed0은 이 회차의 태스크 결과이며 서버 전체 바이트 불변 감사로 확대하지 않는다.

## 증적과 범위

서버 원본 `RECEIPT.json`의 server_log, SHA256 `701b24989041a4a252117cd27b74758c8e817c4d736d128b4146d61b1e2fb22b`. 회수 전후 서버 sha256sum과 수신 raw 바이트가 일치한다. 서버 로그 및 desktop SSH stdout/rc를 별도 보존했다.
Git 원문의 inventory/hosts.yml + inventory/group_vars/all.yml 연결 바이트 SHA256은 `4493fef29c46c0d697e32d777350054392bc4d5301b92468179a2311a5641f7e`로 wrapper header와 일치한다.
원본과 작업 디렉터리는 보존한다. 비밀값·개인키 내용은 읽거나 첨부하지 않았다. 기존 key 경로는 wrapper에 지정했으며 SSH는 기존 키를 인증에 사용했다.

CONTROLLER_NATIVE_SYNTAX=PASS(evidence148), MON_VERIFY_CANDIDATE=PASS(이번 회차).
MON apply/멱등성/rollback, DNS/NTP wrapper 실제 역할 실행, Gate0 check/run, 전역 운영 엔진 전환, Issue9 전체 인수는 NOT_RUN/PENDING이다.

## 후속 실행 범위와 우선순위

| 순서 | 범위 | 필요한 조건 / 이번 상태 |
|---|---|---|
| 1 | MON verify | 기존 wrapper와 후보 엔진의 단일 egress-proxy 읽기 검증 완료. 같은 입력 재실행 불필요 |
| 2 | 역할별 변경·복구 계획 | 원래 목적의 변경 필요성·기존 승인/백업과 복구 범위를 먼저 확정. 엔진 시험만을 위해 정상 서비스를 변경하거나 예전 원본 baseline으로 rollback하지 않음 |
| 3 | DNS 경로 | precheck/verify는 k8s_nodes6대, workers는3대, control-plane은control02/03. worker01 제외 조건과 충돌하므로 기존 worker02 canary를 대입하지 않음 |
| 4 | NTP 경로 | source는control01, clients는control02/03+workers, verify는전체6대. 실제 lock/FD와 source/runtime-vars binding·NTP 선행 Gate 유지. 다른 세션의 변경과 분리 |
| 5 | Gate0 check/run | k8s_nodes 전체6대·교차노드 검사. syntax PASS를 노드 동작 PASS로 바꾸지 않음. 현재 worker01 제외 범위와 대상 승인 정합화 필요 |
| 6 | 운영 엔진 전환 | 위 역할별 검증 및 호출 경로 범위가 충족된 후 결정. 기본 /usr/bin/ansible2.16.19·전역 PATH/RPM 유지 |

모든 다음 역할 실행은 대상·action·현재 source·승인 범위·실행창·중단/복구를 먼저 고정한다. 추가 현장 수집/실행 자동화가 필요하면 먼저 source PR에 포함해 검토한다는 evidence148 리뷰 권고를 적용한다. 이미 승인된 이번 MON wrapper는 수정하지 않고 사용했다.
인증/기준선/대상 불일치, FAIL/unreachable/timeout이면 중단한다. baseline 생성·권한 확대·apply/rollback 자동 전환·자동 재시도는 하지 않는다.

[착수 및148병합 기록](https://github.com/321Team/infra-ansible/issues/9#issuecomment-6041563024). 이번 실행은 종료됐고 추가 역할 실행으로 창을 연장하지 않는다.
