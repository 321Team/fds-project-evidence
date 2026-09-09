# P1-DNS-01 — Internal DNS Primary/Secondary 구축 v1.3-R5

> Current Canonical Baseline: `FDS_Project_Implementation_Baseline_v3.1.15`  
> Execution Evidence Basis: `P1-DNS-01-FRESH-20260902-R2` / Remediation Kit v1.8 / Runbook Supplement v1.9  
> 문서 기준일: 2026-09-03  
> 현재 상태: **Done**  
> Support Review: **이하영 승인 완료 (2026-09-03)**  
> Runbook 보완: **v1.9 설치·정적 검증·R2 정본 읽기 전용 검증 PASS**

## 리뷰 판정 요약

| 검토 영역 | 결과 | 근거 및 남은 조치 |
|---|---|---|
| Primary/Secondary DNS | PASS | dns01 Primary, dns02 Secondary, SOA Serial `2026090101` 일치 |
| DNS 보안 통제 | PASS | 승인 Source ACL/IPSet, TCP/UDP 53 최소 허용, 미인증 AXFR 차단, HMAC-SHA256 TSIG 확인 |
| Resolver/Failover | PASS | k8s-control01과 k8s-api-lb01에서 `.52 → .53` 자동 Failover 및 Primary 복구 확인 |
| 승인 DNS Source `.109` | PASS | dns01/dns02의 BIND ACL과 firewalld IPSet에 `10.1.93.109` 반영·검증 |
| Evidence 무결성 | PASS | Raw TXT 11개, Sidecar 11개, 중앙 `SHA256SUMS` 12개 항목 모두 검증 성공 |
| 정본 패키지 | PASS | v1.8 기반 R2 ZIP/Sidecar 검증 및 정본 경로 반영 완료 |
| Support Review | PASS | 이하영의 전체 Node Resolver 및 CoreDNS Source 질의에 대한 소유권·일정·처리 기준을 반영했고 2026-09-03 승인을 완료했다. |
| 운영 Runbook 보완 | PASS | ansible01/server01_ansible에서 v1.9 Kit 설치 RC 0, Runbook 자체 검증 RC 0, R2 정본 읽기 전용 검증 RC 0을 확인했다. ZIP Hash, CRC, 내부 Manifest, 11/11/12 Count, DNS-EV-03, `.109`, Failover 구분, Secret 비노출이 모두 PASS다. |

**최종 판정:** 기술 구현·증적·Runbook·Support Review 조건이 모두 PASS다. 이권욱 Lead 확정으로 `Done`으로 종결한다.

## 이하영 Support Review 반영

### 리뷰 의견

- 현재 Evidence로는 k8s-control01의 DNS Resolver Canary 완료만 확인된다.
- Kubernetes 전체 Node인 control01~03, worker01~03도 BIND DNS `10.1.93.52`, `10.1.93.53`으로 전환할 것인지 확인이 필요하다.
- 전체 Node 적용 및 검증 일정을 명확히 해야 한다.
- P1-K8S-01에서 CoreDNS의 `fds.internal` Forwarding을 구성한 뒤 BIND에서 관측된 Source IP를 P1-DNS-01 담당자에게 전달한다.

### 반영 결정

| 검토 항목 | 결정 |
|---|---|
| 전체 Node 전환 여부 | **전환 예정**. control01~03, worker01~03은 최종적으로 dns01 `.52`, dns02 `.53`, Search Domain `fds.internal`을 사용한다. |
| 현재 완료 범위 | k8s-control01 Canary/Rollback/Failover와 k8s-api-lb01 Resolver/Failover만 완료됐다. 나머지 5개 Node는 아직 완료로 판정하지 않는다. |
| 실행 소유권 | P1-DNS-01은 Resolver 표준과 DNS 서비스 계약을 제공한다. P1-ANS-01은 종결 상태이므로 6개 Node 반복 적용·멱등성 검증은 신규 `CR-P1-ANS-01-01`에서 수행한다. |
| Kubernetes 소유권 | CoreDNS `fds.internal` Forwarding 구성과 Pod 내부 해석 검증은 P1-K8S-01에서 수행한다. |
| P1-K8S-01 영향 | P1-DNS-01은 G1 Non-blocker다. `/etc/hosts`와 IP Endpoint 임시 조치로 Kubernetes 구축을 계속할 수 있다. |
| P1-DNS-01 종료 조건 | 전체 6개 Node 전환 완료를 P1-DNS-01의 Done 조건으로 추가하지 않는다. 대신 소유 티켓, 일정과 검증 기준이 명시된 Handoff를 종료 조건으로 관리한다. |

### 승인 결과

