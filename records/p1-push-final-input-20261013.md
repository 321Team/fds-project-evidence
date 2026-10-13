# Phase 1 Push 실행 결정·Robot 현행 정보·exact 입력 검토

2026-10-13 KST / 이권욱 / CODEX_ASSISTED.

**Robot 정보와 사용자 실행 허용은 확보했다. 이번 입력의 독립 검토만 기존 PR208에서 회수한 뒤, 시작 시점 조건을 확인하여 실행한다.** 기존 코드 재리뷰나 Harbor Lead의 별도 GO, 계정 보유자·권한·만료 재회신은 추가하지 않는다.

## 실제 확인·반영

| 구분 | 확인한 상태 |
|---|---|
| 사용자 결정 | [직접 답변 기록](https://github.com/321Team/fds-project-evidence/pull/208#issuecomment-6130701774): 해당 창·동시 변경 배제·Secret2개 회수 일괄 허용 |
| 창 | 2026-10-13 09:00 KST 종료, 실제 Push Job 시작 한도07:15. 늦으면 실행하지 않음 |
| Robot | 03:49:19 실측: `robot$push`(DB id3/name push) 활성, `fds` repository Pull/Push, 만료10/18 17:16:55 KST |
| Secret | 사용자가 등록한 두 이름·시각 확인. 값은 조회하지 않음 |
| 소비 경로 | 고정 main의 Workflow8개 바이트 확인: 두 Robot Secret 직접 참조는 app-push.yml 한 개. 다른 branch/동적 소비 부재를 증명한 것은 아님 |
| 권한 통제 | 현재 GWONUK/hayeounglee/supreme33-kr 모두 admin. user 결정의 동시 사용·변경 배제 적용. Repository Secret을 main 전용 강제 보호로 설명하지 않음 |
| 실행 코드 | main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7` 유지, 코드 변경 없음 |
| 입력 | 아래 exact 변환·목표 해시 확정. 원본03:39 검증 결과와 과거 APP/TBS 해시를 재사용 |

## 한 번에 검토할 입력

- [push.pending.json](../evidence/P1-CICD-01/push-final-input-20261013T040013/push.pending.json)에 실제 사용자 실행 결정 URL과 `2026-10-13T09:00:00+09:00`을 채웠다. Source·TBS·OCI·Scan 원본 연결은 이전 검증과 같다.
- [ACTIVATION_PLAN.json](../evidence/P1-CICD-01/push-final-input-20261013T040013/ACTIVATION_PLAN.json)은 독립 검토 후 바꿀 **두 필드만** 명시한다: `template_only: true → false`, `status: PENDING_EXACT_INPUT_REVIEW_AND_NEW_PUSH_AUTHORIZATION → APPROVED_FOR_DELIVERY`.
- 해당 변환의 정확한 UTF-8/LF 결과 SHA256은 **`28ae13b5dee1f16c1fb866eeaaf7984cc4e8286739d7f8da255ab8f02aef665d`**, 파일명은 `push-20261013-0400.json`이다. `verify_bundle.py`가 전체 결과를 메모리에서 재구성하여 해시를 확인한다. 독립 검토자는 원 입력과 이 두 필드 변환/목표 해시를 함께 검토하면 된다.
- 아직 승인 플래그를 바꾼 파일을 생성하거나 Runner에 배치하지 않았다. 현재 pending Gate는 승인 상태2개에서 BLOCK을 유지한다. 변환 후보의 순수 Gate는 `CONDITIONS_MATCH`이며, 이는 형식·선언값 검사다. 외부 승인·Runtime·현재 Scan PASS의 증명이 아니다.
- 원본 Code/Build/Scan 전체를 재검토할 필요는 없다. 검토 범위는 **실행 결정 URL·유효시간, 기존 Source/Run/해시 연결, Robot 관측과 Secret 통제·정리, 두 필드 변환 결과**다. 이번 검토 회신에 위 목표 SHA를 명시하면 실행 입력을 추가 수정하지 않고 이어간다.

## 실행과 완료조건

세부 범위는 [EXECUTION_SCOPE.md](../evidence/P1-CICD-01/push-final-input-20261013T040013/EXECUTION_SCOPE.md), 순서는 [RUN_CARD.md](../evidence/P1-CICD-01/push-final-input-20261013T040013/RUN_CARD.md).

1. 위 목표 해시에 대한 기존 reviewer의 독립 입력 검토를 확보한다. PR 전체 증적 병합을 별도 실행 선행조건으로 추가하지 않는다.
2. Harbor 비중첩·main/Runner/TLS/health·Secret 변경 여부 확인 → 정확한 record 새0600 배치 → 기존 execute=false 1회.
3. VALIDATION=PASS와 실제 입력/원본 결속을 확인한 뒤07:15 이전 execute=true 1회. fresh Scan 두 개와 원격 manifest를 확인한다.
4. 실제 결과·임시 credential 정리·dispatch 봉인 확인 후, 승인된 Actions Secret2개만 등록시각/공유 사용을 다시 확인하여 회수한다. 기존 Robot·credential 원본은 유지한다.

Harbor 비중첩은 companion 세션에 확인 요청했으며, 답변/시작 시점 관측 없이 확보됐다고 선언하지 않는다. 실제 Job 기한은 코드90분이며09:00 벽시계 종료를 자동으로 보장하지 않는다.07:15 이후 시작을 거부하고 중단·정리를 운영자가 추적한다.

## 검증과 한계

- STATIC: 새 pending의 이전 draft 대비 차이는 승인 참조·만료2개, 검토 후 활성화 차이는 플래그2개뿐이다. 같은 Gate 원본과03:39 provenance 검증을 소비한다. 변환 대상 해시·메타데이터·Git blob 연결을 로컬 확인했다.
- RUNTIME_READ: 기존03:49 DB READ ONLY 조회를 증적으로 편입했다. SQL/rc/선택 JSON/원본 출력 해시는 남겼으나 psql stdout 원본 전체를 보존한 영수증은 아니다. token/secret/salt를 조회하지 않았다.
- USER_AUTHORIZATION: 수신. INDEPENDENT_INPUT_REVIEW: PENDING. ADAPTER_VALIDATION/fresh SCAN/PUSH/DEPLOY: NOT_RUN. AC/Status 변경 없음.
- 이 기록은03:10/03:39 시점의 Robot·승인 미확인을 보완한다. 이전 봉인된 증적을 수정하거나 과거 판정을 다시 쓰지 않는다.

`prepare.py`는 이미 수행한 GitHub 조회와 사용자 결정 게시 추적용이다. 다시 실행하는 운영 카드가 아니다. 로컬 재검증은 읽기 전용 `verify_bundle.py`만 사용한다.

편입 원본: [새 회차](../evidence/P1-CICD-01/push-final-input-20261013T040013/), [검증기](../evidence/P1-CICD-01/push-final-input-20261013T040013/verify_bundle.py), [실측 Robot 영수증](../evidence/P1-CICD-01/push-final-input-20261013T040013/robot-metadata/receipt.json).
