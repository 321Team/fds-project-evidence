# O02 실제 알림 수신·취소·해소 — 2026-10-14

CODEX_ASSISTED · 이권욱. **RUNTIME: 한정 시험 완료 / 증적 편입 REVIEW·MERGE: 대기 / 전체 O02 최종 인수·#61 종결: 별도**. 기존 제2운영자 실습과 설정 증적209/210은 그대로 참조한다. 이번 폴더는 첫 schedule 원본과 새 수신 시험의 실제 결과를 보존한다.

## 1. 적용 기준과 실제 실행

- [계획 PR169](https://github.com/321Team/fds-project-baseline/pull/169), 검토 HEAD `58a839d86754717e98845d2e67a07ae48a15ec7d`, merge `0a39a39da8e55f80414431547338044360b9ac22`. 계획 병합은 다른 세션에서 10:22 KST에 수행했다. `postrun/pr169.response.json`, `postrun/reviews169.response.json`으로 연결한다.
- [사용자 허용](https://github.com/321Team/fds-project-baseline/pull/169#issuecomment-6158154174): 10:00~10:45 KST, 새 대기 Run1개·경고/해소 notify 각1개·소유 Run 정상 취소. [운영자 확인](https://github.com/321Team/fds-project-baseline/pull/169#pullrequestreview-5511729427)은 이 회차에 한해 다음 업무상 대기를 기다리는 기존 방침을 대체하는 시험을 수용했다.
- 실행 workflow 원본: `321Team/infra-ansible` main `ec15dcbd022942add199a8f4718c0f88105e880e`. event는 신규 `workflow_dispatch`, Attempt1. 기존 CI rerun은 없다.
- 실행 위치: 이권욱 관리 PC의 기존 `gh` 인증. GitHub hosted notify 외 서버 접속·Runner 공급/삭제·token/Secret/RBAC·변수·Harbor·DB 변경은 없다. 요청·응답 불명확 재요청 없이 각 변경 앞에 claim/시각/범위를 기록했다.

| 단계 | 실제 원본 | 결과와 범위 |
|---|---|---|
| 10:01 사전 확인 | `drill/preflight-20261014T010123Z-*`, `predispatch-*` | exact main/workflows/vars, 활성 regression5상태0, matching Runner0. Linux898분, 2,000분에서 다른 CI500분 유보 후 계산상602분; 자동 예산 보장 아님 |
| 대기 Job | [Run38493795328 / Job115624845990](https://github.com/321Team/infra-ansible/actions/runs/38493795328/job/115624845990) | Job created_at 10:05:28 KST. 실제 queued10분 초과, Attempt1/고정 HEAD/5labels. runner_id0. created_at과 API started_at이 같아도 queued를 실제 실행으로 세지 않음 |
| 실행자 queue-watch | `drill/threshold-queue-watch.json` 및 receipt | 10:15:53, `EPHEMERAL_RUNNER_NOT_SUPPLIED`, action_required=true, rc2. 읽기 실패가 아니라 대응 필요 분류 |
| 경고 | [Run38495038888](https://github.com/321Team/infra-ansible/actions/runs/38495038888), Job115628774938 | notify success, dry-read skipped. ATTENTION/정확 Run·Job1개. [봇 댓글](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6158722178) 10:19:04 |
| 실제 사람 수신·판단 | [이재환 회신](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6158776022), `drill/HUMAN_RECEIPT.json` | 본인 GitHub Notifications 생성10:19:26, 열람10:22:00. 본인 queue-watch10:22:45, 동일 분류·rc2, 공급 없이 시험 Run 취소로 해소 판단 |
| 취소 | `drill/precancel-*`, `regression-cancel.*`, 최종 observation | 10:24:30 정상 취소. Run·Job completed/cancelled를 재조회. 취소 접수만으로 정리 완료 판정하지 않음 |
| 해소 | [Run38495573119](https://github.com/321Team/infra-ansible/actions/runs/38495573119), Job115630460058 | notify success, dry-read skipped. active_runs_read0/NO_ALERT. [봇 해소](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6158791089) 10:24:56 |
| 최종 확인 | `drill/observe-20261014T012608951163Z-*`, `FINAL_RESULT.json` | 10:26:10, 소유 Run3개 terminal·활성 regression0·matching Runner0·main동일. [마감 기록](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6158817442), 시험 예약 o02-1 PAUSED |

`ALERT_DELIVERY_VERIFIED / CLEANUP_VERIFIED / CLEAR_OBSERVED`는 위 한정 시험 판정이다. regression은 cancelled이며 CI PASS가 아니다. 기존 10:45까지의 공급·다른 dispatch 배제 조건을 앞당겨 풀지 않았다. Harbor11:20 창에 실제 작업이 남지 않았다.

사람 수신은 **본인의 공개 회신**에 근거한다. 비공개 Notifications API와 본인 PC JSON을 이권욱이 직접 조회했다고 주장하지 않는다. 운영자 JSON SHA256 `01fd70f7ce102bda35c94cfddce93bc0d91bca1fc25146140b853c2abd7913c0`은 회신 값이며 원본은 본인 보관이다. 이메일·모바일 push 도착, 해소 멘션의 별도 사람 수신은 이 시험의 확인 범위가 아니다.

## 2. 첫 정기 실행과 수동 시험 구분

`first-schedule/`은 [schedule Run38383293926](https://github.com/321Team/infra-ansible/actions/runs/38383293926) / Attempt1 / Job115248769878의 기존 결과를 재사용한다. 10/13 19:25:50 KST 생성, notify success, `NO_ALERT_NO_COMMENT`. 10/14 09:13 KST 다운로드·API digest·내부 JSON sidecar 검증 원본을 편입했으며 다시 실행하지 않았다.

첫 schedule1회 성공과 수동 경고·해소2회 성공은 서로 다른 증거다. cron의 연속 운영·예정 시각 준수·야간 감시·SLA는 입증하지 않는다. 기존 운영자의 지연/누락 확인과 실제 업무 중 수동 queue-watch를 유지한다. 즉시 알림이나 별도 야간 당직을 새 AC로 추가하지 않는다.

| ZIP 원본 | API digest와 동일한 SHA256 | JSON SHA256 |
|---|---|---|
| 첫 schedule | `83820ea39f2682df98271d578a66bed1ec6a50cd185555b4080f535258add2a9` | `d2a9eb0d08bbc8adce917b63fd61860f5c3f2727dc564b0a20162ff39e8abb53` |
| 경고 | `3eae9c057ceba8ab6c3688559f7ec8d879a40c5011aa13abaf7ddb58e19ae2b0` | `51ca70a4e1e5dd54f2527235037273d5e363c3e0f54bf0a65e6442f10353b028` |
| 해소 | `6bc51c5424bad8bd1bbcc6c41e66d83c331417416650b79f6d6f1ead64ada7ac` | `112525d258195b47e370f80a2bd77c41c60d47fe4085894bd629aae2f6964314` |

## 3. O02 인수 대응과 #61 잔여

| 기존 요건 | 근거·현재 단계 | 이번 후속 처리 |
|---|---|---|
| 이권욱 외 공급·인증·회수 운영자 | [증적209](https://github.com/321Team/fds-project-evidence/pull/209), [본인 실습](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6136928532) | 이미 충족한 실습 재사용. 준비 지원·본인 수행 구분 유지 |
| 담당·수신 경로·감시/실패/부재 처리·비용 | [증적210](https://github.com/321Team/fds-project-evidence/pull/210), [연락 경로 정정](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6137285563) | 운영자 이재환, GitHub supreme33-kr/GWONUK, Actions 실패 확인·실제 근무 외 회차 실행자 queue-watch·CI500분 수동 유보 유지. 카카오톡/새 담당자 제외 |
| 실제 경고 게시·사람 수신·처리/해소 | 이번 원본과 본인 회신 | 한정 시험으로 확인. 새 업무 Job 공급/정리를 반복 요구하지 않음 |
| 운영 인수 | 위 세 항목의 실제 근거가 준비됨 | 본 PR에서 **새 원본 편입의 독립 검토1회**. 이권욱이 기존 권한으로 최종 인수 반영. 코드 전수 재리뷰·새 공통 GO 없음 |
| C01 보관6묶음 실효 접근통제 | 기존 #61의 별도 잔여 | 이번 GitHub 수신 시험은 SMB/NTFS ACL 증거가 아님. C01의 별도 유효 처분·증적과 구분 |
| 운영 종료/보관 | 증적210의 기존 조건 | 자원 회수기간 종료 시 알림 중지·원본 보관 확인은 기존 운영 담당/인수자의 후속. 자동 날짜 만료·자동 삭제 없음 |

따라서 O02의 수신 검증 공백은 해소됐지만 #61 전체 Close는 이 원본만으로 선언하지 않는다. 정기 실행 신뢰성 관찰을 이미 성공한 수신 시험의 재실행 조건으로 만들지 않는다.

## 4. 원본 선택·검증 범위

- `SOURCE_INDEX.json`은 관리 PC의 기존 원본→편입 상대 경로·크기·SHA를 기록한다. 원본은 바이트 그대로 복사했다. 모든 분당 관측 요약과 최종 전체 API 원본을 포함하고, 반복된 중간 전체 API 사본은 로컬 원본에 남겼다. 실제 변경 요청/응답·claim·취소 직전·종료 원본은 포함한다.
- ZIP3개는 재압축하지 않았다. Git 보관용 외부 `.zip.sha256`과 archive index만 추가했다. 기존 내부 JSON/sidecar·receipt·당시 판정은 수정하지 않았다.
- `drill/approved-read-tools`는 고정 main의 도구 사본이다. `observe_round.py`, `verify_notice.py`, `cancel_owned_regression.py`, `dispatch_clear_once.py`, `local-helper/ops_api.py`는 관리 PC 회차 보조 코드이며 **저장소 제품 코드의 독립 리뷰와 구분**한다. 제품 Workflow/권한을 변경하거나 서버에 배치하지 않았다. API 변경 범위는 위 사용자 허용1회에 묶였다.
- 정적 복사·digest·sidecar·receipt 응답해시·대상/종료 상태·한정 비밀패턴 검사는 편입 확인이다. 이것을 새 Runtime 재시험이나 독립 승인으로 표시하지 않는다.
- 기존209/210·sealed·sources는 불변. `SHA256SUMS`와 루트 대장은 새 편입 바이트의 무결성을 확인하며 AC 승인 그 자체가 아니다.
