# P1-CICD-01 AC07 — 실제 Runner 최소권한 진단

2026-10-14 KST / CODEX_ASSISTED / 실행·판정 지원: 이권욱 / 증적 독립 검토: 대기.

**실제 진단 PASS, 증적 편입·AC07 최종 인수 대기. 전체 CICD In Progress.**

2026-10-14 21:55:58 KST, 병합된 CICD PR82의 기존 broker로 단기 SA TokenRequest 명령을 **한 번** 실행했다. 실제 Runner에서 고정 SSAR 25건(허용 6·거부 19)이 모두 기대와 일치했고, 지정 Deployment GET 2건이 성공했다. 전후 앱·RBAC 관측과 프로세스 종료를 확인해 21:57:27 KST에 점유 창을 해제했다.

## 판정과 근거

| 항목 | 실제 확인 |
|---|---|
| 코드 | [PR82](https://github.com/321Team/infra-cicd/pull/82), 검토 HEAD `db8230d7580820c55ab388680a1e87fc3e45db0a`, merge `9fb2e2dcac8682a89c4b7c267c833ae8d9aaeb18` |
| 독립 코드 리뷰 | [이하영 APPROVED](https://github.com/321Team/infra-cicd/pull/82#pullrequestreview-5518054443), 정확 HEAD, 미해결 thread 0 확인 후 21:47:44 KST 병합 |
| CI | [PR CI 38564435253](https://github.com/321Team/infra-cicd/actions/runs/38564435253): 696개(17+11+64+604), smoke 일치. [merge CI 38566564766](https://github.com/321Team/infra-cicd/actions/runs/38566564766) success |
| 실행 권한 | 사용자/Lead의 “리뷰 체크 후 차단 사항 없으면 병합 후 착수”; 코드 리뷰 승인과 Runtime 결정을 분리해 [실행 기록](raw/EXECUTION_AUTHORITY.json)에 결속 |
| 실행 대상 | ansible01/server01_ansible → k8s-control01/server02, cicd-runner01/server01_cicd-runner(UID1000). 기존 SSH trust와 CA 사용 |
| SA·API | `ci-cd/cicd-runner-sa`, UID `8f1ddfef-7bec-4b15-8cb7-c4b1a068a176`, `10.1.93.109:6443`; 공개 CA SHA `5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c` |
| 발급·인증 | 21:55:58 발급, 만료값 22:10:58 KST, TTL 900초. CP1 fresh TokenReview와 Runner 인증 PASS. 값은 저장하지 않음 |
| 허용 6 | fds-app의 transaction-api·fds-engine 각각 get/update/patch 권한 질의 허용 |
| 거부 19 | 임의/다른 namespace Deployment patch, Deployment create/delete, Secret get, Pod list, TokenReview create, Role·RoleBinding·ClusterRole·ClusterRoleBinding create/patch/bind/escalate 지정 조합, pods/exec get/create |
| GET 2 | 실제 Runner 토큰으로 지정 두 Deployment 조회, UID가 관리자 전후 관측과 일치 |
| 앱 전후 | Deployment2/Pod6 Ready, UID·generation·spec·이미지·imageID·재시작 횟수 동일. 기존 재시작1인 Pod를 재시작0으로 표시하지 않음 |
| RBAC 정본 보완 | 전체 RoleBinding13/ClusterRoleBinding64를 limit500·continue 없음으로 조회. SA 직접/동명 User/기본 SA·authenticated Group에 대응하는 Binding5/Role5의 규칙과 메타데이터 전후 동일 |
| 회수 | broker/endpoint 완료 후 세 호스트의 해당 진단 Python 프로세스0, 공개 소스6개 폴더42파일 정확 해시·0600, 폴더0700. token 논리 참조 해제 ACK |

25개 SSAR는 **허가 판단 질의**다. 실제 금지된 변경·exec 호출을 하지 않았으며, 모든 API/verb/name/authorization mechanism을 전수 시험한 결과가 아니다. Role/Binding 관측에서는 두 named Deployment의 get/update/patch Role 외에 기본 self-review·discovery용 ClusterRole 4개가 보인다. 따라서 “모든 API 권한이 두 Deployment뿐”이라고 해석하지 않는다. D34의 기존 Deployment patch 잔여위험도 이번 진단으로 제거되지 않는다.

## 실행 순서·원본

1. `raw/pr82-before.json`, `raw/reviews82.json`, `references/pr82.json`으로 HEAD·리뷰·병합을 대조했다. 병합의 8개 코드 바이트는 reviewed HEAD와 같고, `raw/SOURCE_BINDING.json`은 SHA256/Git blob을 연결한다.
2. `raw/COORDINATION_EXTRACT.json`: Harbor·Ansible·D03 관련 세션은 21:50~22:10 창의 관련 변경을 보류했다. 발췌는 실행 후 조회한 메시지 사본이며 원래 세션이 출처다. 상태를 전체 프로젝트 승인으로 확대하지 않는다.
3. `*-before/`, `app-fresh/`, `runner-fresh/`는 bounded read-only SSH 수집. 전체 활동 Run 원문은 `*-fresh-runs.json`에 보존했다. 추가 자료에 포함된 과거 OCI 해시는 기존 범용 Runner 수집기의 부수 관측이며 본 AC07 입력이 아니다.
4. 공개 bundle `1d549ffabc0c4aeb7e2dc77b1e944f19b54a75bcc5e0e910dc35f570ce896bd9`을 신규 비공개 작업 경로에 전송해 대조했다. `native-preflight.*`는 토큰 미발급 PASS. `EXECUTE_INTENT.json`은 1회 시도 소진 기록이다.
5. `native-execute.stdout`은 broker의 원래 공개 결과, `.stderr`는 빈 원본, `.receipt.json`은 실제 명령·시각·rc0 및 stdout/stderr SHA256이다. **Actions dispatch Run이 아닌 SSH broker 진단**이며 CI 번호를 Runtime Run으로 쓰지 않는다. 발급 명령 1회와 API 서버의 정확히 한 번 처리 보장은 구분한다.
6. `app-after/`, `rbac-after/`, `runner-after/`, `cleanup-*`와 `POSTCHECK_SUMMARY.json`에 전후 비교·회수 범위를 담았다. `WINDOW_RELEASE.json`은 점유 해제 기록이다. 공개 소스는 원본 추적을 위해 남겼다.

초기 `rbac-before/` 수집기는 Kubernetes List 항목의 생략 가능한 `kind`를 직접 읽어 KeyError로 종료했다. 실패 원본(rc1·빈 stdout·stderr)을 보존했다. List 자체 kind/apiVersion 검증 후 item kind를 판별하도록 **조회 도구만** 보정한 `rbac-before-r2/`가 성공했다. 이 실패는 토큰 발급/설정 쓰기/Runtime 재시험이 아니다.

## 보안·완료 범위

- Token/Authorization 값·개인키·kubeconfig 원문은 편입하지 않는다. 토큰은 검토된 메모리·private pipe 경로를 거쳤다. 서버 폐기와 물리 메모리 소거를 수행했다고 주장하지 않는다.
- `expires_at`은 API/JWT로 확인한 만료값이다. 만료 후 서버401 관측이나 새 Token 복구를 하지 않았다. **AC08은 미실행**이다. 토큰값을 남겨 두고 나중에 시험하지 않는다.
- 이번 source-directory 검사와 프로세스 관측은 제한된 경로/사용자 범위다. 시스템 전체 로그·메모리·Artifact의 완전한 잔존 부재 검사로 확대하지 않는다.
- 공개 로그의 credential 하위 `runner_token_authentication=NOT_VERIFIED`는 CP1 검증 단계 기록이며 상위 Runner 실관측 `RUNNER_TOKEN_AUTH=PASS`와 구분한다. `SOURCE_APPROVAL=OPERATOR_PINNED_NOT_VERIFIED_IN_TOOL`은 broker가 GitHub 리뷰를 검사하지 않는다는 뜻이며 별도 GitHub 원본으로 결속했다.
- Pure GET 수집기와 로컬 orchestration은 `REVIEW=NOT PERFORMED (Pre-check)` 범위다. 토큰을 다루는 broker/native 코드는 PR82의 독립 검토·병합본이다. 증적 PR 자체의 독립 검토는 별도로 필요하다.
- **DEPLOY=NOT_EXECUTED, DELIVERY_GATE=NOT_VERIFIED**. AC07 증적 심사·Lead 최종 인수 뒤 AC08 진단 구현·리뷰, 이후 AC09 승인된 이전 Digest 복구 순서다. 이번 토큰 1회는 소진됐다.

## 로컬 재검증

이 폴더에서 `python3 -B verify.py`를 실행한다. 원본 hash·명령 rc·8개 source/blob·bundle·review·CI·25권한·두 UID·900초·앱/RBAC 전후·회수 관측을 오프라인 대조한다. 서버 호출·토큰 발급은 없다. `raw/*.py`는 당시 실행 경로의 사본이므로 증적 검토 과정에서 실행하지 않는다.

루트에서 `python3 tools/check-evidence-layout.py --base origin/main`으로 신규 회차·Manifest·대장 연결을 확인한다. 해시와 layout PASS는 실행 원본 진위나 독립 인수 승인을 대신하지 않는다.

관련 티켓: [CICD #11](https://github.com/321Team/infra-cicd/issues/11), [P1-CICD-01 #16](https://github.com/321Team/fds-project-baseline/issues/16). [AC05 증적229](https://github.com/321Team/fds-project-evidence/pull/229)은 별도 완료 이력으로 유지한다.
