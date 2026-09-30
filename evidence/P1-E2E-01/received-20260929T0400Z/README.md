# P1-E2E-01 — 회귀 시험 1회차: Rule·Negative·API/DB/Metric 연결 (2026-09-29 13:00~13:03 KST)

E2E Lead(이재환)가 정본 클러스터의 현재 이미지로 회귀 시험을 실행했다. 시험 전에 합격 기준을 edge01 서버 파일로 기록하고 SHA-256을 남긴 뒤 요청 24건을 보냈으며, 각 거래를 Transaction ID로 API 응답·DB 행·Prometheus Metric 증가분과 대조했다. 명령은 담당자가 edge01·db01(`server08`), k8s-control01(`server02`)에서 직접 실행했다.

이 회차는 10/5 DEC-P1-IMG-01 이미지 전환([#110](https://github.com/321Team/fds-project-baseline/issues/110)) **전** 이미지 기준이다. 전환 후에는 같은 기준으로 다시 실행한다.

**운영 변경:** 없음. 시험 거래 22건(`SIM_rg_202609291300_*`)이 운영 `fdsdb`에 남아 있다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-e2e-rg-20260929/` (환경·Metric 전후, N08) | 828 B `cb971a10…664a38c7` | 서버 `sha256sum`과 로컬 복원본 일치 |
| `edge01/` | `~/p1-e2e-rg-202609291300/` (기준, 요청 응답 24개, 결과·판정) | 2,859 B `8cb2faaa…942a8dc1d` | 서버 `sha256sum`과 로컬 복원본 일치. `criteria.txt` SHA-256 `8aad7cc2…fc83aae8d8`이 시험 때 기록한 `criteria.sha256`과 일치 |
| `db01/` | `~/p1-e2e-rg-20260929-db01.log` | 946 B `bb9fe2a3…7770e6eab` | 서버 `sha256sum`과 로컬 복원본 일치 |

파일별 서버 Hash는 받지 않았다. archive 단위로 대조했다.

## 실행 환경 (`control01/env-before.txt`)

| 항목 | 값 |
|---|---|
| transaction-api | `10.1.93.54/fds/transaction-api@sha256:a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` (Pod 3, worker01/02/03) |
| fds-engine | `10.1.93.54/fds/fds-engine@sha256:5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` (Pod 3, worker01/02/03) |
| 경로 | edge01 → Worker:30080(`.105/.107/.108` 순환, 8건씩). edge01 nginx(:80) upstream은 아직 E-K3S라 Client→edge(:80) 경로가 아니다 |
| 계정·출발지 | `SIM_rg_202609291300_<케이스>`, `source_ip=198.51.100.10`(문서용 IP) |

## 기준 기록 순서 (`edge01/criteria.txt`, `criteria.sha256`)

한 명령 안에서 `criteria.txt` 작성 → `sha256sum` 기록 → 요청 순서로 실행했다. 파일 mtime은 13:00:24(초 단위), 첫 요청은 13:00:24.044다. 초 단위로는 같지만 명령 순서상 기준 기록이 먼저 끝났다. 기준 내용은 시험 뒤 바꾸지 않았다.

## 결과

**케이스 판정 (`edge01/judge.txt`, `results.log`) — 24 PASS / 0 FAIL**

| 구분 | ID | 입력 | 기대 | 실제 |
|---|---|---|---|---|
| Positive | P01 | deposit 10,000 | 모두 false | ✅ |
| | P02 | deposit 3,000,000 (R02 경계) | R02만 | ✅ |
| | P03-1~4 | withdrawal 10,000 ×4 | 1~3 false, 4번째 R01만 | ✅ |
| | P04-1~4 | transfer 700,000 ×4 | 1~3 false, 4번째 R07만 | ✅ |
| | P05 | deposit 1,500,000, `occurred_at` 02:30 KST | R04만 | ✅ |
| Negative | N01 | deposit 2,999,999 | 모두 false | ✅ |
| | N02 | deposit 1,500,000, 05:00 KST (R04 종료 경계) | 모두 false | ✅ |
| | N03 | deposit 999,999, 02:30 KST | 모두 false | ✅ |
| | N04-1~4 | transfer 100,000 ×4 (합산 미달) | 모두 false | ✅ |
| | N05-1~4 | deposit 10,000 ×4 (유형 불일치) | 모두 false | ✅ |
| | N06 | `transaction_type=refund` | 422 | ✅ |
| | N07 | `amount` 누락 | 422 | ✅ |

모든 201 응답은 `fds_evaluation_skipped=false`, `fds_detected`는 트리거 유무와 일치했다.

**N08 비승인 출발지 (`control01/n08.txt`):** control01(`.102`) → Worker 3대 `:30080/readyz` 모두 `000`.

**API ↔ DB (`db01/…db01.log`):** 22행. 201 응답 22건의 `transaction_id`와 DB 행이 1:1로 일치하고, `fds_detected`·`fds_evaluation_skipped`·트리거 Rule이 모두 같다(불일치 0). P05·N02·N03의 `occurred_at`은 요청값(02:30·05:00 KST)으로 저장됐다. N06·N07은 DB 행이 없다.

**Metric 증가분 (`control01/metrics-before.txt` 13:00:18 → `metrics-after.txt` 13:02:23)**

| Metric (Pod 합) | 전 → 후 | 증가 | 기준 |
|---|---|---|---|
| `transaction_save_success_total` | 2 → 24 | +22 | +22 |
| `transaction_save_failure_total` | 0 → 0 | 0 | 0 |
| `missing_client_ip_total` | 1 → 1 | 0 | 0 |
| `fds_evaluated_total` | 2 → 24 | +22 | +22 |
| `fds_detected_total{rule_id}` | R02 2 → R01 1·R02 3·R04 1·R07 1 | 각 +1 | 각 +1 |
| `up{job=~"transaction-api\|fds-engine"}` | 6 → 6 | — | 6 |

시험 전 값(2, 1, R02 2)은 같은 날 12:28 P1-DR-01 E2E 거래 1건(R02, `source_ip` 없음) 등 이전 거래의 누적이다. Metric은 Rule별 누적 카운터라 거래 단위로는 조인되지 않고 전후 증가분으로 대조했다.

**Pod (`env-before.txt`, `env-after.txt`):** 전후 모두 Ready, `restartCount` 변화 없음(transaction-api 0/0/1, fds-engine 0/2/0 — 시험 전 값).

## 한계와 후속

- 10/5 이미지 전환 전 회차다. 전환 후 같은 기준으로 재실행해야 AC "Regression 결과와 Defect 상태가 승인된다" 판정 입력이 된다.
- Client→edge01(:80) 경로가 아니라 edge01→Worker NodePort 직접 경로다(edge01 이관 전).
- FDS 엔진 장애(fail-open) 케이스는 이번 회차에서 실행하지 않았다.
- Defect 0건이라 "실패 재현과 수정 버전 기록" 절차는 이번에 실행되지 않았다.
- 시험 거래 22건은 운영 DB에 남아 있다(`SIM_` 접두사).

AI 사용: CLAUDE_ASSISTED (명령·판정 스크립트 준비, 수신 대조·API/DB 대조·문서화, 실행은 담당자 본인)
