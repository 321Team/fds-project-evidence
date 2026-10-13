# Phase 1 기존 Robot을 이용한 APP Push — 실행 범위 초안

상태: **검토용 / 실제 Push 미승인 / 창 미확정**. 입력·원본 사전점검은 이미 사용자 “착수”에 따라 수행했다. Secret 2개 등록은 사용자가 직접 완료했다.

## 대상·행위

- 저장소 `321Team/infra-cicd`, main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`, 기존 `.github/workflows/app-push.yml`.
- Runner `cicd-runner01 / server01_cicd-runner / UID1000`, HOME0700. 기존 공급 `FDS_CICD_AppWorkflow.57rithja`를 재사용.
- 승인 APP Source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, TBS Run37890963668/1. Source 재빌드 없음.
- Registry `10.1.93.54/fds/transaction-api`, `10.1.93.54/fds/fds-engine` 두 곳.
- 사용자 보유 `robot$push`, 등록된 `HARBOR_CI_ROBOT_USERNAME/TOKEN` 사용. 새 Robot·회전·권한 확대 없음.
- 확정된 새 JSON을 기존 PushInputs0700 아래 새0600 파일로 1회 배치. 기존 record/claim은 보존.
- `execute=false` 1회는 archive/영수증 검증과 Runner checkout·lock·증적 파일 생성까지. Secret 주입·Scan·Registry 쓰기 없음.
- 그 성공 후 승인 유효창의 별도 `execute=true` 1회: fresh DB/두 OCI Scan → 두 repository에 각각 신규 `delivery-<uuid>` tag → tag/digest raw manifest 대조 → 임시 auth 정리. 기존 배포·Pod·서비스·latest/stable tag를 바꾸지 않음.

## 시작 전에 확정할 항목

- Robot의 현재 fds Pull/Push, enabled, 만료가 실행창을 덮는지.
- 정확한 실행 시작/만료와 승인 참조, 확정 JSON/SHA256. 이번 초안의 null을 성공·승인으로 대체하지 않음.
- Harbor 변경·사후 관측과 비중첩, 현재 TLS/health, 현재 main 일치, Runner idle·정상 HOME.
- Repository Secret은 저장소 내 다른 workflow에서도 사용 가능하다. 기존 수동 write/dispatch 통제 적용과 회차 동안 다른 소비 배제를 확인한다. 공유 소비자가 있으면 임의 삭제하지 않는다.
- 제안 정리 범위: 이번에 등록한 Actions Secret 두 이름만 회차 후 회수. Harbor의 기존 Robot 자체와 원 보관 사본은 유지한다. 정리 직전 해당 두 Secret의 등록/갱신 시각과 공유 소비 여부를 확인하며 다른 세션이 갱신한 값을 덮어쓰거나 삭제하지 않는다. 이 삭제 범위는 아직 미확정이다.

## 정상 판정·실패·복구

- 정상: fresh Scan 두 개 HIGH/CRITICAL0 및 DB 유효 → 서비스별 Push/digest 대조 PASS → `dispatch-result.json`와 credential cleanup/봉인 확인. Push 성공을 Deploy나 전체 Delivery/AC 인수로 표시하지 않는다.
- 검증·fresh Scan·TLS·인증·승인 기한·소스/입력 drift에 실패하면 후속 쓰기 중단.
- 부분 Push/timeout/중단이면 해당 nonce/tag와 원 claim·영수증 보존. 자동 retry, claim 삭제, remote tag/blob 삭제를 하지 않는다. 원격 readback으로 어느 쓰기가 있었는지 확인한 뒤 별도 재시도/처분을 결정한다.
- SIGKILL/host 장애는 임시 auth 정리를 보장하지 못한다. 해당 회차 소유 임시 경로·Actions Secret 소비를 확인하고 승인된 정리 범위만 처리한다.
- 결과·명령/시각/rc·Source/Workflow/Run/Attempt·archive/manifest·fresh Scan·remote readback·정리를 비밀값 없이 추적 가능하게 보존한다.

Deploy/TokenRequest/server02 인증/배포 rollback은 별도 단계이며 이 범위에 포함하지 않는다. 이 초안은 승인 요청을 구체화하기 위한 자료이며 실행 허용을 대체하지 않는다.
