# Phase 1 Delivery/Runner 실행 입력 정리 — 2026-10-13

이권욱 / CODEX_ASSISTED. 사용자 “착수”에 따라 DNS 종료 뒤 Delivery/Runner 입력·호출 경로·복귀 조건을 확인했다. **승인된 APP 공급물을 다시 만들 필요는 없고, 다음은 기존 Robot 전달 정보와 실제 회차 입력을 완성하는 단계다.** GitHub·서버 읽기와 로컬 준비를 수행했으며 Push/Deploy/Token 발급·Secret 등록·Runner 공급·정책/서비스 변경은 하지 않았다.

기준: [PR160](https://github.com/321Team/fds-project-baseline/pull/160)~[PR162](https://github.com/321Team/fds-project-baseline/pull/162)의 S01/S04/O02, [CICD11](https://github.com/321Team/infra-cicd/issues/11), [Ansible61](https://github.com/321Team/infra-ansible/issues/61). 관련 관측은 **03:10:12–03:13:18 KST**, GitHub 수집은 `GITHUB_RECEIPTS.json`/`EXTRA_GITHUB_RECEIPTS.json`의 개별 시각이다. 원본 UTC와 PC 수신 시각을 보존한다.

## 확보·재사용한 입력

| 항목 | 확인한 값·범위 | 판정 한계 |
|---|---|---|
| APP Source | `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, 공급 도구 `8eac4c982076e3c219840a13686b15c46879981f` | [기존 APP 확정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6074515472) 재사용. 현 main으로 교체하지 않음 |
| 원 TBS | Run37890963668/Attempt1, workflow `c9eff5fb2e50a690818a3e67347ab4a1bfc88f51`, input `72eb5259…13e3` | 실제 과거 PASS이며 현재 fresh Scan을 대신하지 않음 |
| 공급 바이트 | Runner `FDS_CICD_AppWorkflow.57rithja`, 기존 이미지 archive2개 SHA 일치. API 48,930,304 B, engine 38,500,352 B | 이번은 archive2개와 receipt3개 파일 조회. 기존 원본69개 전체를 새로 검증했다고 표시하지 않음 |
| 다음 Workflow | 현 main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7` = [PR74](https://github.com/321Team/infra-cicd/pull/74) 병합 | 원 TBS Workflow SHA와 새 Push/Deploy 실행 SHA를 분리 |
| Runner 도구 | 정상 계정 uid1000/HOME0700, Skopeo1.24.0·RPM검증 rc0, copy/inspect 필수옵션 존재 | 재설치 불필요. 실제 Skopeo 인증·전송 성공은 아직 미확인 |
| API TLS | 정상 Runner 계정에서 `.109:6443`, 고정 공개 CA `5e4462b4…a49c`, 이름 검증 유지 TLS1.3 | SA Token 인증/실효권한 시험 아님 |
| SA/대상 | `ci-cd/cicd-runner-sa`, UID `8f1ddfef-7bec-4b15-8cb7-c4b1a068a176`; 두 Deployment 각각 Ready3/3 | 관리 경로의 현재 GET. 실제 Runner Token 발급·소비는 미실행 |
| RBAC/HPA | fds-app named Role: 두 Deployment만 get/update/patch, SA binding 확인; 해당 namespace HPA0 | 선택한 Role/Binding 구성 조회. 전체 ClusterRoleBinding·실효권한 전수 확인 아님 |
| Token 정책 | audience `https://kubernetes.default.svc.cluster.local`, 요청/실제 수명 상한900초 | [H03/R1](https://github.com/321Team/fds-project-baseline/pull/160#issuecomment-6084886811)·PR74 재사용. 3600초로 되돌리지 않음 |
| Harbor TLS/health | 타 세션 01:43 Python HTTPS6회/01:48 Worker 설정 관측7파일 해시 대조·재사용 | [기존 근거](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6128729026). 실제 Skopeo/CRI Pull, 최신 Robot·Scan·remote digest와 구분 |

현재 API image `a7093136…cc33`, engine `5e2a081c…7369`. 공급 후보는 API `ef0afe42…dc39`, engine `de34afb7…2813`이다. 두 Deployment UID·전체 spec 해시·실제 image/Ready·CA/SA·두 archive 전체 해시는 `INPUTS.observed.json`에 연결했다. 이 파일은 **template_only=true인 관측표**이며 실행 입력이나 승인 원본으로 사용할 수 없다.

## 다음 실행에서 실제로 채울 항목

| ID | 남은 사실·결정 | 담당·처리 시점 |
|---|---|---|
| D-CRED | 사용할 기존 CI Robot의 정확 ID/세대, 현재 fds Pull+Push·disabled/만료·관련 소비자, 보호된 보관 위치·전달/회수 방법 | 사용자 답변은 보유자 **Harbor Lead(이하영)**. 기존 PR208에서 이 사실만 요청. 비밀값·토큰 해시는 게시하지 않음 |
| D-SECRET | 현재 저장소 Secret은 `CICD_APP_SOURCE_READ_TOKEN` 1개. 현 app-push가 읽는 `HARBOR_CI_ROBOT_USERNAME/TOKEN` 두 이름은 없음 | 현 조직 상속 Secret은 이번 재조회하지 않았다. 저장소 목록만으로 모든 credential 부재를 단정하지 않음. 전달 방식/접근 범위·잔존/정리 결정을 구체화한 뒤 반영 판단 |
| D-PUSH | 새 정확 record, 고정 Workflow SHA·외부 record hash·회차/승인 reference/만료, 현재 Robot·Scan/DB/원격 digest 확인 | 기존 Build/Source 재실행 없이 준비. fresh Scan은 승인된 실제 Push 경로에서 수행; 새로운 Push receipt는 Push **결과**로 생성 |
| D-AUTH | ansible01→control01 **server02**의 실제 기존 인증 경로 | 테스트한 `p1_ansible_ed25519`는 SSH255/Permission denied. 같은 키의 svc_ansible root 읽기는 성공했지만 발급 계정 성공을 대신하지 않음. 키·신뢰·계정·타임아웃을 바꾸지 않았고 반복 시도하지 않음 |
| D-DEPLOY | 새 Push receipt 후 target UID/이전 image·호환성·복귀 범위, 새 plan UUID/approval·유효 구간·console·비중첩, native source/CA/binding과 실제 잔여 Token 예산 | `rollback_approved=false` 유지. 원복 시 이전 image의 업무 포트 metrics 노출 가능성을 함께 처분. 현재 image를 자동 승인 복귀값으로 쓰지 않음 |
| R-O02 | 적격 제2운영자·실제 필요한 **Ansible isolated Job**·기존 접근·관측/연락/대체·정리 | queued/in_progress0, Ansible 등록Runner0. 실제 필요 Job 때 기존 운영자 카드로 수행. 현재 CICD standing Runner는 online1/busy=false이며 서로 다른 모델 |

H03/H05의 과거 expiry와 회신은 당시 근거다. 10/8 기록 `robot$push` fds Pull+Push/10월18일17:16 만료는 현재 후보를 찾는 단서이고 이번 사용 가능 판정이 아니다. 보유자를 알아낸 것과 credential 수신·현행 유효성 확인을 구분한다. 새 Robot 발급을 기본 전제로 만들지 않는다.

## 실행 순서와 호출·복귀 경계

1. **Robot 사실·전달 방법 확인과 기존 발급 계정의 인증 경로 확인을 병행한다.** 이미 확정된 Source·900초 정책·보관 인수·TLS 관측을 재요청하지 않는다. O02 인수 대기를 Delivery의 공통 Gate로 추가하지 않는다.
2. **Push 입력을 완성해 한 번에 검토 가능하게 만든다.** Runner의 새 `FDS_CICD_PushInputs/<새 record>.json`과 외부 SHA를 준비한다. 지금 있는 `run5-push.json`·`run37322456303-push.json`은 다른 회차이며 덮어쓰거나 재사용하지 않는다. 기존 claim2개도 보존한다. 현재 Robot 전달 경로와 회차 값이 없으므로 입력 배치·dispatch는 미실행이다.
3. 기존 `.github/workflows/app-push.yml` main 수동 dispatch의 `execute=false`로 바이트 정합을 확인하고, 허용된 실제 창의 별도 `execute=true`에서 fresh Scan→두 image Push→tag/digest readback→임시 auth 정리까지 연결한다. **execute=false도 Runner의 lock/증적 디렉터리를 생성하므로 완전한 무변경 조회라고 부르지 않는다.** Scan/Push 부분 실패·불명 결과면 원 영수증/claim을 보존하고 자동 rerun/remote 삭제 없이 정확한 tag·digest 상태를 대조한다.
4. **성공한 새 Push receipt를 Deploy 계획에 연결한다.** 미래 Run ID나 성공 receipt를 미리 만들지 않는다. 기존 v2 plan/분리 approval/외부 hash 모델을 사용하며 승인 원문은 `infra-cicd#11`의 GWONUK 작성 기록을 소비하는 현재 코드 계약이다. 이관된 판단을 별도의 새 HBR Lead GO로 돌려보내지 않는다. 실제 입력의 독립 검토와 사용자 실행 판단은 기존 단계대로 구분한다.
5. 기존 `.github/workflows/app-deploy.yml` `execute=false` → 별도 첫 attempt의 `execute=true`, ansible01 broker→CP1 server02 발급/TokenReview→Runner private socket→Session→image-only PATCH/rollout을 사용한다. 기본 Session 여유630초·broker 발급 전 창640초 기준을 기존 코드대로 소비하고 실제 더 짧은 Token은 검사 결과에 따른다. 900초로 합성/갱신하거나 만료 후 쓰기를 하지 않는다. 현재 DeployInputs/DeployClaims/소켓 디렉터리 부재는 아직 준비 전인 상태이며 자동 생성하지 않았다.
6. 실패/만료/승인 변경/SSH·CA·UID drift면 후속 쓰기를 멈춘다. broker 실패만으로 미발급·미배포를 단정하지 않는다. 해당 Run/result/claim·Deployment UID/RV/image와 마지막 checkpoint를 확인한다. 살아 있는 자격증명·승인된 복귀 범위 안의 기존 rollback만 수행하고, 불명확/만료이면 콘솔 인수로 넘긴다. claim·journal을 삭제해 재실행하지 않는다. 소켓은 해당 회차 소유 확인 후 정리하며 논리적 Token 참조 해제와 서버 취소를 혼동하지 않는다.
7. 최종 후보 image·분산 상태를 기준으로 업무 포트 metrics 차단·전용 포트·HTTP/Rule/DB 저장·해당 HA/Negative Gate/rollback을 기존 AC와 연결한다. 이후 불필요한 전체 회귀를 반복하지 않는다. O02는 실제 필요한 Ansible Job에서 별도 제2운영자가 공급·인증·회수까지 수행하며, CICD Push/Deploy를 그 실적으로 대신하지 않는다.

Harbor의 코드 리뷰·자동복구 전체 완료를 Delivery의 새 공통 선행조건으로 만들지 않는다. 실제 사용할 Registry의 상태·권한과 변경/사후 관측 비중첩은 시작 직전에 확인한다. 기존 Runtime 허용을 새 Secret/Token/Push/Deploy 변경에 확대하지 않는다. 입력이 채워지면 대상·영향·복귀가 결속된 실제 실행 범위를 한 묶음으로 제시한다.

## 검증과 증적

- 현장 읽기 4개 receipt: Runner 도구/공급, control01 관리 GET, Runner API TLS는 rc0. CP1 server02 SSH는 rc255로 원문 보존. 실패를 PASS에 합치지 않는다. 원 stdout/stderr와 수집기 SHA를 검증했다.
- GitHub 최신 4저장소 main·열린 PR/queue/Runner, PR74 리뷰/병합·TBS·관련 회신을 수집했다. 참조 source29파일은 고정 commit의 Git blob·SHA256 대조 통과. 원 collector는 순수 읽기 보조이며 **REVIEW=NOT PERFORMED (Pre-check)**다. 코드 승인을 전체 helper로 확대하지 않는다.
- 실제 서버에 지속 파일을 배치하지 않고 stdin Python으로 읽었다. SSH/sudo/API 감사 흔적까지 없다는 뜻은 아니다. 공개 CA 외 비밀키/kubeconfig/Token 내용을 반출하지 않았다. API는 선택 필드 투사와 원 응답 해시이며 완전한 원 API 응답 보관이 아니다.
- 새 코드/회귀 시험·CI 재실행, Secret 등록·발급·Push/Deploy·Runner 신규 공급·AC/Status 변경·Phase2 작업은 없다. 증적 CI·독립 REVIEW/MERGE는 편입 PR의 정확 HEAD 결과를 따른다.

실행 입력은 `INPUTS.observed.json`, 수집·대조 결과는 `VERIFICATION.json`, 공급원 바이트 연결은 `SOURCE_BINDING.json`이다. 당시 collector 파일은 실행 증적이며 무조건 재실행하는 카드가 아니다. 기존 [DNS 결과](p1-worker02-dns-session-20261013.md)와 후속 관계를 유지한다.

편입 원본: [수집회차](../evidence/P1-CICD-01/delivery-runner-readiness-20261013T031012/), [관측 입력](../evidence/P1-CICD-01/delivery-runner-readiness-20261013T031012/INPUTS.observed.json), [검증 결과](../evidence/P1-CICD-01/delivery-runner-readiness-20261013T031012/VERIFICATION.json).
