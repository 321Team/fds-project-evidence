# FDS P1-ANS-01 기술 완료·종결 검토 Notion 입력본 v1.3

> 기준일: `2026-08-31`  
> 기준 Baseline: `FDS_Project_Implementation_Baseline_v3.1.10`  
> Network Baseline: `FDS_Network_Baseline_v2.3`  
> 대상: `P1-ANS-01`  
> 현재 상태: `PASS / APPROVED / DONE`  
> 기술 완료일: `2026-08-28`  
> 정식 종결일: `2026-08-31`  
> 용도: SSH 운영 인계 통제 보완, Notion 기술 완료 티켓 속성 입력 및 승인 증적 제출

---

## 1. 속성정보

| Property | 입력값 | 근거 / 비고 |
|---|---|---|
| Title / Item Name | P1-ANS-01 — Ansible Inventory / OS-Node Bootstrap | Baseline 명칭 유지 |
| Record ID | P1-ANS-01 | Upsert Key |
| Phase | Phase 1 | 최초 WBS |
| Category | Automation / Configuration Management | 최초 WBS |
| Type | Task | 최초 WBS |
| Status | Done | HO-ANS-08·09 PASS 및 Reviewer/Approver 승인 완료 |
| Priority | P0 | 최초 WBS |
| Start | 2026-08-27 | 최초 계획일 |
| End | 2026-09-01 | 최초 계획일 |
| Calendar Days | 6 | 최초 계획 기준 |
| Working Days | 4 | 최초 계획 기준 |
| Technical Completed Date | 2026-08-28 | 실제 기술 적용 완료일 |
| Closed Date | 2026-08-31 | 이하영 Review PASS / Approval APPROVED |
| Lead | 이권욱 | Automation 담당 |
| Support | 이하영, 이재환 | 최초 WBS |
| Security / Operations Reviewer | 이하영 | PASS — 2026-08-31 |
| Approver | 이하영 | APPROVED — 2026-08-31 |
| Exit Criteria | ansible01 `10.250.10.10`에서 CP 3대·Worker 3대 Inventory/SSH `PASS=6`, OS·Kubernetes 선행조건 적용, 재실행 `changed=0`, HO-ANS-08·09 PASS 및 승인 Evidence 확보 | 종결 기준 충족 |
| Related Decision IDs | D01; D13; D25; D28; D31 | Baseline 연결 유지 |
| Related Risk IDs | RISK-03; RISK-04; RISK-05; RISK-14 | Platform, Network, Schedule, Governance |
| Source | FDS_Project_Implementation_Baseline_v3.1.10; FDS_Network_Baseline_v2.3; FDS_Phase1_Logical_Architecture_v3.1.2; 본 티켓 실행·승인 Evidence | 권위·종결 근거 |
| Schedule Note | 2026-08-28 기술 적용 완료 후 2026-08-31 HO-ANS-08·09 PASS와 이하영 Reviewer PASS·Approver APPROVED를 기록했다. HO-ANS-01~04는 각 후속 Ticket Acceptance로 이관한다. | 기술 완료와 정식 종결 구분 |

### 입력 통제

- `Record ID=P1-ANS-01`로 Upsert하고 중복 Page를 생성하지 않는다.
- `Status=Done`, `Technical Completed Date=2026-08-28`, `Closed Date=2026-08-31`로 Upsert한다.
- `HO-ANS-08·09=PASS`, Review `PASS`, Approval `APPROVED`를 승인 Evidence와 함께 반영한다.
- `Start=2026-08-27`, `End=2026-09-01`은 최초 계획값으로 유지한다.
- 담당·지원 인명은 `이권욱`, `이하영`, `이재환` 풀네임으로 입력한다.
- Security / Operations Reviewer와 Approver는 이하영으로 지정한다.
- 동일 인물이 Reviewer와 Approver를 겸임하므로 승인 기록에 겸임 사실을 명시한다.
- Review Result와 Approval Result를 구분해 각각 `PASS`, `APPROVED`, 일자 `2026-08-31`로 기록한다.

---

## 2. Description

# 🎯 User Story