| 항목 | 결과 |
|---|---|
| Support Reviewer | 이하영 |
| 승인일 | 2026-09-03 |
| 상태 | PASS / Approved |
| 승인 근거 | 이권욱 Lead의 승인 완료 확정 및 이하영 Reviewer 회신 캡처 |
| Evidence | `P1-DNS-01_Support_Review_Approval_Record_20260903.md`, `P1-DNS-01_Support_Review_Approval_20260903.png` |

### 전체 Node 적용 권장 일정

| 일자 | 대상 | 작업 및 검증 | 소유 |
|---|---|---|---|
| 2026-09-03 | k8s-control01 | Canary, Public Resolver Rollback, 승인 Resolver 재적용, `.52 → .53` Failover 완료 | P1-DNS-01 Evidence 완료 |
| 2026-09-04 | k8s-control02, k8s-control03 | NetworkManager Profile에 `.52/.53`와 `fds.internal` 적용 후 FQDN·Short Name·외부 이름 해석 검증 | CR-P1-ANS-01-01 |
| 2026-09-07 | k8s-worker01~03 | 동일 설정 적용 후 전체 6개 Node의 설정 Drift, 이름 해석 및 대표 Failover 검증 | CR-P1-ANS-01-01 |

위 일정은 P1-DNS-01의 WBS 종료일인 2026-09-07에 맞춘 권장안이다. P1-ANS-01은 `Done`이므로 기존 티켓을 재개하지 않고 `CR-P1-ANS-01-01`을 발행해 위 일정을 이관한다.

### CoreDNS Source IP 인계 절차

1. 이하영은 P1-K8S-01에서 CoreDNS가 `fds.internal` 질의를 dns01/dns02로 Forward하도록 구성한다.
2. dns01/dns02에서 UDP 53과 TCP 53 요청의 실제 Source IP를 패킷 또는 `named` 로그로 관측한다.
3. 이하영은 관측 Source IP, 관측 시각, 질의 FQDN, UDP/TCP 구분, CoreDNS Pod/Node 정보를 이권욱에게 전달한다.
4. Source가 기존 승인 Node IP `.102~.108` 중 하나이면 ACL/IPSet 변경 없이 Positive Test만 추가한다.
5. Source가 새로운 **고정 IP**이면 이권욱이 해당 `/32`만 BIND ACL과 양쪽 firewalld IPSet에 반영하고 UDP/TCP 53을 재검증한다.
6. Source가 재생성될 수 있는 CoreDNS Pod IP이거나 Pod CIDR 허용이 필요하면 임시 `/32` 또는 Pod CIDR 전체를 곧바로 허용하지 않는다. P1-K8S-01에서 안정적인 Node SNAT/고정 Egress 대안을 우선 검토하고, Network Baseline 변경이 필요할 때만 ICR-D-NET-01을 발행한다.

## Notion 데이터 속성

| Property | 입력값 |
|---|---|
| Record ID | P1-DNS-01 |
| Phase | Phase 1 |
| Category | DNS / Supporting Service |
| Type | Task |
| Status | Done |
| Priority | P1 |
| Start | 2026-08-28 |
| End | 2026-09-07 |
| Calendar Days | 11 |
| Working Days | 7 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | Primary/Secondary·TSIG·승인 Source Query/Recursion·Resolver Failover와 k8s-api-lb01 `.109` 반영이 검증되고, R2 정본 ZIP·Sidecar·내부 `SHA256SUMS` 검증, Secret 비노출 확인, v1.9 Runbook의 ansible01 실행 검증 및 Support Review 승인이 완료됨 |
| Related Decision IDs | D08; D09; D34; D35 |
| Related Risk IDs | RISK-02; RISK-04; RISK-07 |
| Source | FDS Project Implementation Baseline v3.1.15; FDS Network Baseline v2.3; P1-DNS-01 Notion Description v1.2; P1-DNS-01 R2 Evidence Remediation Kit v1.8; P1-DNS-01 R2 Runbook Supplement v1.9; P1-DNS-01-FRESH-20260902-R2; P1-DNS-01 Runbook v1.9 Validation Record 20260903 |
| Schedule Note | 2026-09-03 DNS 기술·증적·Runbook 검증 PASS 및 이하영 Support Review 승인 완료로 Done 전환. P1-ANS-01은 Done이므로 전체 Node Resolver는 CR-P1-ANS-01-01에서 2026-09-04 Control Plane 잔여 2대, 2026-09-07 Worker 3대 및 6 Node 종합 검증 일정으로 수행한다. CoreDNS Source 관측과 필요 시 ACL/ICR 분기는 P1-K8S-01 후속 작업으로 유지한다. |

## 🎯 User Story

인프라 담당자로서 `fds.internal` 내부 DNS를 Primary/Secondary 구조로 제공한다. 이를 통해 Kubernetes Node와 승인된 Service VM이 고정 IP 대신 일관된 FQDN을 사용하고, Primary 장애 시에도 Secondary를 통해 내부 및 외부 이름 해석을 지속할 수 있도록 한다.

