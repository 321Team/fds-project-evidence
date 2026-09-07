# FDS Project Evidence

FDS 프로젝트의 티켓별 실행 증적, 검증 결과, 승인·인수 기록과 SHA-256 무결성 정보를 관리하는 비공개 저장소입니다. 기준선·WBS 정본은 fds-project-baseline에서 별도로 관리합니다.

이 브랜치는 최초 증적 편입 검토 후보입니다. 기존 완료 상태와 증적의 수집·검토 상태를 별도로 기록합니다.

| 항목 | 상태 |
|---|---|
| 대상 저장소 | `321Team/fds-project-evidence` — Private / 연결 확인 |
| 준비 브랜치 | `evidence/initial-import-20260907` — 증적 편입 검토 후보 |
| 검토 Commit / PR | [PR #1](https://github.com/321Team/fds-project-evidence/pull/1) 본문에 HEAD 고정 · Draft / 독립 검토 대기 |
| 기존 완료 티켓 | 13개 — 기존 12개 + 승인·병합 완료 CR 1개 |
| 과거 종결·승인 문서 | 8개 수신 사본 |
| P1-LB-01 | Stage A 원본 21개 및 사후 검토 자료; 전체 티켓 In Progress |

## 읽는 순서

1. [완료 티켓 편입 대장](registry/COMPLETED_TICKETS.md)
2. [수신 문서 목록·SHA-256](registry/RECEIVED_RECORDS.md)
3. [P1-LB-01 Stage A 검토](evidence/P1-LB-01/stage-a/received-20260907/19_stage_a_handoff_review.md)
4. [증적 관리 규칙](governance/EVIDENCE_POLICY.md)
5. [상태·출처 대조](registry/SOURCE_AUTHORITY.md)

## 관리 경계

`fds-project-baseline`은 기준선·WBS·티켓 정본을, 이 저장소는 증적과 그 인수 이력을 관리한다. 기존 문서의 수신 사본은 당시 종결 근거이며 새로운 기준선 정본을 만들지 않는다. 설계 승인·Gate 승인과 실제 Runtime 시험을 구분한다.

`sha256sum --check REGISTRY_SHA256SUMS`로 준비본 파일의 현재 무결성을 확인할 수 있다. 이 결과는 과거 원본 Manifest 검증 또는 담당자의 인수 승인을 대체하지 않는다.

## 2026-09-07 Ansible 병합 후속

- [CR 승인·병합 인계 기록](records/post-merge-20260907/CR-P1-ANS-01-01_CLOSURE.md)
- [원본 수신·인수 대장](registry/FOLLOWUP_RECEIPTS.md)
- [ansible01 수집 실행 절차](runbooks/ANSIBLE_SOURCE_RECEIPT.md)
- [Stage A 실제 인수 체크리스트](handoffs/P1-LB-01_STAGE_A_RECEIVER_CHECKLIST.md)

수집 스크립트는 로컬 모의 파일 검증을 완료했으며 실제 서버 원본 수신은 대기다. 본 증적 PR의 최종 승인·병합과 Stage A 실제 인수는 별도 Gate다.
