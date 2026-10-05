# P1-K8S-01 `ac-net-run01` — Pod/Service 통신·DNS·UDP4789·TCP179 시험 기록 (A′ 재시험 포함), 2026-10-05

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10)의 AC "Calico/CoreDNS 정상", "Pod/Service DNS와 Cross-node Pod 통신 PASS", 핵심 요구 "UDP 4789 중심 Port Matrix, TCP 179/IPIP 기본 미허용"의 잔여 증적을 얻기 위한 `ac-net-run01` 시험의 **실행자 관측 기록**이다. 같은 날 세 번 실행했다(1차·Y′ 재현은 Pod 시작 실패로 중단, A′ 재시험은 통신 시험 수행).

**이 문서는 어떤 AC의 PASS·충족도 주장하지 않는다.** 판정과 인수는 검토자와 Lead가 한다. 코드 병합·Pod Ready·모의 시험은 AC PASS가 아니다.

## 자료 구분

세 압축 파일은 **서버에서 만든 원본 묶음**이다(`CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`가 아니다). 암호·토큰·키 값은 묶음에 없다(복사한 pull secret의 값·base64·해시는 어떤 로그에도 출력하지 않도록 만든 코드이며, 묶음의 `secret-*.err` 4개는 0 byte다).

| 파일 | 만든 곳 | SHA-256 (이 폴더) | 내용 |
|---|---|---|---|
| `acnet-ctl-originals-20261005T152149.tgz` | control01 `/root` (`ac-net-run01`, `…-attempt1-…`, `…-attempt2-…`, `acnet-start-check-*`) | `9728e390ba7153ae0edac4df23f834ee1213205dc286eb81e492f661740f485e` | 회차별 기준선·생성·시험·정리 로그, namespace UID, 시작 직전 노드/LB 조회(stdout·stderr·rc 분리) |
| `acnet-w01-originals-20261005T152149.tgz` | worker01 `/var/log/fds-evidence/P1-K8S-01/ac-net-run01` | `b2a2028e22d941c0a3cd021da6039c477ef3df6ca314eff14410d0d82b344ff9` | T14/T15 tcpdump 원본(`t15-edge-capture.txt`), iptables·nft 전후, DROP counter c0·c1·c2 |
| `ac-net-run01-run2-evidence-20261005T152042.tgz` | ansible01 홈 | `65e772888a7f02eebe428b3e5945f1e0886222db547a47bbc8cd3b48d48a0fe3` | 단계별 실행 출력(`acnet1-run2`·`acnet2-run2`·`ac-net-run01-edge`·`acnet9-run2`), Fresh Gate, 전달 해시, 원인 조사 출력, 정리 후 회복 기록 |

- 각 `.sha256`은 ansible01에서 계산한 값이며 이 폴더의 파일과 일치한다(`SHA256SUMS`). **알려진 불일치 1건과 서버 대조 결과:** ansible01 묶음은 만든 직후 서버 출력에 `5aac3d89028a41c47e8d3f28799ccf94b4b07d9705783354c3541a87f4a06758`(22,297 bytes, 15:20)로 보고됐으나 이 폴더의 파일은 `65e77288…`(22,339 bytes)다. 15:3x에 ansible01에서 읽기 전용으로 대조한 결과 **서버의 현재 파일도 같은 `65e772888a7f02eebe428b3e5945f1e0886222db547a47bbc8cd3b48d48a0fe3`(22,339 bytes)이고** 묶음 `tgz`와 `.sha256`의 수정 시각이 모두 15:21:38.17, 묶음 폴더의 `SHA256SUMS`도 15:21:38.17이다. 즉 15:20에 보고된 첫 빌드가 15:21:38에 **같은 방식으로 다시 만들어진 것으로 보이며**(누가 다시 실행했는지, 두 빌드의 +42 bytes가 어디서 왔는지는 확인하지 못했다), 서버 파일과 이 폴더의 파일은 일치한다. 묶음 안 각 파일의 해시는 내부 `SHA256SUMS`와 일치한다. **위험(작성자 판단): 낮음.** 근거: 서버 파일 = 이 폴더 파일 = `.sha256`, 내부 파일별 해시 일치. 남는 것은 첫 빌드(`5aac3d89…`)의 바이트가 보존되지 않았다는 점뿐이다.
- ansible01 묶음 안의 `SHA256SUMS`는 자기 자신을 한 줄 포함해(빈 파일 해시) 그 한 줄만 검증에 실패한다. 나머지 파일은 모두 일치한다.
- 전달 경로: 서버 → ansible `tar`/`fetch` → ansible01 → 공유 폴더 → 이 저장소.