## 📌 Scope

### In Scope

- dns01 `10.1.93.52` Primary BIND 구축
- dns02 `10.1.93.53` Secondary BIND 구축
- Forward Zone `fds.internal` 및 승인 A Record 관리
- HMAC-SHA256 TSIG 기반 Zone Transfer
- 승인 Source 기반 Query/Recursion ACL
- firewalld IPSet + Rich Rule 기반 TCP/UDP 53 최소 허용
- 승인 External Forwarder `8.8.8.8` 및 `forward only` 적용
- Primary/Secondary SOA Serial 일치 검증
- 미인증 AXFR 및 비승인 Source Query/Recursion 차단
- Primary 장애 중 Secondary Resolution/Forwarding 검증 및 Primary 복구 확인
- k8s-control01 Client Resolver Canary, Rollback 및 자동 Failover 검증
- k8s-api-lb01 `10.1.93.109`의 DNS ACL/IPSet, Resolver 및 Failover 검증
- Kubernetes 전체 Node에 적용할 Resolver 표준과 CR-P1-ANS-01-01 Handoff 정의
- P1-K8S-01 CoreDNS Source IP 관측 결과의 ACL 변경 판단 기준
- Host별 원본 Evidence, 파일별 Sidecar, 중앙 `SHA256SUMS`, ZIP Sidecar를 포함한 증적 생명주기
- 운영, 검증, Rollback 및 Secret 비노출 기준 정의

### Out of Scope

- Reverse Zone 및 PTR Record
- DNSSEC Zone Signing
- Authoritative/Recursive DNS 서버의 물리적 완전 분리
- Hybrid/AWS Route 53 Resolver 연동
- CoreDNS Pod의 실제 Source IP 확정 및 Kubernetes 내부 Forwarding 구현
- 승인되지 않은 Management Subnet 전체 허용
- P1-DNS-01 담당자가 개별 Node에 직접 수행하는 Resolver 일괄 배포 — 반복 적용과 멱등성 검증은 CR-P1-ANS-01-01 범위
- DNS 이외 Host Hardening 항목의 임의 변경

## 📋 핵심 요구사항

### DNS 서비스 및 가용성

- [x] dns01을 `fds.internal` Primary로 구성한다.
- [x] dns02를 `fds.internal` Secondary로 구성한다.
- [x] Primary/Secondary의 SOA Serial은 `2026090101`로 일치한다.
- [x] UDP와 TCP 53 Listener를 서비스 IP와 Loopback에만 노출한다.
- [x] `named`는 `enabled`, `active` 상태로 운영한다.
- [x] SELinux Enforcing 상태에서 서비스를 운영한다.
- [x] Primary 장애 시 Secondary가 내부 이름 및 외부 Forwarding을 지속한다.
- [x] Primary 복구 후 권한 응답과 Zone 상태가 정상임을 확인한다.

### Zone Transfer 및 접근 통제

- [x] Zone Transfer는 HMAC-SHA256 TSIG 인증을 필수로 한다.
- [x] 인증된 Secondary Transfer는 성공한다.
- [x] 미인증 AXFR은 거부한다.
- [x] Query와 Recursion은 승인 Source IP에만 허용한다.
- [x] 공유망 `10.1.93.0/24` 전체를 DNS ACL로 허용하지 않는다.
- [x] Host Firewall은 IPSet과 Rich Rule로 TCP/UDP 53을 제한한다.
- [x] 광범위한 firewalld `service=dns` 허용은 제거한다.
- [x] monitor01 `10.250.10.30`의 직접 질의는 차단한다.
- [x] TSIG Secret과 TSIG MAC은 Evidence에 기록하지 않는다.

### Resolver 및 Forwarding

- [x] 외부 질의는 `8.8.8.8`로 Forward하며 `forward only`를 적용한다.
- [x] k8s-control01은 `10.1.93.52`, `10.1.93.53` 순서와 Search Domain `fds.internal`을 사용한다.
- [x] k8s-control01의 FQDN, Short Name, 외부 이름 해석을 검증한다.
- [x] k8s-control01의 Public Resolver Rollback과 승인 Resolver 재적용을 검증한다.
- [x] k8s-api-lb01 `10.1.93.109`를 양쪽 BIND ACL과 firewalld IPSet에 반영한다.
- [x] k8s-api-lb01의 FQDN, Short Name, 외부 이름 해석을 검증한다.
- [x] k8s-control01과 k8s-api-lb01에서 dns01 장애 시 dns02 자동 Failover를 검증한다.
- [x] 전체 6개 Kubernetes Node가 사용할 Resolver 표준과 CR-P1-ANS-01-01 일정·검증 기준을 정의한다.
- [ ] k8s-control02/03과 k8s-worker01~03에 승인 Resolver를 적용하고 전체 6개 Node를 검증한다. 이 항목은 CR-P1-ANS-01-01 작업이며 P1-DNS-01 Done의 직접 차단 조건은 아니다.
- [ ] P1-K8S-01에서 CoreDNS Forwarding Source IP를 관측하고 ACL 변경 필요 여부를 판정한다. 이 항목은 P1-K8S-01 연계 작업이며 P1-DNS-01 Done의 직접 차단 조건은 아니다.

