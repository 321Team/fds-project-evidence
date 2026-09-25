# FDS Project Evidence

> **증적 현황 안내(2026-09-25 갱신):** [Evidence 후속 현황](registry/EVIDENCE_FOLLOWUP_20260924.md)의 맨 위 절에 main `4d2db33` 기준 병합·잔여 상태를 정리했다. 그 이후 변경은 PR 이력과 해당 문서를 따른다. 아래 과거 검토·병합 대기 표기는 각 작성 시점의 이력이다.

FDS 프로젝트의 티켓별 실행 증적, 검증 결과, 승인·인수 기록과 SHA-256 무결성 정보를 관리하는 비공개 저장소입니다. 기준선·WBS 정본은 fds-project-baseline에서 별도로 관리합니다.

증적 PR #1·#3의 병합을 완료했습니다. FUP-08은 원본 수신·편입 완료이며 FUP-06/07은 후보 편입·확인 한계를 최종 수용했습니다. FUP-09는 기존 이하영 회신에 따른 조건부 인수로 정정합니다. [현재 후속 이슈](https://github.com/321Team/fds-project-evidence/issues/4)에서 원본·참조와 잔여 조건을 추적합니다.

| 항목 | 상태 |
|---|---|
| 대상 저장소 | `321Team/fds-project-evidence` — Private / 연결 확인 |
| 후속 브랜치 | `evidence/stage-a-receipt-correction-20260909` — 기존 인수 회신 연결·관리 기록 정정 후보 |
| 기존 편입 PR | [PR #1](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5595784292) 병합 완료 · `0f16942b2c0525a90fe75a1c17fd19c295352658` |
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

`sha256sum --check REGISTRY_SHA256SUMS`로 관리 문서와 각 수집회차 Manifest의 현재 무결성을 확인할 수 있다. 자체 Manifest가 있는 `evidence/` 수집회차의 개별 파일은 그 폴더에서 해당 Manifest로 확인한다(등록 범위: [증적 관리 규칙](governance/EVIDENCE_POLICY.md) '원본 보존과 무결성'). 이 결과는 과거 원본 Manifest 검증 또는 담당자의 인수 승인을 대체하지 않는다.

## 2026-09-09 병합 후 정정

[PR #3 병합·FUP-09 정정](./records/post-merge-20260909/PR3_CLOSURE_AND_FUP09_CORRECTION.md) · [조건부 인수 회신](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5582767564). Stage A 자료 28개는 회신 기재 Commit과 병합본 사이에서 동일합니다.

## 2026-09-09 후속 착수 — 당시 이력

- [담당별 실행표](runbooks/FUP-04-09_POST_MERGE_FOLLOWUP.md)
- [신규 원본 수신 검토](receipts/library/20260909T054024Z/RECEIPT_REVIEW.md)
- [병합 결과 기록](records/post-merge-20260909/EVIDENCE_PR1_CLOSURE.md)
- [Stage A 인수 참조 회신 양식](handoffs/FUP-09_RECEIPT_REFERENCE_FORM.md)

당시 대기였던 FUP-06/07/08 편입은 PR #3 병합으로 완료됐습니다. FUP-04/05 원본·승인 참조는 대기이며, FUP-09는 조건부 인수와 미포함 2개 항목의 참조 확인 대기로 정정됐습니다. 아래 날짜별 서술은 당시 수신 이력이며 현재 상태는 수신 대장 첫 표를 따릅니다.

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
