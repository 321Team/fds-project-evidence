# P1-K8S-01 T19 노드별 복구 시험 재시험 `t19-run02` — worker01, 2026-10-02

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) AC "…복구…" 항목의 시험(T19, `k8s-worker01` 대상)을 **새 시험 회차 `t19-run02`** 로 다시 실행한 기록이다. 같은 날 먼저 시도한 회차는 사전 합의한 중지 조건으로 중단됐고 그 기록은 별도 PR([evidence#102](https://github.com/321Team/fds-project-evidence/pull/102), `evidence/P1-K8S-01/t19-attempt-20261002/`)에 있다. **이 폴더의 파일과 그 회차의 파일·receipt는 섞지 않았고 승계하지 않았다.**

**이 문서는 T19 PASS나 AC 충족을 주장하지 않는다.** 아래는 실행자(이하영, 작성 보조 Claude Code)의 관측 기록이며 판정은 검토자와 Lead가 한다.

## 자료 구분

세 압축 파일은 **서버에서 만든 원본 묶음**이다(`CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`가 아니다). 서버에서 `sha256sum`으로 계산해 보고한 값과, 공유 폴더로 옮긴 뒤 이 PC에서 다시 계산한 값이 일치한다. 압축은 풀지 않은 채 보관하고 `.sha256` sidecar와 `registry/ARCHIVE_CONTENTS.json`으로 고정한다.

| 파일 | 만든 곳 | SHA-256 (서버 보고값 = 이 폴더) | 내용 |
|---|---|---|---|
| `t19-run02-control01-final.tgz` | control01 `/root/t19-run02-20261002` | `1d76a5b58059908eb41bba30a0ffa4df2c8d61506a6978f76bdcf061ade173db` | 시작 직전 점검, 기준선(시험 전·최종), state·bundle SHA 목록, run-meta, receipt(`NOT_REVIEWED` 백업·`PROTECTION_RESTORED_REVIEWED`), 3-5·원복 출력, 3-6·가드8 결과, 앱 Pod 감시 로그, MON 시험 전·후, 하위 증적 tgz 2개, `RUN02_FINAL_SHA256SUMS` |
| `t19-run02-worker01-final.tgz` | worker01 `/var/log/fds-evidence/P1-K8S-01/t19-run02-20261002` | `24240cdd96f4ddf66ca338e384eff305c8788d4e4c0c48738e241589660e33c7` | firewalld 복원 전·후·OFF, 기준선, 단계별 nft/iptables 스냅샷(전·후), tcpdump 4종 |
| `t19-run02-ansible01-final.tgz` | ansible01 홈 | `4d84a5d74ba336537cdf75780edeac033f059baa5cbe28716f7df2f613a06489` | 접속·Negative 시도 기록 5개, 수집 기록 |

전달 경로: 서버 → ansible `fetch`/`tar` → ansible01 `~/t19-run02-final/`(2026-10-02T21:33 KST) → 공유 폴더 → 증적 저장소. 암호·토큰·키 값은 묶음에 없다(압축을 풀어 키워드 검색으로 확인).

## 회차 식별 ([권욱 A안 수용](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5950943151))

| 항목 | 값 |
|---|---|
| `T19_RUN_ID` | `t19-run02` (새 기준선·receipt 파일명·증적 폴더·로그 경로에 사용) |
| `CONFIG_ATTEMPT_ID` | `gate2-attempt01` (현재 클러스터에 적용된 bundle/state의 identity, **변경하지 않음**) |
| cluster_uid / config_sha256 | `e1669cff-1435-423f-a6c4-28bc44f488de` / `b42e7e80590ac6fb03e1934499c3f0ceeeab33557ecdf3033c3e206936c8ec43` |
| 도구 | `/opt/fds/P1-K8S-01-v4/code/cluster-change.py` sha256 `e955a6f981dbcdc3acac1e97dcecca498f4441e23e6c7ae64bbfb4788f2df162` (infra-kubernetes main `7329bf2`, #52 병합본, 10/2 14:58:36 반영) |
| 원본 state/bundle | `/var/lib/fds/P1-K8S-01/gate2-state.json`(파일 30개), `/root/generated-gate2-attempt01`(파일 21개) — **전체 SHA-256 목록을 보존**(`canonical-sha/state.sha256`·`bundle.sha256`)하고 시험에서 읽지도 쓰지도 않음 |
| run02 작업본 | `/var/lib/fds/P1-K8S-01/t19-run02-state` — 원본과 **전체 파일 SHA-256 일치**(`STATE_COPY_IDENTICAL`) 확인 후 도구는 이 작업본만 사용 |
| 실행자·입회 | 이하영(K8S/SEC Lead). 검토 Review Owner 권욱 |

### 승인과 Gate (모두 #10)
- A안 수용: [5950943151](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5950943151)
- MON 방식 ②·Full T19 사전승인: [5951768037](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5951768037)
- 실행자 Gate 확인: [5951837779](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5951837779)
- 3-4 receipt 승인(`PROTECTION_RESTORED_REVIEWED`, 3-5 진입): [5952074346](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5952074346)
- 종료 보고: [5952375659](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5952375659)

## 실행 기록 (KST, 서버 원본 파일 기준)

| 시각 | 단계 | 결과 | 파일 |
|---|---|---|---|
| 20:02~20:03 | 새 기준선(재부팅 후, 시험 전) | 노드 6/6 Ready, readyz passed, worker01 bootID `ba183c9b-1ddb-4302-a86d-8176674525f5`, firewalld disabled/inactive, 앱 Pod 재시작 3·4 | `fresh-baseline-*.txt` |
| 20:43 | MON 시험 전 | 23/23, `up==0` 없음 | `mon-pre/` |
| 20:57:56 | 시작 직전 점검 | 노드 6/6, readyz passed, bootID 일치, 앱 3·4 | `pre-start-check.txt` |
| 20:58:55 | **3-1 방화벽 선복원** | `FIREWALL_CONFIG_RESTORED_TRAFFIC_TEST_REQUIRED`, firewalld enabled/active, 10250은 CP `.102/.103/.104`만 허용 | worker01 `01-`·`02-`·`03-*.txt` |
| 21:00:36 | Positive control01 → worker01:10250 | **OK** | `matrix-cp-restore.txt` |
| 21:01:05 | 승인 SSH(ansible01 → worker01) | **pong** | `run02-ssh-after-restore.txt` |
| 21:03:18 | **Negative** edge01(10.1.93.50) → 10250 | **FAIL**, SYN 5·SYN-ACK 0·RST 0 | `run02-matrix-edge-restore.txt`, `neg-edge-10250.txt` |
| 21:17~21:19 | 3-5 직전 자체 확인, receipt 갱신 | 확인 통과, receipt `NOT_REVIEWED`→`PROTECTION_RESTORED_REVIEWED` | `pre-3-5-selfcheck.txt`, receipt |
| 21:19:58 | **3-5 `rollback-node`** | `CALICO_RESTORED_TEST_REQUIRED`, rc=0, worker01 HEP·node Felix 삭제 | `3-5-rollback-node.txt` |
| 21:20~21:22 | **3-6 복구 판정** | 다른 5대 HEP/GNP/Felix 동일, Positive OK, ssh pong, Negative FAIL(즉시 거절, SYN 1), chrony·DNS 정상 | `3-6-*.txt`, `run02-matrix-edge-after-rollback.txt`, `rb-*` |
| 21:23~21:24 | 원복: Felix 재생성(가드3~5), HEP 재생성(가드6) | absent 확인, dry-run→create, `FELIX_INTENDED_MATCH`, `HEP_CREATED_AND_ENFORCING` | `4-felix-recreate.txt`, `5-create-hep.txt` |
| 21:24:55 | HEP + firewalld 상태 Negative | FAIL, SYN 5·무응답 | `run02-matrix-edge-after-reapply.txt`, `re-*` |
| 21:26:49 | 가드7: **firewalld OFF** | `UnitFileState=disabled`, `ActiveState=inactive` | worker01 `6-firewalld-off.txt` |
| 21:27 | 가드8: firewalld OFF 후 | Positive OK, ssh pong, **Negative FAIL**, SYN 5·SYN-ACK 0·RST 0 | `7-after-firewalld-off-control01.txt`, `run02-matrix-edge-after-off.txt`, `off-*` |
| 21:28~21:30 | 가드9: 최종 기준선 비교 | 아래 "확인한 사실 3" | `final-baseline-control01.txt`, worker01 `8-final-worker01.txt` |
| 21:30:16 | MON 종료 후 | 23/23, 시험 전과 목록 동일 | `mon-post/` |
| 21:32:49 | 종료 처리 | 감시 종료, 최종 해시 목록 생성 | `run02-end.txt`, `RUN02_FINAL_SHA256SUMS` |

## 확인한 사실

1. **방화벽 복원이 앱 Pod 재시작을 일으키지 않았다.** 앱 Pod 감시 로그(`restart-watch.txt`, 5초 간격 347건, 20:58:36~21:32:44)에서 `node=Ready`, `boot=ba183c9b`, `fds-engine-5699669f6f-bp6t6` 재시작 3, `transaction-api-b784c8c5d-rq9b6` 재시작 4가 **전 구간 일치**하고 이상 줄이 0건이다. 방화벽 복원(20:58:55), 3-5, HEP 재생성, firewalld OFF 모두 이 구간에 있다. 10/2 먼저 시도한 회차의 앱 Pod 재시작은 방화벽 복원이 아니라 시험 직전 재부팅이었다는 정정은 evidence#102 README에 있다.
2. **승인 경로는 전 구간 유지됐다.** 모든 단계에서 ansible01 → worker01 SSH `pong`, control01 → worker01:10250 `OK`.
3. **최종 기준선(시험 전 20:02 대비)**: 노드 bootID diff 없음, 다른 5대 노드의 HEP·GNP·Felix UID·generation 동일, **worker01의 HEP·node Felix만 새 UID**(HEP `aa7effb8-d409-4da5-ab84-6a066ac5036b` → `f650c589-5261-4566-a186-606440cc304a`, Felix `42e72ba0-5a5e-421a-b25a-97c152800292` → `f85d9eb8-d095-4e53-8117-e5cbeef95a5e`, 둘 다 generation 1). worker01 GNP는 gen 4 그대로. readyz passed, 앱 3·4, 9100 FAIL·10250 OK(시험 전 기준과 같음), firewalld disabled/inactive.
4. **Felix 재생성**: 번들 `felix/k8s-worker01.json` spec 그대로 생성(manifest sha256 `0eec62b2cc0238dad810b62148a9d09452f76c5302f3e69bc107767314a1b7d6`), live spec은 번들 필드와 일치(`FELIX_INTENDED_MATCH`)하고 API 기본값 `nftablesMode`가 추가됐다.
5. **receipt**: `NOT_REVIEWED`(sha256 `8d9fe9d9766553de2305436d55b497fcbd3ab36e8ce3fddb89ddc49acc29b415`, `…NOT_REVIEWED.json`에 보존) → 권욱 승인 후 `status`와 `reviewer_reference`만 갱신한 `PROTECTION_RESTORED_REVIEWED`(sha256 `c7328f74af3fe24886c25fb0ee8368f3a1ab5b82a9e67308dc8883c8b18abd20`). `node`·`cluster_uid`·`attempt_id`·`config_sha256`·`evidence` 3건은 변경하지 않았다. `attempt_id`는 도구 규칙에 따라 `gate2-attempt01`이다. 10/2 먼저 시도한 회차의 receipt·증적 목록은 승계하지 않았다.
6. **MON**: 시험 전(20:43) 23/23, 종료 후(21:30) 23/23, `up==0` 없음, `up-targets.txt` 두 시점 동일(sha256 `c75cfcd1230747ccac942d20d2b58282b2bf7ad68d7a0814fc70faff33c2ef49`). 18:09 목록 대비 차이는 재부팅에 따른 앱 Pod instance 2건(`.99`→`.104`, `.100`→`.105`)뿐이다.

## Negative 4회 요약 (edge01 → worker01:10250, 모두 worker01 `ens160` 캡처)

edge01(10.1.93.50)은 worker01 TCP 10250 허용 Source가 아니다(권욱 검토 [5952074346](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5952074346)).

| 상태 | 결과 | SYN 도달 | SYN-ACK | RST | 형태 |
|---|---|---|---|---|---|
| firewalld만 복원 + HEP 있음 (21:03) | FAIL | 5 | 0 | 0 | 무응답 재전송 |
| HEP 삭제, firewalld만 (21:21) | FAIL | 1 | 0 | 0 | **즉시 거절**("호스트로 갈 루트가 없음") |
| HEP 재적용 + firewalld (21:24) | FAIL | 5 | 0 | 0 | 무응답 재전송 |
| **HEP 재적용 + firewalld OFF (21:27)** | FAIL | 5 | 0 | 0 | 무응답 재전송 |

Calico DROP counter(`iptables-save -c`의 `cali-pi-_IZ_dpYgvbSNCZTvi1r- … -m mark --mark 0x40000/0x40000 -j DROP`) 전·후: 방화벽 복원 단계 91→124(+33), HEP 삭제 단계는 해당 규칙 없음, HEP 재적용 단계 13→44(+31), firewalld OFF 단계 12→19(+7).

## 해석과 한계

1. **차단 지점**: HEP를 지우면 edge01이 firewalld의 즉시 거절을 받고(SYN 1), HEP를 다시 만들면 조용히 버려진다. 마지막 단계는 **firewalld가 꺼진 상태에서 HEP만으로** 막혔고 같은 시간 Calico DROP counter가 +7 올랐다(edge01 SYN 5개 이상). 이를 근거로 최종 상태의 Negative는 Calico HEP/GNP 차단으로 본다. **앞 단계(firewalld와 HEP가 함께 켜진 시점)의 Negative는 `ENFORCEMENT_POINT=NOT_ATTRIBUTED`** 이며 counter 증가량은 edge01 SYN보다 커서 다른 트래픽이 섞여 있다. 단일 시도의 관측이며 방화벽 단독 차단 등을 주장하지 않는다.
2. **감시 기록 공백**: 20:59:18~21:00:13(55초), 21:01:21~21:05:11(230초). 실행자의 `^C`와 명령 오류(백그라운드 감시의 리다이렉트 권한 오류, 21:02:42 시도 실패)로 생겼다. 공백 직후 스냅샷은 모두 3·4였다(`restart-watch.txt` 주석 줄).
3. **MON 구간 값 없음**: 방화벽 복원~3-5 구간 중 worker01 `9100` 수집 상태는 수집하지 않았고 시험 전·종료 후 값만 있다(방화벽에 9100 허용이 없어 이 구간 수집 중단이 예상됨).
4. **MON 수집자**: 시험 전·후 MON 값은 MON Lead가 아니라 Support(이하영)가 control01에서 같은 방법으로 읽기 전용 수집했다. MON Lead 사후 확인은 [#22](https://github.com/321Team/fds-project-baseline/issues/22)에 요청했다.
5. **`RUN02_FINAL_SHA256SUMS`의 `run02-wrapup.txt` 항목은 불일치**한다. 이 파일은 같은 명령에서 `tee`로 쓰이는 중에 해시됐기 때문이며 나머지 45개 항목은 모두 일치한다(이 PC에서 확인).
6. **receipt는 검토자 확인 후 갱신**한 것이며, receipt의 `reviewer_reference` 필드는 도구 검증 필수 필드가 아니다(도구가 `node/cluster_uid/attempt_id/config_sha256/evidence`만 검사). 도구 검증은 3-5에서 통과했다.
7. **증적 목록 `evidence` 3건**(`evidence/t19-run02-w01-evidence.tgz`, `evidence/t19-run02-ansible01-evidence.tgz`, `matrix-cp-restore.txt`)은 3-4 시점의 중간 묶음이며, 이후 단계(3-5~가드9)의 기록은 receipt에 바인딩되지 않았다.
8. 실행 전 점검에서 `probe-w01`은 5일 전부터 `Unknown` 상태여서(10/2 먼저 회차 기준선에서도 같음) 이번 시험에서 쓰지 않았다.
9. 이 증적은 단일 시험 회차의 관측이다. 세부 재현성(반복 시험)이나 다른 노드에 대한 일반화를 주장하지 않는다.

## 판정 경계

- `T19_RUN02_EXECUTION = COMPLETED_NO_STOP_CONDITION` (실행자 관측)
- `POD_RESTART_AFTER_FIREWALL_RESTORE = NOT_OBSERVED` (감시 347건, 공백 2구간)
- `FINAL_STATE = CALICO_PROTECTION_ONLY / FIREWALLD_DISABLED / HEP_GNP_FELIX_REAPPLIED` (최종 기준선 대조)
- `ENFORCEMENT_POINT = NOT_ATTRIBUTED` (방화벽+HEP 병행 단계), 최종 firewalld OFF 단계는 Calico 차단 정황
- **T19 최종 PASS, AC "복구" credit, #10 종결은 이 문서가 판정하지 않는다.** 검토자·Lead가 증적을 보고 판단한다.

## 검토 상태

AI 세션(Claude Code)의 편입 작성이며, `governance/EVIDENCE_POLICY.md`의 독립 검토는 아직 없다. 서버 원본 내부 파일(특히 worker01 nft/iptables counter, tcpdump 원본, receipt 내용)은 검토자가 압축을 풀어 확인해 주기 바란다.