### Evidence 및 운영 문서

- [x] 원본 TXT 11개와 대응 Sidecar 11개를 확보한다.
- [x] `EVIDENCE_INDEX.md`와 원본 TXT를 포함한 중앙 `SHA256SUMS` 12개 항목을 생성한다.
- [x] 모든 파일별 Sidecar와 중앙 Manifest 검증을 통과한다.
- [x] ZIP CRC, ZIP Sidecar 및 필수 멤버 검증을 통과한다.
- [x] DNS-EV-03 판정을 `PASS`로 확정한다.
- [x] v1.7 정본을 백업·Retire하고 v1.8 기반 R2를 정본 경로에 승격한다.
- [x] Runbook v1.9에서 대화형 셸을 종료할 수 있는 상위 `exit` 사용을 Subshell/Return Code 방식으로 보완한다.
- [x] ZIP Sidecar는 실행 위치에 독립적인 상대 파일명만 기록하도록 Runbook v1.9에 고정한다.
- [x] ansible01에서 `validate_runbook_v1_9.sh`와 `validate_canonical_r2_v1_9.sh`의 Return Code 0을 확인하고 결과를 리뷰 기록에 반영한다.
- [x] 이하영 Support Review를 2026-09-03 완료한다.

## 승인 DNS 레코드

| FQDN | IPv4 | 용도 |
|---|---:|---|
| `dns01.fds.internal` | `10.1.93.52` | Primary DNS |
| `dns02.fds.internal` | `10.1.93.53` | Secondary DNS |
| `edge.fds.internal` | `10.1.93.50` | Edge/DMZ |
| `vpn-gw.fds.internal` | `10.1.93.51` | VPN Gateway |
| `harbor.fds.internal` | `10.1.93.54` | Harbor Registry |
| `db.fds.internal` | `10.1.93.55` | PostgreSQL VM |
| `control01.fds.internal` | `10.1.93.102` | Kubernetes Control Plane |
| `control02.fds.internal` | `10.1.93.103` | Kubernetes Control Plane |
| `control03.fds.internal` | `10.1.93.104` | Kubernetes Control Plane |
| `worker01.fds.internal` | `10.1.93.105` | Kubernetes Worker |
| `worker02.fds.internal` | `10.1.93.107` | Kubernetes Worker |
| `worker03.fds.internal` | `10.1.93.108` | Kubernetes Worker |
| `k8s-api.fds.internal` | `10.1.93.109` | Kubernetes API LB |

## 승인 DNS Source

양쪽 BIND ACL과 firewalld IPSet은 다음 `/32` Source만 허용한다.

| 분류 | 승인 IP |
|---|---|
| Edge/VPN | `10.1.93.50`, `10.1.93.51` |
| DNS | `10.1.93.52`, `10.1.93.53` |
| Registry/DB | `10.1.93.54`, `10.1.93.55` |
| Control Plane | `10.1.93.102`, `10.1.93.103`, `10.1.93.104` |
| Worker | `10.1.93.105`, `10.1.93.107`, `10.1.93.108` |
| API LB | `10.1.93.109` |

다음 Source는 명시적으로 승인하지 않는다.

- monitor01 `10.250.10.30`
- Management 대역 전체
- Physical LAN `10.1.93.0/24` 전체
- 향후 Pod CIDR 전체

CoreDNS는 P1-K8S-01에서 실제 Source IP를 관측한 뒤 필요한 주소만 추가한다. 관측 전에 Node 대역이나 Pod CIDR 전체를 선제 허용하지 않는다.

## ✅ Acceptance Criteria

