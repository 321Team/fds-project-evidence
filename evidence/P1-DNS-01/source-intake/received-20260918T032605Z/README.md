# DNS Source 이관을 위한 현장 수집 원본

수신 기준: 2026-09-18 12:26:05 KST. 대상 티켓 P1-DNS-01은 기존 **Done / 2026-09-03**을 유지한다. 이 묶음은 소스 복원·비교를 위한 현재 관찰 자료이며 과거 인수의 재승인, 새로운 AC PASS 또는 배포 승인이 아니다. 편입 상태는 **독립 리뷰·병합 대기**다.

## 출처와 파일 보존

- `stage1/dns01`, `stage1/dns02`: 사용자가 11:05:05 / 11:05:13 KST에 수집한 7개씩 총 14개 파일. 설정은 `named-checkconf -p -x`의 정규화·마스킹 결과이며 원 named.conf/include 파일 구조가 아니다. 1차 명령별 RC 기록은 미제공이다.
- `stage1/screenshots`: 당시 systemctl 화면 2개. `${NAMEDCONF}` / `$OPTIONS`가 해석되지 않은 표시이므로 화면만으로 실제 경로를 확정하지 않는다.
- `stage2/dns01`, `stage2/dns02`: 사용자가 12:24:50~12:24:53 KST에 수집한 24개씩 총 48개 파일. 실행기 Source는 [infra-dns commit 091ecee](https://github.com/321Team/infra-dns/blob/091ecee21d777ab36877381a1b3f5bb8ef1f6eb2/tools/collect_dns_zone_readonly.py), SHA-256 `9458d9aa60d8589809eadc129cd4186f7084a2eea7fdba8302c5a090ae0e1346`이며 두 SESSION 값과 일치한다.
- 원본 총 64개는 바이트 그대로 보관한다. filename/folder mapping·수신 SHA-256·크기는 [MANIFEST.json](MANIFEST.json)에 있다. 이 문서·MANIFEST·RECEIPT_SHA256SUMS는 수신 후 생성한 관리 자료다. 서버 명령으로 생성된 과거 증적으로 위장하지 않는다.
- 1차 Manifest 12항목, 2차 Manifest 46항목 모두 일치한다. 각 원 SHA256SUMS는 변경하지 않았다. 수신 해시 일치는 파일 무결성 확인이며 작성자 서명이나 독립 승인을 의미하지 않는다.
- 민감정보 패턴과 TSIG 마스킹을 확인했다. 실제 private key / TSIG key 파일 및 그 hash / 인증된 AXFR MAC은 포함하지 않는다. 패턴 검사는 모든 비밀정보 부재의 증명이 아니므로 독립 diff 검토를 유지한다.

## 확인 결과

| 항목 | dns01 | dns02 |
|---|---|---|
| 수집 종료 | 12:24:51 KST | 12:24:53 KST |
| 상태 | COMPLETE_COLLECTION_ONLY | COMPLETE_COLLECTION_ONLY |
| 실행 파일 / 프로세스 root | `/usr/sbin/named` / `/` | 동일 |
| 실제 config 인자 | `/etc/named.conf` | 동일 |
| BIND | 9.18.33 | 9.18.33 |
| Zone 실제 경로 | `/var/named/fds.internal.zone` | `/var/named/slaves/fds.internal.zone` |
| 원 Zone 형식 | text / 698 bytes | raw / 822 bytes |
| named-checkzone | text RC 0 | text RC 1 → raw RC 0 |
| 전후 PID / Zone stat / serial | 변경 미관측 | 변경 미관측 |
| serial | 2026090101 | 2026090101 |

dns02의 text RC 1은 바이너리 raw를 text로 읽은 시도 결과다. 이어 raw 검사 RC 0으로 정규화했으므로 이것을 Zone 손상이나 수집 실패로 판정하지 않는다. 다른 수집 명령은 모두 RC 0이다. 오류 stderr와 전체 프로세스 argv는 Collector 설계상 보존하지 않았으며 COMMANDS.json에 해당 제한을 명시했다. 실제 명령 trace와 범위는 각 호스트 원본을 따른다.

정규화 Zone 882 bytes는 양쪽에서 바이트가 같고 SHA-256은 `7161d50eaaed299d4cc14eb409a5351e7c260aff572db04e8a3802c97c09b954`다. A 13개 / NS 2개 / SOA 1개 / TTL 300을 확인했다. A Record 이름·주소는 [승인 R5 기록](https://github.com/321Team/fds-project-evidence/blob/90093f88167055f81e8789d2a848f44ead0ee9ce/records/received-20260907/P1-DNS-01_Notion_Description_v1.3_Review.md)의 13개와 일치한다. `.56`은 ACL/ipset의 후속 허용 대상이며 현재 Zone에 A Record가 없는 것은 그 자체로 결함이 아니다.

원본 Zone SHA-256:

- dns01: `f4bbbc4818e9724b07c1452caecfdb8d0629c8bf6fb75ea092ae44adc31642d8`
- dns02: `9f654c78cc5b8addbc2605dcd2b61c310f43a84cf754734f8a4d6414b0478d64`

## 방화벽 판정

양쪽 호스트의 runtime 설정끼리, permanent 설정끼리 바이트가 같다. public은 기본 zone이고 runtime에서 ens160이 연결되어 있다. 일반 services는 `cockpit dhcpv6-client ssh`, 직접 ports는 비어 있으며 DNS 허용은 다음 rich rule이다.

```text
rule family="ipv4" source ipset="fds-dns-clients" service name="dns" accept
```

이 rich rule과 ipset 14개는 runtime/permanent가 일치한다. `.50 .51 .52 .53 .54 .55 .56 .102 .103 .104 .105 .107 .108 .109`이며 관리 `.10/.20/.30`과 전체 /24 허용은 없다. 1차 마스킹 BIND ACL의 loopback 외 14개와도 일치한다. 이 관찰은 [P1-DNS-01 #12](https://github.com/321Team/fds-project-baseline/issues/12)와 후속 [.56 결정 #78](https://github.com/321Team/fds-project-baseline/issues/78)의 범위에 맞는다.

runtime/permanent 전체 텍스트 차이는 public의 active 표기와 ens160 interface 표기다. permanent의 interface 칸이 비어 있다는 이유만으로 영구 설정 누락을 단정하지 않는다. NetworkManager 연결 또는 기본 zone을 통해 interface가 귀속될 수 있다([firewalld 공식 설명](https://firewalld.org/documentation/zone/connections-interfaces-and-sources)). 이 서버의 NetworkManager profile과 재기동 지속성은 미수집·미시험이다.

`nm-shared` 등 비활성 기본 zone에 dns service가 있는 것을 현재 ens160의 무제한 DNS 허용으로 해석하지 않는다. 실제 `dns` service 정의, policy/direct/kernel 규칙 전체와 패킷 허용·거부 시험은 이번 범위에 없다. 방화벽 전체 enforcement PASS는 주장하지 않는다.

## 소유권·검토·잔여 범위

- 원본 관찰 자료는 이 증적 저장소, 주 Zone Source 및 마스킹 참고 설정은 [infra-dns PR #1](https://github.com/321Team/infra-dns/pull/1)이 관리한다. dns02 raw 파일은 전송으로 생성되는 사본이며 배포용 주 Zone으로 승격하지 않는다.
- 발행 정본은 docs-v3.1.19 / `966fc5365874b1d259a9810fc876b57c3bfa0e08`. 후속 리뷰 위임 정책에서도 이 증적 저장소의 모든 PR은 독립 검토 대상이다. 이하영 `hayeounglee`의 검토를 요청하며 AI 기술 점검은 독립 승인이 아니다.
- 새 질의·재전송·failover·재시작·배포·티켓 종결을 수행하지 않았다. 원본 named.conf/include의 파일 구조, dns service 정의/NM persistence, v1.9 과거 실행 검증 원본은 남은 자료다. 이 자료의 편입이 downstream Runtime Gate를 자동 해제하지 않는다.
- 변경은 새 수집회차 경로 추가뿐이며 기존 R2 증적·수신 기록을 수정하지 않는다. 복구는 이 편입 PR revert이며 서버 원복 작업은 없다.

이 디렉터리에서 `sha256sum -c RECEIPT_SHA256SUMS`로 새 관리 자료를 포함한 66개 파일을 확인한다. 각 `stage1/<host>`와 `stage2/<host>`에서 `sha256sum -c SHA256SUMS`로 서버가 제공한 Manifest를 별도 확인한다.
