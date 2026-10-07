# P1-K8S-01 `mtu-path-run01` — 핵심 요구 "MTU 후보 1450 실측" 경로 관측 시험 원본, 2026-10-07

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 6의 보완 시험(교차 노드 Pod TCP 흐름의 캡슐화 여부·MSS·호스트 관측 세그먼트 크기)의 **서버 원본과 실행자 출력**을 편입합니다. 이전 [evidence#83](https://github.com/321Team/fds-project-evidence/pull/83)(`mtu-20261001`)의 공백(`DF/PMTU=NOT_PERFORMED`, 실제 패킷·MSS 미관측, 캡슐화 여부 미구분)을 정책 변경 없이 좁히려는 1회 시험이다.

**이 문서는 MTU AC의 PASS·충족을 주장하지 않는다.** 판정과 인수는 검토자와 Lead가 한다. 캡슐화 경로의 1450과 DF/PMTU는 이 시험으로 확인되지 않았고 `NOT_VERIFIED`/`NOT_PERFORMED`를 유지한다.

## 승인·기록 (모두 #10)
[계획·GO 요청 6030353160](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6030353160) → [조건부 1회 GO 6030613770](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6030613770) → [사전 확인 NO-GO 6030925566](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6030925566) → [변경 GO 요청 6030938621](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6030938621) → [변경 조건부 1회 GO 6031080670](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6031080670) → [착수 기록 6031289687](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6031289687) → [종료 기록 6031350840](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6031350840).

## 자료 구분
두 압축 파일은 **서버·ansible01에서 만든 원본 묶음**이다(콘솔 붙여넣기 재구성본이 아니다).

| 파일 | 만든 곳 | SHA-256 | 내용 |
|---|---|---|---|
| `mtu-path-run01-originals-20261007.tgz` | ansible01이 control01·worker01의 `/root/mtu-path-run01-20261007`을 `tar` 후 `fetch` | `a569a76623d68352bfd9a2105999c23d0e671226ef828f530335f7191d7dbc9e` | `k8s-control01.tgz`(S0 파일 8개와 `run-b/` 32개 파일: 후보·donor JSON, 생성 응답, 캡처 `20-capture.*`, 필터, 요청 출력, 정리 해시), `k8s-worker01.tgz`(`run-b/` 13개 파일: 이미지 확인, 캡처, 필터, MTU·offload), 내부 `SHA256SUMS` |
| `mtu-path-run01-ansible01-20261007.tgz` | ansible01 `~/`의 단계별 출력 파일과 각 `.sha256` | `a486c0eb4fb5cfdf8d72cb1ca243547c5fba3552a5461621854b189a25386b5c` | 22개 파일: 10/7 13:23 첫 S0 시도(스크립트 없음으로 실패, 서버 미실행), 13:25 S0, 13:26 NO-GO 조회, 14:00 Gate·diff·이미지 확인, 14:04 생성, 14:05 캡처·요청, 14:06 정리 |

- 서버 묶음 해시 `a569a766…`은 ansible01 계산값과 PC 복사본 재계산이 일치한다. 내부 `SHA256SUMS`(control01·worker01 묶음 2/2)와 ansible01 묶음의 sidecar **11쌍 모두 일치**한다. 묶음 안의 `*.sha256`은 ansible01에서 만든 값이다.
- 전달 경로: 서버 → ansible `tar`/`fetch`(서버 `/tmp`의 임시 tgz는 수집 직후 삭제) → ansible01 → 공유 폴더 → 이 저장소.
- 개인키·`client-key-data`·`dockerconfigjson`·Bearer·password·token 값 패턴을 풀어서 전체 검색했고 일치 0건이다. `4-donor.json`·`10-created.json`에는 Pod spec과 CNI·last-applied annotation이 있으며 자격증명 값은 없다.

## 시험 회차 (2026-10-07 KST)
| 시각 | 사건 |
|---|---|
| 13:25 / 13:26 | S0 사전 확인 **NO-GO**(`probe-w01` `Failed`, 대상 CoreDNS `.119` 부재). 서버 변경 없음 |
| 14:00:00~14:00:51 | 생성 전 Gate: 6/6 Ready, etcd leader `.102`·term 18, 대상 CoreDNS `10.244.246.121`(`k8s-control01`), donor `probe-w01`(uid `f517b3e5-cf61-4a33-8c23-fa25b64072ce`, `Failed`), 후보 JSON sha256 `59daf411…`, server dry-run rc=0(차이는 ServiceAccount 토큰 볼륨·마운트뿐), worker01 이미지 `quay.io/calico/node@sha256:c061070a…` `crictl inspecti` rc=0 |
| **14:04:17** | `icr39-probe/mtu-client-w01` 1회 `create` rc=0, **UID `55a98b1a-f37d-48da-8252-02a4f3720cf9`**, 14:04:20 Running, `k8s-worker01`, IP `10.244.79.111`, command `sleep infinity` |
| 14:05:11 / 14:05:12 | 양쪽 캡처 시작(`tcpdump -p -nn -vv -s 128 -tttt -l`, 60초, 같은 필터 파일), worker01 PID 929199 / control01 PID 1651085 |
| **14:05:15** | 작은 요청 1회(응답 176자 `404`), 큰 요청 1회(`X-Pad` 20,000자, 응답 29,674자 `200 OK`), 둘 다 rc=0 |
| 14:06:08 / 14:06:12 | 캡처 종료(`timeout` rc=124, 60초 만료) |
| **14:06:44** | **UID 결속 삭제 rc=0**, `get pod` **NotFound**. 사후 Gate: 6/6 Ready, etcd 3 member·leader `.102`, CoreDNS 2개 Running |

## 관측 (판정 아님)
PC에서 `20-capture.txt` 두 파일을 다시 계산한 결과이며 서버 보고와 같다.
| 라벨 | 값 | 비고 |
|---|---|---|
| `ENCAP_UDP4789` | **NOT_OBSERVED** | 양쪽 85줄 중 `VXLAN`·`4789` 포함 줄 0. 필터 범위(IPv4·inner IHL5 등) 안의 결과이며 "항상 비캡슐화"로 확대하지 않음 |
| `SYN_MSS` | **1410** (양쪽, SYN 줄 4개) | |
| 호스트 관측 TCP payload 최대 | **8998**(IP 총길이 9050), 양쪽 동일. 1410을 넘는 payload 줄이 10개(control01 2796·4096·4194·6990·8388·8998, worker01은 2698·4661 추가) | **TSO/GSO/GRO가 묶은 호스트 관측치**이며 선로 MTU·PMTU 증거가 아님. 캡처에 `cksum incorrect`가 보이는 것도 checksum offload와 부합 |
| 링크 MTU | control01·worker01 `ens160` 1500, `vxlan.calico` 1450, `veth_mtu=1450`, IPPool `vxlan=CrossSubnet`·`ipip=Never`, 양쪽 offload on(변경 없음) | |
| 캡처 통계 | worker01 42/42/drop 0, control01 42 captured·**43 received by filter**·drop 0 | control01의 1건 차이는 종료 시점의 차이로 보이며 원인을 확정하지 않음 |
| 필터 | 두 노드의 `20-filter.txt`가 바이트 동일. client `10.244.79.111`, server `10.244.246.121`(`SERVER_HEX=0x0af4f679`) | 권욱님 6030613770의 좁은 필터 구조 |

## 한계
1. 6대 노드가 모두 `10.1.93.0/24`이고 `vxlanMode=CrossSubnet`이어서 이 흐름은 **VXLAN으로 캡슐화되지 않았다.** 따라서 **캡슐화 경로의 1450과 DF/PMTU는 확인하지 못했다.**
2. 최대 payload 8998은 offload로 묶인 호스트 관측치다. 실제 wire 길이·PMTU를 보여 주지 않는다. offload는 끄지 않았다.
3. `ENCAP_UDP4789=NOT_OBSERVED`는 필터가 잡는 형식(IPv4, inner Ethernet/VLAN 없음, inner IHL5) 안에서만 의미가 있고 다른 형식·truncation은 NOT_VERIFIED다. `-s 128`은 앞 128바이트만 저장하는 제한이다.
4. 링크 MTU는 control01·worker01만 조회했다(GO 범위). 나머지 4대는 조회하지 않았다.
5. 클라이언트는 `probe-w01`(`Failed`, kubectl `Unknown`) spec을 복제한 새 Pod다. 이 시험으로 10/1 증적(evidence#83)의 재현성을 판단하지 않는다. `icr39-probe` Pod 4개(evidence#83이 쓰던 Pod 포함)는 이 시험 시점에 모두 `Unknown`이었다.
6. 같은 환경·같은 흐름 구조(클라이언트 Pod → CoreDNS TCP 9153 `/metrics`)이나 클라이언트·서버 Pod가 다르므로 evidence#83과 값을 같은 측정으로 합치지 않는다.
7. 10/7 13:23 첫 S0 시도 파일(`mtu-s0-c01-…T132311`)은 `mtu-s0.sh`가 없어 ansible이 실패한 기록이며 서버에서 실행되지 않았다.
8. 서버 쪽 셸 history와 명령 입력 원문은 파일로 없다. 실행한 스크립트 내용은 #10 기록과 단계별 출력의 명령줄로 확인한다.
9. 독립 검토 전이다. 이 편입은 AC 인수나 티켓 종결을 뜻하지 않는다.

AI usage: CLAUDE_CODE_ASSISTED.
