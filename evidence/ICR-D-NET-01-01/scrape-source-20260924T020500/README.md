# ICR scrape Source 수신·연결 대조 — 2026-09-24 KST

**판정: 무결성 확인 / Pod 경로·SNAT 및 출발 포트 변환 확인 / counter 수집 PARTIAL.**
책임: ICR-D-NET-01-01 Lead 이권욱. 연계: baseline #14·#17·#19, infra-kubernetes PR27·PR28.
운영 정책 적용·통신 AC PASS·IF-06B 인수로 확대하지 않는다.

## 출처·무결성

- 사용자 첨부 `ICR_Scrape_Source_Q9M3kW.tar.gz`, 10,233bytes.
- SHA256 `2d4014cd30af788438a62a3d166bec372b7ac4919c9ae6527ea6a1427cb6c9f3`.
- 외부 sidecar 일치, 내부12/12, 실행 소스4/4, 캡처 stdout3/3 해시 일치.
- 원 실행 소스 `df024dc641e1a09a4d7e0f018117cfd04000aee5` ([PR28](https://github.com/321Team/infra-kubernetes/pull/28)), REVIEW=NOT PERFORMED (Pre-check).
- `original/` 13개 파일은 tar 내부 원문 바이트 그대로다. 원 Manifest와 controller rc를 사후 정정하지 않았다. `RECEIPT.json`과 이 검토서에 별도 판정을 기록한다.
- 원 archive는 기존 사용자 첨부 보관을 유지한다. 식별자는 RECEIPT.json 참조. 재압축/Release Asset 업로드 없음, 독립 검토자의 원 archive 접근 인계는 미확인이다.
- 현재 디렉터리 SHA256SUMS는 편입 자료용이다. Git에는 텍스트 사본만 편입하며 .gitattributes의 -text를 유지한다.

## 실행과 완전성

| 항목 | 결과 |
|---|---|
| controller 시작 | 2026-09-24 02:04:57.517521 KST, server01_ansible |
| 전후 sender 조회 | 02:04:58.762–58.825 / 02:05:30.171–30.215 KST |
| 대상·계정 | control01(.102), worker01(.105), worker03(.108); svc_ansible |
| inventory | infra-ansible da7f2ccd52ee407e61376d11375a1361f076f112, tracked_changes=false; inventory hash 0e7e66c6b182c95d9bff4502e02de7c8669a781296b7ff45965a8b2defb4f565 |
| 현장 Ansible | syntax-check 성공, 각 host ok9/changed2/unreachable0/failed0 |
| changed6 | ansible01에 단계별 envelope JSON6개 저장; 서버 설정 변경이 아님 |
| 수집 명령 | 일반 조회31개 중23 rc0·8 rc1; 별도 tcpdump3개 rc0 |
| controller rc | 원 기록은0이나 선택 counter8조회 실패. 수신 판정은 PARTIAL |

모든 shell/API 동작 성공으로 보고하지 않는다. SHA 일치는 바이트 무결성이며 독립 실행 인증 또는 AC PASS가 아니다.

## 같은 연결의 3지점 대조

전후 guard에서 Pod UID `46c00f91-2073-440a-800c-6cedba89d291`, monitoring-api/prometheus-58c848c688-kzvhp,
worker03, PodIP10.244.39.219, hostIP10.1.93.108, SA prometheus, Ready 및 imageID가 모두 일치한다.
imageID는 `10.1.93.54/fds/prometheus@sha256:b77f9cee82fd1c61521634d2d6b192fc526ffd938e904b8e6836b6c0cf8d875a`다.

| 관측 위치 | Source | Destination | 관측 수 |
|---|---|---|---|
| worker03 calib6219a02ba1 | 10.244.39.219:Pod 출발 포트 | 10.1.93.105:9100/10250 | SYN64 |
| worker03 ens160 | 10.1.93.108:변환된 출발 포트 | 동일 | SYN64 |
| worker01 ens160 | worker03 ens160과 동일 IP·포트 | 동일 | SYN64 |

목적 IP/port, Flags, TCP sequence, window 및 TCP options(TS val 포함), length를 키로 대조했다.
각 지점에서 키64개가 고유하며 세 집합이 완전히 일치한다. 동일한 packet64개를 세 위치에서
본 것이며 독립 패킷192개로 합산하지 않는다. 재전송을 묶으면 TCP 연결19개(9100 6개,
10250 13개)이며, packet 수는 각각21/43이다. 19개 연결 모두 source IP와 port가 변환된다.

대표값:

| Port | Pod Source | Wire Source | TCP seq |
|---|---|---|---|
| 9100 | 10.244.39.219:60702 | 10.1.93.108:21109 | 349599148 |
| 10250 | 10.244.39.219:39458 | 10.1.93.108:2832 | 2806707438 |

`FLOW_CORRELATION.json`에 대조 키·19개 연결·64개 대응을 남겼다. sender route는 해당 Calico veth를
직접 가리키며, veth에서 나온 같은 SYN이 worker03 ens160과 worker01 ens160에 보인다.
따라서 **해당 Prometheus Pod의 네트워크 경로와 worker03에서의 SNAT/출발 포트 변환은 관측 근거가 확보**됐다.
PID/socket 단위 프로세스 조회나 특정 NAT 규칙에 대한 귀속을 수행한 것은 아니다.

세 캡처는 02:05:00.757–29.498 KST 사이에64개 제한으로 종료했다(전체35초가 아님).
필터는 SYN·RST를 양방향으로 포함하며 SYN-ACK도 매칭하지만, 보존된64개는 모두 Flags[S]다.
**이 제한 관측 구간에서 SYN-ACK/RST는 미관측**이다. 모든 시점·다른 인터페이스·기존 연결의 응답 부재를 뜻하지 않는다.
각 tcpdump의 kernel dropped0은 캡처 버퍼 손실 통계이며 Netfilter DROP0의 증거가 아니다.
호스트 시각 동기화 오차를 별도 검증하지 않았으므로 timestamp 차이를 정확한 네트워크 지연으로 보고하지 않는다.

## 리스너·경로와 counter 누락

- worker01/03 모두 TCP9100/10250 LISTEN 관측.
- worker01 → PodIP는 via10.1.93.108/ens160, worker01 → wire Source .108은 ens160 직접 경로다.
  route entry가 있다는 사실은 실제 반환 패킷 성공을 뜻하지 않는다.
- 이전01:21 HEP/GNP snapshot의 worker01 ingress는9100 허용이 없고10250은 CP3개 source만 허용한다.
  이번 .108 source와 불일치한다. 하지만 이번 window의 실제 정책/kernel counter를 확보하지 못해 정확한 drop rule은 미확인이다.
- 실패8개는 두 Worker의 filter/nat × before/after 조회다. 실행된 명령은
  `/usr/sbin/xtables-nft-multi -c -t filter|nat`이고 모두 rc1, `No valid subcommand given`이다.
  수집기 tool()이 symlink의 root 소유권/권한 검증 후 resolved 경로를 반환하면서 `iptables-save`
  호출명이 사라진 코드 결함이다. sudo 권한 부족·서버 정책 오류로 분류하지 않는다.

## 보완과 인수 범위

수집기는 root target 검증을 유지하면서 원래 명령명으로 호출하도록 수정한다. counter8조회 실패를
숨기지 않도록 부분 결과와 controller 종료 코드를 보완한다. 이미 확보한 패킷 수집을 반복하지 않고
`--counters-only`로 기존 두 Worker의 IPv4 iptables tables/counters를20초 간격으로 읽는다.
수정본의 실제 서버 실행은 미수행이며 새 window가 과거 누락 counter를 복원하지는 않는다.

PR27의 .108/32 임시 진단 후보는 이 실제 wire source와 맞지만, .108은 다른 workload/호스트 트래픽도
공유할 수 있는 node identity다. 승인 Prometheus만 허용하는 영구 통제/AC07 충족으로 인정하지 않는다.
정책 후보의 독립 코드 리뷰·적용, kubelet IP SAN/CA+SA, monitor01:443 IF-06B source/return·TLS/Auth는 별도 후속이다.
이번 실측으로 전체 내부 SNAT 정책 위반이나 IF-06B Source를 자동 판정하지 않는다.

기존 ICR AC·담당·일정·open 상태 유지. 증적 편입은 EVIDENCE_POLICY의 독립 리뷰·병합 대기다.
