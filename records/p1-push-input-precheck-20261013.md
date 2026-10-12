# Phase 1 새 Push 입력·원본 사전점검 — 2026-10-13

CODEX_ASSISTED · 이권욱 인수 범위 / 사용자 “착수”에 따른 실행 입력 준비·사전점검.

**확인한 공급 데이터로 새 `push.draft.json`을 작성했고, 실제 Runner 원본과의 연결을 검증했다. Secret 미등록·보유자 회신 대기는 해소됐다. 최종 입력 승인·이번 Push 실행 범위는 아직 확정하지 않아 Actions 사전검증 dispatch와 실제 Push는 수행하지 않았다.**

## 이번에 완료한 것

| 구분 | 수행·결과 | 한계 |
|---|---|---|
| 사용자 입력 | 등록한 계정은 `robot$push`, 유효한 토큰 보유를 사용자 직접 확인 | Secret 내용은 읽지 않았다. 현재 권한·disabled·만료는 별도 미관측 |
| GitHub READ | `HARBOR_CI_ROBOT_USERNAME`, `HARBOR_CI_ROBOT_TOKEN` 등록 확인. main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`, 조회 시 queued/in_progress 0 | 계정 인증 성공·권한 검사와 구분. 목록 수집 시각은 개별 receipt |
| RUNTIME_READ | **03:39:02 KST**, 정상 `cicd-runner01/server01_cicd-runner` UID1000, 기존 SSH 경로, rc0/stderr0 | 해당 호스트 읽기만. Registry 접속·credential 열람·지속 파일 배치 없음 |
| 공급 원본 | APP→Build→Scan 영수증3개 해시·context·Source 연결, OCI archive2개 내부 blob/manifest/config/layer 검증, 보고서2개 해시·이미지·패키지 범위·기존 HIGH/CRITICAL0 대조 통과 | 과거 Scan의 진위·연결 검증이다. **현재 취약점 Scan PASS가 아니다** |
| 설치 scanner | 현 실행 바이너리 해시·root 소유·0755를 병합 소스의 검사 함수로 확인 | 바이너리를 실행하거나 DB를 갱신하지 않음 |
| STATIC_INPUT | 현재 main의 순수 Gate 실행: 의도한 미승인 사유 **2개만 BLOCK** | adapter `execute=false` PASS라고 표시하지 않음 |

공급 Source는 `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, TBS는 Run37890963668/Attempt1이다. [APP Lead 확정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6074515472)의 Source 승인 참조와 Runner 원본의 값을 일치시켰다. 원 TBS Workflow `c9eff5fb2e50a690818a3e67347ab4a1bfc88f51`와 새 Push용 main SHA를 섞지 않는다.

원본을 읽은 수집기는 현재 main의 `inspect_archive`, `check_report`, `verify_binary`를 바이트 그대로 메모리에 불러 사용했다. 전체 Push adapter를 실행한 것은 아니다. 수집기 자체는 읽기 전용 준비 보조이며 독립 코드 승인 결과를 주장하지 않는다. 4개 모듈·Gate·Workflow 원본6개의 Git blob/SHA256과 수집기/출력/종료코드를 보존했다. 검사 시작 뒤 쓰기·새 프로세스·소켓 접속을 거부하는 audit hook을 사용했으며, 원 보고서의 이미지 설정·패키지 내용은 반출하지 않았다.

## 승인 상태를 임의 변경하지 않은 이유

`push.draft.json` SHA256: `a00999626803967016ec5a6f35b0283b88465d86d223d16e28e5e68f3c7e4141`.

- `template_only=true`, 상태는 `PENDING_EXACT_INPUT_REVIEW_AND_NEW_PUSH_AUTHORIZATION`이다.
- `push_authorization.workflow_sha`는 현재 main에 고정했지만 `reference`와 `expires_at`은 null이다. 미래 Run ID나 만료된 과거 Push 승인을 넣지 않았다.
- 현재 `delivery_gate.py`는 초안/미승인 여부 두 항목에서만 거부한다: `TEMPLATE_OR_UNCONFIRMED_INPUT`, `DELIVERY_INPUT_NOT_APPROVED`.
- 기존 [Push adapter 인계](https://github.com/321Team/infra-cicd/blob/2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7/docs/push-adapter-20261005.md)는 “독립적으로 검토된 record의 정확한 해시”를 요구한다. `push_workflow.py`의 execute=false도 같은 Gate를 호출한다. 이것은 새로 만든 Lead 승인 조건이 아니라 기존 실행기 계약이다.
- 이 두 플래그만 임의로 바꿔 PASS를 만들거나 Gate를 우회하지 않았다. 등록된 Secret을 쓰는 임시 Workflow도 만들지 않았다. 검토는 이번 입력·권한 사용·유효 구간에 한정하며 병합된 코드 전체를 재리뷰하지 않는다.

`harbor.if09_ac02=PASS`는 [10/2 HBR AC-02 완료 보고](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5947371286)를 재사용한 값이다. 새 Robot 인증이나 별도 SEC AC02/IF09 인수 판정이 아니다. TLS PASS는 [10/13 01:43 소비자 Python HTTPS 관측](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6128729026)을 재사용한 값이며 실제 Push 시작 시 상태를 다시 확인한다. 근거와 한계는 `VERIFICATION.json`에도 분리했다.

## 남은 입력을 한 번에 확정할 범위

1. **Robot 현행 정보:** 전체 이름은 사용자 회신 `robot$push`로 해소됐다. 현재 fds Pull/Push·disabled·만료가 남는다. 10/8의 10/18 17:16 만료는 후보 단서이며 자동 확정하지 않는다. 직접 확인 가능하면 Lead 회신 없이 진행한다. 토큰 원문은 재요청하지 않는다.
2. **실제 Push 창·범위:** [EXECUTION_SCOPE.md](../evidence/P1-CICD-01/push-input-precheck-20261013T033902/EXECUTION_SCOPE.md)의 두 이미지·fresh Scan·새 delivery tag·원격 manifest 확인·사본/Actions Secret 정리 범위와 유효기간을 확정한다. 저장소 Secret이 main 전용 접근 경계가 아니라는 기존 통제의 적용 범위도 함께 기록한다.
3. **확정 JSON/해시 검토 후 기존 실행기:** 새 이름으로 Runner에 배치 → main `app-push.yml execute=false` → 승인된 창에서 별도 `execute=true`. 초안을 활성 입력 폴더에 놓지 않았다. 데이터·코드 바이트가 바뀌지 않은 부분은 재시험하지 않는다.

Harbor Lead의 회신이나 Harbor 자동복구 전체 완료를 공통 선행조건으로 추가하지 않는다. 실제 Registry 건강상태와 변경·사후 관측 비중첩만 회차 시작 시 확인한다. `server02` 인증과 Deploy 복귀값은 Deploy 단계 잔여이며 Push 준비를 막는 조건으로 추가하지 않는다.

현재 단계: **STATIC/원본 RUNTIME_READ 완료, ADAPTER_VALIDATION 미실행, fresh SCAN/PUSH/DEPLOY 미실행, 독립 INPUT_REVIEW·이번 회차 승인 미완료, AC/Status 변경 없음.** 새 PR·코드 변경·새 Robot·Secret 수정·발급·재기동·Phase2 작업은 없다. 기존 PR208의 입력/증적 검토에 추가한다.

편입 원본: [회차](../evidence/P1-CICD-01/push-input-precheck-20261013T033902/), [초안](../evidence/P1-CICD-01/push-input-precheck-20261013T033902/push.draft.json), [검증](../evidence/P1-CICD-01/push-input-precheck-20261013T033902/VERIFICATION.json).
