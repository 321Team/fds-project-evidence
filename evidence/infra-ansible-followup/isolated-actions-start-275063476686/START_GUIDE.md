# 격리 Actions 정상 시험 시작 v1.0

대상: [PR20](https://github.com/321Team/infra-ansible/pull/20),
[Run35139314896 / Attempt1](https://github.com/321Team/infra-ansible/actions/runs/35139314896),
source `2750634766862d7fe19479acacc4259ee8315061`.
제작 시 Run/Job은 queued이며 Runner가 아직 배정되지 않았다. queued는 PASS가 아니다.
기준은 ISOLATED_ACTIONS_ENTRY.md, wrapper 사전 검토는 START_REVIEW.md다.

## 제공 내용

- 기존 Admin token v1.1.1, Runner v1.2, Input guard v1.0 원본 ZIP을 변경 없이 포함했다.
- 서버/일반 로그인/홈 확인 후 신규 홈 디렉터리에만 해제한다. HOME 환경변수를 덮어쓰지 않는다.
- 새 wrapper에는 chmod·삭제·prune·서비스/방화벽/권한 변경이 없다.
- 기존 Runner launcher가 계정·비sudo·자원·SELinux·rootless·이미지/prepare·격리를 재검사한다.
- 기존 token guard가 검증된 파일 FD에만0600을 적용한다. 입력 경로/홈 디렉터리의 권한을 변경하지 않는다.
- payload 내부 README는 과거 버전 제작 시점 기록이다. 실행에는 이 최상위 README와 01/02 진입점만 사용한다.
  이전의 임의 token 경로 chmod 안내를 실행하지 않는다.

## 1. 두 서버의 원래 로그인 홈에 ZIP과 sidecar 복사

`FDS_Ansible_Isolated_Actions_Start_v1_0.zip`과 `.zip.sha256`를
ansible01의 server01_ansible 홈, cicd-runner01의 server01_cicd-runner 홈에 각각 놓는다.
아래 블록은 서로 다른 호스트에서 실행한다. sudo로 시작하지 않는다.

## 2. ansible01 — 최신 대기 Run 확인 및 새 토큰 발급

```bash
(
set -euo pipefail
umask 077
cd "$HOME"
sha256sum -c FDS_Ansible_Isolated_Actions_Start_v1_0.zip.sha256
TASK_ACTIONS_ADMIN=$(mktemp -d "$HOME/ansible-actions-start-admin.XXXXXXXX")
unzip -q FDS_Ansible_Isolated_Actions_Start_v1_0.zip -d "$TASK_ACTIONS_ADMIN"
cd "$TASK_ACTIONS_ADMIN/FDS_Ansible_Isolated_Actions_Start_v1_0"
bash 01-admin-token.sh
)
```

PR head와 Run/attempt/job/labels·queued 상태가 다르면 토큰 발급 전 중단한다.
기존 gh 인증을 사용하며 로그인·관리 권한·조직 정책을 변경하지 않는다.
`PASS_TOKEN_PACKET`일 때 출력된 `TOKEN_PACKET=` 일반 파일을 기존 비공개 전송 방법으로
cicd-runner01의 `/home/server01_cicd-runner/` 바로 아래에 원래 파일명으로 복사한다.
PAT/gh 인증파일을 복사하지 않는다. token packet은 이 대화·GitHub·증적에 첨부하지 않는다.

실패하면 HOME_PREFLIGHT archive와 sidecar 및 Admin 도구 HOME_EVIDENCE를 제출한다.
이미 Run이 종료됐거나 attempt가 바뀌었다면 이 키트의 고정값을 임의로 편집하지 않는다.
새 실행 대상을 확인해 후속 시작 절차를 고정한다.

## 3. cicd-runner01 — 입력 보호 후 일회성 Job 수신

```bash
(
set -euo pipefail
umask 077
cd "$HOME"
sha256sum -c FDS_Ansible_Isolated_Actions_Start_v1_0.zip.sha256
TASK_ACTIONS_RUNNER=$(mktemp -d "$HOME/ansible-actions-start-runner.XXXXXXXX")
unzip -q FDS_Ansible_Isolated_Actions_Start_v1_0.zip -d "$TASK_ACTIONS_RUNNER"
cd "$TASK_ACTIONS_RUNNER/FDS_Ansible_Isolated_Actions_Start_v1_0"
bash 02-runner-serve.sh
)
```

질문에는 `ansible-runner-token-xxxx.json` 형식의 **파일명만** 입력한다.
새 파일의 실제 basename을 사용한다. 홈·디렉터리·절대경로는 입력하지 않는다.
형식/일반 파일/링크/소유자/만료 검사가 실패하면 serve는 실행되지 않는다.
입력 보호 성공 후 sudo 암호를 요청할 수 있다. Podman은 기존 전용 비sudo 계정으로 실행한다.

기존 성공 PREPARED 영수증을 고정했다:
`/home/ansible-verify/ansible-actions-6ca2111d63f740438342fd7da89e25da/evidence/PREPARED.json`.
기존 이미지/bundle이 일치하는지 launcher가 재확인한다. 파일이 없거나 상태가 바뀌면 중단하고 결과를 제출한다.
오류를 피하려고 PREPARED 파일·이미지 ID를 수기로 수정하지 않는다.

Listener는1개 Job 뒤 종료하고 controller는 최대1시간이다. 정상/실패 모두 종료까지 기다린다.
`SESSION_ENDED_REQUIRES_CI_REVIEW`는 세션 종료만 뜻한다. Actions Job/Check와 artifact를 별도로 인수한다.
중간 실패 때 동일 명령을 반복하지 않고 증적부터 확인한다. 기존 앱 Runner 서비스는 건드리지 않는다.

## 제출 및 후속

Runner 종료 후 `HOME_EVIDENCE=`의 `ansible-actions-runner-evidence.tar.gz`와 `.sha256`를 제출한다.
입력 보호 실패 시 해당 HOME_EVIDENCE의 RESULT.json과 sidecar를 제출한다.
새 session의 실제 Runner ID/name을 증적에서 읽고 관리 API 부재를 확인한다. 이전 ID3을 새 실행에 재사용하지 않는다.
정상 전체 PASS·artifact·정리 확인 후에만 별도 count 결함 PR/새 세션을 시작한다.

이 패키지는 Run 재실행/변수 변경/코드 병합/운영 apply를 수행하지 않는다.
로컬 확인: Bash3개 구문 통과, 잘못된 제작 환경 계정에서 두 진입점 조기 거절, payload3개 hash/manifest 정확 집합.
실제 관리자 토큰 발급 및 Runner serve는 이 패키지 제작 시 NOT_RUN이다.
