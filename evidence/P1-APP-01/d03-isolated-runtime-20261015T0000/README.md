# P1 D03 두 번째 격리 회차 — bind 권한에 따른 스키마 미적용 실패

**RUN202610150000은 10/15 00:01:31~34 KST에 DB 기동 뒤 schema 조회에서 FAILED로 종료됐다. POST0, cleanup_confirmed=true다.** DB 로그와 사후 mode가 bind 디렉터리 접근 실패를 확인한다. D03 실패 처리 계약/APP/E2E 인수는 아직 미충족이다. CODEX_ASSISTED · 작성/실행 이권욱 · 독립 증적 편입 리뷰 대기.

## 기준·결정·시각

- 실제 실행 코드: [PR35](https://github.com/321Team/fds-msa/pull/35) merge `016390855fcec335e941b811123bb11b88015610`, 승인 HEAD `cbbdd90424829e9f0062db5be13cd1814d7a2f54`, [이재환 독립 승인](https://github.com/321Team/fds-msa/pull/35#pullrequestreview-5518212440)·필수CI38562811319 SUCCESS. tree/source 일치. 후보 이미지2 jobs SKIPPED.
- 기존 [PR230](https://github.com/321Team/fds-project-evidence/pull/230)은 첫 회차(tmpfs 옵션 거부)의 CLEANUP_FAILED/POST0 및 사후 부재를 보존해 병합했다. 이번 회차와 결과를 합치거나 첫 원본을 수정하지 않는다.
- [직전 제안](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6168990088)22:20~22:30/22:50 창을 그대로 사용하지 않았다. 사용자 직접 회신 **“실행창 비어있음. 지금 착수”**를 받아 같은 범위의 즉시 작업을 **10/15 00:00~00:10 시작/00:30 정리 종료**로 기록했다. [결정 기록](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6171377353), `decisions/USER_DECISION.json`·plan/auth·GitHub readback을 연결한다. 사용자 지시의 적용·시간 변경을 독립 리뷰어의 실행 GO로 표시하지 않는다.
- 고정 plan SHA `256dbf22a82600ed78212e1f862669b62cf1cea49d79559c3addf31bf7ea6ef6`. 기존 제안 대비 RUN만 바뀌고 source/이미지/cases/최대7POST·4컨테이너·900초 상한은 동일하다. 실제 별도 claim으로1회 소비, 자동재실행0.
- 실행·수신 경로: cicd-runner01/UID1000 server01_cicd-runner/rootless Podman6.1.0. strict SSH로 직접 실행·바이트 수신. 소스/argv/time/rc는 `transport/`, `received/`에 보존하며 콘솔 제출 사본이 아니다.

## 실제 경과

| 단계 | 원본과 판정 |
|---|---|
| 00:01:10 직전 조회 | GitHub online/busy=false, Worker0·컨테이너0·18081미사용, MemAvailable8867MiB, 앱2 config ID/DB config ID·RepoDigest 일치. 기존credential부재/claim유지, 새claim/output/번들경로 부재 |
| 00:01:17~19 준비 | 새 번들 SHA `ebc6c643…` 배치/source10·manifest16/전체17파일 대조. 실제 loopback helper2 PASS, 전후 Worker0/컨테이너0/포트미사용. 앱/DB Runtime 아님 |
| 00:01:31~34 Runtime | DB create1/start1 rc0, check-container rc0 뒤 첫 schema query rc3: `relation "alembic_version" does not exist`. API/engine/fixture 미생성, POST/케이스0 |
| 원인 증적 | DB 로그 `find: '/opt/app-root/src/postgresql-start': Permission denied`; 사후 stage/code·hooks 실제0700, 내부파일0644. hooks label `container_file_t:s0`. tmpfs 옵션 오류는 이 회차에서 발생하지 않음 |
| 정리 | 정확 DB CID의 logs→rm --force --time=5 rc0→exists rc1. 원본 FAILED/cleanup_confirmed=true, env2 제거 |
| 00:01:42 회수 / 00:03:09 보완 | helper10/runtime40의 단계별 서버 사본50 수신·해시 대조. 네 정확 이름 각각exists rc1·전체컨테이너0·credential부재·POSTintent0·claim SHA보존. 추가create/start/POST 없음 |

## 원인·해석·후속

보조 supervisor는 비밀값 보호를 위해 umask077을 유지한다. `Path.mkdir(mode=0755)`는 이 umask를 상속해0700이 되며, rootless bind의 host 소유자는 컨테이너 root로 매핑된다. UID26 DB 계정은0700 hooks를 탐색할 수 없어 schema hook이 실행되지 않았다. UID10001 앱 계정이 사용할 code 디렉터리도 같은0700이므로 같은 결함 범위로 다룬다. 단순 DB 기동·check-container 성공만으로 schema 준비를 확인할 수 없다는 점도 보존한다.

[수정 PR36](https://github.com/321Team/fds-msa/pull/36)은 비밀값 없는 read-only bind 루트 code/hooks만 명시적으로0755로 만들고 출력/부모stage0700·credential0600·파일0644·umask/SELinux/:ro,z/UID를 유지한다. 원 실행 번들·mode·실패 원본은 변경하지 않았다. 수정 코드는 이 회차에 실행되지 않았다. 독립 리뷰·CI·병합과 새 회차/시간창 결정이 끝나기 전 추가 Runtime을 실행하지 않는다.

## 읽는 순서와 검증 한계

1. `received/runtime/FDS_D03_202610150000/`의 `result.json`, `011-command.json`, `014-command.json`, `cleanup.json`.
2. `records/POSTFAILURE_READBACK.json`: 직접 mode/context·4개 정확 이름·credential부재·claim. 오류 원본을 덮어쓰는 기록이 아니다.
3. `decisions/`와 `records/USER_AUTHORIZATION_GITHUB_READBACK.json`, invocation intent/receipt, claim.
4. `provenance/`·source/plan hash, 준비/helper 및 fresh image 관측.
5. `verify.py`, `RECEIVED_INDEX.json`, `VERIFIED.json`, `SHA256SUMS`.

- 단계별 직접 서버 사본50개(helper10/runtime40, plan/auth 중복 포함)와 로컬 결정·provenance/SSH transport를 합친80개 입력을 Index로 구분한다. 80개 전부가 독립 서버 원본인 것은 아니다. image 계층/OCI archive는 미수신이며 기존 공급과 fresh config ID/digest로 연결한다. 새 load/pull/build/scan/Push/Deploy 없음.
- 원본 CRLF/LF 바이트를 변환하지 않는다. `db.env`·`api.env`의 값은 읽거나 반출하지 않았고 삭제·부재만 확인했다. 개인키/토큰/JWT 패턴을 검사했다. 명령의 `--env-file` 경로 표기는 credential 값이 아니다.
- helper result는 결정 파일 배치 전에 생성된 원본이며, 이후 decision_directory/plan SHA는 stage transport 결과에 기록된다. 둘을 덮어써 일치시킨 것으로 표시하지 않는다.
- source의 독립 승인은 d03_lab 실행 코드 범위다. SSH transport·수집/보조 supervisor는 **REVIEW NOT PERFORMED**이며 source/receipt를 보존했다. 이번 실패 원인에 supervisor의 umask 상속이 관련됨을 숨기지 않는다.
- `verify.py`의 EVIDENCE_VERIFICATION PASS는 실패 증적 결속 확인이다. DB schema/쓰기·D03 세 실패 경로 검증은 완료되지 않았다. PG16.8/운영16.14 차이·새DB취약점스캔 미수행·운영K8S/TLS 제외·production_runtime_claim=false를 유지한다.
- APP15/E2E20/Review30 OPEN·기존AC/완료일, DB11 종결을 유지한다. 이 PR은 실패 원본 편입이며 인수/Phase1 종결이 아니다.
