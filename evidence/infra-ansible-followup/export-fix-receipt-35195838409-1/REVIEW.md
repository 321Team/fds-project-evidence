# Export fix 정상 Actions 최종 증적 검수

**판정: 정상 실행의 직접 기술 증적 조건 충족.** PR22 source `31895081e30e27481e7c17407047c9454e3b247a`, Run `35195838409`, Attempt **1**에 대해 CI·Job·Check·Runtime·artifact·로컬 정리·원격 Runner 등록 부재까지 연결했다. 이는 기술적 원본 검수 결과이며 독립 승인이나 Issue #5 전체 AC 승인 기록이 아니다.

## 이번 Receipt 원본

- 파일: `ansible-export-fix-receipt.tar.gz`, 6,611 bytes.
- SHA256: `40410f2eca8da7ed4c7c509a499443663a202bf56210588912f6a5abb3246c15`.
- 제공 sidecar 일치, manifest **7/7**, 포함 파일 집합 정확히 일치. 압축 경로·중복·링크·JSON 중복 키도 확인했다.
- 수집 시각: **2026-09-17 18:57:32–18:57:35 KST** (`09:57:32–09:57:35 UTC`). Runtime 종료 17:24:06 KST 이후다.
- hostname ansible01 / uid1000. 배포한 Receipt v1.0 ZIP의 collect.py SHA256과 RESULT의 script_sha256이 일치한다.
- 5개 명령 모두 GET, rc0, timeout=false. Runner 조회에는 `--paginate --slurp`가 적용됐다. 토큰 발급·삭제·rerun·설정 변경 기록은 없다.

## 두 잔여 항목 해소

| 항목 | 원문 대조 결과 |
|---|---|
| Check | `105118736321`, regression, completed/success |
| Check 연결 | source `31895081e30e27481e7c17407047c9454e3b247a`, PR22, suite `95316041498`, app github-actions/15368 |
| Run/Job | Run35195838409/Attempt1, 동일 Job ID, Runner26/name, labels, 실행 시각 일치 |
| Runner 원격 등록 | 전체 1페이지, total_count0, ID26 및 이름 `ansible-ci-a6b75591ba3d4d38b5a3c3797afd8d37` 부재 |

부재는 **위 수집 시점의 등록 목록**에 관한 사실이다. 이후에도 계속 부재라는 보장이나 삭제 명령 성공으로 표현하지 않는다. 기존 ID5/ID6 부재를 이번 세션에 승계하지 않았다. Check 원문의 app.permissions는 GitHub Actions 앱 메타데이터이며 Workflow에 부여된 GITHUB_TOKEN 권한으로 해석하지 않는다.

## 기존 원본과 연결한 전체 결과

| 단계 | 검증 결과 |
|---|---|
| CI / Job / Check | PASS / success / success |
| 구문 / 단위시험 | 32/32 rc0 / 58 tests OK |
| Guard / Contract / DNS | 14/14 / 58/58 / 양 엔진 rc0 |
| Artifact10487510294 | 459,726 bytes, SHA256 `b973ff4e2b021fb7de017684d4b928c3958349d339df58fda360a3987352d9a5`, 내부 831/831 |
| Runtime / IPC | 정상, configure/listener rc0, Succeeded, OOM=false |
| 격리 / SELinux | 18/18 true / Enforcing |
| 로컬 정리 | runner/proxy/workspace 모두 REMOVED |
| 원격 등록 부재 | 세션 종료 후 Runner26/name 부재 확인 |

원본 Runtime 외부/중첩 manifest는 16/16, 9/9였다. Artifact fixture 669개 중 666개 실제 파일과 정확히 명시된 cache 제외 3개를 대조한 이전 검증을 동일 source/Run/Attempt/Runner에 연결했다. 이전 원본·검증 결과는 변경하지 않았다.

## 최신 리뷰 및 다음 단계

- PR17 HEAD `6b2ac7a80be1acd187ac73cbd1cf957f708edf85`: supreme33-kr 리뷰5232880227은 COMMENTED. Workflow/CI 핵심 부분을 검토했으나 전체 대조·사람 확인은 PENDING.
- PR19 HEAD `4da96621fd05a4943b76ca32b860a5779ec65e00`: supreme33-kr 리뷰5232900696은 COMMENTED. container.py 집중 검토이며 admin-token.py·launch.py 등 나머지 범위의 검토는 완료되지 않았다.
- Evidence PR13: 기존 hayeounglee COMMENTED는 과거 HEAD 대상이다. 이번 최종 Receipt와 원본 연결·registry 보존이 새 리뷰 범위다.
- PR22는 TEST ONLY / DO NOT MERGE, Draft/Open이다. PR17/19도 Draft/Open, Issue5 Open을 유지한다.

**권고:** 추가 서버 실행에 앞서 위 최신 HEAD와 이번 증적을 기준으로 독립 검토를 마무리한다. 현재 정상 실행에 관해서는 Runner·토큰·prepare·Receipt 재실행이 필요하지 않다. 새 코드의 count 재시험 여부는 `FOLLOWUP_REVIEW.md`의 변경 영향과 기존 결함 원본을 근거로 검토할 수 있도록 정리했다. 새 테스트 실행이나 재시험 면제를 여기서 확정하지 않았다.

운영 Apply, 운영 엔진 전환, 일반 자동 CI 활성화, 독립 승인, PR 병합, Issue 종결은 수행하지 않았다.

## 재검증과 보관

`originals/`에 수신 Receipt와 sidecar를 동일 bytes로 보존했다. `prior/`에는 이전 VALIDATION과 배포 collect.py를 보존했다. `verify_receipt.py`는 archive·manifest·Check/Run/Job/PR·조회 완결성·세션 후 시각·기존 검증 연결을 검사한다. 자체 validator 실행은 독립 승인이 아니다.

별도 보관 ZIP에는 이전 `FDS_Ansible_Export_Fix_Runtime_Review_20260917_v1_0.zip`도 동일 bytes로 포함한다. 그 ZIP의 `verify_archives.py`와 `verify_semantics.py`로 Runtime/artifact 검증을 재현하고, 이번 `verify_receipt.py`로 마지막 연결을 확인할 수 있다. Git에는 이번 관리 Receipt의 전체 텍스트 원문과 검수 기록을 추가하며 기존 Runtime/artifact 원문 경로는 보존한다.
