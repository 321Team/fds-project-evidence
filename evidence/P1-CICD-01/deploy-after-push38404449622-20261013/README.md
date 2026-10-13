# 새 Push 이후 Deploy 준비 — 승인 전

이권욱 / CODEX_ASSISTED. 2026-10-13 **22:45~22:48 KST** 조회 기준. 준비·조회와 로컬 입력 검증을 수행했다. 이번 회차 서버 공급·Token 발급·Workflow dispatch·Deploy는 모두 미실행이며 사용자 실행 결정·독립 정확 입력 검토는 대기다.

## 제안하는 한 회차

**10/13 23:15~23:25 KST 실제 시작, 10/14 00:15까지 정리**를 제안한다. 준비 파일 배치 후 false 사전검증 1회 → 통과 후 true Deploy 1회, 해당 Run을 위한 TokenRequest 1회다. 실패·dispatch 응답 불명 시 자동 재실행하지 않는다. 시작 마감까지 독립 입력 검토·최신 상태·비중첩·이권욱 콘솔 대기가 확인되지 않으면 실행하지 않는다. 이 시간은 아직 승인되지 않았다.

`fds-app`의 transaction-api → fds-engine 순서로 image만 바꾸고, 각 단계 Ready 및 마지막 두 앱 Ready를 확인한다. 실패 시 실행기가 적용을 확정한 앱만 지정 이전 digest로 역순 복귀한다. 권한·시한 소진, PATCH 결과 불명, checkpoint 실패는 자동 복귀 대상이 아니며 상태를 보존하고 콘솔에서 실제 상태를 대조한다. 지정 외 image·수동 추가 PATCH·재발급은 포함하지 않는다.

Push, drain/reboot/HA/Probe 장애, 업무 POST·DB 쓰기, 최종 APP·DB 인수는 이 회차 범위에 없다. 기존 순서 Deploy → 최소 HA/복귀 → 최종 APP 회귀 → DB 판단을 유지한다.

## 정확 입력과 변경 근거

