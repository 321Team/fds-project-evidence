# 이전 등록 검사 Runner의 부재 확인

## 제출 증적 판정

`ansible-runner-absence.rgFIkmVJ.txt`는 137 bytes, SHA256 `9f1fe479c231d8176fd97f56601755832217606c42f32dbf42640e428de00174`다. 원본 sidecar와 일치하며 두 파일을 변경 없이 보존한다.

- 저장소: `321Team/infra-ansible`.
- 대상 이름: `ansible-ci-e64364fe3bab45fabcc43aea675c9693` (이전 v1.1 등록 실패의 실제 이름과 일치).
- 기록된 조회 시점: 2026-09-16 16:39:10 UTC / 2026-09-17 01:39:10 KST.
- `query_rc=0`, 대상 이름과 일치하는 JSON 객체 없음.

제공한 `gh api --paginate`의 정확한 이름 필터 조회 절차에 따라, **제출 증적 기준 조회 시점의 대상 이름 부재를 확인**한다. 파일에는 선별 결과만 있어 저장소 전체 Runner 수/다른 이름의 상태/원래 agentId/독립 API 재조회 성공까지 증명하지 않는다. 이번 작업에서 삭제는 수행하지 않았다. 기존 infra-cicd Runner ID2는 대상이 아니다.

v1.1의 configure/remove rc0 및 전체 FAIL은 이력으로 유지한다. 부재 확인은 원래 검사 실패나 BOM 직접 예외를 소급 수정하지 않는다. v1.2 실제 PASS_PREPARE와 결합해 새 단기 토큰으로 등록·제거 재검사할 선행 확인을 충족했다. 실제 새 등록/Actions는 아직 NOT_RUN이다.

## 1. ansible01: 새 토큰 발급

기존 발급 PASS한 관리 도구 v1.1.1을 그대로 사용한다. sudo 없이 기존 관리 로그인에서 실행한다. 기존 ZIP/sidecar가 로그인 홈에 있다는 전제다. 새 폴더에 풀어 이전 실행을 덮어쓰지 않는다.

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

`PASS_TOKEN_PACKET`인 경우에만 `TOKEN_PACKET=` 파일을 비공개 전송 경로로 cicd-runner01의 `/home/server01_cicd-runner/`에 옮긴다. 양쪽 토큰은 사용 시 최소10분 이상 남아 있어야 하므로 바로 전송/실행한다. 토큰 원문/JSON은 대화나 GitHub에 첨부하지 않는다. 실패하면 이 단계의 HOME_EVIDENCE 압축/sidecar를 제출하고 등록 검사를 진행하지 않는다.

## 2. cicd-runner01: v1.2 등록·제거 검사

관리 도구의 이전 README에 있는 v1.1 등록 경로 대신, 아래 실제 검증된 v1.2 키트와 새 PREPARED 경로를 사용한다. 관리 helper 버전1.1.1과 Runner 버전1.2는 서로 다른 도구의 버전이다.

```bash
(
set -euo pipefail
cd /home/server01_cicd-runner/ansible-runner-v1_2.RxNbHB6V/FDS_Ansible_Actions_Runner_v1_2
sha256sum -c SHA256SUMS
read -r -p '전송한 새 TOKEN_PACKET 절대 경로: ' TASK_TOKEN_PATH
chmod 600 -- "$TASK_TOKEN_PATH"
sudo bash run.sh registration-check \
  --prepared /home/ansible-verify/ansible-actions-6ca2111d63f740438342fd7da89e25da/evidence/PREPARED.json \
  --token-file "$TASK_TOKEN_PATH"
)
```

예상 상태는 `PASS_REGISTRATION_CHECK`다. 새 고유 이름으로 등록한 뒤 제거하며 Listener/job을 시작하지 않는다. 실패 시 다음 단계로 진행하지 않는다. 계정·격리·이미지/키트 결합·토큰 유효시간·identity·반환코드·정리를 실행기에서 다시 확인한다.

새 관리 토큰 발급과 등록 검사 각각의 `HOME_EVIDENCE=` 압축/sidecar를 제출한다. 두 도구 모두 기존 로그인 홈에 증적을 만든다. 새 등록 결과의 ID/name에 대한 관리 API 부재도 후속 확인한다.

## 상태 유지

Runner 코드 변경 없음. PR19 HEAD `9cb8d6c702f750b9276daec859b1c237109daed1`, bundle `5c0e851db396689ca6549562f2a442cd5a6e6b58d2d30dd0f99d5f3338dc3bfe`, 준비 이미지 `sha256:02d097ce453f4011218a081286e02be2c4d64599d1b329d6d98e049b9c34fd85` 유지. 코드·증적 PR은 Draft, Issue5는 open/AC 미완료다. 실제 등록 검사/BOM 처리 성공, Actions 활성화·정상/결함 CI·독립 승인·merge·운영 적용은 다음 단계이며 이번 파일만으로 완료하지 않는다.
