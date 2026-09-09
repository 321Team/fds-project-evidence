# DEC-P1-MON-01 — Kubernetes-Integrated Hybrid Monitoring Architecture

> Document Revision: `v1.1`  
> Canonical Baseline: `FDS_Project_Implementation_Baseline_v3.1.13`  
> Notion 적용 방식: `Record ID=DEC-P1-MON-01` Upsert

## Notion 데이터 속성

| Property | 입력값 |
|---|---|
| Record ID | DEC-P1-MON-01 |
| Phase | Phase 1 |
| Category | Monitoring / Architecture / Security |
| Type | Decision |
| Status | Done |
| Priority | P0 |
| Start | 2026-08-31 |
| End | 2026-08-31 |
| Calendar Days | 1 |
| Working Days | 1 |
| Lead | 이권욱 |
| Support | 이하영, 이재환 |
| Exit Criteria | Grafana 포함 Kubernetes 내부 관측 Stack, node-exporter 통제 예외, monitor01 외부 Watchdog, IF-05/IF-06 계열, 보안·Rollback·후속 구현 책임을 D33으로 승인하고 Baseline·Architecture·Addendum·Release Notes를 발행 |
| Related Decision IDs | D05; D14; D17; D19; D33 |
| Related Risk IDs | RISK-04; RISK-07 |
| Source | FDS_Project_Implementation_Baseline_v3.1.13; FDS_Network_Baseline_v2.3; FDS_Phase1_Logical_Architecture_v3.1.3; FDS_Phase1_Physical_Architecture_v3.1.3; FDS_D-SEC-01_Monitoring_System_Exception_Addendum_v1.0; FDS_Project_Implementation_Baseline_Release_Notes_v3.1.13 |
| Schedule Note | 2026-08-31 사용자 승인으로 D33 Fixed/Done. 설계 종결만 의미하며 Runtime 14개 Acceptance는 P1-MON-01에 귀속한다. WBS v3.1.12에는 미등록이므로 차기 Roll-up에서 Closed Register와 Decision Register에 동기화한다. |

---

# 🎯 Decision Story

인프라·모니터링 의사결정 담당자로서 금융권 운영 원칙을 반영한 교육·PoC 환경의 관측 구조를 확정한다. 이를 통해 Application·Kubernetes·Node 상태는 Kubernetes 내부에서 수집하고, Kubernetes 장애와 독립된 `monitor01(.30)`이 외부 관점의 서비스 가용성과 Monitoring heartbeat 단절을 감지하도록 한다.

---

# 📌 Scope

## In Scope

- `monitoring-api`: Prometheus, Alertmanager, Grafana, kube-state-metrics
- `monitoring-node`: node-exporter DaemonSet 전용 통제 예외
- `monitor01(.30)`: External Prometheus, Blackbox Exporter, TLS Reverse Proxy, 제한 Remote Write Receiver
- Grafana P0 포함 및 `ClusterIP + 승인 관리 단말 Port-forward` 접근
- Prometheus·Grafana·Alertmanager PVC와 P0 Retention 원칙
- IF-05, IF-05A, IF-05B, IF-06, IF-06A, IF-06B Interface 동결
- D-SEC-01 Monitoring System Exception Addendum 연계
- P0 단일 Replica Known Limitation과 P1-MON-02 확장 경계
- 문서 Rollback 및 Runtime Rollback 승인 원칙

## Out of Scope

- Kubernetes Manifest 적용 및 실제 Target `UP` 판정
- Grafana Dashboard·Datasource Runtime 검증
- Alert Firing/Resolved 및 PVC 재시작 시험
- NetworkPolicy·Host Firewall·RBAC Positive/Negative Test
- Production 금융 규제 준수 또는 Production HA 적합성 주장
- Loki, SIEM, 장기 로그 보존
- Prometheus 2 Replica, Alertmanager 3 Replica, PDB, TopologySpread, 장기 Remote Storage

위 Runtime 항목은 `P1-MON-01`, HA·장기보존 고도화는 `P1-MON-02`에서 판정한다.

---

# 📋 핵심 요구사항

- [x] Primary Metrics Collector를 Kubernetes 내부 Prometheus로 확정한다.
- [x] Kubernetes 장애와 동일 장애영역에 포함되지 않는 외부 Watchdog을 유지한다.
- [x] node-exporter를 업무 Workload와 분리하고 Host 접근 예외를 최소화한다.
- [x] Grafana를 P0 Review 범위에 포함하되 외부 Service Entry를 금지한다.
- [x] Monitoring Image, RBAC, Secret, Network, Storage의 Mandatory Control을 정의한다.
- [x] P0와 P1-MON-02의 HA·장기보존 범위를 중복 없이 분리한다.
- [x] Interface, Evidence, Rollback 책임을 구현 티켓에 연결한다.

