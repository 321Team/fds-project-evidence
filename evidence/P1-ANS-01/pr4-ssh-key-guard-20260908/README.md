# PR #4 증적 열람 시작점

이 폴더는 [infra-ansible PR #4](https://github.com/321Team/infra-ansible/pull/4)의 수신 증적을 GitHub에서 직접 읽기 위한 등록본이다. 코드 검토 HEAD는 `5a2c3786f6af9f107200654aa12c92c3b09700f0`로 고정한다. 현재 PR #4는 **APPROVED / 사람 확인 CONFIRMED / MERGED·CLOSED**이다. [승인·병합 종결 기록](../../../records/post-merge-20260908/INFRA_ANSIBLE_PR4_CLOSURE.md)을 따른다. 리뷰어가 확인한 증적은 `d948fbb6bfc5e48bad19135034a1db35347e09e9`로 고정하고, 이 후속 갱신은 관리 기록만 변경한다. 증적 편입 PR 전체의 승인·병합은 별도 대기다.

## 검토 순서

1. [현재 자료 인덱스](EVIDENCE_INDEX.json), [소스 28개 고정 참조](SOURCE_REVIEW_INDEX.json), [원본→Git 매핑](SOURCE_FILE_MAP.json)을 읽는다.
2. [실행 보고서](extracted/ssh-main/results/VERIFICATION_REPORT.json)와 [실행 입력 Manifest](extracted/ssh-main/results/SOURCE_MANIFEST.json)을 확인한다.
3. [2.16.19 SSH 원문](extracted/ssh-main/results/2.16.19_readonly_ssh.txt), [2.21.3 SSH 원문](extracted/ssh-main/results/2.21.3_readonly_ssh.txt), [2.16.19 check 원문](extracted/ssh-main/results/2.16.19_hardening_check.txt), [2.21.3 check 원문](extracted/ssh-main/results/2.21.3_hardening_check.txt)을 대조한다. check의 두 번째 검사는 skipped이며 readonly 단계에서는 실행된다.
4. control01·02의 [after 상태](extracted/control01-after/STATE_REPORT.json), [after 상태](extracted/control02-after/STATE_REPORT.json)와 각각 포함된 baseline-before를 비교한다. [신규 SSH 콘솔 제출본](review/REMOTE_SSH_CONSOLE_SUBMISSION.md)은 서버 sidecar를 받은 자료와 출처가 다르다.
5. [종합 기술 검토 v1.17](review/FDS_SSH_Key_Guard_Fix_Review_v1.17.md), [재검토 v2 대응](review/FDS_PR4_Submitted_Review_Assessment_v1.1.md), [출력 재생 결과](review/review-parser-replay-20260908.json)를 확인한다.
6. clone한 이 폴더에서 `sha256sum --check SHA256SUMS`로 등록 텍스트 바이트를 대조한다. 저장소 전체는 루트 REGISTRY_SHA256SUMS를 사용한다.

## 원본과 과거 기록

원본 ZIP SHA-256: `7067291df4b5a26741ba45797fded205099fec9fce5d11c016982f3a5d93b308`. [압축 원본 보관 참조](SOURCE_PACKAGES.json)에서 TAR·sidecar의 원래 해시를 확인할 수 있다. 저장소 정책에 따라 ZIP/tar.gz는 Git에 올리지 않는다. 압축 원본 자체를 독립 대조하려면 기존 배포 묶음이 별도로 필요하다. 내부 recovery-original의 TAR도 별도 원본에 남아 있으며, 그 sidecar와 STATE_REPORT는 보존한다. 존재하지 않는 TAR 경로를 현재 Git 다운로드 링크로 표시하지 않는다.

서버 원본과 v1.17 등 과거 검토서의 ‘REMOTE_PENDING’, ‘NOT VERIFIED’, ‘Git 미등록’ 문구는 당시 상태·판단 주체를 보존한 것이다. 이 폴더는 텍스트 열람 경로를 제공하며 리뷰어의 확인 여부를 자동 변경하지 않는다. 자료 접근 문제와 독립 증적 확인은 별도 상태다.

## 배포 참조와 한계

[wrapper](distribution-reference/run-server-verify.sh)·[고정 requirements](distribution-reference/requirements-2213.txt)·[배포 Manifest](distribution-reference/SOURCE_MANIFEST.json)는 기존 배포본과 같은 바이트의 판독용 참조다. 이 폴더는 완전한 실행 키트가 아니며 wrapper를 여기서 바로 실행하도록 안내하지 않는다. CI·내부 API·구조화 출력 개선은 미구현 후속 항목이다. 새 서버 실행, 운영 업그레이드, 전체 apply/rollback, PR #3, Bootstrap, 병합 승인은 포함하지 않는다.
