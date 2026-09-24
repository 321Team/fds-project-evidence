# 증적 관리 규칙 — 초기 준비안

## 저장소와 브랜치

- 저장소는 Private로 운영한다. main에는 검토된 증적 편입 기록을 병합한다.
- 최초 준비 브랜치: evidence/initial-import-20260907. 이후 evidence/<ticket-id>-<수집회차>를 사용한다.
- Draft PR에서 범위, 수신 파일, 검증 결과, 미수신 항목, 기존 완료 상태와 편입 상태를 제시한다.
- 최소 1인의 독립 검토 후 이권욱이 검토 Commit을 확인하여 병합한다. 이번 준비 요청은 최종 승인·병합·Runtime 실행을 포함하지 않는다.
- 독립 검토는 [중앙 리뷰 권한 정책 §3.1](https://github.com/321Team/fds-project-baseline/blob/f3dc4cfa1584cd4a9c4435bc7324bd12d1dd297d/governance/REVIEW_AUTHORITY_POLICY.md#31-증적-저장소-예외)에 따라 다음을 확인한다: 원본 출처, 수신 바이트·해시, 실제 실행 여부, AC와 판정의 대응, 누락·오표기·민감정보, 정정 이유. 작성자·실행자의 자체 검토나 AI 보조 점검만으로 독립 검토 완료로 표시하지 않는다.
- 2026-09-23 [사전 검증(Pre-check) 코드 예외](https://github.com/321Team/fds-project-baseline/blob/f3dc4cfa1584cd4a9c4435bc7324bd12d1dd297d/governance/REVIEW_AUTHORITY_POLICY.md)([baseline PR #93](https://github.com/321Team/fds-project-baseline/pull/93))는 이 저장소에 적용하지 않는다. Pre-check 도구의 실행 결과·로그·사본을 편입하는 PR도 독립 검토를 거친다. 소스 저장소에서 리뷰 없이 병합된 Pre-check 코드의 결과는 `REVIEW=NOT PERFORMED (Pre-check)` 상태의 소스 SHA로 연결한다. 이를 리뷰된 코드의 실행 결과로 표시하지 않는다.
- GitHub Free 제약으로 보호 규칙을 적용할 수 없는 경우 PR·정확한 Commit 확인·독립 검토·수동 병합을 기록한다. 설정이 강제 적용됐다고 미리 표시하지 않는다.

## 완료 티켓의 편입

- 기존 Done/완료일/원 승인자는 그대로 보존한다. 저장소 편입 심사는 과거 기술 작업의 재승인이 아니다.
- 원본 경로, 수집 시각, 원 작성자, 기존 Manifest, 원 승인 기록을 연결하고 수신 시각을 별도 기록한다.
- Done이라는 상태만으로 현재 원본 파일·Checksum 검증이 완료됐다고 표시하지 않는다.
- 로그 미수신은 증적 수집 대장의 Pending으로 기록한다. 종결 티켓을 자동 재개하거나 시험을 재실행하지 않는다.
- 설계 티켓은 승인된 설계·결정 기록을, 구현 티켓은 실제 시험·로그·검토 기록을 수집한다.
- D-NET/P1-NET/P1-LNX의 공통 원본은 한 번 보관하고 여러 티켓에서 참조한다.

## 저장 경로

- 이 저장소에 편입하는 증적은 `evidence/<Record ID>/` 아래에 둔다. Record ID는 책임 티켓·Decision·CR ID다. 수집회차는 그 아래 하위 경로(예: `received-<수신시각>/`)로 구분한다. 2026-09-23 사용자 결정으로 티켓의 Evidence Path를 `321Team/fds-project-evidence:evidence/<Record ID>/`로 통일했다([baseline Phase 2 기록 §3](https://github.com/321Team/fds-project-baseline/blob/f3dc4cfa1584cd4a9c4435bc7324bd12d1dd297d/audit/phase2-repo-bootstrap-20260923/README.md)).
- `receipts/`(수신 검증), `records/`(수신 사본·병합 후 기록), `registry/`(대장), `handoffs/`, `runbooks/`는 기존 역할을 유지한다. 원본 증적 자체를 이 경로에 새로 두지 않는다.
- 수신 원본이나 과거 문서에 적힌 서버 수집 경로·논리 경로(예: 서버의 `docs/evidence/<ID>/`)는 출처 정보이므로 고치지 않는다.
- 2026-09-24 `docs/evidence/P1-DB-01/evidence-20260907.md`를 `evidence/P1-DB-01/evidence-20260907.md`로 옮겼다. 내용은 바꾸지 않았다(SHA-256 `f8f3151e4dabfb7d2d4e7a0e74124eaa6d140001d8d00ec49dfa22a547e34b65` 동일). 이전 경로의 고정 Commit 링크(예: `90093f8`)는 계속 유효하다.
- 예외 목록의 정본은 [`governance/EVIDENCE_LAYOUT_EXCEPTIONS.json`](EVIDENCE_LAYOUT_EXCEPTIONS.json)이다. 예외를 추가·변경·삭제할 때는 이 파일과 아래 목록을 같은 PR에서 함께 고친다. 약칭(`-7/` 등)을 쓰지 않고 전체 경로를 적는다.
- 현재 예외(2026-09-24): `evidence/infra-ansible-followup/`, `evidence/infra-ansible-issue-6/`, `evidence/infra-ansible-issue-7/`, `evidence/infra-ansible-issue-8/`. 경로 통일 전 `infra-ansible` 저장소의 Issue 단위로 편입된 기록이다. 내용이 P1-ANS-01·P1-CICD-01 등 여러 Record에 걸쳐 있어 단일 Record ID로 대응되지 않는다. 또한 `evidence/infra-ansible-issue-8/received-20260914-4a9790642852/SOURCE_SELECTION.json`은 폴더 Manifest(`REVIEW_SHA256SUMS`)로 고정된 수신 기록인데 파일 81개의 git 경로를 담고 있어, 옮기면 기록과 실제 위치가 어긋난다. 그래서 현재 경로를 유지한다. 이 폴더들을 가리키는 기존 링크는 확인한 범위(2026-09-24, 정책 적용 대상 저장소 main)에서 모두 Commit 고정 링크다. 예외 경로에는 새 증적을 추가하지 않고 책임 Record ID 경로를 사용한다.
- 점검: 편입 PR은 `python3 tools/check-evidence-layout.py --base origin/main` 결과를 PR에 적는다. 이 도구는 Record ID 형식, 예외 목록과 정책의 일치, 예외 경로의 새 파일, 대장·수집회차 Manifest 해시, 모든 추적 파일의 대장 연결을 확인한다. 결과는 경로·목록·현재 바이트 점검이며 원본 진위·시험 PASS·인수 승인을 뜻하지 않는다.

## 원본 보존과 무결성

- 원본 21개 등 수신 파일은 바이트 그대로 복사한다. 자동 줄바꿈 정규화를 끈다.
- P1-DNS-01 R2 ZIP을 재압축하거나 내부 Index/Manifest를 바꾸지 않는다. 기록된 ZIP SHA-256과 수신 바이트, sidecar, 내부 Manifest를 차례로 대조한다.
- 새 인수 문서는 새 수집회차 경로에 작성한다. 기존 원본에 사후 Commit이나 승인 문구를 삽입하지 않는다.
- P1-ANS 승인본 05h/05j 실제 배포 여부는 별도 확인한다. 로컬에서 생성한 Manifest를 과거 서버 검증으로 대체하지 않는다.
- 사용자 콘솔 보완은 콘솔 제출 자료로 표시한다. 서버 .txt/.sha256을 받지 않았으면 서버 원본 Hash 검증을 주장하지 않는다.
- Index에는 수신 바이트의 SHA-256과 그 검증 범위를 기록한다. Hash 일치가 시험 PASS 또는 승인 진위의 단독 증거가 되지는 않는다.
- 루트 `REGISTRY_SHA256SUMS`의 등록 범위(2026-09-24 결정):
  - 관리 문서(루트 파일, `.github/`, `governance/`, `registry/`, `records/`, `receipts/`, `handoffs/`, `runbooks/`, `tools/`, `tests/`, `tickets/`)는 모두 등록하고, 변경하는 PR에서 해시를 갱신한다.
  - `evidence/` 수집회차 폴더에 자체 SHA256SUMS·Manifest가 있으면 그 파일이 폴더 내 파일의 무결성 기준이다. 대장에는 그 Manifest 파일과, Manifest가 덮지 않는 파일(예: 편입 README)만 등록한다. 자체 Manifest가 없는 수집회차는 파일을 모두 등록한다.
  - 이미 대장에 개별 등록된 `evidence/` 항목은 이력으로 유지한다.
  - 전체 확인은 대장 검사와 각 수집회차 Manifest 검사를 함께 수행한다. 두 결과 모두 현재 파일 무결성 확인일 뿐 원본 Manifest 검증이나 인수 승인을 대체하지 않는다.
- 중앙 정책 §3.2 4-1의 순수 검증기를 운영 서버에서 리뷰 없이 실행한 결과는 대상 서버, 실행 SHA, 명령, 계정, KST 시각, 순수 검증기 판단 근거, 결과 경로와 함께 편입한다. 빠진 항목은 미수신으로 표시한다. 이 결과를 운영 적용·AC 인수·리뷰된 코드의 실행 결과로 표시하지 않는다.

## 자료 유형과 접근

- Git: 검토할 텍스트 로그·설정 사본·Index·Manifest·수신/승인 기록. 비밀키, 토큰, 암호, 실제 credential 포함 파일은 제외한다.
- 기존 ZIP/tar.gz: 승인된 별도 패키지 보관 위치 또는 Private Release Asset에서 원래 바이트를 보존하고 URI·SHA-256을 연결한다. 이 준비 단계는 Release Asset 업로드를 수행하지 않는다.
- 압축 파일의 무결성 조건(2026-09-24): 보관 위치와 관계없이 원래 바이트를 재압축하지 않고, SHA-256을 기록한다. Git에 둔 압축 파일은 같은 이름의 `.sha256` sidecar가 있어야 하고 그 값이 파일 바이트와 일치해야 한다(`tools/check-evidence-layout.py`가 확인). Git에 둘 수 있는 압축 파일은 1MB 이하이며, 내부 파일 목록(이름·크기·SHA-256)을 [`registry/ARCHIVE_CONTENTS.json`](../registry/ARCHIVE_CONTENTS.json)에 함께 편입한다. 점검 도구는 이 목록을 압축 파일 바이트에서 다시 계산해 대조한다. 목록 초안은 `python3 tools/check-evidence-layout.py --archive-index-draft`로 만든다. 1MB를 넘으면 별도 보관소에 두고 URI·SHA-256만 연결한다. 목록은 리뷰에서 내용물의 존재를 보이게 하는 장치이며, 내부 파일 내용 검토는 리뷰어가 압축을 풀어 수행한다.
- 내부 주소와 Host 식별자를 포함하므로 필요한 팀원에게만 접근을 부여한다. 신규 팀 권한은 본 준비에서 변경하지 않는다.
- Git은 서버 mode 0640/소유자를 그대로 복구하는 도구가 아니다. 서버 권한은 수집 메타데이터로 기록한다.

## 단계 구분

수신 문서 확보 → 원본·기존 Manifest 대조 → 편입 PR 검토 → 승인된 편입 기록 병합 순서로 진행한다. 기록만 먼저 등록한 티켓은 원본 미수신 표시를 유지한다. 원본 완비가 필요한 Runtime Gate는 해당 티켓의 승인 규칙으로 별도 판단한다.

Lead의 자체 Runtime 판정과 이 저장소의 편입 심사는 별개다. 증적 PR의 독립 검토·병합만으로 업무 티켓을 Done 처리하지 않는다. 종결은 해당 Lead가 필수 AC와 남은 작업을 근거로 판단한다(중앙 정책 §3.1).

P1-LB Stage A 자료 등록은 전체 P1-LB Done 또는 Kubernetes Bootstrap 해제를 자동 의미하지 않는다. Stage B, 이하영 실제 인수와 OS/Node·Runtime Gate는 별도로 확인한다.
