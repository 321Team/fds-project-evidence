# P1-SEC-01 — AC-02 잔여 흐름 읽기 전용 시험: IF-12B, IF-13A, IF-03 (2026-10-04)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). AC-02(Allow/Deny 매트릭스) 중 증적이 비어 있던 세 흐름을 기존 Pod에서 읽기 전용으로 시험했다: **IF-12B**(control01 → 전 노드 kubelet 10250, `kubectl logs`/`exec`), **IF-13A**(워크로드 → CoreDNS와 DNS 외 egress 차단), **IF-03**(`fds-engine:8001` 승인 접속과 비승인 Pod 차단). Pod·정책 등 클러스터 객체를 만들거나 바꾸지 않는다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-ac02-residual-20261004T130105Z.tar.gz` |
| SHA-256 | `1087547663c339df8167d55056e7cc172bc3b678cffe2e52c172f51eea29ae55` (같은 폴더 `.sha256` sidecar, 서버 콘솔 출력, ansible01 재계산과 일치) |
| 수집 | k8s-control01, 계정 `server02`(sudo), 2026-10-04T13:01:05Z (22:01:05 KST). 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 스크립트 작성·수신 검증·편입 정리는 Claude Code 보조 |
| 전달 경로 | control01 → ansible01(`scp`, `~/p1-sec01-evidence/`) → 사용자가 zip으로 내려받아 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신 시각 | 2026-10-04 22:07 KST |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버 sidecar = 콘솔 출력(3자 일치). 아카이브 내부 `SHA256SUMS` 전 항목 일치(상위 디렉터리 기준 검증). 비밀정보 패턴 검색(`password|secret=|token=|BEGIN … KEY|bearer|authorization:`) 일치 0건.
- **실행 스크립트 바이트 확인:** `scripts/collect-ac02-residual-v3.sh`(SHA-256 `12ff2cdd5c1be597ea8ddc4c562c464e41679d3979dfe214ce3b17bde64231ae`, 119줄)는 control01에서 실행된 파일을 `scp`로 가져온 것이며 작성 원본과 바이트 동일하다.
- 스크립트는 Pod를 만들지 않는다. 기존 Pod에서 `kubectl exec`로 짧은 TCP 접속·이름 조회만 하고, `calico-node` Pod에 `logs --tail=1`과 `exec -- ls /`를 수행한다.

## 관측값 (원본 보존 — 판정 아님)

`PASS=23 FAIL=0 SKIP=1 CHECK=0`, `IF-03 unapproved negative executed and passed: 3 pod(s)` (`99-summary.txt`).

| 흐름 | 시험 | 결과 |
|---|---|---|
| IF-12B | control01 → 노드 6대(`k8s-control01~03`, `k8s-worker01~03`)의 calico-node Pod에 `logs`, `exec` 각 1회 | 12/12 `OK`. 노드별 `logs-<노드>.txt`, `exec-<노드>.txt` 12개 보존. Pod↔노드 매핑은 `05-calico-node-pods.txt` |
| IF-13A | `fds-engine` Pod에서 `kubernetes.default` 조회, `transaction-api` Pod에서 `fds-engine.fds-app` 조회, kube-dns ClusterIP `10.96.0.10:53` TCP | 3/3 `RESOLVED`/`CONNECTED` |
| IF-13A | `fds-engine` → `transaction-api:8000`, `db01 10.1.93.55:5432`, `8.8.8.8:53`, `1.1.1.1:443` | 4/4 `TIMEOUT`(차단 기대와 일치) |
| IF-03 | `transaction-api` → `fds-engine:8001` | `CONNECTED` |
| IF-03 | `monitoring-api`의 prometheus·alertmanager·grafana → `fds-engine:8001` | 3/3 `TIMEOUT` (`nc -w 3`, 경과 시간 ≥2초로 즉시 거부와 구분) |
| IF-03 | `monitoring-api`의 `kube-state-metrics` → `fds-engine:8001` | **SKIP** (`NO_TOOL`: 컨테이너에 `sh`가 없어 시험하지 못함) |

