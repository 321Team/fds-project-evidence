# PR #22 export-fix positive Actions 원본 검증

2026-09-17 수신한 `ansible-actions-runner-evidence.tar(9).gz`와 sidecar를 GitHub 원본 Job·artifact에 연결해 검증했다. **Run/Job success, CI_RESULT PASS, artifact 내부 검증 PASS, Runtime·격리·로컬 정리 PASS**다. Check 원문과 Runner ID26의 원격 등록 부재는 아직 수집 전이다.

## 대상

| 항목 | 값 |
|---|---|
| PR / source | #22 / `31895081e30e27481e7c17407047c9454e3b247a` |
| 변경 원본 PR17 HEAD | `6b2ac7a80be1acd187ac73cbd1cf957f708edf85` |
| Run / Attempt | `35195838409` / `1` |
| Job / 결론 | `105118736321` / success |
| Runner | ID26 / `ansible-ci-a6b75591ba3d4d38b5a3c3797afd8d37` |
| Job 시각 | 2026-09-17 17:16:37–17:23:49 KST |
| Runtime 세션 | 17:16:22–17:24:06 KST |
| 실행 Workflow blob | `d27abb5111452f1b563d3cf0531a717483bec82c` |

Workflow/event SHA `c1bad37e7fe8fafb9297f1fc1bbc015e4de7caa9`와 checkout source는 구분했다. 해당 event SHA의 Workflow 원문 blob은 사전검증본과 동일하다. exact-source checkout, CI 실행, artifact 보존 단계가 모두 success이고 세션·Job·CI 시각 순서도 일치한다.

## 원본 무결성

| 원본 | SHA256 | 검증 |
|---|---|---|
| 외부 Runtime 6,332 bytes | `8ae7c22a2c294aa1a77fcb7cb77f3424063ddb7ef625beabb2b5561b13b1cb64` | sidecar, manifest 16/16 |
| 중첩 Runtime | `d2cf2a5c7cecc38d1ac7ac0dac9f3aa233303bc55d10daa849f1ac1f5b2ec5af` | sidecar, manifest 9/9 |
| Artifact #10487510294, 459,726 bytes | `b973ff4e2b021fb7de017684d4b928c3958349d339df58fda360a3987352d9a5` | API/upload/실제 ZIP digest 일치, manifest 831/831 |

Artifact 원본 ZIP을 직접 확보했다. fixture manifest 669개 중 666개 파일이 일치하며, 나머지 3개는 ARTIFACT_SCOPE에 해시까지 명시된 module-cache 제외 항목과 정확히 일치한다. 다른 누락을 허용한 것은 아니다. 전체 보관본은 `FDS_Ansible_Export_Fix_Runtime_Review_20260917_v1_0.zip`에 원본 archive와 검증 결과를 함께 담았다.

## 실제 Actions 결과

- 엔진 2.16.19 / 2.21.3 구문검사 **32/32 rc0**.
- 원본 `unit-tests/stderr.log`: **58 tests / OK**. 이번 소스의 export 오류 회귀시험을 포함한다.
- Guard **14/14**, Contract **58/58** 기대결과 일치. 누락·중복 없이 엔진×case 집합을 확인했다. Contract 실제 CLI report 32개와 origin 파일 해시를 대조했고, 파생 변조 26개는 별도 matrix 행이다.
- Guard baseline은 각 엔진 14개 모두 PASS. 고의 변조 행의 FAIL/ERROR는 기대한 탐지 결과이므로 정상 baseline 실패로 해석하지 않는다.
- 양쪽 DNS fixture rc0. `CI_RESULT=PASS`, `PASS_FRESH_OFFLINE_FIXTURES`.
- Runtime IPC·identity 정상, configure/listener rc0, `reported_job_result=Succeeded`, container exited/rc0/OOM=false.
- 격리 **18/18 true**, rootless, SELinux Enforcing. runner/proxy/workspace 모두 `REMOVED`.
- `remove_rc=null`은 원격 삭제 성공 증명이 아니다. Runner 등록 부재는 반드시 별도 조회한다.

## 남은 인수·리뷰

1. 동일 Attempt/Job에 연결된 Check `105118736321`의 원문 성공·source·suite·app 확인. 현재 연결의 endpoint 제한으로 원문을 읽지 못했다. Job success를 Check 원문 검증으로 대체하지 않는다.
2. 모든 repository Runner 페이지에서 ID26 또는 해당 이름 부재 확인. 다른 Runner 존재는 허용한다. ID5/6 부재를 승계하지 않는다.

두 항목은 `FDS_Ansible_Export_Fix_Receipt_v1_0`에서 기존 ansible01 gh 인증으로 GET만 수행한다. 원본 artifact는 다시 다운로드할 필요가 없다. Runner serve, token, prepare, rerun은 이번 후속 절차에 필요하지 않다.

최신 독립 리뷰: PR17과 PR19에 supreme33-kr의 **COMMENTED** 리뷰가 추가됐다. 각각 Workflow/CI 실행기 핵심 부분, container.py의 격리 검증을 집중 확인했으며, 리뷰 본문은 전체 대조·실서버 재현·사람 확인을 PENDING으로 남겼다. **APPROVED가 아니다.** PR13의 기존 COMMENTED도 그대로다. 미검증 파일 범위와 전체 인수 판단은 남아 있다.

이번 정상 Actions는 수정 소스의 정상 실행·artifact 생성 회귀를 확인한다. 모든 저장장치 고장을 실제 서버에서 주입했다는 의미는 아니다. 앞서 별도 검증한 지속 쓰기 불가 조건의 한계와 LOCAL/MOCK 결과를 실제 장애 주입으로 승격하지 않는다.

운영 Apply, 운영 엔진 전환, 독립 승인, PR 병합, Issue 종결은 수행하지 않았다. PR22는 TEST ONLY / DO NOT MERGE를 유지한다.

## 재검증

전체 보관 ZIP을 풀고 포함된 `verify_archives.py` 다음 `verify_semantics.py`를 실행하면 파일 해시와 의미 대조를 재현할 수 있다. 검증기는 업로드 원본이 없으면 `originals/`의 동일 bytes를 사용한다. Git evidence에는 검토에 필요한 원문 일부와 전체 원본의 인덱스·해시를 싣는다. Git의 발췌만으로 전체 ZIP bytes를 재구성하지 않는다.
