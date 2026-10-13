# Deploy 실행 결과 및 시작 마감에 따른 보류 — 2026-10-13 KST

AI 사용: CODEX_ASSISTED · 실행자 이권욱의 승인 범위 내 보조.

**판정: 사전검사 SUCCESS, 실제 true Run FAILURE, 추가 Run NOT DISPATCHED. Deploy/Delivery/최종 인수 PASS가 아니다.**

## 승인과 실행 범위

- 승인된 창은 16:15~17:00 KST이며 새 Run 시작 마감은 16:30이었다. 두 앱의 지정 새 digest 적용과 실패 시 지정 이전 digest 복귀만 포함했다. HA/drain/reboot/APP·DB 최종 인수는 제외했다.
- [독립 입력 검토](https://github.com/321Team/fds-project-evidence/pull/213#pullrequestreview-5499902059)는 HEAD `5c4f6b6ee469697d96249b525d35acd4edaf9261`의 exact record `11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50`에 대한 사용 동의다. 이후 증적/설명 추가를 이 승인으로 확대하지 않는다.
- [원 승인 JSON](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6140076685), plan, record는 변경하지 않았다. source는 `infra-cicd@2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`; 앱 source `affbc69beef9967f7977d09a6fec14f7fb6c0e94` 및 성공 Push Run38318968352를 재사용했다.
- 사용자는 추가 질문에 **“새 Run 추가 1회 허용”**이라고 답했다. 질문에는 원 종료 17:00 및 **16:30까지 시작할 수 있을 때만**이라는 조건이 포함되어 있었다. 답변 처리 직후 clock 조회가 **16:30:14 KST**였으므로 추가 Run을 dispatch하지 않았다. 이 시각은 처리 시 조회값이며 사용자의 답변 도착 시각을 단정하지 않는다. 16:35:32 재조회도 마감 경과였다. 승인 횟수 증가는 시작 마감 연장으로 해석하지 않았다.

## 실제 수행

| 단계 | 시각 KST | 결과와 근거 |
|---|---|---|
| 실행 전 재조회 | 16:12~16:15 | 두 앱/SA/CA 일치, Harbor HTTPS ping·health 200/8 healthy, 기존 작업의 Runtime 종료 확인. `fresh-071215`, `health-071215`, `EXECUTION_ENTRY_CHECK.json` |
| 준비 파일 배치 | 16:15:49~16:16:03 | Ansible controller tar·13개 파일 해시 일치, Runner record SHA 일치. 디렉터리0700/파일0600. `operations/stage-*` |
| false 사전검사 | Run38361678189/Attempt1 | [SUCCESS](https://github.com/321Team/infra-cicd/actions/runs/38361678189), `PREFLIGHT=SUPPLIED_BYTES_MATCH`, `TOKEN_ISSUED=false`, `DEPLOY=NOT_EXECUTED`, `APPROVAL_REFERENCE=NOT_VERIFIED`. result SHA `2c9c415cbf0bf90e163d136effcc7d071ccefe833b6bd042eba36f11d3162e35` |
| true 실행 | Run38361855044/Attempt1 | [FAILURE](https://github.com/321Team/infra-cicd/actions/runs/38361855044), 인증 전달 단계 16:18:48~16:20:48의 120초 대기 만료. result `MANUAL_RECONCILIATION_REQUIRED`/`DEPLOY_HANDOFF_UNCONFIRMED`/`DEPLOY=NOT_CONFIRMED`, SHA `7494b3ffd54085ee0230d371660dd4c9937829740bcc92dc994d60c9c4a33653` |
| 첫 broker 실행 | 16:19:01 | 실행자가 준비한 CLI 종료 인자가 `2026-10-13T17:00:00+09:00`였다. 기존 UTC-only 검사에 맞지 않았다. `operations/broker-execute-*`, `BROKER_TIME_DIAGNOSIS.json` |
| 동일 Run broker 정정 호출 | 16:20:51 | 같은 종료 순간을 `2026-10-13T08:00:00+00:00`로 표기했으나 Runner 연결 대기 종료 뒤였다. 추가 Workflow Run은 아니다. 두 broker 출력 모두 `TOKEN_ISSUANCE=NOT_CONFIRMED`, `HANDOFF=NOT_CONFIRMED`/rc1 그대로 보존 |
| 사후 상태 대조 | 16:21:51~16:28:35 | socket 부재, 해당 plan claim/checkpoint0, 앱 두 Deployment의 UID/spec/image/RV/generation 유지·각 Ready/Available/Updated3. 마지막 Pod 조회는 6개 Running/Ready. `runtime-reads/072149980833`, `fresh-072150`, `app-post-attempt` |
| CP1 발급 전 진단 | 16:23:49 | 기존 staged source7개 hash 확인 후 NativeAccess·SA·SelfSubjectAccessReview `PREISSUE_PREFLIGHT_PASS`. 진단은 `issue()`/`review()`를 호출하지 않았다. `preissue-diagnosis` |
| 추가 Run | 마감 이후 | 사용자 추가 1회 승인 기록, **NOT DISPATCHED**. `WORKFLOW_RUNS_AT_CLOSEOUT.json`에도 기존 false/true 두 Run만 존재 |

## 실패 원인과 원본/판단의 구분

첫 broker의 UTC 표기 오류는 Codex가 준비한 실행 명령의 오류다. 승인 record나 배포 source를 변경할 사유로 처리하지 않는다. 동일 source의 `deploy_native_probe.expiry/Window`로 `UTC_EXPIRY_REQUIRED`를 로컬 재현했고, `transfer_deploy_credential.execute`는 Window 검증 후에 CP1 Session과 Runner Bridge를 만든다. 첫 호출은 SSH/발급 이전 검사에서 실패한 것으로 판단한다.

정정 호출은 Runner step 종료 3초 뒤 시작했다. 승인 구현에서 `deploy_handoff.relay`는 Runner의 `deploy-ready`와 binding을 확인한 뒤에만 CP1에 `issue-once`를 보낸다. 이 순서, 실패 시각, socket/claim 부재를 대조하면 이번 두 호출에서 토큰 발급 경로에 진입하지 않았다고 판단한다. **서버 audit 전수 조회로 발급 0을 증명한 것은 아니다.** 원 broker `TOKEN_ISSUANCE=NOT_CONFIRMED`, `ENDPOINT_CLEANUP=NOT_CONFIRMED`, `server_revocation=NOT_PERFORMED`는 변경하지 않는다. CP1 진단 PASS도 과거 발급 여부를 증명하지 않는다.

관측된 Deployment 형상은 이전과 같고 rollout/rollback 수행 증적은 없다. Pod의 worker02 두 컨테이너는 현재 restartCount1, 나머지는0이다. 실행 직전 Pod별 restartCount 대조 자료가 없어 이번 창 재시작0으로 확대하지 않는다. 앱 가용성과 현재 형상 조회는 HTTP/업무 회귀 성공을 의미하지 않는다.

## 원본과 검증 범위

- `dispatch-false/`, `dispatch-true/`: workflow_dispatch 요청·응답, 실제 Run/Job 메타데이터, 원본 job log와 해시. 이 폴더의 요청 파일은 과거 실행 입력이며 재실행 지시가 아니다.
- `operations/`: 당시 명령 문자열·rc·시각·stdout/stderr 원본. `broker-execute`는 최초 잘못된 UTC 표기도 원문 그대로 남겼다. 현재 수정된 로컬 orchestrator를 과거 실행본으로 복사하지 않았다.
- `runtime-reads/`: 당시 수집기와 결과. 원본 result/dispatch bytes는 base64 및 SHA256로 보존한다. `selected-original-receipts/`는 이 bytes를 그대로 추출했으며 대응표는 `RECEIPT_VERIFICATION.json`에 있다.
- `fresh-*`, `health-*`, `preissue-diagnosis`, `app-post-attempt`: 제한된 읽기 조회의 collector, rc, 시각, 필터링된 출력. 원격 collector는 `REVIEW=NOT PERFORMED (Pre-check)`이며 실행 source 독립 승인과 구분한다. 원본 Kubernetes 응답 전체가 아니라 선택 필드와 원 응답 해시다.
- 파일·원본 해시 대조는 무결성 검사다. 테스트나 Deploy 성공으로 간주하지 않는다. 이 증적 편입의 최신 HEAD 독립 REVIEW/MERGE는 별도로 필요하다.

## 보존과 다음 완료조건

Ansible의 `/home/server01_ansible/FDS_CICD_DeployController.2fb09791-d0ca-443f-9c1b-77747c3f3a73`, Runner 입력 record와 두 실행 결과 디렉터리, CP1 staged source `/home/server02/FDS_NativeProbeSource.5qtjnwf3`를 보존했다. 해당 plan claim 삭제, token/server 강제 회수, 서버 파일 정리는 수행하지 않았다. claim은 관측 시 없었으며 socket은 Workflow가 닫은 것으로 관측됐다.

다음 실제 Deploy는 **새 시작 가능 시간의 명시적 조정**이 필요하다. 기존 승인 창이 만료되면 새 시간창에 맞는 plan/approval/record 결속과 필요한 독립 입력 검토를 다시 준비한다. 현재 명령카드는 오늘의 종료 순간을 보존한 정정본이며 다른 창으로 자동 재사용하지 않는다. 실행 전 UTC Window 인자 검증과 Harbor 비중첩·source/현재 대상·credential 경계 확인을 dispatch 전에 끝내고, 실제 Run binding을 만든 후 120초 내 연결해야 한다. 실패 시 자동 재실행하지 않는다.

배포 성공 이후 최종 형상 확인→별도 승인 범위의 최소 HA→복구→최종 APP 회귀 순서를 유지한다. **DB #11은 최종 APP 회귀 후 인수 판단**이며 이번 실패 회차로 종결하지 않는다. W4 `NOT_MEASURED`, rollback 시 이전 업무 포트 `/metrics` 노출 복원, DR·C01·Grafana의 기존 한계도 유지한다.
