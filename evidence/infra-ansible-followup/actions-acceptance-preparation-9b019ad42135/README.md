# 활성화·음성 인수 준비 결과

실제 Actions NOT_RUN / 독립 승인 대기. 사용자 요청에 따라 승인 전 가능한 패치 준비와 국소 검증을 완료했다.

- 사전 딥리뷰 commit: `d9711b330dc213b0d5b8fea81dcb2a6d8b48e40a` (patch 작성 전 기록).
- source PR17: `9b019ad4213539e9a6edf2409e1d0bd0d4ef46f6`.
- 실제 국소 시험 source base: `5ed6d3947a15d59cf6c360c0419f961b8143c707`의64파일. TESTED_SOURCE_FILES.json Git blob/tree 대조.
- 게시 변경은 runbook1개 수정·검토/인수 문서2개와 비활성 patch2개 추가다. 기존 실행 코드·Workflow 템플릿·guard blob은 보존했다.
- 활성화 patch: Workflow1개 신규 추가를 제안하며 템플릿과 동일 바이트. 실제 저장소 활성화는 하지 않았다.
- 결함 patch: 첫 guard count `!= 1` → `!= 2` 한 줄. OR·다른 guard·시험 기대값은 유지한다.

기존 runbook의 `or → and`는 matrix의 OR 전제조건에서 실제 CLI 전에 중단됨을 로컬 생성 단계에서 재현했다.
새 count 결함은 variant6개 생성 후 첫 CLI 호출 지점까지 도달한다. 이 생성 단계 확인은 subprocess를 가로챈 모의 검증이다.
다음 public CLI 결과는 실제 Ansible2.16.19 localhost 실행이며 생성 모의 검증과 구분한다.

| 대상 | 결과 |
|---|---|
| 정상2.16.19 | harness rc0, PASS14 / FAIL0 / ERROR0 |
| count 결함2.16.19 | harness rc1, Ansible CLI rc2, PASS9 / FAIL5 / ERROR0 |
| 결함 source 단위 | 57 PASS / rc0, guard 검사 이전의 unit 실패가 아님 |
| 적용 범위 | 활성화1파일·결함1줄; 역적용 후 source bytes 복원 |

5 FAIL은 첫 guard의 one_plain/one_restricted/two_plain/two_restricted/mixed이며 두 번째 guard7개는 PASS다.
이 실패 원문을 PASS로 바꾸지 않았다. 기대한 결함 탐지를 확인했다는 뜻이다.
negative-unit stdout의 일부 PASS/FAIL JSON은 기존 unit의 모의 출력이다. unittest stderr57 OK/rc0으로 판정한다.

2.21.3, 전체 CI, 새 게시 HEAD의 전체 Runtime, GitHub Actions, 새 Runner 세션은 이번에 실행하지 않았다.
기존 서버 PASS를 새 SHA의 전체 CI PASS로 전용하지 않는다. PR19는 `2fae52a9e09e33b8c8bff6c653b8533d8b52dc47` 그대로다.
다음은 최신 HEAD 독립 검토 → 별도 활성화 변경 → 정상/결함 Actions·artifact·세션 정리 인수다.
운영자 수집 증적은 원래 로그인 홈의 신규 전용 경로에 저장하며 임의 경로 chmod/재귀 삭제는 하지 않는다.

[인수표](https://github.com/321Team/infra-ansible/blob/9b019ad4213539e9a6edf2409e1d0bd0d4ef46f6/docs/ci/ACTIONS_ACCEPTANCE.md)
및 INPUT_RECEIPT.json의 범위를 확인한다. 이 폴더는 선택 원문 증적이며 Actions artifact 전체가 아니다.
원본14개 관찰/각 CLI 로그/summary·rc를 정상과 결함별로 보존했다. module cache·venv·wheel은 포함하지 않았다.
