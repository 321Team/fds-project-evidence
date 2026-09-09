# D-NET-01 Closure Report v1.0

> 확정일: 2026-08-26  
> 상태: DONE / APPROVED  
> 적용 기준: FDS Network Baseline v2.3

## 1. 작업 목적

8대 Windows/VMware 환경의 Physical 및 Management 네트워크를 확정하고, 변경할 수 없는 현장 Gateway 조건에서 Management Source를 보존하는 운영 가능한 경로를 구현한다.

## 2. 확정 사양

| 영역 | 확정값 |
|---|---|
| Physical LAN | `10.1.93.0/24` |
| Physical Gateway | `10.1.93.254` — 프로젝트 비관리/변경 불가 |
| Bootstrap DNS | `8.8.8.8` |
| VMnet0 | Bridged, 실제 Windows `이더넷`에 명시 연결 |
| VMnet1 | Host-only `10.250.10.0/24`, DHCP Off |
| server01 VMnet1 Host | `10.250.10.254/24`, Default Route 없음 |
| VMnet8 | NAT `192.168.10.0/24`, FDS VM NIC 연결 금지 |
| mgmt-gw01 Physical | `ens160`, `10.1.93.58/24` |
| mgmt-gw01 Management | `ens224`, `10.250.10.1/24` |
| Management VM | ansible `.10`, runner `.20`, monitor `.30` |
| Physical Return Route | `10.250.10.0/24 via 10.1.93.58` |
| Internal NAT | 금지 |
| External NAT | 내부망 이외 목적지에 한한 조건부 Masquerade |

## 3. IPAM 확정

| 분류 | 주소 |
|---|---|
| P0/P1/Phase 2 승인 풀 | `.50~.55`, `.58`, `.102~.105`, `.107~.109` |
| Reserved | `.56`, `.57`, `.59` |
| DO_NOT_USE | `.100`, `.101`, `.106` |

`.100/.101/.106`은 현장 응답 장비가 존재하므로 FDS VM에 할당하지 않는다.

## 4. 검증 결과

| 검증 | 결과 |
|---|---|
| Windows server01~08 PostBuild | 전부 `FAIL=0` |
| K8s 예정 노드 6대 Linux 필수조건 | PASS |
| K8s 예정 노드 6대 Network Verify | 전부 `FAIL=0` |
| Physical 6대 Return Route | `.58` 경유 PASS |
| Source Preservation | `PASS=6`, `FAIL=0` |
| ansible01 Network Verify | `FAIL=0` |
| cicd-runner01 Network Verify | `FAIL=0` |
| monitor01 Network Verify | `FAIL=0` |
| mgmt-gw01 Verify | `FAIL=0` |

Source 보존 승인값:

```text
Route           : Physical destination via 10.250.10.1
Expected Source : 10.250.10.10
Remote Observed : 10.250.10.10
Result          : PASS
```

## 5. 수용된 경고와 예외

| 항목 | 처리 |
|---|---|
| `vmnet0_mapping` | Virtual Network Editor 수동 화면 증적 |
| `vmware_editor_proof` | VMnet1/8 Mode, CIDR, DHCP 및 FDS NIC 미사용 증적 |
| `.100/.101/.106` 응답 | `DO_NOT_USE`, FDS 미할당 예외 등록 |
| Gateway ICMP 미응답 가능성 | 프로젝트 비관리 장비이므로 Route/ARP/TCP 증적 병행 |

## 6. 범위 이관

| 항목 | 후속 과제 |
|---|---|
| containerd, kubelet, kubeadm, API Server, Calico | `P1-K8S-01` |
| BIND Primary/Secondary, `fds.internal` Forward Zone | `P1-DNS-01` |
| Reverse/PTR | `N/A — Out of Scope` |
| vpn-gw01, OCI Relay, AWS S2S | Phase 2 |

Kubernetes 미구축으로 발생하는 `containerd`, `kubelet`, `TCP 6443` G1 Role Check는 D-NET-01 결함이 아니다.

## 7. Evidence 인덱스

```text
01_Windows_PostBuild_server01-08
02_VMware_Virtual_Network_Editor
03_Linux_Node_Network_Verify
04_K8s_Linux_Prerequisites
05_Physical_Return_Route
06_Source_Preservation_PASS6
07_Management_VM_Verify
08_mgmt-gw01_Verify
09_DO_NOT_USE_IP_Exception
10_D-NET-01_Closure
```

## 8. 최종 판정

```text
Ticket     : D-NET-01
Result     : PASS
Status     : DONE
Gate       : CLOSED
Next       : P1-K8S-01 / P1-DNS-01
```