자동화 담당자 이권욱으로서 `ansible01`에서 Kubernetes 예정 노드 6대의 OS와 Node Bootstrap 설정을 일관되게 적용한다. 이를 통해 수동 설정 편차를 줄이고 동일한 구성을 반복 재현할 수 있게 한다.

---

# 📌 Scope

## In Scope

- `ansible01` `10.250.10.10`
- Control Plane 3대·Worker 3대 Inventory
- `svc_ansible`·SSH Key·sudo
- `common`·`k8s_prereq` Role
- Check/Diff·Canary·전체 적용·멱등성·Evidence
- VS Code Remote-SSH를 통한 `ansible01` 작업 환경

## Out of Scope

- VMware VM 생성
- 동결된 IP·Route 자동 변경
- `containerd`, `kubelet`, `kubeadm`, `kubectl` 설치
- `kubeadm init/join`과 Calico 완료 판정
- Kubernetes 보안 Manifest
- 애플리케이션 Delivery

---

# 🖥️ 배포 대상

| Inventory Group | Host | IP | 결과 |
|---|---|---|---|
| k8s_control_plane | k8s-control01 | 10.1.93.102 | PASS |
| k8s_control_plane | k8s-control02 | 10.1.93.103 | PASS |
| k8s_control_plane | k8s-control03 | 10.1.93.104 | PASS |
| k8s_workers | k8s-worker01 | 10.1.93.105 | PASS |
| k8s_workers | k8s-worker02 | 10.1.93.107 | PASS |
| k8s_workers | k8s-worker03 | 10.1.93.108 | PASS |

관리 경로는 `ansible01(10.250.10.10) → 10.250.10.1 → 각 Node`를 사용한다. 각 Node의 반환 경로는 `10.250.10.0/24 via 10.1.93.58`이며, 실제 SSH 로그에서 원본 Source `10.250.10.10`이 6대 모두 보존됨을 확인했다.

---

# 📦 구현 구성

| 구성 | 역할 |
|---|---|
| `ansible.cfg` | Project 기본 설정 및 Inventory 연결 |
| `inventory/hosts.yml` | CP 3대·Worker 3대, 접속 사용자·키·Python 정의 |
| `inventory/group_vars/all.yml` | 공통 변수와 Bootstrap Host Mapping 정의 |
| `playbooks/precheck.yml` | Host/OS, SELinux, 시간, Swap, Module, Sysctl, 반환 경로 검증 |
| `playbooks/site.yml` | `common`, `k8s_prereq` Role 적용 |
| `roles/common` | 공통 Package, chronyd, Timezone, `/etc/hosts`, SELinux 통제 |
| `roles/k8s_prereq` | Swap 비활성화, Kernel Module, Kubernetes Sysctl 구성 |
| `docs/evidence/P1-ANS-01/` | 실행·검증·무결성 증적 |

## 적용된 Baseline

- `chronyd` 활성·기동
- Timezone `Asia/Seoul`
- Ansible 관리 블록으로 Kubernetes 예정 Node 6대의 `/etc/hosts` Mapping 구성
- SELinux `Enforcing` 유지
- Active/Persistent Swap 비활성화
- `overlay`, `br_netfilter` Module의 현재·영속 상태 보장
- 다음 Sysctl의 현재·영속 값 `1` 보장
  - `net.bridge.bridge-nf-call-iptables`
  - `net.bridge.bridge-nf-call-ip6tables`
  - `net.ipv4.ip_forward`

IP, Prefix, Gateway, Return Route, NAT 및 VMnet 역할은 변경하지 않았다.

---

# 📋 핵심 요구사항

- [x] Inventory Group과 Host Variables를 실제 Node/IP와 일치시켰다.
- [x] Secret과 Private Key를 Source에 평문 저장하지 않았다.
- [x] 적용 전 Canary 대상에서 `--check --diff`를 수행했다.
- [x] Network Freeze 항목을 변경하지 않았다.
- [x] Canary 적용·사후검증 후 전체 6대로 확장했다.
- [x] 전체 2차 실행에서 `changed=0`을 확인했다.

---

# ✅ Acceptance Criteria