| ID | 완료 조건 | 현재 판정 |
|---|---|---|
| DNS-AC-01 | dns01 Primary와 dns02 Secondary가 활성화되고 부팅 시 자동 시작됨 | PASS |
| DNS-AC-02 | 승인된 13개 A Record가 양쪽 권한 서버에서 동일하게 응답함 | PASS |
| DNS-AC-03 | SOA Serial이 `2026090101`로 일치함 | PASS |
| DNS-AC-04 | Fresh HMAC-SHA256 TSIG Transfer가 성공하고 BADKEY/BADSIG가 없음 | PASS |
| DNS-AC-05 | 미인증 AXFR이 실패함 | PASS |
| DNS-AC-06 | 승인 Source만 Query/Recursion과 TCP/UDP 53에 접근할 수 있음 | PASS |
| DNS-AC-07 | `8.8.8.8` Forwarding과 `forward only` 외부 해석이 정상임 | PASS |
| DNS-AC-08 | Primary 중단 중 dns02가 내부·외부 해석을 지속함 | PASS |
| DNS-AC-09 | k8s-control01 Resolver Canary, Rollback, Reapply, Failover가 정상임 | PASS |
| DNS-AC-10 | k8s-api-lb01 `.109`의 ACL/IPSet, Resolver 및 Failover가 정상임 | PASS |
| DNS-AC-11 | monitor01의 직접 내부/재귀 질의가 차단됨 | PASS |
| DNS-AC-12 | 원본 11개, Sidecar 11개, Manifest 12개와 ZIP Sidecar가 검증됨 | PASS |
| DNS-AC-13 | Evidence에 TSIG Secret, Key Hash, 인증 AXFR MAC이 노출되지 않음 | PASS |
| DNS-AC-14 | v1.8 기반 R2가 정본 경로에 반영되고 ZIP SHA-256이 일치함 | PASS |
| DNS-AC-15 | 재실행 가능한 Runbook에 Subshell Guard와 상대 ZIP Sidecar 규칙이 반영됨 | PASS — v1.9 설치/Runbook/Canonical RC 0 |
| DNS-AC-16 | 이하영 Support Reviewer가 정본과 검증 결과를 승인함 | PASS — 2026-09-03 |
| DNS-AC-17 | 전체 6개 Node Resolver 전환의 소유 티켓, 일정, 검증 기준이 명시됨 | PASS |
| DNS-AC-18 | CoreDNS Source 관측과 ACL/ICR 분기 기준이 P1-K8S-01 Handoff로 명시됨 | PASS |

## 🧪 검증 및 증적

### Test 결과

| Test ID | 검증 항목 | 결과 | Evidence |
|---|---|---|---|
| DNS-PT-01 | dns01 권한 A/SOA 및 승인 13개 Record | PASS | `dns01/20260902T184229+0900_dns01_evidence.txt`, `inventory/20260902T212724+0900_dns_record_inventory_evidence.txt` |
| DNS-PT-02 | dns02 권한 A/SOA 및 Secondary 상태 | PASS | `dns02/20260902T184239+0900_dns02_evidence.txt` |
| DNS-PT-03 | 외부 Forwarding | PASS | dns01/dns02 Evidence |
| DNS-PT-04 | Fresh HMAC-SHA256 TSIG Transfer | PASS | `tsig/20260902T212908+0900_dns02_fresh_tsig_evidence.txt` |
| DNS-PT-05 | Primary 장애, Secondary 지속 서비스, Primary 복구 | PASS | `failover/` 및 `recovery/` Evidence |
| DNS-NT-01 | 비승인 Source 내부 질의 차단 | PASS | `monitor01/20260902T184303+0900_monitor01_negative.txt` |
| DNS-NT-02 | 미인증 AXFR 차단 | PASS | dns01/dns02 Evidence |
| DNS-NT-03 | 비승인 Source 재귀 질의 차단 | PASS | monitor01 Negative Evidence |
| DNS-NT-04 | Reverse/PTR | N/A | Phase 1 Out of Scope |
| DNS-CR-01 | k8s-control01 Resolver Canary | PASS | `client/20260902T184246+0900_k8s_control01_evidence.txt` |
| DNS-CR-02 | k8s-control01 Public Resolver Rollback | PASS | `rollback/20260902T184517+0900_k8s_control01_rollback_evidence.txt` |
| DNS-CR-03 | 승인 Resolver 재적용 | PASS | Client Evidence |
| DNS-CR-04 | k8s-control01 `.52 → .53` 자동 Failover | PASS | `failover/20260902T184138+0900_k8s_control01_failover_evidence.txt` |
| DNS-CR-05 | k8s-api-lb01 `.109` Resolver/ACL/IPSet/Failover | PASS | `lb/20260902T184256+0900_k8s_api_lb01_evidence.txt`, `failover/20260902T184144+0900_k8s_api_lb01_failover_evidence.txt` |
| DNS-EV-01 | dns01 원본, Sidecar, Record Inventory | PASS | dns01 및 inventory Evidence |
| DNS-EV-02 | dns02 원본, Sidecar, Fresh TSIG | PASS | dns02 및 tsig Evidence |
| DNS-EV-03 | 중앙 무결성, Index, Manifest, ZIP Sidecar | PASS | `EVIDENCE_INDEX.md`, `SHA256SUMS`, ZIP Sidecar |
| DNS-RB-01 | Runbook v1.9 설치 및 자체 정적 검증 | PASS | `P1-DNS-01_Runbook_v1.9_Validation_Record_20260903.md` |
| DNS-RB-02 | R2 정본 읽기 전용 무결성 재검증 | PASS | `P1-DNS-01_Runbook_v1.9_Validation_Record_20260903.md` |

