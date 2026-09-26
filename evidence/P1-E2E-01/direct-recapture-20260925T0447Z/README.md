# P1-E2E-01 — Lead 직접 재수집 원본 (2026-09-25)

[PR #31](https://github.com/321Team/fds-project-evidence/pull/31)이 지적한 "R01/R02/R04/R07 시험값" 항목에 대해, 담당 Lead(이재환, supreme33-kr)가 db01에서 `psql`로 기존 거래 레코드를 조회한 **출력 파일 그대로**를 편입한다. 손으로 고치지 않았다. 이 PR의 이전 커밋(`0110c05`)의 `fraud-rules-db-evidence.txt`는 정리본이었고 설명 문장에 잘못된 SQL과 잘못된 시각(09:18)이 있었다. 이번 커밋에서 원본으로 교체했다([하영님 리뷰](https://github.com/321Team/fds-project-evidence/pull/37#pullrequestreview-5313449647)).

## 수집 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이재환(supreme33-kr) 본인, db01 계정 `server08` |
| 시각 | 2026-09-25T04:49Z (13:49 KST), `commands.log` 참조 |
| 실행 | `psql -U fds_app -h 127.0.0.1 -d fdsdb -f queries.sql` 1회. 결과는 `\o`로 파일마다 저장 |
| 방식 | 신규 거래를 발생시키지 않았고 기존 레코드만 조회했다(SELECT 전용) |
| 검증 | 압축본 SHA-256 `de7261699efbbee2ea7c616792b54e43d9b0d893449e099659f841d437934008`이 서버 출력과 일치, `server-SHA256SUMS` 19개 항목 모두 일치 |

## 파일 목록

- `queries.sql`: 실행한 SQL 전문. 룰 조회는 `fds_rules::jsonb @> '[{"rule_id":"R04","triggered":true}]'` 형태다.
- `rules-recent20.txt`: 최근 20건(`fds_rules IS NOT NULL`, 시각 내림차순).
- `rules-r04-r07.txt`: R04 또는 R07이 `triggered:true`인 레코드(최대 5건).
- `rules-full-rows.txt`: 룰별(R01/R02/R04/R07) 최신 트리거 레코드 1건씩의 전체 컬럼(`\x` 형식). 입력값(`amount`, `transaction_type`, `account_id`, 시각)이 포함된다.
- `schema-transactions.txt`(`\d transactions`), `psql-info.txt`(버전·계정·시각), `hostname.txt`, `commands.log`, `server-SHA256SUMS`.

## 확인된 사실

- R01/R02/R04/R07 네 룰 모두 실제 DB 레코드에서 `triggered:true` 사례가 있다. 예: R04 `2026-09-23 01:18:25+09` 1,500,000원 출금("심야(KST 01시) 고액 거래"), R07 `2026-09-22 17:00:40+09`("1시간 내 소액 분산 이체 3건 / 합산 2,100,000원"), R01·R02는 `2026-09-23 10:18:54+09` 3,500,000원 출금 연속 요청("10분 내 인출 24회", "고액 거래 3,500,000원"). R02는 `2026-09-25 13:33:16+09` 레코드도 있다.
- 룰 임계값은 레코드의 `detail` 문자열에 함께 기록되어 있다(예: threshold 3, 3,000,000원).

## 미수신·미확인

- 정상 거래 E2E의 **요청·응답 원문**(HTTP). 이번에는 DB에 저장된 결과만 확보했다.
- 룰별 **기대값 표**(입력→기대 결과). 레코드는 실제 결과이며 기대값과의 대조는 별도 문서에 있다.
- 이번 조회 시점에 새로 발생시킨 거래는 없다.

AI 사용: CLAUDE_ASSISTED (실행은 담당자 본인, Claude는 SQL 작성·복원·검증·문서화)
