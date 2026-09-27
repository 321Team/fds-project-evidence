# P1-SEC-01 — PSA·RBAC·Prometheus Allow/Deny 현장 실행 세션 수집본 (2026-09-26)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 앞 수집회차: [received-20260926T034804Z](../received-20260926T034804Z/README.md).

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec-01-20260926-session-20260926T152344Z.tar.gz`, 75,241 bytes |
| SHA-256 | `bf3d2da6efad25adb4bdb0bf314d6ecaa1a9a95a0b6c7537ec9d0183e96c8ded`. 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 | k8s-control01, `server02`, 2026-09-26 15:23:44 UTC 압축(내부 파일은 12:59:12Z~15:22:44Z 사이 여러 스크립트 실행분을 한 번에 묶음) |
| 수집 방법 | `~/p1-sec01/scripts/sec-evidence/` 아래 기존 평가 스크립트(`01-psa-violation.sh`, `02-prometheus-9100-10250-diag.sh`, `03-rbac-can-i-full.sh`, `05-workload-deny.sh`)의 개별 실행 결과 폴더와, GNP 패치 작업의 백업/patch JSON을 하나의 tar.gz로 묶음(ad-hoc 수집, `tools/collect-p1-sec-01-originals.sh`와 별개) |
| 전달 경로 | control01 → ansible01(`scp`, `sha256sum` 재계산 일치 확인) → 사용자가 ZIP으로 압축해 이 세션에 업로드 → 세션에서 압축 해제 후 SHA-256 재확인 |
| 수신 시각 | 2026-09-26T15:52Z(세션 업로드 기준) |
| 수집·제공 | 이하영(P1-SEC-01 Lead, 세션 조작자). 수집·편입 정리는 Claude Code 보조 |

## 수신 검증

- sidecar 일치(`bf3d2da6…`). 압축 내부 tar member 151개(파일 138개 + 디렉터리 13개; 파일 수는 `registry/ARCHIVE_CONTENTS.json`의 entries 138과 일치). 내부 `SHA256SUMS`(tar.gz 루트, 파일 138개 대상) 전부 `OK`.
- 비밀정보 검색: `password|secret.{0,20}=|token.{0,20}=|BEGIN (RSA|EC|PRIVATE) KEY|postgresql://|ENC_KEY=` 패턴 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 이 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

## 내용물 요약 (원본 보존 — 판정 아님)

