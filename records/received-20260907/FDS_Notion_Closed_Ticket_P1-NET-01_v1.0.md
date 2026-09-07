# FDS 종결 티켓 P1-NET-01 Notion 입력본 v1.0

> 기준일: `2026-08-27`  
> 기준 Baseline: `FDS_Project_Implementation_Baseline_v3.1.5`  
> 대상: `P1-NET-01`  
> 현재 상태: `DONE / CLOSED`  
> 실제 종결일: `2026-08-26`  
> 용도: Notion 종결 티켓 속성 입력 및 증적 제출용 Page Body

---

## 1. 속성정보

| Property | 입력값 | 근거 / 비고 |
|---|---|---|
| Title / Item Name | P1-NET-01 — Bridged Multi-MAC Smoke Test / Source Preservation | 최초 WBS 명칭과 실제 종결 범위를 병기 |
| Record ID | P1-NET-01 | Upsert Key |
| Phase | Phase 1 | 최초 WBS |
| Category | Network / Connectivity Validation | 수행 범위 기준 |
| Type | Task | 최초 WBS |
| Status | Done | Closed Register v3.1.5 |
| Priority | P0 | 최초 WBS |
| Start | 2026-08-27 | 최초 계획일 |
| End | 2026-08-27 | 최초 계획일 |
| Calendar Days | 1 | 최초 계획 기준 |
| Working Days | 1 | 최초 계획 기준 |
| Closed Date | 2026-08-26 | 실제 종결 기록 |
| Lead | 이권욱 | Infrastructure / Network 담당 |
| Support | 이하영 | 최초 WBS |
| Exit Criteria | Bridged Node 6대의 `/24`·Gateway·승인 통신 경로와 Physical/Management Return Route를 검증하고, Management Source Preservation `PASS=6`, `FAIL=0` 증적을 확보 | Closed Register 및 Network Closure Evidence |
| Related Decision IDs | D05; D13; D14; D15; D16 | Bridged Endpoint, VMnet 분리, Return Route, 비관리 Gateway, IP 예외 |
| Related Risk IDs | RISK-02; RISK-04 | Bridged Multi-MAC 및 비관리 Gateway 검증 위험 |
| Source | FDS_Project_Implementation_Baseline_v3.1.5; FDS_Remaining_Backlog_WBS_v3.1.5; FDS_Network_Baseline_v2.3; D-NET-01_Closure_Report_v1.0; FDS_Notion_Network_Parameter_Patch_v1.2 | 권위·종결 근거 |
| Schedule Note | 최초 계획은 2026-08-27 1일이었으나 D-NET-01 및 P1-LNX-01 통합 검증 증적이 2026-08-26 확보되어 조기 종결했다. Remaining Backlog에는 재등록하지 않고 Closed Ticket로 관리한다. | 계획일과 실제 종결일 구분 |

### 입력 통제

- `Record ID=P1-NET-01`로 Upsert하고 중복 Page를 생성하지 않는다.
- `Status=Done`, `Closed Date=2026-08-26`을 유지한다.
- `Start/End=2026-08-27`은 최초 계획값이며 실제 작업완료일로 해석하지 않는다.
- 담당·지원 인명은 `이권욱`, `이하영` 풀네임으로 입력한다.
- Reviewer / Approver는 확인 가능한 승인 기록이 없어 임의 지정하지 않는다.

---

## 2. Description

아래 코드 블록 안쪽을 `P1-NET-01` Notion Page Body에 붙여넣는다.

