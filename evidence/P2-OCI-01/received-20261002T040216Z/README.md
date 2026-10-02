# P2-OCI-01 — OCI Relay local IPsec prerequisite / reboot persistence Runtime (2026-10-02)

Record ID: **P2-OCI-01**

이 수집회차는 OCI Relay `fds-p2-oci-relay01`에서 수행한 local IPsec prerequisite와 reboot persistence 확인 결과의 원본 로그를 보존한다.
실제 peer tunnel, NAT-T 경로, VCN/AWS/On-Prem route, failure/recovery 시험은 아직 수행하지 않았으며 D21 Go/No-Go는 PENDING이다.

## Source / receipt provenance

| 항목 | 값 |
|---|---|
| Source host | `fds-p2-oci-relay01` |
| Source file | `/home/opc/p2-oci-relay-local-runtime-20261002T035954Z.log` |
| Source capture time | `2026-10-02T03:59:54+00:00` |
| Source capture RC | `0` |
| Source SHA256 | `bb8bcf469c87d1a026b91dc40d02745918f62a54a7b7b5126c56b314d7ebbb46` |
| Source size | `2184 bytes` |
| First receiver | OCI Cloud Shell `/home/catchmeupn/p2-oci-relay-local-runtime-20261002T035954Z.log` |
| Cloud Shell receipt time proxy | `2026-10-02 04:02:16.612629115 +0000` |
| Cloud Shell SHA256 | source와 exact match |
| Windows SHA256 / size | source와 exact match / `2184 bytes` |
| Chat upload SHA256 / size | source와 exact match / `2184 bytes` |

원본 로그는 재작성·요약본으로 대체하지 않고 수신 바이트를 그대로 편입한다.

## Reboot persistence traceability

현재 raw 로그는 **재부팅 후 snapshot**이다. `REBOOT_PERSISTENCE=PASS` 판정은 raw 파일 단독이 아니라 아래 P2-OCI-01 실행 연쇄와 함께 판단한다.

- pre-reboot local prerequisite clean PASS: https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5945082639
- actual reboot + post-reboot persistence PASS: https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5945352648
- source-host Runtime evidence capture: https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5945370129
- receiver SHA256 exact-match receipt: https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5945393705

## Captured Runtime result

- SELinux: `Enforcing`
- firewalld: `active` / `enabled`
- ipsec.service: `active` / `enabled`
- `net.ipv4.ip_forward=1`
- `rp_filter`: all/default/enp0s5/ip_vti0/lo 모두 `0`
- IPv4 ICMP redirects: accept/send `0`
- `/etc/sysctl.d/99-fds-p2-oci-relay.conf` SHA256: `f29553ffb2d3710edd50a769ff8d787e91403bbb7d582a656e6ecdab7636cc76`
- Libreswan `4.15` / kernel XFRM / `ipsec.conf` syntax / Pluto: `OK`
- Pluto IKE UDP/500, NAT-T UDP/4500 listener: `OK`
- capture: `CAPTURE_RC=0`

## Scope boundary

이 증적은 **OCI Relay 로컬 OS/Libreswan prerequisite 및 reboot persistence Runtime** 범위만 지원한다.
다음을 주장하지 않는다.

- 실제 peer IPsec tunnel UP
- OCI↔AWS 또는 OCI↔On-Prem packet path 성공
- VCN/AWS/On-Prem route acceptance
- 승인/미승인 workload TCP path 판정
- failure/recovery acceptance
- D21 GO 승인
- P2-VPN-01 또는 G4 완료

## Security / handling

편입 대상 원본에서 private-key header, GitHub token 패턴, AWS access key 패턴, password/token/secret assignment의 단순 민감정보 패턴 검사를 수행했고 탐지 0건이었다.
이는 일반적인 정적 문자열 검사 결과이며 모든 민감정보 부재를 절대적으로 보증하는 것은 아니다.
