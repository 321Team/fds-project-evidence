# P1-K8S-01 `t19-cp02-run01` — control02 CP 보호 복구 시험(AC4)·OFF 진단 기록, 2026-10-06

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10)의 AC4(CP 노드 방화벽·Calico HostEndpoint 보호 복구) 시험 `t19-cp02-run01`(대상 `k8s-control02` `10.1.93.103`, attempt `gate2-attempt01`)의 **서버 원본 묶음과 실행자 기록**입니다.

**이 문서는 어떤 AC의 PASS·충족도 주장하지 않는다.** 판정과 인수는 검토자와 Lead가 한다. 첫 OFF 상태 Negative는 **FAIL**이며 T19/AC4는 HOLD, #10 Close는 승인되지 않았다.

## 자료 구분

두 압축 파일은 서버·ansible01에서 만든 **원본 묶음**이다(재구성 사본이 아니다). 암호·토큰·키 값은 묶음에 없다(PC에서 `dockerconfigjson`, 개인 키 헤더, `password`·`token`·`Authorization`·`client-key-data`·API key 패턴을 전체 검색했고 일치 0건).

| 파일 | 만든 곳 | SHA-256 | 내용 |
|---|---|---|---|
| `cp02-ansible01-evidence-20261006.tgz` | ansible01 `~/` (`cp02-*20261006*`) | `f683177c42063ac2fa03b1c85f8fecdbcd41723a002bb43afcc0311fcc11e6eb` (PC 복사본 기준) | 단계별 실행 출력과 각 `.sha256`: 도구·render 복원, 시작 직전 Gate, T0~3-6, 원복, firewalld OFF, 첫 OFF Negative, 진단 1~4, attempt02, 최종 기준선, 감시 종료. 내부 `.sha256` 37쌍은 PC에서 모두 일치 확인 |
| `cp02-server-originals-20261006.tgz` | ansible01이 control01·control02·edge01에서 `tar`/`fetch`로 수집 | `16d4f54b3a30ca3e447c31de42bef6d790e96b3169f46a0ea3aefbe2ab17bf0a` (ansible01 계산값과 일치) | `control01-originals.tgz`(`/root/t19-cp02-run01-20261006`: receipt·감시·health·rollback/recreate 출력), `control02-originals.tgz`(`/var/log/fds-evidence/P1-K8S-01/t19-cp02-run01-20261006`: tcpdump·firewalld 출력·attempt02 폴더), `edge01-attempt02.jsonl`, 이들의 `SHA256SUMS` |

- 전달 경로: 서버 → ansible `tar`/`fetch` → ansible01 → 공유 폴더 → 이 저장소.
- `cp02-server-originals-20261006.tgz.sha256`은 ansible01에서 계산한 값이며 이 폴더의 파일과 일치한다. `cp02-ansible01-evidence-20261006.tgz.sha256`은 **PC에서 계산한 값**이다(원래 파일명 `cp02-evidence-20261006.tgz`를 이 저장소에서 위 이름으로 바꿨다).
- `cp02-ansible01-evidence-20261006.tgz`의 해시는 서버에서 출력한 값을 가지고 있지 않아 PC 복사본 기준이다. 이 묶음 안의 `cp02-evidence-20261006.tgz`(0바이트, 파일명 패턴이 겹쳐 자기 자신이 포함됨)와 그 `.sha256`은 의미 없는 항목이며 검증에 실패한다. 나머지는 모두 일치한다.
- 서버 원본 묶음 안의 `7-drop-c0/c1/c2.txt`(control02)는 **0바이트**다. 첫 OFF 상태 Negative에서 카운터 저장이 비어 있었다는 사실이며 값 0을 뜻하지 않는다.

## 회차 식별

