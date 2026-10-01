# P1-K8S-01 Calico MTU 설정·실측값 증적 — 2026-10-01

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 "MTU 후보 1450 실측 확정"에 대응하는 읽기 전용 조회 결과다. **MTU 값 3곳을 관측했고, ICMP DF ping은 시험하지 못했으나 ICMP를 쓰지 않는 TCP 큰 데이터 교차 노드 시험은 통과했다.** 아래 "한계"를 반드시 함께 본다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | `k8s-control02` `server03` 홈 `~/mtu-check.txt` |
| 수집 | 2026-10-01T12:10:31+09:00 (파일 2행 `date -Is`) |
| 수집 명령 | 아래 "수집 명령" 블록(읽기 전용 `kubectl get/exec cat`, `ip link`, `ping`) |
| 실행자 | 이하영(K8S/SEC Lead) |
| 전달 경로 | control02 콘솔 출력 붙여넣기 → Claude Code 세션에서 파일 재구성 |
| 자료 구분 | **CONSOLE_SUBMITTED / RECONSTRUCTED_COPY** (서버 `.txt`/`.sha256` 파일을 직접 수신하지 않음) |
| 편입 작성 | Claude Code 세션 (AI 보조) — 독립 검토 필요 |
| 추가 수집 | `mtu-tcp-check.txt` (control02 `server03` 홈 `~/mtu-tcp-check.txt`, 2026-10-01T15:23:51+09:00, 아래 "TCP 큰 데이터 시험") |

## 무결성

**자료 구분: `CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`.** 서버의 `mtu-check.txt`와 `.sha256` 파일을 직접 수신하지 않았다. 따라서 **서버 원본 파일의 해시 검증을 주장하지 않는다.**

확인한 범위는 다음으로 한정한다.

- 실행자가 control02 콘솔에서 `sha256sum ~/mtu-check.txt`를 실행해 화면에 보고한 SHA256과, 콘솔 출력에서 재구성한 이 폴더의 `mtu-check.txt`의 SHA256이 일치한다.
- `[sudo]` 암호 프롬프트는 파일에 포함되지 않은 것으로 재구성했고 이 재구성이 보고 해시와 일치한다.

```
7d1b9bcbed2a5ffcc2d67370ed30a812201cbc85f5b9bc622b8e54ffbebb43de  mtu-check.txt   (서버 화면 보고값 = 재구성본)
92ff04600fdb2590e00b425237bc3110940b16ca37db13ec8ecfb2f398aa2f3d  mtu-tcp-check.txt   (서버 화면 보고값 = 재구성본)
```

```bash
sha256sum --check SHA256SUMS
```

`SHA256SUMS`는 이 폴더에 편입된 파일의 무결성 목록이며 서버 원본의 증명이 아니다. 서버 원본 `.txt`와 `.sha256`을 파일로 수신하면 새 수집회차로 보완할 수 있다. 암호·토큰 값은 파일에 없다.

## 수집 명령

```bash
{
echo "# MTU check"; date -Is; hostname
kubectl -n kube-system get cm calico-config -o jsonpath='{.data.veth_mtu}'
kubectl get ippool -o jsonpath='...'
ip -o link show | grep -E "vxlan.calico|ens160"
kubectl -n icr39-probe exec probe-w01 -- cat /sys/class/net/eth0/mtu
kubectl -n icr39-probe exec probe-w02 -- cat /sys/class/net/eth0/mtu
kubectl get globalnetworkpolicies.crd.projectcalico.org -o yaml | grep -ciE "icmp"
ping -c 2 -W 1 <Pod IP 10.244.69.210>; ping -c 2 -W 1 <노드 IP 10.1.93.107>
} 2>&1 | tee ~/mtu-check.txt
```

(kubectl은 `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf`로 실행)

## 확인한 사실

| 항목 | 값 |
|---|---|
| calico-config `veth_mtu` | **1450** |
| IPPool | `default-ipv4-ippool` 10.244.0.0/16, `ipip=Never`, `vxlan=CrossSubnet` |
| control02 `ens160` | mtu 1500 |
| control02 `vxlan.calico` | mtu **1450** (1500 − VXLAN 오버헤드 50과 일치) |
| `probe-w01` Pod eth0 | **1450** |
| `probe-w02` Pod eth0 | **1450** |

설정값, 터널 인터페이스, 서로 다른 두 Worker의 Pod 인터페이스가 모두 1450으로 일치한다.

## TCP 큰 데이터 시험 (ICMP 미사용)

