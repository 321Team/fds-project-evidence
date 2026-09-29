# P1-APP-01 — Workload별 Request/Limit 부하 재시험: 승인 목표 부하 (2026-09-29 17:54~18:10 KST)

APP Lead(이재환)가 승인된 목표 부하로 정본 클러스터의 transaction-api·fds-engine 부하 재시험을 했다. 목표 부하·합격 기준·산식·관측 query는 아래 결정과 승인으로 시험 전에 고정했고, 시험 전에 서버 파일로 기록해 SHA-256을 남겼다. 명령은 담당자가 k8s-control01(`server02`)과 edge01(`server08`)에서 직접 실행했다.

- 결정안 v2: [#15 comment 5885861552](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5885861552)
- G3 확인(GWONUK APPROVED): [#15 comment 5886568007](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5886568007)
- 승인 대상 조정(Support 승인 대기 제외, fail-closed 해석 반영): [#15 comment 5886692226](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5886692226)

> **판정 상태 — 진단·이력 증적 ([GWONUK 리뷰](https://github.com/321Team/fds-project-evidence/pull/75#pullrequestreview-5350629433) 해결안 B 반영)**
> 측정값과 산식 결과는 합격 기준 1~5를 모두 충족한다. 그러나 운영 Runtime에 쓴 부하 생성 코드 `gen2.py`와 조회 코드 `q_range.py`가 실행 전에 독립 코드 리뷰(REVIEW_AUTHORITY_POLICY §3, §3.2 4-1(5))를 거치지 않았으므로 `RUNTIME_GOVERNANCE=NONCOMPLIANT`다. 이 RUN은 진단·이력 증적으로만 편입하며, Resource baseline 최종 확정과 #15 핵심 요구 체크의 근거로 쓰지 않는다. 정식 판정은 코드 리뷰를 마친 exact SHA로 결정안 v2 기준 그대로 새 RUN을 실행해 별도 증적으로 한다. 세 파일(`gen2.py`·`q_range.py`·`promql.txt`)은 같은 바이트로 [fds-msa#15](https://github.com/321Team/fds-msa/pull/15)에 올려 독립 코드 리뷰를 요청했다.

**실행 근거와 시점:** 시험은 승인 대상 조정 코멘트(17:38 KST)를 근거로 17:54:55~18:09:55에 실행했다. 18:05에 올린 G3 확인 요청([5887096583](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5887096583))의 "시험 착수 전" 표현은 실제 시각과 다르며, G3 재확인([5887187108](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5887187108), "2차 부하시험 GO")은 시험이 끝난 뒤인 18:11에 받았다.

**스크립트:** `edge01/gen2.py`는 [evidence#71](https://github.com/321Team/fds-project-evidence/pull/71) `gen.py`와 요청 생성 로직(요청 내용·속도 제어·동시 상한 64·timeout 10초)이 같고, 단계 값·상태 코드 집계·30초 진행 로그·epoch 기록만 다르다. `control01/q_range.py`는 Prometheus를 읽기만 하는 새 조회 스크립트다. 둘 다 시험 전에 SHA-256을 고정했고, 중앙 정책 §3 코드 리뷰는 거치지 않았다.

**운영 변경:** 없음(Deployment·Resource·replica 변경 없음). 시험 거래 21,000건(`SIM_load_202609291754_<n>`, 10,000원)이 운영 `fdsdb`에 남아 있다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-app-load2-20260929/` (10개) | `load2-control01.tar.xz` 7,936 B, SHA-256 `e54b925c…232a9f2e` | base64로 받아 복원. 서버 `sha256sum`과 일치. 개별 파일 10개는 archive 내부와 바이트 동일 |
| `edge01/` | `~/p1-app-load2-202609291754/` (7개) | `load2-edge01-202609291754.tar.xz` 76,472 B, SHA-256 `a25b9f07…31b47a11` | PC에서 scp로 받음. 서버 `sha256sum`과 일치. 개별 파일 7개는 archive 내부와 바이트 동일. `criteria.sha256` 재검증 OK |

- archive 이름은 서버 이름 그대로다(이름 변경 없음). 두 archive 모두 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 내부 목록을 올렸다.
- 수신 경위: edge01에서 archive SHA-256을 기록(18:15)한 뒤, scp 명령을 PC가 아닌 edge01 셸에서 한 번 잘못 실행해 같은 파일을 자기 자신에게 복사했다. 이후 PC에서 받은 파일의 SHA-256이 처음 기록한 값과 같아 내용 변화가 없음을 확인했다.

## 기준 고정 순서 (archive 안 파일 시각, KST)

| 시각 | 파일 | 내용 |
|---|---|---|
| 17:46:21 | `control01/env-before.txt` | 이미지 digest·Resource·Pod 배치·restartCount·마지막 종료 사유·시각 동기 |
| 17:46:36 · 17:46:51 | `control01/promql.txt` · `q_range.py` | 관측 query Q1~Q3와 조회·구간·집계·fail-closed 규칙, 조회 스크립트 |
| 17:47:02 | `control01/pre.sha256` | promql.txt `deccc549…863d91a1`, q_range.py `5b59d0d5…b65cfd85` — 시험 뒤 다시 계산해도 같다 |
| 17:54:05 · 17:54:21 | `edge01/criteria.txt` · `gen2.py` | 목표 부하·합격 기준·산식·판정·중단 조건(결정·승인 링크와 promql.txt SHA 포함), 부하 생성기 |
| 17:54:55 | `edge01/criteria.sha256` | criteria.txt `077610fc…cdf3f987`, gen2.py `60f09400…768c2916` — 시험 뒤 `sha256sum -c` OK |
| 17:54:55.811 | `edge01/requests.log` 첫 줄 | 첫 요청 |

`criteria.sha256`과 첫 요청은 같은 초다. 한 명령 안에서 SHA-256을 기록한 뒤 생성기를 시작했다(생성기 SHA와 Worker 3대 `/readyz` 200을 확인한 경우에만 시작하도록 했다). 기준 파일은 시험 뒤 바꾸지 않았다.

## 시험 조건

| 항목 | 값 |
|---|---|
| 대상 이미지 | transaction-api `10.1.93.54/fds/transaction-api@sha256:a7093136…ac45cc33`, fds-engine `10.1.93.54/fds/fds-engine@sha256:5e2a081c…24f67369`(`env-before.txt`) |
| Resource·replica | 두 서비스 모두 requests 250m/256Mi, limits 500m/512Mi, Pod 3개(worker01·02·03에 1개씩) |
| 경로 | edge01 → Worker `:30080`(`.105/.107/.108` 순환). edge01 nginx(:80) 이관 전이라 NodePort 직접 경로 |
| 부하 | 기준 B 20 rps 600초 → 피크 P 50 rps 180초 → 무부하 120초 관찰, 총 21,000건 |
| 생성기 (`gen2.py`) | 정해진 속도로 계속 보내는 방식, 동시 처리 상한 64, 요청마다 새 연결, timeout 10초. 요청마다 새 계정, 입금 60·출금 20·이체 20%, 10,000원, `source_ip` 198.51.100.10 → Rule이 걸리지 않는 입력 |
| 관측 | control01에서 Prometheus(`monitoring-api/prometheus`, 이 시험 전용 port-forward `127.0.0.1:19091`)를 시험 뒤 `query_range`로 조회: start 17:53:55.811(기준 시작 − 60초), end 18:09:55.812(관찰 끝), step 15s → `q1.json`·`q2.json`·`q3.json`, Q별 6 series·390 points(`q_range.out`) |
| 시각 동기 | control01 NTP 차 0.00003초(시험 전)·0.0001초(시험 후), edge01 0.00014초 |

`pf.log`는 port-forward 연결 기록이다(사전 점검 3회 × query 3개, 구간 조회 3개 = 12건).

## 결과

**클라이언트 (`edge01/stages.log`, `requests.log`)**

| 구간 | 시각(KST) | 요청 | 달성 처리량 | 상태 | Worker 분배 | p50 / p95 / p99 / max (ms) |
|---|---|---|---|---|---|---|
| B 기준 | 17:54:55~18:04:55 | 12,000 | 20.00 rps (100.0%) | 201 × 12,000 | 4,000 × 3 | 23.9 / 27.5 / 29.7 / 49.7 |
| P 피크 | 18:04:55~18:07:55 | 9,000 | 50.00 rps (100.0%) | 201 × 9,000 | 3,000 × 3 | 19.2 / 25.0 / 28.4 / 47.2 |
| 관찰 | 18:07:55~18:09:55 | 0 | — | — | — | — |

유형은 B 입금 7,218·출금 2,356·이체 2,426, P 입금 5,420·출금 1,774·이체 1,806이다.

**자원 (`control01/q1.json`·`q2.json`·`q3.json`)**

| 워크로드 | 기준 구간 CPU 최대 (Q1) | 피크 CPU 최대 (Q1) | 메모리 최대 (Q2) | throttling 최대 (Q3) |
|---|---|---|---|---|
| transaction-api | 93.1m | 174.0m | 121.9MiB | 0% |
| fds-engine | 9.7m | 17.8m | 69.9MiB | 0% |

Pod당 판정에 쓴 측정값은 기준 37개, 피크 9개, 메모리 61개다. 빠진 point와 NaN은 없다.

**Pod (`env-before.txt` 17:46:21 → `env-after.txt` 18:15:11):** 이미지·Node·restartCount·마지막 종료 사유가 전후 같다(fds-engine 0/2/0, transaction-api 0/0/1, `Unknown`은 시험 전부터 있던 기록). OOMKilled는 없다.

## 산식 적용

| 워크로드 | CPU request | CPU limit | 메모리 request | 메모리 limit |
|---|---|---|---|---|
| transaction-api | 93.14 × 1.5 = 139.7 → 150m ≤ 250m | 174.02 × 2 = 348.0 → 400m ≤ 500m | 121.95 × 1.2 = 146.3 → 192Mi ≤ 256Mi | 384Mi ≤ 512Mi |
| fds-engine | 9.75 × 1.5 = 14.6 → 최소 100m ≤ 250m | 17.80 × 2 = 35.6 → 100m ≤ 500m | 69.87 × 1.2 = 83.8 → 128Mi ≤ 256Mi | 256Mi ≤ 512Mi |

## 합격 기준 판정

| # | 기준 | 결과 | 판정 |
|---|---|---|---|
| 1 | 201 외 응답·timeout·연결 오류 0 | 21,000건 모두 201 | PASS |
| 2 | throttling(Q3) 기준·피크 구간 최대 25% 미만 | 두 워크로드 모두 0% | PASS |
| 3 | restartCount 변화 0, OOMKilled 0 | 변화 없음, OOMKilled 없음 | PASS |
| 4 | 두 워크로드 모두 현재 값 ≥ 산식 결과 | 위 표 | PASS |
| 5 | 구간별 달성 처리량 ≥ 목표의 98% | B 100.0%, P 100.0% | PASS |
| — | fail-closed(필요 시계열 부재·유효 샘플 없음) | 해당 없음 | — |
| — | p95 (기록만, 판정 미사용) | B 27.5ms, P 25.0ms | — |

**측정 결과: 합격 기준 1~5 수치는 모두 충족한다(현재 값 requests 250m/256Mi, limits 500m/512Mi로 관측 부하를 수용). 다만 `RUNTIME_GOVERNANCE=NONCOMPLIANT`(실행 코드 사전 독립 리뷰 누락)이므로 이 RUN으로 Resource baseline을 확정하지 않는다.**

## 판정 범위

- 이 증적이 보여 주는 것(진단·이력): 결정안 v2의 승인 목표 부하(기준 20 rps 10분 → 피크 50 rps 3분, Phase 1 프로젝트 내부 목표)에서, 현재 이미지와 현행 Resource로 관측 부하를 수용했다(201 외 응답·throttling·재시작·OOM 0, 산식 결과 ≤ 현재 값).
- 이 증적을 쓰지 않는 곳: Resource baseline 최종 확정과 P1-APP-01 핵심 요구 "Workload별 Request/Limit을 부하 시험으로 확정한다"의 체크. 실행 코드가 사전 독립 코드 리뷰를 거치지 않았기 때문이다(`RUNTIME_GOVERNANCE=NONCOMPLIANT`). 정식 판정은 리뷰된 exact SHA로 새 RUN을 실행해 별도 증적으로 한다.
- 이 증적으로도, 새 RUN으로도 확정하지 않는 것: 지연 SLO(p95는 기록만), 최종 ingress(edge01 nginx :80) 경로의 지연, 50 rps를 넘는 처리량, 10/5 전환 이미지의 자원 특성, #15의 다른 AC와 종결, MS-G3-01 #29 Gate.
- 10/5 이미지 전환 뒤에는 #15를 다시 판정하지 않는다. #20 회귀 2회차에서 축약본(기준 20 rps 2분 → 피크 50 rps 2분)을 regression gate로만 돌리고, 이상이 있으면 #20 Defect·#15 영향 재검토·새 이미지 full profile 재시험으로 연결한다(결정안 v2 8절).

## 계산 방법

- 판정은 받은 원본(`q1~q3.json`, `env-before.txt`·`env-after.txt`, `stages.log`, `requests.log`)으로 로컬에서 계산했다. 규칙은 `promql.txt`·`criteria.txt` 그대로다.
- 구간 시각은 `stages.log`의 epoch를 쓴다: B 1790672095.811~1790672695.811, P ~1790672875.811, 관찰 끝 1790672995.812.
- CPU·throttling은 평가 시각이 [구간 시작 + 60초, 구간 끝]에 드는 값만, 메모리는 기준 시작부터 관찰 끝까지 전체를 쓴다. 워크로드 값은 Pod 3개 값 중 최대다.
- 달성 처리량 = 해당 구간 요청 가운데 요청 시작 시각(t0)이 구간 안인 건수 ÷ 구간 길이.
- 지연 분위수는 Python `statistics.quantiles(n=100)`(exclusive)로 계산했다.
- 검산: 구간을 시각 대신 point 순번(B n=8~44, P n=48~56, 메모리 n=4~64)으로 잘라도 같은 값이 나온다.

## 한계와 후속

- 경로는 edge01 → Worker NodePort 직접이다. 자원 크기 판정용이며 최종 ingress 경로 지연의 근거가 아니다.
- [evidence#71](https://github.com/321Team/fds-project-evidence/pull/71)(5/20/50 rps 각 90초, 병합)은 사전 관측 자료이며 이번 판정에 섞지 않았다. #71 README의 "10/5 이미지 전환 이후 같은 방식으로 재검증해 판정" 문구는 결정안 v2로 대체됐다.
- fds-engine은 산식상 100m/128Mi로도 충분하다. 값을 낮추는 조정은 이 결정 범위 밖이다(별도 제안).
- 시험 거래 21,000건이 운영 DB에 남아 있다. 기존 시험 거래와 함께 정리 기준·시점을 [#11](https://github.com/321Team/fds-project-baseline/issues/11)에 별도 결정안으로 올린다.
- 운영 Runtime에 쓴 `gen2.py`(부하 생성)·`q_range.py`(조회)는 실행 전 독립 코드 리뷰를 거치지 않았다(REVIEW_AUTHORITY_POLICY §3, §3.2 4-1(5): 부하 시험은 순수 검증기 예외 대상이 아님). #71 증적 편입 리뷰는 이 코드 리뷰를 대신하지 않는다. 정식 근거는 두 스크립트를 코드 PR로 고정해 독립 리뷰를 받은 뒤 같은 기준으로 새 RUN을 실행해 만든다.
- #15 Support(이하영) 승인은 휴가로 받지 않았다. 근거는 승인 대상 조정 코멘트(REVIEW_AUTHORITY_POLICY §1·§4)다. 이 증적 PR의 독립 리뷰는 §3.1대로 유지한다.

AI 사용: CLAUDE_ASSISTED (결정안·명령·부하 생성기·판정 계산 준비, 수신 대조·문서화, 서버 명령 실행은 담당자 본인)
