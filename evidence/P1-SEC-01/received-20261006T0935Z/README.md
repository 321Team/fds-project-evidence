# P1-SEC-01 — AC-03 can-i 보완 수집 원본: RC 결속 재수집 81행 + prometheus-sa `/metrics` 기록 (2026-10-06)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). #107(`collect-cani-core36b.sh`, 2026-10-04) 증적은 `kubectl auth can-i`의 종료코드(RC)와 stderr를 버렸다. Review Owner [딥리뷰 6010258709](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6010258709) §3에 따라, **#49 `verify-rbac.sh`(yes=rc0/no=rc1 짝·timeout 검증)와 같은 항목이 없는 행만** RC를 행별로 결속해 다시 읽었다. 읽기 전용(`auth can-i`, `get`)이며 클러스터 객체를 만들거나 바꾸지 않는다. 이 폴더는 관측 원본이며 **AC-03 MET 판정이 아니다.**

## 출처와 수신

| 항목 | 값 |
|---|---|
| 수집기 | `scripts/collect-cani-gap.sh` rev `v3-20261006`, SHA-256 `a7754f5dc41b2f8a7998847bc898152c3a1eb2646fae4ba0fa79545441bb92b4` (병합본과 일치, `00-environment.txt`의 `script_sha256`과 같음). `infra-kubernetes` [PR #64](https://github.com/321Team/infra-kubernetes/pull/64) merge `bbffdcae0292e59382cb6c6c16fc66aaed161464` (HEAD `b9bb02f`) |
| 실행 | `k8s-control01`, 계정 `server02`(sudo), 2026-10-06T09:27:45Z (18:27:45 KST), `TIER=AB`. 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 수신 검증·편입 정리는 Claude Code 보조 |
| 서버 버전 | Client·Server `v1.36.4` (`00-environment.txt`) |
| 전달 경로 | ansible01 clone(병합 커밋 checkout) → `scp`로 control01 복사 → control01에서 실행 → ansible01이 결과를 `scp`로 가져옴 → 사용자가 zip으로 공유 폴더에 올려 세션에 전달 → 압축 해제 후 해시 재확인 |
| 수신 시각 | 2026-10-06 (편입 정리 18:3x KST) |

| 아카이브 | SHA-256 |
|---|---|
| `p1-sec01-cani-gap-v3-20261006T092745Z.tar.gz` | `2f3e82ac32a68126c3decac5ea1d44da57ff392aec2a41fa5ee3774b2460667a` |

## 수신 검증

- 아카이브 바이트 SHA-256 = 서버 sidecar(`.sha256`) = control01 콘솔 출력 = ansible01 재계산(4자 일치). 아카이브 내부 `SHA256SUMS` 270개 항목 전부 일치(총 271개 파일). 비밀정보 패턴 검색 일치 0건.
- 실행 스크립트 SHA-256은 병합된 `ops/p1-sec01-cani-gap/collect-cani-gap.sh`와 같다. 시작 전 ansible01·control01에서 패키지 `SHA256SUMS` 일치(4개 항목)를 확인했다.
- `run-console.txt`는 control01에서 수집기 출력을 `tee`한 **서버 파일**이다. 콘솔에 함께 찍힌 `PROCESS_RC=0`은 `tee` 밖에서 출력되어 이 파일에 없으며, 같은 값이 `completion.txt`의 `EXIT_CODE=0`에 있다.

## 관측값 (원본 보존 — 판정 아님)

`EXPECTED=81 GOT=81 TOTAL=83 UNIQUE_IDS=83 PASS=81 FAIL=0 ERROR_OR_TIMEOUT=0 RECORD_ONLY=2 AUX_RC_NONZERO=0`, `COLLECTOR_STATUS=COMPLETE`, `SEAL_STATUS=COMPLETE`, `EXIT_CODE=0`. 사전 점검은 관리자 `yes`/rc0, 가짜 SA `no`/rc1로 정상(`00-precheck.txt`). 모든 행에 RC가 기록되어 있다(rc 0: 6행, rc 1: 77행, 그 외 없음).

| 주체 | 행 수 | 결과 |
|---|---|---|
| `ci-cd:cicd-runner-sa` | 25 | 기대 `yes` 5행(transaction-api get·patch, fds-engine get·update·patch)은 `yes`/rc0, 기대 `no` 20행은 `no`/rc1 |
| `monitoring-node:default` | 28 | 28행 모두 `no`/rc1 (기대 `no`) |
| `monitoring-node:node-exporter-sa` | 28 | 28행 모두 `no`/rc1 (기대 `no`) |
| `monitoring-api:prometheus-sa` | 2 (RECORD) | 아래 참조 |

### 기록 전용 2행 — 기대값 없음 (`RECORD`)

| ID | 질의 | 결과 |
|---|---|---|
| M001 | `get /metrics` (non-resource URL) | **`no` / rc 1** |
| M002 | `get nodes --subresource=metrics` | `yes` / rc 0 |

- **`/metrics`(non-resource)는 현재 `no`다.** 권한을 추가하지 않았고 그대로 기록했다.
- 적용된 Binding 원본(`20-*`, `21-clusterrolebindings.json`, 5개 수집 모두 rc 0): `prometheus-sa`가 주체인 ClusterRoleBinding은 `prometheus-sa-kubelet-metrics` 하나이며, 이 ClusterRole은 `nodes/metrics` `get`만 허용한다(10-02 [evidence#99](https://github.com/321Team/fds-project-evidence/pull/99) `48-prometheus-clusterrole.yaml`와 같은 구성). ClusterRole `prometheus-role`(09-22)과 `prometheus-kubelet-scrape`(09-22, `nonResourceURLs: /metrics, /metrics/cadvisor` 포함)는 아직 존재하지만 이 시점에 `prometheus-sa`에 묶인 Binding에서 보이지 않는다.
- 09-26 [evidence#49](https://github.com/321Team/fds-project-evidence/pull/49)의 `get /metrics` `yes`는 그 시점의 Role 구성(위 두 ClusterRole 포함)에서의 결과이며, 현재 값과 다르다. 이 차이가 의도된 최소권한 전환인지, 설계상 `/metrics`가 필요한지는 이 증적으로 판정하지 않는다(Review Owner·MON 확인 필요).

## 행 대조 (정정)

- "36건"은 요구사항 번호(3·6)이고 #107 수집 표는 **90행**(node-exporter-sa 28 + monitoring-node:default 28 + Runner 34)이다.
- 이 수집은 그중 **81행**을 대상으로 했다. #49의 RC 검증 증적과 같은 항목인 Runner 9행(create/delete deployments, update deployment/transaction-api·other-app, get·list secrets, create pods/exec, create rolebindings, `* *`)은 재수집에서 제외했다. 근거와 행 목록은 `infra-kubernetes` `ops/p1-sec01-cani-gap/README.md`와 수집기 소스에 있다.
- #107의 기존 PASS 90행은 수정하지 않았다. 이 폴더는 그 RC 신뢰성의 보완 근거다.

## 실행상의 기록 (은닉 아님)

- control01로 복사하는 첫 시도에서 호스트 이름이 풀리지 않아 IP로 다시 복사했고, 결과 회수 첫 시도는 `scp`가 중괄호 묶음을 해석하지 못해 실패했다. 두 경우 모두 서버 상태와 시험 결과에 영향이 없다.
- 수집기 병합 시 독립 리뷰: 이재환(`supreme33-kr`)의 승인은 수정 전 HEAD `869bb2e`에 대한 것이고, 수정 HEAD `b9bb02f`는 Review Owner 이권욱이 승인·병합했다. 수집기 소스의 새 HEAD에 대한 이재환 승인은 없다.

## 한계와 주의

1. **한 시점(2026-10-06 18:27 KST) 결과이며 `can-i`는 authorization 평가 증적이다.** 실제 Token 인증, Admission(PSA), 업무 객체 변경 시험이 아니다.
2. SA 외 주체(사용자·그룹)와 TokenRequest 정책은 시험하지 않았다.
3. 보조 수집(Binding/Role 목록)은 판정에 쓰이지 않는 참고 원본이다.
4. 행 누락·중복 경로(종료코드 12)는 수집기 로컬 시험에서 재현하지 못했다(수집기 README 한계). 이번 실행은 81행이 모두 있고 ID가 중복 없음을 `GOT`/`UNIQUE_IDS`로 확인했다.

## AC와의 대응 (판정이 아니라 연결)

| #19 항목 | 관련 파일 |
|---|---|
| AC-03 SA별 can-i (RC 결속 보완) | 아카이브 `results.tsv`, `raw/<ID>.{stdout,stderr,rc}`, `99-summary-provisional.txt` |
| 핵심 요구 3 (monitoring-node 생성 제한) | `monitoring-node:default`·`node-exporter-sa` 56행 |
| 핵심 요구 6 (Runner 기존 2개 Deployment만) | `ci-cd:cicd-runner-sa` 25행 |
| 핵심 요구 5 (Prometheus 권한) | M001·M002, `20-*`, `21-clusterrolebindings.json` |