```markdown
# 🎯 User Story

Infrastructure / Network 담당자 이권욱으로서 Kubernetes 예정 Physical Node 6대의 VMware Bridged 통신과 Management Return Path를 검증한다.

이를 통해 Shared L2 환경에서 Node별 Bridged 연결이 승인된 경로로 동작하고, `ansible01(10.250.10.10)`의 Management Source가 원본 주소로 유지되는지 확인하여 Kubernetes 및 Ansible 후속 구축의 네트워크 선행조건을 종결한다.

---

# 📌 Scope

## In Scope

- Kubernetes 예정 Physical Node 6대의 Bridged NIC 및 `/24` Prefix 확인
- Default Gateway `10.1.93.254` 설정 확인
- Node 간 승인된 Physical 경로의 통신 확인
- Physical Node의 `10.250.10.0/24 via 10.1.93.58` Return Route 확인
- `ansible01(10.250.10.10)`에서 Physical Node로 접속 시 Remote Observed Source 확인
- Management Source Preservation `PASS=6`, `FAIL=0` 검증
- DAD / ARP / Route / 승인 TCP 경로 기반 Positive·Negative Test
- Network Baseline 및 Closure Evidence 연결

## Out of Scope

- `containerd`, `kubelet`, `kubeadm`, Kubernetes API Server 및 Calico 구성
- Kubernetes Required Port의 서비스 기동 완료 판정
- BIND Primary / Secondary 및 `fds.internal` 구축
- Reverse Zone / PTR
- 현장 Gateway `10.1.93.254`의 설정 변경 또는 관리권 확보
- Phase 2 OCI / AWS VPN 구성

---

# 📋 핵심 요구사항

- [x] Physical Node 6대의 Bridged Interface가 Physical LAN `10.1.93.0/24`에 연결된다.
- [x] 각 Node의 Prefix가 `/24`로 설정되어 있다.
- [x] 각 Node의 Default Gateway가 `10.1.93.254`로 설정되어 있다.
- [x] 모든 Physical Node에 `10.250.10.0/24 via 10.1.93.58` Return Route가 존재한다.
- [x] 내부 Physical / Management 경로에 Source NAT를 적용하지 않는다.
- [x] Management Source를 `10.250.10.10` 원본 주소로 보존한다.
- [x] `.100`, `.101`, `.106`은 `DO_NOT_USE`로 유지하고 FDS VM에 할당하지 않는다.
- [x] 프로젝트 비관리 Gateway의 Ping 단독 결과를 완료 Gate로 사용하지 않는다.

---

# ✅ Acceptance Criteria

- [x] Bridged Node 6대의 Prefix가 모두 `/24`다.
- [x] Bridged Node 6대의 Default Gateway가 모두 `10.1.93.254`다.
- [x] Physical / Management Return Route가 `10.1.93.58` 경유로 정상 동작한다.
- [x] Node 간 승인 경로 통신이 정상이다.
- [x] `ansible01(10.250.10.10)`에서 접속할 때 Remote Observed Source가 `10.250.10.10`으로 유지된다.
- [x] Management Source Preservation 결과가 `PASS=6`, `FAIL=0`이다.
- [x] 관련 Linux Network Verify 결과가 `FAIL=0`이다.
- [x] 비관리 Gateway의 ICMP 응답 여부와 무관하게 Route / ARP / 승인 TCP 경로로 합격 근거를 확보했다.

---

# 🧪 Test Result

| TC ID | 검증 항목 | 예상 결과 | 실제 결과 | 판정 |
|---|---|---|---|---|
| TC-P1NET-01 | Node 6대 Prefix / Gateway | `/24`, Gateway `10.1.93.254` | 기준값 일치 | PASS |
| TC-P1NET-02 | Bridged Node 승인 경로 | Node 간 승인 경로 통신 가능 | 통신 정상 | PASS |
| TC-P1NET-03 | Management Return Route | `10.250.10.0/24 via 10.1.93.58` | 6대 경로 정상 | PASS |
| TC-P1NET-04 | Source Preservation | Remote Observed Source=`10.250.10.10` | `PASS=6`, `FAIL=0` | PASS |
| TC-P1NET-05 | Gateway 비관리 조건 | Ping 단독이 아닌 Route / ARP / TCP로 판정 | 승인 경로 증적 확보 | PASS |
| TC-P1NET-06 | 사용금지 IP Negative Test | `.100/.101/.106` 미할당 | `DO_NOT_USE` 유지 | PASS |

---

# 🧪 검증 및 증적

## Primary Evidence

- `03_Linux_Node_Network_Verify`
- `05_Physical_Return_Route`
- `06_Source_Preservation_PASS6`
- `07_Management_VM_Verify`

## Supporting Evidence

- `01_Windows_PostBuild_server01-08`
- `02_VMware_Virtual_Network_Editor`
- `04_K8s_Linux_Prerequisites`
- `08_mgmt-gw01_Verify`
- `09_DO_NOT_USE_IP_Exception`
- `10_D-NET-01_Closure`

## Evidence Location / Source

- Evidence Path: `docs/evidence/D-NET-01/`
- Configuration Baseline: `FDS_Network_Baseline_v2.3`
- Closure Record: `D-NET-01_Closure_Report_v1.0`
- Parameter Patch: `FDS_Notion_Network_Parameter_Patch_v1.2`
- Closed Register: `FDS_Remaining_Backlog_WBS_v3.1.5`

> P1-NET-01은 D-NET-01 및 P1-LNX-01 수행 과정에서 확보된 공통 Network Evidence를 재사용한다. 증적 제출 시 위 인덱스의 실제 로그·요약·캡처 파일을 함께 첨부한다.

---

# 🔗 Dependency

- **Blocked By:** `D-NET-01`, `P1-LNX-01` — `DONE / CLOSED`
- **Blocks / Next:** `P1-ANS-01`, `P1-K8S-01`, G1 Infrastructure Ready
- **Related Ticket:** `D-NET-01`, `P1-LNX-01`, `P1-ANS-01`, `P1-K8S-01`
- **Milestone Contribution:** G0 Network `PASS`의 실행 검증 근거 및 G1 Network 선행조건

---

# ⚖️ Decision / Risk Control

- **Related Decision IDs:** `D05`, `D13`, `D14`, `D15`, `D16`
- **Decision Control:** Bridged Endpoint, VMnet 분리, Return Route, 내부 Source NAT 금지, 비관리 Gateway 및 Reserved / DO_NOT_USE 주소 결정을 준수한다.
- **Related Risk IDs:** `RISK-02`, `RISK-04`
- **Risk Control:** Bridged Multi-MAC 제한은 Node 6대 실제 통신으로 검증하고, 비관리 Gateway는 Ping 단독이 아닌 Route / ARP / 승인 TCP 경로로 판정한다.
- **Change Control:** IP, Prefix, Gateway, VMnet 역할, Route, NAT 또는 승인 통신 경로 변경은 Network / Interface Change Request 후 반영한다.

---

# 📝 Completion Record

- **Result:** `PASS`
- **Status:** `DONE`
- **Ticket Gate:** `CLOSED`
- **Lead:** 이권욱
- **Support:** 이하영
- **Original Plan:** `2026-08-27` / 1일
- **Completed Date:** `2026-08-26`
- **Exit Criteria:** Bridged Node 6대 Connectivity, Physical / Management Return Route, Management Source Preservation `PASS=6`, `FAIL=0`, 관련 Network Verify `FAIL=0`
- **Reviewer / Approver:** 미입력 — 입력 시 풀네임 사용
- **Closure Basis:** `FDS_Network_Baseline_v2.3`, `D-NET-01_Closure_Report_v1.0`, `FDS_Notion_Network_Parameter_Patch_v1.2`, `FDS_Remaining_Backlog_WBS_v3.1.5`
- **Closure Boundary:** 본 종결은 Bridged Connectivity와 Management Source Preservation 범위에 한한다. Kubernetes 서비스 및 Required Port 기동 완료는 `P1-K8S-01`에서 판정한다.
- **Next:** 종결 이력을 유지하고 `P1-ANS-01`, `P1-K8S-01`의 선행 Network Evidence로 연결한다.
```

---

## 3. 증적 제출 체크리스트

- [ ] Notion 속성에 `Status=Done`, `Closed Date=2026-08-26` 반영
- [ ] Lead `이권욱`, Support `이하영` 풀네임 확인
- [ ] Page Body Description 적용
- [ ] `03_Linux_Node_Network_Verify` 첨부
- [ ] `05_Physical_Return_Route` 첨부
- [ ] `06_Source_Preservation_PASS6` 첨부
- [ ] `07_Management_VM_Verify` 첨부
- [ ] `D-NET-01_Closure_Report_v1.0` 첨부 또는 링크
- [ ] Reviewer / Approver를 승인 기록에 따라 풀네임으로 입력
- [ ] 증적 파일과 본문의 `PASS=6`, `FAIL=0` 값 대조

## 4. 제출 시 유의사항

- 현재 작업공간에서 확인된 것은 증적 인덱스와 Closure Report다. 실제 로그·요약·캡처 파일은 제출 시 별도로 첨부해야 한다.
- Reviewer / Approver의 풀네임은 확인 자료가 없어 본 문서에서 지정하지 않았다.
- P1-NET-01은 종결 티켓이므로 Remaining Backlog View가 아니라 Closed Ticket View에서 관리한다.
