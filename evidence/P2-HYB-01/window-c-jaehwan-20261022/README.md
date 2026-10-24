# P2-HYB-01 — 창 C 재환 몫 원본: G·W0·A2-ON/OFF·A4 회귀·녹화·ROSA 관측 (2026-10-22 KST)

- 책임: [baseline#47](https://github.com/321Team/fds-project-baseline/issues/47) (P2-HYB-01 Hybrid DB / Registry Integration) 창 C 재환 몫 · Lead 이재환
- 대상: db01 `10.1.93.55`, ROSA HCP `fds-rosa-hcp` (cluster ID `2th4q1q4qf7ra35862s1u9q7f6n0vnmc`), `fds-app` namespace
- 경로: VPN_RUN `20261022T1500`(창 B 유지), DB_RUN **`20261022T2038`**(infra-db `57f050ef`, `db01-rosa.sh` `3f7f95f6…70d8`·`apply.sh` `c893d058…b245`)
- 원본 출처: db01 파일은 db01에서 묶은 `db01/windowC-db01-20261022T2038.tgz`를 scp로 받은 것이고, PC 파일은 재환 PC에서 만든 것이다. 두 묶음을 `p47-windowC-20261022.tgz` 하나로 반출했다([6355690272](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6355690272)).
- 이 폴더의 파일은 위 묶음을 풀어 **바이트 그대로** 옮긴 것이다(재압축 없음). 2026-10-24에 로컬 사본과 공유 폴더 사본을 다시 해시해 `8eb86b92…9cca` 일치를 확인했다.
- 하영 몫(SA pull 연결·S·D·restart·C-STOP)은 [`evidence/P2-ROSA-01/window-c-hayeong-20261022/`](../../P2-ROSA-01/window-c-hayeong-20261022/README.md)에 있다.

## 기록 연결

| 단계 | GitHub 기록 |
|---|---|
| 수동 C 변경 GO / 통합 GO | [6339564113](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6339564113) / [6338326769](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6338326769) |
| G·W0·A2-ON 기록 | [6340047661](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340047661) |
| A2-ON·D HOLD (20:40:32 게시) | [6339848618](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6339848618) |
| 이권욱 NP0 한정 수용·A4 1회 GO (21:21) | [6340597438](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340597438) |
| 하영 C-STOP | [6341388160](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6341388160) |
| 재환 결과(A4·녹화·C-STOP 관측·A2-OFF·VPN 증분) | [6341600008](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6341600008) |
| 원본 반출(공유 폴더, 47/47) | [6355690272](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6355690272) |

## 결과 요약 (보고 기준, 판정은 각 링크)

| 단계 | 시각(KST) | 결과 | 원본 |
|---|---|---|---|
| G | T0 20:32:06 | 창 B 유지 구성 인계, 사전 점검 대비 증분 0 | (VPN 조회, 이 폴더 밖) · 6340047661 |
| W0 | 20:38:20 | `W0_READY(pre-apply)=YES`, `RUNTIME_PERMANENT_MATCH=YES` | `db01/w0-check-…`, `db01/w0-fw-…` |
| A2-ON | 20:39:41~49 | `RESULT a2-apply=OK`, pg_hba 1줄 `hostssl fdsdb fds_app 10.20.10.0/24 scram-sha-256` | `db01/a2-apply-…`, RUN 폴더 |
| A4 회귀 | 21:09:50~52 | B1 11 PASS / 0 FAIL, B2 14 PASS / 0 FAIL / INFO 1, DB 대조 불일치 0 (B1 11행·B2 12행) | `pc/a4-regression/` |
| 녹화 | 21:44:12~37 | 거래 201 11건, 탐지 4건, 프록시 로그 ↔ db01 11행 11/11 일치 | `pc/recording/` |
| C-STOP 관측 | 22:02 직전 | db01 `10.20.0.0/16` 출발지 세션 0 (C-STOP 자체는 하영 22:00:44~55) | 6341600008 §3 |
| A2-OFF | 22:02:49~57 | `RESULT a2-rollback=OK 22:02:57 — W0 대조 일치` | `db01/a2-rollback-…`, `a2.receipt` |
| SYN 관측 | 20:39~22:05 | tcpdump 28,593 패킷, 커널 drop 0 | `db01/c-db-20261022T2038.log` (pcap은 미편입) |
| VPN 증분 | G → 마감 | `worker -> db01 5432` 새 연결 vpn-gw01·Relay 모두 0 → 533, db01 첫 SYN 533과 일치 | 6341600008 §5 (이 폴더 밖) |
| A5 | — | **NOT_RUN** (GO 범위에서 생략) | — |
| ROSA 관측 | 20:40~22:05 | Pod 수·앱별 네트워크 수신량. 21:10(A4)·21:45(녹화) 증가. **21:13 증가 1건은 원인 미확인** | `pc/rosa-monitoring/` |

DB 개방 구간은 20:39:49~22:02:57(83분)로 보고됐다.

## 편차 (덮지 않음)

- **A4 회귀(21:09:50~52)는 이권욱 A4 1회 GO([6340597438](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340597438), 21:21) 게시 전, STOP 유지 중에 실행됐다.** 재환이 6341600008 §0에서 **승인 밖 실행으로 분류**해 달라고 요청했다. 결과만 원본과 함께 보존한다.
- 녹화 송신(21:44:12~37)은 21:21 GO 뒤이고 시험 종료 상한 21:55 안이다. 다만 **GO의 착수 기한 21:35 이후에 송신했다.** 21:28부터 준비했고, 21:36에 로컬 프록시가 종료돼 첫 시도는 송신 0건이었다(`endpage-rosa-proxy-20261022T2120.log`). 21:43에 다시 기동했다. 판단은 이권욱에게 맡겼다.
- 6340047661의 "D 미착수" 표기는 틀렸다. D는 20:43:19에 실행됐다([하영 정정 6340066460](https://github.com/321Team/fds-project-baseline/issues/47#issuecomment-6340066460)).
- HOLD(6339848618)는 A2-ON 완료(20:39:49) 43초 뒤에 게시됐다. A2-ON은 그 전 GO 순서대로 실행됐다.
- 원인 조사로 db01에서 조회만 했다: PostgreSQL 로그 grep, `pg_stat_activity`, `psql host=127.0.0.1 dbname=fdsdb user=fds_app -c "select 1"` 로컬 로그인 1회. 비밀번호·DB 사용자 변경은 없다(6341600008 §0).
- A5 네트워크 거부 시험은 GO대로 생략했다(**NOT_RUN**, 미충족 유지).
- ROSA 네트워크 그래프의 21:13 증가 1건은 기록상 송신이 없어 **원인 미확인**이다.
- A4 RUN 이름 `202610221209`는 Git Bash에서 `TZ`가 적용되지 않아 UTC 기준으로 붙었다. 실제 송신은 21:09:50~52 KST다.
- 이 편입은 위 실행의 소급 승인이 아니다.

## 파일

| 경로 | 출처 수준 | 내용 |
|---|---|---|
| `bundle/README.md`, `bundle/SHA256SUMS` | 바깥 묶음 안의 파일, 바이트 동일 | 반출 묶음 설명, 묶음 내부 47개 해시 |
| `db01/w0-check-20261022T2038.txt`, `db01/w0-fw-20261022T2038.txt` | db01 묶음을 푼 파일, 바이트 동일 | W0 `check`, firewall check 출력 |
| `db01/a2-apply-20261022T2038.txt`, `db01/a2-rollback-20261022T2038.txt` | 같음 | A2-ON·A2-OFF 출력 |
| `db01/c-db-20261022T2038.log` | 같음 | tcpdump 실행 로그(snaplen 128, 28,593 패킷, drop 0) |
| `db01/db_202610221209.log` | 같음 | A4 DB 조회 23행(`pc/a4-regression/db_202610221209.log`와 바이트 동일) |
| `db01/p2-hyb01-rosa-20261022T2038/` | 같음 | `a2.receipt`, `hba-rules.before/after`, `nm-routes.before`, 단계 로그 3개 |
| `pc/a4-regression/` | 바깥 묶음을 푼 파일, 바이트 동일 | `p2e2e.py`(`a00ae029…a07d`), `PLAN_202610221209/`(criteria `0d87ea0f…ff97`), `OUT_B1_…`·`OUT_B2_…` 응답·판정, DB 조회 로그 |
| `pc/recording/` | 같음 | 로컬 프록시 로그 2개(21:20 첫 시도, 21:45 녹화분), db01 녹화 거래 11행 |
| `pc/rosa-monitoring/` | 같음 | OpenShift 기본 모니터링(Prometheus) `query_range` 원데이터 2개, 2단 그래프 PNG(1920×1080) |
| `SHA256SUMS` | 이 폴더에서 계산 | 이 폴더 파일 해시 |

db01 단계 로그 중 3개는 상위 출력과 바이트가 같다: `db01-check-203820.log` = `w0-check-…`, `db01-a2-apply-203940.log` = `a2-apply-…`, `db01-a2-rollback-220249.log` = `a2-rollback-…`.

## 편입하지 않은 원본 (공유 폴더 유지)

[증적 관리 규칙](../../../governance/EVIDENCE_POLICY.md) '자료 유형과 접근'은 "1MB를 넘으면 별도 보관소에 두고 URI·SHA-256만 연결한다"고 정한다. 바깥 묶음과 db01 묶음은 이 한도를 넘어 Git에 넣지 않았다. pcap과 영상 2개는 이번 편입 범위에서 빼기로 결정했다(사용자 결정). 원본은 모두 아래 묶음 안에 그대로 있다.

- 보관 위치: `\\10.1.93.150\HybridCloud과정공유디렉토리\07_프로젝트\제01조\02차 프로젝트\p47-windowC-20261022.tgz` (고정 비공개 공유 폴더)

| 원본 | 위치 | 크기(B) | SHA-256 |
|---|---|---:|---|
| `p47-windowC-20261022.tgz` | 공유 폴더 | 15,428,609 | `8eb86b92b18b3bcc0847069a590b41eb5a4816d288ac6b3368f6429da0789cca` |
| `db01/windowC-db01-20261022T2038.tgz` | 바깥 묶음 안 | 1,511,772 | `b2748f7dee8ed872a39c115012fbb2daf4f416c33015a8f763095a74c5d8502b` |
| `c-db-20261022T2038.pcap` | db01 묶음 안 | 3,371,532 | `9953792dbda0a4a96775c6d26960e246fd377a3dc3206b63daa7d147cfd57b10` |
| `pc/recording/demo-original-20261022T2144.mp4` | 바깥 묶음 안 | 5,308,531 | `f7c975a6bbab8bf3fbbb7e8b3c90c5b34e1b08cf42aef08004f1dd06a119204d` |
| `pc/recording/demo-final-shortlabel-rosa.mp4` | 바깥 묶음 안 | 8,966,052 | `2aa31a5c3123dbdde1da644549da2f296d75015f7f93cfbf2dca79c00804d54c` |

- `demo-original-20261022T2144.mp4`는 6341600008 §2의 원본 영상 `2026-10-22 21-44-09.mp4`(45.2초)와 크기·SHA-256이 같다. `demo-final-shortlabel-rosa.mp4`는 짧은 표시와 끝 12초 ROSA 관측을 붙인 최종 영상이다(6355690272).
- pcap은 `tcp port 5432 and net 10.20.0.0/16`을 snaplen 128로 잡아 TCP 5432 헤더와 TLS 시작부만 담는다(6341600008 §4, 6355690272).

## 묶음 내부 목록

### 바깥 묶음 `p47-windowC-20261022.tgz` (일반 파일 48개)

`SHA256SUMS` 1개와, 그 안에 적힌 47개 항목(`README.md` 포함)이다. 전체 해시는 `bundle/SHA256SUMS`(원본 바이트)에 있다.

| 경로 | 개수 | 편입 |
|---|---:|---|
| `README.md`, `SHA256SUMS` | 2 | `bundle/`에 그대로 |
| `db01/windowC-db01-20261022T2038.tgz` | 1 | 묶음은 미편입, 안쪽 파일은 아래 표대로 |
| `pc/a4-regression/` (`p2e2e.py`, `db_202610221209.log`, `PLAN_…/` 3, `OUT_B1_…/` 14, `OUT_B2_…/` 18) | 37 | 전부 |
| `pc/recording/` (프록시 로그 2, `db01-end-rows-202610222144.txt`, mp4 2) | 5 | mp4 2개 제외 3개 |
| `pc/rosa-monitoring/` (`rosa-net.json`, `rosa-pods.json`, `rosa-pods-network-20261022.png`) | 3 | 전부 |

### db01 묶음 `windowC-db01-20261022T2038.tgz` (일반 파일 14개, 자체 Manifest 없음)

| 파일 | 크기(B) | SHA-256 | 편입 |
|---|---:|---|---|
| `a2-apply-20261022T2038.txt` | 4,506 | `11b712ec416932f9ddf8aecf8a433b9dc05d51acca8b885096fe3eb1ce909aa3` | O |
| `a2-rollback-20261022T2038.txt` | 2,916 | `166d856247bffcd4f3d22216832d7036a94ec3a3ccf6424301148dc9c9b653ea` | O |
| `c-db-20261022T2038.log` | 259 | `83329ec0d033f252dd05a195f31a21e7c7d429d9ee53b0b4722f50f138851b88` | O |
| `c-db-20261022T2038.pcap` | 3,371,532 | `9953792dbda0a4a96775c6d26960e246fd377a3dc3206b63daa7d147cfd57b10` | X |
| `db_202610221209.log` | 2,572 | `44fe9b425fc6d841c4a17fc115466fca26cde04f1f86a939774238ba9d248937` | O |
| `p2-hyb01-rosa-20261022T2038/a2.receipt` | 379 | `a9e8c863bee8edd6951d28eb3fe7ed89eba66e2f09b02b7fe112ddf6f514c3ac` | O |
| `p2-hyb01-rosa-20261022T2038/db01-a2-apply-203940.log` | 4,506 | `11b712ec416932f9ddf8aecf8a433b9dc05d51acca8b885096fe3eb1ce909aa3` | O |
| `p2-hyb01-rosa-20261022T2038/db01-a2-rollback-220249.log` | 2,916 | `166d856247bffcd4f3d22216832d7036a94ec3a3ccf6424301148dc9c9b653ea` | O |
| `p2-hyb01-rosa-20261022T2038/db01-check-203820.log` | 2,618 | `c2a2c6834946ce60448e4018430e70f697f2748a9fc4de97a4a3b8e99f9470c6` | O |
| `p2-hyb01-rosa-20261022T2038/hba-rules.after` | 583 | `33bae3be83a5e27059ba0683f8dd7f1d7408faa573dad47225d425d2419052d2` | O |
| `p2-hyb01-rosa-20261022T2038/hba-rules.before` | 518 | `e36d1525767c30ccb5bc3ec84c077d7bf86878c2efaf055c3bd04714ff2ceb8d` | O |
| `p2-hyb01-rosa-20261022T2038/nm-routes.before` | 26 | `e69abdade09c6bc1644819cee8f8f864af6a2c181a6a2583c6a63b757de5847b` | O |
| `w0-check-20261022T2038.txt` | 2,618 | `c2a2c6834946ce60448e4018430e70f697f2748a9fc4de97a4a3b8e99f9470c6` | O |
| `w0-fw-20261022T2038.txt` | 2,268 | `243a7275297118d225b9aef03d1da06bd04acb32197de9c394946f750bd63381` | O |

### 대조 방법

```sh
cd evidence/P2-HYB-01/window-c-jaehwan-20261022
sha256sum -c SHA256SUMS                                          # 이 폴더 59개
grep ' \*pc/' bundle/SHA256SUMS | grep -v '\.mp4$' | sha256sum -c  # 묶음 해시와 pc/ 43개 대조
```

- 2026-10-24 편입 준비 때 묶음을 바이트에서 직접 다시 계산했다. 바깥 `SHA256SUMS` 47/47 일치, db01 묶음 `b2748f7d…502b` 일치. 편입한 58개(`bundle/` 2, `db01/` 13, `pc/` 43)는 묶음 안 원본과 바이트가 같다.
- db01 묶음에는 자체 Manifest가 없다. 위 db01 표는 묶음 바이트에서 계산한 값이다.

## 판정 범위

`G=OK / W0=READY / A2_ON=OK(20:39:49) / A4=B1 11/11·B2 14/14·DB 불일치 0(승인 밖 실행) / REC=201 11건·탐지 4·DB 11/11(착수 기한 뒤 송신) / A2_OFF=OK(22:02:57, W0 일치) / A5=NOT_RUN`

창 C 재환 몫 실행 증적이다. 위 값은 실행자 보고와 원본 파일 내용이며, AC PASS나 승인 판정이 아니다. 해시 일치는 무결성 확인이며 시험 PASS의 단독 근거가 아니다. P2-HYB-01 전체 AC 완료나 티켓 종결이 아니다.

## 민감정보

- **자격증명 0건:** 편입 전 `password|passwd|DATABASE_URL|token|BEGIN .*PRIVATE|eyJ|bearer|sha256~|postgres(ql)?://|aws_secret|AKIA` 패턴으로 이 폴더를 검사했다. 일치는 `p2e2e.py`가 URL에 사용자·비밀번호가 들어 있으면 거부하는 검사 코드 1줄(`u.password`)뿐이다. DB 비밀번호·DSN·Secret 값·kubeconfig·토큰은 없다.
- `psql` 로컬 로그인 1회(위 편차)에서 쓴 비밀번호는 어느 파일에도 없다.
- **식별자 포함:** 내부 IP(db01·worker 노드·pg_hba 대상), ROSA Route host, NM 연결 UUID, 시험 거래 ID·SIM 계정 ID, 재환 PC의 로컬 경로. 원본 바이트 보존 규칙에 따라 그대로 둔다.

AI 사용: CLAUDE_ASSISTED
