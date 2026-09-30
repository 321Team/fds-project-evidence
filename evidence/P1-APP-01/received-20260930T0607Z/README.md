# P1-APP-01 — Workload별 Request/Limit 부하 재시험 3차: 리뷰 완료 도구로 승인 목표 부하 (2026-09-30 14:48~15:03 KST)

APP Lead(이재환)가 독립 코드 리뷰를 마친 부하 시험 도구로, 결정안 v2의 승인 목표 부하를 정본 클러스터의 transaction-api·fds-engine에 걸었다. 목표 부하·합격 기준·산식·관측 query는 아래 결정·승인 그대로이고, 시험 전에 서버 파일로 기록해 SHA-256을 남겼다. 명령은 담당자가 k8s-control01(`server02`)과 edge01(`server08`)에서 직접 실행했다.

- 결정안 v2: [#15 comment 5885861552](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5885861552)
- G3 확인(GWONUK APPROVED): [#15 comment 5886568007](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5886568007)
- 승인 대상 조정: [#15 comment 5886692226](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5886692226)
- G3 재시험 조건(2차 RUN `202609291754` 판정): [#15 comment 5887738911](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5887738911) — ① 실행 코드를 소스 PR로 고정 ② 작성자 외 독립 리뷰 ③ 같은 v2 `criteria`/`promql` 기준으로 새 RUN ④ 사전 SHA → Runtime 원본 → 사후 SHA를 같은 회차로 편입 ⑤ 새 증적 PR 독립 리뷰 후 판정
- 실행 코드: [fds-msa#15](https://github.com/321Team/fds-msa/pull/15) 병합 main `1aac16fdeac9b0f6d0c1133c5c5819aa7790b81`(GWONUK 최종 APPROVED [5361462041](https://github.com/321Team/fds-msa/pull/15#pullrequestreview-5361462041), 리뷰 HEAD `c449c16`, CI Run 36662551165 SUCCESS). 실행 파일 SHA-256이 병합 파일과 같다(아래).

**운영 변경:** 없음(Deployment·Resource·replica 변경 없음). 시험 거래 21,000건(`SIM_load_202609301445_<n>`, 10,000원)이 운영 `fdsdb`에 남아 있다. 정리는 [#11 결정안 5887795557](https://github.com/321Team/fds-project-baseline/issues/11#issuecomment-5887795557) 기준을 따른다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-app-load3-20260930/` (11개) | `load3-control01.tar.xz` 9,780 B, SHA-256 `76aea964…7e653f90b1` | base64로 받아 복원. 서버 `sha256sum`과 일치. 개별 파일 11개는 archive 내부와 바이트 동일 |
| `edge01/` | `~/p1-app-load3-202609301445/` (8개) | `load3-edge01-202609301445.tar.xz` 81,852 B, SHA-256 `cac22822…c4bfb6e` | 이 PC(Git Bash)에서 scp로 받음. 서버 `sha256sum`과 일치. 개별 파일 8개는 archive 내부와 바이트 동일. `criteria.sha256` 재검증 OK |

- archive 이름은 서버 이름 그대로다. 두 archive 모두 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 내부 목록을 올렸다.
- 도구 전달: 저장소 파일을 PC에서 base64로 만들어 서버 셸에 붙여넣고 복원했다(`control01/kit.b64` = `promql.txt`+`q_range.py` tar.gz, `edge01/gen3.b64` = `gen3.py` gzip). 복원 직후 병합 파일 SHA-256과 대조했다(`sha256sum -c` 성공).
- 전달 경위: edge01에 처음 붙여넣은 `gen3.py` base64는 작성 오류(AI 준비 단계 오류)로 복원되지 않아(`gzip: invalid compressed data`, `gen3.py: 실패`) 시작 조건에서 멈췄다. 이때 부하 요청은 한 건도 나가지 않았고 Worker `/readyz` GET 3건만 실행됐다. 같은 폴더에서 `gen3.b64`를 올바른 본문으로 덮어써 다시 복원·대조했고, `criteria.txt`는 이 뒤에 처음 만들어졌다. 폴더의 `gen3.b64`는 이 두 번째 본문이다.
- `promql.txt`·`q_range.py`의 archive 안 시각(09:00)은 전달 묶음에 고정한 시각이 복원된 것이다. 서버에 둔 시각은 `pre.sha256`(14:43)으로 본다.

## 기준 고정 순서 (archive 안 파일 시각, KST)

| 시각 | 파일 | 내용 |
|---|---|---|
| 14:43:02 | `control01/env-before.txt` | 이미지 digest·Resource·Pod 배치·restartCount·마지막 종료 사유·시각 동기 |
| 14:43 | `control01/pre.sha256` | promql.txt `deccc549…863d91a1`, q_range.py `5b59d0d5…b65cfd85` — 병합 main과 같고, 시험 뒤 다시 계산해도 같다 |
| 14:47 | `edge01/gen3.py` · `criteria.txt` | 부하 생성기(병합 파일), 목표 부하·합격 기준·산식·판정·도구 SHA(결정·승인 링크 포함) |
| 14:48:08 | `edge01/criteria.sha256` | criteria.txt `21a64d38…78c2b2ec`, gen3.py `8d94a97f…eb3dd610` — 시험 뒤 `sha256sum -c` OK |
| 14:48:08.955 | `edge01/requests.log` 첫 줄 | 첫 요청 |

한 명령 안에서 생성기 SHA 대조와 Worker 3대 `/readyz` 200 확인이 모두 맞을 때만 `criteria.sha256`을 기록하고 생성기를 시작했다. 기준 파일은 시험 뒤 바꾸지 않았다.

## 시험 조건

| 항목 | 값 |
|---|---|
| 대상 이미지 | transaction-api `10.1.93.54/fds/transaction-api@sha256:a7093136…ac45cc33`, fds-engine `10.1.93.54/fds/fds-engine@sha256:5e2a081c…24f67369`(`env-before.txt`) |
| Resource·replica | 두 서비스 모두 requests 250m/256Mi, limits 500m/512Mi, Pod 3개(worker01·02·03에 1개씩) |
| 경로 | edge01 → Worker `:30080`(`.105/.107/.108` 순환). edge01 nginx(:80) 이관 전이라 NodePort 직접 경로 |
| 부하 | 기준 B 20 rps 600초 → 피크 P 50 rps 180초 → 무부하 120초 관찰, 총 21,000건 |
| 생성기 (`gen3.py`) | 정해진 속도 송신, 진행 중 요청 상한 64(포화 시 `LOAD_GENERATOR_SATURATED`), 단계 끝 2초 안 미완료 시 `STAGE_NOT_DRAINED`, 30초 사이·단계 끝 마지막 구간 201 외 10건 이상 시 `ERROR_THRESHOLD`(모두 종료 코드 2). 요청마다 새 계정·새 연결, timeout 10초, 입금 60·출금 20·이체 20%, 10,000원, `source_ip` 198.51.100.10 → Rule이 걸리지 않는 입력 |
| 관측 | control01에서 Prometheus(`monitoring-api/prometheus`, 이 시험 전용 port-forward `127.0.0.1:19091`)를 시험 뒤 `query_range`로 조회: start 1790747228.955(기준 시작 − 60초), end 1790748188.965(관찰 끝), step 15s → `q1.json`·`q2.json`·`q3.json`, Q별 6 series·390 points(`q_range.out`) |
| 시각 동기 | control01 NTP 차 0.00019초(시험 전)·0.00005초(시험 후), edge01 0.00018초 |

`pf.log`는 port-forward 연결 기록이다(사전 점검 2회 × query 3개, 구간 조회 3개 = 9건). 시험 뒤 이 port-forward만 종료했다.

## 결과

**생성기 (`edge01/stages.log`, `gen.rc`)** — `DONE outstanding 0 codes {201: 21000}`, 종료 코드 `0`. 중단 조건(포화·단계 끝 미완료·오류 임계)은 한 번도 걸리지 않았고, 두 단계 모두 끝난 뒤 4ms 안에 요청이 다 끝났다(`DRAINED`).

**클라이언트 (`edge01/requests.log`)**

| 구간 | 시각(KST) | 요청 | 달성 처리량 | 상태 | Worker 분배 | p50 / p95 / p99 / max (ms) |
|---|---|---|---|---|---|---|
| B 기준 | 14:48:08~14:58:08 | 12,000 | 20.00 rps (100.0%) | 201 × 12,000 | 4,000 × 3 | 23.2 / 28.6 / 31.8 / 54.5 |
| P 피크 | 14:58:08~15:01:08 | 9,000 | 50.00 rps (100.0%) | 201 × 9,000 | 3,000 × 3 | 18.0 / 24.3 / 26.9 / 49.2 |
| 관찰 | 15:01:08~15:03:08 | 0 | — | — | — | — |

- 유형은 B 입금 7,204·출금 2,475·이체 2,321, P 입금 5,395·출금 1,802·이체 1,803이다.
- 요청 시작 시각을 초 단위로 세면 B 600초 동안 매초 20건, P 180초 동안 매초 50건이다(최소 = 최대). 발사 지연 뒤 몰아서 보낸 구간은 없다([fds-msa#15 리뷰](https://github.com/321Team/fds-msa/pull/15#pullrequestreview-5360224070) 비차단 관찰 확인).

**자원 (`control01/q1.json`·`q2.json`·`q3.json`)**

| 워크로드 | 기준 구간 CPU 최대 (Q1) | 피크 CPU 최대 (Q1) | 메모리 최대 (Q2) | throttling 최대 (Q3) |
|---|---|---|---|---|
| transaction-api | 94.5m | 174.8m | 121.9MiB | 0% |
| fds-engine | 10.7m | 20.4m | 70.0MiB | 0% |

워크로드별(Pod 3개 합) 판정에 쓴 측정값은 기준 111개, 피크 24개, 메모리 183개다. 빠진 point와 NaN은 없다.

**Pod (`env-before.txt` 14:43:02 → `env-after.txt` 15:04:36):** 이미지·Node·restartCount·마지막 종료 사유가 전후 같다(fds-engine 0/2/0, transaction-api 0/0/1, `Unknown`은 시험 전부터 있던 기록). OOMKilled는 없다.

## 산식 적용

| 워크로드 | CPU request | CPU limit | 메모리 request | 메모리 limit |
|---|---|---|---|---|
| transaction-api | 94.5 × 1.5 = 141.7 → 150m ≤ 250m | 174.8 × 2 = 349.6 → 400m ≤ 500m | 121.9 × 1.2 = 146.3 → 192Mi ≤ 256Mi | 384Mi ≤ 512Mi |
| fds-engine | 10.7 × 1.5 = 16.0 → 최소 100m ≤ 250m | 20.4 × 2 = 40.8 → 100m ≤ 500m | 70.0 × 1.2 = 84.0 → 128Mi ≤ 256Mi | 256Mi ≤ 512Mi |

## 합격 기준 판정

| # | 기준 | 결과 | 판정 |
|---|---|---|---|
| 1 | 201 외 응답·timeout·연결 오류 0 | 21,000건 모두 201 | PASS |
| 2 | throttling(Q3) 기준·피크 구간 최대 25% 미만 | 두 워크로드 모두 0% | PASS |
| 3 | restartCount 변화 0, OOMKilled 0 | 변화 없음, OOMKilled 없음 | PASS |
| 4 | 두 워크로드 모두 현재 값 ≥ 산식 결과 | 위 표 | PASS |
| 5 | 구간별 달성 처리량 ≥ 목표의 98% | B 100.0%, P 100.0% | PASS |
| — | 생성기 종료 코드 0(`criteria.txt` 판정 조건) | `0` | 충족 |
| — | fail-closed(필요 시계열 부재·유효 샘플 없음) | 해당 없음 | — |
| — | p95 (기록만, 판정 미사용) | B 28.6ms, P 24.3ms | — |

**판정: 합격 기준 1~5를 모두 충족하고 생성기 종료 코드가 0이다. `criteria.txt`의 판정 규칙에 따라 현재 이미지 기준 Resource baseline 현재 값(requests 250m/256Mi, limits 500m/512Mi) 유지가 확정 조건을 만족한다.** 실행 코드는 독립 코드 리뷰를 마친 병합 SHA와 같다(G3 재시험 조건 ①~④). 이 증적 PR의 독립 리뷰(⑤) 뒤 #15 핵심 요구 "Workload별 Request/Limit을 부하 시험으로 확정한다" 체크를 판단한다.

## 판정 범위

- 이 증적이 보여 주는 것: 결정안 v2의 승인 목표 부하(기준 20 rps 10분 → 피크 50 rps 3분, Phase 1 프로젝트 내부 목표)에서 현재 이미지와 현행 Resource가 관측 부하를 수용했다(201 외 응답·throttling·재시작·OOM 0, 산식 결과 ≤ 현재 값).
- 확정하지 않는 것: 지연 SLO(p95는 기록만), 최종 ingress(edge01 nginx :80) 경로의 지연, 50 rps를 넘는 처리량, 10/5 전환 이미지의 자원 특성, #15의 다른 AC와 종결, MS-G3-01 #29 Gate.
- 10/5 이미지 전환 뒤에는 #15를 다시 판정하지 않는다. #20 회귀 2회차에서 축약본(기준 20 rps 2분 → 피크 50 rps 2분)을 regression gate로만 돌리고, 이상이 있으면 #20 Defect·#15 영향 재검토·새 이미지 full profile 재시험으로 연결한다(결정안 v2 8절).
- 2차 RUN `202609291754`([evidence#75](https://github.com/321Team/fds-project-evidence/pull/75), 진단·이력)과 수치가 거의 같지만, 판정에는 이 3차 RUN 원본만 쓴다.

## 계산 방법

- 판정은 받은 원본(`q1~q3.json`, `env-before.txt`·`env-after.txt`, `stages.log`, `requests.log`, `gen.rc`)으로 로컬에서 계산했다. 규칙은 `promql.txt`·`criteria.txt` 그대로다.
- 구간 시각은 `stages.log`의 epoch를 쓴다: B 1790747288.955~1790747888.956, P 1790747888.960~1790748068.960, 관찰 끝 1790748188.965.
- CPU·throttling은 평가 시각이 [구간 시작 + 60초, 구간 끝]에 드는 값만, 메모리는 기준 시작부터 관찰 끝까지 전체를 쓴다. 워크로드 값은 Pod 3개 값 중 최대다.
- 달성 처리량 = 해당 구간 요청 가운데 요청 시작 시각(t0)이 구간 안인 건수 ÷ 구간 길이.
- 지연 분위수는 Python `statistics.quantiles(n=100)`(exclusive)로 계산했다.

## 한계와 후속

- 경로는 edge01 → Worker NodePort 직접이다. 자원 크기 판정용이며 최종 ingress 경로 지연의 근거가 아니다.
- fds-engine은 산식상 100m/128Mi로도 충분하다. 값을 낮추는 조정은 이 결정 범위 밖이다.
- 시험 거래 21,000건이 운영 DB에 남아 있다(SIM_load 누계: 9/29 RUN 2건 27,750 + 이번 21,000). 정리는 #11 결정안대로 모든 판정이 끝난 뒤 infra-db PR로 한다.

AI 사용: CLAUDE_ASSISTED (명령·전달 묶음 준비, 수신 대조·판정 계산·문서화, 실행은 담당자 본인)
