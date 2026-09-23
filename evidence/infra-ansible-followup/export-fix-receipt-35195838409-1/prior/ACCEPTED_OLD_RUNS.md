# 격리 Actions 정상·count 고의결함 시험 통합 인수 기록

기록일: 2026-09-17 KST. 기술적 증적 검수 결과이며 독립 승인·병합 기록이 아니다.

## 판정

- 정상 시험: CI PASS / Runner v1.3 Runtime PASS / 격리 18/18 PASS / 로컬 정리 PASS / Runner ID5 원격 부재 확인 / 원본 Artifact 인수 완료.
- 고의결함 시험: **기대 count 결함 탐지 PASS**. 실제 CI_RESULT·Job·Check는 **FAIL / failure 그대로 보존**한다. Runner ID6 Runtime·격리 18/18·로컬 정리·원격 등록 부재까지 확인했다.
- 정상·negative 인수를 위한 직접 기술 증적 조건은 충족했다. Issue #5 전체 AC 승인·독립 리뷰·증적 PR 병합·운영 적용 완료를 의미하지 않는다.
- 기존 Attempt1 환경 실패 증적은 수정하지 않는다. 새 시험 결과는 새 경로에만 추가한다.

## 실행 연결표

| 항목 | 정상 | count 고의결함 |
|---|---|---|
| 시험 전용 PR | infra-ansible #20, DO NOT MERGE | infra-ansible #21, DO NOT MERGE |
| source checkout | `2750634766862d7fe19479acacc4259ee8315061` | `c50a6b3316fabba08d5211933e3733f8026e2d95` |
| Run / Attempt | `35139314896 / 2` | `35173018935 / 1` |
| Job / Check ID | `104963520513` | `105048547807` |
| Job / Check 결론 | success | failure |
| Job 실행 시각(KST) | 2026-09-17 06:36:52~06:44:05 | 2026-09-17 12:12:01~12:17:03 |
| Runner ID | 5 | 6 |
| Runner name | `ansible-ci-3b46463efffc4a2c861f839e80fdfbd9` | `ansible-ci-717c2a4d2df149408ae59b4dd68d2c04` |
| workflow/event SHA | `7f2cb2b2684db412b5dd499729d38cb8364014ec` | `441e91c72504c48fc1fedf4a10ff0d8fd6a221fd` |
| Artifact ID | `10470072587` | `10478742095` |
| 원격 부재 수집 시각(KST) | 2026-09-17 10:58:24~30 | 2026-09-17 12:30:56~59 |

관리 Receipt의 원본 PR·Run·Job·Check 연결 및 전체 runner 목록을 대조했다. 양쪽 목록은 해당 수집 시점에 `total_count=0`이다. 현재 시점의 지속적인 등록 부재 또는 삭제 명령 성공을 주장하지 않는다. `remove_rc=null`과 원격 부재 증명을 구분한다.

## 시험 결과와 범위

| 항목 | 정상 | count 고의결함 |
|---|---|---|
| syntax | 2엔진 × 16 = 32/32 rc0 | 32/32 rc0 |
| unit | 57 tests / OK | 57 tests / OK |
| baseline guard / 엔진별 | PASS14 / FAIL0 / ERROR0 | PASS9 / FAIL5 / ERROR0 |
| guard mutation matrix | 14/14 기대 판정 일치 | count 변경으로 baseline 포함 불일치 검출; 전체 PASS 아님 |
| contract matrix | 58/58 PASS | guard 단계 조기 종료로 NOT_RUN |
| DNS 2.16.19 / 2.21.3 | 모두 rc0 | NOT_RUN |
| CI_RESULT | PASS | FAIL |

negative source는 정상 source 대비 1 commit / 1 file / +1 -1이다. `playbooks/harden_svc_ansible_key.yml` 첫 guard의 `(p1_managed_key_count.stdout | int) != 1`을 `!= 2`로 변경했다. `negative/github/compare.json`에 비교 원문을 보존한다.

두 엔진 모두 `one_plain`, `one_restricted`, `two_plain`, `two_restricted`, `mixed` 5개가 첫 `Count P1 managed SSH keys` guard에서 불일치했다. 둘째 restricted guard는 7/7 기대 판정과 일치한다. 각 엔진의 baseline 결과 14개 원문과 생성된 `ssh-guards.yml`을 함께 편입했다.

실패 전파: guards EXIT_CODE=1 → fixture FAIL → CI_RESULT FAIL → Job/Check failure. source SHA 불일치, IPC 초기화 실패, timeout, OOM, artifact 업로드 실패로 대체 판정하지 않았다. 별도 mutation variant의 의도된 ERROR를 baseline ERROR0과 혼동하지 않는다.

## Runtime·정리

양쪽 세션 모두 같은 Runner v1.3 bundle/image를 사용했다.