| Acceptance Criteria | 실제 결과 | 판정 |
|---|---|---|
| `ansible all -m ping` PASS=6, FAIL=0 | 6대 모두 `SUCCESS`, `pong`, 실패 0 | PASS |
| 접속 Source `10.250.10.10` | 6대 `sshd` 로그에서 `svc_ansible from 10.250.10.10` 확인 | PASS |
| Playbook `failed=0`, `unreachable=0` | 전체 Apply·Postcheck·멱등성 실행 모두 0 | PASS |
| 2차 실행 `changed=0` | 6대 모두 `changed=0` | PASS |
| Linux/Kubernetes 선행조건 | SELinux, Time, Swap, Module, Sysctl, Return Route 통과 | PASS |
| Evidence 확보 | 증적 파일과 SHA-256 Manifest 생성·검증 | PASS |

---

# 🧪 Test Result

| TC ID | 검증 항목 | 실제 결과 | 판정 |
|---|---|---|---|
| TC-P1ANS-01 | Network Route / TCP 22 | 6대 모두 Route 선택 정상, TCP 22 Connected | PASS |
| TC-P1ANS-02 | Inventory Graph | CP 3대·Worker 3대, 총 6대 일치 | PASS |
| TC-P1ANS-03 | Ansible Ping | `SUCCESS=6`, `FAIL=0` | PASS |
| TC-P1ANS-04 | Management Source Preservation | 6대 모두 `10.250.10.10` | PASS |
| TC-P1ANS-05 | Syntax / Check-Diff | 최종 Syntax 통과, Canary 예상 변경 검토 | PASS |
| TC-P1ANS-06 | Canary Apply / Postcheck | k8s-control01 `failed=0`, `unreachable=0`; 모든 선행조건 통과 | PASS |
| TC-P1ANS-07 | Canary Idempotency | `changed=0` | PASS |
| TC-P1ANS-08 | Full Apply | 6대 `failed=0`, `unreachable=0` | PASS |
| TC-P1ANS-09 | Full Postcheck | 6대 `ok=15`, `changed=0`, `failed=0`, `unreachable=0` | PASS |
| TC-P1ANS-10 | Full Idempotency | 6대 `ok=16`, `changed=0`, `failed=0`, `unreachable=0` | PASS |
| TC-P1ANS-11 | Final Ping | 6대 모두 `SUCCESS`, `changed=false` | PASS |
| TC-P1ANS-12 | Evidence Integrity | SHA-256 Manifest 전 항목 검증 성공 | PASS |

---

# 🚀 배포 결과

## Canary

- 대상: `k8s-control01`
- Check/Diff에서 `/etc/hosts`, `/etc/modules-load.d/k8s.conf`, `/etc/sysctl.d/99-kubernetes.conf` 예상 변경을 사전 확인했다.
- 적용 후 Host/OS, SELinux, Timezone, NTP, chronyd, Swap, Module, Sysctl, Management Return Route 검증을 모두 통과했다.
- Canary 재실행 결과 `changed=0`을 확인했다.

## Full Apply

- `k8s-control01`: Canary 적용 완료 상태이므로 `changed=0`
- 나머지 5대: 각 `changed=4`, `failed=0`, `unreachable=0`
- 나머지 5대의 변경 항목:
  1. Timezone `Asia/Seoul` 정규화
  2. Ansible 관리 `/etc/hosts` 블록
  3. `/etc/modules-load.d/k8s.conf`
  4. `/etc/sysctl.d/99-kubernetes.conf`

## Full Idempotency

| Host | ok | changed | unreachable | failed | skipped |
|---|---:|---:|---:|---:|---:|
| k8s-control01 | 16 | 0 | 0 | 0 | 4 |
| k8s-control02 | 16 | 0 | 0 | 0 | 4 |
| k8s-control03 | 16 | 0 | 0 | 0 | 4 |
| k8s-worker01 | 16 | 0 | 0 | 0 | 4 |
| k8s-worker02 | 16 | 0 | 0 | 0 | 4 |
| k8s-worker03 | 16 | 0 | 0 | 0 | 4 |

---

# 🧾 검증 및 증적

## Primary Closure Evidence

