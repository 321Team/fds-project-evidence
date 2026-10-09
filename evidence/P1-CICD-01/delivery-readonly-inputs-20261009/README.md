# APP Delivery 입력 사전 관측 — 2026-10-09 19:21:47 KST

## 확인된 범위

Harbor 복구 작업과 분리하여 control01에서 Kubernetes API GET 3건만 수행했다. 기존 `svc_ansible` SSH·become 경로, `/etc/kubernetes/admin.conf`를 사용했으며 자격증명 원문은 읽어 전달하지 않았다. Deployment/Pod/ServiceAccount 응답 중 필요한 식별·이미지·상태 필드만 서버 메모리에서 선택해 수신했다. 전체 API 응답 원문은 미보관이며 `raw_stdout_sha256`을 전체 원문 수신 증거로 표시하지 않는다.

- `transaction-api`, `fds-engine` 각각 Deployment ready3/3, Pod3개 모두 Running/Ready, 관측 Pod imageID가 해당 Deployment image digest와 일치.
- 현재 image digest: transaction-api `a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33`, fds-engine `5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369`.
- 승인 Source affbc69의 기존 Run37890963668 TBS 후보 digest `ef0afe42…`/`de34afb7…`와 다름. 이는 아직 후보 Push/Deploy를 실행하지 않은 상태와 부합하며 drift/장애로 판정하지 않는다.
- `ci-cd/cicd-runner-sa` UID `8f1ddfef-7bec-4b15-8cb7-c4b1a068a176`, automountServiceAccountToken=false. UID 조회는 최신 RBAC/TokenReview/배포 권한 검증이 아니다.
- 현재 CICD main `c9eff5fb2e50a690818a3e67347ab4a1bfc88f51` 재조회. 해당 소스의 `docs/deploy-workflow-handoff.md`에 따라 execute=false도 완성된 plan/approval/새 Push receipt/SA UID 입력을 요구하므로 placeholder dispatch를 수행하지 않았다.

## 산출물·잔여

`DELIVERY_INPUT_MATRIX.json`에 source/run/후보 digest와 현재 Deployment UID/generation/container/image를 연결했다. 현재 이미지는 **관측된 원복 후보**이며 승인된 rollback plan이 아니다. source/TBS는 [증적190](https://github.com/321Team/fds-project-evidence/pull/190), 원본 보관은 [증적195](https://github.com/321Team/fds-project-evidence/pull/195)에 연결한다.

다음 입력은 새 Push receipt, 사용 시점 scan/Robot/trust 인계, 정확한 대상·원복 승인, 최신 RBAC/CA/토큰 결속, Harbor 비중첩 및 별도 실행 GO다. 원본 관측은 시점 정보이며 실제 실행 전 재확인한다.

STATIC_RECEIPT=RECORDED / READONLY_API=3_OF_3_RC0 / REVIEW=NOT_PERFORMED before collection / DEPLOY_PLAN=NOT_APPROVED / TOKEN_ISSUED=false / PUSH_DEPLOY=NOT_RUN. 수집기의 실행 바이트 SHA와 명령·시각·rc는 invocation.json에 고정했다. 신규 모듈의 독립 리뷰를 마친 것으로 표시하지 않는다.

Harbor에 연결하거나 이미지 pull, TokenRequest, 서비스 재시작, Pod/Deployment 변경을 수행하지 않았다. Ready 관측을 앱 기능/Health E2E 또는 Delivery Gate 인수로 확대하지 않는다. 기존 sealed 증적은 수정하지 않는다.
