# 정상 인수 후 count 재시험 및 독립 리뷰 인계

## 확인된 사실

1. 기존 정상 source `2750634766862d7fe19479acacc4259ee8315061` 대비 새 시험 source `31895081e30e27481e7c17407047c9454e3b247a`의 전체 tree를 직접 비교했다. 런타임 코드 변경은 tools/run-ansible-ci.py, 시험 변경은 tests/test_ci_regression.py다. 다른 차이는 Workflow ref/주석과 문서다. 정확한 변경 집합은 SOURCE_IMPACT.json에 보존했다. GitHub compare는 diverged/merge-base 기준이므로 두 HEAD의 직접 비교를 대신하지 않았다.
2. SSH guard, 기대 matrix, verification_contract.py, verification-kit.py, 비활성 일반 Workflow 템플릿, count 고의결함 patch는 Git blob이 같다. Runner PR19 HEAD도 동일하다.
3. 실행기의 export 본문은 try 블록으로 이동했고 export 예외 시 status FAIL, 오류 유형/errno, 결과 재기록 시도를 추가했다. fixture 판정/CLI 반환 매핑을 변경한 diff는 없다. 추가 단위시험은 합성 manifest 쓰기 오류에 대한 FAIL 및 잔존 PASS 수정 검사다.
4. 새 source의 정상 실제 Actions와 unit58은 이번 원본으로 확인됐다. 기존 count 시험은 source c50a6b3316fabba08d5211933e3733f8026e2d95 / Run35173018935/Attempt1 / Runner6의 과거 증적이며 새 source의 직접 count 실행으로 표기하지 않는다.
5. 기존 결함 시험에서 양 엔진 baseline은 PASS9/FAIL5/ERROR0, CI_RESULT FAIL, Job/Check failure, artifact 및 정리/원격 부재까지 검수됐다. 원본 인수 기록은 prior/ACCEPTED_OLD_RUNS.md와 기존 evidence 경로에 있다.

## 권고와 판단이 남은 부분

현재 변경으로 count 판정이나 정상 artifact export의 실패 전파가 달라졌다는 근거는 발견하지 못했다. 따라서 무조건 Run을 추가하기보다 **변경된 export 예외 처리와 기존 실패 증적의 충분성을 독립 검토하는 것이 우선**이다. 이 권고는 재시험 면제 승인이나 전체 코드 무결점 판정이 아니다.

검토 중 실패 전파/불완전 artifact 인수에 공백이 확인되거나 리뷰어가 새 source의 직접 count 증적을 요구하면 별도 격리 count 시험을 선택한다. 이 경우 현재 정상 source에서 count 한 줄만 변경하고, Workflow 허용 ref와 새 PR/HEAD/Run/Attempt/Job을 고정해야 한다. 기대결과는 양 엔진 baseline FAIL5/PASS9/ERROR0, CI FAIL/rc1, Job/Check failure, 정상 artifact 업로드, 새 Runner의 Runtime·로컬/원격 정리다. 과거 queued ID를 재사용하지 않는다.

## 최신 HEAD별 검토 범위

| 대상 | 후속 검토 범위 |
|---|---|
| PR17 / 6b2ac7a80be1acd187ac73cbd1cf957f708edf85 | export 예외의 FAIL 전파, best-effort 재기록 한계, test_ci_regression 추가시험, verification-kit.py 및 기존 리뷰에서 미대조한 파일, count 범위 결정 |
| PR19 / 4da96621fd05a4943b76ca32b860a5779ec65e00 | admin-token.py·launch.py 및 입력 보호/프록시/정리 코드의 미검토 범위, 최신 Runtime 원본과의 연결 |
| evidence PR13 / 이번 추가 HEAD | receipt7/7, Check/source/suite/app, 종료 후 Runner26 부재, prior Runtime/artifact 연결, 기존 blob 보존과 registry append |

COMMENTED를 APPROVED로 바꾸지 않는다. Review 승인·수동 병합·일반 CI 활성화·운영 적용은 각 범위의 판단을 유지한다. 불필요한 토큰 발급이나 정상 세션 반복은 요청하지 않는다.
