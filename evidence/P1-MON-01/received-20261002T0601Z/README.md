# P1-MON-01 — monitoring PSA·monitoring-node 생성 권한·Alertmanager 현장 설정·NetworkPolicy 읽기 전용 조회 (2026-10-02 15:01 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 읽기 전용으로 조회했다. 운영 변경은 없다. 사용한 명령은 `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get … -o json|yaml|wide`와 `-o jsonpath`뿐이고, 객체 생성·변경·삭제, 재시작, `exec`, 서버 dry-run은 하지 않았다. 분석은 저장한 JSON을 `an.py`(같은 폴더, Python 3 표준 라이브러리)로 읽어 출력했다.

대상 AC(#17 본문, 판단은 이 증적의 독립 리뷰·병합 뒤 MON Lead가 한다):
- 2절 "`monitoring-api` PSA Restricted와 `monitoring-node` 통제 예외를 적용한다." — 2026-09-30 보류 사유 중 "임의 Workload 생성 RBAC 금지"를 보완하는 조회([#17 5910525074](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5910525074), [5926312855](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5926312855))
- 4절 "IF-24 Alertmanager Webhook은 구성하지 않으며 Alertmanager는 외부 monitor01로 직접 송신하지 않는다." — 현장 Alertmanager 설정 확인

**AC 체크는 이 기록만으로 바꾸지 않는다.**

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-mon-psa-rbac-20261002T150142/`(서버 파일 12개 중 9개 편입) | `control01-psa-rbac-20261002.tgz` 5,936 B(서버 이름 `p1-mon-psa-rbac-small.tgz`), SHA-256 `3e2d20b0…a61b38` | 15:04 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일은 archive를 그대로 푼 것이다 |

- archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다.
- **서버에만 있는 원본(이 PR에 없음):** `rbac.json`(341,915 B, SHA-256 `dbd26d53…ee06`), `np-api.json`(40,796 B, `1deb17fe…59dc`), `pods-api.json`(60,301 B, `af14139b…087c`). 붙여넣기 전달 한도 때문에 편입하지 않았고 SHA-256만 archive 안 `SHA256SUMS`에 있다. 따라서 아래 2절 RBAC 표는 `summary.txt`(스크립트 출력)에 의존하며, `rbac.json`을 받아 `an.py`로 재현하는 것은 **독립 리뷰 요청 시 제공할 수 있다(현재 NOT VERIFIED)**.
- 비밀 정보 검색 0건이다. Alertmanager 설정은 `webhook_url` 값을 마스킹했고(실제 설정은 `webhook_url_file` 경로만 사용), Prometheus 설정에는 `password_file` 경로만 있다. `node-ds.yaml`의 `harbor-pull-secret`은 Secret 이름일 뿐 내용이 아니다.

## 1. namespace PSA 라벨·Pod (`ns.json`, `summary.txt`)

| namespace | enforce | audit | warn |
|---|---|---|---|
| `monitoring-api` | restricted | restricted | restricted |
| `monitoring-node` | **privileged** | restricted | restricted |

- `monitoring-api` Pod 4개는 모두 오늘(10/2 00:50~03:57Z) 만들어져 enforce=restricted 아래에서 admit됐다: prometheus `00:50:04Z`, alertmanager·grafana `02:53:37Z`, kube-state-metrics `03:57:01Z`.
- `monitoring-node` 객체(`node-objects.txt`): Pod `node-exporter` 3개(Worker 3대, Running), Service `node-exporter`(ClusterIP 9100), DaemonSet `node-exporter` 1개, ServiceAccount `default`·`node-exporter-sa`, NetworkPolicy `default-deny-all`·`node-exporter-allow`, LimitRange `monitoring-node-default-limits`. 다른 Workload·Role·RoleBinding은 없다.
- DaemonSet `node-exporter`(`node-ds.yaml`): 이미지 `10.1.93.54/fds/node-exporter@sha256:4d5c92fc…`, `privileged: false`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`, `hostNetwork`·`hostPID: true`, HostPath `/`는 `readOnly: true` 마운트, collector는 `--collector.disable-defaults` 뒤 8개(cpu·loadavg·meminfo·diskstats·filesystem·netdev·time·timex).

## 2. monitoring-node에서 Workload를 만들거나 수정할 수 있는 주체 (`summary.txt`, `an.py`)

- 대상 자원: pods, replicationcontrollers, deployments, daemonsets, statefulsets, replicasets, jobs, cronjobs. 대상 verb: create·update·patch(`*` 포함). 대상 범위: 모든 ClusterRoleBinding(클러스터 전체에 적용)과 `monitoring-node`의 RoleBinding.
- **`monitoring-node`의 RoleBinding은 0개다.** ClusterRoleBinding으로 위 권한이 닿는 주체는 아래뿐이다.

| 주체 | 성격 |
|---|---|
| `Group/system:masters`, `Group/kubeadm:cluster-admins` | 클러스터 관리자 그룹 |
| `ServiceAccount/kube-system/` `cronjob-controller`·`daemon-set-controller`·`deployment-controller`·`generic-garbage-collector`·`job-controller`·`persistent-volume-binder`·`replicaset-controller`·`replication-controller`·`statefulset-controller` | Kubernetes 내장 컨트롤러(각 `system:controller:*` ClusterRoleBinding) |

- `monitoring-node`의 ServiceAccount `node-exporter-sa`·`default`와 monitoring 관련 사용자·ServiceAccount는 이 표에 없다.
- `an.py`의 "기본 주체" 분류는 이름이 `system:`·`kubeadm:`으로 시작하는 주체만 거른다. 컨트롤러 ServiceAccount 이름(`cronjob-controller` 등)은 이 접두사가 없어 "기본 외 주체"로 출력됐다. 위 표에서 성격을 구분했다.
- **한계:** `pods/exec`, `pods/ephemeralcontainers`, `escalate`·`bind`·`impersonate`, ServiceAccount 토큰 발급 등 다른 경로의 권한은 조사하지 않았다. PSA 예외 목록(AdmissionConfiguration)과 admission webhook도 보지 않았다.

## 3. Alertmanager 현장 설정 (`alertmanager-config.masked.yml`)

`ConfigMap monitoring-api/alertmanager-config`의 `alertmanager.yml` 요약(webhook URL 마스킹 처리 후 저장):

- receiver는 2개다: `screen-only`(integration 없음)와 `discord-notifications`.
- `discord-notifications`는 `discord_configs`(`webhook_url_file: /etc/alertmanager/secrets/discord/webhook_url`, `http_config.proxy_url: http://10.1.93.56:3128`) 하나뿐이다.
- `webhook_configs`·monitor01(`10.250.10.30`) 대상은 없다.
- 이 설정은 CR-P1-MON-01-02([#75](https://github.com/321Team/fds-project-baseline/issues/75)) 승인 예외(Discord 1개 목적지, 정본 D-ID 등록은 [Decision 요청 5842467994](https://github.com/321Team/fds-project-baseline/issues/75#issuecomment-5842467994) 별도)에 해당한다. IF-24(Alertmanager→monitor01 Webhook)와는 별개다.

## 4. monitoring-api NetworkPolicy (`summary.txt`; 원본 `np-api.json`은 서버에만)

NetworkPolicy 16개. egress가 있는 규칙만 요약한다.

| 규칙 | 대상 → 목적지:포트 |
|---|---|
| `allow-prometheus-egress-alertmanager` | prometheus → alertmanager:9093 |
| `allow-prometheus-egress-kube-state-metrics` | prometheus → kube-state-metrics:8080 |
| `allow-prometheus-egress-kubelet` | prometheus → 6노드 `10.1.93.102/103/104/105/107/108`:10250 |
| `allow-prometheus-egress-node-exporter` | prometheus → Worker 3대:9100 |
| `allow-prometheus-egress-scrape` | prometheus → transaction-api:9091, fds-engine:9090 |
| `prometheus-allow`(infra-kubernetes 03 중복 정의) | prometheus → alertmanager:9093, transaction-api:9091, fds-engine:9090, Worker 3대:9100·10250, kube-state-metrics:8080 |
| **`prometheus-remote-write-allow`** | **prometheus → `10.250.10.30/32`:443** |
| `allow-grafana-to-prometheus`, `grafana-allow` | grafana → prometheus:9090 |
| `alertmanager-egress` | alertmanager → `10.1.93.56/32`:3128 |
| `kube-state-metrics-allow` | kube-state-metrics → CP 3대:6443 |
| `monitoring-api-dns-allow` | 전체 Pod → kube-system kube-dns:53 |
| `default-deny-all`, `alertmanager-allow`, `allow-grafana-ingress-from-prometheus-ns`, `allow-prometheus-ingress-to-alertmanager` | egress 규칙 없음(Default Deny 또는 ingress만) |

- 개수 16은 2026-09-30 적용 후 값([evidence#79](https://github.com/321Team/fds-project-evidence/pull/79) `post/summary.txt`)과 같다.
- Prometheus Remote Write 규칙은 `10.250.10.30/32` TCP 443 한 줄이다. Alertmanager egress에 monitor01 경로는 없다.

## 5. Prometheus 송신 설정 (`prom-remote-write.txt`)

`ConfigMap monitoring-api/prometheus-config`의 `remote_write` 블록: `url: https://10.250.10.30/api/v1/write`, `ca_file`(승인 Root), `insecure_skip_verify: false`, `min_version: TLS12`, `basic_auth`(사용자 `fds-heartbeat`, `password_file`), `write_relabel_configs`: `__name__`이 `fds_monitoring_heartbeat`인 것만 `keep`, `labelkeep __name__`. 저장소 소스(infra-monitoring main `kubernetes/monitoring/prometheus.yaml`)와 같은 내용이다.

## 판정 범위

- 이 기록이 보여 주는 것: 조회 시점(15:01 KST)의 PSA 라벨, `monitoring-node` 객체 구성과 DaemonSet 보안 설정, Workload 생성·수정 권한 주체 목록(위 자원·verb 범위), Alertmanager 현장 receiver, monitoring-api NetworkPolicy와 Prometheus 송신 설정.
- **NOT VERIFIED:** 서버에만 있는 `rbac.json`·`np-api.json`·`pods-api.json` 원본 재현(요청 시 제공), 2절 한계에 적은 다른 권한 경로, 이미지 Trivy 결과(별도 기록 #13 5925883099, evidence#88·#89).
- **NOT RUN:** `.108` 출발지 시험(잘못된 인증 401·8443 직접 차단·tcpdump) — [QA 5946270938](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5946270938) 범위, 별도 수집회차.
- 운영 변경이 없어 되돌릴 대상은 없다. 서버 원본 폴더는 보존한다.

AI 사용: CLAUDE_ASSISTED (조회 스크립트 준비, 수신 대조·판정·문서화, 실행은 담당자 본인)
