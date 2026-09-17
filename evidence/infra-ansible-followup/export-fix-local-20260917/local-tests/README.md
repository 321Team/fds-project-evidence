# Ansible 추가 로컬 시험 결과 — 2026-09-17 v1.0

## 결론

기존 통합 단위시험은 **156/156 PASS**이다. 증적 변조 시험, 교차 식별정보 대조 모형,
타임아웃 반복 시험도 아래 한정된 범위에서 기대한 동작을 확인했다.

다만 증적 저장 실패 시 **프로세스는 rc=1인데 앞서 저장한 CI_RESULT.status=PASS가
남는 진단 불일치**를 재현했다. 전체 판정이 거짓 성공한 것은 아니다.
rc·Job/Check·원본 digest·완전한 manifest·source/Run/Attempt binding을 함께 요구하면
이번 실패 사례는 모두 인수 거부된다.

이 보고서는 추가 LOCAL/MOCK 시험이다. 새 GitHub Actions, Podman, VM Runtime,
Ansible 양 엔진 실행이나 운영 Apply를 수행한 결과가 아니다.

## 대상과 원본 보존

- PR17: 9b019ad4213539e9a6edf2409e1d0bd0d4ef46f6
- PR19: 4da96621fd05a4943b76ca32b860a5779ec65e00
- PR17 68개 파일 + PR19 도구 57개 파일 = 통합 125개.
- Git blob SHA와 실행 모드 전수 검증 후 복원. 각 시험 후 원본 125개 재검증.
- source-map.json 및 results/SOURCE_BINDING.json에 출처/객체/파일 hash 기록.
- GitHub source/evidence HEAD, PR 본문·댓글·리뷰 및 Issue는 이번에 수정하지 않았다.
- 종료 직전 PR17/19 동일 HEAD 확인: results/FINAL_STATE.json.
- 기존에 인수한 positive/negative 실제 증적을 다시 판정하거나 변경하지 않았다.
- 수신 원본의 복사본 대신 명시적으로 SYNTHETIC인 새 임시 fixture를 사용했다.

## 1. 기존 시험 156개

| Suite | 개수 | 결과 |
|---|---:|---|
| tests/test_*.py | 57 | PASS |
| tools/ansible-runner/test-kit.py | 37 | PASS |
| tools/ansible-runner/test-registration.py | 13 | PASS |
| tools/ansible-runner/test-ipc.py | 7 | PASS |
| tools/ansible-admin-token/test-admin-token.py | 22 | PASS |
| tools/ansible-runner-input/test_safe_input.py | 20 | PASS |
| 합계 | 156 | PASS |

각 도구는 별도 Python interpreter에서 실행했다. 서로 다른 common/container 모듈 이름 충돌을
방지했다. 이것은 하나의 interpreter에 모든 모듈을 동시에 적재하는 통합시험은 아니다.

