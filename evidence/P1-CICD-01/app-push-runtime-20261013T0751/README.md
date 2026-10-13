# Phase 1 APP fresh Scan·Push 단일 회차 — 2026-10-13 07:51 KST

CODEX_ASSISTED · 실행자 이권욱. **RUNTIME: fresh Scan·Push PASS, 임시 인증 및 Actions Robot Secret 두 개 회수 PASS. Deploy는 미실행이며 전체 Delivery/AC 인수는 미완료다.**

## 승인·실행·원본

- 사용자 창 변경/행위·정리 허용: [6130830892](https://github.com/321Team/fds-project-evidence/pull/208#issuecomment-6130830892), 기존 [구체 범위](https://github.com/321Team/fds-project-evidence/blob/a7083cf8e86980b4bce9c48c9b24bfb3ff0bf2c3/evidence/P1-CICD-01/push-window-1200-20261013/EXECUTION_SCOPE.md). 실제 시작 한도10:00, 종료12:00.
- exact 입력 독립 검토: [supreme33-kr APPROVED 5496659933](https://github.com/321Team/fds-project-evidence/pull/208#pullrequestreview-5496659933), 검토HEAD539d02f. 입력3209 B/SHA `13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89`. 허용된 두 필드만 변환했으며 frozen pending/ACTIVATION_PLAN은 수정하지 않았다.
- 실행 코드: infra-cicd main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`, 기존 app-push.yml. Source APP `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, TBS37890963668/1·Workflowc9eff5fb의 archive를 재사용했다. 새 Build/기존 CI 재실행이 아니다.
- 사전검증: [Run38318762530/Attempt1](https://github.com/321Team/infra-cicd/actions/runs/38318762530), Job115041584651 success, `VALIDATION=PASS`, `PUSH=NOT_EXECUTED`.
- 실제 실행: [Run38318968352/Attempt1](https://github.com/321Team/infra-cicd/actions/runs/38318968352), Job115042237182 success. 실제 Job 시작07:51:02, Push 처리07:51:06.983–07:51:27.709 KST. execute=true 1회, 재시도0.
- 대상: cicd-runner01/server01_cicd-runner UID1000. 기존 엄격 SSH 경로로 0700 PushInputs에0600 파일을 O_EXCL/O_NOFOLLOW 배치. 사후bytes/hash/owner/nlink 대조. input·claim은 보존한다.
- 원본 private 결과: `/home/server01_cicd-runner/FDS_CICD_Push.cb_o91gw`; 검증 결과: `FDS_CICD_Push.aisebqro`. 정확 Job log의 EVIDENCE_DIR로 연결했다.

## 실제 결과

| 이미지 | fresh HIGH/CRITICAL | 원격 tag·digest readback | manifest digest |
|---|---|---|---|
| transaction-api | 0 / 0 | PASS | `sha256:ef0afe42feb0f9e50f54b5aaab99a34bbeb01f10bc9fb8a0580519101645dc39` |
| fds-engine | 0 / 0 | PASS | `sha256:de34afb7a557d6ccc844fb74613ebc971eb493260236acc35ef3051935122813` |

새 태그는 두 repository 모두 `delivery-931b66469d0e4946853f44a3ba404bea`다. 기존 태그 덮어쓰기/삭제는 하지 않았다. 현재 DB를 새 다운로드했으며 DB_PREFLIGHT PASS, scan context·source·archive/report/manifest 결속이 일치한다. 세부 DB 시각·SHA와 결과는 VERIFICATION/selected-original-receipts에 있다.

## 정리·검증

- 정상 Runner online/idle, 활성 실행0, main 일치, Secret 이름/갱신시각 불변을 실행 직전 확인했다. 다른 Harbor 세션의 현장 작업 없음과 구간 비중첩을 확인했다. Runner→Harbor 기본 신뢰 TLS/HTTP200·8개 component healthy를 전후 확인했다.
- credential-cleanup/dispatch-result PASS, 관련 봉인11항목 및 fresh report·DB hash를 수신 원본과 대조했다. 사후 FDS_CICD_PushAuth 디렉터리0. 단일 사용 claim의 Run/Attempt/input 결속을 확인하고 보존했다.
- 실행 종결/다른 활성Run0 및 원래 updated_at을 다시 확인한 뒤 `HARBOR_CI_ROBOT_TOKEN`, `HARBOR_CI_ROBOT_USERNAME` 두 Actions Secret만 삭제했다. readback에서 두 이름 부재, `CICD_APP_SOURCE_READ_TOKEN` 메타데이터 그대로를 확인했다. Harbor Robot 자체와 원 보관 credential은 변경하지 않았다.
- 전달/읽기 helper는 별도 독립 코드 리뷰를 받지 않았다. 실제 Push는 병합된 코드와 승인된 입력으로 실행했으며, helper의 자체 점검을 독립 REVIEW로 표시하지 않는다. **이번 새 Runtime 증적의 독립 편입 REVIEW/MERGE는 대기**다. 기존 입력 승인과 구분한다.

## 수신·보존 범위와 한계

- 원본 result/dispatch/Scan·DB receipt 일부를 바이트 그대로 selected-original-receipts에 보관한다. 전체 선택 receipt/manifest 바이트는 execution-result/stdout.json의 raw_b64에도 보존하며 SHA와 결속한다. 전체 Scan report·Trivy DB·OCI archive·auth 내용은 Git으로 반출하지 않았다. 보고서·DB는 hash만 수신했다.
- 원 Actions Job log는 로컬 보호 작업 경로에 보존하며 binding 파일에 SHA/Run/Job/원본 경로를 연결한다. Git에는 전체 Job log를 넣지 않는다. GitHub preflight는 필요한 필드 투영과 원 API snapshot hash를 제공한다.
- 로컬 읽기 카드 초안의 문자열 구문 오류는 서버 전송 전 compile에서 중단됐고 수정한 validation-result-v2만 실행됐다. gh 로그 출력은 ANSI 표시 보호로 처음 거부되어 바이트 파일로 수신한 뒤 경로만 추출했다. Runtime 재시도나 코드/보안 검증 우회가 아니다.
- 내부 하위 receipt의 `DELIVERY_GATE=NOT_VERIFIED`, `source_approval=NOT_VERIFIED` 등은 해당 구성 요소의 판정 범위다. 승인 원본·입력 검토·실행 성공을 연결하되 이를 전체 Delivery 완료로 바꾸지 않는다.
- Deploy/Token 발급/Pod 재시작/HA/HTTP Probe 장애/최종 거래 회귀/AC·Status 변경/Phase2는 이번 회차에서 수행하지 않았다. 다음은 새 Push 결과를 Deploy 입력 준비에 연결하고 별도 실행 범위·복귀 조건을 확정하는 일이다.
