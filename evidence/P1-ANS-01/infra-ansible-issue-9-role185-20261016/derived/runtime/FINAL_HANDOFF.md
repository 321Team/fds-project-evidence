# F1/F2 보완 후보 단회 격리 시험 결과

기록 시각: 2026-10-16T17:25:02.114548+09:00. 판정: **PASS_LOCAL_ROLE_FIXTURES_185_OWN_CLEANUP_CONFIRMED**.

## 실제 완료

- session `p1-role-cc7e9fc7dd9049a4`, source `affaad6b1a31d680164d9e3d5ef5d2a9d3fce95a`, tree `2563bcea5ceee3543451e96ac76011ef05e486bf`.
- 공급 1회, 사용자 같은 TTY의 stage 1회·plan 1회·입력 대조 1회·execute 1회. 각 종료 코드 0.
- 실제 컨테이너 실행: 2026-10-16T17:09:25.953288654+09:00 → 2026-10-16T17:13:51.387027915+09:00 (약 265.4초).
- 고정 7개 묶음 **185 PASS / 0 FAIL / 0 SKIP**. 환경 준비 명령 11개는 185건에 포함하지 않았다.

| 시험 묶음 | 통과/예정 | 묶음 종료 코드 |
|---|---:|---:|
| mon-2.16.19 | 45/45 | 0 |
| mon-2.21.3 | 45/45 | 0 |
| ntp-legacy | 48/48 | 0 |
| ntp-flow | 25/25 | 0 |
| ntp-serial | 1/1 | 0 |
| ntp-transport | 2/2 | 0 |
| ntp-wrapper | 19/19 | 0 |

실패 조건을 확인하는 개별 시험의 종료 코드 1·2·64는 해당 기대값과 일치한 경우에만 통과로 집계했다. `ntp-serial`의 내부 rc2는 세 번째 대상 실패 후 복원·후속 중단을 확인하는 예상 결과이며, 묶음 실행기 rc는 0이다. MON은 엔진별 40개 명령 영수증과 5개 직접 검증 사례로 45건이다.

## F1/F2 및 증적 대조

- F1: 실제 Ansible 설정 77개와 서버 읽기에서 수집한 임시 디렉터리 154개의 uid1001/gid1002·0700을 확인했다. 두 MON 엔진 모두 실제 copy→slurp→assert가 통과했고 `module-ready.txt`의 정확 바이트를 대조했다.
- F2: MON 명령 영수증 80개의 intent·실제 rc·기대 rc·시각·원본 로그 크기/해시를 대조했다. 최종 45건씩과 부분 원장 사례가 일치하며, `initial_error=null`·`evidence_errors=[]`이다. 부분 원장의 `INCOMPLETE` 표시는 그대로 보존하고 최종 `RESULTS.json`으로 완료를 판정했다.
- 서버 원본 3,446개, 터미널 원본 12개, 공급 manifest 487개 항목, 호스트 명령 영수증 69개, 바깥 실행 영수증 18개를 대조했다. 실행 전 고정 181개 파일도 불변이다.
- NTP `observed_sha256`은 시험 기준 `observed-chrony.conf`의 해시다. 첫 로컬 검증 스크립트가 이를 parser 바이너리 해시로 오해한 오류를 보존하고 바로잡았다. 원본·후보·서버 실행은 변경하거나 반복하지 않았다. parser 바이너리는 별도 공급 manifest로 결속돼 있다.

## 격리와 회수

- 정확 CID `b0d9da1071bd48759f1866549d37f682888b01f9c8dca6017823725cd65aec79`의 create/start/rm가 각 1회이고 모두 rc0이다. stop·강제 삭제·추가 컨테이너·재실행은 없다.
- read-only rootfs, network none, capability 없음, no-new-privileges, SELinux container_t, 분리 namespace, 지정 3개 bind, CPU/메모리/PID 제한을 수집 원본과 대조했다.
- 자동 회수 `OWN_CONTAINER_REMOVED`; 2026-10-16T17:17:55.927957+09:00 같은 rootless store의 정확 CID 부재 rc1·실행기 0·조회 오류 0을 확인했다. 추가 수동 회수는 필요하지 않다.
- 입력/증적 경로 `/home/server01_cicd-runner/role185-p1-role-cc7e9fc7dd9049a4`, `/home/ansible-verify/p1-role-cc7e9fc7dd9049a4`는 원본 보존을 위해 남아 있다. 실행 중 객체나 회수 미완료로 집계하지 않는다. 사용자 승인 창은 연장하지 않았다.

## 인계할 원본과 판정 경계

- `FINAL_RESULT.json`, `EVIDENCE_AUDIT.json`: 결과와 근거/한계.
- `HOST_COMMAND_AUDIT.json`, `SUITE_CASE_AUDIT.json`, `MON_COMMAND_AUDIT.json`, `FIXTURE_TMP_DIRECTORY_AUDIT.json`: 세부 연결.
- `runtime-originals-20261016T081814170331.tar` — SHA-256 `a9e448e2ac046d734eb066b06b43fc487a4cb8509b84bb8c244b64330184b12b`.
- `originals-20261016T081814170331/`: 서버 원본 3,446개와 수집 파생 영수증 1개.
- `operator-originals-20261016T081814168345/`: 터미널 stdout/stderr/rc 12개 원본.
- `FINAL_BINDING.json` / `FINAL_SHA256SUMS`: 인계 파일 고정.

이 결과는 실제 Linux 격리 컨테이너에서 실행한 LOCAL/MOCK 역할 시험이다. 실제 Ansible 모듈·파일·parser 경로는 실행했으나 서비스/chronyc 등 대체 관측은 계속 모의이며, 운영 호스트 MON/NTP 적용·GitHub CI·병합·Phase 1 AC 최종 인수가 아니다. 별도 테스트나 새 전체 리뷰가 필요하다는 뜻도 아니다.

중앙 세션은 이 정확 결과와 원본을 기존 통합/게시 절차에 연결한다. 이 실행 세션은 공통 STATUS/CONTROL/ROUND, 고정 후보, 과거 실패/회수 원본, sources/sealed를 변경하지 않았으며 GitHub 게시도 수행하지 않았다. 현재 회차의 추가 서버 실행·관측·회수는 필요하지 않다.