| 파일 | 용도 |
|---|---|
| `01_network_precheck.txt` | ansible01 Route 및 TCP 22 사전 확인 |
| `03_inventory_validation.txt` | Inventory List·Graph·Group 검증 |
| `04b_ansible_ping_success.txt` | 6대 Ansible Ping 성공 |
| `05a_precheck_syntax.txt` | Precheck Syntax 검증 |
| `05b_node_precheck.txt` | 전체 Node 선행조건 사전검증 |
| `05c_source_preservation.txt` | SSH Source `10.250.10.10` 보존 |
| `05d_sudo_become_validation.txt` | 6대 `svc_ansible` 로그인, 비대화형 sudo 및 become UID 0 검증 |
| `05e_ssh_host_key_config.txt` | Ansible `HOST_KEY_CHECKING=True` 및 환경 Override 부재 확인 |
| `05f_known_hosts_inventory.txt` | Known Hosts 권한·항목·Fingerprint·SHA-256 Inventory |
| `05f2_host_key_enforced_ping.txt` | Strict Host Key Checking 강제 상태의 6대 Ping 성공 |
| `05g_ssh_key_lifecycle_validation.txt` | Controller/Node Key 권한 및 동일 Fingerprint 검증 |
| `05g2_key_restriction_canary.txt` | 관리 Key 제한 Canary 적용 |
| `05g3_key_restriction_fresh_ssh.txt` | Canary 신규 SSH Session 및 sudo 검증 |
| `05g4a_key_restriction_full_check.txt` | 잔여 5대 Key 제한 Check Mode 검증 |
| `05g4_key_restriction_full.txt` | 잔여 5대 Key 제한 적용 |
| `05g5_key_restriction_full_fresh_ssh.txt` | 6대 신규 SSH Session 및 sudo 검증 |
| `05g5b_key_restriction_ansible_validation.txt` | 6대 Ansible Ping 및 become 재검증 |
| `05g6_key_restriction_idempotency.txt` | 6대 Key 제한 재실행 `changed=0` |
| `05h_ssh_key_lifecycle_record.md` | 관리 Key 책임자와 발급·보관·회전·폐기·복구 절차 |
| `05i_ansible_version_support.txt` | 배포판 제공 Ansible Core Version 및 Update 상태 확인 |
| `05j_reviewer_approver_record.md` | Reviewer / Approver 겸임 및 실제 결과·일자 기록 |
| `06b2_site_syntax_after_fix.txt` | 수정 후 Site Syntax 검증 |
| `06b6_check_diff_control01.txt` | Canary Check/Diff 성공 |
| `06c_canary_apply.txt` | Canary 적용 |
| `06d_canary_postcheck.txt` | Canary 사후검증 |
| `06e_canary_idempotency.txt` | Canary 멱등성 |
| `06f_full_apply.txt` | 전체 6대 적용 |
| `06g_full_postcheck.txt` | 전체 6대 사후검증 |
| `06h_full_idempotency.txt` | 전체 6대 2차 실행 `changed=0` |
| `07_final_ansible_ping.txt` | 최종 6대 Ping 성공 |
| `99_SHA256SUMS.txt` | 증적 무결성 Manifest |

## Troubleshooting / Audit Trail

다음 로그는 해결 과정을 보존하기 위한 감사 이력이며 최종 `PASS` 판정 근거로 사용하지 않는다.

- `04_ansible_ping.txt`: 초기 Inventory 미인식 이력
- `06a_site_syntax.txt`: 초기 Site 검증 이력
- `06b_site_check_diff.txt`: `bootstrap_host_records` 미정의 실패 이력
- `06b3_check_diff_readonly_command_failed.txt`: Check Mode의 Read-only Command Skip 이력
- `06b4_check_diff_control01.txt`: Canary Check/Diff 중간 수정 이력

## Evidence Location / Integrity

- Evidence Path: `docs/evidence/P1-ANS-01/`
- SHA-256 검증: `99_SHA256SUMS.txt`의 모든 대상 파일 `성공`
- SHA-256 `성공`은 파일 무결성을 뜻한다. 개별 테스트의 합격 여부는 Primary Closure Evidence의 실행 결과와 Recap으로 판정한다.
- 증적을 추가·수정하면 `99_SHA256SUMS.txt`를 재생성하고 다시 검증한다.

