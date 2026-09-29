# P1-DNS-01 / infra-dns #7 B·C Runtime evidence — 2026-09-29

## 범위

이 수집회차는 `321Team/infra-dns` Issue #7의 후속 Runtime 중 아래 항목을 보존한다.

- B: 허용/비허용 Source의 UDP/TCP 53 packet 동작
- C: dns02 → dns01 순차 reboot persistence

Issue: https://github.com/321Team/infra-dns/issues/7

이 폴더의 원본 텍스트 파일은 사용자로부터 수신한 바이트를 그대로 편입한다. 별도 재포맷·내용 보정은 하지 않는다.

## 승인 및 실행 경계

Lead `hayeounglee`는 Issue #7 comment `5863068158`에서 B/C 실행에 동의했다.

실행 순서는 승인 Runbook대로 다음과 같이 유지했다.

1. B 완료·판정
2. C dns02 pre-check → reboot → post-check → 정상 복귀 확인
3. C dns01 pre-check → reboot → post-check

dns02가 정상 복귀하기 전 dns01 reboot는 수행하지 않았다.

## B — UDP/TCP 53 packet test

### 허용 Source

- source: control01 `10.1.93.102`
- target: dns01 `10.1.93.52`, dns02 `10.1.93.53`
- UDP/TCP SOA query: `fds.internal SOA`
- 결과: dns01/dns02 모두 UDP/TCP `NOERROR`, RC=0
- 최초 기능시험 시각: 2026-09-28 14:35:13 KST
- 상세 판정 기록: infra-dns #7 comment `5864121832`

허용 Source의 `dig` 출력은 사용자 콘솔 제출 자료로 확인했으며, 별도 서버 생성 원본 파일은 이 수집회차에 수신하지 않았다. 따라서 이 폴더의 SHA-256 Manifest는 허용 Source console transcript 자체의 서버 원본성을 주장하지 않는다.

### 비허용 Source

- source: ansible01 `10.250.10.10`
- target: dns01 `10.1.93.52`, dns02 `10.1.93.53`
- route precondition: PASS
- client `dig`: UDP/TCP 모두 `host unreachable`, RC=9
- server attribution:
  - dns01이 직접 `ICMP ... admin prohibited filter` 반환
  - dns02가 직접 `ICMP ... admin prohibited filter` 반환
- 유효 DNS 응답: 0건

원본 capture:

- `dns-packet-b-client.dns01.20260929T112421.txt`
- `dns-packet-b-client.dns02.20260929T112013.txt`

판정 기록:

- dns02 attribution PASS: infra-dns #7 comment `5882423201`
- dns01 attribution 및 B 최종 PASS: infra-dns #7 comment `5882475798`

## C — reboot persistence

### dns02

pre:

- file: `dns-reboot-c-pre.dns02.20260929T112958.txt`
- pre boot_id: `de864d96-d040-4aaa-aecd-a72bc69573e0`
- named/firewalld/NetworkManager active+enabled
- default/active zone `public`, `ens160`
- runtime/permanent DNS rich rule 동일
- NM `connection.zone=""`, `connection.autoconnect=yes`
- `ens160=10.1.93.53/24`
- control01 pre UDP/TCP SOA: `NOERROR`, RC=0

post:

- file: `dns-reboot-c-post.dns02.20260929T114016.txt`
- post boot_id: `dc49e66c-49a0-4fe3-b65b-43adc78552b5`
- boot_id 변경 및 uptime 0 min으로 실제 reboot 확인
- named/firewalld/NetworkManager active+enabled
- zone/rich rule/NM/IP/route 유지
- control01 post UDP/TCP SOA: `NOERROR`, RC=0

Runtime 최종 판정: PASS  
판정 기록: infra-dns #7 comment `5882644611`

### dns01

pre:

- file: `dns-reboot-c-pre.dns01.20260929T114536.txt`
- pre boot_id: `4e25100f-789c-46eb-9ca9-22ae24de92e1`
- named/firewalld/NetworkManager active+enabled
- default/active zone `public`, `ens160`
- runtime/permanent DNS rich rule 동일
- NM `connection.zone=""`, `connection.autoconnect=yes`
- `ens160=10.1.93.52/24`
- control01 pre UDP/TCP SOA: `NOERROR`, RC=0

post:

- file: `dns-reboot-c-post.dns01.20260929T115024.txt`
- post boot_id: `08074700-5cd6-4f78-8c66-351b555c6cb7`
- boot_id 변경 및 uptime 1 min으로 실제 reboot 확인
- named/firewalld/NetworkManager active+enabled
- zone/rich rule/NM/IP/route 유지
- control01 post UDP/TCP SOA: `NOERROR`, RC=0

Runtime 최종 판정: PASS  
판정 기록: infra-dns #7 comment `5882717205`

## 원본 무결성

| File | Size (bytes) | SHA-256 |
|---|---:|---|
| `dns-packet-b-client.dns02.20260929T112013.txt` | 4574 | `40238b8dee94c30d4034af5953834a749a6da380331e3dd46098113a1a3b3db0` |
| `dns-packet-b-client.dns01.20260929T112421.txt` | 1646 | `5327a6d2908f43a7dc80eb41d32549f3dfc008a92daa4e0efc8357d0f8c85eb7` |
| `dns-reboot-c-pre.dns01.20260929T114536.txt` | 1527 | `fef9dc53d1a6b9b35ca96bebb79b1ede7ce59bc39bab45584fcde186a539367d` |
| `dns-reboot-c-post.dns01.20260929T115024.txt` | 1520 | `d96ba840a98d04c161e899d7359fa9e1f310ec25c60353286d15293da96ddecc` |
| `dns-reboot-c-pre.dns02.20260929T112958.txt` | 1569 | `1464a9937cd1a6d2cfdff5536650754ff8388b0b30721f47c9f57cc809720de3` |
| `dns-reboot-c-post.dns02.20260929T114016.txt` | 1547 | `fb1601d2f6bc7d483736794ffb1885fe5c7b7b262125ae8ef83acea84228f6d0` |

`SHA256SUMS_EVIDENCE`는 이 README와 위 6개 수신 원본을 검증한다.

## Secret-free 범위

이 수집회차에는 TSIG key material, password, private key, token을 의도적으로 수집하지 않았다. 원본 파일은 packet capture 및 서비스/네트워크 상태 출력으로 구성된다.

## 판정과 한계

- #7-A: 기존 Evidence PR #61에서 완료
- #7-B Runtime: PASS
- #7-C dns02 Runtime: PASS
- #7-C dns01 Runtime: PASS
- B/C 원본 편입: 이 PR에서 수행
- Evidence 독립 리뷰: PENDING
- Evidence merge: PENDING
- infra-dns #7 close: 독립 리뷰·병합 후 별도 최종 판단

이 증적 PR의 생성만으로 Issue #7 종결 또는 P1-DNS-01 재인수를 주장하지 않는다.