| 하위 폴더/파일 | 내용 | 관련 baseline AC |
|---|---|---|
| `evidence-psa-20260926T125912Z/` | `01-psa-violation.sh` 결과: fds-app/monitoring-api/ci-cd 각 namespace의 psa-compliant(allow)와 privileged/hostnetwork/hostpid/hostpath/runasroot(전부 deny) 검증. monitoring-node의 hostnetwork는 설계대로 allow. `results.tsv`에 PASS/FAIL 요약 | SEC-AC-01 |
| `evidence-rbac-20260926T125917Z/`, `evidence-rbac-20260926T134922Z/` | `03-rbac-can-i-full.sh` 결과: SA 8개(transaction-api-sa, fds-engine-sa, node-exporter-sa, alertmanager-sa, grafana-sa, kube-state-metrics-sa, prometheus-sa, cicd-runner-sa) 존재·금지권한 미포함 확인. `can-i-list_*.txt`에 `kubectl auth can-i --list` 원본, **`verify-rbac.tsv`에 8개 SA 전체의 개별 Positive/Negative `can-i <verb> <resource>` 확인 30건 포함**(예: `prometheus-sa get nodes --subresource=metrics`=yes, `get /metrics`=yes, `kube-state-metrics-sa list pods/deployments -A`=yes, `cicd-runner-sa update deployment/transaction-api`=yes·`update deployment/other-app`(resourceNames 제한)=no, 각 SA `get/list secrets`=no 등) | SEC-AC-03 |
| `evidence-workload-deny-20260926T133305Z/`, `evidence-workload-deny-20260926T133726Z/` | `05-workload-deny.sh` **2회 실행**. **T133305Z(1차): `fds-app/fds-engine` 4건 PASS(BLOCKED/TIMEOUT), `default/gap-probe` 4건 FAIL(비승인 접근이 실제로 CONNECTED됨 — 이 시점 차단 미완성)**. **T133726Z(2차, 재검증): 8/8 전부 PASS(BLOCKED/TIMEOUT)**. 두 회차 사이에 무엇이 조치됐는지는 이 회차 수집 범위에 없음(1차는 이 세션 대화 시작 이전에 실행된 것으로 추정, 조치 내용 미확인). **최종 판정은 T133726Z 기준.** | SEC-AC-04 (Deny) |
| `evidence-prom-diag-20260926T125921Z/` `…T134600Z/` `…T143922Z/` `…T144802Z/` | `02-prometheus-9100-10250-diag.sh` 4회 실행분(시간순). 최초 실패(GNP 미비) → GNP 패치 후 여전히 kubelet SAN mismatch FAIL 3/3 → SAN 재발급 후 PASS 3/3. `targets.json`에 각 시점 Prometheus `/api/v1/targets` 원본 포함 | SEC-AC-04 (Allow) |
| `gnp-backup-20260926T132313Z/`, `gnp-backup-20260926T143747Z/` | Worker 3대(`fds-k8s-host-k8s-worker0{1,2,3}`) GNP 변경 전 snapshot(JSON) | SEC-AC-04 변경 이력 |
| `gnp-after-apply.yaml`, `targets-after-gnp.json` | Worker GNP apply 직후 상태 | SEC-AC-04 |
| `gnp-cp-backup-20260927T000029Z/` | Control Plane 3대(`fds-k8s-host-k8s-control0{1,2,3}`) GNP의 apply 전 원본(`.yaml`/`-current.json`)과 patch 후 내용(`-patched.json`, 10250 ingress source에 Worker 3대 IP `10.1.93.105/107/108` 추가). **폴더명 시각 표기 정정: 이름의 `Z`는 실제로는 KST 벽시계 시각이며 UTC가 아니다**(생성 명령이 `date +%Y%m%dT%H%M%SZ`를 `-u` 없이 사용해 로컬(KST) 시각에 리터럴 `Z`를 붙임). 실제 UTC로는 `2026-09-26T15:00:29Z` 부근(archive 수집시각 `15:23:44Z`보다 약 23분 전)이며, tar 최상위 `STAMP`(`date -u` 사용, 진짜 UTC)와는 생성 방식이 다르다. 이 세션에서 만든 `gnp-backup-*`, `*.bak-*` 류 폴더/파일명도 동일하게 KST를 `Z`로 잘못 표기했을 가능성이 높다(개별 재검증 안 함). 원본 폴더/파일명 자체는 바꾸지 않았다. | SEC-AC-04 |
| `00-environment.txt` | 세션 실행 환경, `kubectl version`, `kubectl get nodes`(패치 완료 후 6/6 Ready) | — |
| `99-csr-final.txt` | 6개 kubelet-serving CSR(Worker 3 + CP 3) 전체 승인(`Approved,Issued`) 상태 | SEC-AC-04 선행 조치(kubelet 인증서) |

## 세션 중 발견·조치 요약 (baseline #19 코멘트와 대응)

1. **SEC-AC-01 실증**: PSA `restricted:v1.36`가 실제로 privileged/hostNetwork/hostPath/hostPID/runAsRoot Pod 생성을 거부함을 3개 namespace에서 확인. kube-system 예외 문서화는 이 회차 범위 밖(미수집).
2. **SEC-AC-04 Allow 미충족 원인 2건과 조치**:
   - Control Plane GNP(`fds-k8s-host-k8s-control0N`)의 10250 ingress 허용 source에 Prometheus 실제 소스(Worker 노드 IP, SNAT 후)가 누락 → Worker 3대 IP를 CP 3대 GNP에 추가(dry-run 검증 후 적용, canary control01 → 02/03 확대).
   - Worker·CP 6대 전부 kubelet serving 인증서가 IP SAN 없는 자체서명 상태(`serverTLSBootstrap` 미설정) → 6대 전부 `serverTLSBootstrap: true` 추가, kubelet 재시작, CSR 승인.
   - 조치 후 Prometheus target 15/15(kubelet 6, cadvisor 6, node-exporter 3) 전부 `up`, DOWN 0.

## 한계·미수신 (이번 회차에서 하지 않은 것)

