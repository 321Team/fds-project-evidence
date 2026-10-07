# infra-ansible PR73 — 격리 CI 및 Runner 정리 원본

CODEX_ASSISTED. 책임: [infra-ansible#61](https://github.com/321Team/infra-ansible/issues/61), 소비 작업: [#62](https://github.com/321Team/infra-ansible/issues/62). CI 운영 증적이므로 상위 Record ID P1-CICD-01에 보존한다. Harbor Runtime 증적이 아니다.

## source / review / CI / merge 연결

- 실행 source: `d6914a8f70ce6439979dfbeee902481a648f6dea`, [PR73](https://github.com/321Team/infra-ansible/pull/73).
- [Run37612957459, attempt1, Job112764390649](https://github.com/321Team/infra-ansible/actions/runs/37612957459/job/112764390649): 2026-10-07 20:32:03~20:39:46 KST, SUCCESS. checkout source와 CI_RESULT source_commit 동일.
- 원본 [실행 결과 기록](https://github.com/321Team/infra-ansible/pull/73#issuecomment-6037162822), [Issue62 결과](https://github.com/321Team/infra-ansible/issues/62#issuecomment-6037163168).
- 실행 당시 독립 승인은 ef4bd345 기준이고, 해당 HEAD 이후 runbook/manifest 2파일 변경은 재검토 중이었다. 격리 CI 실행을 독립 리뷰 완료나 운영 배포로 표현하지 않는다.
- 이후 20:59:51 KST에 이하영(hayeounglee)이 exact d6914a8f를 재승인했다. 21:02:14 KST merge `da4e273e7e26a9a0b51211e5146066960df072b5`, 검토 HEAD와 merge tree 파일 차이0. 아래 원 조회 JSON은 CI 완료 당시 snapshot이므로 과거 OPEN/이전 승인 상태를 사후 수정하지 않는다.

## 실제 결과와 범위

Ansible2.16.19/2.21.3 각각 문법36건(총72), unit-tests/guards/contract/B2 양 엔진/DNS 양 엔진 7단계 rc0. artifact upload SUCCESS. `production_apply=false`, `operational_engine_transition=false`, 범위는 syntax/localhost fixtures다. 실제 Harbor 원본 분석·Docker restart·앱 Delivery·AC 인수·Issue Close가 아니다.

정상 로그인 server01_cicd-runner@cicd-runner01의 사용자 직접 sudo 인증 후 기존 v1.3 launcher와 ansible-verify/UID1001 격리 계정을 사용했다. Runner58/name `ansible-ci-e60c795b24ca4234ab95eabaf12ecf5b`가 Job과 container 결과에서 일치한다. 컨테이너 reported_job_result=Succeeded와 CI 성공은 각각 확인했다.

launcher/operator rc0, 종료20:40:03 KST. 원 archive의 CLEANUP은 runner/proxy/workspace=REMOVED이며 별도 조회도 GitHub runner0·podman 컨테이너0·runner.py 부재를 확인했다. 발급 측 packet은 전달 직후 삭제됐고 수신 측 packet/incoming은 종료 후 부재를 확인했다. 토큰 값·token hash·native Runner 자격증명 파일은 증적으로 수집하지 않았다.

## 원본과 무결성

두 압축본은 재압축하지 않았다. 각각1MiB 이하며 sidecar와 registry/ARCHIVE_CONTENTS.json의 내부 파일 목록을 함께 편입한다.

| 원본 | SHA256 | 검증 |
|---|---|---|
| ci-artifact-11479579258.zip | e46958722d6df05bd4cb332954412468e3f2e8e97955946f9997b982c5be61b4 | GitHub artifact digest 일치, 최상위 manifest1007/1007, fixture682개 및 명시 cache 제외3개 대조 |
| ansible-actions-runner-evidence.tar.gz | ef035835c0aa02f2a48e4f027b270b4694fa9358faf2999a713aa0cc4dd95af7 | 서버 sidecar 일치, 외부 manifest16개·내부 archive manifest9개 대조 |

서버 원본 경로는 `/home/server01_cicd-runner/ansible-actions-evidence-4nzn2vwg/ansible-actions-runner-evidence.tar.gz`다. 원 host archive 안에 원래 중첩 archive/sidecar와 정리·실행 기록이 있다. 실제 서버 보관 권한과 Git 파일 mode는 구분한다.

- `VERIFIED_RESULT.json`: 수신 후 검증 결과. 새로운 합성 실행 증적이 아니다.
- `job/run/artifact/runners-final.json`: CI 완료 직후 GitHub API 원 snapshot. 이후 리뷰·병합 상태와 구분한다.
- `preflight.json`, `release-result.json`: 입력 전달 직전 조건 및 발급 측 packet 삭제 기록. 과거 준비 상태를 현재 상태로 덮어쓰지 않았다.
- `operator.rc`, `operator-ended.txt`, `containers-final.json`, `runner-process-final.txt`, `receiver-token-absence.txt`: 기존 접근으로 읽은 종료·정리 결과.
- 폴더 `SHA256SUMS`는 이번 편입 시 생성한 manifest이며 압축 내부 원 manifest와 구분한다. hash 일치는 파일 무결성이지 원본 진위·AC 승인 자체가 아니다.

검증 스크립트 재실행이나 실제 Runtime 반복은 이번 편입에 포함하지 않는다. 독립 증적 검토·병합이 남아 있으며 편입만으로 #61/#62 또는 Phase1을 종결하지 않는다. 보완 시 기존 회차를 덮어쓰지 않고 별도 회차/기록으로 연결한다.
