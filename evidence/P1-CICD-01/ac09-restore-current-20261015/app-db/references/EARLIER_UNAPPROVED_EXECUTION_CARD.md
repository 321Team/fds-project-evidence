# AC09 이전 이미지 복구 → 현행 복원 실행 검토 카드

2026-10-15 · 작성: CICD 단일 실행 세션 · **PREPARED / INPUT_REVIEW_PENDING / RUNTIME_NOT_AUTHORIZED**

중앙 CONTROL의 Harbor .50 우선권을 유지한다. 이 카드는 새 실행 허가·예약·SEC 위험수용이 아니다. 현재 단계에서 새 TokenRequest, Runner 공급, dispatch, Deployment 변경, 거래 POST, DB 쓰기는 모두 0이다.

## 1. 병합·입력 결속

- [PR86](https://github.com/321Team/infra-cicd/pull/86): 12:24:52 KST merge `bb328e9d6a8828db84a694492baabbf090844841` 확인. [이하영 코드 승인](https://github.com/321Team/infra-cicd/pull/86#pullrequestreview-5527574497)은 HEAD `b88e24d9bf43a85d33192850d9aab45d1ad39c5d` 대상이며 Runtime 승인이 아니다.
- 이번 후보 workflow SHA: `fddc76e1c261cd938f06211b7ed035fdcb32e606`. 이후 main에 들어온 PR84는 Phase 2 문서 변경이다. 승인 HEAD와 `tools/delivery` 및 `app-deploy.yml` diff 0, 전달 모듈 37개 바이트 대조·compile 완료. 기존 Linux CI [38672442477](https://github.com/321Team/infra-cicd/actions/runs/38672442477)의 754건 성공을 재사용하며 새 CI 실행은 하지 않았다.
- [SOURCE_BINDING.json](SOURCE_BINDING.json)의 Git blob/SHA256으로 37개 파일 추적. native bundle SHA256 `16366261081cf95639480cfb9256255541bc1099fde717225e4ad8f6e322ae8b`.
- 과거 승인 원문·plan·Push receipt 바이트를 재사용한다. origin Run `38412128227`/Attempt1, Build `38395350748`/1, Push `38404449622`/1. origin plan SHA256 `ed7787673f5b8f8f1f97e49e78a9359ec1c09f8835acda19cc93d7e130ee2ad4`, approval `fb1458a22db9fa91397810293cbbb0f66198b08786e6e365150cef18e0bebb4d`.
- [과거 승인 댓글](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6147190360)의 현재 작성자·본문을 정확 대조했다. 과거 만료 창은 연장하지 않는다. 별도 후속 철회 결정의 부재까지 이 대조 하나로 증명하지 않으므로, 새 승인에 historical basis의 사용 가능 여부를 명시한다.
- 새 승인 파일은 모두 `template_only=true`, 승인자/댓글/시각 미입력이다. validator가 `APPROVAL_SCHEMA_OR_TEMPLATE_INVALID`로 거부함을 확인했다. 실제 Run ID·combined input record·승인 해시는 아직 없다. 로컬 검증에 사용한 Run1은 형식 확인용 값이며 실제 실행 이력이 아니다.

| 회차 | 요청 ID | plan SHA256 | 새 승인에 제안하는 보상 |
|---|---|---|---|
| R1: 이전 이미지로 복구 | `cd01e613-d576-41eb-8354-8e9283d0f60d` | `6e622c0bf539830c77cc841beb6852b0db65a9652822754d30141e587ca71d2d` | `allow_rollback=true`: 명확한 배포 실패 시 **현행 이미지**로 보상 |
| R2: 현행 이미지로 복원 | `3451e56c-57bc-490e-8d15-6cede958229f` | `3b928b2c74600d81066f4577a0b3095df027351434137249a67ef5e328720183` | `allow_rollback=false`: 실패 시 구버전으로 자동 역복귀하지 않고 콘솔 인수 |

R2의 false는 현재 **권고안**이다. 구버전 metrics 재노출을 늘리는 자동 역복귀를 피하려는 선택이며, 복원 실패 시 혼합 상태가 남을 수 있다. 정확한 콘솔 복구 주체·권한·대상 이미지와 실패 인수를 확정하지 못하면 R1도 시작하지 않는다. 기존 origin의 true를 이 선택의 승인으로 사용하지 않는다.

## 2. 정확한 대상과 관측

두 Deployment만, namespace `fds-app`, registry `10.1.93.54/fds/`를 사용한다. Secret, replica, Service, RBAC, NetworkPolicy, DB schema는 변경 대상이 아니다.

| 대상 | 고정 UID | 현행 → 이전 → 현행 |
|---|---|---|
| transaction-api | `8a2af808-ec33-41f2-80b5-addde4e28910` | `338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0` → `a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` → 첫 digest |
| fds-engine | `bf825dec-465b-4603-8b71-f768d195531c` | `8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d` → `5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` → 첫 digest |

- 12:39 KST control01의 Deployment/Pod/Service/EndpointSlice GET4개: 현행 두 digest·각 Ready3·기존 UID 확인. 이 관측은 미래 실행 직전 fresh 검사를 대신하지 않는다.
- Worker01/02/03에서 대상4개 digest의 CRI 캐시 메타데이터 확인. 조회 rc0, 내부 도구 stderr135바이트는 원문 대신 해시 기록. layer 전체 완전성·Registry 재Pull 가능성·새 Robot 자격을 검증한 결과는 아니다.
- 12:41 worker01의 기존 OCI manifest와 작은 상위 layer 내용만 읽어 앱 source12개 해시 확인. pull/mount/container 실행 없음. 11개만 `adc90410`과 같고 API `db.py` 1개는 다르다. [호환성 메모](DB_COMPATIBILITY.md)를 새 판단 입력으로 사용한다.
- db01 기존 `svc_ansible` SSH는 인증 단계 rc255. SQL 미실행. 현 DB 제약·권한·revision 및 구버전의 현 DB 동작은 **NOT_VERIFIED**다.

## 3. Runtime 전에 닫을 항목

1. APP/DB 담당: [기존 APP 검토](../phase1-ac09-app-evidence-20261015/APP_ROLLBACK_EVIDENCE.md)에 이번 11/12 대조·index 선언 차이·현재 catalog 결과를 결합해 호환성 제한을 판단한다. [DB_CATALOG_READONLY.sql](DB_CATALOG_READONLY.sql)은 정상 `server08@db01` 콘솔 경로로만 전달·조회할 준비가 되어 있다. 암호/새 SSH 권한은 요구하지 않는다.
2. SEC 이하영: 아래 두 업무 `/metrics` 재노출의 범위·30분 상한·실패 시 남는 노출을 수용 또는 거부한다. [SEC_STATUS §4](../phase1-central-control-20261015/SEC_STATUS.md)는 검토 입력이며 본인 승인이 아니다. 거부하면 HOLD; 옛 이미지를 재빌드해 같은 digest 복구라고 표시하지 않는다.
3. 중앙 이권욱: Harbor 작업의 실제 종료·회수 확인 뒤 공유창·비중첩·정상 계정의 콘솔 복구 인수자를 정하고, **R1/R2 각 true1회·TokenRequest 명령 각1회·총 POST2건·보상 방향**을 명시한다. 코드 승인·이전 forward 승인과 이번 실행을 구분한다.
4. 현재 source/main·두 plan·새 승인·native bundle·최종 record 해시와 실제 Run/Job을 결속한다. false모드 두 건을 먼저 검증한다. 준비 중 main이 움직이면 실제 workflow SHA/바이트 영향부터 대조하고 즉석 수정·dispatch하지 않는다.
5. 첫 쓰기 직전: 두 UID/full spec/imageID/각Ready3/Worker별 Local Endpoint·기존 허용 경로·현재 metrics404·전용200·DB catalog/시험 계정0행·Harbor/캐시 공급 상태·CA·권한·다른 작업/Runner/claim을 새로 확인한다. 부족하면 첫 PATCH 전에 HOLD한다.

## 4. 한정 회차와 유한 시간 — 미승인 제안

**전체 공유창 45분, 첫 이전-image PATCH 시도 `P`부터 업무 metrics 노출 상한30분**을 SEC 제안과 동일하게 제출한다. `W`는 향후 확정할 공유창 시작이며 지금 예약 시각은 없다. 정상 진행의 목표 배분이지, 실패 복구의 최악 시간 보장이 아니다.

| 시점 | 진행/중단 기준 |
|---|---|
| W~W+8분 | fresh 검사·두 false job·정상 계정과 console/broker 준비. false도 로컬 입력/시간/CA 검증일 뿐 원격 승인·Runtime PASS 아님 |
| P≤W+10분 | R1 첫 PATCH 허용 상한. 준비가 늦으면 첫 쓰기 없이 종료·재계획 |
| P+10분 목표 | API→engine 순서로 이전 두 이미지 Ready. 2×300초 대기는 요청·승인 조회 비용을 제외한 코드 대기 예산이며 보장 시간이 아님 |
| P+12분 목표 | 이전 상태 Health·승인된 P01/DB/metrics 확인. 지연·업무 실패 시 추가 시험을 줄이고 현행 복원을 우선. POST 자동 재시도 없음 |
| **P+15분까지** | R1 job/broker가 종료되고 두 이전 baseline이 안정된 경우 **R2 첫 현행-image PATCH** 착수 목표. 단순 dispatch 시각으로 충족 표시하지 않음 |
| P+25분 목표 | 현행 두 이미지 Ready. 상태별 검증·업무metrics404·전용target6 회복으로 연결 |
| **P+30분까지** | 마지막 구버전 Pod 종료·현행 업무metrics404 및 Health/DB/계측 확인. 초과하면 새 시험 중단, 미회수 노출과 실제 복구 권한을 보고; 자동 연장 없음 |
| W+45분까지 | 원본·claim/checkpoint·receipt 확보, Runner/job별 회수, 소켓/프로세스 및 credential 만료·참조 정리 확인. 결과 불명·노출 미회수면 창 해제/완료 처리하지 않음 |

병합 adapter는 회차 시작 및 첫 PATCH 직전에 **승인/credential 각각 잔여630초 이상**을 요구한다. broker 발급 직전 승인창은640초 이상, 요청 TTL900초·검증된 실제 만료시간을 쓴다. receiver 대기120초, broker candidate30초, 승인/TokenReview 등은 기존 유한 timeout을 유지한다. Actions timeout30분은 승인이나 토큰 수명을 늘리지 않는다. 두 token을 미리 발급하거나 한 token을 두 회차에 재사용하지 않는다.

새 승인 창 후보는 R1 `W~W+25분`, R2 `W~W+40분`이다. 두 false 검증을 먼저 할 수 있도록 두 창 시작은 W로 두되, 실제 R2 쓰기는 R1 종료/두 이전 Ready 뒤에만 한다. 승인자는 exact KST로 변환해 결정해야 한다. 실제 잔여 시간·공급 지연·복구 인수로 위 배분을 만족할 수 없으면 시작 전에 숫자를 조정해 **SEC와 동일한 최종 수치**로 다시 판단하며 런타임 임의 연장하지 않는다.

한도: 각 phase false1·true1(총 최대4 job), 각 실제 Run Attempt1, 재실행0. ephemeral Runner는 job별 필요할 수 있으므로 공급/회수도 최대4건을 정확 Job에 한정하는 후보이며, 1개 등록으로4개 job을 처리한다고 가정하지 않는다. TokenRequest **명령 호출 최대2회**, true회차별1회; CLI 내부 전송 횟수를 이 숫자로 주장하지 않는다. 정상 image PATCH는 총4회, R1의 명확한 실패 보상은 실제 반영된 대상에 한해 최대2회 추가. GET/관측은 기존 deadline 내에서만 수행한다. 새 회차·재발급·권한 우회는 포함하지 않는다.

## 5. 상태별 업무·DB·계측 검증

기존 APP 도구/경로와 [APP_E2E_STATUS](../phase1-central-control-20261015/APP_E2E_STATUS.md)를 재사용한다. 이 준비 단계에서 새 runtime 도구를 만들지 않았다. 향후 실행 위치는 정상 Runner `server01_cicd-runner@10.250.10.20`, broker는 기존 CP1 정상 관리 계정/CA 경로다. 업무 관측은 기존 허용 edge→Worker NodePort30080→API 및 API→engine, MON 경로를 사용하며 Runner에 NodePort/exec 권한을 추가하지 않는다.

- R1/R2 각각 고유 account의 정상 deposit10000 KRW **1건씩, 총2건만 후보**. payload template은 phase별 UUID 계정, 문서용 source IP `198.51.100.10`, 실제 시각의 명시적 offset을 요구한다. template wrapper 자체는 전송 payload가 아니며 `approved_to_post=false` 상태다.
- 두 앱 `/livez`·`/readyz`200, 안정화 구간 restart/CrashLoop 없음. API readyz의 SELECT1만으로 insert/Rule 호환성 PASS를 판정하지 않는다.
- HTTP201, UUID transaction_id, `fds_detected=false`, `fds_evaluation_skipped=false`; `fds_rules`는 R01/R02/R04/R07 네 행의 triggered=false·detail=null. 같은 ID/account/금액/통화/거래유형/IP/시간/판정의 DB1행과 일치. 이전0행·이후1행을 확인하며 원본 시험행을 삭제하지 않는다.
- 같은 phase의 안정된 동일 Pod 집합에서 `transaction_save_success_total`·`fds_evaluated_total` 각각 +1, `transaction_save_failure_total`·`missing_client_ip_total`·`fds_evaluation_error_total` 증가0. 동시 거래가 있거나 Pod가 교체되면 귀속 미확인으로 기록하고 다른 phase/이전 Pod counter와 차감하지 않는다.
- R1에서는 구버전 업무8000/8001 metrics 노출을 기록한다. R2 종료는 **직접 앱 업무포트404**, 전용9091/9090 200 및 target6 정상으로 판단한다. edge404만으로 대체하지 않는다. metrics label/value 민감도 및 전체 도달 source는 미확인으로 유지하고 원문을 공용 증적에 무분별하게 싣지 않는다.
- APP의 D04 판단에 필요하면 R2의 같은1건을 Client→edge 경로로 결합할 수 있으나, 실제 경로/수행자·두 요구의 인수 범위를 승인에 먼저 확정한다. 추가 거래·부하·장애·전체Rule 재시험을 자동 가산하지 않는다.

## 6. 실패·복원·회수

- Drift/claim 충돌/부족 시간/DB 호환성 불명/SEC 판단 부재는 첫 쓰기 전 HOLD.
- R1 정상 완료 뒤 업무 확인 실패는 adapter 자동 보상 조건이 아니다. 유효한 R2와 안정된 두 이전 baseline이 있어야 현행 복원으로 진행한다.
- PATCH 결과 불명, checkpoint 실패, 승인 철회/만료, 권한 상실은 자동 보상을 포함해 추가 쓰기를 멈춘다. 원본·claim·마지막 확인 이미지·미확인 대상을 콘솔 인수자에게 넘긴다. mixed/Ready 불량 상태에 정상 plan-2를 강행하지 않는다.
- R2 실패는 구버전 자동 역복귀 없음. 현재 상태를 읽어 정확한 대상/UID/spec/복구 권한을 다시 결속한 복구가 필요하다. 이 카드만으로 `kubectl rollout undo`, 강제 patch, 새 TokenRequest를 허용하지 않는다.
- POST timeout/응답 유실은 저장 실패로 단정하지 않고 고유 account/ID로 DB 대조. 자동 재시도·DELETE·migration·권한/보안 통제 완화 없음.
- 토큰 값은 파일/로그에 남기지 않는다. 정리는 이번 승인된 정확 경로/Job/등록/소켓만. durable claim/checkpoint·원본은 보존하며 광범위 삭제·호스트 전원 종료 없음.
- **정상 rollout ≠ Health/E2E 완료 ≠ AC09 인수.** 복구·현행 복원 실제 결과를 증적 PR로 독립 검토하고 관련 AC/전체 Exit를 따로 판단한다.

## 7. 중앙에 넘기는 현재 결론

로컬 후보·출처·범위·시간·실패 카드 준비 완료. 다음은 **현재 DB read-only 원본 수신 → APP/DB 차이 판단 및 SEC 처분 → Harbor 해제 뒤 중앙 exact 창/복구 인수·두 회차 승인 → 입력 finalization/false → R1→R2 순차 실행**이다. 현재 실제 승인/Run/공급/점유/예약은 생성하지 않았다.