## 회차 식별

| 회차 | 실행 source | T0 → 종료 | namespace UID | 결과 |
|---|---|---|---|---|
| 1차 | `a24f0a23fa6ddb43a58bfc3de612e8677b359fc5` | 13:21:06 → cleanup 13:27:52~13:28:38 | `4bf0a246-34bd-477f-92e5-649269439641` | probe-b·c `ErrImageNeverPull`, `WAIT_RC=1`, STOP, `CLEANUP_COMPLETE` |
| Y′ 재현 | 같음(제한 진단 GO) | **13:58:10** → cleanup 14:01:41~14:02:27 | `a060ad27-9c86-4b54-b35a-f9845898d848` | 같은 실패 재현, 읽기 전용 수집 후 `CLEANUP_COMPLETE` |
| **A′ 재시험** | **`e469761c284e4057e11045307c2177ab1238c938`** (PR #62, merge `98f30c08…`) | **15:08:01** → cleanup 15:13:53~15:14:40, 회복 15:15:28 | `955c51b9-e8d3-4128-8ddc-9c60e687052a` | Pod 3개 Ready, `acnet-2` 수행, `acnet-3` 판정 `NOT_VERIFIED`, `CLEANUP_COMPLETE` |

승인·판단 기록(모두 #10): [STOP 보고](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5988134652) · [Y′ 결과](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5988467389) · [기록 파일 내용·원인](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5988570688) · [Y′ 제한 GO](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5988317167) · [A′ 조건부 GO](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5988933029) · [시작 기록](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5989047645) · [결과 보고](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5989192506) · [PMO/QA 결정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5989234529). 코드: [infra-kubernetes#62](https://github.com/321Team/infra-kubernetes/pull/62)(독립 APPROVED, 병합).

## 실패의 원인 조사 (읽기 전용, 1차·Y′)

- 같은 digest 이미지가 3 Worker에 있고 정확한 reference `crictl inspecti`가 rc=0인데 worker02·03의 kubelet만 `imagePullPolicy: Never` Pod에 `ErrImageNeverPull`을 냈다(worker01은 정상). kubelet·containerd 인자와 설정 해시, CRI endpoint는 같았다.
- worker02·03의 `image_manager/pulled/sha256-e3f8f418…`(= `sha256("sha256:1972a9af…")`) 기록이 이 이미지를 `fds-app/harbor-pull-secret`·`fds-gate2-probe/harbor-pull-secret`으로 받은 것으로 적고 있고 worker01에는 없다(`pulled-record-20261005T141701.txt`, `acnet-cause2/3/4-*.txt`). 시험 Pod에는 secret이 없었다. **원인 후보이며 확정이 아니다.**
- worker01만 containerd 소켓 uid·gid가 1000(`server05`), Harbor CA(`certs.d`)가 있었다(`containerd-cfg-diff-*`, `w01-why-*`, `w01-certs-*`). kubelet·containerd는 3대 모두 root이고 실패 시각 접근 오류는 없었으며(`w-sock-*`) 원인으로 단정하지 않는다.

## A′ 재시험 관측 (판정 아님)

변경(승인된 PR #62): Pod 3개에 `imagePullSecrets`·`imagePullPolicy: IfNotPresent`, `acnet-1`이 `fds-app/harbor-pull-secret`을 시험 namespace로 복사(복사본 1개, 값 비출력, 내부 비교), `acnet-9` 허용 목록에 secret 1개. 원본은 `acnet1-run2-20261005T150801.txt`, control01 `ac-net-run01/`.

| 단계 | 시각 | 관측 |
|---|---|---|
| `acnet-1` | 15:08:01~04 | `secret copy verified`, Pod 3개 Ready(`WAIT_RC=0`), `CREATE_COMPLETE`, `SCRIPT_RC=0` |
| `acnet-2` | 15:10:01~34 | T09: 3개 Pod에서 `kubernetes.default…`→`10.96.0.1`, `kube-dns.kube-system…`→`10.96.0.10`, 없는 이름→`GAIERROR -2`, `quay.io` 해석. T07: Pod IP HTTP 6방향 **6/6 `HTTP 200`**. T08: Service ClusterIP 6 + FQDN 6 **12/12 `HTTP 200`**. `SCRIPT_RC=0` |
| `acnet-3` | 15:11:18~15:12:41 | 스크립트 판정 `CAPTURE=INVALID`, `T14_UDP4789`·`T15_TCP179`·`T15_IPIP`·`COUNTER_ATTRIBUTION` 모두 **`NOT_VERIFIED`**. edge01은 `SUDO_NO`로 raw IPIP를 보내지 못함 |
| `acnet-9` | 15:13:53~15:14:40 | UID 일치, 허용 객체 6개, `delete_rc=0`, namespace NotFound, `leftover=0`, `CLEANUP_COMPLETE` |
| 회복 | 15:15:28 | nodes boot_id 6/6·HEP/GNP/Felix 20/20·fds-app 6/6 restart가 `acnet-1` 기준선과 동일, namespace NotFound, MON `count(up)`·`count(up==1)` 23 |

### T14·T15 보조 관측 (판정을 바꾸지 않음)
캡처 판정이 INVALID인 원인은 `acnet-3`이 캡처 시작 뒤 고정 `sleep 25` 후 `async_status`를 한 번 조회하는데 그 시점에 85초 `tcpdump`(15:12:47 종료)가 끝나지 않았기 때문으로 보인다. 종료 뒤 캡처 원본(`t15-edge-capture.txt`, sha256 `70886fb52724b96d886dcc23006a391dc3701b9b6968c57d4b55d54b78612e07`)은 801줄이며 `794 packets captured / 794 received by filter / 0 packets dropped by kernel`이다(`acnet3-recheck-*.txt`, `…post-run2-…-recount.txt`).
- 시험 시도(15:12:01~06)는 캡처 구간(15:11:22.5~15:12:47.5) 안이고, 같은 구간에 승인된 SSH 대조 패킷(ansible01↔worker01:22)이 335줄 기록돼 있다. 통계 완성과 drop 0만으로 정상 종료·양성 대조·시험 구간 포함을 모두 입증했다고 주장하지 않는다.
- edge01 → worker01:179 SYN 5개가 도착했고 SYN-ACK·RST·ICMP 응답은 0. **SYN 5개는 1회 연결 시도의 재전송일 수 있어 "새 연결 시도 5회"가 아니다.** 응답 미관측은 관측 사실이며 특정 Calico 규칙의 차단 확증이 아니다.
- edge01 → worker01:4789 1개가 도착했고 tcpdump는 `VXLAN (invalid)`로 표시했다. 스크립트의 `udp4789_arrived`는 목적지 4789 뒤 문자열 `UDP`만 세므로 이 형식을 놓친다. 정상 VXLAN 데이터 경로 검증이 아니다.
- DROP counter는 잡음 구간(c0→c1) +3, 시험 구간(c1→c2) +5로 같은 규칙에서 증가해 시험 패킷 귀속이 입증되지 않는다.
- IPIP는 송신하지 못했다(`T15_IPIP=NOT_VERIFIED`, 권한 확대 없음). 승인 범위는 프로토콜별 1회 시도였고 같은 패킷을 다시 보내지 않았다.

## 한계와 정정 (검토자가 알아야 할 것)

각 항목 끝의 "위험"은 **작성자의 판단과 근거**이며 판정은 검토자가 한다.

1. **15:00 시작 직전 기준선 파일은 불완전하다.** `ac-net-run01-start-baseline-20261005T150047.txt`(`417c928e7c4e3936142fc824e2e8aab8a4a3bd323133fc392c7687720f4b1b00`)는 `User interrupted` 6건, Pod 행 0, 1,027 bytes다. 시작 기록에 적었던 "`SECT123_NO_DIFF`·`PODS_NO_DIFF`"(당시 `diff`가 왜 차이 없음으로 나왔는지 설명하지 못함)는 **철회**했고 재사용하지 말 것([정정](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5989192506)). 대체 근거는 `acnet-1`이 15:08:02에 스스로 남긴 기준선과 15:15:28 회복 기록의 대조(boot_id·HEP/GNP/Felix·fds-app)이며 **fds-app 외 namespace의 Pod restart는 시작 시점과 비교하지 못했다.** **위험(작성자 판단): 낮음~중간.** 근거: `acnet-1`은 namespace·Secret·Pod를 만들기 전(15:08:02)에 기준선을 남기며 그 자료는 완전하다(오류 0, boot_id 6/6·HEP/GNP/Felix 20/20·fds-app 6/6을 15:15 기록과 기계 대조, 개수 확인). 15:00~15:08은 시작 직전 노드·LB 조회(15:00:47, rc 0), MON 23, 이미지 직접 조회(15:04)로 보인다. 남는 위험은 15:00 파일이 "차이 없음"으로 잘못 보고된 경위 미상(절차 신뢰)과 fds-app 외 Pod restart 미비교이며, PMO/QA가 이 정정을 [수용](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5989234529)했다.
2. **`acnet-0-precheck.sh`(#61)가 `PRECHECK_FAIL`을 냈으나 오탐이다.** worker의 `crictl` 경고(stderr)가 ansible 출력에서 성공 표시 `ACNET_IMAGE_OK` 바로 뒤에 붙어 한 줄 일치(`grep -Fxq`)가 실패했다(3대 `rc=0`, `exact_marker_lines=0`, `marker_anywhere=1`). 이미지 항목은 직접 조회한 원본(`acnet-gate-manual-20261005T150452.txt`)으로 채웠고 precheck PASS는 근거로 쓰지 않았다. **위험: 낮음.** 근거: 3 Worker의 `rc=0`·성공 표시 존재(`marker_anywhere=1`)와 직접 조회 `inspecti_rc=0`·`digest_rows=1`이 일치하고, precheck PASS를 근거로 쓰지 않았다. 보완 코드는 별도 PR.
3. **실제 T0 15:08:01은 제출한 비중첩 구간(15:10~)보다 2분 일렀다.** 15:08:01~15:10의 동시 작업 유무와 당시 공지·회신 시각은 이 기록으로 확정하지 못했다. **위험: 낮음.** 근거: 15:08:01은 앞서 공지한 "13:20~15:20"(클라우드1조 오후 1:00)과 그 구간 재환 확인(13:10 요청, 회신은 이하영 확인, [시작 기록](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5987973645)) 안에 있고, 그 구간에 #13 AC-03 미시작·MON 17:00 이후·서버 실행 중인 #19 없음으로 기록돼 있다. 다만 새 구간(15:10~17:10) 공지·회신의 정확한 시각은 이 폴더로 확정하지 못했고, 회신 원문은 첨부하지 않았다.
4. A′ 변경(pull secret 복사 + `IfNotPresent`)의 **조합**이 Pod Ready를 만든 것만 관측했다. 두 변경의 개별 인과와 실제 image pull 발생 여부는 확인하지 않았다. **위험: 낮음.** 근거: 인과를 주장하지 않으며 Pod Ready는 AC PASS가 아니다. 통신 시험의 입력(Pod 3개 Ready)을 얻었다는 사실만 기록했다.
5. 캡처 job(`j863296593517.1652805`)의 최종 async 상태는 15:29:55에 읽기 전용으로 회수했다: `finished=1`, **`rc=0`**, 시작 15:11:22.513992, 종료 15:12:47.536386, `delta 0:01:25.022`(ansible01 `~/acnet3-asyncstatus-20261005T152955.txt`, sha256 `026005adc923daf9d4ff03ad3675f146f2d15ee80e9b9b10092baf5d49033499`). **이 파일은 이 폴더의 묶음에 들어 있지 않고** 실행자가 콘솔에 붙인 출력으로 확인한 값이며(`CONSOLE_SUBMITTED`) 서버 원본 편입은 후속이다. 스크립트 판정(`CAPTURE=INVALID`)은 바꾸지 않았다. **위험: 낮음.** 근거: `finished=1`·`rc=0`·종료 15:12:47.536이 캡처 파일 수정 시각(15:12:47.5)·tcpdump 통계(0 dropped)와 일치한다. 빠진 것은 서버 파일의 편입뿐이다.
6. 시작 전 읽기 전용 기록 묶음(`ro-evidence-20261005`)은 이 PR에 넣지 못했고 후속으로 편입한다.
7. 서버 원본 해시를 편입자가 독립 재계산한 것은 이 폴더 안의 `.sha256`과 파일 일치까지이며 서버 원본과의 일치는 서버 보고값에 의존한다.

AI usage: CLAUDE_CODE_ASSISTED (작성 보조). 실행자 이하영(P1-K8S-01 Lead).
