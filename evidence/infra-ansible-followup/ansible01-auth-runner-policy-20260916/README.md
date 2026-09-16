# gh 인증 범위 확인 및 repository Runner 허용 설정 변경 수신

## 확인된 사실

- 인증 txt236bytes, SHA256844169babce3a93d7d745a33e35d8ab7fe8acd57fa26d2c584719c2418ba156b 및 제출 sidecar 일치. GH_TOKEN/GITHUB_TOKEN 미설정, GWONUK(keyring), active=true, HTTPS, gist/read:org/repo/workflow scopes, AUTH_STATUS_RC=0. OAuth/classic 구분은 token 표시 행 제거로 확정하지 않는다. 입력에 실행 시각이 없으므로 임의 시각을 부여하지 않는다.
- 사용자: Policies에는 이미 추가돼 있었으며 Repository self-hosted runners에 infra-ansible을 추가했다고 보고. 첫 화면은 Selected repositories/2 selected repositories와 infra-ansible/infra-cicd 체크를 보인다. 두 번째 Policies 화면은 baseline/evidence/infra-ansible/infra-cicd 체크를 보인다. 이미지 bytes는 변경 없이 보관했다.
- 두 설정은 별도다. Actions 사용 허용이 repository-level self-hosted runner 생성 허용을 자동으로 대신하지 않는다. 공식 설명은 Repository self-hosted runners에서 Selected repositories를 고르고 저장소를 선택한 뒤 Select repositories로 반영하도록 안내한다.

## 판정과 다음 실행

필요한 repo scope는 이미 관측되어 지금 재로그인·scope 확대·새 PAT를 요구할 근거가 없다. 사용자가 변경한 저장소 수준 Runner 생성 허용은 앞선 등록 token POST403과 직접 관련된 정책 경계다. 다만 화면은 선택 상태이며 설정 저장/API 효과를 독립 확인한 것은 아니다. 이전403의 응답 설명도 누락되어 원인을 확정하지 않는다. 저장 후 기존 v1.1.1 관리 helper로 POST201/PASS_TOKEN_PACKET을 확인하는 것이 다음 단계다.

상세403 수집을 보완한 v1.1.2 후보는 사용자 변경 소식을 받기 전 로컬 작성/28검사를 했으나 GitHub 반영·배포·서버 실행하지 않았다. 정책 변경이라는 새 증거에 따라 해당 추가 배포를 보류한다. 현재 배포된 도구는 v1.1.1이며 코드 PR19 HEAD52271b7fafd5f442cf5540978b8c5df74bf352de를 유지한다.

## ansible01 기존 일반 로그인에서 재실행

선택을 Select repositories로 저장한 후 기존 v1.1.1 ZIP을 사용한다.

```bash
(
set -euo pipefail
cd "$HOME"
sha256sum -c FDS_Ansible_Admin_Token_v1_1_1.zip.sha256
TASK_ADMIN_DIR=$(mktemp -d "$HOME/ansible-admin-retry.XXXXXXXX")
unzip -q FDS_Ansible_Admin_Token_v1_1_1.zip -d "$TASK_ADMIN_DIR"
cd "$TASK_ADMIN_DIR/FDS_Ansible_Admin_Token_v1_1_1"
sha256sum -c SHA256SUMS
python3 -I -B admin-token.py
)
```

성공/실패 모두 HOME_EVIDENCE archive+sidecar를 기존 로그인 홈에서 제출한다. 성공 시 TOKEN_PACKET은 자격증명이므로 비공개로 cicd-runner01 기존 로그인 홈에만 전송한다. 대화/GitHub/증적에는 올리지 않는다. 실패하면 새 증적으로 다음 조치를 정하며 단순 반복하지 않는다.

## PASS_TOKEN_PACKET 이후

기존 Runner v1.1의 실제 PASS_PREPARE와 bundle/image binding을 유지하며 재빌드하지 않는다. cicd-runner01에서 다음을 실행한다.

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

이 단계는 등록 후 즉시해제 검사이며 Actions Job을 실행하지 않는다. 홈의 별도 Runner 증적 archive+sidecar를 제출한다. 이번 정책 선택 화면을 Runner 등록 성공·workflow 활성화·독립 승인·merge·운영 적용·Issue5 AC 완료로 간주하지 않는다.

공식 근거: [조직의 Actions 및 repository Runner 정책](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization), [repository Runner token API](https://docs.github.com/en/rest/actions/self-hosted-runners#create-a-registration-token-for-a-repository).
