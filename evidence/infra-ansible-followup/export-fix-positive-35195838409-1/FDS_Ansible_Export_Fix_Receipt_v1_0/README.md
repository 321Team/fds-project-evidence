# Export fix receipt v1.0

PR #22 / source `31895081e30e27481e7c17407047c9454e3b247a` / Run `35195838409` / Attempt **1** / Job and Check `105118736321` / Runner **26**.

현재 Run/Job success, 원본 artifact 내부, 단위시험 58개, Runtime·격리·로컬 정리는 검증됐다. 남은 Check 원문과 Runner 등록 부재만 수집한다.

## 실행

이 ZIP과 `.zip.sha256`를 ansible01의 `server01_ansible` 로그인 홈에 복사한다. 해당 일반 계정에서 sudo 없이 실행한다.

```bash
(
set -euo pipefail
umask 077
cd "$HOME"
sha256sum -c FDS_Ansible_Export_Fix_Receipt_v1_0.zip.sha256
TASK_RECEIPT=$(mktemp -d "$HOME/ansible-export-fix-tools.XXXXXXXX")
unzip -q FDS_Ansible_Export_Fix_Receipt_v1_0.zip -d "$TASK_RECEIPT"
cd "$TASK_RECEIPT/FDS_Ansible_Export_Fix_Receipt_v1_0"
bash run.sh admin
)
```

`STATUS=COLLECTED_BOUND_REVIEW_REQUIRED`와 `HOME_EVIDENCE=`에 표시되는 `ansible-export-fix-receipt.tar.gz` 및 같은 경로의 `.sha256`를 전달한다. 이 상태는 수집 완료이며 최종 인수나 독립 승인이 아니다.

조회 실패, 대상 변경, Runner 등록 잔존이면 `COLLECTION_INCOMPLETE`와 nonzero 종료코드가 나온다. 생성된 두 증적 파일을 그대로 전달하고 조건을 수기로 고치지 않는다. 사전조건 또는 증적 기록 자체가 실패하면 `STOP_LOCAL_PREREQUISITE_OR_EVIDENCE_WRITE_ERROR`이며 archive가 없을 수 있다.

## 범위와 판단

- 기존 `gh` 인증으로 PR, 해당 Attempt Run/Job, 해당 Check, 모든 페이지의 repository Runner 목록을 **GET**한다.
- Runner ID26 또는 `ansible-ci-a6b75591ba3d4d38b5a3c3797afd8d37` 이름이 어느 페이지에도 없어야 한다. 다른 Runner가 존재하는 것은 실패 조건이 아니다.
- 원본 artifact ZIP은 이미 검증·확보했으므로 재다운로드하지 않는다.
- 토큰 발급, Runner 등록/삭제, Workflow 재실행, prepare, 서비스/권한 변경은 없다. 인증 파일·토큰·raw stderr는 증적에 포함하지 않는다.
- API 실패나 불완전한 페이지 목록을 Runner 부재로 해석하지 않는다. 해당 세션 종료 후의 조회인지 시간도 검사한다.
- 이전 Start v1.1, 새 Start v1.0 또는 Runner serve를 다시 실행할 필요가 없다.

원본은 Attempt2 Receipt v1.0의 읽기 전용 수집기이며, 대상 상수·PR binding·세션 종료 시각을 갱신하고 불필요한 artifact 다운로드와 Runner 파일 탐색기를 제거했다. 단위시험은 모의 API 응답으로 수행했다. 실제 ansible01 조회 결과는 아직 없다.
