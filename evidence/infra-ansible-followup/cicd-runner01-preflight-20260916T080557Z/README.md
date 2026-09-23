# cicd-runner01 사전점검 수신 및 stdout 출처 확인

사용자가 제출한 원본 압축/sidecar와 내부 파일을 그대로 보존한다.

## 사전점검 판정

- 실행 시각: 2026-09-16 08:05:57 UTC / 17:05:57 KST, 원본 RUN_RESULT.json 기준.
- 호스트 cicd-runner01, UID1000. 계정 이름은 이 자료에 없으므로 UID만으로 확정하지 않는다.
- Linux x86_64 / CPython3.12.14 / glibc2.39, Git/Bash/grep, venv/ensurepip, Python 로컬 IPC: 7개 모두 true.
- 결과는 `CAPABILITY_READY` 및 `PREFLIGHT_ONLY`. results는 빈 객체이며 Actions NOT_RUN, 운영 apply/엔진 전환 false다.
- 원본 압축 SHA256 `90aedb59188ef8030bb3ddb2413b8f786d1fe9b5f7a631108a76b4600881cc65`, sidecar 일치. 내부 SHA256SUMS의 원본2개 파일 및 파일집합 일치.
- 표시된 PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c`는 조회한 현재 HEAD와 같다. preflight는 PINNED.json의 값을 기록할 뿐 source pack/wheel 검증이나 해당 소스 실행을 수행하지 않는다.

이 호스트에서는 Codex 환경에서 관측한 로컬 IPC 생성 차단이 재현되지 않았다. 이는 Ansible2.21.3 Local RPC 또는 전체 두 엔진 시험이 이미 통과했다는 뜻이 아니다. Runner 저장소 접근·격리·권한·작업 정리와 독립 승인은 이 자료로 검증할 수 없다. 실제 `run`은 운영 SSH 키/배포 권한과 분리된 실행 환경이 확인된 뒤 진행한다. 등록 범위가 infra-cicd인 기존 Runner를 Ansible Runner로 자동 승격하지 않는다.

## 증빙 PR13 리뷰의 stdout 확인 요청 대응

[리뷰](https://github.com/321Team/fds-project-evidence/pull/13#pullrequestreview-5219964286)는 COMMENTED이며 APPROVED가 아니다. unit-tests/stdout.log의 PASS/FAIL·engine null/ERROR14는 병렬 guard 실행의 로그가 섞여야만 나오는 값이 아니라, 단위시험이 호출한 모의 CLI의 출력이다.

원래 검증 소스 `a487c4fc5185bf0b9cd82f7f739651d4d580ba6b` clean checkout에서 아래 세 unittest만 순차 실행해 기존 stdout 전체와 **바이트 단위 동일**하게 재현했다. 기존 stdout과 재현 stdout SHA256 모두 `05355062e41e382f7b03cf1cc10cb31db49a039ec3cabe2a00f22e9814953dd9`다. 원본 로그는 수정하지 않았다.

| 출력 | 생성한 단위시험 / 원인 |
|---|---|
| status PASS, status FAIL | CIGateTests.test_cli_exit_status_tracks_failure: ci.execute를 두 결과로 patch하고 ci.main의 반환값 확인. main이 JSON을 stdout으로 출력 |
| engine2.16.19, PASS14 | HarnessTests.test_cli_contract_and_stale_results: subprocess를 합성 정상 결과로 patch한 runner.run 호출 |
| engine null, ERROR14 | 같은 시험에서 FileNotFoundError('engine absent')를 주입한 두 번째 runner.run 호출 |
| engine2.16.19, ERROR14 | HarnessTests.test_engine_mismatch_stops_before_playbook: 기대2.21.3에 모의2.16.19 버전을 반환, 실제 playbook 전 중단 확인 |

unittest의 시험 진행·`Ran ... OK`는 stderr.log, 위 호출의 print는 stdout.log에 캡처된다. verification-kit.py는 unit-tests → guards → contract → DNS를 for 루프로 순차 실행하며 logged()는 각 프로세스의 stdout/stderr 파일을 따로 열고 종료를 기다린다. 검토한 캡처 코드와 정확한 재현 결과에서는 제기된 stdout 혼입을 뒷받침하는 근거가 발견되지 않았다.

`stdout-origin/`에 원문 명령·stdout·stderr·exit0·재현 메타데이터를 보존했다. 해당 소스5개 파일은 현재 PR17 HEAD에서도 바이트가 동일하다. 이번 3개 시험은 모의 CLI 단위시험이며 실제 엔진 성공 수에 더하지 않는다. 기존 56개 단위 PASS와 전체 CI FAIL 판정도 바꾸지 않는다.

## 후속

격리 실행 호스트/계정과 운영 권한 분리를 확인한 뒤 전달된 키트로 두 엔진 전체 시험을 수행한다. 코드 PR17·18 정식 승인, 증적 추가분 리뷰, 실제 정상/고의 결함 Actions와 운영 인수는 별도 대기다. 이 편입은 사전점검 수신과 리뷰 질의 해명이며 main 병합·Runner 설정·운영 적용을 포함하지 않는다.
