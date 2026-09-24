# P1-E2E-01 — 직접 재수집 (2026-09-25)

[fds-project-evidence PR #31](https://github.com/321Team/fds-project-evidence/pull/31)에서 지적된 "R01/R02/R04/R07 시험값 미수신" 상태를 해소하기 위한 자료다. 담당 Lead 본인(이재환, supreme33-kr)이 db01에서 직접 DB를 조회했다.

## 수집 정보

| 항목 | 값 |
|---|---|
| 대상 | db01(10.1.93.55), `fdsdb.transactions` 테이블 |
| 실행자 | 이재환(supreme33-kr) 본인, db01에 직접 SSH 접속하여 `psql`로 조회 |
| 수집 시각 | 2026-09-25 (KST) |
| 방식 | 신규 거래를 발생시키지 않고, 기존에 실제로 트리거됐던 거래 레코드를 `fds_rules IS NOT NULL` 조건으로 조회 |

## 파일 목록

- `fraud-rules-db-evidence.txt` — R01/R02(2026-09-23 10:18대 연속 트리거)·R04(2026-09-23 01:18 심야 고액거래)·R07(2026-09-22 17:00, 2026-09-09 소액분산이체) 4개 룰 전부 `triggered: true` 사례를 DB 레코드로 직접 확인.

## 대응 관계

이 자료의 R01/R02 트리거 레코드는 [P1-MON-01 direct-recapture](../../P1-MON-01/direct-recapture-20260925T012800Z/)의 `discord-screenshot.png`에 찍힌 `FDSDetectionBurst`(R02 관련) alert와 같은 계열의 이상거래 탐지 파이프라인이 정상 동작 중임을 뒷받침한다.

## 이번에 하지 않은 것

- 신규 거래 발생(재실행) 없음 — 이미 존재하는 레코드 조회만 수행.
- 단위테스트 재실행 없음(`fds-msa/fds-engine/tests/test_rules.py` 16개 PASS는 기존 기록 유지, 이번 재수집 범위 아님).

AI 사용: CLAUDE_ASSISTED (담당자 본인이 직접 쿼리를 실행했으며, Claude는 쿼리 작성·결과 정리·파일화만 수행)