| 항목 | 값 |
|---|---|
| 도구 (고정 커밋 `b4303f2df512a8791d2421203cf159567d076b2a`, `321Team/infra-kubernetes` `ops/p1-k8s-01-v4`) | `RUNBOOK_FINAL.md b5388dc5…`, `cluster-change.py e955a6f9…`, `node-evidence.py 8ce58544…`, `render.py c640831e…` (복원 보고 [6009072708](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6009072708), 승인 [6009176490](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6009176490)) |
| 실제 T0 | 2026-10-06 14:40:29 KST (첫 방화벽 변경 `restore-firewall`) |
| 5초 감시 | 14:38:55 ~ 15:51:44, 데이터 782줄, `LEADER_CHANGED_OR_UNKNOWN` 0 |
| 승인·판단 | [계획 5979416203](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5979416203) · [GO 5979476603](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5979476603) · [GO 재확인 6010041894](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010041894) · [시작 기록 6010108406](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010108406) · [T0 6010138462](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010138462) · [검토 요청 6010214492](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010214492) · [receipt 승인 6010511558](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010511558) · [STOP 보고 6010743768](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010743768) · [Felix 로그 6010763095](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010763095) · [Pod 노드 6010777720](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010777720) · [1회 승인 6010822688](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010822688) · [실행 가이드 6010911166](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6010911166) · [최종 보고 6011043599](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6011043599) |

## 시간순 관측 (판정 아님)

| 시각(KST) | 단계 | 관측 (원본) |
|---|---|---|
| 14:40:29 | 3-1 `restore-firewall` | control02 `3-1-restore-firewall.txt`: `FIREWALL_CONFIG_RESTORED_TRAFFIC_TEST_REQUIRED; keep HEP until protective rules/tests are reviewed` |
| 14:41~14:45 | 3-2 Positive, 3-3 Negative | `cp02-3-2-positive-…T144143`, `cp02-3-2b-3-3-…T144325`, `cp02-3-3-negative-…T144510` |
| 14:58~15:06 | 3-4 receipt·검토 | receipt `NOT_REVIEWED` 작성, 검토 요청 후 승인 댓글 기준으로 갱신(`k8s-control02-protection-receipt.json` `PROTECTION_RESTORED_REVIEWED`, `.NOT_REVIEWED.json` 보존) |
| 15:14 | 3-5 `rollback-node` | `cp02-3-5-rollback-…T151427`, control01 `3-5-*` |
| 15:15 | 3-6 복구 판정 | `cp02-3-6-…T151548` |
| 15:17 | 원복 | Felix 재생성·`create-hep`(`cp02-4-5-recreate-…T151737/T151750`, control01 `4-*`, `5-*`), `cp02-5b-hep-fw-negative-…T151751` |
| 15:21:16~17 | firewalld OFF | `cp02-6-off-…T152115`: disabled/inactive, 새 SSH 연결 ok, OFF 상태 Positive `c01_to_c02:6443/10250 … OK` |
| **15:22:30** | **OFF 상태 Negative (첫 시도)** | **`CONNECTED`×3** (6443/10250/2379), DROP 카운터 스크립트 값 0 → **FAIL**, STOP (`cp02-7-off-negative-…T152215`) |
| 15:24~15:29 | 읽기 전용 진단 1~4 | `cp02-stop-diag-…T152444`, `diag2-…T152603`, `diag3-…T152742`, `diag4-…T152918` |
| 15:46~15:48 | **attempt02 (별도 진단 1회)** | 아래 |
| 15:49:54 | 최종 기준선 | `cp02-final-gate-…T154954`, `cp02-final-mon-…T154954` |
| 15:51:44 | 감시 종료 | `cp02-watch-end-…T155140`, control01 `restart-watch.txt` |

### 첫 OFF 상태 Negative와 Felix 로그 (diag4)
- 15:23:14 KST(로그 UTC `06:23:14`)에 control02의 calico-node(Pod `calico-node-bp7jz`, 노드 `k8s-control02` 확인)가 `Detected out-of-sync Calico chain, marking for resync`를 `cali-INPUT`, `cali-from-host-endpoint`, `cali-fh-ens160`, `cali-failsafe-in` 등 다수 체인에 출력했고, `INPUT` 체인은 Felix가 기대한 규칙 `Cz_u1IQiXIMmKD4c`가 없는 상태(`actualRuleIDs`에 없음)로 감지됐다.
- 이는 firewalld OFF 이후 Calico 규칙이 재적용된 근거일 수 있으나, **규칙이 실제로 빠진 시점·15:22:30 당시 INPUT 상태·복구 완료 시각은 확정하지 못했다**(원인 확정 아님).

