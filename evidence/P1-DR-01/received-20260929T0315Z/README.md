# P1-DR-01 — PostgreSQL Backup → 격리 Restore → 원본 비교 → Restore 후 E2E (2026-09-29 12:15~12:30 KST)

DR Lead(이재환)가 db01에서 운영 `fdsdb`를 `pg_dump`로 백업하고 새 격리 DB `fdsdb_dr_20260929`에 `pg_restore`로 복구해 원본과 행 단위로 비교했다. 이어서 짧은 작업창에서 DB 이름을 맞바꿔 정본 앱이 **복구본을 실제로 쓰게 한 상태로 E2E 거래 1건**을 처리한 뒤 원래대로 되돌렸다. 명령은 담당자가 db01·edge01(`server08`), k8s-control01(`server02`)에서 직접 실행했다.

[2026-09-15 콘솔 기록](../console-restore-test-20260915/README.md)의 한계 — 성공한 `pg_restore` 실행 화면, 원본·복구본 직접 비교, `alembic_version` 조회, Restore 후 E2E 없음 — 를 이번 실행 로그로 보완한다.

**운영 변경 (모두 원복)**
- 운영 `fdsdb`: `pg_dump`·`SELECT`로 읽음. E2E 작업창 동안 `ALLOW_CONNECTIONS false` → 이름 변경(`fdsdb_orig_20260929`) → 원래 이름·`ALLOW_CONNECTIONS true`로 복구. **데이터는 변경되지 않았다**(행 전체 md5 전후 동일)
- 앱 DB 세션 7개(`.50`×3, `.105`×2, `.107`×1, `.108`×1)를 두 번 종료. 앱·매니페스트·Secret·`pg_hba`·방화벽 변경 없음, Pod 재시작 없음
- 새 격리 DB `fdsdb_dr_20260929` 생성·복구. E2E 거래 1건이 추가된 상태로 **현재 유지 중**(삭제 여부는 DR Lead 결정)
- 보관 디렉터리 `/var/lib/pgsql/fds-evidence/`(postgres:postgres 700) 생성, dump 파일 저장 후 권한 600 정정
- 작업창은 12:23 KST 팀 카카오톡 대화방에 담당자가 공지했다("없으시면 db restore,e2e 테스트 진행을위해 잠깐 끊겠습니다"). 대화방 원문은 이 저장소에 편입하지 않았다

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `db01/` | `~/p1-dr-20260929/` 5개 파일 | ① 12:17 1,591 B `5d06c9f3…84e224c8`(`dr-rehearsal.log`·`perm-fix.log`) ② 12:30 2,155 B `3e4cc7be…6ea7205`(5개 전체) | 두 archive 모두 서버 `sha256sum`과 로컬 복원본 일치. ①의 두 파일은 ② 안의 같은 파일과 바이트 동일 |
| `edge01/` | `~/p1-dr-e2e-20260929-edge01.log` | 409 B `45566b31…3f750a20` | 서버 `sha256sum`과 로컬 복원본 일치 |
| `console/` | 없음 | — | control01 Pod 상태 콘솔 제출 원문. 서버 파일·Hash 없음 |

파일별 서버 Hash는 받지 않았다. archive 단위로 대조했다.

