# Ansible CI 활성화 선행 검토·수정

현재 판정: **PASS_LOCAL / PASS_LOCAL_MODEL / PASS_EXPECTED_FAILURES**.
실제 GitHub Actions, 새 CI HEAD의 양 엔진 전체 Runtime, 독립 승인, 활성화, merge는 미완료다.

## 코드와 사전 검토

- [PR17](https://github.com/321Team/infra-ansible/pull/17) 새 HEAD: `5ed6d3947a15d59cf6c360c0419f961b8143c707`.
- 코드 변경 전 딥리뷰 커밋: `224f8cdb3e44def48ee016d1565d9e2bea1f1d6a`.
- 부모 검토 기준: `169571801d1b0cee0ba75137380149a48d6b56dd`.
- 실행한 작업 트리는 위 부모에서 분기한 로컬 수정본이었다. TESTED_SOURCE_FILES.json의64개 파일 Git blob이 게시된 새 tree 전체와 일치함을 대조했다.
- 기존63개 파일 중60개 보존, Workflow·단위시험·runbook3개 변경, 사전검토1개 추가.
- PR19 `2fae52a9e09e33b8c8bff6c653b8533d8b52dc47` 및 실제 prepare/등록 PASS를 받은 Runner 본체·이미지는 변경하지 않았다.

### 수정 이유와 동작

기존 runs-on은 설정 JSON을 직접 사용해 필수 격리 라벨 없이도 Job 조건을 통과할 수 있었다.
비활성 초안에서 발견한 설정 경계 결함이며 실제 잘못된 Runner 배치가 관측된 것은 아니다.
infra-cicd 저장소 전용 Runner가 공유된다는 가정도 하지 않는다.

runs-on을 `[self-hosted, Linux, X64, fds-ci, ansible-isolated]`로 고정했다.
ANSIBLE_CI_RUNNER_LABELS는 정해진 문자열에 대한 확인값으로만 사용하고 임의 Runner 선택에 사용하지 않는다.
빈 값·넓은/부분 라벨·잘못된 JSON·객체는 skip하고 동일 저장소 PR 및 workflow_dispatch만 허용한다.
GitHub 문자열 비교의 대소문자 무시를 로컬 모델에 반영했으며 순서·공백은 자동 보정하지 않는다.

## 실제 수행한 로컬 검증

- `python3 -B -m unittest discover -s tests -p 'test_*.py' -v`: **57개 PASS / rc0**.
- 원문 YAML 조건·selector 모델: **22개 기대결과 일치**.
- 변수 selector / 넓은 label 설정 / non-PR 이벤트 우회 재주입3종: 모두 assertion failure 및 **exit1** 확인.
- 실패는 테스트 결함 감지에 의한 것이며 예외/구문 오류로 우연히 실패한 결과가 아니다.
- 최종 원문 유지, diff 공백 검사, 게시 source64 Git blob 일치, .github/workflows 파일0개 확인.

unit.log에 출력된 일부 PASS/FAIL JSON과 엔진표시는 기존 단위시험의 모의 CLI stdout이다.
**새 Ansible 엔진 Runtime PASS 또는 실제 Actions 결과가 아니다.** 총계는 unittest의 Ran57/OK와 rc0로 판정한다.
로컬 모델은 GitHub의 실제 expression engine/scheduler 검증을 대체하지 않는다.
기존 1695718의 실제 서버 양 엔진 PASS 원문은 보존하며 이번5ed6d39 HEAD 전체 실행으로 전용하지 않는다.

## 리뷰어 지정

현재 사용자 지시에 따라 이재환(`supreme33-kr`)에게 PR19·증적PR13·수정PR17 리뷰 요청을 등록했다.
Ansible 지원 담당 기록, 최근 CICD 관련 검토 이력 및 양 저장소 write 권한을 확인했다.
현재 CICD 기록에 이하영 부재/이재환 대체 검토가 명시돼 있지만 그 과거 예외를 자동 확장한 것은 아니다.
이번 선택은 현재 사용자의 관련 담당자 지정 지시에 따른 것이다.

- [Ansible 담당 근거](https://github.com/321Team/fds-project-baseline/issues/65)
- [최근 CICD 검토 담당 근거](https://github.com/321Team/infra-cicd/pull/13)
- PR17의 기존 hayeounglee 요청과 과거 리뷰는 유지했다. PR18은 변경하지 않았다.
- 리뷰 요청은 승인·인수·merge가 아니다. 상시 Lead/Support·저장소 권한은 변경하지 않았다.

## 다음 단계

새 HEAD의 독립 리뷰 → 별도 Workflow 활성화 변경 검토/반영 → 격리 ephemeral Runner에서 정상·고의 결함 Actions 인수.
실제 source/workflow/check SHA, Run/Attempt, artifact 해시와 각 세션 정리·등록 부재를 확인한다.
현재 Workflow는 docs/ci의 비활성 템플릿이며 변수 변경·등록/serve·토큰 발급·운영 적용은 수행하지 않았다.
서버에서 지금 추가로 실행할 명령은 없다.

공식 근거:
[Runner 라벨 매칭](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/use-in-a-workflow),
[표현식 비교](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions).
