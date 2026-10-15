# P2-VPN-01 — Stage B 터널 수립·시험·양쪽 원복, RUN `20261015T1100` — 2026-10-15

출처 티켓: [fds-project-baseline#37](https://github.com/321Team/fds-project-baseline/issues/37) (P2-VPN-01) · 실행 기록 [infra-terraform#11](https://github.com/321Team/infra-terraform/issues/11) · 코드 [infra-vpn PR #6](https://github.com/321Team/infra-vpn/pull/6)

vpn-gw01(On-Prem) ↔ AWS Relay 사이 IPsec(IKEv2, PSK)을 route OFF 상태로 1회 수립했다. 지정 시험(T1·T2·T4·T5·T10)을 마친 뒤 같은 창에서 양쪽을 원복했다. 터널은 유지하지 않았다. Stage C(route 활성화)·worker→DB 허용 시험·DB 변경은 범위 밖이다.

## 기록 연결

| 단계 | GitHub 기록 |
|---|---|
| 작업창 GO(11:00~13:00 KST, P8 권욱 확인) | [#11 6182615142](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6182615142) |
| 시작 기록(조회 게이트·B0·B1) | [#11 6182821690](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6182821690) |
| 완료 보고 | [#11 6183080378](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6183080378) |
| 결과 리뷰(수용, 출처 한계 명시) | [#11 6183290093](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6183290093) |
| 최종 세션 조회 사본 수용 | [#11 6183629239](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6183629239) |
| 직전 확인 원문 위치·sudo/RC 설명 | [#11 6182597656](https://github.com/321Team/infra-terraform/issues/11#issuecomment-6182597656) |

## 실행 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이재환. Relay: CloudShell `netop` 프로필 → `assumed-role/FDS-Network-Operator/321team-jaehwan`(MFA) → SSM `ssm-user` + sudo. vpn-gw01: `server08` + sudo |
| 원복 인수자 | 이권욱(해당 시간 대기·양쪽 접근, GO 본문) |
| 코드 | infra-vpn merge `6432d7ebb712aaf6368e9a7a001ae55fc572215e`(PR6 HEAD `73ac1cd9…`와 트리 동일) |
| 배포 묶음 | `package/p2-vpn-01-stageb.tgz` 13,888 B, SHA256 `358624f5a380e341b7095ccd13357d03f9bf6d346a8d4c331f0552a212b0bbaf` — 양쪽 같은 묶음 |
| 대상 | Relay `i-05e4b63d31d8d5ac5`(10.20.110.10, EIP `3.36.239.132`/`eni-0017c49242017af9b`, Libreswan 4.15-10.el9), vpn-gw01 10.1.93.51(Libreswan 5.4-1.el10) |
| 시각(KST) | 조회 게이트 10:59:38 → B0 11:06~11:07 → B2 11:13 → B3·B4 11:15~ → T 11:22~11:24 → 원복 vpn-gw01 11:25:15·Relay 11:26:40 → 마지막 AWS 호출 11:28:25 |
| SSM 세션 | `l5dv2nyaxzkqiecv5nvaan6cku`(게이트·B0·B1), `df72gcfla8x4zky7ne4nibukzi`(B2, 터미널 기록 없음), `qgxh9k9e6t7y52utz5cux3slv8`(B3~원복) — 모두 Terminated. 기존 `5rfcx2p4…`는 History Terminating, SESSION_CLEANUP=PENDING |

## 파일

| 경로 | 출처 수준 | 내용 |
|---|---|---|
| `p37-stageb-20261015T1100.tgz` (+ `.sha256`) | CloudShell에서 묶어 다운로드한 **원본** archive, 24,140 B `7ece6715…` | `gate-aws.log`·`b3-relay.log`·`SHA256SUMS` |
| `cloudshell/` | 위 archive를 푼 파일(바이트 동일, `cloudshell/SHA256SUMS` 2/2) | `gate-aws.log`: 10:59:38~11:12 조회 게이트(P2/P3/P5/P6)·B0·B1(세션 l5dv). `b3-relay.log`: B3~Relay 원복(세션 qgxh). `script -q -f` 출력 기록, 입력 기록 없음 |
| `vpngw01-stageb-20261015T1100.txt` | 실행자 터미널 출력을 채팅으로 옮긴 **사본**(base64 본문·알고리즘 목록만 생략, 머리말 표시) | vpn-gw01 직전 재확인·B0·B1·B2 결과 줄·B4·B5·status·T4/T5 카운터·T10·원복·항목별 대조 |
| `relay-b2-20261015T1100.txt` | 사본(결과 줄) | Relay B2. PSK 입력 회차라 기록하지 않음 |
| `stageb-final-ssm-query-terminal-copy-20261015T0228Z.txt`, `README-final-ssm-query.md` | 터미널 화면 사본과 그 설명(파일 원본 없음) | 11:28:19 Active 없음, 세션 3개 Terminated, 11:28:25 마지막 조회. 6183629239에서 수용 |
| `operator-notes-README.md` | 공유폴더 `p37-stageb-run-20261015T1100\README.md` 사본 | 실행 직후 파일 설명·오입력 기록 |
| `precheck-20261015T0110Z/` | vpn-gw01 10:10:50 사전 읽기(P5·P7) 사본: 생략 없는 `.full.txt`, 파생 `.txt`, `precheck-notes-README.md`(sudo·RC 설명) | 공유폴더 `p37-stageb-precheck-20261015\`와 같은 바이트. 6182615142에서 수용 |
| `package/` | 배포 묶음 원본 + `.sha256` + 준비 기록 `MANIFEST.md` | 6개 파일 blob·SHA256, 병합 커밋 결속 |

PSK·secrets 내용·그 해시, xfrm 키는 없다. 실행기가 SPI·키를 가렸다. 로그의 64자 hex 문자열은 설치 파일 SHA256이다(`946cba4c…`·`d8c1f567…`·`f4026138…`).

## 결과 요약

| 항목 | Relay | vpn-gw01 |
|---|---|---|
| 조회 게이트 | 흔적 0, 유닛 없음, nft firewalld만, ipsec inactive/disabled(Pluto rc33), public runtime=permanent(`eth0`은 NM 결속, zone 미지정→public), `ip_forward=0` | 흔적 0, 유닛 not-found, nft firewalld만, ipsec active·`loaded 0`, public runtime=permanent(`ens160` 같은 구조), `ip_forward=1` |
| B0 | 외부 1 + 내부 6/6 OK, 7파일 | 같음(b64 사본 끝 빈 줄 1개, 복원 tgz 일치) |
| B1 `check` | rc0 | rc0 |
| B2 `psk` | 0600 root, owner=RUN, rc0 | 같음 + `rereadsecrets rc=0` |
| B3/B4 `apply` | `APPLY_OK` rc0, `firewalld_changed=yes`(500·4500/udp permanent→reload), `eth0` public 유지 | `APPLY_OK` rc0(`RELAY_EIP=3.36.239.132`), `firewalld_changed=no`, `99-fds-p2-vpn-gw.conf` ip_forward=0 |
| B5 `up` / T1 | IKE·Child SA established, espinudp(vpn-gw01은 NAT 뒤 121.160.42.93:64916), xfrm `10.1.93.0/24↔10.20.0.0/16` out·fwd·in | `initiator established IKE SA … authby=secret`, Child SA, 같은 정책 |
| T2(진단) | `probe 10.1.93.51 22` → `rc=0 CONNECTED` | — |
| T4 / T5 | `probe 10.1.93.55 5432`·`22` → 각 `rc=124 TIMEOUT` | `from_vpc` 마지막 drop 0→3→6 |
| T10 | stop → forward 0·표 없음 / start → forward 1·표 재적재 | 같음 |
| 원복 | `ROLLBACK_DONE` rc0, receipt `cleaned_at 02:26:40Z by=rollback`, 흔적·OWNER·ACTIVE 없음, SAD 0, ipsec inactive/disabled, ports 비움, bootstrap 그대로 | `ROLLBACK_DONE` rc0, `cleaned_at 02:25:15Z`, `rereadsecrets rc=0`, 흔적 없음, SAD 0, ipsec active·`loaded 0`, 방화벽 그대로, gw conf 원래 11줄 |

## 한계

- vpn-gw01 출력과 최종 SSM 조회는 터미널 화면 사본이다. 서버나 CloudShell에서 직접 수집한 파일 원본이 아니다.
- 실행 중 오입력 2건이 있었고, 둘 다 `b3-relay.log`에 남아 있다. 상태 변경은 없었다.
  - B3 확인 묶음을 apply보다 먼저 실행했다. 그 결과는 apply 직전 상태로 해석한다.
  - vpn-gw01용 줄을 Relay에서 실행했다. apply는 경로가 없어 rc127로 실행되지 않았고, 나머지는 읽기와 프롬프트 문자열 오입력이다.
- 종료 시점의 AWS route 재조회는 하지 않았다. route OFF는 실행 전 조회(`10.1.93.0/24` route table 0개)와 승인 범위에 근거한다.
- 이 증적은 지정 시험·원복 범위의 결과다. Stage C, 상시 터널, worker→DB 허용 경로, #37·G4 완료로 확대하지 않는다.
