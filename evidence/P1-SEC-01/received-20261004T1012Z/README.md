# P1-SEC-01 — 핵심 요구사항 3 보완: `monitoring-node:default` SA 읽기 전용 `can-i` 재수집 (2026-10-04)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 같은 날 앞 회차 [`received-20261004T0825Z`](../received-20261004T0825Z/README.md)에서 시험하지 않은 `system:serviceaccount:monitoring-node:default`(monitoring-node Namespace의 `default` SA)를 확인한다. 독립 리뷰 B-107-01(재환 님)과 PMO/QA 권장(권욱 님)에 따라, 앞 회차의 스크립트·원본·결과는 **수정하지 않고** `DEF` 한 줄만 바꾼 새 스크립트로 새 회차를 만들었다. 읽기 전용이며 클러스터 객체를 만들거나 바꾸지 않는다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-cani-core36-20261004T100847Z.tar.gz` |
| SHA-256 | `a9e5acd3820426490d802d7880ed851edd150dfba005ab9b7d45afda883dd33b` (같은 폴더 `.sha256` sidecar, 서버 콘솔 출력과 일치) |
| 수집 | k8s-control01, 계정 `server02`(sudo), 2026-10-04T10:08:47Z (19:08:47 KST). 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 스크립트 작성·수신 검증·편입 정리는 Claude Code 보조 |
| 전달 경로 | control01 → ansible01(`scp`, `~/p1-sec01-evidence/`) → 사용자가 zip으로 내려받아 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신 시각 | 2026-10-04 19:12 KST |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버 sidecar = 콘솔 출력(3자 일치). 아카이브 내부 `SHA256SUMS` 7개 항목 전부 일치(상위 디렉터리 기준).
- **실행 스크립트 바이트 해시 확인:** `scripts/collect-cani-core36b.sh`(SHA-256 `c984a9ecd4ae759c03f965c8ef0a933cb66877685bc7d967c16e656b6dc5ea1b`, 76줄)는 control01에서 실행된 파일을 `scp`로 가져온 것이며 작성 원본과 바이트 동일하다.
- **앞 회차 스크립트와의 차이는 정확히 한 줄이다**(`diff collect-cani-core36.sh collect-cani-core36b.sh`):
  ```
  16c16
  < DEF=system:serviceaccount:default:default
  ---
  > DEF=system:serviceaccount:monitoring-node:default
  ```
  앞 회차 스크립트(`96b1ccaf…aa64`)는 control01에 그대로 남아 있고 덮어쓰지 않았다.
- 비밀정보 검색 일치 0건.

## 관측값 (원본 보존 — 판정 아님)

`PASS=90 FAIL=0`. 주체별 행 수: `monitoring-node:node-exporter-sa` 28, **`monitoring-node:default` 28**, `ci-cd:cicd-runner-sa` 34.

`monitoring-node:default` 28개 점검은 **전부 `no`**이다: Workload 생성(deployments, statefulsets, daemonsets, jobs, cronjobs, replicasets, pods), Pod 서브리소스(`exec`·`attach`·`portforward`) create, 기존 daemonsets·deployments `update`·`patch`·`delete`, `serviceaccounts/token` create, `rolebindings`·`roles` create, Secret `get`·`list`, `*`, 권한 상승 경로(`clusterrolebindings` create, `clusterroles`의 `bind`·`escalate`, `users`·`groups`·`serviceaccounts`의 `impersonate`).
`01-sa-monitoring-node.txt`는 monitoring-node SA가 `default`와 `node-exporter-sa` 두 개임을 보여 준다. `node-exporter-sa`(28)와 `cicd-runner-sa`(34)도 앞 회차와 같은 결과로 다시 전부 기대와 일치했다.

## 한계와 주의

1. **이 회차의 `can-i --list` 파일(`11-…`)은 `node-exporter-sa` 기준이다.** 스크립트가 `--list`를 `node-exporter-sa`에만 수행하므로 `monitoring-node:default`의 `--list` 원본은 없다. `monitoring-node:default`는 28개 개별 `can-i` 결과로만 확인했다.
2. RBAC 평가 결과이며 Admission(PSA 등)이나 실제 Pod 생성 시도를 시험하지 않는다.
3. 주체 범위: `monitoring-node`의 SA 2개와 Runner SA만 시험했다. 사용자·그룹 등 SA 외 주체, 다른 Namespace의 SA가 monitoring-node에 접근하는 경로는 시험하지 않았다.
4. 한 시점(2026-10-04T10:08Z)의 결과이다. 앞 회차(08:16Z)와 약 2시간 차이이며 그 사이 RBAC 변경 여부는 확인하지 않았다.
5. 스크립트는 `infra-*` 저장소의 코드가 아니며 별도 코드 리뷰를 받지 않은 조회 전용 도구이다.
6. 앞 회차의 "`default:default`"는 `default` Namespace의 SA로 정정됐다. 이 회차가 그 시험을 대체하는 것이 아니라 보완한다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| 핵심 요구사항 3: monitoring-node 신규 Workload 생성 제한 | `results.tsv`의 `monitoring-node:default` 28행과 `node-exporter-sa` 28행 |
| 핵심 요구사항 6: Runner | 앞 회차 결과와 같음(34행) |

AC 체크, Gate, 티켓 상태는 이 PR로 바꾸지 않는다. 판정은 Review Owner·Lead가 #19에서 별도로 한다.
