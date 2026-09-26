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

- sidecar 일치(`bf3d2da6…`). 압축 내부 151개 파일, 내부 `SHA256SUMS`(tar.gz 루트) 전부 `OK`.
- 비밀정보 검색: `password|secret.{0,20}=|token.{0,20}=|BEGIN (RSA|EC|PRIVATE) KEY|postgresql://|ENC_KEY=` 패턴 0건.
- 압축을 다시 하거나 내용을 고치지 않았다. 이 폴더 `SHA256SUMS`는 이 README·원본·sidecar를 고정한다.

## 내용물 요약 (원본 보존 — 판정 아님)

| 하위 폴더/파일 | 내용 | 관련 baseline AC |
|---|---|---|
| `evidence-psa-20260926T125912Z/` | `01-psa-violation.sh` 결과: fds-app/monitoring-api/ci-cd 각 namespace의 psa-compliant(allow)와 privileged/hostnetwork/hostpid/hostpath/runasroot(전부 deny) 검증. monitoring-node의 hostnetwork는 설계대로 allow. `results.tsv`에 PASS/FAIL 요약 | SEC-AC-01 |
| `evidence-rbac-20260926T125917Z/`, `evidence-rbac-20260926T134922Z/` | `03-rbac-can-i-full.sh` 결과: SA 8개(transaction-api-sa, fds-engine-sa, node-exporter-sa, alertmanager-sa, grafana-sa, kube-state-metrics-sa, prometheus-sa, cicd-runner-sa) 존재·금지권한 미포함 확인. `can-i-list_*.txt`에 개별 `kubectl auth can-i --list` 원본 포함 | SEC-AC-03 (Positive 케이스 명시 확인은 별도 필요, README 하단 한계 참조) |
| `evidence-workload-deny-20260926T133305Z/`, `evidence-workload-deny-20260926T133726Z/` | `05-workload-deny.sh` 결과: 비승인 Workload(`fds-app/fds-engine`, `default/gap-probe`)의 worker(.105/.107) 9100/10250 접근 8/8 BLOCKED/TIMEOUT | SEC-AC-04 (Deny) |
| `evidence-prom-diag-20260926T125921Z/` `…T134600Z/` `…T143922Z/` `…T144802Z/` | `02-prometheus-9100-10250-diag.sh` 4회 실행분(시간순). 최초 실패(GNP 미비) → GNP 패치 후 여전히 kubelet SAN mismatch FAIL 3/3 → SAN 재발급 후 PASS 3/3. `targets.json`에 각 시점 Prometheus `/api/v1/targets` 원본 포함 | SEC-AC-04 (Allow) |
| `gnp-backup-20260926T132313Z/`, `gnp-backup-20260926T143747Z/` | Worker 3대(`fds-k8s-host-k8s-worker0{1,2,3}`) GNP 변경 전 snapshot(JSON) | SEC-AC-04 변경 이력 |
| `gnp-after-apply.yaml`, `targets-after-gnp.json` | Worker GNP apply 직후 상태 | SEC-AC-04 |
| `gnp-cp-backup-20260927T000029Z/` | Control Plane 3대(`fds-k8s-host-k8s-control0{1,2,3}`) GNP의 apply 전 원본(`.yaml`/`-current.json`)과 patch 후 내용(`-patched.json`, 10250 ingress source에 Worker 3대 IP `10.1.93.105/107/108` 추가) | SEC-AC-04 |
| `00-environment.txt` | 세션 실행 환경, `kubectl version`, `kubectl get nodes`(패치 완료 후 6/6 Ready) | — |
| `99-csr-final.txt` | 6개 kubelet-serving CSR(Worker 3 + CP 3) 전체 승인(`Approved,Issued`) 상태 | SEC-AC-04 선행 조치(kubelet 인증서) |

## 세션 중 발견·조치 요약 (baseline #19 코멘트와 대응)

1. **SEC-AC-01 실증**: PSA `restricted:v1.36`가 실제로 privileged/hostNetwork/hostPath/hostPID/runAsRoot Pod 생성을 거부함을 3개 namespace에서 확인. kube-system 예외 문서화는 이 회차 범위 밖(미수집).
2. **SEC-AC-04 Allow 미충족 원인 2건과 조치**:
   - Control Plane GNP(`fds-k8s-host-k8s-control0N`)의 10250 ingress 허용 source에 Prometheus 실제 소스(Worker 노드 IP, SNAT 후)가 누락 → Worker 3대 IP를 CP 3대 GNP에 추가(dry-run 검증 후 적용, canary control01 → 02/03 확대).
   - Worker·CP 6대 전부 kubelet serving 인증서가 IP SAN 없는 자체서명 상태(`serverTLSBootstrap` 미설정) → 6대 전부 `serverTLSBootstrap: true` 추가, kubelet 재시작, CSR 승인.
   - 조치 후 Prometheus target 15/15(kubelet 6, cadvisor 6, node-exporter 3) 전부 `up`, DOWN 0.

## 한계·미수신 (이번 회차에서 하지 않은 것)

- **kube-system PSA 예외**: 이번 `01-psa-violation.sh` 실행 범위에 kube-system이 없다. 별도 확인 필요.
- **RBAC Positive 케이스**: `can-i-list` 파일들은 `kubectl auth can-i --list` 결과이며, 각 SA가 실제로 허용돼야 할 개별 동작(예: prometheus-sa의 `nodes/metrics` get)을 `can-i <verb> <resource>` 형태로 명시 확인한 기록은 이 회차에 없다.
- **AC 최종 충족 판정**: 이 편입은 원본 보존이며, SEC-AC-01/03/04의 baseline AC 체크·Status 변경은 하지 않았다. AC 판정은 P1-SEC-01 Lead(이하영)가 baseline #19에서 별도로 한다.
- 이 tar.gz는 세션에서 사용자가 압축해 업로드한 것으로, `tools/collect-p1-sec-01-originals.sh`처럼 저장소에 등록된 수집기가 아니라 이번 세션 전용 ad-hoc 스크립트(`~/collect-p1-sec-01-20260926.sh`, control01 로컬)로 만들었다. 스크립트 자체는 이 편입에 포함하지 않았다.

이 편입은 원본 보존이다. P1-SEC-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