### 정본 Evidence 위치

- 논리 경로: `docs/evidence/P1-DNS-01/`
- 중앙 서버: ansible01
- 중앙 절대 경로: `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/`
- 정본 Directory: `P1-DNS-01-FRESH-20260902-R2/`
- 정본 ZIP: `P1-DNS-01-FRESH-20260902-R2.zip`
- ZIP Sidecar: `P1-DNS-01-FRESH-20260902-R2.zip.sha256`
- 정본 ZIP SHA-256: `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab`

### 최종 무결성 수치

| 항목 | 최종값 | 판정 |
|---|---:|---|
| Raw TXT | 11 | PASS |
| TXT Sidecar | 11 | PASS |
| 중앙 `SHA256SUMS` 항목 | 12 | PASS |
| ZIP Sidecar 대상 | `P1-DNS-01-FRESH-20260902-R2.zip` | PASS |
| ZIP SHA-256 Check | Expected = Actual | PASS |
| ZIP CRC | No errors detected | PASS |
| Required Members | Present | PASS |
| DNS-EV-03 | PASS | PASS |

### Evidence 보안 기준

- TSIG Secret 원문을 저장하지 않는다.
- TSIG Key 파일 Hash를 저장하지 않는다.
- 인증 AXFR 출력의 TSIG MAC/Record를 저장하지 않는다.
- `/etc/named.conf` 및 Zone 파일처럼 Secret이 없는 구성만 Hash로 추적한다.
- Host별 원본은 서로 다른 로컬 `/approved` 경로를 하나의 공유 저장소로 간주하지 않는다.
- Host별 Staging → 보안 전송 → Sidecar 확인 → ansible01 중앙 집계 순서로 관리한다.

### 현재 재실행 정책

- DNS Collector, TSIG Rotation, Primary Stop/Start, Failover, Recovery, Resolver Rollback 테스트를 재실행하지 않는다.
- Support Review는 현재 정본 ZIP과 Sidecar 및 내부 `SHA256SUMS`를 대상으로 2026-09-03 완료했다.
- 추가 재실행은 정본 Hash 불일치, 누락, Secret 노출 또는 Reviewer의 구체적 재현 요구가 있을 때만 승인 후 수행한다.
- 전체 Node Resolver 배포 결과는 P1-DNS-01 R2 정본을 다시 생성하지 않고 `docs/evidence/CR-P1-ANS-01-01/`에 별도 보관한 뒤 본 티켓에 링크한다.
- CoreDNS Forwarding 결과는 P1-K8S-01 Evidence로 보관하며, BIND ACL/IPSet이 실제로 변경된 경우에만 P1-DNS-01에 변경 Evidence를 추가한다.

## 🔗 Dependency

### 선행 의존성

| 의존 항목 | 상태 | 설명 |
|---|---|---|
| D-NET-01 | Done | Physical LAN 주소와 기본 Network Baseline 확정 |
| P1-LNX-01 | Done | CentOS Stream 10, SELinux, firewalld 운영 기반 |
| D08 / D09 | Approved | `fds.internal`, dns01/dns02 역할 및 주소 확정 |
| D34 / D35 | Approved | k8s-api-lb01 `.109`와 최신 Interface Contract 반영 |

### 후속 연계

| 후속 티켓 | 이관 내용 |
|---|---|
| P1-K8S-01 | CoreDNS Forwarding, 실제 Source IP 관측, 기존 승인 Source 여부 확인 및 ACL/ICR 분기 |
| CR-P1-ANS-01-01 | 종결된 P1-ANS-01의 Change Request. 2026-09-04 control02/03, 2026-09-07 worker01~03 적용 및 전체 6개 Node 검증 |
| P1-LB-01 | `k8s-api.fds.internal` 소비 및 API LB 운영 |
| DEC-P1-TLS-01 | FQDN과 인증서 SAN 정합성 |
| P1-HBR-01 | `harbor.fds.internal` 소비 |
| P1-CICD-01 | Runner의 내부 FQDN 및 Harbor/Kubernetes API 소비 |
| P1-MON-01 | Monitoring 대상 FQDN 소비와 외부 Watchdog 연계 |

### Gate 영향

