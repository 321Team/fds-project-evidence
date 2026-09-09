# D34 / D-SEC-01 Approval and Review Disposition Record v1.0

- Record ID: D34
- Related Ticket: D-SEC-01
- Approval Date: 2026-09-01
- Approval Authority: Project Lead 이권욱
- Technical Review Owner: 이하영
- Support: 이재환
- Approval Instruction: `권장안 대로 모두 적용 후 정본 적용`
- Result: PASS — Recommendations Applied
- Canonical Release: FDS_Project_Implementation_Baseline_v3.1.14

---

## 1. 승인 범위

본 기록은 `D-SEC-01 6차 재검수 — 최적 권장안 및 영향성 검토`의 P0 수정사항과 Lead 결정표를 승인하고, 승인 결과를 기존 v3.1.13에 소급 덮어쓰지 않은 채 v3.1.14 정본으로 발행한다는 결정 증적이다.

## 2. 권장안 조치 결과

| # | 승인 항목 | 적용 결과 | 정본 반영 위치 |
|---:|---|---|---|
| 1 | 6개 Node firewalld OFF + Calico HEP/GNP | 적용 | Baseline §5.2, D-SEC §3, ICR v1.3, P1-K8S v1.1 |
| 2 | BGP Disabled + VXLANCrossSubnet + natOutgoing | 적용 | Baseline §5.2, D-SEC §3, P1-K8S v1.1 |
| 3 | kube-system enforce Privileged, audit/warn Restricted | 적용 | Baseline §5.3, D-SEC §1 |
| 4 | CoreDNS 별도 PSA 표현 제거·Manifest 하드닝 | 적용 | Baseline §5.3, D-SEC §1 |
| 5 | IF-06B Remote Write 유지, IF-24 P1 N/A | 적용 | Baseline §11/Interface Register, D-SEC §3, P1-MON v1.2, ICR v1.3 |
| 6 | static local PV·WaitForFirstConsumer·Retain·nodeAffinity | 적용 | Baseline §10, D-SEC §5, P1-K8S/P1-MON |
| 7 | P1 secretbox, P2 KMS v2 | 적용 | Baseline §6, D-SEC §5, P1-SEC Handoff |
| 8 | Prometheus/KSM RBAC 분리·nodes/proxy 금지 | 적용 | Baseline §6, D-SEC §4, P1-SEC/P1-MON |
| 9 | Runner 인증·Workflow 책임 분리 | 적용 | Baseline §7, D-SEC §4, P1-SEC/P1-CICD |
| 10 | ICR 범위를 Worker 3대에서 K8s Node 6대로 확대 | 적용 | ICR v1.3 |
| 11 | App 업무/metrics Port와 Probe 계약 정정 | 적용 | Baseline §8/Interface Register, D-SEC §3/§5, P1-APP Handoff |
| 12 | P1-LB API LB와 App NodePort 책임 분리 | 적용 | Baseline §4/§8, P1-LB Guide v1.2, Ticket Update Pack |

### 정본 교차검증 추가 교정

- `k8s-api-lb01 10.1.93.109`는 단순 Service VIP가 아니라 실제 LB VM Interface이므로 DNS Query Source가 될 수 있다.
- P1-LB Guide의 `8.8.8.8` 직접 사용을 제거하고 dns01/dns02 및 Search Domain을 적용했다.
- P1-DNS-01 v1.1에 `.109/32` BIND ACL·firewalld IPSet·Resolver·Failover Acceptance를 추가했다.
- 이는 기존 P1-DNS-01 범위의 Consumer ACL 변경이며 Routing/SNAT 변경이 없으므로 별도 네트워크 ICR을 발행하지 않는다.

## 3. 상태 전이

| Record | 이전 상태 | 승인 후 상태 |
|---|---|---|
| D-SEC-01 / D17 | Revision Required / In Review | Done / PASS |
| MS-G0-01 | In Progress / CONDITIONAL PASS | Done / FULL PASS |
| P1-K8S-01 | Preflight Conditional | Preflight GO / Runtime P1-LB Stage A 조건부 |
| P1-SEC-01 | Prework only | Manifest/Prework GO / Runtime Platform Ready 조건부 |
| ICR-D-NET-01-01 | v1.2 In Review / Worker 중심 | v1.3 Approved Change / In Progress / 6 Node |
| P1-MON-01 | In Progress | Manifest GO / Runtime Storage·App·Security·IF-06B 조건부 |

## 4. 승인과 Runtime 검증의 경계

- 본 승인은 설계·Ticket Handoff·정본 발행에 대한 승인이다.
- Runtime 미검증 항목을 PASS 또는 Done으로 간주하지 않는다.
- HEP/GNP, Secret encryption, Storage/PVC, Probe 장애 주입, IF-06B Route·TLS·heartbeat는 각 구현 티켓의 Evidence로 판정한다.
- Secret, token, kubeconfig, CA private key와 실제 credential은 본 증적에 포함하지 않는다.

## 5. 형상관리

- v3.1.13은 이전 Released 정본으로 보존한다.
- v3.1.14를 2026-09-01 현재 정본으로 승격한다.
- Rollback 시 v3.1.14 파일을 삭제하거나 v3.1.13을 수정하지 않고, 승인된 변경 통제로 이전 정본을 재지정한다.
