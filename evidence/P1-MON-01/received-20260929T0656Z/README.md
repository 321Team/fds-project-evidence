# P1-MON-01 — 핵심 요구사항 섹션 1~4 근거 대조 (2026-09-29 15:56~16:16 KST)

[#17](https://github.com/321Team/fds-project-baseline/issues/17) 본문 "핵심 요구사항" 섹션 1~4에서 체크되지 않은 **24줄**을 정본 [v3.1.20](https://github.com/321Team/fds-project-baseline/blob/main/baseline/FDS_Project_Implementation_Baseline_v3.1.20.md) 기준과 대조했다. 이미 병합된 증적으로 판정할 수 있는 줄은 그 경로를 연결했다. 원본이 없던 줄은 MON Lead(이재환)가 읽기 전용 조회로 보완했다. 조회 서버는 k8s-control01(`server02`), edge01(`server08`), ansible01(`server01_ansible`)이다.

**판정 규칙:** 한 줄을 체크하려면 두 조건을 모두 만족해야 한다.
- 요구사항 문구의 모든 조건을 관측했다.
- 합격 기준이 정본에 있다.

하나라도 빠지면 "관측된 것"만 기록하고 체크하지 않는다.

**운영 변경:** 없음.
- Grafana 로그인 시험(`collect.txt`)은 control01 `kubectl port-forward`로 거부(401)를 확인하는 요청이다.
- ansible01에서는 kubeconfig가 없어 port-forward를 실행하지 않았다.

## 수신·대조

| 폴더 | 서버 원본 (생성 시각 KST) | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-mon-req-20260929/collect.txt` (15:56:55) | `mon-req-control01.tar.xz` 1,776 B, SHA-256 `197f7bdc…39c1dccc` | 서버 `sha256sum`과 일치, 개별 파일은 archive 내부와 바이트 동일 |
| `control01/` | `~/p1-mon-req-20260929/recheck-nodes-proxy.txt` (16:00:00) | `mon-req-recheck.tar.xz` 792 B, SHA-256 `b88819f4…18bbce81` | 같음 |
| `control01/` | `~/p1-mon-req-20260929/supp.txt` (16:15:31) | `mon-req-supp.tar.xz` 2,328 B, SHA-256 `5a0a5e93…f1646b6c` | 같음 |
| `edge01/` | `~/p1-mon-edge-20260929/edge-metrics.txt` (15:57:45) | `mon-edge.tar.xz` 448 B, SHA-256 `73233f55…3bc19e12` | 같음 |
| `ansible01/` | `~/p1-mon-pf-20260929/pf.txt` (16:16:23) | `mon-pf.tar.xz` 284 B, SHA-256 `dcdec509…b344f2cc` | 같음 |
| `local/` | 없음 — 서버 원본이 아니다 | 없음 | `edge01-metrics-external-20260929.txt`(16:06:57). 담당자 PC(서비스망 `10.1.93.29`)에서 Claude Code가 `curl`로 **직접 실행한 기록**이다. Hash는 이 폴더 `SHA256SUMS`에만 있다 |

- archive는 base64로 채팅에 붙여 받아 디코드했다. 파일별 서버 Hash는 받지 않았고 archive 단위로 대조했다.
- 각 archive 옆 `.sha256` 파일은 서버가 출력한 archive Hash 한 줄이다.

## `nodes/proxy` 조회 정정

`collect.txt`의 `kube-state-metrics-sa get nodes/proxy: yes`는 **명령 형식 오류**다.
- `kubectl auth can-i get nodes/proxy`는 `TYPE/NAME` 형식이라 "이름이 `proxy`인 노드를 get할 수 있는가"를 묻는다.
- KSM에는 `nodes` get 권한이 있어서 yes가 나왔다.

하위 리소스는 `--subresource=proxy`로 다시 조회했다(`recheck-nodes-proxy.txt`). 네 SA 모두 **no**다. 원본 `collect.txt`는 수정하지 않았다.

## 체크 — 8줄

| 섹션 | 요구사항 | 정본 기준 | 근거 |
|---|---|---|---|
| 2 | node-exporter `privileged=false`·`allowPrivilegeEscalation=false`·`seccomp=RuntimeDefault`·`drop ALL` | 694행 | [`received-20260927T0745Z/control01-mon21-ne/ds-after.yaml`](../received-20260927T0745Z/control01-mon21-ne/ds-after.yaml) 58~66행. 9/27 liveness 반영 뒤 관측 |
| 2 | node-exporter HostPath 전부 read-only, Kubernetes API RBAC 없음 | 694행(HostPath read-only), 800행(`node-exporter-sa`, Kubernetes API 권한 없음) | 같은 파일: hostPath `/` 1개, mount `/host` `readOnly: true`(72·85행)<br>`received-20260926T0445Z/console-sa-rbac/`: node-exporter 바인딩 0건<br>`collect.txt`: 전체 RoleBinding·ClusterRoleBinding 중 node-exporter 관련 0건 |
| 2 | Prometheus·KSM RBAC는 승인 읽기 Verb만, Secret 읽기·쓰기 Verb 금지 | 693행(읽기 전용 RBAC), 704행(Prometheus는 `nodes/metrics get` 등만, Secret 읽기 금지) | `supp.txt` prometheus-sa `can-i --list`: 리소스 권한은 `nodes/metrics [get]` 하나 (주 1)<br>`recheck-nodes-proxy.txt` KSM `can-i --list`: get/list/watch만, secrets 없음<br>`collect.txt`: 네 SA `list secrets`·`create pods` 모두 no |
| 2 | Prometheus·KSM 별도 ServiceAccount/ClusterRole, `nodes/proxy` 금지 | 704행 | `collect.txt` 바인딩 2건: `kube-state-metrics-binding`(kube-state-metrics-role → kube-state-metrics-sa), `prometheus-sa-kubelet-metrics`(같은 이름 ClusterRole → prometheus-sa)<br>`recheck-nodes-proxy.txt`: 네 SA 모두 `--subresource=proxy` no |
| 2 | Grafana Anonymous·Sign-up·기본 관리자 암호 금지, 자격정보 Secret 관리 | 701행 | `supp.txt`(16:15): `GF_AUTH_ANONYMOUS_ENABLED=false`, `GF_USERS_ALLOW_SIGN_UP=false`. `GF_SECURITY_ADMIN_USER`·`GF_SECURITY_ADMIN_PASSWORD`는 Secret `grafana-admin-credentials`의 `admin-user`·`admin-password` 키 참조(값은 수집 안 함)<br>`collect.txt`(15:56): `admin:admin`으로 `/api/org` **401**, 비인증 401, `/api/health` 200 |
| 2 | edge01을 통한 외부 `/metrics` 차단 | 837행(edge01 경유 Client 접근은 403/404 차단·Negative Test), 850행 | `edge01/edge-metrics.txt`: nginx `location = /metrics { return 404; }`(190행), edge01 자신에서 요청해도 404<br>`local/…`: 외부 출발지 `10.1.93.29`에서 시험 (주 2) |
| 3 | Prometheus 목표 보존기간 15일, PVC 80% 상한 | 42행(15d·`retention.size≤16GB`), 804행(PVC 용량의 최대 80%) | `supp.txt`: 현재 Deployment args `--storage.tsdb.retention.time=15d`, `--storage.tsdb.retention.size=16GB`, PVC `prometheus-data` Bound 20Gi. Prometheus 크기 단위는 2진이라 16GB = 16GiB = 20GiB의 80% |
| 3 | 외부 Plugin 미설치 | 요구사항 문구 | `collect.txt`: `/var/lib/grafana/plugins` 비어 있음(`total 0`)<br>`supp.txt`: `GF_PLUGINS_PREINSTALL_DISABLED=true` |

**주 1:** 목록의 나머지는 이 SA 전용 권한이 아니다. 모든 인증 주체가 받는 기본 권한이다(self-review `create`, discovery·health 같은 non-resource URL `get`).

**주 2:** `local/` 외부 출발지 시험 결과는 다음과 같다.
- `/metrics`, `//metrics`, `/./metrics`, `/%6detrics`: 모두 nginx가 직접 404(`text/html`)를 반환했다.
- `/METRICS`: 앱까지 전달됐고 앱이 404(JSON)를 반환했다.
- `/metrics/`, `/metrics%2f`: 307로 `/metrics`로 넘어간 뒤 404가 났다.
- 응답에 `# HELP` 줄은 0개다.
- 대조군 `/readyz`는 200이다. 같은 경로로 앱까지 도달한다는 뜻이다.

## 체크하지 않음 — 16줄

| 섹션 | 요구사항 | 관측된 것 | 체크하지 않은 이유·후속 |
|---|---|---|---|
| 1 | Grafana 관리 접근은 승인 관리 단말의 `kubectl port-forward`만 | 9/26 `run2`: Ingress 0, ClusterIP, control01 port-forward `/api/health` 200·비인증 401, Worker IP:3000 직접 3/3 실패 | 정본 700행은 승인 단말을 `ansible01(.10)` 또는 `cicd-runner01(.20)`로 정한다. 두 단말 모두 API LB `.109:6443`을 경유해야 한다.<br>`ansible01/pf.txt`: kubectl과 kubeconfig가 없다(`server=없음`). 승인 단말 경로는 시험할 수 없었고 control01 경로만 확인됐다.<br>이미 체크된 AC "승인 관리 단말의 Port-forward는 성공…"도 같은 control01 근거다. 처리는 MON Lead 결정 대기 |
| 1 | 모든 Image Harbor 승인 Digest 고정·Trivy 연결 | Prometheus·Alertmanager·Grafana Deployment는 `:latest` 태그(9/26~27 관측) | Digest 고정·Trivy 연결 전 |
| 2 | `monitoring-api` PSA Restricted, `monitoring-node` 통제 예외 | `run3-mon17fast/ns-psa-labels.txt`: api `enforce/audit/warn=restricted`, node `enforce=privileged`·`audit/warn=restricted` → 정본 679~681행과 일치 | 통제 예외 조건 중 셋이 확인되지 않았다.<br>① 정본 694행 "불필요 Collector 비활성": 현재 args는 `--path.rootfs=/host` 하나뿐이다.<br>② "승인 Digest": HBR 승인은 확인하지 않았다.<br>③ 681행 "임의 Workload 생성 RBAC 금지": `monitoring-node` 바인딩을 전수 조회하지 않았다 |
| 2 | Default Deny 이후 필요한 Scrape·Datasource·Alert·Remote Write 경로만 허용 | `supp.txt`: 두 Namespace에 `default-deny-all`이 있다. 필요한 경로(Scrape·Datasource·Alert·Remote Write·DNS)는 모두 허용돼 있다. Alertmanager → `10.1.93.56:3128`은 정본 1053행 승인 경로다 | "필요한 경로만"을 판정할 수 없다. 현장 규칙이 두 소스의 합집합이다.<br>① infra-monitoring과 infra-kubernetes `manifests/03-networkpolicy.yaml`에 같은 경로가 중복 정의돼 있다.<br>② `allow-prometheus-egress-scrape`가 옛 `fds` Namespace를 대상으로 남아 있다. 소스 main은 `fds-app`으로 바뀌었지만 현장에 반영되지 않았다.<br>③ kube-system 전체 Pod에 53을 허용하는 규칙이 있다.<br>소스 단일화·현장 정리 후 다시 판정 |
| 2 | TCP 9100/10250 HostEndpoint/GNP와 실제 Source 관측 | 9100 양성·음성은 9/27에 완료했다(AC 체크됨) | 10250 실제 출발지 관측 원본 없음 |
| 3 | Prometheus·Grafana·Alertmanager PVC와 Request/Limit 정의 | `supp.txt`: 네 Pod 모두 requests/limits가 있다. Grafana는 manifest에 명시돼 있다(200m/256Mi·1/1Gi) | Prometheus·Alertmanager는 manifest에 값이 없다. LimitRange `monitoring-api-default-limits` 기본값(200m/256Mi·500m/512Mi)이 주입된 것이라 Component별 정의로 보지 않는다. 소스 명시 필요 |
| 3 | P1-K8S가 제공한 static local StorageClass/PV가 `Bound`, `WaitForFirstConsumer`·`Retain`·nodeAffinity 승인값 일치 | `collect.txt`: PV 3개 Bound·`Retain`·nodeAffinity `k8s-worker03`·20/5/2Gi·`/home/fds-local-pv/*`, SC `fds-local-storage` WFFC·`no-provisioner` → 정본 41·42·791·802행 값과 일치 | 정본 802행은 "StorageClass/PV와 Host Directory는 P1-K8S-01 소유"라고 정한다. 그런데 현장 객체는 MON 소스(infra-monitoring `pv-monitoring-storage.yaml`)로 만들어졌다.<br>P1-K8S 소스 infra-kubernetes `manifests/04-storage.yaml`(`fds-local-retain`, SC `reclaimPolicy: Retain`)은 적용되지 않았다(infra-kubernetes `docs/evidence/P1-SEC-01/GATE2_RUNTIME_EXECUTION_20260922.md`).<br>현장 SC의 `reclaimPolicy`는 `Delete`다. 정적 PV에는 PV의 `Retain`이 적용된다.<br>"P1-K8S가 제공한" 조건은 K8S Lead 확인이 필요하다 |
| 3 | Datasource `http://prometheus.monitoring-api.svc:9090` Server-side Access | 현장 `grafana-datasources` ConfigMap: `http://prometheus:9090`(`collect.txt`) | 소스 main은 FQDN이다. 현장 반영 필요 |
| 3 | P0 기본 Dashboard 3종·기본 Alert Rule Source 관리 | 현장 Dashboard 4개(`fds-overview` 추가, `run3-mon17fast/grafana-api.txt`) | 추가 Dashboard 처리 결정과 현장↔소스 대조 전 |
| 4 | 외부 Watchdog 7줄 | — | monitor01 receiver·TLS·heartbeat 5분 단절 시험(G8)과 LB Probe 재시험 전 |

## 한계

- node-exporter 두 줄은 9/27 관측이다. 오늘 DaemonSet은 다시 조회하지 않았다.
- NetworkPolicy 양성·음성 시험은 이번에 다시 하지 않았다. 규칙 목록만 대조했다.
- `local/` 기록은 담당자 PC에서 직접 실행한 결과다. 서버 원본·서버 Hash가 없다.
- `collect.txt`에서는 화면 표시용 필터 때문에 조회 당시 화면에 바인딩 줄이 보이지 않았다. 하지만 파일에는 기록돼 있다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·정본 대조·문서화. 서버 명령 실행은 담당자 본인, `local/` 외부 시험은 Claude Code가 담당자 PC에서 직접 실행)