57개 외의 99개는 기존 개별 시험의 재검증이며 새로 작성한 99개 시험이 아니다.
subTest 반복을 별도 unittest 개수로 더하지 않았다.
results/EXISTING_SUITES.json, 각 *.stdout.log/*.stderr.log 참고.

시험 자식에게는 제한된 환경변수만 전달했다. 실제 gh/Podman/SSH/Ansible 명령 및
소켓 연결은 로컬 audit guard로 차단했다. 엔진·등록 API 호출은 mock이고,
실제 실행된 자식은 로컬 Python, 합성 fake-gh shell, 임시 Git fixture 작업뿐이다.
테스트가 출력하는 합성 FAIL/PASS JSON은 실제 Actions 결과가 아니다.

## 2. 증적 저장 실패 — 12개 시나리오

- 정상 대조군 1개: rc0, 완전한 manifest.
- fixture 실패 대조군 1개: rc1, FAIL 결과와 완전한 manifest.
- 저장 실패 주입 10개: 모두 rc1, 불완전 manifest, 합성 원본 로그 보존.
- 오류 종류: ENOSPC, EACCES, EIO, partial manifest 및 지속 쓰기 장애.
- 실제 디스크를 채우거나 서버/파일시스템 권한을 바꾸지 않고 Path I/O에 오류를 주입했다.
- 실제 CI main/execute와 artifact export 코드를 사용했다. 엔진/빌드/fixture는 mock이다.
  합성 CI_RESULT의 syntax 항목은 실제 양 엔진 구문시험 수행 근거가 아니다.

### 관찰 F-01 — export 실패 뒤 잔존 PASS

원본 코드의 10개 저장 장애 중 **8개**에서 root 또는 artifact의 기존 PASS가 남았다.

| 범위 | 관찰 |
|---|---|
| 단일 경로 장애 7개 | artifact mkdir, result 복사, log 복사/읽기, scope 쓰기, manifest 쓰기/부분 쓰기 |
| 지속 장애 1개 | scope 기록 실패 이후 모든 결과 갱신 쓰기도 거부 |
| 전체 인수 판정 | rc1 + manifest 불완전으로 전부 거부 |
| 원본 로그 | 12개 시나리오 모두 임시 fixture의 원본 보존 |

root CI_RESULT는 테스트 단계가 끝난 뒤 export보다 먼저 PASS로 기록된다.
이후 finally의 export에서 예외가 나면 현재 코드는 이를 전파하며 CLI는 rc1로 종료한다.
따라서 이 현상은 **결과 파일만 보는 도구의 오판 위험**이며,
기존에 완전한 원본·Job/Check까지 대조해 인수한 성공 시험을 뒤집는 근거가 아니다.

results/STORAGE_FAILURES.json과 results/faults/에 원본 관찰을 보존했다.
'passed_exit_and_preservation'은 종료·원본 보존 조건만 의미한다.
이를 진단 상태 일관성까지 PASS했다는 뜻으로 해석하면 안 된다.
'acceptance_allowed'는 이번 하네스의 결합 판정이며 배포된 인수 서비스가 아니다.

## 3. 변조·혼입 — 25개 기존 코드 + 35개 신규 모형

### 기존 코드 25개

- common.manifest: 정상 대조군 1개, 변조·누락·추가·중복 manifest·잘못된 hash·
  traversal·절대/비정규 경로·symlink·hardlink·FIFO 거부 13개.
- launch.copy_original: 정상 대조군 1개, host result 누락/중복/비정상 JSON/과대 크기,
  구성원 수 초과, 링크, gzip 손상, sidecar hash/name 오류, archive 링크 거부 10개.
- 25/25 기대 동작 확인. 실제 운영 원본은 수정하지 않았다.
- copy_original은 제한된 host result 읽기/외부 hash 검사 함수이다.
  내부 전체 manifest 검증이나 모든 archive 경로 검증까지 수행한다고 확대하지 않는다.

### 새 검토용 교차 대조 모형 35개

review_binding.py를 신규 작성하여 source·PR·Run·Attempt·Job/Check·Runner ID/name·
bundle/image·cleanup·원격 Runner 목록 완결성을 합성 fixture로 검사했다.

- 정상/expected-negative 대조군 2개 + 혼입/오류 33개 = 35/35.
- negative의 CI FAIL / Job failure를 positive의 PASS와 구분한다.
- 이 모형은 기존 Receipt collector나 운영 판정기에 반영되지 않았다.
- 신뢰할 수 있는 expected 값 및 입력 provenance를 별도로 확보해야 한다.
- byte digest, 전체 manifest, fixture matrix, 수집 시각/최신성, API provenance 검증을
  대신하지 않는다. 이 함수 하나로 실제 증적을 인수하면 안 된다.

results/TAMPER_MATRIX.json 참조.

## 4. 타임아웃 — 200회 반복 + 기존 취약한 시험 조건 10회 재현

| 종류 | 횟수 | 결과 |
|---|---:|---|
| 첫 출력 관찰 후 시험 타이머 시작 | 100 | 로그 보존·timed_out=true·nonzero 모두 확인 |
| 아무 출력 없는 자식의 시간초과 | 100 | 빈 로그 허용·timed_out=true·nonzero 모두 확인 |
| 기존 0.3초 제한 + 합성 초기 지연 0.4초 | 10 | 시간초과 자체는 정상, 기존 'before timeout' 문자열 검사는 모두 실패할 조건 |

readiness 반복에는 0~0.4초의 합성 초기 지연을 넣었다. 자식 프로세스는 실제 로컬
Python이며 VM/Podman이 아니다. readiness 방식은 시험 하네스의 Popen 반환 전
첫 출력을 기다려 시험의 시간 경계를 조정한다. 운영 Controller 시간초과 구현은 바꾸지 않았다.

과거 배포된 readiness patch와 이번 하네스의 byte 동일성은 검사하지 않았다.
같은 원리를 이용한 독립 재현이며 기존 원본 시험 156개는 이번 환경에서 그대로 PASS했다.
즉 과거의 시작 지연 문제를 운영 로그 유실로 판정하지 않는다.

results/TIMEOUT_MATRIX.json 및 results/timeouts/*/evidence/ 참조.

## 5. 검토용 수정안 — 원격 미반영

results/artifact-export-status.patch는 PR17의 두 파일만 변경하는 **제안**이다.

1. tools/run-ansible-ci.py: export 예외를 잡아 메모리 결과를 FAIL로 만들고,
   고정된 오류 종류/errno를 기록하며 쓰기 가능한 결과 파일을 best-effort로 갱신.