| 입력 | 값 |
|---|---|
| CICD main | `147f760298dd4a683ea58f2a887483769352b97d` |
| 앱 Source / TBS | `affbc69beef9967f7977d09a6fec14f7fb6c0e94` / Run38395350748 Attempt1 |
| 새 Push | [Run38404449622 Attempt1](https://github.com/321Team/infra-cicd/actions/runs/38404449622), 두 이미지 원격 digest 확인 PASS |
| Push 원본 SHA256 | `8be5cef6cc47e0afcd5236f031bc7c180cdec40ba34039729741114c46f38276` |
| 새 request UUID | `37a528cd-184a-4e0f-8f17-62416ca2e4e4` |
| plan SHA256 | `ed7787673f5b8f8f1f97e49e78a9359ec1c09f8835acda19cc93d7e130ee2ad4` |

[`deploy-plan.unapproved.json`](deploy-plan.unapproved.json)의 `template_only=false`는 실제 값을 채운 plan이라는 뜻이며 실행 승인이 아니다. 별도 approval/record·실제 Run은 만들지 않았다. `PLAN_VALIDATION.json`의 Run1은 메모리 내부 정적 검증용 sentinel이며 실제 Deploy 회차로 기록하지 않았다.

| 앱 | 현재·복귀 digest | 새 digest |
|---|---|---|
| transaction-api | `a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` | `338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0` |
| fds-engine | `5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` | `8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d` |

두 repository는 `10.1.93.54/fds/<앱>`이다. 복귀하면 **업무 포트 `/metrics` 노출이 다시 생긴다**. 이를 영구 위험수용이나 현재 보안 완료로 표시하지 않는다.

## 직접 조회한 기준선

- Deployment UID는 plan과 일치한다. API generation11, engine generation5, 각 replicas/updated/ready/available3, HPA0. 각 Worker에 앱별 Pod1개, 총6개 Running/Ready. Worker02의 두 기존 Pod restartCount는 각각1이고 나머지0이다. 현재 회차 실패나 재시작 증가로 해석하지 않는다.
- 두 앱 non-root UID10001/GID999, read-only root filesystem, privilege escalation false, volume mount0. 새 TBS의 격리 기동 검사가 이 조건을 다뤘지만 Kubernetes·DB·업무 성공은 아직 입증하지 않았다.
- 세 Worker 모두 지정 복귀 digest의 CRI 캐시 메타데이터가 있다. 레이어 무결성·Harbor 재-pull·복귀 실행 성공은 미검증이다. imagePullPolicy는 IfNotPresent다.
- CP1 기존 server02 경로의 SA GET, CA 해시, Runner→API TLS 검증 PASS. SA UID `8f1ddfef-7bec-4b15-8cb7-c4b1a068a176`, automount=false. 두 Deployment만 get/update/patch 가능한 기존 Role/Binding을 확인했다.
- CP1 발급 전 권한 확인(config/SA/SelfSubjectAccessReview) PASS. TokenRequest·TokenReview는 호출하지 않았다. 사용한 기존 stage는 이전 source2d8a14c이며 필요한 7개 모듈은 현재147f760 Git bytes와 같다.
- 이전 Deploy38364658401의 claim1/checkpoint9와 결과를 다시 읽었고 이전 socket은 없다. 새 plan에 그 claim·token·실패 candidate를 재사용하지 않는다. Runner Worker0, Actions 진행 Run0, Harbor TLS/health 정상이다.
- Harbor PR62는 [21:54 병합 기록](https://github.com/321Team/infra-harbor-trivy/pull/62#issuecomment-6146040006)상 코드 병합만 완료했고 운영 공급/H6는 미실행이다. 이번 health 조회는 H6 배제·종료를 증명하지 않는다. 실행 직전 Harbor 변경/H6/사후 관측과 다른 앱/DB/MON 변경 비중첩을 다시 확인한다.

## 검증·기존 리뷰 재사용

[PR218 최신 HEAD9647a83 독립 리뷰](https://github.com/321Team/fds-project-evidence/pull/218#pullrequestreview-5504467642)는 **승인**이며 해당 HEAD CI도 success다. PR218은 조회 시 Draft/Open, 미병합이다. 이 승인은 Push 증적 편입 검토이며 새 Deploy 실행 승인이나 최종 인수가 아니다.

현재 Git 원본으로 필요한 Deploy 모듈·workflow18파일을 이전 실제 Deploy source와 비교해 **변경0**을 확인했다. 변경된 Build/Scan 측의 run.py 권한·기동 검사는 PR217의 성공 TBS 증적으로 연결한다. 불변 Deploy 코드 전체 시험·전체 코드 리뷰를 반복하지 않는다.

- STATIC: plan 스키마·두 target·TBS/Push 원본 결속 PASS, 현재 Git blob/SHA·AST import closure·13-member 로컬 controller archive 무결성 PASS.
- READ-ONLY RUNTIME: 계정·명령·시각·출력 hash를 포함한 collector/receipt/stdout을 보존했다. 수집기 자체는 `REVIEW=NOT PERFORMED (Pre-check)`이며 리뷰된 배포 코드의 실행 결과로 표시하지 않는다.
- 새 Deploy approval JSON, record SHA 및 전체 approval/Workflow 입력 검증은 사용자 결정 후 생성·대조할 항목이다. 새 Token·Deploy·앱 업무 회귀는 미실행이다.

## 실행 전·중·후 판정

1. 사용자 창/복귀 범위·콘솔·비중첩 결정 후 infra-cicd#11의 별도 정확 approval JSON 원문을 만든다. plan bytes는 유지한다. `approved_by=GWONUK`, not_before/expiry, `allow_rollback=true`, 정확 plan hash를 결속한다. 사용자 결정을 대리 기록하며 독립 승인으로 표시하지 않는다. 생성된 approval/record의 hash와 실제 원문을 독립 검토받는다.
2. 승인된 현재 main/plan/record/CA/SA UID와 fresh 두 Deployment UID·현재 image·Ready/spec·HPA0, Worker0, Harbor health·작업 비중첩을 확인한다. 불일치면 중단한다. 이전 source·UTC 오류·만료 창을 복사하지 않는다.
3. [`STAGING_AND_DISPATCH.md`](STAGING_AND_DISPATCH.md)에 따라 새 UUID 경로에만 공급한다. 사전검증 Run1회 성공 후 true Run1회를 시작한다. 실제 Job이23:25 이전에 시작했음을 확인한다. 대기열에서 마감을 넘긴 Run은 broker를 연결하지 않고 취소·결과를 보존한다.
4. 실제 Run/Attempt1/HEAD/plan/record/SA UID와 socket을 확인한 후 기존 broker1회로 native token을 발급·전달한다. TTL900초, audience/API/CA 통제는 유지한다. 실행기는 시작 시 승인·실제 credential 잔여가 각각630초 이상인지 확인하고 각 요청마다 유효성을 재확인한다. 남은 시한을 충분하다고 추정하지 않는다.
5. 성공은 원본 receipt의 두 READY·error NONE, 이후 fresh Deployment/Pod별 새 digest·Ready3·재시작/endpoint·socket 정리와 일치해야 한다. Ready만으로 HTTP·업무·DB 성공을 선언하지 않는다. token 원문을 저장하지 않으며 local reference/endpoint 정리와 만료를 기록한다. server 강제 revoke를 수행한 것으로 표시하지 않는다.
6. 실패/timeout/전송 단절은 원본·claim/checkpoint를 보존한다. 승인된 실행기 조건에서 가능한 지정 image 복귀만 수행한다. 불명확 상태·권한 소진이면 다음 변경을 멈추고 이권욱 콘솔에서 현재 형상을 확인한다. 자동 재발급·rerun·claim 삭제0회. 복귀 READY도 업무 HEALTH_NOT_VERIFIED로 유지한다.

독립 검토 범위는 새 plan/Push 연결, 현재 복귀 기준선, 새 source 표기·패키지, 승인 후 생성할 exact record, 시간·실패/정리 경계다. Phase1 전체나 변경 없는 Deploy 코드의 새 공통 승인을 요구하지 않는다.