- **kube-system PSA 예외**: 이번 `01-psa-violation.sh` 실행 범위에 kube-system이 없다. 별도 확인 필요. (kube-system 라벨 자체는 같은 날 baseline #19에서 별도로 적용됐으나, 이 편입에는 그 원본이 없다.)
- **RBAC Positive 케이스 커버리지**: `verify-rbac.tsv`에 8개 SA 전체의 Positive/Negative가 이미 있으나(위 표 참조), 이 30건이 baseline SEC-AC-03이 요구하는 전체 요구 매트릭스를 다 덮는지(예: 모든 리소스 조합)는 이 편입만으로 단정하지 않는다.
- **AC 최종 충족 판정**: 이 편입은 원본 보존이며, SEC-AC-01/03/04의 baseline AC 체크·Status 변경은 하지 않았다. AC 판정은 P1-SEC-01 Lead(이하영)가 baseline #19에서 별도로 한다.
- 이 tar.gz는 세션에서 사용자가 압축해 업로드한 것으로, `tools/collect-p1-sec-01-originals.sh`처럼 저장소에 등록된 수집기가 아니라 이번 세션 전용 ad-hoc 스크립트(`~/collect-p1-sec-01-20260926.sh`, control01 로컬)로 만들었다. 스크립트 자체는 이 편입에 포함하지 않았다.

## 독립 검토 반영 (2026-09-26, GWONUK 리뷰 B1~B4)

원본 파일(tar.gz, sidecar)은 변경하지 않았고, 이 README의 오표기만 정정했다.

- **B1 (workload-deny 이력 오표기)**: "8/8 BLOCKED/TIMEOUT"로 두 회차를 뭉뚱그렸던 것을 T133305Z(4 PASS/4 FAIL)→T133726Z(8/8 PASS) 2단계로 분리 기록.
- **B2 (파일 개수 오표기)**: "151개 파일"을 "tar member 151개(파일 138 + 디렉터리 13)"로 정정, `ARCHIVE_CONTENTS.json`(138)과 일치시킴.
- **B3 (RBAC Positive 오기록)**: "Positive 미수신"이 틀렸음을 확인 — `verify-rbac.tsv`에 이미 8개 SA 전체 Positive/Negative 30건이 있었다. 표·한계 절 정정.
- **B4 (timestamp 시간대 불일치)**: `gnp-cp-backup-20260927T000029Z` 등 세션 내 일부 폴더명의 `Z`가 실제로는 UTC가 아니라 KST임을 확인·명시.

## 후속 정정 — 실제 SA 불일치 발견 (2026-09-27)

**이 편입 자체(원본 tar.gz)는 변경하지 않으며, 아래는 해석상 주의사항 추가다.** 2026-09-27 infra-monitoring 실제 매니페스트·라이브 클러스터 대조 결과, 위 §"내용물 요약"의 `prometheus-sa`/`alertmanager-sa`/`grafana-sa`는 **실제 운영 중인 Pod가 쓰는 SA가 아님**을 확인했다.

```
kubectl -n monitoring-api get pod -l app=prometheus   -o jsonpath='{.items[0].spec.serviceAccountName}'  → prometheus
kubectl -n monitoring-api get pod -l app=alertmanager -o jsonpath='{...}'                                 → default
kubectl -n monitoring-api get pod -l app=grafana      -o jsonpath='{...}'                                 → default
```

`prometheus-sa`/`alertmanager-sa`/`grafana-sa`는 네임스페이스에 객체로는 존재하나(`kubectl get sa` 확인) 아무 Pod도 참조하지 않는 미사용 SA다. 이 tar.gz의 `can-i-list_monitoring-api_prometheus-sa.txt`·`verify-rbac.tsv`의 prometheus-sa/alertmanager-sa/grafana-sa 관련 행은 **실제 운영 identity가 아닌 미사용 SA를 검증한 결과**이며, kube-state-metrics-sa·node-exporter-sa는 실제 사용 SA와 일치해 그대로 유효하다.

실제 `prometheus` SA(`ClusterRoleBinding prometheus-kubelet-scrape`)는 이번 tar.gz에 포함되지 않은 추가 조회(2026-09-27, baseline #19 참조)로 `nodes`(get/list/watch)·`nodes/metrics`(get/list/watch)·`/metrics/cadvisor`를 가지며, `nodes/proxy`·`secrets`는 여전히 `no`(baseline 보안 요구사항은 유지). 다만 baseline 명세("`nodes/metrics`와 `/metrics`만")보다 넓은 `nodes` 전체 리소스 권한을 갖고 있어 명세 불일치가 있다. 상세: [baseline #19 코멘트](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5853235663).

이 편입은 원본 보존이다. P1-SEC-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
