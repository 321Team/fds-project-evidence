# P1-K8S-01 Calico MTU 설정·실측값 증적 — 2026-10-01

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 "MTU 후보 1450 실측 확정"에 대응하는 읽기 전용 조회 결과다. **MTU 값은 확인했으나 큰 패킷 통과(DF ping)는 시험하지 못했다.** 아래 "한계"를 반드시 함께 본다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | `k8s-control02` `server03` 홈 `~/mtu-check.txt` |
| 수집 | 2026-10-01T12:10:31+09:00 (파일 2행 `date -Is`) |
| 수집 명령 | 아래 "수집 명령" 블록(읽기 전용 `kubectl get/exec cat`, `ip link`, `ping`) |
| 실행자 | 이하영(K8S/SEC Lead) |
| 전달 경로 | control02 콘솔 출력 붙여넣기 → Claude Code 세션에서 파일 재구성 |
| 편입 작성 | Claude Code 세션 (AI 보조) — 독립 검토 필요 |

## 무결성

control02에서 실행한 `sha256sum ~/mtu-check.txt`와 편입본의 해시가 일치한다. 콘솔 붙여넣기로 옮겼으나 바이트 단위로 원본과 같다(`[sudo]` 암호 프롬프트는 tty로 출력되어 파일에 없다. 재구성 결과가 서버 해시와 일치하여 확인).

```
7d1b9bcbed2a5ffcc2d67370ed30a812201cbc85f5b9bc622b8e54ffbebb43de  mtu-check.txt
```

```bash
sha256sum --check SHA256SUMS
```

암호·토큰 값은 파일에 없다.

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

## 한계 (큰 패킷 통과 미시험)

1. **DF 큰 패킷 ping 시험을 하지 못했다.** control02에서 Pod IP(10.244.69.210)와 worker02 노드 IP(10.1.93.107)로 작은 ping(56바이트)이 모두 100% 손실이다. 작은 패킷도 도달하지 않으므로 큰 패킷 시험은 MTU 증거가 되지 않는다.
2. 차단 원인은 확정하지 않았다. 현재 GlobalNetworkPolicy 전체에 `icmp` 문자열이 0건이므로 HEP/GNP에 ICMP 허용 규칙이 없는 것과 일치하나, 실제 패킷의 차단 지점은 증명하지 않았다. 담당자는 HEP/GNP 적용 영향으로 추정한다.
3. 시험을 위해 정책을 일시 변경하지 않았다.
4. MTU 값은 control02와 Worker 2대의 Pod에서만 조회했다. 다른 노드의 `vxlan.calico` 값은 이 파일에 없다(같은 calico-config가 모든 노드에 적용).
5. CrossSubnet 노드 간 TCP 통신은 별도 증적(`../icr39-verification-20260927/`)에 있다. 이 폴더의 값과 큰 패킷 경로의 연결은 확인되지 않았다.
6. FelixConfiguration `default`에는 mtu 관련 설정이 없다(별도 조회, 이 파일 밖). MTU는 `calico-config`의 `veth_mtu`로 지정된다.

## 검토 상태

AI 세션의 자체 대조(해시 일치, 민감정보 확인)이며 `governance/EVIDENCE_POLICY.md`의 독립 검토는 아직 없다. 이 편입은 AC 인수나 티켓 종결을 뜻하지 않는다.