2. tests/test_ci_regression.py: manifest 쓰기 장애에 대한 회귀시험 1개 추가.

검증:
- 원본 코드 + 새 회귀시험: 예상대로 실패(red control).
- 수정안: 기존 156개 + 새 1개 = **157/157 PASS**.
- 수정안에 동일 저장 실패 시나리오 12개 재실행.
- 쓰기가 가능한 단일 경로 장애 7개의 잔존 PASS는 FAIL로 갱신됨.
- 지속 장애 1개는 파일 재기록이 불가능하여 기존 PASS가 남는 것을 재확인.
  메모리/CLI 결과는 FAIL, rc1, manifest 불완전이므로 인수 거부.
- git apply --check / reverse --check PASS.
- 원본 candidate 125개와 원격 HEAD 그대로 유지.

**한계:** 이 수정안은 상태 진단 보완이다. 지속 장애·전원 손실·SIGKILL·OOM에서 결과 기록의
내구성을 보장하는 원자적 publication 설계가 아니다. incomplete artifact를 성공으로 인수하지
않는 결합 검사는 수정 후에도 필수이다. 독립 코드 리뷰 전 배포나 병합하지 않는다.

results/PROPOSAL_VALIDATION.json, PROPOSAL_STORAGE_FAILURES.json 참조.

## 6. 단계별 판정과 다음 작업

| 단계 | 이번 수행 |
|---|---|
| STATIC/LOCAL | 소스 무결성, 기존 시험, 실제 로컬 자식 시간초과 확인 |
| MOCK | CI 저장 장애, 변조, 교차 대조 모형 |
| 새 Actions CI / 서버 Runtime | NOT RUN |
| 독립 REVIEW / MERGE | NOT DONE |
| 운영 Apply / 엔진 전환 | NOT RUN |
| 원격 PR/Issue 기록 변경 | NOT DONE |
| 결과 패키지 제공 | 본 ZIP 및 sidecar |

권고:
1. F-01과 수정 diff를 PR17의 별도 독립 리뷰 대상으로 제출한다.
2. 채택 시 새 HEAD에 맞춰 리뷰 범위를 갱신한다. 기존 승인이나 테스트 source를
   새 HEAD에 자동 승계하지 않는다.
3. 필요하면 export를 staging 디렉터리에서 완성한 뒤 공개하는 원자적 publication을
   별도 설계한다. 이번 best-effort patch와 혼동하지 않는다.
4. 일반 CI 활성화·실제 취소/동시성 시험은 별도 승인 범위에서 수행한다.
5. 기존 Start v1.1이나 새 prepare/token 명령을 이번 추가 로컬 시험 때문에 실행하지 않는다.

## 7. 재현 및 패키지 범위

이 ZIP은 **리뷰용 시험 결과/코드/수정 diff**이며 서버 실행 키트가 아니다.
원격 Git에 이미 보존된 원본 소스 125개 및 기존 업로드 증적은 중복 수록하지 않았다.

재현하려면 Python 3.12, PyYAML, Git을 갖춘 별도의 빈 로컬 작업 디렉터리에
본 하네스 *.py와 source-map.json을 복사한다. 이미 접근 허가된 로컬 infra-ansible 저장소가
두 정확한 commit 객체를 갖고 있을 때 다음 순서로 실행할 수 있다.

1. recreate_source_input.py에 그 로컬 저장소의 절대 경로를 인자로 전달한다.
   네트워크 fetch는 하지 않으며 125개 Git 객체·mode를 검증해 입력 JSON을 만든다.
2. prepare_and_run.py 실행: 새 candidate와 results를 만들고 원본 156개 실행.
3. storage_matrix.py, tamper_matrix.py, timeout_matrix.py 실행.
4. candidate를 새 proposal 디렉터리로 복사하고 제공 patch를 그 사본에만 적용.
5. validate_proposal.py 실행, storage_matrix.py에 proposal 절대 경로를 전달.

하네스는 기존 결과 디렉터리 재사용 시 중단한다. 원본 결과를 덮어쓰지 않는다.
유효한 배포 ZIP/PREPARED를 수기로 수정하거나 이 합성 결과를 실제 서버 증적과 혼합하지 않는다.

타임아웃 private 중복 로그 및 변조 시험 fixture 실물(링크/FIFO/고의 손상 archive)은 ZIP에서 제외했다.
변조 시험은 판정 JSON과 fixture 재현 코드로 보존했다. storage fault와 timeout은 모든 관찰 case를 보존했다.
PACKAGE_INDEX.json과 SHA256SUMS가 패키지 파일 목록 및 bytes를 정의한다.
