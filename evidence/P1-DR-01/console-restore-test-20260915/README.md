# P1-DR-01 — 격리 DB 복구 시험 콘솔 기록 (2026-09-15)

[baseline#21 증적 보완 요청](https://github.com/321Team/fds-project-baseline/issues/21)(2026-09-24, 이권욱)에 대해, 담당 Lead(이재환)가 2026-09-15 db01에서 실행하고 작업 세션에 붙여넣은 **콘솔 화면을 그대로** 편입한다. 요약이나 재작성이 아니다(파일마다 붙여넣은 내용 원문). 서버가 만든 파일 원본은 아니며, 명령 출력의 서버 로그·해시와 대조하지 않았다.

## 파일과 제출 시각

| 파일 | 제출 시각(UTC) | 내용 |
|---|---|---|
| `console-01.txt` | 2026-09-15T09:14:34Z | `pg_restore --version`, `pg_restore -l` 백업 TOC(작성 2026-09-03 17:31:15 KST, dbname `fdsdb`, PostgreSQL 16.14, TOC 15) |
| `console-02.txt` | 09:16:37Z | 격리 DB `fdsdb_repro_test_0915` 생성(`sudo -u postgres createdb -O fds_app`), 첫 `pg_restore` 시도(peer 인증 실패) |
| `console-03.txt` | 09:17:22Z | 조회 시도(peer 인증 실패) |
| `console-04.txt` | 09:17:48Z | 격리 DB 조회: `transactions` 15건, 대표 3건(`transaction_id`, `account_id`, `fds_rules`) |
| `console-05.txt` | 09:18:30Z | 정리 시도(`postgres` 비밀번호 인증 실패) |
| `console-06.txt` | 09:18:51Z | 격리 DB 삭제(`sudo -u postgres dropdb`), 임시 dump 삭제(이미 없음) |

실행 계정은 db01 OS 계정 `server08`이며 DB 접속은 `fds_app`(비밀번호 프롬프트)과 `postgres`(sudo peer)다. 비밀번호 값은 파일에 없다.

## 백업 파일

| 항목 | 값 |
|---|---|
| 파일 | `fdsdb_backup_20260903.dump` (PostgreSQL custom format, gzip) |
| 크기 | 5,206 bytes |
| SHA-256 | `80962dcd41c8afe3920c7194e8b5e2a4531ee901b4027aad1d47209ed4a46f3d` |
| 보관 위치 | 담당자 PC `C:\하이브리드클라우드09\팀프로젝트\db백업파일\` (2026-09-25 해시 재계산). 거래 데이터가 들어 있어 **이 저장소에는 넣지 않았다.** 팀 보관 위치 지정 필요 |
| 생성 | TOC 기준 2026-09-03 17:31:15 KST, `pg_dump` 16.14. 생성 명령 원문은 이 자료에 없다 |

## AC 대응 (판정하지 않음)

| AC | 이 자료로 확인되는 것 | 한계 |
|---|---|---|
| 운영 원본을 덮어쓰지 않음 | 복구 대상이 격리 DB `fdsdb_repro_test_0915`이며 운영 `fdsdb`가 아님(console-02). 시험 후 삭제(console-06) | 운영 `fdsdb`의 전후 상태 조회는 없다 |
| Backup 정상 생성·검증 | TOC가 `alembic_version`, `transactions`, PK 2개, 인덱스 2개, `pgcrypto`를 포함(console-01), 파일 SHA-256 | 생성 명령·시각 원문 없음 |
| 빈 대상에 Schema/Data 복구 | 격리 DB에서 `transactions` 15건 조회(console-04) | **성공한 `pg_restore -h 127.0.0.1 …` 실행 화면은 제출되지 않았다.** 복구 성공은 조회 결과로만 추정된다. `alembic_version` 조회 없음 |
| 대표 Transaction/FDS Result 일치 | 복구본의 대표 3건과 `fds_rules` 값(console-04) | 원본(운영 또는 dump) 쪽 같은 행 조회와의 **직접 비교는 없다.** 당시 세션이 dump를 오프라인 해석해 일치를 확인했다고 적었으나 그 출력은 이 자료에 없다(NOT VERIFIED) |

## 이번에 하지 않은 것

- dump 파일 편입, 새 복구 시험 실행, AC 체크·Status 변경.

AI 사용: CLAUDE_ASSISTED (실행은 담당자 본인, Claude는 세션 기록에서 원문 추출·문서화)