---

# 🔀 대안 검토

| 대안 | 구성 | 장점 | 제약 / 기각 사유 |
|---|---|---|---|
| A. External-only | monitor01 Prometheus가 App·Node·Kubelet을 직접 수집 | 구현 단순, Cluster 장애와 독립 | Kubernetes Service Discovery·Namespace·RBAC 운영과 괴리되고 Grafana P0 Review 범위가 부족 |
| B. In-cluster-only | 모든 Monitoring Component를 Kubernetes 내부 배치 | Kubernetes-native 운영과 구성 일관성 | API·CNI·Worker 장애 시 수집·Dashboard·Alert가 함께 중단되는 동일 장애영역 |
| C. Hybrid — 채택 | In-cluster Stack + monitor01 External Watchdog | Kubernetes-native 관측과 외부 장애감지를 동시에 확보 | TLS, Remote Write Allowlist, 이중 운영 경계를 추가 관리해야 함 |

**선정 결과:** 대안 C를 채택한다. P0 범위에서 운영 복잡성을 제한하기 위해 monitor01에는 heartbeat와 승인 self/target-health Metric만 전송하고 전체 Application Metric 복제는 금지한다.

---

# ✅ Decision

1. Prometheus, Alertmanager, Grafana, kube-state-metrics는 `monitoring-api`에 배치한다.
2. `monitoring-api`는 PSA `enforce/audit/warn=restricted`를 적용한다.
3. node-exporter만 `monitoring-node`에 DaemonSet으로 배치한다.
4. `monitoring-node`는 PSA `enforce=privileged`, `audit/warn=restricted`를 사용하되 Container `privileged=true`는 금지한다.
5. Prometheus, Grafana, Alertmanager는 `ClusterIP`만 사용하고 외부 Ingress·NodePort·LoadBalancer를 생성하지 않는다.
6. Grafana 관리 접근은 승인 관리 단말의 `kubectl port-forward`만 허용한다.
7. `monitor01(.30)`은 External Prometheus + Blackbox Exporter 기반 Watchdog으로 유지한다.
8. In-cluster Prometheus는 `fds_monitoring_heartbeat=1`과 승인된 self/target-health Metric만 monitor01 `.30:443`으로 HTTPS Remote Write한다.
9. monitor01은 프로젝트 Private CA가 서명한 전용 Leaf와 TLS Reverse Proxy로 Remote Write Path만 localhost Receiver에 전달한다.
10. P0 단일 Replica는 교육·PoC Known Limitation이며 Production 금융 HA 수준으로 표현하지 않는다.
11. Prometheus 2 Replica, Alertmanager 3 Replica, PDB, TopologySpread 및 장기 보존은 `P1-MON-02`에서 수행한다.

---

# 🔐 Mandatory Controls

- Monitoring Image는 Harbor 승인 Repository의 Digest로 고정한다.
- Prometheus와 kube-state-metrics RBAC는 필요한 `get/list/watch` 및 승인된 non-resource URL `get`만 허용한다.
- Secret 읽기와 `create/update/patch/delete` 권한은 금지한다.
- Grafana Anonymous Access, Sign-up, 기본 관리자 암호를 금지한다.
- Grafana 관리자·Remote Write 인증정보는 Kubernetes Secret으로 관리한다.
- node-exporter HostPath는 read-only이며 Host 쓰기와 Privilege Escalation을 금지한다.
- node-exporter Container는 `privileged=false`, `allowPrivilegeEscalation=false`, `seccomp=RuntimeDefault`, `capabilities.drop=ALL`을 기본으로 한다.
- `hostNetwork` Policy 동작은 Calico 시험과 Node Host Firewall의 TCP 9100 Allowlist를 함께 검증한다.
- App `/metrics`는 Cluster 내부 수집만 허용하고 edge01 외부 경로에서는 차단한다.
- Remote Write에는 업무 Payload, 개인정보 Label 및 전체 Application Metric을 포함하지 않는다.

---

# ✅ Acceptance Criteria

- [x] Hybrid Monitoring 배치와 장애영역이 Logical/Physical Architecture v3.1.3에 반영됐다.
- [x] Kubernetes 내부 Stack, node-exporter 예외 및 monitor01 외부 Watchdog 역할이 확정됐다.
- [x] IF-05/IF-06 계열의 Source, Destination, Protocol, Port, Owner, Acceptance가 동결됐다.
- [x] D-SEC-01 Monitoring System Exception Addendum v1.0이 발행됐다.
- [x] Grafana P0 범위와 P1-MON-02 HA·장기보존 경계가 분리됐다.
- [x] P1-MON-01의 14개 Runtime Acceptance와 Evidence 책임이 정의됐다.
- [x] 문서 Rollback과 Runtime Rollback 승인 원칙이 정의됐다.
- [x] Baseline v3.1.13 및 Release Notes에 D33 변경이 반영됐다.

