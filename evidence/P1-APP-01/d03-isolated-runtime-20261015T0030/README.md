# D03 격리 Runtime — RUN 202610150030

**현재 판정: LAB_RUNTIME_PASS, POST 7회 / 저장 6행 / cleanup_confirmed=true.** 운영 환경 전체 검증이나 APP/E2E 최종 인수는 아니다. 독립 증적 리뷰·편입은 이 폴더를 다루는 PR에서 별도 판단한다.

## 실행·수신과 승인 근거

- 실행자 이권욱(CODEX_ASSISTED), 호스트 `cicd-runner01`, rootless Podman 6.1.0, UID1000, amd64. 실제 Runtime **2026-10-15 00:30:11.032~00:30:32.557 KST**, 수신 **00:30:45.919**, helper/권한/정리 재조회 **00:30:47.123**. 마지막 원격 작업은 이 읽기이며 Runner 사용 종료. 이후 로컬 증적 편입만 수행한다.
- 사용자 최신 직접 지시 “착수”를 [새 1회 결정](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6171930117)에 연결했다. 시작 00:30~00:40, 수집·정리 종료 01:00 KST. 새 RUN, 새 claim, plan SHA `a051a3f06ab885e258f1a2fa4f7ea0431999f095dd6f5cd369200d4cfe13a265`. 사용자 발언/해석/범위는 `decisions/USER_DECISION.json`, GitHub readback은 `records/USER_AUTHORIZATION_GITHUB_READBACK.json`에 보존한다.
- 실행 코드 [fds-msa PR36](https://github.com/321Team/fds-msa/pull/36), merge `6531b51c991535794c1f9705dc14f199001d1961`, 승인 HEAD `60f463f6ac8096546e71384696606f30aaa17823`. [이재환 코드 독립 승인](https://github.com/321Team/fds-msa/pull/36#pullrequestreview-5520172412), CI38586467623 PASS와 merge tree 동일. bundle SHA `d05f89052b2d1611ad59f832a381c450482e31c867dd74975b3a8c555e26ceef`, source10파일/manifest16 대조, 실제 fixture helper2 PASS. 코드 리뷰는 현장 실행 GO나 본 증적 편입 승인을 대신하지 않는다.
- 앱 source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, API config `ab34196baf2b878222857be47b200baed0151679a5b19fe15635ba50f77bffee`, engine config `b82d35a60e7a7f4a30366a926699fa4b673e69610f64fa0e7f294673ed12f4fc`. PG16.8 기존 고정 digest/config은 plan·provenance·사전 원본을 참조한다. 새 load/pull/build/scan/Push/Deploy/Secret 변경은 없다.
- 00:28:27 직접 조회로 Worker0/컨테이너0/가용메모리8839MiB/이미지3개 식별값을 확인하고, 배치·Runtime 직전에도 유휴 조건을 확인했다. 최대4컨테이너/7POST/900초·실패 시 재실행 금지 범위에서 **실제 1회**, 자동 재실행0.

## 결과와 원본 대응

경로 축약 `rt` = `received/runtime/FDS_D03_202610150030/`. 각 `NNN-command.json`은 argv, 시각, rc와 공개 stdout/stderr를 보존하며 비밀정보가 포함될 수 있는 inspect 출력은 실행 도구가 기록하지 않는다.

| 검증 | 실제 결과 | 원본 |
|---|---|---|
| DB 초기화·식별 | schema 0003 적용, `fds_lab\|postgres\|0003`, PostgreSQL16.8 | rt/011,012-command.json; 068,089 DB 로그 |
| bind 권한 수정 | code/hooks0755, 상위out/stage0700, 파일0644, SELinux container_file_t:s0 | records/POSTRUN_READBACK.json |
| 격리·기동 | DB network=none, 나머지3개 DB 네트워크 공유, lo만 존재/IPv4 route0, host port binding0, read-only·비privileged | rt/*-isolation.json, loopback-namespace.json,006/013/016/019-create |
| Listener | 업무8000/8001 metrics404, 관리9090/9091 metrics200 | rt/027~030-command.json |
| 정상 PRE | 201, 저장1, R01/R02/R04/R07 모두 false | rt/PRE-result.json,034~036-command.json |
| READ timeout | 2.017526초, 201, null/null/skipped=true, 저장1, evalerror+1 | rt/READ-result.json,038~040-command.json |
| READ 회복 | 201, 정상 판정/저장1 | rt/READ_POST-result.json |
| 엔진 HTTP500 | fixture의 실제500 1건, API201·null/null/skipped=true, 저장1, evalerror+1 | rt/HTTP-result.json,067/079 fixture 로그 |
| HTTP 회복 | 201, 정상 판정/저장1 | rt/HTTP_POST-result.json |
| DB 저장 실패 | API500 `transaction save failed`, 저장0, save_failure+1; 대상 RUN의 단일계정 트리거 | rt/DB-result.json,054~059-command.json |
| DB rollback·회복 | marker PID84 뒤 동일 PID84 ROLLBACK, trigger 제거조회0, 후속201·저장1 | rt/060/068 DB 로그,059,DB_POST-result.json |
| 최종 대조 | 순서 일치한 fixture7요청, DB6개 고유Transaction ID, save6/fail1/evalerror2, readiness3개200 | rt/065~071-command.json,verified-cases.json |
| 정리 | 역순 정확CID4개 logs/rm rc0/exists rc1, env2부재, 전체컨테이너0/Worker0 | rt/072~091-command.json,cleanup.json; records/POSTRUN_READBACK.json,runtime-collection-summary.json |

DB 로그에서 schema hook10과 logging hook20의 source·ALTER SYSTEM5회·최종 D03 prefix/영문 statement/ROLLBACK이 확인된다. 개별 GUC의 `SHOW` 조회는 실행하지 않았으므로 별도 조회 완료로 표시하지 않는다. PG HOME/tmpfs 쓰기와 앱 read-only rootfs 기동은 이번 실제 기동·7요청에서 확인됐다. 준비 중 DB check-container rc2(009), API readiness 초기 rc1(022)은 제한된 readiness 대기이며 POST 재실행이 아니다. 4개 cleanup exists rc1은 부재 판정이다.

## 무결성·재검증

- `RECEIVED_INDEX.json`: 총177입력, 직접 서버 사본147(helper10/runtime137, 단계별 decision 중복 포함), 원본 bytes 복사. 서버 manifest 총141항목을 대조한다. 로컬 decision/provenance/transport는 서버 원본과 구분한다. SHA 일치만으로 시험 통과를 선언하지 않고 원본 명령·응답·DB·metric·fixture·rollback·정리를 `verify.py`로 대조했다.
- 실행: Python 표준 라이브러리만으로 `python -I -B verify.py`. 예상 `evidence_verification=PASS`, 실제 원본 `LAB_RUNTIME_PASS`, POST7/stored6/PID84/정리true. 실패 시 증적 편입 중단; 이 검증기는 서버에 연결하거나 재실행하지 않는다.
- 원본 LF/CRLF 보존(`.gitattributes * -text`). `db.env`/`api.env`는 반출·manifest 편입하지 않았다. 비밀값 없는 코드의 DATABASE_URL 조립 문자열과 실제 비밀값을 구분한다. 토큰/개인키/JWT 패턴 검사와 경로 제외를 검증기에 포함했다. claim `af145cd3a2d47a907f13274194efaef94041cf91d441a87df647b7003155cbac`와 서버 원본/기존 이미지는 보존했다.
- 보조 supervisor/transport/수집기는 **REVIEW NOT PERFORMED**. PR36의 코드 독립승인 범위와 구분하며 이 PR에는 사용한 공개 입력·collector·receipt를 실어 증적 검토가 가능하게 한다. 이전 회차 supervisor umask077 영향은 PR232 원본을 유지하고, 이번 명시 chmod0755의 실제효과를 별도로 기록한다.

## 한계·후속

PG16.8/운영DB16.14 차이, 새 DB image 취약점 스캔 미수행, 격리 컨테이너 환경/HTTP loopback·운영K8S/TLS 제외를 유지한다. occurred_at는 검토된 고정 payload의 RUN 날짜12:00 KST이며 실제 수신00:30과 다르다. 이번 판정은 실패 처리 계약과 회복이며 야간 Rule·운영 회귀 판정으로 확대하지 않는다. 로그 수집 시점의 관측이며 지연·부하 시험도 아니다.

이전 RUN202610142110의 CLEANUP_FAILED([PR230](https://github.com/321Team/fds-project-evidence/pull/230))와 RUN202610150000의 FAILED/정리true([PR232](https://github.com/321Team/fds-project-evidence/pull/232))는 그대로 보존한다. 이번 성공으로 과거 결과를 덮어쓰지 않는다. APP15/E2E20/Review30 OPEN·AC·완료일은 유지하고 DB11 종결은 별개다. 다음 단계는 독립 증적 편입 리뷰, 이어서 기존 기능/부하/보안 근거와 요구별 대조 후 APP/E2E의 담당자 판정이다.
