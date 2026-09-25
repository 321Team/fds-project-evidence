# PR47 Runner readiness 수신 검증 — 2026-09-24

관련: [infra-ansible #5](https://github.com/321Team/infra-ansible/issues/5), [PR47](https://github.com/321Team/infra-ansible/pull/47). 조회·수신 검증: 2026-09-24 04:18–04:22 KST. 작성: GWONUK의 Codex 보조 수신 검토. 타인의 독립 리뷰가 아니다.

## 판정

**PASS_PREPARED_IMAGE_READINESS 수신 검증 완료.** cicd-runner01의 기존 v1.3 PREPARED와 현재 rootless image 결합 확인 범위다. 일반 CI, 새 세션 전체 격리/IPC, Runner 등록·종료·정리, Issue5 최종 인수는 미완료다.

| 항목 | 확인 결과 |
|---|---|
| 원본 | ansible-pr47-readiness.tar.gz, 1,361 bytes |
| SHA256 | `d58c76fa3818c30f273115d4f18b515aeb8ed079b6e6ab712ba7fa7d598f1153` — sidecar 일치 |
| 내부 무결성 | manifest 6/6 일치, 일반 파일 7개(자체 manifest 포함), 누락·추가 파일·링크 없음 |
| 현장 시각 | 수집 2026-09-24 02:00:56 KST, 검사기 결과 시각 02:00:58.858930 KST |
| 현장 결과 | host=cicd-runner01, execution.rc=0, stderr=0 bytes |
| 후보 HEAD | `c6ba5f87711acc3eeeba12c13c72cedd09d178f8` — 조회 시 PR47과 일치 |
| PREPARED SHA256 | `955be6482f01e58bea960efb14e6ffed52dc61f1beb79e1de57eb03a098cff73` — 현장 검사기 보고값 |
| bundle | `e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6` |
| image | `sha256:3f96787b2a8db29294002677a3e733689439952ad9e95db721acf8e16ff601f1` |
| 부수 행위 | token_read / container_started / runner_registered 모두 false |

`received/` 7파일은 수신 archive에서 읽은 bytes를 그대로 보존했다. 원본 압축파일은 Git에 재압축·편입하지 않았다. 아래 보관 참조와 같은 bytes다.

- 원본 [보관 파일](https://chatgpt.com/api/library/files/libfile_0fad781a3fe48191b623f2ea7e81fba1/download), sidecar [보관 파일](https://chatgpt.com/api/library/files/libfile_00bc23e7d8848191925daf56de7821fa/download). 이 URI는 원 소유자 접근 범위이며 리뷰어 접근 권한을 새로 부여한 것은 아니다. 팀 리뷰에는 Git의 전체 추출 원문과 검증 기록을 제공한다.
- [변경 없는 검사기 원문](https://github.com/321Team/fds-project-evidence/blob/b90c1d39decb6bfc5adeeebd8591133304a7a9c5/evidence/infra-ansible-followup/export-fix-actions-start-31895081e30e/FDS_Ansible_Export_Fix_Start_v1_0/check-readiness.py), blob `ab0a41b12e1bc743b993d9f27c5658b75311e90a`.
- 검사기 조건: 전용 계정 UID1001/GID1002, cicd-runner01, PREPARED 비링크·owner·0600·크기, PASS_PREPARE/repository/version/bundle/image/cleanup 결합, podman image inspect의 image ID/amd64/linux/bundle label 확인.

**한계:** archive에는 실행된 검사기 사본, PREPARED 전체 원문, image inspect 원문이 없다. source 연결은 CONTEXT와 저장소 원문 대조, 상세 값은 현장 검사기의 결과 보고에 근거한다. 수신자가 서버에서 다시 실행했거나 PREPARED 원문 해시를 독립 재계산했다고 주장하지 않는다. 위 범위 수신에 추가 재수집을 필수로 요구하지 않는다. 새 serve는 기존 launcher의 현장 계정/권한/격리/IPC 검사로 별도 판정한다.

## 최신 GitHub 대조와 다음 단계

- PR47 Open / Ready, HEAD 변동 없음. main 대비 Workflow 55줄 한 파일이며 blob `a6741487ae1a3b96afef6c7ae05e4c63942b42b8`은 템플릿과 동일하다. 기존 같은 HEAD 기술 COMMENT를 재사용한다. 현재 독립 APPROVED 없음, 기존 요청 Reviewer hayeounglee 유지.
- Run35889332032 / Attempt1 / source c6ba5f87는 `completed / skipped`. 일반 회귀 PASS가 아니다.
- Variables의 마지막 프로젝트 기록은 enabled=false 및 고정 라벨이다. 이번에는 관리 화면/API 실제 변수값을 새로 조회하지 않았다. 활성화 직전에 다시 확인한다.
- 일반 Workflow 최초 인수의 구문 기대값은 PR47에 기록된 23개×두 엔진=46개이며 실제 plan의 `(engine,path)` 전체 집합을 대조한다. 과거 32개 성적을 현재 PASS로 승계하지 않는다.
- 기존 PREPARED/image는 재사용 후보로 확인됐다. 새 prepare/이미지 build, 과거 PR20/21/22 시험 반복, 과거 token/preflight 재사용은 이번 후속에 포함하지 않는다.

순서: 현재 HEAD 독립 Workflow 리뷰 → 준비된 실행 시점의 Variables/Runner 공급 → 일반 Workflow 정상 Run과 고의 count 결함 Run의 각 source/attempt/Check/artifact → 각 세션 종료·로컬 정리 및 실제 Runner ID/name 부재 → 증적 독립 리뷰·Lead 최종 AC 판단. 증적 PR 병합을 현장 준비 작업의 추가 선행조건으로 삼지 않는다.

일반 자동 활성화·코드 병합에는 현행 리뷰 정책을 적용한다. 별도 승인된 격리 후보 시험까지 독립 승인을 일괄 선행으로 확대하지 않는다. 이번 작업에서는 새 Run을 만들거나 등록 토큰을 발급하지 않았다.

## 단계 구분

| 단계 | 이번 결과 |
|---|---|
| STATIC / 수신 검증 | archive·manifest·원문 판정·source/HEAD·기존 review 대조 완료 |
| MOCK | 새 모의시험 미실행, 동일 코드의 이전 검증을 새 실행으로 표시하지 않음 |
| CI | PR47 현재 Run skipped; 정상/결함 일반 CI 미실행 |
| RUNTIME | 제출된 02:00 KST readiness만 제한 범위 PASS; 수신자 서버 직접 실행 없음 |
| REVIEW | 자체 수신 검토 완료; PR47 및 이 증적 편입의 독립 리뷰 별도 |
| MERGE / PUBLICATION | 이번 증적은 검토용 후보; PR47 병합·운영 반영·정본 발행 없음 |

Issue5 Open과 #9 운영 엔진 전환 PENDING을 유지한다. NTP PR44의 별도 차단은 일반 CI 선행조건으로 추가하지 않는다.
