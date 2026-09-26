# P1-MON-01 — AC 근거 보완 조회 3회차 (2026-09-26, k8s-control01)

[증적 보완 요청 대응표](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5843098390)의 "읽기 전용 조회로 보완 가능한 것"을 MON Lead(이재환)가 k8s-control01(`server02`)에서 수집했다. 모든 명령은 조회(GET)만 했고 클러스터 변경은 없다. 각 회차 파일은 서버에서 tar.gz로 묶어 base64로 받았고, archive SHA-256과 서버 `sha256sum` 결과가 수신본과 일치한다. 각 폴더의 `server-sha256sums.txt`는 서버가 만든 파일을 그대로 옮긴 것이다(원래 이름 `SHA256SUMS`).

| 회차 | 시각(UTC) | archive SHA-256 | 내용 |
|---|---|---|---|
| `run1-20260926T0419Z` | 04:19:37~04:20:01 | `901e28a5…c2c79f` | Service·Endpoints, Grafana provisioning 로그 요약, `prometheus-p0-test-alert` ConfigMap, Grafana port-forward 로그 |
| `run2-20260926T0425Z` | 04:25:09~04:25:28 | `3353bf4e…d4e06` | Ingress 0건, Grafana port-forward `/api/health` 200, 비인증 `/api/search` 401, Worker IP:3000 직접 접근 3/3 타임아웃, monitoring-api ConfigMap 목록 |
| `run3-mon17fast` | 04:43:18~04:43:24 | `2457e893…5494b4` | Grafana API(Dashboard 목록·Datasource·Datasource health), namespace PSA 라벨, node-exporter DaemonSet YAML·Pod imageID, Prometheus `up`·`node_scrape_collector_success` 조회 |

## run1의 빈 파일 5개 (재수집 사유)
run1의 `ingress-all.txt`, `grafana-health-via-pf.txt`, `grafana-search-noauth.txt`, `nodeip-3000-direct.txt`, `monitoring-api-cm.txt`는 **0바이트**다. 수집 직후 화면에는 내용이 출력됐으나, 04:21Z에 이 5개 파일만 비워졌다. 화면 출력(`==> 파일명 <==` 줄)을 터미널에 다시 붙여넣어 셸 리다이렉션으로 비워진 것으로 추정한다. 같은 명령을 run2로 다시 수집했으며 run2가 이 5개 항목의 원본이다. run1은 서버 해시 기록과 함께 그대로 보존한다. run1의 `grafana-provisioning-log.txt`(696줄 원본)는 편입하지 않았다. 서버 해시(`ee751f7b…`)만 run1 `server-sha256sums.txt`에 있고, 요약본 `grafana-provisioning-summary.txt`를 편입했다.

## 확인된 사실 (판정 아님)
- **Grafana:** Dashboard 4개(Application & FDS, Kubernetes Workload, Node & Monitoring Health, FDS Overview 발표용). Datasource `Prometheus`(uid `prometheus`)는 `access: proxy`, url `http://prometheus:9090`, health `"status":"OK"`. AC 요구사항의 URL 표기(`http://prometheus.monitoring-api.svc:9090`)와는 문자열이 다르다(같은 namespace 짧은 이름).
- **Grafana 노출:** Ingress 0건, Service 4개 모두 ClusterIP, 승인 경로(control01 port-forward) 200, 비인증 API 401, Worker IP:3000 직접 접근 실패.
- **node-exporter:** `privileged: false`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `seccompProfile RuntimeDefault`, capabilities drop ALL, HostPath `/`→`/host` `readOnly: true`, `hostNetwork`·`hostPID: true`(통제 예외 대상). 3개 Pod imageID 모두 `10.1.93.54/fds/node-exporter@sha256:56566542…`. `last-applied-configuration`에는 `:latest`가 남아 있다.
- **PSA:** `monitoring-api` enforce/audit/warn=restricted. `monitoring-node` enforce=privileged, audit/warn=restricted.
- **Target:** `up` 20개 중 UP 6개(transaction-api 2, fds-engine 2, kube-state-metrics 1, node-exporter `.108` 1). node-exporter `.105`·`.107`과 kubelet·kubelet-cadvisor 12개는 DOWN(크로스노드 host GNP, #14). **`job="prometheus"`(self) target이 설정에 없다**(infra-monitoring#16).
- **Collector:** `.108` node-exporter collector 49개 중 성공 40개. 실패 9개(bcachefs, bonding, fibrechannel, ipvs, nfs, nfsd, pressure, tapestats, zfs)는 해당 기능·장치가 없는 collector다(원인 미확인).
- **p0 Test Alert:** ConfigMap `prometheus-p0-test-alert`(2026-09-22T05:45:35Z 생성)의 `FDSMonitoringPipelineTest`는 `expr: vector(1) == 0`(비활성 상태), `severity: info`.

## 이번에 확보하지 못한 것
- node-exporter ServiceAccount `node-exporter-sa`의 RoleBinding/ClusterRoleBinding 부재 확인
- Prometheus 재시작 전후 같은 query 결과, Test Alert 전이, 거래 후 Metric 조회

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
