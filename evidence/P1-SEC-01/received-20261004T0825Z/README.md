# P1-SEC-01 — 핵심 요구사항 3·6 간접 권한 읽기 전용 `can-i` 시험 (2026-10-04)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 핵심 요구사항 3(monitoring-node 신규 Workload 생성 제한)과 6(Runner는 기존 2개 Deployment `get/update/patch`만 허용)에 대해, [evidence#99](https://github.com/321Team/fds-project-evidence/pull/99) 리뷰가 "직접 create 권한만 확인, 간접 경로 NOT_VERIFIED"로 남긴 범위와 evidence#49가 `transaction-api`만 시험한 범위를 보완하는 **읽기 전용** 시험이다. 클러스터 객체를 만들거나 바꾸지 않는다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-cani-core36-20261004T081607Z.tar.gz` |
| SHA-256 | `3cc4c44be2587399427bc3b2e84603c09dd1447bd1d411cd5cfa8a3996bf06ae` (같은 폴더 `.sha256` sidecar, 서버 콘솔 출력과 일치) |
| 수집 | k8s-control01, 계정 `server02`(sudo), 2026-10-04T08:16:07Z (17:16:07 KST). 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 스크립트 작성·수신 검증·편입 정리는 Claude Code 보조 |
| 전달 경로 | control01 → ansible01(`scp`, `~/p1-sec01-evidence/`) → 사용자가 zip으로 내려받아 세션에 전달 → 세션에서 압축 해제 후 해시 재확인 |
| 수신 시각 | 2026-10-04 17:2x KST 이후 |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버가 만든 sidecar = 콘솔에 출력된 해시(3자 일치).
- 아카이브 내부 `SHA256SUMS` 7개 항목 전부 일치. 이 Manifest의 경로는 폴더 이름으로 시작하므로 **상위 디렉터리에서** `sha256sum -c`로 검증한다(폴더 안에서 실행하면 경로를 찾지 못한다).
- **실행한 스크립트의 바이트 해시를 확인했다.** `scripts/collect-cani-core36.sh`(SHA-256 `96b1ccaf45303ee06617bdf77cfd21944bc818baa36a6f7219feccc544cdaa64`, 76줄)는 control01에서 실제 실행된 파일을 `scp`로 가져온 것이며, 작성 원본(로컬 저장소 사본)과 바이트 동일하다. 앞선 수집(#99)의 "실행본 해시 미수신" 한계는 이 수집에는 해당하지 않는다.
- 비밀정보 검색(`password|secret=|token=|BEGIN … KEY|bearer|authorization:`): 일치 0건.

## 내용물 (원본 보존 — 판정 아님)

| 파일 | 내용 |
|---|---|
| `results.tsv` | 90개 점검 결과(`result expect actual subject ns verb resource sub`) |
| `99-summary.txt` | `PASS=90 FAIL=0` |
| `00-environment.txt` | 실행 시각, 호스트, kubectl 버전(v1.36.4) |
| `01-sa-monitoring-node.txt`, `02-sa-ci-cd.txt` | 두 Namespace의 ServiceAccount 목록 |
| `10-runner-list-fds-app.txt` | `cicd-runner-sa`의 `fds-app` `auth can-i --list` |
| `11-nodeexp-list-monitoring-node.txt` | `node-exporter-sa`의 `monitoring-node` `auth can-i --list` |

## 관측값

**핵심 요구사항 3 — monitoring-node** (대상: `node-exporter-sa`, `default:default`. `monitoring-node` Namespace의 ServiceAccount는 이 둘뿐이다) — 각 28개 점검, **전부 `no`**:
- 생성: deployments, statefulsets, daemonsets, jobs, cronjobs, replicasets, pods
- Pod 서브리소스 create: `exec`, `attach`, `portforward`
- 기존 Workload 수정: daemonsets·deployments 각각 `update`·`patch`·`delete`
- `serviceaccounts/token` create, `rolebindings`·`roles` create, Secret `get`·`list`, `*`
- 권한 상승 경로: `clusterrolebindings` create, `clusterroles`의 `bind`·`escalate`, `users`·`groups`·`serviceaccounts`의 `impersonate`
- `node-exporter-sa`의 `can-i --list`(monitoring-node)에는 SelfSubject 검토 3종과 Non-Resource URL(`get`)뿐이며 Workload·Secret·RBAC 관련 규칙이 없다.

**핵심 요구사항 6 — Runner** (`cicd-runner-sa`, `fds-app`) — 34개 점검, **전부 기대와 일치**:
- `yes` 6건: `transaction-api`와 `fds-engine` 각각에 대해 `get`·`update`·`patch`.
- `no`: 두 Deployment `delete`, `other-app` `get/update/patch/delete`, deployments `create/list/delete`, statefulsets·daemonsets·jobs·replicasets·pods create, daemonsets·statefulsets update, `pods/exec` create, Secret `get/list`, rolebindings create, 권한 상승 경로(`clusterrolebindings` create, `bind`, `escalate`, `impersonate`), `kube-system`·`monitoring-api`의 deployments `get`, `*`(전 Namespace).
- `can-i --list`(fds-app): `deployments.apps`는 **리소스 이름이 `fds-engine`, `transaction-api`로 제한된 `[get update patch]`뿐**이다. 목록·삭제 규칙이 없다.

## 한계와 주의

1. **RBAC 평가 결과이다.** `auth can-i`는 Authorization 결과를 묻는 것이며 Admission(PSA 등)이나 실제 Pod 생성 시도를 시험하지 않는다.
2. **주체 범위.** monitoring-node는 SA 2개(`node-exporter-sa`, `default`)만 시험했다. 사용자·그룹 등 SA 외 주체, 다른 Namespace의 SA가 monitoring-node에 접근하는 경로는 시험하지 않았다. Runner는 `cicd-runner-sa`만 시험했다.
3. **Runner 범위.** `fds-app` 안의 항목과 `kube-system`·`monitoring-api`의 deployments `get`만 대표로 확인했다. 모든 Namespace의 모든 리소스를 열거한 것이 아니며, 전 Namespace `*` 권한이 없음(`no`)을 확인했다.
4. **TokenRequest 정책은 포함하지 않았다.** `cicd-runner-sa` 토큰의 수명·발급 정책(#19 In Scope의 "Role/TokenRequest 정책")은 이 시험 대상이 아니다.
5. **한 시점의 결과이다.** 2026-10-04T08:16Z 한 번 실행했다. RBAC가 이후 바뀌면 달라질 수 있다.
6. 이 스크립트는 `infra-*` 저장소의 코드가 아니며 별도 코드 리뷰를 받지 않았다(조회 전용). 가짜 `kubectl` 스텁에서 정상·결함 주입 시험을 로컬로 확인했으나 이 확인은 증적이 아니다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| 핵심 요구사항 3: monitoring-node 신규 Workload 생성 제한 | `results.tsv`(두 주체 × 28개 = 56개: Namespace 범위 44 + 클러스터 범위 12), `11-nodeexp-list-monitoring-node.txt` |
| 핵심 요구사항 6: Runner는 기존 2개 Deployment `get/update/patch`만 | `results.tsv`(Runner 34개), `10-runner-list-fds-app.txt` |
| AC-03 SA별 `can-i` (보강) | 위 두 항목 |

AC 체크, Gate, 티켓 상태는 이 PR로 바꾸지 않는다. 판정은 Review Owner·Lead가 #19에서 별도로 한다.
