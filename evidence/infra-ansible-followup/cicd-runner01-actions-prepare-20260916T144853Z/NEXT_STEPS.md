# 다음 실행: 등록 후 즉시 해제

실제 prepare를 통과한 v1.1 키트를 그대로 사용한다. 이미지나 코드 변경 및 prepare 재실행은 현재 필요하지 않다. 아직 등록/해제 API 동작을 검증한 것은 아니므로 다음 검사 성공을 선행 확정하지 않는다. 이 단계는 Job Listener를 시작하지 않는다.

## 1. ansible01 기존 관리 로그인

같은 `FDS_Ansible_Actions_Runner_v1_1.zip` 및 `.zip.sha256`를 ansible01 로그인 홈에도 복사한다. zip SHA256은 `aefcc2cf5be904a3cdde0b769e5bed3650e593b3123aee71f0f0ec3234efc65a`다. 새 폴더에 풀어 관리 호스트에서만 단기 토큰을 발급한다.

```bash
(
set -euo pipefail
cd "$HOME"
sha256sum -c FDS_Ansible_Actions_Runner_v1_1.zip.sha256
TASK_TOKEN_KIT_DIR=$(mktemp -d "$HOME/ansible-runner-token-kit.XXXXXXXX")
unzip -q FDS_Ansible_Actions_Runner_v1_1.zip -d "$TASK_TOKEN_KIT_DIR"
cd "$TASK_TOKEN_KIT_DIR/FDS_Ansible_Actions_Runner_v1_1"
sha256sum -c SHA256SUMS
python3 -I -B admin-token.py
)
```

성공하면 `TOKEN_PACKET=/home/server01_ansible/ansible-runner-token-....json`처럼 파일 경로를 출력한다. gh/PAT 자격증명은 관리 호스트에 유지한다. 해당 packet 하나만 기존 WinSCP/SFTP 전송 방법으로 cicd-runner01의 `server01_cicd-runner` 홈에 복사한다. **packet은 자격증명이므로 이 대화·증적에 첨부하지 않는다.** 경로만 입력하며 token 원문을 명령줄에 붙이지 않는다.

GitHub의 등록·제거 토큰은 발급 후1시간 유효하다. 이 키트는 각 단계에서 두 토큰 모두 10분 이상 남았는지 검사하므로 전송 후 곧바로 검사한다. 발급 권한 오류가 있으면 해당 단계에서 멈추며 PAT를 복사해 우회하지 않는다. 공식 근거: [GitHub repository Runner token API](https://docs.github.com/en/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository).

## 2. cicd-runner01 기존 로그인

아래 질문에는 방금 전송한 packet의 **절대 파일 경로**를 입력한다.

```bash
(
set -euo pipefail
cd "$HOME/FDS_Ansible_Actions_Runner_v1_1"
sha256sum -c SHA256SUMS
read -r -p '전송한 TOKEN_PACKET 절대 파일 경로: ' TASK_TOKEN_PATH
chmod 600 -- "$TASK_TOKEN_PATH"
sudo bash run.sh registration-check \
  --prepared /home/ansible-verify/ansible-actions-a1a17a5e782944ab924a6af14fae7a52/evidence/PREPARED.json \
  --token-file "$TASK_TOKEN_PATH"
)
```

성공·실패 모두 `HOME_EVIDENCE=`가 가리키는 기존 로그인 홈의 archive와 `.sha256`를 제출한다. 토큰 packet은 제출하지 않는다. 등록 성공 후 API에 남는 이름은 `ansible-ci-<이번 새 UUID>`이며 prepare 때 관측한 UUID를 새 등록 ID로 재사용하지 않는다.

`PASS_REGISTRATION_CHECK`는 config/remove 반환코드, repository/name/id, 컨테이너 정리의 통과다. 후속으로 관리 호스트의 Runner 목록에서 이번 ID/name의 부재도 확인해야 한다. 관측 대상 이름/ID는 등록 검사 증적을 받아 확정하며 임의 추정하지 않는다. 기존 infra-cicd Runner ID2를 변경하거나 삭제하지 않는다.

등록/해제 검사까지 확인한 후에 독립 활성화 리뷰와 정상/고의 결함 Actions로 진행한다. 지금 `serve`나 workflow 활성화로 건너뛰지 않는다.
