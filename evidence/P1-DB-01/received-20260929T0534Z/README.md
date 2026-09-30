# P1-DB-01 — Credential 하드코딩 검사 · 시간대/Timestamp 저장 기준 확인 (2026-09-29)

[#11](https://github.com/321Team/fds-project-baseline/issues/11) 핵심 요구 중 "Credential을 Source에 하드코딩하지 않는다"와 "시간대와 Timestamp 저장 기준을 고정한다"의 잔여 근거를 보완한다. 본문 기록상 잔여는 각각 "전체 Source/자격정보 참조 대조 기록 미확인", "세션 timezone GUC, 명시 입력 offset/naive 처리 및 승인 계약 대조"였다.

**운영 변경:** 없음. 시험 거래 3건(`SIM_tz_143441_naive|utc|kst`, deposit 1,500,000)이 운영 `fdsdb`에 남아 있다.

## 수신·대조

| 폴더 | 원본 | archive | 대조 |
|---|---|---|---|
| `edge01/` | 서버 `~/p1-db-tz-20260929/` (`naive.json`·`utc.json`·`kst.json`·`results.log`) | `db-tz-edge01.tgz` 577 B, SHA-256 `18217064…4452feca` (+`.sha256`) | 서버 `sha256sum`과 수신 archive 일치. 개별 파일 4개는 archive 내부와 바이트 동일(`cmp`) |
| `db01/` | 서버 `~/p1-db-tz-20260929-db01.log` | `db-tz-db01.tgz` 267 B, SHA-256 `a15e43a6…6de0104f` (+`.sha256`) | 서버 `sha256sum`과 수신 archive 일치. 개별 로그는 archive 내부와 바이트 동일 |
| `local/` | 담당자 PC에서 Claude Code가 실행한 `git grep`/`git log -p` 결과 | 없음 | **서버 원본이 아니라 로컬 재현 기록**이다. 대상 저장소·커밋 SHA와 패턴을 파일 머리에 적었다 |

archive 2개의 내부 목록은 `registry/ARCHIVE_CONTENTS.json`에 등록했다.

## 1. Credential 하드코딩 검사 (`local/credential-scan-local-20260929.txt`)

| 대상 (origin/main) | 파일 수 | 비밀번호 포함 DSN | `password` 등 할당 |
|---|---|---|---|
| fds-msa `5271e606` | 99 | 8곳 — 모두 시험용·자리표시자 | 0 |
| infra-kubernetes `032c208a` | 349 | 0 | 1곳 — 가림 기능 시험 입력 `synthetic-password` |
| infra-monitoring `352ebfc1` | 89 | 0 | 1곳 — 시험 입력 `never-accept-secret-value` |
| infra-db `ab603a9c` | 4 | 0 | 0 |
| infra-ansible `96b49a5c` | 260 | 0 | 1곳 — 가림 기능 시험 입력 `VerySecret123` |
| fds-msa **Git 이력 전체**(95커밋) | — | 고유값 5종 — 모두 시험용·자리표시자 | 0 |

fds-msa에서 나온 DSN의 성격:
- `candidate:candidate@127.0.0.1` — 후보 이미지 워크플로의 `--network none` 격리 컨테이너용 가짜 값
- `test:test@localhost` — 단위 시험의 `os.environ.setdefault` 기본값
- `user:pass@10.1.93.55` — `transaction-api/app/db.py` 주석의 형식 예시
- `fds_app:CHANGE_ME@10.1.93.55` — `references/upstream/…/secret.example.yaml` 예시 파일

앱은 `DATABASE_URL = os.environ["DATABASE_URL"]`(`transaction-api/app/db.py`)로 접속 정보를 받는다.

`tools/check_source.py`는 개인키와 GitHub 토큰 패턴만 검사하므로 이 판정의 근거로 쓰지 않았다.

**범위 밖:** 클러스터 Secret 값 자체, 비밀번호 회전 이력(#19 비밀정보 후속 항목), 이 5개 외 저장소.

## 2. 시간대·Timestamp 저장 기준 (`edge01/`, `db01/`, 2026-09-29 14:34 KST)

같은 시각(2026-09-28 17:30 UTC = 2026-09-29 02:30 KST)을 세 형식으로 보냈다. 경로는 edge01 → Worker `.105:30080`이다.

| 입력 형식 | `occurred_at` | 응답 | DB 저장 (`at time zone` UTC / KST) |
|---|---|---|---|
| offset 없음(naive) | `2026-09-28T17:30:00` | 201, **R04만 true**("심야(KST 02시)") | 17:30 / 02:30 |
| UTC | `2026-09-28T17:30:00Z` | 201, R04만 true | 17:30 / 02:30 |
| KST | `2026-09-29T02:30:00+09:00` | 201, R04만 true | 17:30 / 02:30 |

- `occurred_at`·`received_at` 컬럼은 `timestamp with time zone`이고, DB 세션 `TimeZone`은 `Asia/Seoul`이다. DB/Role 단위 timezone 설정은 없다(같은 날 P1-DR-01 `db01/e2e-pre.log` 기준, [evidence#67](https://github.com/321Team/fds-project-evidence/pull/67)).
- offset이 없는 입력도 **판정(fds-engine, 코드상 UTC 간주)과 저장(transaction-api→DB)이 모두 UTC로 해석**해 같은 순간이 됐다. 판정과 저장 사이의 기준 불일치는 관측되지 않았다.
- 승인 계약과 대조: 계약 v1.0(`fds-msa/docs/transaction-api_fds-engine_contract_v1.0.md`)은 `occurred_at`을 ISO8601 UTC로 정의하고, 2026-09-03 팀 결정(`fds-engine/app/rules.py` 머리말)은 판정을 KST 기준으로 한다. 이번 결과는 "UTC 기준 순간 저장 → KST로 판정·표시"와 일치한다.

## 한계와 후속

- offset 없는 입력을 UTC로 저장하는 동작은 DB 드라이버가 naive 값을 **컨테이너 로컬 시간대**로 해석하기 때문으로 보인다(현재 UTC로 관측, 컨테이너 TZ 설정은 직접 확인하지 않음). 10/5 이미지 전환 후 컨테이너 시간대가 달라지면 결과가 바뀔 수 있으므로 전환 후 회귀에 naive 입력 1건을 포함한다.
- 핵심 요구 "transaction-api 승인 경로만 허용"(최종 허용 목록 적용 전), "Client와 fds-engine 직접 DB 접근 차단"(음성 시험 전)은 이 기록의 범위가 아니다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·로컬 검사 실행·문서화, 서버 명령 실행은 담당자 본인)
