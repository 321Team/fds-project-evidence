# P1 D-03 격리 Runtime 첫 회차 — 컨테이너 생성 전 실패 보존

**RUN202610142110은21:10:13 KST DB create에서 실패했다. 앱 기동/POST0, D03 실패 처리 계약은 미검증이다.** 원본 `CLEANUP_FAILED`/rc1을 유지하며 사후 직접 조회의 객체·credential 부재와 구분한다. CODEX_ASSISTED · 작성/실행 이권욱 · 독립 증적 편입 리뷰 대기.

## 범위·기준·실제 경과

- 대상: APP #15 / E2E #20 / Review #30. 기존 OPEN/In Progress·완료일 유지. DB #11 종결을 재개하지 않는다.
- 실행 도구 [fds-msa PR34](https://github.com/321Team/fds-msa/pull/34) merge `192c5ab04a5e7469dcb45d19d620d3b71b33f72d`, 승인 HEAD `4e32e71d08c9510461cc5d4774968f53af814bbb`. [이재환 독립 승인](https://github.com/321Team/fds-msa/pull/34#pullrequestreview-5514692752), source validation [38530506527](https://github.com/321Team/fds-msa/actions/runs/38530506527) SUCCESS. 이미지 후보2 jobs SKIPPED.
- [AC05 회수·창 해제](https://github.com/321Team/fds-project-baseline/issues/16#issuecomment-6166968029)와 사용자 종료 통지 뒤 준비 재개. AC05 PR229 최종 편입/인수와 별개다.
- [구체 실행안](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6167792466) → [사용자 직접 결정 기록](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6167814983). 기존OCI2 load·고정DB pull, Runtime 최대1회/7POST, 시작21:10~21:20·정리21:40 KST, Runner 전용 확인. `decisions/` 원문·plan SHA로 결속.
- 실제 위치: cicd-runner01/UID1000 server01_cicd-runner/rootless Podman6.1.0. 기존 strict SSH 경로로 실행·수신했으며 콘솔 복사 제출이 아니다. argv/실행 SHA/UTC시각/rc는 `transport/` 및 `received/` receipt에 보존하며 본문은KST로 표기한다.

| 단계 | 실제 수행·판정 |
|---|---|
| 준비 20:53~54 | Worker0·컨테이너0·포트18081미사용, 고정번들 배치/source10·manifest18 해시, 실제 loopback helper2 PASS/rc0. 앱/DB Runtime 아님 |
| 공급 21:00:17~31 | 앱 OCI2 load·DB pull 각각1회/모두rc0. 이후 보조 검사 오류의 SUPPLY_STOP도 원본 보존 |
| 공급 보완 21:01:58 | 고정 index→platform manifest→config digest와 실제 image ID 대조. 공급 재시도0, 코드/plan/이미지 변경0 |
| Runtime 21:10:13 | claim 생성 뒤 DB `podman create`1회가rc125: `unknown mount option "uid=26"`. start0·POST0·케이스 결과0. API/engine/fixture 미생성 |
| 자동 정리 | 정확 DB 이름 exists rc1이나 CID 미확정이라 원본 `CLEANUP_FAILED`, cleanup_confirmed=false. db.env/api.env 제거 |
| 사후 확인 21:10:19 / 21:11:35 | 전체컨테이너0·Worker0·credential 부재, 추가로 네 정확 이름 exists 각각rc1. claim/SHA와 실패 원본 보존. 후속 rm/prune/재시도0 |

## 읽는 순서

1. `received/runtime/FDS_D03_202610142110/result.json`, `006-command.json`, `007-command.json`, `cleanup.json`.
2. `transport/postfailure-exact-absence-read/stdout.json`: 네 정확 이름·credential·POST intent·claim 사후 읽기. 원본의 정리 실패를 덮어쓰는 파일이 아니다.
3. `received/runtime/FDS_D03_RuntimeInvocation_202610142110/`의 intent/receipt와 `FDS_D03_Claims/202610142110.json`.
4. `decisions/`, `provenance/`, `records/REVIEW_CI_before_runtime.json`: 사용자 결정·정확 plan/hash·승인 source 연결.
5. `received/helper/`와 `received/supply/`, `transport/`: 실제 helper, 공급, 보조 검사 정정·회수.
6. `RECEIVED_INDEX.json`, `VERIFIED.json`, `verify.py`, `SHA256SUMS`: 편입 바이트와 판정 대조.

## 공급 검사 오류의 정정

보조 검증기가 `skopeo inspect --config` 출력의 SHA `d0614d…`를 실제 OCI config ID로 잘못 비교했다. 고정 amd64 manifest `sha256:862cf9364c60a1c47f1721b4700302a959969a09091a8434b3c64949730ed1f1`의 `config.digest`와 실제 Podman ID는 `sha256:5f7659016ef769811a0fdc349c9cad11f520dc7e147633bb1025e499002d9cd2`로 일치한다. index RepoDigest `d33717…`, User26/linux/amd64, 두 앱 config ID도 일치했다. 원 SUPPLY_STOP과 별도 `FDS_D03_SupplyValidation_202610142110/`을 함께 보존한다. [정정 기록](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6167968268). 실제 공급3명령은 재실행하지 않았다.

## 수신·검증과 한계

- `received/`는 단계별 직접 수신61개 파일 사본이다(helper10/supply22/runtime29, plan/auth 단계 간 중복 포함). `RECEIVED_INDEX.json`은 이 사본과 로컬 실행안/검증기/SSH receipt/결정 기록을 합친108개 입력의 복사 경로·크기·SHA를 구분한다. 108개 전부가 별도 서버 원본이라는 뜻이 아니다.
- 서버 manifest51항목과 수신 바이트를 대조했다. 이미지 계층·OCI archive 자체는 수신하지 않았고 공급 전SHA와 실제 image metadata로 연결한다. 원본 번들은 SHA `29b378e5…`, 원본source10개/실행plan7개SHA를 결속한다. Runtime이 stage한도구2개 bytes도 plan과 일치한다.
- `verify.py`는 시간창/plan/claim·명령7개·create1/start0·POST0·rc125·원본실패·사후부재·공급정정/이미지 결속·원본/manifest를 재검산한다. **EVIDENCE_VERIFICATION PASS는 Runtime PASS가 아니다.**
- raw와 문서는 줄바꿈 변환 없이 수신 바이트를 보존한다. db.env/api.env는 조회·편입하지 않았으며 사후 부재만 확인했다. token/개인키/JWT 패턴점검을 수행한다. 기존 image cache·claim·원본은 보존한다.
- source PR34의 독립 승인은 실제 `d03_lab.py` 실행 코드에 해당한다. 이 회차의 SSH transport/보조 공급·수집 검사기는 `REVIEW=NOT PERFORMED`이며 사용자 실행 범위 내 보조 실행/읽기를 구분해 source와receipt를 보존한다. 이를 독립 리뷰된 코드로 표시하지 않는다.
- DB16.8 이미지 공급은 완료했지만 DB 기동·쓰기·schema·read timeout/HTTP500/INSERT rollback은 모두미검증. 운영PG16.14와patch차이·새DB 취약점스캔 미수행·운영K8S/TLS 검증 제외를 유지한다. `production_runtime_claim=false`.

## 후속

[소스 수정 PR35](https://github.com/321Team/fds-msa/pull/35)에서 Podman6.1 옵션 파서가 거부하는 두 tmpfs의 uid/gid를 제거하는 수정안을 독립 리뷰한다. UID26:GID0·0770·자원/네트워크/정리/증적 기준은 유지하고 실제 기동은 새 승인 회차에서 확인한다. 이 회차 1회 승인은 소진됐으며 같은claim·번들에 덮어쓰거나 자동 재실행하지 않는다. 새 코드 리뷰/CI/병합 → 새 plan·RUN/창 결정 → 실제 시험 → 증적 편입·D03 처분 순서다. 이 PR은 실패·정리 한계·사후부재를 보존하는 편입이며 APP/E2E 인수 또는Phase1 종결을 요청하지 않는다.