---

# 🛠️ 문제 해결 기록

| 문제 | 원인 | 조치 | 최종 상태 |
|---|---|---|---|
| Inventory가 비어 있음 | Project Inventory 설정 미연결 | `ansible.cfg`와 `inventory/hosts.yml` 연결 및 Group 검증 | 해결 |
| `bootstrap_host_records` undefined | 변수 탐색 경로가 실행 구조와 불일치 | `inventory/group_vars/all.yml` 정의 및 `site.yml`에서 공통 변수 명시 로드 | 해결 |
| Check Mode에서 SELinux Assertion 실패 | Read-only `command`가 Check Mode에서 Skip되어 Register 값 없음 | 조회 Task에 `check_mode: false` 적용 | 해결 |
| VS Code Remote-SSH 접속 준비 | Windows Host에서 ansible01 원격 개발환경 필요 | 전용 Host Alias·사용자 Key로 접속하고 Remote Server 기동 확인 | 해결 |

초기 실패는 수정 후 Syntax, Check/Diff, Canary, 전체 적용, 사후검증 및 멱등성으로 재검증했다.

---

# 🔐 보안 및 변경 통제

- Windows Host → `ansible01` 접속 Key와 `ansible01` → 관리 Node 접속 Key를 분리했다.
- 관리 Node는 `svc_ansible` 계정, SSH Public Key 및 sudo를 사용한다.
- Private Key와 Password는 Ansible Source와 Evidence에 평문 저장하지 않는다.
- 실제 관리 접속 Source는 6대 모두 `10.250.10.10`으로 보존됐다.
- SELinux는 모든 대상에서 `Enforcing`을 유지했다.
- 동결된 IP, Prefix, Gateway, Return Route, NAT, VMnet 역할은 변경하지 않았다.
- Kubernetes Package 및 Cluster 구성은 `P1-K8S-01`에서 수행한다.

## `/etc/hosts` 관리 경계

- Ansible 관리 블록은 Kubernetes 예정 Node 6대의 Hostname/FQDN Mapping에만 사용한다.
- 실제 적용 블록은 `k8s-control01~03`, `k8s-worker01~03`의 Node Mapping으로 한정돼 있다.
- Kubernetes Service 이름, Pod/Service 주소, `*.svc` 이름, CoreDNS Cluster Domain 및 Application Service DNS를 정적 등록하지 않는다.
- Service Discovery와 CoreDNS Record는 `P1-K8S-01`, 외부·사내 DNS Record는 `P1-DNS-01`의 책임 범위로 유지한다.

---

# 🔎 운영·지원 검토 반영

## 검토 결론

P1-ANS-01의 실제 변경 범위는 Kubernetes, 보안, 애플리케이션 및 모니터링 기능과 직접 충돌하지 않는다. 다만 이 판단은 `P1-K8S-01`에서 Container Runtime/CNI/SELinux/필수 포트 Preflight를 별도로 수행하는 조건부 판단이다.

## Handoff 및 Open Control

