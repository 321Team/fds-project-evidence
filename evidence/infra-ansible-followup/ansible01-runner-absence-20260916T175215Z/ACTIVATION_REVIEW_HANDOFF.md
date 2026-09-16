# Workflow 활성화 검토 인계

이 문서는 검토안이다. 활성화, 변수 변경, Runner serve, 리뷰 요청 전송, merge를 실행하지 않았다.

## 검토할 고정 소스

| 범위 | PR | 현재 HEAD |
|---|---|---|
| Ansible CI 실행기·비활성 Workflow | infra-ansible #17 | 169571801d1b0cee0ba75137380149a48d6b56dd |
| egress 후속 회귀 | infra-ansible #18 | d5147ebff0febbb8ab2afca28fe64d68301e033c |
| 격리 Runner·입력 보호 도구 | infra-ansible #19 | 2fae52a9e09e33b8c8bff6c653b8533d8b52dc47 |

세 PR은 Draft/open이다. 등록된 PR review는 각각0건이므로 최신 HEAD 독립 승인은 확인되지 않았다.
증적 PR13의 기존 COMMENTED 리뷰는 6a6a384c2870729d26767ec8d6e745ee75567ffe 대상이며 최신 증적 승인이 아니다.
PR17/18의 요청 목록은 hayeounglee, PR19/증적PR13은 현재 요청 목록이 비어 있다.
이 스냅샷은 갱신 시점 확인이며 향후 리뷰/커밋 변경 시 다시 대조한다.

## 충족한 Runner 준비 조건

- 고정 v1.2 이미지 prepare PASS.
- 같은 이미지·bundle의 실제 registration-check PASS, ID3 등록/제거 rc0.
- 이번 ID3 또는 이름의 관리 API 목록 부재 PASS.
- 격리/정리 PASS.
- 입력 경로 방어 도구 로컬20/20 PASS. 실제 토큰 입력 시 보호 도구 서버 검사는 별도로 남는다.

위 사실은 등록 검증 단계의 완료 근거다. 실제 Actions Job 성공/실패 차단 또는 운영 적용을 증명하지 않는다.

## 활성화 변경에서 검토할 구체적 내용

현재 템플릿은 PR17의 `docs/ci/ansible-regression.workflow.yml`에 있다.
이 파일을 읽어 확인한 기존 동작은 다음과 같다.

- `ANSIBLE_CI_ENABLED == 'true'`, 비어 있지 않은 labels, 동일 저장소 PR 조건이 모두 충족될 때 Job 실행.
- contents:read, checkout persist-credentials:false, 고정 action commit.
- 실제 PR head SHA를 CI_SOURCE_SHA로 사용하고 exact source를 checkout.
- 신규 RUNNER_TEMP 하위 실행 디렉터리, Job timeout30분, 결과 artifact14일 보관.
- labels가 비어 있을 때 skip과 유효한 sentinel selector를 함께 유지.

활성화안은 이 경계를 유지하고 다음을 검토해야 한다.

1. 검토/승인된 소스의 템플릿을 `.github/workflows/`에 반영하는 별도 변경.
2. Runner selector 후보 `["self-hosted","Linux","X64","fds-ci","ansible-isolated"]`와 세션에서 실제 등록하는 labels의 일치.
3. `ANSIBLE_CI_ENABLED=true` 적용 시점과 실행 대상 source/workflow SHA 확정. 변수값은 이번 작업에서 변경하지 않았다.
4. CI_WHEEL_DIR을 사용할 경우 컨테이너 내부 경로와 고정 의존성 계약 확인. 호스트 경로를 임의로 노출하지 않는다.
5. 운영 SSH 키·배포 권한을 전달하지 않는 기존 격리 및 저장소 범위 유지.
6. fork 거절, 비활성/빈 selector에서 skip, 정상/고의 결함에서 각각 기대 conclusion을 검토한다.

## 실제 Actions 인수 순서

독립 검토와 활성화 변경 반영 후, 승인된 SHA를 고정하여 정상 및 고의 결함 시험을 각각 수행한다.
각각 새로운 단기 토큰과 ephemeral 1-job 세션을 사용한다. 토큰 경로는 입력 보호 도구를 통과해야 한다.
Run ID/Attempt, source/workflow/check SHA, conclusion, artifact SHA를 연결한다.
고의 결함 시험은 기대한 결함에서 nonzero가 발생했는지 확인하며 임의 환경 오류를 실패 차단 성공으로 대체하지 않는다.
각 세션의 container/workspace 정리 및 GitHub 등록 부재를 다시 확인한다.

다음 착수 대상은 위 활성화 변경의 딥리뷰와 검토 가능한 수정안 준비다.
현재 첨부의 성공만으로 Draft 해제, 승인, merge, 운영 apply, 엔진 전환, Issue5 AC 체크를 수행하지 않는다.
