# Export 수정 코드 정상 Actions 시작 키트 v1.0

이 키트의 버전은 **Export Fix Start v1.0**이며 포함된 Runner는 **v1.3**이다.
과거 `FDS_Ansible_Isolated_Actions_Start_v1_1`의 PR20 시작 명령 대신 아래 새 파일명과 절차를 사용한다.
이 키트는 PR22의 한 정상 시험에만 사용한다. 실행 시 상태가 바뀌면 검사가 중단한다.

## 고정 실행 대상

| 항목 | 값 |
|---|---|
| 저장소 / 시험 PR | 321Team/infra-ansible / #22 TEST ONLY, DO NOT MERGE |
| 기준 PR17 HEAD | 6b2ac7a80be1acd187ac73cbd1cf957f708edf85 |
| 실제 checkout source | 31895081e30e27481e7c17407047c9454e3b247a |
| Branch | test/issue-5-export-fix-positive-20260917 |
| Run / Attempt | 35195838409 / 1 |
| regression Job / Check | 105118736321 |
| Runner bundle SHA256 | e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6 |
| image ID | sha256:3f96787b2a8db29294002677a3e733689439952ad9e95db721acf8e16ff601f1 |

`EXPECTED.json`은 조회용 고정값이다. 값이 바뀌면 수기로 편집하거나 검사 조건을 삭제하지 않는다.
Run/Job이 이미 종료됐다면 토큰을 다시 발급하지 않고 해당 실행 증적을 확인한다.

## 1. cicd-runner01 — 토큰 없는 현재 상태 확인

ZIP과 sidecar를 `/home/server01_cicd-runner/`에 놓고 **server01_cicd-runner 일반 계정**에서 실행한다.
root/sudo 로그인으로 시작하지 않는다. 내부에서 읽기 점검을 위한 sudo/runuser만 사용하며
Podman image inspect는 전용 비sudo 계정 ansible-verify로 실행한다. 컨테이너 시작·등록·삭제·prepare는 하지 않는다.

```bash
(
set -euo pipefail
umask 077
cd "$HOME"
sha256sum -c FDS_Ansible_Export_Fix_Start_v1_0.zip.sha256
TASK_EXPORT_CHECK=$(mktemp -d "$HOME/ansible-export-fix-check.XXXXXXXX")
unzip -q FDS_Ansible_Export_Fix_Start_v1_0.zip -d "$TASK_EXPORT_CHECK"
cd "$TASK_EXPORT_CHECK/FDS_Ansible_Export_Fix_Start_v1_0"
bash 00-runner-readiness.sh
)
```

`"status": "PASS_PREPARED_IMAGE_READINESS"`와 exit0일 때만 다음 단계로 진행한다.
`HOME_READINESS=` 압축파일과 sidecar를 보존한다. 이 결과는 PREPARED와 현재 image metadata 확인이며
전체 계정/자원/SELinux/IPC/18개 격리 검사는 serve의 기존 launcher에서 다시 수행한다.
실패 시 같은 prepare를 반복하거나 PREPARED/홈 권한을 바꾸지 말고 이 증적부터 확인한다.

## 2. ansible01 — 새 실행 대상 검증 후 단기 토큰 발급

ZIP과 sidecar를 `/home/server01_ansible/`에 놓고 **server01_ansible 일반 계정**에서 실행한다.
기존 gh 인증을 사용한다. 아래 검사는 GET만 하며, 통과한 뒤 기존 Admin helper가 등록/제거 단기 token packet을 발급한다.

```bash
(
set -euo pipefail
umask 077
cd "$HOME"
sha256sum -c FDS_Ansible_Export_Fix_Start_v1_0.zip.sha256
TASK_EXPORT_ADMIN=$(mktemp -d "$HOME/ansible-export-fix-admin-tools.XXXXXXXX")
unzip -q FDS_Ansible_Export_Fix_Start_v1_0.zip -d "$TASK_EXPORT_ADMIN"
cd "$TASK_EXPORT_ADMIN/FDS_Ansible_Export_Fix_Start_v1_0"
bash 01-admin-token.sh
)
```

