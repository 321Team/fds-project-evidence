# P1-MON-01 — AC 근거 보완 조회 3회차 (2026-09-26, k8s-control01)

[증적 보완 요청 대응표](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5843098390)의 "읽기 전용 조회로 보완 가능한 것"을 MON Lead(이재환)가 k8s-control01(`server02`)에서 수집했다. **run1~3은 조회(GET)만 했고 클러스터 변경이 없다. run4는 운영 상태를 바꿨다**(테스트 거래 1건 저장, KSM 약 3분 중단 — 아래 run4 절). 각 회차 파일은 서버에서 tar.gz로 묶어 base64로 받았고, archive SHA-256과 서버 `sha256sum` 결과가 수신본과 일치한다. 각 폴더의 `server-sha256sums.txt`는 서버가 만든 파일을 그대로 옮긴 것이다(원래 이름 `SHA256SUMS`).

| 회차 | 시각(UTC) | archive SHA-256 | 내용 |
|---|---|---|---|
| `run1-20260926T0419Z` | 04:19:37~04:20:01 | `901e28a5…c2c79f` | Service·Endpoints, Grafana provisioning 로그 요약, `prometheus-p0-test-alert` ConfigMap, Grafana port-forward 로그 |
| `run2-20260926T0425Z` | 04:25:09~04:25:28 | `3353bf4e…d4e06` | Ingress 0건, Grafana port-forward `/api/health` 200, 비인증 `/api/search` 401, Worker IP:3000 직접 접근 3/3 타임아웃, monitoring-api ConfigMap 목록 |
| `run3-mon17fast` | 04:43:18~04:43:24 | `2457e893…5494b4` | Grafana API(Dashboard 목록·Datasource·Datasource health), namespace PSA 라벨, node-exporter DaemonSet YAML·Pod imageID, Prometheus `up`·`node_scrape_collector_success` 조회 |

## run1의 빈 파일 5개 (재수집 사유)
run1의 `ingress-all.txt`, `grafana-health-via-pf.txt`, `grafana-search-noauth.txt`, `nodeip-3000-direct.txt`, `monitoring-api-cm.txt`는 **0바이트**다. 수집 직후 화면에는 내용이 출력됐으나, 04:21Z에 이 5개 파일만 비워졌다. 화면 출력(`==> 파일명 <==` 줄)을 터미널에 다시 붙여넣어 셸 리다이렉션으로 비워진 것으로 추정한다. 같은 명령을 run2로 다시 수집했으며 run2가 이 5개 항목의 원본이다. run1은 서버 해시 기록과 함께 그대로 보존한다. run1 `server-sha256sums.txt`에는 `SHA256SUMS` 자신의 줄도 있다. 2단계에서 `sha256sum * > SHA256SUMS`를 다시 실행할 때 1단계에서 만든 같은 이름의 파일이 이미 있었기 때문이며(셸이 파일을 먼저 비운 뒤 계산), 증적 판단에는 영향이 없다. run1의 `grafana-provisioning-log.txt`(696줄 원본)는 편입하지 않았다. 서버 해시(`ee751f7b…`)만 run1 `server-sha256sums.txt`에 있고, 요약본 `grafana-provisioning-summary.txt`를 편입했다.