---

# 🧪 검증 및 증적

- `FDS_Project_Implementation_Baseline_v3.1.13.md`
- `FDS_Project_Implementation_Baseline_Release_Notes_v3.1.13.md`
- `FDS_Phase1_Logical_Architecture_v3.1.3.mmd`
- `FDS_Phase1_Physical_Architecture_v3.1.3.mmd`
- `FDS_D-SEC-01_Monitoring_System_Exception_Addendum_v1.0.md`
- `P1-MON-01_Notion_Description_UserStory_v1.0.md` Revision v1.1
- `FDS_Document_Distribution_Manifest_v3.1.13.md`
- 사용자 승인 기록 — 2026-08-31

---

# 🔗 Dependency

- **Blocked By:** D-ARC-01 Architecture Freeze, D-SEC-01/D17 Security Baseline Review, DEC-P1-TLS-01/D19 TLS Trust 원칙
- **Blocks / Next:** P1-MON-01 Runtime 구축·검증, P1-MON-02 HA·장기보존 고도화
- **Related Ticket:** D-SEC-01, P1-SEC-01, P1-K8S-01, P1-APP-01, P1-HBR-01, P1-DOC-01
- **Milestone Contribution:** G0 Design Freeze의 Monitoring 변경 통제, G2 Security / Feature Ready의 선행 설계

D-SEC-01 본체가 `In Review`인 상태는 유지한다. 본 Decision과 Addendum 발행은 D17 전체 검토를 종결하거나 P1-SEC-01 Runtime 검증을 대체하지 않는다.

---

# ⚖️ Decision / Risk Control

- **Decision Register:** D33 — Kubernetes-Integrated Hybrid Monitoring 승인
- **Related Decision IDs:** D05, D14, D17, D19, D33
- **Related Risk IDs:** RISK-04, RISK-07
- **Risk Control:** 외부 Watchdog 경로는 승인 TCP·Route·Source Evidence로 판정하고, Default Deny 및 node-exporter 예외는 D-SEC-01/P1-SEC-01 통제로 검증한다. D33과 P1-MON-02를 차기 WBS Roll-up에 연결해 변경 추적성을 보존한다.
- **Change Control:** Component Placement, Namespace, Exposure, Port, Remote Write Payload, PSA 예외 또는 P0/P1 경계 변경은 새 Decision과 Interface 영향도 검토 없이 적용하지 않는다.

---

# 🔍 Review / Handoff

- **이권욱:** Decision Owner·Approver, Baseline/Architecture/Interface/배포 정합성 관리
- **이하영:** D-SEC-01 및 P1-SEC-01 관점의 PSA·RBAC·NetworkPolicy·Host Firewall·System Exception 검토
- **이재환:** P1-MON-01 구현 Lead로 Manifest, Dashboard, Alert, Storage, Watchdog 연계, Runtime Evidence와 Runbook 수행
- **Handoff Gate:** P1-MON-01은 본 Decision을 변경하지 않고 Runtime Acceptance 14개를 수행한다. 변경 필요 시 구현 우회가 아니라 Change Request를 발행한다.

---

# ↩️ Rollback

- Runtime 적용 전 문서 오류가 확인되면 v3.1.12를 직전 정본으로 재지정하고 v3.1.13은 `Superseded / Rollback` 이력으로 보존한다.
- Runtime 적용 후에는 Monitoring Component를 임의 삭제하거나 monitor01의 과거 광범위 Scrape를 승인 없이 복원하지 않는다.
- IF-05/IF-06, RBAC, Host Firewall, Remote Write 및 Evidence 보존 영향도를 검토한 별도 Rollback Decision과 Runbook에 따라 수행한다.

---

# 📝 Completion Record

- **Result:** PASS
- **Status:** Done
- **Decision Result:** APPROVED / D33 Fixed
- **Completed Date:** 2026-08-31
- **Reviewer:** 이하영, 이재환 — 영향 분야 검토
- **Approver:** 이권욱
- **Exit Criteria:** Kubernetes 내부 관측 Stack, node-exporter 통제 예외, monitor01 외부 Watchdog, P0/P1 경계, Interface와 Rollback 원칙 승인
- **Closure Boundary:** 본 종결은 설계 Decision 완료를 의미한다. Kubernetes Manifest, Target, Dashboard, Alert, PVC, 보안 통제, 장애·복구 Runtime 완료는 `P1-MON-01`에서 별도 판정한다.
