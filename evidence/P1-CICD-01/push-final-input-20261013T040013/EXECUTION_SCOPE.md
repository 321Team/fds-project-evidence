# Phase 1 APP Push 단일 회차 실행 범위

2026-10-13 KST / 이권욱 / CODEX_ASSISTED. 실제 실행 허용은 이 문서에 대한 사용자 결정으로 기록하며, 독립 입력 검토와 구분한다.

## 대상과 순서

1. 기존 `321Team/infra-cicd` main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`의 `app-push.yml`만 사용한다. 입력을 독립 검토한 뒤 정상 Runner 계정 `cicd-runner01/server01_cicd-runner`의 기존 `FDS_CICD_PushInputs`(0700)에 새 JSON(0600)을 배타 생성한다. 기존 입력·claim은 보존한다.
2. 기존 APP Source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, TBS Run37890963668/Attempt1, `FDS_CICD_AppWorkflow.57rithja` 원본을 사용한다. 이미 확인한 원본을 재빌드하지 않는다.
3. `execute=false` 1회로 입력·원본을 검증한다. Secret 주입·Registry 쓰기·새 취약점 검사는 이 단계에 없다.
4. 성공하면 동일한 검토 입력으로 `execute=true` 1회: fresh DB/Scan → `10.1.93.54/fds/transaction-api`, `10.1.93.54/fds/fds-engine`에 각 새 `delivery-<uuid>` 태그 → tag/digest 원격 manifest 일치 확인 → 임시 인증 파일 정리·증적 봉인.
5. 두 이미지 모두 fresh Scan HIGH/CRITICAL 0, 원격 digest 일치, `dispatch-result.json` 및 credential cleanup/봉인까지 확인한다. Push 완료와 Deploy/전체 Delivery·AC 인수를 구분한다.

새 Robot·권한 확대·회전·배포·Pod/서비스 재시작·기존 태그 덮어쓰기·원격 artifact 삭제는 포함하지 않는다. 실제 토큰 인증은 4번에서 확인한다. 토큰만 검사하는 새 Workflow는 만들지 않는다.

## 제안 유효창과 시작 조건

- 허용 결정·이번 exact JSON 해시 독립 검토 이후부터 **2026-10-13 09:00:00 KST**까지 1회. `execute=true` 실제 Job 시작이 **07:15 KST** 이후이면 시작하지 않고, 대기열에 남으면 취소한다. 현 Workflow 최대 90분과 결과/정리 15분 여유를 고려한 최종 시작 한도다. 지연되면 시각만 몰래 연장하지 않고 미실행으로 보존한다.
- `execute=false`가 07:15 전 성공하지 않으면 실제 Push를 하지 않는다. 코드의 `expires_at`은 새 전송 전 검사이며 실행 중인 요청을 벽시계 시각에 자동 종료하는 장치가 아니다. 실행자는 실제 Run/Attempt와 상태를 추적하고 오류·창 초과 위험 시 중단/정리한다.
- actual main 일치, 정상 Runner idle·HOME, Harbor TLS/health와 변경·사후 관측 비중첩을 실제 시작 직전에 확인한다. Harbor 작업창 예약을 이 문서가 대신하지 않는다.
- Robot `robot$push`: 03:49:19 KST 현재 enabled, `fds` repository Pull/Push, 만료 **10/18 17:16:55 KST**를 실제 읽기 확인했다. 저장소 Secret 내용과 실제 인증 성공은 아직 확인하지 않았다.
- Repository Secret이 다른 branch Workflow와 관리자에게도 사용 가능하다는 기존 잔여위험을 수용하고, 이번 회차 동안 해당 Secret을 쓰는 다른 실행 및 관련 Workflow/Secret 동시 변경을 배제한다. main 제한과 동등한 강제 보호라고 표현하지 않는다. 03:59 전후 조회상 세 계정 GWONUK/hayeounglee/supreme33-kr 모두 admin이므로 과거 권장 역할을 현재 권한으로 간주하지 않는다.

## 회차 뒤 정리

- Workflow가 만든 이번 회차의 임시 auth 파일 제거와 receipt 봉인을 확인한다.
- 사용자가 이번에 등록한 `HARBOR_CI_ROBOT_USERNAME`(2026-10-12T18:34:05Z), `HARBOR_CI_ROBOT_TOKEN`(18:34:27Z) **두 Actions Secret만 회차 종료 뒤 삭제**하는 안이다. 정리 직전 이름·갱신 시각·다른 실행의 사용 여부를 확인하고, 갱신/공유 소비가 발견되면 삭제하지 않고 인수한다.
- Harbor의 기존 Robot 자체·권한·원 보관 credential과 다른 Actions Secret은 유지한다. token 값·인증 원문·전체 Scan report를 공개하지 않는다.

## 실패·중단·복구

- 입력/해시·승인·TLS·Scan·인증·기한 실패 시 후속 Push를 하지 않는다. 기존 보안 검증을 해제하지 않는다.
- 한 서비스만 성공하거나 timeout/중단이면 원격 쓰기 여부를 단정하지 않는다. nonce/tag·claim·원본 영수증을 보존하고 원격 readback으로 남은 상태를 확인한다. 자동 retry·claim 삭제·태그 삭제로 우회하지 않는다.
- 실패 뒤 남은 auth는 해당 회차 소유 경로만 확인·정리한다. SIGKILL/host 장애로 확인 불가하면 성공으로 표시하지 않고 수동 인수한다.
- 실제 명령·시각·rc·Source/Workflow/Run/Attempt·해시·fresh Scan·원격 결과·정리를 비밀값 없이 기존 PR208에 연결한다.

## 승인·검토 구분

사용자 실행 허용과 기존 [Push adapter의 exact record 독립 검토](https://github.com/321Team/infra-cicd/blob/2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7/docs/push-adapter-20261005.md)는 별개다. 새 코드 리뷰·별도 Harbor Lead GO·새 PR을 추가하지 않는다. 기존 PR208의 이하영/이재환 검토에서 이번 입력·유효창·Secret 통제만 한 번에 확인한다. 허용/검토 전에는 승인 상태 플래그를 바꾸거나 Runner에 실행 입력을 배치하지 않는다.
