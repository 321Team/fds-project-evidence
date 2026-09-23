# ICR scrape counter 보완 수신·분석 — 2026-09-24 02:40 KST

판정: **카운터 보완 수집 완료 / worker01 호스트 GNP의 실제 DROP 증가 확인 / 통신 복구·AC 인수 미완료**.

책임: ICR-D-NET-01-01 이권욱. 정책·인증서 변경은 기존 K8S/SEC Lead, scrape 서비스 인수는 MON 담당 범위를 유지한다. 이 기록은 사용자 실행 원본의 자체 수신 분석이며 독립 코드/증적 리뷰가 아니다.

## 원본과 실행

- archive `ICR_Scrape_Counters_cXoiN1.tar.gz`, 60,846 bytes, SHA256 `85e57eb5ab91562209538677fe1658fa4e3c6e6bc4810371a93d0d19f550ef47`.
- 외부 sidecar 일치, 내부10/10·실행 소스5/5·보존된 read stdout7/7 해시 일치. controller rc0, envelope4/4 rc0, 조회9/9 rc0, read_failures0. 실제 Ansible syntax-check 성공.
- source `91b9792e0e276c0f97c36a0124fda14cf56a6b3b`, merge `07dcd51ffda40dd467ff3792ed6736d5d166291d`, [수집기 수정 PR30](https://github.com/321Team/infra-kubernetes/pull/30). REVIEW=NOT PERFORMED (Pre-check).
- controller server01_ansible@ansible01, 시작02:40:27.659 KST. 기존 infra-ansible commit `da7f2ccd52ee407e61376d11375a1361f076f112`, tracked_changes=false. 기존 inventory/계정 svc_ansible/sudo 사용.
- worker01 02:40:29.956–49.987, worker03 02:40:29.967–50.001 KST. 기존 `sudo -n /usr/sbin/iptables-save -c`를 각20초 간격 두 번 실행. symlink의 실행명 iptables-save를 유지했으며 resolved target은 xtables-nft-multi다. 이전 호출 오류가 이번 실행에서 해소됐다.
- control01 전후 guard02:40:28.878–50.703의 sender UID/node/IP/SA/imageID 동일. monitoring-api/prometheus-58c848c688-kzvhp, UID `46c00f91-2073-440a-800c-6cedba89d291`, worker03, PodIP10.244.39.219, hostIP10.1.93.108, SA prometheus. 기존02:05 sender와도 동일하다.
- Ansible control01 ok9/changed2, 각Worker ok5/changed1, failed/unreachable 모두0. changed4는 delegated localhost 결과 파일 저장이다. 서버 설정·방화벽·NAT·계정·서비스 변경이나 새 연결·패킷 캡처는 실행하지 않았다.

## 카운터 대조

두 서버 모두 mangle/raw/filter/nat 4개 테이블을 확보했다. worker01 441규칙, worker03 618규칙의 전후 순서·규칙 텍스트와 chain 정의가 동일하며 음수 counter delta는0이다. 이는 두 snapshot 비교 결과이며 중간 시점의 모든 변경 여부를 증명하지 않는다. 전체 원본은 original의 worker JSON stdout, 선택 규칙의 전후값·행번호는 COUNTER_DELTA_SUMMARY.json에 있다.

| 관측 규칙 | 전 → 후 packets | 증가 packets / bytes |
|---|---:|---:|
| worker03, .105 TCP9100 egress 허용 mark | 4,037 → 4,051 | 14 / 840 |
| worker03, .105 TCP10250 egress 허용 mark | 8,063 → 8,095 | 32 / 1,920 |
| worker01, host GNP 내 source .108 일치 mark | 12,100 → 12,146 | 46 / 2,760 |
| worker01, 같은 host GNP 최종 DROP | 23,311 → 23,357 | 46 / 2,760 |
| worker03, cali-nat-outgoing MASQUERADE | 4,415 → 4,431 | 16 / 960 |

위 수치는 packet counter다. 연결 수나 이번 창에서 캡처한 SYN 수로 바꾸어 쓰지 않는다. `14+32=46`, bytes도 `840+1920=2760`으로 일치한다. 시계 오차 측정·동시 per-flow capture는 수행하지 않았다.

### worker01 실제 DROP 규칙

filter 호출 경로: `INPUT → cali-INPUT → cali-from-host-endpoint → cali-fh-ens160 → cali-pi-_IZ_dpYgvbSNCZTvi1r-`.

마지막 chain의 첫 규칙 comment가 `GlobalNetworkPolicy fds-k8s-host-k8s-worker01 ingress`로 정책 이름을 직접 연결한다. 마지막 DROP rule comment는 `cali:wYUSqCe2q6dO_hSD`이며 `--mark 0x40000/0x40000 -j DROP`이다. 그 앞의 무조건 mark0x40000 설정과 DROP이 모두46 증가했다. filter stdout의 source .108 match는292행, 최종 mark/DROP은298/299행이다.

이 chain은 관리 SSH와 CP .102/.103/.104의 TCP10250, 노드간 UDP4789 허용 후 최종 Deny를 수행한다. TCP9100 허용은 없고 .108의 TCP10250도 허용하지 않는다. .108이 등장하는 규칙은 UDP4789 판단을 위한 source mark이며 모든 포트 Allow가 아니다. 그 source match도46 증가했고 최종 DROP까지 이어진다. 조회한 두 서버의4개 테이블에서 양수 증가한 명시적 DROP/REJECT는 이 규칙 하나다. native nftables/IPv6/다른 커널 계층 전체에 대한 진술은 아니다.

### 기존 패킷 관측과의 관계

[02:05 Source 회차](../scrape-source-20260924T020500/README.md)는 Pod veth→worker03 ens160→worker01 ens160의64 SYN을 대조해 SNAT/출발포트 변환을 확인했다. 이번02:40은 새 counter 창이다. 이전64패킷이 이번46 DROP이라는 뜻은 아니다.

**직접 확인:** worker01의 이름이 식별된 host GNP가 해당20초 창에서46패킷을 DROP했고 .108 source-match counter가 같은 양 늘었다. 송신 측 .105:9100/10250 허용 counter 합과도 일치한다.

**해석:** 기존 Source/도착 패킷·규칙 불일치·현재 양쪽 counter를 함께 보면 이 host GNP가 교차노드 scrape를 차단한다는 판단을 강하게 뒷받침한다. 단, 집계 counter는 packet identifier가 아니므로 각 Prometheus PID/연결별 DROP을 독립적으로 일대일 입증하지는 않는다. 통신 성공·복구 완료로 판정하지 않는다.

### NAT 규칙

worker03의 `cali-nat-outgoing`에는 `cali40masq-ipam-pools src` 및 `! cali40network-ip-pools dst` 조건의 `MASQUERADE --random-fully` 규칙이 있고16 증가했다. 같은 snapshot의 KUBE-POSTROUTING 및 vxlan interface MASQUERADE는 증가0이다. Calico NAT 경로가 활동한 사실을 확인했으며, 모든16건을 이번 scrape의 고유 연결로 귀속하지 않는다. ipset member/conntrack 원문은 미수집이다.

NAT table은 새 연결의 첫 패킷 중심으로 평가되므로 filter의46과 NAT의16을 같은 분모로 비교하지 않는다. 공식 근거: [Netfilter NAT 구조](https://netfilter.org/documentation/HOWTO/netfilter-hacking-HOWTO-3.html), [Calico outgoing NAT](https://docs.tigera.io/calico/latest/networking/configuring/workloads-outside-cluster). 문서는 동작 해석의 참고이며 설치 버전 일치/현장 성공 증거를 대신하지 않는다. 내부 대역이라는 이유만으로 natOutgoing의 비적용을 가정하거나 전역 NAT 변경을 제안하지 않는다.

## 후속 결정에 넘길 범위

1. 호출 오류 보완과 worker01 차단 지점 조사에 필요한 이번 수집은 완료다. 같은 counter/패킷 관측을 반복하도록 요구하지 않는다.
2. [운영 후보 PR27](https://github.com/321Team/infra-kubernetes/pull/27), 현재 검토 HEAD `e91f4a048269866f8f0d74e9237684cc4c4a291b`에 이 증거를 연결한다. 기존 `.108/32→.105/32:9100` 임시 후보의 독립 코드 리뷰와 담당 K8S/SEC Lead의 범위 판단, 기존 승인 음성 시험 workload·사전 차단 확인이 남는다. 2026-09-24 수신 검토 시 reviews0, Draft/open/unmerged다.
3. .108은 노드 identity이며 Prometheus 전용 identity가 아니다. 같은 노드의 비승인 workload 접근이 허용되면 FAIL·회수 조건을 유지한다. 해당 제한을 만족시킬 수 없다면 후보는 HOLD하고 identity를 유지하는 정책 설계가 필요하다. ICR 상시 공동 서명을 새로 요구하지 않는다.
4. 변경 시험에서는 worker01 node-exporter의 연속 scrape 성공, 같은 노드 비승인 workload 실패, 관리 경로 회귀, 종료 시 임시 후보 회수를 함께 남긴다. 현재 이 조건의 실제 실행·결과는 없다.
5. kubelet SAN/CA/SA와 TLS PR29, IF-06B monitor01:443, NodePort 및 다른 노드 인수는 별도다. 이번 창에 target API 조회가 없어 최신 UP/DOWN 재판정도 하지 않는다.

기존 ICR AC 집계3 PASS / 8 PARTIAL / 2 FAIL(보고) / 6 NOT_VERIFIED / 1 BLOCKED 및 담당·일정·open 상태를 유지한다. 수집 성공과 통신 AC를 구분한다. 이전02:05 회차의 원 rc0·8개 조회 오류·PARTIAL 기록은 변경하지 않는다.

## 편입 상태

원 archive 바이트와 원문11파일을 변경하지 않았다. 원 archive는 사용자 첨부로 보존하며 Git binary/Release 업로드나 재압축은 하지 않았다. 이번 첨부의 Library ID는 제공되지 않아 발명하지 않았고 file citation ID·원 파일명·SHA256을 receipt에 기록했다. 독립 검토자의 archive 접근 인계는 미확인이다.

새 회차만 기존 증적 Draft PR23에 추가한다. EVIDENCE_POLICY에 따라 독립 편입 REVIEW PENDING / MERGE NOT DONE. Git 게시 바이트·CI 상태는 게시 후 PR 기록으로 연결한다. 소스의 기존 LOCAL17 PASS·CI NOT RUN과 이번 실제 순수 조회 성공을 구분한다. AI 사용: CODEX_ASSISTED.
