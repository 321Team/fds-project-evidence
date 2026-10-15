# AC09 DB 사후 거래 행 대조 결과

사용자가 전달한 **2026-10-15 16:22:17 KST** `server08@db01` 콘솔 결과를 보존하고 로컬에서 기존 API 원문과 대조했다. **R1·R2 모두 같은 거래 ID의 DB 행 내용 일치로 판정한다.** 이 후속 READ ONLY 조회는 16:06:17에 반환한 배포 작업창을 다시 점유하거나 16:20 보안 수용을 연장한 실행이 아니다.

## 수집·무결성

- 콘솔 `db01/server08`, DB `fdsdb/postgres`, timezone `Asia/Seoul`, `transaction_read_only=on`, `AC09_DB_AFTER_RC=0` 및 psql rc0 확인.
- [사용자 원문](USER_CONSOLE_OUTPUT.txt)을 그대로 보존했다. 전달 텍스트에서 LF로 재구성한 결과 6파일과 고정 SQL의 SHA256 **7개 전부**가 사용자 제공 값과 일치한다. 비어 있는 stderr도 해당 SHA와 일치한다. 재구성 파일을 새 원격 수집 파일로 표시하지 않는다.
- SQL SHA `8bb9b1c3d32fea5c821064547341b369aebae6a0b8b3de6606a743dd8ff3694c`, DB JSONL SHA `993b2e9588945e1e31551e61c94788756b7356670a475cca7cb88acf22d83a4f`.
- [실제 로컬 검증 결과](VERIFICATION.json), [대조 절차](verify_received_evidence.py). 중앙은 추가 SQL·SSH·POST를 실행하지 않았다. 실행자는 사용자이며 중앙은 수신 증적을 검증했다.

## API 원문과 실제 행

| 항목 | R1 이전 이미지 | R2 현행 이미지 |
|---|---|---|
| 거래 ID | `22b7c46c-cd07-4539-a7fc-8890b67b12ee` | `1827bd8a-a921-49f9-83f7-22529e903451` |
| 해당 계정 또는 ID의 행 수 | 1 | 1 |
| 계정·금액·통화·유형·source_ip | 실제 요청과 일치, 10000 KRW deposit | 실제 요청과 일치, 10000 KRW deposit |
| occurred_at | 15:48:17.993816 KST, 요청 UTC와 같은 순간 | 15:56:28.439537 KST, 요청 UTC와 같은 순간 |
| received_at | 15:48:19.508568 KST | 15:56:29.942495 KST |
| FDS | detected=false, skipped=false, R01/R02/R04/R07 false/detail null | 동일 |
| 판정 | SAME_ID_DB_ROW_CONTENT_MATCH | SAME_ID_DB_ROW_CONTENT_MATCH |

기존 `runtime-1535/r1-post-one/stdout.json` 및 `r2-post-one/stdout.json`의 실제 POST·HTTP 201·응답 body SHA를 확인하고 입력/응답 공통 **10항목**을 각각 대조했다. `received_at`은 API 입력/응답에 없는 DB 고유 필드로서 원문과 관측 구간을 별도로 확인했다. 양 값은 해당 HTTP 시작~종료 관측 사이에 있으나, 이를 새 지연 기준이나 엄격한 시계 오차 입증으로 사용하지 않는다. jsonb의 필드 순서를 내용 불일치로 보지 않고 Rule ID별 의미와 중복/누락 여부를 대조했다.

## 남은 구분

DB 사후 행 미수집 상태는 해소됐다. 과거 사전 0행 미수집 이력은 보존하며 사후 조회로 소급 증명하지 않는다. 기존 HTTP/계측/정리·작업창 반환 결과는 그대로 유지한다. **SEC 15/30분 시각 증적 사후 판정과 AC09 최종 인수는 아직 미완료**다. 수신된 DB 결과로 시각 조건이나 전체 Phase 1 완료를 선언하지 않는다.

기존 실행자의 봉인된 446파일 및 manifest를 수정하지 않고 이 별도 후속 폴더에 추가했다.