## 같은 날 만든 다른 실행 (이 폴더에 포함하지 않음, 은닉 아님)

이 시험은 한 번에 완성되지 않았고 스크립트를 고쳐 가며 4회 더 실행했다. 아래는 control01·ansible01에 원본이 남아 있으며 이 PR에는 넣지 않았다.

| 실행(UTC) | 아카이브 SHA-256 앞 16자리 | 이 PR에서의 취급 |
|---|---|---|
| 10:42:47Z | `f84cc258cc729716` | 스크립트 v1(`c54337b2…`). IF-13A 7/7·IF-03 승인 PASS였으나 `nc -z`가 타임아웃과 거부를 구분하지 못해 IF-03 비승인 Negative는 판정 불가(`CHECK` 3, `FAIL` 1), IF-12B는 조회가 0건 |
| 10:46:16Z, 10:53:01Z | `73b6b3ac0e34dcd1`, `7e2058a58ed7e2ed` | 실행에 쓴 스크립트 바이트가 보존되지 않아 증적에서 제외. 결과는 아래 11:23Z와 같음 |
| 11:23:44Z | `f7f99bc04d68ada7` | 스크립트 v2(`d96e3ca6…`, 바이트 확인). 결과는 이 회차와 같지만 IF-12B의 노드 열이 노드 이름이 아니라 Pod 나이(`16d`/`24d`)로 기록되고 파일명이 겹쳐 노드별 매핑을 확인할 수 없어 이 회차(v3)로 대체 |

v2와 v3의 차이는 `05-calico-node-pods.txt`를 만드는 한 줄뿐이다(`-o wide`의 `awk $8`을 `-o custom-columns=…NODE:.spec.nodeName`으로 교체). 시험 흐름은 같다.

## 한계와 주의

1. **IF-12B는 허용되는 쪽의 확인이다.** control01(CP)에서 노드로의 `logs`/`exec`가 성공함을 보인다. CP 외 출발지가 10250에 접근하지 못한다는 차단 쪽 시험은 이 회차에 없다.
2. **`TIMEOUT`은 차단과 다른 원인(대상 무응답)을 단독으로 구분하지 못한다.** 같은 회차에서 같은 대상(IF-03의 `fds-engine:8001`, IF-13A의 kube-dns)에 승인된 출발지는 `CONNECTED`였다는 점이 보조 근거이며, DNS 외 대상(`db01:5432`, `8.8.8.8`, `1.1.1.1`)의 차단은 정책 파일 확인이 아닌 접속 결과만이다.
3. **IF-03 비승인 Negative는 3개 Pod, 도구가 `nc`다.** 승인 접속은 `python`으로 시험해 도구가 다르다. `kube-state-metrics`는 시험하지 못했다.
4. **시도는 Pod당 1회, 제한시간 3초다.** 한 시점(2026-10-04T13:01Z)의 결과이다.
5. 시험 대상은 이 회차에 포함된 흐름뿐이다. IF-12A·12C, IF-05C, IF-06B, IF-09, IF-10, IF-13A의 Deny 행 전반은 이 시험이 다루지 않는다.
6. 스크립트는 `infra-*` 저장소의 코드가 아니며 별도 코드 리뷰를 받지 않은 조회 전용 도구다. 가짜 `kubectl`·`nc` 스텁에서 로컬 확인을 했으나 이는 증적이 아니다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| AC-02 IF-12B | `results.tsv`의 IF-12B 12행, `05-calico-node-pods.txt`, `logs-*.txt`, `exec-*.txt` |
| AC-02 IF-13A | `results.tsv`의 IF-13A 7행 |
| AC-02 IF-03 | `results.tsv`의 IF-03 5행 |

AC 체크, Gate, 티켓 상태는 이 PR로 바꾸지 않는다. 각 흐름의 판정(MET/RISK/Known Issue)은 Review Owner·Lead가 #19에서 별도로 한다.