## 확인된 사실 (판정 아님)
- **Grafana:** Dashboard 4개(Application & FDS, Kubernetes Workload, Node & Monitoring Health, FDS Overview 발표용). Datasource `Prometheus`(uid `prometheus`)는 `access: proxy`, url `http://prometheus:9090`, health `"status":"OK"`. AC 요구사항의 URL 표기(`http://prometheus.monitoring-api.svc:9090`)와는 문자열이 다르다(같은 namespace 짧은 이름).
- **Grafana 노출:** Ingress 0건, Service 4개 모두 ClusterIP, 승인 경로(control01 port-forward) 200, 비인증 API 401, Worker IP:3000 직접 접근 실패.
- **node-exporter:** `privileged: false`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `seccompProfile RuntimeDefault`, capabilities drop ALL, HostPath `/`→`/host` `readOnly: true`, `hostNetwork`·`hostPID: true`(통제 예외 대상). 3개 Pod imageID 모두 `10.1.93.54/fds/node-exporter@sha256:56566542…`. `last-applied-configuration`에는 `:latest`가 남아 있다.
- **PSA:** `monitoring-api` enforce/audit/warn=restricted. `monitoring-node` enforce=privileged, audit/warn=restricted.
- **Target:** `up` 20개 중 UP 6개(transaction-api 2, fds-engine 2, kube-state-metrics 1, node-exporter `.108` 1). node-exporter `.105`·`.107`과 kubelet·kubelet-cadvisor 12개는 DOWN(크로스노드 host GNP, #14). **`job="prometheus"`(self) target이 설정에 없다**(infra-monitoring#16).
- **Collector:** `.108` node-exporter collector 49개 중 성공 40개. 실패 9개(bcachefs, bonding, fibrechannel, ipvs, nfs, nfsd, pressure, tapestats, zfs)는 해당 기능·장치가 없는 collector다(원인 미확인).
- **p0 Test Alert:** ConfigMap `prometheus-p0-test-alert`(2026-09-22T05:45:35Z 생성)의 `FDSMonitoringPipelineTest`는 `expr: vector(1) == 0`(비활성 상태), `severity: info`.

## 콘솔 제출 자료 — node-exporter SA 권한 (`console-sa-rbac/`)
**콘솔 제출 자료**다. 사용자가 채팅에 붙여넣은 출력 원문이며, 서버 파일·서버 Hash는 없다. 명령은 `commands.txt`에 있다.
- `rolebinding,clusterrolebinding -A` 결과를 `node-exporter`로 거르면 헤더 2줄만 남는다. 바인딩 0건이다.
- `auth can-i --list`(SA `node-exporter-sa`)에는 모든 인증 주체 기본 권한(self*reviews create, discovery·health non-resource get)만 있다. 리소스 get/list/쓰기 권한은 없다.
- `automountServiceAccountToken`은 SA·Pod 모두 미설정(빈 줄 2개)이므로 기본값 true다.

## run4 — 거래 1건 후 Metric 조회 + Test Alert(TargetDown) 재시험 (`run4-e2e-s8-20260926T0502Z`)
2026-09-26 14:02:36~14:11:31 KST(05:02:36~05:11:31Z), k8s-control01. archive `b3155fc5…709846`(2,384 B)를 **05:1x UTC에 채팅으로 수신**해 대조했다(폴더명 `received-…T0445Z`는 run1~3 수신 기준이며, run4 수신은 그보다 늦다). **이 회차는 운영 상태를 바꿨다**(아래 2개). MON Lead가 실행을 결정했다.

**A. 거래 1건 → Metric 조회**(AC "거래 호출 후 API/FDS/DB 저장 Metric과 Kubernetes/Node Metric 조회")
- `transaction-api` port-forward로 `POST /api/v1/transactions` 1건을 보냈다(계좌 `MON-E2E-20260926`, deposit 10,000 KRW). 응답 `HTTP=201`, `fds_detected:false`, R01/R02/R04/R07 모두 미탐지, `fds_evaluation_skipped:false`(`txn-response.txt`). **fdsdb에 거래 1건이 저장됐다.**
- 거래 전→후(`metrics-before.txt`→`metrics-after.txt`, 40초 간격): `sum(transaction_save_success_total)` 0→1, `sum(transaction_save_failure_total)` 0→0, `sum(fds_evaluated_total)` 1→2, `fds_detected_total{rule_id="R02"}` 1→1. K8s `kube_deployment_status_replicas_available{namespace="fds-app"}` 2개 Deployment 각 2, Node `node_memory_MemAvailable_bytes` `.108` 조회 성공. `.105`·`.107`은 크로스노드 이슈로 series가 없다.
- 카운터는 Pod별 합계이며 Pod 재시작 시 초기화된다. 거래 전 값 0은 현재 Pod 수명 기준이다.

**B. TargetDown 재시험**(9/24 요청 1-1·1-2)
- 방법: `s8_target_down.sh`(infra-monitoring main `72e952c`, H03 수정본)와 같은 절차를 명령 줄로 실행했다. KSM `replicas=0` → 30초 간격 관측 6회 → `replicas=1` → 30초 간격 관측 10회. 중단 시 `replicas=1` 복구 trap을 걸었다. 명령 원문은 PR 코멘트에 있다.
- 타임라인(`s8-timeline.txt`): 14:03:24 up=1 → 14:03:55 up=0 → 14:04:56 **pending** → 14:05:56 **firing** → 14:06:58 복구 up=1, ALERTS 소멸 → 14:11:31까지 유지. 최종 KSM 1/1(`ksm-final.txt`).
- Alertmanager `/api/v2/alerts`: firing 중 `TargetDown` active, startsAt `05:05:43Z`, receiver `discord-notifications`(`am-during.json`). 복구 후 빈 목록(`am-after.json`).
- **KSM 중단 약 3분 동안 kube-state-metrics 지표 공백이 생겼다.**

## 콘솔 제출 자료 — Discord 수신 화면 (`console-discord/`)
`discord-targetdown-firing-resolved.png`는 사용자가 채팅에 첨부한 Discord 화면 캡처다(SHA-256 `a2a60316…46ffd3`, 수신 파일 그대로). `[FIRING:1] TargetDown critical`(메시지 묶음 시각 "오후 2:05")과 `[RESOLVED] TargetDown critical`이 보인다. 캡처에 날짜와 RESOLVED 개별 시각은 표시되지 않는다. 시각 근거는 run4 타임라인과 Alertmanager 기록이다.

## 이번에 확보하지 못한 것
- Prometheus 재시작 전후 같은 query 결과
- p0 Test Alert(`FDSMonitoringPipelineTest`) 전환 전후 ConfigMap: 이번 재시험은 TargetDown 방식으로 했다

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