| ID | 조건 / 통제 | 책임 Ticket | 현재 상태 | 완료 증적 |
|---|---|---|---|---|
| HO-ANS-01 | Container Runtime과 kubelet의 cgroup driver 일치 확인 | P1-K8S-01 | TRANSFERRED / OPEN | Runtime 설정, kubelet 설정 및 Preflight 결과 |
| HO-ANS-02A | SELinux `Enforcing`에서 Container Runtime·kubelet·Calico 호환성 검증 | P1-K8S-01 | TRANSFERRED / OPEN | Enforcing 상태, Service Log, Pod/CNI 검증 |
| HO-ANS-02B | SecurityContext·PSA Restricted의 실제 Cluster 호환성 검증 | P1-SEC-01 | TRANSFERRED / OPEN | Admission, Pod 기동, Denied/Allowed Evidence |
| HO-ANS-03 | 6대의 Hostname, MAC Address, `product_uuid` 고유성 검증 | P1-K8S-01 | TRANSFERRED / PARTIAL — Hostname만 확인 | 6대 식별자 Matrix 및 중복 0건 결과 |
| HO-ANS-04A | Kubernetes/Calico 필수 포트와 Node 간 경로 검증 | P1-K8S-01 | TRANSFERRED / OPEN | Port Matrix, Listener, Firewall 및 Node 간 통신 결과 |
| HO-ANS-04B | API LB `.109:6443 → .102~.104:6443` Stage A/B 검증 | P1-LB-01 | TRANSFERRED / OPEN | Listener, Backend Health, API, 단일 Backend 장애 결과 |
| HO-ANS-04C | `.50/32 → Worker:30080` 허용 및 기타 Source 차단 | P1-SEC-01 | TRANSFERRED / OPEN | Host Firewall·NetworkPolicy Positive/Negative Test |
| HO-ANS-APP | transaction-api Service `80→8000`, `/readyz`, `/livez` 계약 | P1-APP-01 | TRANSFERRED / OPEN | Service/Endpoint/Probe Contract Test |
| HO-ANS-05 | `/etc/hosts` 관리 블록을 Node Mapping으로 제한 | P1-ANS-01 | PASS | `06f_full_apply.txt`, 최종 관리 블록 |
| HO-ANS-06 | `svc_ansible` sudo/become 동작 확인 | P1-ANS-01 | PASS — 6대 로그인 사용자 `svc_ansible`, 비대화형 sudo 및 become UID `0` | `05d_sudo_become_validation.txt`, `05b_node_precheck.txt`, `06d_canary_postcheck.txt`, `06g_full_postcheck.txt` |
| HO-ANS-07 | SSH Host Key Checking 설정 및 Known Hosts 통제 증적 | P1-ANS-01 / 운영 인계 | PASS — `HOST_KEY_CHECKING=True`, 환경 Override 없음, 6대 Known Hosts 및 강제 Ping 검증 | `05e_ssh_host_key_config.txt`, `05f_known_hosts_inventory.txt`, `05f2_host_key_enforced_ping.txt` |
| HO-ANS-08 | 관리 SSH Key의 발급·보관·회전·폐기 책임자와 절차 지정 | P1-ANS-01 / 운영 인계 | PASS — Owner 이권욱, Reviewer/Approver 이하영 | `05g_ssh_key_lifecycle_validation.txt`, `05g2~05g6`, `05h_ssh_key_lifecycle_record.md` |
| HO-ANS-09 | Reviewer / Approver 승인 기록 | P1-ANS-01 | PASS — Review PASS / Approval APPROVED / 2026-08-31 | `05j_reviewer_approver_record.md` |

### 운영·보안 통제 검증 요약

- `svc_ansible`은 6대 모두 비대화형 `NOPASSWD` sudo와 Ansible become으로 UID `0` 실행이 확인됐다.
- Ansible은 `HOST_KEY_CHECKING=True`이며 Inventory에서 `StrictHostKeyChecking=yes`, 전용 `known_hosts`, `IdentitiesOnly=yes`를 강제한다.
- `known_hosts`는 mode `600`이며 6대 Host Key와 Server ED25519 Fingerprint를 Inventory로 보존했다. 파일 SHA-256은 `f19d029172b6b539fbd9324189358961ca99fe5c07bf055dcfe2e2935bf05003`이다.
- 관리 Key Fingerprint는 `SHA256:VPGV/RGA8TrwO/3FC4YPxGzRNhBWuB+9hCzPV5plkws`로 Controller와 6대 `authorized_keys`가 일치한다.
- 관리 Key는 `from="10.250.10.10",restrict` 조건으로 제한했으며 6대 신규 SSH Session, sudo, Ansible Ping 및 become을 재검증했다.
- Key 제한 Playbook의 전체 재실행 결과는 6대 모두 `changed=0`, `unreachable=0`, `failed=0`이다.
- 설치된 `ansible-core-2.16.19-2.el10`은 현재 활성화된 CentOS Stream 10 AppStream 기준 Update 대상이 없으므로 배포판 채널 기준 PASS로 기록한다. Upstream 2.16 계열 유지보수 상태는 운영 Upgrade 검토 항목으로 남긴다.

### 2026-08-31 검토 의견 반영