**dump 원본은 이 저장소에 넣지 않았다.** 거래 데이터가 들어 있어 [9/27 보관 위치 결정](https://github.com/321Team/fds-project-baseline/issues/21#issuecomment-5852937013)대로 db01에만 둔다.

| 항목 | 값 |
|---|---|
| 위치 | db01 `/var/lib/pgsql/fds-evidence/fdsdb_backup_20260929T121555.dump` |
| 형식·크기 | PostgreSQL custom format(`pg_dump -Fc`), 51,491 B |
| SHA-256 | `ffc96357cfa0b933892591ccf715296ced74752412cb405a8fe8325fe4139f4a` (권한 정정 전후 동일) |
| 권한 | 디렉터리 `drwx------ postgres postgres`, 파일 `-rw------- postgres postgres` |
| 접근 | db01 sudo → `postgres` peer 인증. 비밀번호를 쓰지 않았다 |

## 1. Backup → 격리 Restore → 원본 비교 (`db01/dr-rehearsal.log`, 12:15:55~57)

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

**권한 정정 (`db01/perm-fix.log`, 12:17:44):** `pg_dump`가 기본 umask로 파일을 만들어 dump가 644로 생성됐다. 디렉터리가 700이라 다른 계정은 접근할 수 없었지만 9/27 결정(파일 600)과 달라 `chmod 600`으로 정정했다. 원본 로그는 수정하지 않고 정정 기록을 별도 파일로 남겼다.

## 2. 작업창 전 확인 (`db01/e2e-pre.log`, 12:26:08)

| 항목 | 원본 `fdsdb` (oid 16389) | 복구본 (oid 32882) |
|---|---|---|
| 소유자·collation·인코딩 | fds_app / ko_KR.UTF-8 / UTF8 | 동일 |
| DB 권한 `datacl` | `{=Tc/fds_app,fds_app=CTc/fds_app}` | `(default)` — 기본값(PUBLIC 접속·임시, 소유자 전체)과 같은 실효 권한 |
| DB/Role 단위 설정 | 없음 | 없음 (서버 timezone `Asia/Seoul`) |
| 데이터 | 1,209행, md5 `93d60e0f…` | 동일 — 12:15 이후 신규 거래 없음 |
| 세션 | `.50`×3, `.105`×2, `.107`×1, `.108`×1 | 없음 |

`pg_dump`(`--create` 없이)는 DB 단위 권한·설정을 옮기지 않는다. 이번에는 실효 차이가 없었지만 Runbook에 복구 후 재적용 확인 단계로 넣는다.

## 3. Restore 후 E2E (`db01/e2e-swap.log`·`e2e-swapback.log`, `edge01/…edge01.log`)

| 시각(KST) | 단계 | 결과 |
|---|---|---|
| 12:28:10~13 | 교체: 원본 접속 차단 → 세션 7개 종료 → `fdsdb`→`fdsdb_orig_20260929`, 복구본→`fdsdb` | `psql rc=0`, `fdsdb` = oid **32882**(복구본) |
| 12:28:21 | edge01 → Worker 3대 `/readyz` | `200 200 200` |
| 12:28:21 | **E2E** `POST /api/v1/transactions` (`.105:30080`, `SIM_dr21_20260929`, 3,500,000 KRW, transfer) | **HTTP 201**, `transaction_id=fe2501ac-d2bb-456f-bcc6-dc1fe061229c`, `fds_detected=true`, R02 `triggered=true`, `fds_evaluation_skipped=false` |
| 12:28:50 | 복구본 확인 | 앱 세션 7개 모두 **oid 32882**에 연결. 복구본 1,210행, E2E 거래 저장(`received_at` 12:28:21.689948) |
| 12:28:50~54 | 원복: 복구본 접속 차단 → 세션 7개 종료 → 이름 원복 → 접속 허용 | `psql rc=0`, `fdsdb` = oid **16389**, `datallowconn=t` |
| 12:29:14 | 원복 확인 | 원본 **1,209행·md5 `93d60e0f…` 동일·E2E 거래 0건**. 복구본 1,210행(md5 `74b4549a…`)·E2E 거래 1건. 앱 세션 7개가 oid 16389에 재연결 |
| 12:30 | edge01 `/readyz`, control01 Pod | 3대 200. `restarts` 0/0/1(시험 전과 동일) |

DB 연결이 끊긴 시간은 교체 약 3초, 원복 약 4초다.

## 한계와 후속

- E2E는 거래 1건(R02 고액 거래)이다. 전체 Rule 회귀는 #20 최종 회귀에서 다룬다.
- E2E 요청은 edge01에서 Worker NodePort로 직접 보냈다. edge01 nginx(:80) upstream은 아직 E-K3S이며, E-K3S 세션도 작업창 동안 복구본에 연결됐다.
- E2E 거래는 복구본에만 남아 있고 운영 `fdsdb`에는 없다(의도한 결과).
- 로그의 SAMPLE·E2E 행에는 `SIM_` 시험 계정의 `account_id`·금액·`fds_rules`만 있다. `source_ip`와 비밀값은 포함하지 않았다.
- 행 md5 비교는 같은 서버·같은 세션 설정에서 한 것이다. 서버 간 이동 복구는 범위 밖이다.
- 9/3 dump(`fdsdb_backup_20260903.dump`)의 db01 이전, 격리 DB 삭제, Runbook 작성은 별도로 남아 있다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