- P1-DNS-01은 **G1 Non-blocker Supporting Service**다.
- Kubernetes Bootstrap은 `/etc/hosts`와 IP Endpoint를 사용해 진행할 수 있다.
- DNS 미완료를 이유로 Kubernetes 구축 전체를 중단하지 않는다.
- 반대로 DNS 사용 전환 시에는 각 소비 티켓에서 Resolver와 FQDN 검증을 별도로 완료한다.
- 전체 Node Resolver 전환 지연은 P1-K8S-01을 차단하지 않지만, 운영 전환 전에는 CR-P1-ANS-01-01 Evidence로 6개 Node 상태를 확인한다.

## ⚖️ Decision / Risk Control

### 확정 Decision

| Decision | 확정 내용 |
|---|---|
| D08 | 내부 DNS Zone은 `fds.internal`을 사용한다. |
| D09 | dns01 `.52`를 Primary, dns02 `.53`을 Secondary로 사용한다. |
| D34 | k8s-api-lb01은 `10.1.93.109`, FQDN은 `k8s-api.fds.internal`을 사용한다. |
| D35 | 최신 Interface Contract에서도 DNS Consumer `.109`와 FQDN 계약을 유지한다. |
| TSIG | Zone Transfer는 HMAC-SHA256 TSIG만 허용한다. |
| Resolver | Client는 dns01 `.52`를 우선, dns02 `.53`을 차선으로 사용한다. |
| Search Domain | `fds.internal`을 사용한다. |
| Forwarding | P1은 `8.8.8.8`, `forward only`를 사용한다. |
| ACL | 공유 대역 전체가 아니라 승인된 `/32` Source만 허용한다. |
| Reverse/DNSSEC | Reverse/PTR와 DNSSEC Signing은 P1에서 제외한다. |

### 구현 중 발생한 이슈와 처분

| 이슈 | 원인 | 최종 처분 | 현재 영향 |
|---|---|---|---|
| dns01 BIND 미동작 | BIND 서비스가 비활성 상태 | 설치 상태 확인 후 구성·Enable·Start | 해소 |
| dns02 Zone 미로딩 | Primary `.52:53` 미가동으로 Host Unreachable | Primary 복구 및 Fresh TSIG Transfer | 해소 |
| dns02 SSH 로그인 실패 | dns01 계정 `server01_dns01`이 dns02에 존재하지 않음 | dns02 실제 계정 `server08` 사용 | 해소 |
| `/approved/evidence` Permission Denied | 일반 사용자에게 중앙 경로 생성 권한 없음 | 사용자 쓰기 가능한 Staging과 ansible01 중앙 집계로 변경 | 해소 |
| `.109` 질의 실패 가능성 | BIND ACL과 IPSet에서 `10.1.93.109` 누락 | 양쪽 DNS에 ACL/IPSet 추가 후 직접 질의·Failover 검증 | 해소 |
| R2 v1.7 DNS-EV-03 조건부 | Index와 중앙 Hash가 최종 정본 상태를 반영하지 못함 | v1.8 Script로 Index/Hash/ZIP 재생성 후 새 정본 승격 | 해소 |
| ZIP Hash 불일치 | Work의 신규 ZIP과 기존 Canonical ZIP이 서로 다른 세대 | 기존 정본 백업·Retire 후 신규 ZIP/Sidecar 원자적 승격 | 해소 |
| ZIP Sidecar 절대경로 | `sha256sum` 입력에 절대 경로 사용 | v1.9에 `cd` 후 ZIP Basename으로 Sidecar를 생성·검증하는 규칙 고정 | 해소 — ansible01 RC 0 |
| 터미널 강제 종료 | 대화형 SSH에서 상위 레벨 `exit` 실행 | v1.9에 Subshell + Return Code + Host/User/PWD Guard 고정 | 해소 — ansible01 RC 0 |

### 잔여 위험 및 통제

| 위험 | 영향 | 통제/인수 조건 | 소유 티켓 |
|---|---|---|---|
| 단일 Public Forwarder `8.8.8.8` 의존 | 외부 DNS Forwarding 장애 가능 | P1 승인값 유지, 내부 Zone은 독립 제공; P2에서 다중/내부 Forwarder 검토 | P2 DNS 개선 |
| CoreDNS 실제 Source 미확정 | 선제 ACL 확대 시 불필요한 공격면 증가 | P1-K8S-01에서 Source를 관측한다. 기존 Node IP면 변경 없이 검증하고, 신규 고정 IP면 최소 `/32`, Pod IP/CIDR이면 안정적 Egress 또는 ICR을 우선 검토한다. | P1-K8S-01 |
| 일부 Kubernetes Node Resolver 미전환 | 현재 control01만 검증되어 Node별 이름 해석이 불균일함 | 2026-09-04 control02/03, 2026-09-07 worker01~03 및 6개 Node 종합 검증 | CR-P1-ANS-01-01 |
| 기존 백업/Stage 오삭제 | Rollback 근거 손실 | Support Review는 완료됐으나 Cleanup은 별도 승인 전까지 보존한다. | 후속 Housekeeping |