- 이하영 Reviewer 의견의 cgroup driver, SELinux/Runtime/Calico, Node 식별자, Kubernetes/Calico Port는 `P1-K8S-01`; SecurityContext/PSA와 제한 NodePort Source는 `P1-SEC-01`; API LB는 `P1-LB-01`; Service/Probe 계약은 `P1-APP-01`로 이관한다.
- SSH 관리 Key 책임자와 절차는 `05h_ssh_key_lifecycle_record.md`에 Operational Owner `이권욱`, Reviewer/Approver `이하영`으로 문서화했다.
- 이재환 Support 의견의 P1-SEC-01 SecurityContext·PSA Restricted와 실제 Cluster 호환성 검증은 `HO-ANS-02`의 P1-K8S-01 실클러스터 검증 조건에 포함한다.
- 이하영 Reviewer `PASS`, Approver `APPROVED`, 일자 `2026-08-31`을 `05j_reviewer_approver_record.md`에 기록했다.

## Reviewer / Approver Record

| 항목 | 입력값 |
|---|---|
| Security / Operations Reviewer | 이하영 |
| Review Result | `PASS` |
| Review Date | `2026-08-31` |
| Approver | 이하영 |
| Approval Result | `APPROVED` |
| Approval Date | `2026-08-31` |
| Dual Role | `YES` — 동일인이 Reviewer와 Approver를 겸임 |
| Approval Comment / Reference | `HO-ANS-08·09 PASS 및 P1-ANS-01 종결 승인. 후속 Handoff는 각 책임 Ticket에서 미완료 상태로 검증.` |

Reviewer와 Approver의 겸임을 명시했으며 Review `PASS`, Approval `APPROVED`를 별도 결과로 기록했다. `HO-ANS-09=PASS`, Ticket `Status=Done` 전환을 승인한다.

## P1-K8S-01 Go/No-Go 경계

- `P1-ANS-01`은 `Done / Closed Date 2026-08-31`이다.
- `P1-K8S-01`은 P1-ANS Inventory·SSH·OS Prerequisite Evidence를 재사용한다.
- Container Runtime/CNI 설치 및 Cluster Apply의 Go 판단은 이관된 `HO-ANS-01·02A·03·04A` 검증 결과로 수행한다.
- `HO-ANS-02B·04C`, `HO-ANS-04B`, Service/Probe 계약은 각각 P1-SEC-01, P1-LB-01, P1-APP-01에서 완료 판정한다.

---

# 🔗 Dependency / Handoff

- **Blocked By:** `D-NET-01`, `P1-LNX-01`, `P1-NET-01` — `DONE / CLOSED`
- **Ticket Result:** `P1-ANS-01 = PASS / APPROVED / DONE`
- **Dependency Released:** `P1-K8S-01` Preflight 착수 가능
- **Conditional Gate:** Container Runtime/CNI/Cluster Apply 전 `HO-ANS-01~04` 검증
- **Milestone Contribution:** `MS-G1-01`의 Ansible Inventory/SSH/OS-Node Bootstrap 항목 `DONE`
- **Related Ticket:** `P1-DNS-01`
- **Handoff Boundary:** `P1-K8S-01`은 본 Inventory, SSH, OS Prerequisite 및 Evidence를 재사용하되 cgroup driver, SELinux 호환성, Node 식별자 고유성, Kubernetes/Calico 필수 포트를 별도 Preflight한 후 `containerd/kubeadm/Calico/CoreDNS` 구축을 수행한다.

---

# ⚖️ Decision / Risk Control

- **Related Decision IDs:** `D01`, `D13`, `D25`, `D31`
- **Decision Control:** 승인된 Baseline, 동결 Network Parameter 및 복원 Ticket 추적성을 유지했다.
- **Related Risk IDs:** `RISK-03`, `RISK-04`, `RISK-05`, `RISK-14`
- **Risk Control:** CentOS/Kubernetes 선행조건을 사전·사후 검증하고, 비관리 Network 조건은 Route/TCP/Source Evidence로 판정했으며, 전체 증적과 소유자를 Ticket에 연결했다.

---

# 📝 Technical Completion Record

