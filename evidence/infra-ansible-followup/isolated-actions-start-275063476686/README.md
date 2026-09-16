# Issue #5 격리 Actions 정상 시험 착수 기록

정본 [docs-v3.1.18](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.18),
최종화 commit `72599ae49342b0fb8dbd3d8ee60314afb9f907bb`의 Baseline §4/§10 및 P1-CICD-01 요구사항을 검토했다.
사용자가 격리 시험 착수를 명시적으로 지시했고, Workflow 작성 전에 착수 기준·딥리뷰를 commit
`a54ac17ef70b7465e45b31b423811ed630e35eeb`으로 기록했다.

## 현재 상태

- [시험 전용 Draft PR20](https://github.com/321Team/infra-ansible/pull/20), source `2750634766862d7fe19479acacc4259ee8315061`.
- [Run35139314896 / Attempt1](https://github.com/321Team/infra-ansible/actions/runs/35139314896), Job104939547998: **queued / Runner 미배정**.
- 정상 시험만 생성했다. 서버 serve는 연결 부재로 Codex에서 실행하지 않았으며, 실제 CI 판정은 NOT_ASSESSED다.
- reviewer `supreme33-kr`에게 PR20 리뷰를 요청했다. 독립 승인·병합·Issue #5 AC 완료를 선언하지 않았다.
- 정상 결과·artifact·새 세션 정리 확인 뒤에 결함 시험을 별도 진행한다.

## 착수 조건 및 승인 해석

`ISOLATED_ACTIONS_ENTRY.md`에 정본 조항과 이번 시험의 권장 구현값을 구분해 기록했다.
확인한 정본은 모든 격리 시험 전에 독립 승인을 일괄 요구하지 않는다.
기존 자체 작성 기록의 일괄 사전 승인 해석은 이번에 정정했다.
독립 리뷰·최종 인수·수동 병합 및 운영 배포 통제는 유지한다.

시험은 같은 저장소·main 대상의 고정 시험 브랜치 두 개와 격리 라벨로만 선택하며,
현재 정상 브랜치 하나만 생성했다. contents:read, full-SHA Actions, exact checkout,
운영 자격증명 분리, rootless 일회성 Runner 및 기존 자원·격리·정리 검사를 유지한다.
PR17 원본68개 파일은 모두 동일하고 기준 문서·시험 Workflow 두 파일만 추가했다.

## 로컬 검증과 서버 시작 묶음

- Workflow 조건 모델18개, 보호 조건 완화 변이5개 검증.
- Bash 진입점3개 구문 검사, 잘못된 제작 환경에서 진입점2개 조기 중단.
- 기존 Admin v1.1.1, Runner v1.2, Input Guard v1.0 ZIP3개 hash 및 manifest 정확 집합 보존.
- 위 검사는 실제 GitHub Actions의 정상/결함 성공 증적이 아니다.
- 시작 묶음: `FDS_Ansible_Isolated_Actions_Start_v1_0.zip`,101059bytes,
  SHA256 `fa8ec5397af20239e02909039a2b080d62618dd8033fc362fa565ecf53b200db`.
- 서버 명령은 `START_GUIDE.md`; wrapper 사전 검토는 `START_REVIEW.md`.
  증적은 기존 로그인 홈의 새 디렉터리에 생성하며 token은 증적에 포함하지 않는다.

`RUN_SNAPSHOT.json`은 선택한 Run 필드와 attempt1 jobs 응답을 기록한다.
`RESULTS.json`의 상태는 기록 시점의 관측이며, 실제 서버 시작 전 관리자 진입점이 Run/PR/Job을 다시 확인한다.
현재 시험 HEAD와 Run이 변경되면 이 고정 시작 묶음은 토큰 발급 전에 중단한다.
