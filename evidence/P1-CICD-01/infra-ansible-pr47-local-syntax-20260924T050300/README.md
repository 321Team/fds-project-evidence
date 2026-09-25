# PR47 리뷰 전 로컬 구문 검증 v1.0

기준: 2026-09-24 KST · 관련: infra-ansible #5 / PR47, fds-project-evidence PR24

## 결론

**리뷰 전에 가능한 작업을 수행했다. 현재 후보의 양 엔진 구문 검사 46/46 PASS.** 코드/Workflow HEAD는 변경하지 않았다. 일반 CI 활성화·전체 fixture·실제 Runner·독립 코드 리뷰·병합은 미완료다.

- source: `c6ba5f87711acc3eeeba12c13c72cedd09d178f8` ([PR47](https://github.com/321Team/infra-ansible/pull/47)).
- 실제 실행: 2026-09-24 **05:03:00–05:03:29 KST**, Codex Linux x86_64 / CPython3.12.14 로컬 환경.
- 단계: **LOCAL / STATIC_SYNTAX**. GitHub Actions CI, cicd-runner01 RUNTIME, 운영 서버 인수와 구분한다.

## 새로 확인한 범위

| 항목 | 결과 |
|---|---|
| 원본 연결 | 현재 GitHub tree의 Playbook/role/module 관련54파일을 Git blob SHA와 mode로 대조한 선택 snapshot |
| 의존성 | 현재 lock의 wheel12개 파일 집합·크기·SHA256 일치. 네트워크 다운로드 없이 새 venv2개에 --no-index/--require-hashes로 설치, pip check 양쪽 성공 |
| 엔진 | 실제 ansible-playbook --version으로 2.16.19 / 2.21.3 확인 |
| 현재 plan | Playbook21개 + fixture YAML2개 = 엔진당23개 |
| 구문 검사 | 2.16.19:23/23 rc0, 2.21.3:23/23 rc0. 정확한 (engine,path) 집합46건 대조 |
| 원문 증적 | 각 명령·stdout·stderr·종료코드, 설치/버전 로그, plan 및 LOCAL_SYNTAX_RESULT.json 보존 |
| 결과 manifest | results/SHA256SUMS의231파일 전부 일치, 정확한 집합 확인 |
| 소스 보존 | 실행 전·후 선택 snapshot54파일의 Git blob/mode 일치 |

현재 후보의 변경 없는 `tools/run-ansible-ci.py`에서 `plan()`과 `syntax_gate()`를 호출했다. 파일 blob은 `8eb183d2080ba37d1f266b29ae45d0b20a14d55d`이다. 기존 CI 실행기 전체 `execute()`는 호출하지 않았다. `run_local_syntax.py`는 이번 로컬 수행을 기록하는 진단 driver이며 서버 배포용 실행 키트가 아니다.

구문 명령은 실제 후보 코드의 `ansible-playbook --syntax-check -i localhost, -c local ...`이다. 운영 inventory/SSH·apply·서비스·방화벽 변경은 수행하지 않았다. host pattern 불일치 경고가 있어도 이 단계는 구문 검사이며 노드 접근 성공을 의미하지 않는다. 동적 include 내부 경로·조건식·템플릿의 실제 동작은 구문 검사만으로 판정하지 않는다.

## 기존 시험 이후 증가한 대상

과거 정상 Actions source `31895081e30e27481e7c17407047c9454e3b247a`의 Playbook14개와 현재21개를 GitHub tree로 대조했다. 증가한7개는 다음 NTP Playbook이다. 7개×두 엔진=14개가 이전32개 대비 증가분이며 이번46개 검사에 모두 포함된다.

1. playbooks/cr-p1-ntp-01-01-apply-clients.yml
2. playbooks/cr-p1-ntp-01-01-apply-source.yml
3. playbooks/cr-p1-ntp-01-01-diagnose.yml
4. playbooks/cr-p1-ntp-01-01-pathcheck.yml
5. playbooks/cr-p1-ntp-01-01-precheck.yml
6. playbooks/cr-p1-ntp-01-01-rollback.yml
7. playbooks/cr-p1-ntp-01-01-verify.yml

NTP PR44의 HEP/GNP·커널 계약 지적을 해결했다는 결과가 아니다. 현재 PR47 source의 구문에만 적용한다. 과거 CI32 PASS를 현재46 PASS로 승계하지 않고 실제 이번 결과로 기록했다.

## 검증 한계와 완료하지 않은 단계

- 전체218파일 Git checkout이 아닌 선택54파일 snapshot이다. 운영 코드의 의미·전체 회귀/fixture, source clean-check, packaging·artifact export, GitHub scheduler/checkout과 전체 CI를 검증하지 않았다.
- 원본 PLAN.json의 scope는 기존 실행기 전체 설명을 보존한다. **이번 실제 실행 scope는 LOCAL_SYNTAX_RESULT.json의 LOCAL_STATIC_SYNTAX_ONLY**, fixture_tests_executed=false / github_actions_executed=false다.
- wheel 무결성과 새 venv 설치 성공은 cicd-runner01의 현재 실행 경계·격리·IPC·통신·정리 성공을 뜻하지 않는다.
- 새 토큰, Runner 등록, Variables 변경, Actions 재실행, 운영 엔진 전환, 코드 PR 병합, 정본 발행은 미수행이다.
- PREPARED/image의 기존 현장 수신 PASS는 이전 readiness 증적에 귀속한다. 이번 로컬 검증으로 그 관측 시각을 갱신하지 않는다.

## 남은 후속과 리뷰 요청 범위

이 결과 확보 뒤 현재 PR47의 추가 선택적 구문/동일 코드 시험을 반복하지 않는다. 다음은 기존 요청 리뷰어 이하영(hayeounglee)의 정확한 HEAD 독립 검토와 현장 실행 준비다.

| 대상 | 독립 검토 범위 / 다음 완료조건 |
|---|---|
| [infra-ansible PR47](https://github.com/321Team/infra-ansible/pull/47) | HEAD c6ba5f87…의 Workflow55줄, exact source/labels/최소권한/실패전파/artifact/전용 Runner 경계. 기존 기술 COMMENT와 이번 로컬 구문 결과를 참고하되 타인의 승인으로 대체하지 않음 |
| [fds-project-evidence PR24](https://github.com/321Team/fds-project-evidence/pull/24) | 기존 readiness 수신 기록과 새 로컬 구문 원문·집합·판정 한계를 포함한 **추가 후 최신 HEAD** 검토. Runtime/일반 CI로 과장하지 않았는지 확인 |
| 일반 CI | 실행 직전 Variables·Runner·queued/in_progress를 확인하고 정상 Run/Attempt/Job을 새로 고정 → 기존 전용1-job serve → 정상/고의 count 결함·artifact·세션 정리 인수 |

일반 Workflow 활성화·코드 병합의 독립 리뷰는 기존 정책을 따른다. 병합 전 로컬/격리 후보 시험까지 일괄 승인 대기로 확대하지 않는다. 증적 PR24 병합은 현장 준비의 추가 선행조건이 아니다.

현재 기록의 Run35889332032/1은 skipped이므로 새 실행 입력으로 사용할 수 없다. 실행 시 source/labels/격리·경합 상태가 맞지 않으면 중단하고, 활성화 후 중단은 enabled=false·진행 Run 별도 종료·해당 세션 정리/Runner 부재 확인으로 처리한다. 변수 false만으로 실행 종료나 정리 성공을 선언하지 않는다.

원격 독립 리뷰는 여전히 미완료이며 사용자 대신 별도 메시지나 리뷰 재요청을 보내지 않았다. 기존 두 PR의 요청 리뷰어를 유지했다.