- **Result:** `PASS / APPROVED`
- **Status:** `DONE`
- **Ticket Gate:** `CLOSED / HANDOFF TRANSFERRED`
- **Lead:** 이권욱
- **Support:** 이하영, 이재환
- **Original Plan:** `2026-08-27` ~ `2026-09-01` / Calendar 6일 / Working 4일
- **Technical Completed Date:** `2026-08-28`
- **Closed Date:** `2026-08-31`
- **Inventory / SSH:** CP 3대 + Worker 3대, `PASS=6`, `FAIL=0`
- **Playbook:** 전체 `failed=0`, `unreachable=0`
- **Idempotency:** 전체 6대 2차 실행 `changed=0`
- **OS / Node Prerequisite:** SELinux, Time, NTP, chronyd, Swap, Module, Sysctl, Return Route `PASS`
- **Evidence:** `docs/evidence/P1-ANS-01/`, SHA-256 검증 성공
- **Support Review:** 이재환 — 조건부 Handoff 의견 반영
- **Security / Operations Reviewer:** 이하영 — PASS / 2026-08-31
- **Approver:** 이하영 — APPROVED / 2026-08-31
- **Reviewer / Approver 겸임:** 예 — 동일인 겸임 사실을 승인 기록에 명시
- **Closed Control:** `HO-ANS-05~09 PASS`
- **Transferred Control:** `HO-ANS-01·02A·03·04A → P1-K8S-01`; `HO-ANS-02B·04C → P1-SEC-01`; `HO-ANS-04B → P1-LB-01`; Service/Probe 계약 → P1-APP-01
- **Closure Boundary:** 기술 완료 범위는 Ansible Inventory/SSH와 OS·Kubernetes Node 선행조건까지다. Kubernetes Package·Cluster·CNI 완료 판정은 `P1-K8S-01` 범위다.
- **Next:** 승인본 `05h`, `05j`를 실제 Evidence 경로에 반영하고 `99_SHA256SUMS.txt` 재생성·검증; 각 후속 Ticket에서 이관 통제 검증

---

## 3. Notion 제출 체크리스트

- [ ] `Record ID=P1-ANS-01` Page에 Upsert
- [x] `Status=Done`, `Technical Completed Date=2026-08-28`, `Closed Date=2026-08-31` 반영
- [ ] Lead `이권욱`, Support `이하영`, `이재환` 풀네임 확인
- [ ] 본 Description 반영
- [ ] Primary Closure Evidence 첨부 또는 Repository Link 연결
- [ ] `99_SHA256SUMS.txt` 검증 결과 대조
- [ ] Troubleshooting 로그를 Primary Evidence와 구분
- [x] SSH Host Key Checking 및 Known Hosts 통제 증적 첨부
- [x] 관리 SSH Key 권한·Fingerprint·Source 제한·신규 접속·멱등성 검증
- [x] `05h_ssh_key_lifecycle_record.md`에 발급·보관·회전·폐기·복구 책임자와 절차 작성
- [ ] 승인본 `05h`, `05j`를 실제 Evidence 경로에 반영하고 `99_SHA256SUMS.txt` 재생성·검증
- [x] 이하영 Reviewer 검토 결과·일자와 Approver 승인 결과·일자 입력
- [x] Reviewer / Approver 동일인 겸임 사실 및 승인 의견 명시
- [x] HO-ANS-01~04를 P1-K8S/P1-SEC/P1-LB/P1-APP Acceptance로 이관
- [x] `MS-G1-01`의 Ansible 항목을 `Done`으로 반영
- [x] `Status=Done`과 실제 `Closed Date` 반영

## 4. 최종 판정

`P1-ANS-01`은 기술 Scope, Acceptance, HO-ANS-08·09 및 Reviewer/Approver 승인 기준을 충족해 `DONE / CLOSED 2026-08-31`로 판정한다. 실제 Ansible Repository에 승인본 `05h`, `05j`를 배치하고 `99_SHA256SUMS.txt`를 재생성·검증하는 작업은 배포 후속 조치다. Kubernetes 관련 `HO-ANS-01~04`는 완료로 추정하지 않고 P1-K8S-01, P1-SEC-01, P1-LB-01, P1-APP-01에서 각 Acceptance와 Evidence로 검증한다.