### attempt02 (`off-negative-diag-attempt02`, 원본: control02 `off-negative-diag-attempt02/`, edge01 JSONL)
- 승인된 별도 진단 1회: edge01(`10.1.93.50`) → control02 `6443/10250/2379` 새 TCP 연결 각 1회, timeout 5초. 모두 `TIMEOUT`(15:47:16~31), source 포트 `59429/35079/47601`.
- tcpdump(control02 `ens160`): 위 tuple의 SYN 15개(포트당 5, 1초 간격 재시도)만 도착, 같은 tuple의 SYN-ACK·RST 0, `15 packets captured / 15 received / 0 dropped by kernel`. capture 구간 15:47:12~15:48:12, `CAPTURE_RC=124`(`timeout` 정상 종료).
- 해당 deny 규칙(`cali-pi-_11qIE40BCFHOuO0csFl`, `cali:tizFkLOu9UxtkEst`) 카운터: before `[725:57899]`(15:46:15) → after `[823:65822]`(15:48:36), +98. 접속과 무관하게 이 규칙은 이미 증가 중(15:44:10 `[645:50656]` → 15:46:15 `[725:57899]`, +80)이라 **이번 접속으로의 귀속은 INCONCLUSIVE**.
- PC에서 `rules-before.txt`와 `rules-after.txt`를 카운터(`[pkts:bytes]`)와 `# Generated/Completed` 주석을 제외하고 비교했을 때 **538줄 모두 동일**(구조 변경 없음). `input-before/after`는 카운터만 다르다. firewalld는 전후 모두 inactive/disabled.
- 이 결과는 **현재 시점의 차단 관측**이며 첫 실패 해소·연속 보호·T19/AC4 PASS가 아니다.

### 최종 기준선 (15:49:54, 시험 전 14:15:47 Gate와 대조)
etcd 3/3 healthy·leader `10.1.93.102`·term 18, Node 6/6 Ready, readyz 5곳 ok, boot_id 6개 목록 해시 동일(`573954c2e208b022`), Pod 44개 재시작 목록 해시 동일(`42c422b7b9fd011f`), 원본 state 30개 목록 해시 `2a0411a9cf844e776ab31c9adab03e850673ca87fe65944c37d21abbf49146a2` 불변, Calico UID·generation 비교에서 **control02 Felix·HEP 2건만 다름(재생성)**, MON 23/23 up(`up==0` 0, 두 집합 EQUAL, remote_write 실패·재시도·대기 0, Prometheus 시작 13:24:31 유지). 비교 파일: `cp02-gate-control01-…T141546.txt.calico.cmp`, `cp02-final-gate-…T154954.txt.calico.cmp`.

## 한계와 미검증
1. **첫 OFF Negative(15:22:30)는 FAIL**이며 이 폴더의 어떤 후속 관측으로도 대체·합산하지 않았다.
2. 카운터 귀속은 INCONCLUSIVE이고, 규칙 유실 시각과 15:22:30 당시 INPUT 상태는 측정한 원본이 없다.
3. 시험 전 edge01의 control02 도달성은 측정하지 않았다.
4. control02 `7-drop-c0/c1/c2.txt`는 0바이트다(값 0이 아님).
5. 서버 원본 묶음은 ansible01에서 수집했고 control01·control02 안의 개별 파일 해시는 `SHA256SUMS`(attempt02 폴더)와 receipt의 evidence 해시 외에는 서버에서 따로 대조하지 않았다.
6. 최종 보고 시점의 `rules-before/after` 대조(위 538줄 동일)는 이 PR 준비 중 PC에서 한 것이며 #10 최종 보고에는 NOT_VERIFIED로 적었다.
7. 첫 묶음의 해시는 PC 복사본 기준이다.
8. 시험 중 etcd leader 변경, quorum·health·API·boot 이상, 예상 밖 restart·policy drift는 관측되지 않았다(감시 782줄 상태 1종). 이는 AC 충족 판정이 아니다.

AI usage: CLAUDE_CODE_ASSISTED.