### Baseline 버전 정합성

- R2 실행 Evidence의 생성 기준 표기는 Baseline v3.1.14다.
- 현재 프로젝트 정본은 Baseline v3.1.15다.
- v3.1.15의 DNS 관련 변경은 기존 `.109` 및 FQDN Interface Contract를 유지하는 성격이며, R2에서 검증한 DNS 서비스·TSIG·ACL·Failover 결과를 무효화하는 동작 변경은 없다.
- 따라서 기존 원본 Evidence를 수정하지 않고, 본 v1.3 디스크립션에서 현재 Baseline과 실행 당시 Evidence 기준을 함께 추적한다.

## 📝 Completion Record

| Field | 값 |
|---|---|
| Result | DNS 기능 PASS / 보안 통제 PASS / Failover PASS / R2 Evidence Integrity PASS |
| Status | Done |
| Exit Criteria | 기술·증적·Runbook·Support Review 조건 모두 충족 |
| Completed Date | 2026-09-03 |
| Reviewer / Approver | 이하영 / 이권욱 — Approved |

### 리뷰어 최종 체크리스트

- [x] 정본 ZIP SHA-256이 `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab`와 일치한다.
- [x] ZIP Sidecar는 상대 파일명 `P1-DNS-01-FRESH-20260902-R2.zip`을 가리킨다.
- [x] 정본 Directory의 내부 `SHA256SUMS` 검증이 전부 성공한다.
- [x] Raw TXT 11개, Sidecar 11개, Manifest 12개다.
- [x] DNS-EV-03은 `PASS`다.
- [x] `.109`는 dns01/dns02 ACL과 IPSet에 반영됐다.
- [x] TSIG Secret과 민감 MAC 정보가 정본 Evidence에 포함되지 않았다.
- [x] 중복 Failover Evidence는 서로 다른 Consumer(k8s-control01, k8s-api-lb01)의 독립 테스트로 식별된다.
- [x] 전체 6개 Node 전환 여부, 소유권, 적용 일정과 검증 기준이 기록됐다.
- [x] CoreDNS Source 전달 후 ACL 유지·최소 `/32` 추가·ICR 발행을 구분하는 기준이 기록됐다.
- [x] Runbook v1.9의 ansible01 설치·자체 검증·정본 읽기 전용 검증 Return Code 0이 기록됐다.
- [x] 이하영 Support Review 의견과 승인 일자가 기록됐다.
- [x] 이권욱 Lead가 `Done` 전환 및 Completion Date를 기록했다.

## 변경 이력

| Version | Date | 변경 내용 |
|---|---|---|
| v1.0 | 2026-09-01 | Primary/Secondary, TSIG, ACL, Forwarding, Failover 기본 구현 |
| v1.1 | 2026-09-02 | k8s-api-lb01 `.109` DNS Consumer 요구사항 추가 |
| v1.2 | 2026-09-02 | `/approved` 권한 실패, 원본/Sidecar/중앙 `SHA256SUMS` 증적 계약 보완 |
| v1.3 | 2026-09-03 | `.109` 반영, R2 v1.8 재생성·검증·정본 승격, DNS-EV-03 PASS, 최종 ZIP Hash 및 리뷰 종료 게이트 반영 |
| v1.3-R1 | 2026-09-03 | 이하영 Support Review 반영: 전체 6개 Node Resolver 전환의 P1-ANS-01 소유권·일정, P1-K8S-01 CoreDNS Source 관측 및 ACL/ICR 분기 기준 추가 |
| v1.3-R2 | 2026-09-03 | P1-ANS-01 Done 상태 확인 후 전체 Node Resolver 실행을 신규 CR-P1-ANS-01-01로 이관하고 P1-DNS-01의 후속 참조를 동기화 |
| v1.3-R3 | 2026-09-03 | Runbook Supplement v1.9의 Subshell/Return Code, Host·User·PWD Guard, 상대 ZIP Sidecar, 정본 읽기 전용 검증 규칙을 반영. 로컬 정적 검증 PASS, ansible01 실행 검증 대기 |
| v1.3-R4 | 2026-09-03 | ansible01에서 Runbook Supplement v1.9 설치 RC 0, Runbook 자체 검증 RC 0, R2 정본 읽기 전용 검증 RC 0 확인. DNS-AC-15 PASS 및 최종 직접 종료 게이트를 Support Review 승인으로 축소 |
| v1.3-R5 | 2026-09-03 | 이하영 Support Review 승인 완료, DNS-AC-16 PASS, 이권욱 Lead 확정, Status Done 및 Completed Date 반영 |
