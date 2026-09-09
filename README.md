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

ansible01에서 CR 17개·P1-ANS 38개·DNS ZIP/Sidecar 2개가 수신됐다. DNS 원본 수신 검증은 완료됐다. P1-ANS Manifest 2개 불일치는 2026-09-08 사용자 제출 종결 증적과 대조해 원인·파일명 Alias·신규 수신회차 Manifest를 등록했으며 독립 검토 대기다. CR은 2026-09-09 Refinalization 원본까지 수령하여 기존 17개·Rollback 5개·Refinalization 1개, 총 23개의 수신·보완 검증을 완료했다. 독립 편입 검토는 대기다. 본 증적 PR의 최종 승인·병합과 Stage A 실제 인수는 별도 Gate다.

- [2026-09-07 Ansible 원본 수신 검토](receipts/ansible01/20260907T063705Z/FDS_Ansible_Evidence_Receipt_Review_v1.0.md)

## Stage A 승인 범위 정정

[Stage A 승인 범위 정정](registry/STAGE_A_APPROVAL_SCOPE_CORRECTION.md): D36에 반영된 Technical/Evidence PASS와 CR 리뷰의 Listener Ready PASS를 유지한다. 증적 제출은 완료됐고 별도 Stage A PASS 재승인은 요구하지 않는다. FUP-09는 이하영의 증적 인수 기록 확인으로 한정하며 OS/Node Bootstrap Gate는 별도다.

## 2026-09-08 PR #4 재검토 자료

[PR #4 증적 열람](./evidence/P1-ANS-01/pr4-ssh-key-guard-20260908/README.md) · [재환님 인계](handoffs/INFRA_ANSIBLE_PR4_REVIEW.md). PR #4는 독립 승인·사람 확인·main 병합을 완료했다. [종결 기록](records/post-merge-20260908/INFRA_ANSIBLE_PR4_CLOSURE.md)을 참조한다. 본 증적 편입 PR 전체의 승인·병합은 별도 대기다.

## 2026-09-08 FUP-01/02 우선 보완

- [FUP-02 사용자 제출 수신·판정](receipts/user-upload/20260908T111104Z/README.md): 기존 Git 수신본 38/38 동일, 05h/05j 승인본 반영 후 구 Manifest 갱신 누락 원인 확인, 파일명 Alias와 신규 수신회차 Manifest 등록.
- [FUP-01/02 읽기 전용 보완 절차](runbooks/FUP-01-02_REMEDIATION.md): FUP-01 변경 노드 5대의 보존 파일 경로를 확정하고 stat/slurp 전용 수집기를 제공. 실제 원본 수령 전에는 FUP-01을 완료 처리하지 않음.


## 2026-09-08 FUP-01 Rollback 원본 수신

[보완 수신 검토](receipts/ansible01/20260908T115139Z/FDS_FUP01_Rollback_Receipt_Review_v1.0.md): 외부 sidecar 일치·내부 6/6·변경 노드 5/5 수신. JSON은 9월 4일 변경 전 상태이며 현재 DNS나 rollback 재시험 결과가 아니다. 보관 권한은 수집 보고 기반으로 표시한다. FUP-01 전체는 Refinalization 원본 미수신으로 대기하며 기존 Done·FUP-02·독립 검토·병합 상태는 유지한다.


## 2026-09-09 FUP-01 원본 보완 완료

[Refinalization 수신 검토](receipts/ansible01/20260909T003726Z/FDS_FUP01_Refinalization_Receipt_Review_v1.0.md) · [원본](evidence/CR-P1-ANS-01-01/received-20260909T003726Z/evidence_refinalization.20260904T183221+0900.txt). 승인 당시 Hash 일치, 내부 Manifest 2/2·기존 참조 4/4·Commit/Tree 대조 완료. FUP-01은 원본 보완 완료·독립 편입 검토 대기다. 위 날짜별 미수신 기록은 당시 이력으로 보존한다.