- bundle SHA256: `e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6`
- image: `sha256:3f96787b2a8db29294002677a3e733689439952ad9e95db721acf8e16ff601f1`
- IPC preflight true, 격리 18/18 true, SELinux Enforcing, configure/listener rc0.
- 컨테이너 exited / ExitCode0 / OOMKilled=false. 실제 Job 결론과 컨테이너 종료코드는 별도다.
- runner·proxy·workspace 모두 REMOVED. 컨테이너 exists rc1은 부재 확인값이다.
- 운영 inventory/SSH 실행, production apply, 운영 엔진 전환은 수행하지 않았다.

## 원본 무결성 재검증

| 대상 | 정상 | negative |
|---|---|---|
| Runner outer manifest | 16/16 | 16/16 |
| Runner nested manifest | 9/9 | 9/9 |
| 관리 Receipt manifest | 9/9 | 7/7 |
| Artifact manifest | 831/831 | 592/592 |
| Fixture manifest | 666 일치 + 명시된 cache 3건 제외 | 427/427 |

정상 cache 누락 3개는 ARTIFACT_SCOPE의 경로·해시와 정확히 일치한다. 임의 누락으로 허용하지 않았다. 상세 재검증은 `VALIDATION.json`, `SEMANTIC_VALIDATION.json`에 기록한다.

원본 ZIP SHA256:

- 정상: `396253ca61721f663988404d3db1d9f55a14ce3881068084b34ba3555240bcda` (459427 bytes)
- negative: `0a25a223fd9447df9d92a0086d973c9268a7f635d9db50f2f6bbedafdabe6cfe` (303785 bytes)
- negative 최종 Receipt: `9d6b9ada049e8b1ae423e2274029718bdeee73046ae2b8ec6761f869667e8478`

## 보존 구조와 검증 방법

- `positive/`, `negative/`: 검토에 필요한 원문 바이트의 사본. `ORIGIN_INDEX.json`으로 출처·경로·해시를 연결한다.
- `ARCHIVE_INDEX.json`: 원본 tar/ZIP 및 수신 sidecar의 별도 패키지 내 경로·원래 파일명·크기·SHA256.
- 기존 압축파일은 재압축하지 않고 **그 바이트 그대로** `FDS_Ansible_Actions_Acceptance_20260917_v1_0.zip`의 `originals/`에 보존했다. 원본 내부 경로나 Manifest는 수정하지 않았다.
- Git에는 원문 선별 사본과 검토 기록을 게시한다. `artifact-selected/`는 전체 ZIP 추출본이 아니다. 해당 디렉터리의 원본 SHA256SUMS를 부분 사본 전체에 실행하면 의도적으로 미편입 파일이 보고된다. 전체 검증은 별도 원본 ZIP에서 수행한다.
- 이 새 경로의 전체 편입 파일은 `PUBLICATION_SHA256SUMS`, 저장소 대장은 `REGISTRY_SHA256SUMS`로 별도 검증한다. 원본 sidecar에는 원래 basename이 남아 있으므로 별도 패키지에서는 ARCHIVE_INDEX의 파일명 대응을 사용한다.
- 원본 Actions 다운로드: [정상 Run](https://github.com/321Team/infra-ansible/actions/runs/35139314896/attempts/2), [negative Run](https://github.com/321Team/infra-ansible/actions/runs/35173018935/attempts/1). Artifact 보존 기한과 무관하게 이번 별도 패키지에 원본을 확보했다. GitHub 권한이나 공유 범위는 변경하지 않았다.

## 독립 리뷰 인계

1. evidence PR #13 새 HEAD: 본 증적 추가와 registry append, 기존 원본 불변, 양쪽 source/Run/Attempt/Job/Check/Runner 결합, cache 제외 및 NOT_RUN 표기의 적정성 검토.
2. infra-ansible PR #17 HEAD `9b019ad4213539e9a6edf2409e1d0bd0d4ef46f6`: 실행기·실패 차단 및 향후 활성화 변경 검토. 시험 전용 source의 CI 결과를 이 HEAD의 직접 실행 결과로 승계하지 않는다.
3. infra-ansible PR #19 HEAD `4da96621fd05a4943b76ca32b860a5779ec65e00`: 격리·IPC·입력 보호·정리 통제의 코드와 Runtime 연결 검토.
4. 기존 stdout 혼재 질의의 설명: [응답 기록](https://github.com/321Team/fds-project-evidence/pull/13#issuecomment-5707334275). `unit-tests/stdout.log`는 unit test 내부 CLI 호출의 2+3 JSON 출력이며 독립 guards 실행 결과와 구별한다. 기존 COMMENTED를 APPROVED로 해석하지 않는다.

기존 리뷰 요청은 보존하며 실제 리뷰 참여자 `hayeounglee`에게 새 증적 범위 검토를 요청한다. 요청은 리뷰 완료가 아니다. PR #20/#21은 TEST ONLY / DO NOT MERGE 유지. 토큰 발급, Start v1.1/v1.2, prepare, serve, rerun은 더 수행할 필요가 없다. 승인·병합·Issue #5 종결 및 운영 apply는 별도 판단이다.