DF ping은 ICMP가 막혀 시험할 수 없어서(아래 한계 1), 허용된 TCP로 큰 데이터를 교차 노드로 보내는 시험을 추가했다. 정책은 변경하지 않았다.

| 항목 | 내용 |
|---|---|
| 클라이언트 | `icr39-probe/probe-w01` (worker01, `calico/node` 이미지의 bash `/dev/tcp`) |
| 서버 | CoreDNS Pod `10.244.246.119` (k8s-control01) TCP 9153 `/metrics` — 기존 서비스, 읽기 요청만 |
| 요청 | 기준: `GET /x`(작은 요청). 시험: `GET /metrics` + 20,000자 `X-Pad` 헤더 |
| 결과 | 기준 응답 175자, 시험 응답 **25,951자**, 패딩 20,000자 확인(`pad_chars=20000`) |

- 요청 방향 20KB 이상과 응답 방향 약 26KB가 노드를 건너 정상 수신됐다. Pod MTU 1450 기준 TCP MSS는 약 1410이므로 양방향 모두 가득 찬 크기의 세그먼트가 여러 개 필요한 양이다.
- 도구 제약(`wc`·`head`·`tr` 없음)으로 응답 길이는 bash 변수 문자 수이며 정확한 바이트 수가 아니다(ASCII라 근사). 마지막 개행은 제거된다.
- **실제 패킷 크기·MSS는 캡처하거나 읽지 않았다.** 큰 세그먼트가 가득 찬 크기로 전송됐다는 것은 양이 필요로 하는 추정이다.
- 출발·도착 노드(worker01 → control01)는 같은 서브넷이다. `vxlan=CrossSubnet`이므로 이 경로가 VXLAN으로 캡슐화됐는지는 구분하지 않았다. 경로가 캡슐화 여부와 무관하게 큰 TCP 데이터를 통과시킨다는 것까지만 확인한다.
- 이 시험은 DF/PMTU 방식의 직접 시험이 아니다. 동등성 판단은 검토자에게 맡긴다.

## 한계

1. **ICMP DF 큰 패킷 ping 시험을 하지 못했다.** control02에서 Pod IP(10.244.69.210)와 worker02 노드 IP(10.1.93.107)로 작은 ping(56바이트)이 모두 100% 손실이다. 작은 패킷도 도달하지 않으므로 이 ping은 MTU 증거가 되지 않는다. 대체로 위 "TCP 큰 데이터 시험"을 수행했다.
2. 차단 원인은 확정하지 않았다. 현재 GlobalNetworkPolicy 전체에 `icmp` 문자열이 0건이므로 HEP/GNP에 ICMP 허용 규칙이 없는 것과 일치하나, 실제 패킷의 차단 지점은 증명하지 않았다. 담당자는 HEP/GNP 적용 영향으로 추정한다.
3. 시험을 위해 정책을 일시 변경하지 않았다.
4. MTU 값은 control02와 Worker 2대의 Pod에서만 조회했다. 다른 노드의 `vxlan.calico` 값은 이 파일에 없다(같은 calico-config가 모든 노드에 적용).
5. CrossSubnet 노드 간 TCP 통신은 별도 증적(`../icr39-verification-20260927/`)에 있다. 이 폴더의 값과 큰 패킷 경로의 연결은 확인되지 않았다.
6. FelixConfiguration `default`에는 mtu 관련 설정이 없다(별도 조회, 이 파일 밖). MTU는 `calico-config`의 `veth_mtu`로 지정된다.

## 판정 경계

- `MTU_CONFIG_AND_INTERFACE_VALUES = OBSERVED` (콘솔 제출 자료 기준)
- `MTU_TCP_LARGE_TRANSFER_CROSS_NODE = OBSERVED_PASS` (비ICMP 시험, 요청 20KB+·응답 약 26KB 통과)
- `MTU_DF_PMTU_ICMP_TEST = NOT_PERFORMED` (ICMP가 허용되지 않아 시험 불가)
- DF/PMTU 직접 시험과의 동등성, AC 충족 여부는 검토자·Lead가 판단한다. 이 문서는 충족을 주장하지 않는다.

## 검토 상태

AI 세션의 자체 대조(화면 보고 해시와 재구성본 해시 일치, 민감정보 확인)이며 `governance/EVIDENCE_POLICY.md`의 독립 검토는 아직 없다. 이 편입은 AC 인수나 티켓 종결을 뜻하지 않는다.
