# P1-DR-01 — PostgreSQL Backup → 격리 Restore → 원본 직접 비교 리허설 (2026-09-29 12:15~12:17 KST)

DR Lead(이재환)가 db01에서 운영 `fdsdb`를 `pg_dump`로 백업하고, 새 격리 DB `fdsdb_dr_20260929`에 `pg_restore`로 복구한 뒤 원본과 행 단위로 비교했다. 명령은 담당자가 db01(`server08`)에서 직접 실행했다.

[2026-09-15 콘솔 기록](../console-restore-test-20260915/README.md)에서 한계로 남은 세 가지 — 성공한 `pg_restore` 실행 화면, 원본·복구본 직접 비교, `alembic_version` 조회 — 를 이번 실행 로그로 보완한다.

**운영 변경**
- 운영 `fdsdb`는 읽기만 했다(`pg_dump`, `SELECT`).
- 새 격리 DB `fdsdb_dr_20260929` 생성·복구. **Restore 후 E2E 방식 결정 전까지 삭제하지 않고 유지한다.**
- 보관 디렉터리 `/var/lib/pgsql/fds-evidence/`(postgres:postgres 700) 생성, dump 파일 1개 저장 후 권한 600으로 정정(아래 "권한 정정")

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `db01/` | `~/p1-dr-20260929/` (`dr-rehearsal.log`, `perm-fix.log`) | 1,591 B, SHA-256 `5d06c9f3…84e224c8` | 서버 `sha256sum`과 로컬 복원본 일치(파일별 서버 Hash 없음) |

**dump 원본은 이 저장소에 넣지 않았다.** 거래 데이터가 들어 있어 [9/27 보관 위치 결정](https://github.com/321Team/fds-project-baseline/issues/21#issuecomment-5852937013)대로 db01에만 둔다.

| 항목 | 값 |
|---|---|
| 위치 | db01 `/var/lib/pgsql/fds-evidence/fdsdb_backup_20260929T121555.dump` |
| 형식·크기 | PostgreSQL custom format(`pg_dump -Fc`), 51,491 B |
| SHA-256 | `ffc96357cfa0b933892591ccf715296ced74752412cb405a8fe8325fe4139f4a` (정정 전후 동일) |
| 권한 | 디렉터리 `drwx------ postgres postgres`, 파일 `-rw------- postgres postgres` |
| 접근 | db01 sudo → `postgres` peer 인증. 비밀번호를 쓰지 않았다 |

## 결과 (`db01/dr-rehearsal.log`)

| 항목 | 결과 |
|---|---|
| Source DB | PostgreSQL 16.14 (`show server_version`, `select version()`), `pg_dump`/`pg_restore` 16.14 |
| 원본 상태 | `alembic_version=0003`, `transactions` 1,209행(`received_at` 2026-08-27 12:06:57 ~ 2026-09-27 19:13:01 KST) |
| Backup | 12:15:57 KST, `pg_dump rc=0`. TOC: `pgcrypto` 확장, 테이블 2(`alembic_version`, `transactions`), 데이터 2, PK 2, 인덱스 2 |
| Restore | `createdb -O fds_app` rc=0, `pg_restore -v` **rc=0** |
| 복구 순서 | 확장 → 테이블 생성 → 데이터 적재 → PK 제약 → 인덱스 → ACL (`pg_restore -v` 출력 순서) |
| 원본·복구본 비교 | 둘 다 `alembic_version=0003`, 1,209행, **행 전체 md5 `93d60e0f4f9801915b4361e716055120` 동일**(`transaction_id` 순 `row::text` 연결), 인덱스 3개 동일, 소유자 `fds_app` 동일 |
| 대표 Transaction/FDS Result | 최근 3건(`SIM_ha22_20260927`, `SIM_mon_ac2_…T052217Z`, `SIM_mon_ac2_…T051949Z`)의 금액·`fds_detected`·`fds_rules`(R01/R02/R04/R07)가 두 DB에서 같다 |
| 접근 통제 | `pg_hba_file_rules` 원격 규칙은 `hostssl fdsdb fds_app` + 출발지 `.105/.107/.108/.50` + `scram-sha-256`만 존재 |

## 권한 정정 (`db01/perm-fix.log`)

`pg_dump`가 기본 umask로 파일을 만들어 dump가 **644**로 생성됐다. 디렉터리가 700이라 다른 계정은 접근할 수 없었지만 9/27 결정(파일 600)과 달라, 12:17:44 KST에 `chmod 600`으로 정정했다. 원본 로그는 수정하지 않고 정정 기록을 별도 파일로 남겼다. 정정 전후 SHA-256은 같다.

## 한계와 후속

- **Restore 후 E2E는 이 기록에 없다.** 방식(복구본을 앱이 실제로 쓰게 하는 방법)은 DR Lead 결정 대기다.
- 로그의 SAMPLE에는 시험 거래의 `account_id`·금액·`fds_rules`가 들어 있다. 모두 `SIM_` 시험 계정이다. `source_ip`와 비밀값은 포함하지 않았다.
- 행 md5 비교는 같은 서버·같은 세션 설정에서 한 것이다. 서버 간 이동 복구는 이 기록의 범위가 아니다.
- 9/3 dump(`fdsdb_backup_20260903.dump`)의 db01 이전은 별도로 남아 있다.
- Runbook은 별도 작성 대상이다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
