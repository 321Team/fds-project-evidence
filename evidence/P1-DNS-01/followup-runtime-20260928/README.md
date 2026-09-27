# P1-DNS-01 follow-up Runtime evidence — 2026-09-28

## 현재 판정

이 수집회차는 `infra-dns` 후속 이슈 #6과 #7-A의 **읽기 전용 Runtime 원본**을 보존한다.

- 기준 `infra-dns/main`: `5f7505f9613e4b94aedd4bcdaba52f2b3f1a5f19`
- #6 named 구조 collector: `1466aa8fa321e0d86d26e9ecf095d1471924036f64389c2c320e492f4826cb4f`
- #7-A firewall/NM collector: `326cf3676df37a90728fc0b44a7eb447af19958dd51f60de59201a4245c94021`
- dns01/dns02 모두 `COMPLETE_COLLECTION_ONLY`
- 각 archive 내부 `SHA256SUMS` 4세트 전 항목 일치
- archive 외부 `.sha256` sidecar도 실제 upload bytes와 일치
- secret-free 재검사: 탐지 0건

## 원본 archive

| Host | File | SHA-256 |
|---|---|---|
| dns01 | `archives/p1-dns-followup-dns01-20260928.tar.gz` | `d66851969da035d6818407e828a9f3c2c6be862dc9a046be923814155a773fcf` |
| dns02 | `archives/p1-dns-followup-dns02-20260928.tar.gz` | `72d726c35e935c0d8b630605e1f8861a38e625ffa47537b43e2bcc9f045ca73b` |

원본 archive는 업로드 받은 bytes 그대로 보존한다. 상세 구조와 검사 결과는 `MANIFEST.json`, 외부 receipt는 `RECEIPT_ARCHIVES_SHA256SUMS`를 기준으로 한다.

## #6 결과

양 노드 공통:
- `named.conf` 및 include 파일 5개 수집
- `fds-transfer-key` 정의/참조 일치
- `keys_referenced_but_not_defined=[]`
- `/etc/crypto-policies/back-ends/bind.config` → `/usr/share/crypto-policies/DEFAULT/bind.txt`
- TSIG secret 원문/원문 hash는 수집하지 않음

dns01의 expanded sanitized SHA는 `795007395c75647959d829cde7a384c2aeba86954b237c74de531dea694d7f1d`로 2026-09-18 reference와 다르다. sanitized diff에서 Root DNSSEC KSK-2024 trust anchor(key tag 38696) 추가 1건으로 분류했다. dns02는 2026-09-18 pinned SHA와 일치한다.

## #7-A 결과

양 노드 공통:
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

`interface_in_permanent_public=false`만으로 persistence를 주장하지 않는다. NetworkManager profile 기반 연결 상태는 확인했지만 **reboot 후 지속성은 아직 시험하지 않았다.**

## Secret-free 검사

편입 전 archive 내부 전체 텍스트를 대상으로:
- PEM private key header
- `ghp_` / `github_pat_` token pattern
- `secret "..."` 중 `?` 이외 값

을 재검사했고 **0건**이었다.

## 범위와 잔여 작업

- #6 양 노드 Runtime collection/integrity/TSIG reference: **PASS**
- #7-A 양 노드 read-only Runtime / NM parser fix: **PASS**
- Evidence 독립 리뷰: **PENDING**
- #7-B UDP/TCP 53 packet test: **NOT RUN**
- #7-C reboot persistence: **NOT RUN**
- v1.9 Runbook 원본 terminal log: 현재 `infra-dns` / `fds-project-evidence` 기본 브랜치 tree에서 찾지 못함
- 이 PR의 병합만으로 #7 전체 완료, packet 차단/허용, reboot persistence, P1-DNS-01 재인수를 주장하지 않는다.
