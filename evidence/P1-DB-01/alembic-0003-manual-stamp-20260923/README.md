# P1-DB-01 — db01 `alembic_version` 0002→0003 수동 stamp 실행 기록 (2026-09-23)

[fds-msa PR #8](https://github.com/321Team/fds-msa/pull/8)의 리뷰 항목 B1-1("리뷰 전 운영 선반영의 **실행 당시** 기록")에 대응한다. 실행자는 P1-DB-01 Lead(이재환)이며, 이 기록은 담당 Lead가 콘솔에 붙여넣어 제출한 화면(`console-transcript.txt`)을 그대로 편입한 것이다.

## 실행 기록

| 항목 | 값 |
|---|---|
| 대상 | db01(10.1.93.55) `fdsdb`, 테이블 `alembic_version` |
| OS 계정 / 접속 | `server08` 셸에서 `psql -h 127.0.0.1 -U fds_app -d fdsdb` (DB 계정 `fds_app`, 비밀번호는 프롬프트 입력) |
| 실행 시각 | **2026-09-23 01:30:30~01:30:58 KST** (2026-09-22T16:30:30Z~16:30:58Z). 지시문 전달 시각(16:30:30Z)과 결과 제출 시각(16:30:58.411Z)의 사이다. 서버 쪽 정확한 시각(PostgreSQL 로그 등)은 대조하지 않았다 — NOT VERIFIED |
| 실행 전 조회 | `SELECT version_num FROM alembic_version;` → `0002` (1개 행) |
| 실행 SQL | `UPDATE alembic_version SET version_num = '0003';` (WHERE 절 없음. 이 테이블은 단일 행이라 `UPDATE 1`) |
| 실행 결과 | `UPDATE 1` |
| 실행 후 재조회 | 이 콘솔 자료에는 없다. 이후 2026-09-25 15:31 KST GWONUK의 읽기 전용 실측(fds-msa PR #8 코멘트)에서 `alembic_version = 0003`으로 확인됨 |

실행 목적: P1-DB-01 AC("Schema/Migration이 재현 가능하다")의 근거인 TC-SCHEMA 증적 카드를 PARTIAL_VERIFIED → PASS로 올리기 위해서였다(당시 작업 세션의 기록). 리뷰·승인 없이 실행됐다.

실행 경위: 작업 지시(AI 보조 세션)에 따라 db01 셸에서 `alembic stamp 0003`을 시도했으나 db01에는 저장소가 없어 실패했고(`cd: fds-msa: 그런 파일이나 디렉터리가 없습니다`, `No config file 'alembic.ini' found`), `alembic stamp`가 하는 일(단일 head의 버전 표식 변경)을 psql로 직접 수행했다. 해당 지시는 "승인 불필요"로 안내됐으나 운영 DB 변경이라 POLICY §3.1상 사전 리뷰 대상이었으므로 절차 이탈로 기록한다. 이 시점에 fds-msa PR #8(0003 revision)은 아직 없었다(2026-09-25 작성) — 즉 표식이 코드보다 먼저 바뀌었다.

## 자료의 성격과 한계

- `console-transcript.txt`는 **콘솔 제출 자료(붙여넣기)** 이며 서버가 만든 파일 원본이 아니다. 명령 출력의 SHA-256·서버 로그와는 대조하지 않았다.
- 실행 시각은 대화 기록 기준의 28초 구간이다. 정확한 시각은 확인하지 못했다.
- 인덱스 2종의 `indexdef` 전문은 이 기록에 없다. 2026-09-25 GWONUK 실측 결과를 참조한다.
- 사전 `pg_indexes` 조회(2026-09-23)의 전문은 이번 자료에 없다(별도 자료 필요).

## 되돌리기

`UPDATE alembic_version SET version_num = '0002' WHERE version_num = '0003';` (인덱스는 유지)

AI 사용: CLAUDE_ASSISTED (Claude는 콘솔 지시문 작성·기록 정리, 실행은 담당자 본인)
