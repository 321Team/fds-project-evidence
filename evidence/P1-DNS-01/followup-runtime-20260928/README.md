# P1-DNS-01 follow-up Runtime evidence — 2026-09-28

## 범위와 기준

이 수집회차는 `infra-dns` 후속 이슈 #6과 #7-A의 읽기 전용 Runtime 원본을 보존한다.

- source repo: `321Team/infra-dns`
- source main: `5f7505f9613e4b94aedd4bcdaba52f2b3f1a5f19`
- #6 collector: `collect_named_structure_readonly.py`
  - SHA-256 `1466aa8fa321e0d86d26e9ecf095d1471924036f64389c2c320e492f4826cb4f`
  - source PR #15 approved head `ea60d73d6dc79cb8e610315a84f275d5c22f5149`
  - merge commit `1f7319bd2bbc33fb740c3a9ea13e66b93e6310ab`
- #7-A collector: `collect_dns_firewall_readonly.py`
  - SHA-256 `326cf3676df37a90728fc0b44a7eb447af19958dd51f60de59201a4245c94021`
  - source PR #16 approved head `2b86f06b7d4b7c2d60dd4bcab0cb2e75e2887e27`
  - merge commit `5f7505f9613e4b94aedd4bcdaba52f2b3f1a5f19`
- user-upload 수신 시각: `2026-09-28T02:30:38.435+09:00`

## Runtime provenance

| Host | 계정 | 명령 | 결과 경로 | 완료 시각(KST) | 결과 |
|---|---|---|---|---|---|
| dns01 | `server01_dns01` | `python3 ./collect_named_structure_readonly.py` | `/home/server01_dns01/dns-named-structure.dns01.jdtceg7q` | `2026-09-28T02:11:37.065688+09:00` | COMPLETE / RC=0 |
| dns01 | `server01_dns01` | `python3 ./collect_dns_firewall_readonly.py` | `/home/server01_dns01/dns-firewall.dns01._o_ec2cr` | `2026-09-28T02:20:13.349950+09:00` | COMPLETE / RC=0 |
| dns02 | `server08` | `python3 ./collect_named_structure_readonly.py` | `/home/server08/dns-named-structure.dns02.q06t98ae` | `2026-09-28T02:22:55.856544+09:00` | COMPLETE / RC=0 |
| dns02 | `server08` | `python3 ./collect_dns_firewall_readonly.py` | `/home/server08/dns-firewall.dns02.barc4maw` | `2026-09-28T02:25:23.618582+09:00` | COMPLETE / RC=0 |

두 collector는 서버 설정·파일·패키지·서비스·방화벽/네트워크·계정/권한을 변경하지 않고 지정 수집 경로에 결과만 남기는 1회성 read-only validator로 사용됐다. reload/restart/reboot는 수행하지 않았다.

## 원본 archive와 무결성

수신한 tar.gz를 재압축하거나 변환하지 않고 원래 바이트 그대로 Git에 편입한다.

- `archives/p1-dns-followup-dns01-20260928.tar.gz`
  - size: 10055 bytes
  - SHA-256: `d66851969da035d6818407e828a9f3c2c6be862dc9a046be923814155a773fcf`
- `archives/p1-dns-followup-dns02-20260928.tar.gz`
  - size: 9901 bytes
  - SHA-256: `72d726c35e935c0d8b630605e1f8861a38e625ffa47537b43e2bcc9f045ca73b`

각 archive의 같은 이름 `.sha256` sidecar와 수신 바이트가 일치했다. 각 archive 내부 서버 생성 `SHA256SUMS` 4세트도 전 항목 일치했다. 내부 파일 목록·크기·SHA-256은 `registry/ARCHIVE_CONTENTS.json`에 등록한다.

## #6 결과

양 노드에서:
- `fds-transfer-key` defined/referenced 일치
- `keys_referenced_but_not_defined=[]`
- `/etc/crypto-policies/back-ends/bind.config` → `/usr/share/crypto-policies/DEFAULT/bind.txt`
- TSIG secret 원문과 원문 hash는 수집하지 않음

dns01 expanded sanitized SHA-256은 `795007395c75647959d829cde7a384c2aeba86954b237c74de531dea694d7f1d`이다. 2026-09-18 reference 대비 차이는 Root DNSSEC KSK-2024 trust anchor(key tag 38696) 추가 1건으로 분류했다.

dns02 expanded sanitized SHA-256은 `ea12325ab17893b25c112914432f045fd574af2a9704d12601a41486fa058f48`이며 `expanded_matches_20260918_pinned_hash=true`였다.

## #7-A 결과

양 노드에서:
- firewalld active/enabled = true/true
- default zone = `public`
- `ens160` runtime public = true
- DNS service runtime/permanent = `53/tcp`, `53/udp`
- DNS rich rule runtime/permanent = true/true
- `fds-dns-clients` ipset = 14/14, runtime/permanent 동일
- NetworkManager active connection 확인
- `connection.zone=""` → firewalld default zone 사용
- `connection.autoconnect=yes`
- direct rules runtime/permanent = 없음

`interface_in_permanent_public=false`만으로 reboot persistence를 주장하지 않는다.

## Secret-free 검사

수신 archive 전체 텍스트를 대상으로 PEM private key header, GitHub token pattern, unmasked `secret "..."`을 재검사했고 탐지 0건이었다.

## 판정과 한계

- #6 양 노드 Runtime collection / integrity / TSIG reference: PASS
- #7-A 양 노드 read-only Runtime / NM parser fix: PASS
- Evidence 독립 리뷰: PENDING
- #7-B UDP/TCP 53 실제 packet test: NOT RUN
- #7-C reboot persistence: NOT RUN
- v1.9 Runbook 원본 terminal log: 현재 `infra-dns` / `fds-project-evidence` 기본 브랜치 tree에서 찾지 못함

이 수집회차 편입 또는 PR 병합만으로 #7 전체 완료, packet 허용/차단, reboot persistence, P1-DNS-01 재인수를 주장하지 않는다.
