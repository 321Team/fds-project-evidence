# P1-CICD-01 — 새 APP Run 이후 Deploy 연결 잔여

CODEX_ASSISTED · 2026-10-08 KST. 책임 [infra-cicd#11](https://github.com/321Team/infra-cicd/issues/11) / [baseline#16](https://github.com/321Team/fds-project-baseline/issues/16). STATIC 소스 대조·설계 준비이며 실행 입력/승인 원본이 아니다.

기준 main `4e9324cd8acf0ba67b35f950b4c952db8064540e`, 새 APP Build/Scan Run37642123031/1, source `adc90410f99cb7af5b40bc8ff92c45272e9f8bee`. [PR65](https://github.com/321Team/infra-cicd/pull/65)의 Push 초안과 [증적147](https://github.com/321Team/fds-project-evidence/pull/147)을 재사용한다. 그 초안을 다시 만들거나 미확정값을 PASS로 채우지 않았다.

## 중복 구현 방지와 실제 공백

Deploy adapter/plan/claim/approval/credential/transport 연결 라이브러리는 이미 main에 있다. 과거 `docs/deploy-readiness-37331796555.md`의 초기 “adapter 없음” 문구는 현 상태가 아니다. 같은 문서의 후속 구현 절과 최신 `docs/deploy-execution-connection.md`를 함께 읽어야 한다.

main workflow는 app-push, app-test-build-scan, runner-smoke, source-validation, trivy-db-preflight, trivy-toolcheck 여섯 개다. 별도 Deploy workflow는 없고, 기존 연결 문서도 운영 CLI/Workflow 및 실제 credential metadata·읽기 권한의 연결을 잔여로 남긴다. 새 adapter를 처음부터 구현하기보다 **기존 연결 API를 소비하는 실행 진입점과 입력/인증 인계**를 다음 코드 범위로 권고한다. 실제 integration은 새 소스 PR 및 검증이 필요하다.

## 생산·소비 입력표

| 입력 | 지금 재사용 가능 | 다음 확보 / 책임 |
|---|---|---|
| APP Source/Build/Scan | 새 Run37642123031의 receipt·로컬 OCI 식별값 | evidence147 독립 인수 별도 / CICD |
| 새 Push receipt·Harbor 원격 digest | 아직 없음. 과거 Run37331796555는 다른 이미지 | 기존 Robot 권한·만료·전달·회수 조건 인계 후 새 Push / HBR→CICD |
| Deployment UID/resourceVersion/image | 10/6 CP1 스냅샷은 설계 참고 | 실제 실행 직전 읽기 조회. 옛 image를 현재 rollback 값으로 단정하지 않음 / K8S→CICD |
| SA/audience/RBAC/Token TTL | 기존 제한된 get/update/patch 계약·검증 모듈 | 검토된 실제 발급·만료 metadata, Runner 인증/거부 경로 확인. Secret/Pod list 권한 확대 없음 / SEC·K8S |
| plan/approval/context | v2 분리 원본·claim 구현 | 새 계획 bytes 및 외부 해시, infra-cicd#11 승인 raw body, 실제 Deploy Run/Attempt / CICD Lead |
| Health/E2E/rollback | 기존 절차와 후보만 참고 | 이전 digest 보존·Pull 가능성·APP/DB 호환성과 검증 주체 확정 / APP·HBR·CICD |

## 다음 구현의 완료조건

1. 입력 확인만 하는 경로는 API 변경·claim 소비·token 발급을 하지 않는다. 정상 fixture뿐 아니라 승인 byte 불일치/만료/철회, 잘못된 Run/Attempt, 미확정 Push 및 대상 drift가 변경 전에 차단되는지 검증한다.
2. 실제 실행 경로는 기존 v2 승인 fresh lookup→lock/claim→credential→기존 adapter 순서를 유지한다. GitHub 댓글 읽기 권한과 rate budget을 실제 Workflow에 결속하고 PAT 공유나 권한 확대를 기본 해결책으로 쓰지 않는다.
3. 부분 rollout·401/403·429/timeout·승인 철회·readiness 실패를 구분한다. 승인 소멸 시 자동 rollback을 억지로 진행하지 않고 기존 MANUAL_RECONCILIATION_REQUIRED 계약을 유지한다. claim/checkpoint 삭제로 재시도하지 않는다.
4. 실행/실패/정리 원본, 두 Deployment별 결과, 승인·계획·Push·source·Run 연결을 남긴다. manifest 적용만으로 Pod imageID/Health/E2E를 PASS 처리하지 않는다.
5. 코드 리뷰/CI 이후 새 실행창·복구 범위를 고정한다. Source validation이나 이전 Push 승인으로 Deploy를 실행하지 않는다.

지금은 운영 CLI/Workflow 코드 변경, 토큰/Secret 생성, cluster 조회·patch, Push·Deploy 실행을 하지 않았다. 다음은 HBR 입력을 기다리는 동안 기존 모듈의 실행 진입점 설계를 확정하고 모의 실패 경로를 준비하는 것이다. 이 문서 자체는 실행 승인을 생성하지 않는다.
