# 증적 관리 규칙 — 초기 준비안

## 저장소와 브랜치

- 저장소는 Private로 운영한다. main에는 검토된 증적 편입 기록을 병합한다.
- 최초 준비 브랜치: evidence/initial-import-20260907. 이후 evidence/<ticket-id>-<수집회차>를 사용한다.
- Draft PR에서 범위, 수신 파일, 검증 결과, 미수신 항목, 기존 완료 상태와 편입 상태를 제시한다.
- 최소 1인의 독립 검토 후 이권욱이 검토 Commit을 확인하여 병합한다. 이번 준비 요청은 최종 승인·병합·Runtime 실행을 포함하지 않는다.
- 2026-09-23 [사전 검증(Pre-check) 코드 예외](https://github.com/321Team/fds-project-baseline/blob/e491eb8363533828fe00aab103c369c6626edd2e/governance/REVIEW_AUTHORITY_POLICY.md)([baseline PR #93](https://github.com/321Team/fds-project-baseline/pull/93))는 이 저장소에 적용하지 않는다. Pre-check 도구의 실행 결과·로그·사본을 편입하는 PR도 독립 검토를 거친다. 소스 저장소에서 리뷰 없이 병합된 Pre-check 코드의 결과는 `REVIEW=NOT PERFORMED (Pre-check)` 상태의 소스 SHA로 연결한다. 이를 리뷰된 코드의 실행 결과로 표시하지 않는다.
- GitHub Free 제약으로 보호 규칙을 적용할 수 없는 경우 PR·정확한 Commit 확인·독립 검토·수동 병합을 기록한다. 설정이 강제 적용됐다고 미리 표시하지 않는다.

## 완료 티켓의 편입

- 기존 Done/완료일/원 승인자는 그대로 보존한다. 저장소 편입 심사는 과거 기술 작업의 재승인이 아니다.
- 원본 경로, 수집 시각, 원 작성자, 기존 Manifest, 원 승인 기록을 연결하고 수신 시각을 별도 기록한다.
- Done이라는 상태만으로 현재 원본 파일·Checksum 검증이 완료됐다고 표시하지 않는다.
- 로그 미수신은 증적 수집 대장의 Pending으로 기록한다. 종결 티켓을 자동 재개하거나 시험을 재실행하지 않는다.
- 설계 티켓은 승인된 설계·결정 기록을, 구현 티켓은 실제 시험·로그·검토 기록을 수집한다.
- D-NET/P1-NET/P1-LNX의 공통 원본은 한 번 보관하고 여러 티켓에서 참조한다.

## 원본 보존과 무결성

- 원본 21개 등 수신 파일은 바이트 그대로 복사한다. 자동 줄바꿈 정규화를 끈다.
- P1-DNS-01 R2 ZIP을 재압축하거나 내부 Index/Manifest를 바꾸지 않는다. 기록된 ZIP SHA-256과 수신 바이트, sidecar, 내부 Manifest를 차례로 대조한다.
- 새 인수 문서는 새 수집회차 경로에 작성한다. 기존 원본에 사후 Commit이나 승인 문구를 삽입하지 않는다.
- P1-ANS 승인본 05h/05j 실제 배포 여부는 별도 확인한다. 로컬에서 생성한 Manifest를 과거 서버 검증으로 대체하지 않는다.
- 사용자 콘솔 보완은 콘솔 제출 자료로 표시한다. 서버 .txt/.sha256을 받지 않았으면 서버 원본 Hash 검증을 주장하지 않는다.
- Index에는 수신 바이트의 SHA-256과 그 검증 범위를 기록한다. Hash 일치가 시험 PASS 또는 승인 진위의 단독 증거가 되지는 않는다.

## 자료 유형과 접근

- Git: 검토할 텍스트 로그·설정 사본·Index·Manifest·수신/승인 기록. 비밀키, 토큰, 암호, 실제 credential 포함 파일은 제외한다.
- 기존 ZIP/tar.gz: 승인된 별도 패키지 보관 위치 또는 Private Release Asset에서 원래 바이트를 보존하고 URI·SHA-256을 연결한다. 이 준비 단계는 Release Asset 업로드를 수행하지 않는다.
- 내부 주소와 Host 식별자를 포함하므로 필요한 팀원에게만 접근을 부여한다. 신규 팀 권한은 본 준비에서 변경하지 않는다.
- Git은 서버 mode 0640/소유자를 그대로 복구하는 도구가 아니다. 서버 권한은 수집 메타데이터로 기록한다.

## 단계 구분

수신 문서 확보 → 원본·기존 Manifest 대조 → 편입 PR 검토 → 승인된 편입 기록 병합 순서로 진행한다. 기록만 먼저 등록한 티켓은 원본 미수신 표시를 유지한다. 원본 완비가 필요한 Runtime Gate는 해당 티켓의 승인 규칙으로 별도 판단한다.

P1-LB Stage A 자료 등록은 전체 P1-LB Done 또는 Kubernetes Bootstrap 해제를 자동 의미하지 않는다. Stage B, 이하영 실제 인수와 OS/Node·Runtime Gate는 별도로 확인한다.