순서대로 `STATUS=PASS_EXPORT_FIX_QUEUED_SOURCE`, `STATUS=PASS_TOKEN_PACKET`, `TOKEN_PACKET=...`가 나와야 한다.
PR/HEAD/Run/Attempt/Job/labels/Runner 미배정, queued1개·in_progress0개를 확인한다.
목록의 total_count와 반환 항목 수가 기대와 다르면 불완전 조회/경쟁 작업으로 중단한다.
API 조회와 Runner 배정 사이의 원자성은 보장하지 않으므로 통과 후 바로 다음 단계를 진행하고 최종 Job provenance를 대조한다.

`TOKEN_PACKET=`에 표시된 **파일 하나만** 기존 비공개 전달 경로로
`cicd-runner01:/home/server01_cicd-runner/`에 원래 파일명 그대로 복사한다.
토큰 내용·PAT·gh 인증 파일은 채팅/GitHub/증적에 올리지 않는다.
`HOME_PREFLIGHT=` 압축파일과 sidecar는 토큰을 포함하지 않는 사전점검 증적이다.

## 3. cicd-runner01 — ephemeral Runner 한 세션

앞선 readiness가 PASS한 동일 서버의 **server01_cicd-runner 일반 계정**에서 실행한다.

```bash
(
set -euo pipefail
umask 077
cd "$HOME"
sha256sum -c FDS_Ansible_Export_Fix_Start_v1_0.zip.sha256
TASK_EXPORT_SERVE=$(mktemp -d "$HOME/ansible-export-fix-serve.XXXXXXXX")
unzip -q FDS_Ansible_Export_Fix_Start_v1_0.zip -d "$TASK_EXPORT_SERVE"
cd "$TASK_EXPORT_SERVE/FDS_Ansible_Export_Fix_Start_v1_0"
bash 02-runner-serve.sh
)
```

질문에는 `ansible-runner-token-....json` **파일명만** 입력한다. 검증된 입력 보호·현재 PREPARED/이미지 검사·
rootless IPC/격리 검사와 한 Job 이후 정리를 기존 v1.3 launcher가 수행한다.
serve wrapper와 payload는 기존 검증본과 바이트 동일하다. 내부 payload README에는 작성 당시 실패 이력이 있으므로
현재 실행 대상과 순서는 이 최상위 README/EXPECTED.json을 따른다.

## 반환할 증적과 완료 기준

- `HOME_READINESS=`의 `ansible-export-fix-readiness.tar.gz`와 `.sha256`.
- `HOME_PREFLIGHT=`의 `ansible-export-fix-preflight.tar.gz`와 `.sha256`.
- `HOME_EVIDENCE=`의 `ansible-actions-runner-evidence.tar.gz`와 `.sha256`.

`SESSION_ENDED_REQUIRES_CI_REVIEW`는 세션 종료 표시이며 CI PASS가 아니다.
정상 기대: exact source, syntax32/32 rc0, unit58 OK, 양 엔진 guard/contract 완전 집합 및 DNS rc0,
CI_RESULT PASS/실행기0·Job/Check success·artifact 업로드 및 원본 전체 manifest 일치.
unit 안의 의도된 export 실패 로그는 unittest 결과와 구분한다. 환경 오류·취소·timeout·skipped는 PASS가 아니다.

Runner/container/proxy/workspace 정리와 **이번 새 Runner ID/name**의 종료 후 GitHub 원격 부재를 확인해야 인수가 끝난다.
과거 ID5/ID6 부재로 대체하지 않는다. 관리 Receipt와 원본 artifact는 새 세션 식별 후 읽기 수집한다.
정리 실패 시 증적을 보존하고 전체 Runner 삭제나 podman prune으로 처리하지 않는다.
독립 승인·병합·Issue5 종결·운영 Apply·엔진 전환·일반 Workflow 활성화는 이 키트에 포함하지 않는다.

## 제작 검증

`validation/`에 Workflow 비교/조건 모형과 시작 보호 시험 원문을 수록한다.
이는 STATIC/LOCAL/MOCK 검증이며 실제 서버 readiness나 이번 Actions 성공 성적이 아니다.
수신 원본의 변조를 확인하는 SHA256은 독립 승인이나 현재 호스트 상태를 증명하지 않는다.
