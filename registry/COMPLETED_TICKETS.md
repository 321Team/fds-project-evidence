# 완료 티켓 증적 편입 대장 v1.8

> **2026-09-24 현재 상태:** [Evidence 후속 현황](EVIDENCE_FOLLOWUP_20260924.md)을 먼저 확인한다. PR7·17·21 및 DB 증적 PR2는 main 편입 완료다. FUP-09 Permanent 조건 해소와 DAD 증적 편입은 확인됐으며 DAD 잔여 인수 판단은 별도다. PR22·23·24의 독립 검토와 필요한 원본 접근 인계는 후속 현황에서 추적한다. 아래 과거 검토·병합 대기 표기는 각 작성 시점의 이력이다.

기존 기준선의 완료 티켓 12개와 2026-09-07 승인·병합 완료된 CR-P1-ANS-01-01을 포함해 13개를 관리한다. 기존 12개는 v3.1.16 Closed/Project Status Register 및 v3.1.17 WBS 대조 기록, 추가 CR은 infra-ansible PR #1의 실제 승인·병합 기록을 근거로 한다. 기준선·WBS 원본은 이 작업에서 변경하지 않는다.

2026-09-19 조회에서 baseline CLOSED는 18건이다. 추가 5건 Decision과 원본 미수신 한계는 [공백 기록](CLOSED_TICKET_EVIDENCE_GAP_20260919.md)에 정리했다. 이 링크만으로 대장 13건이 원본 완비·실제 인수 완료가 되지 않는다.

| 티켓 | 종결일 | 이번 수신 | 추가 확인 |
|---|---|---|---|
| [D-ARC-01](../tickets/D-ARC-01/README.md) | 2026-08-26 | 새 수신본 독립 승인·편입 완료 | 후보 원본 2개·PR #3 편입 완료 유지. 과거 정본의 Architecture v3.1.2 APPROVED 메타데이터 연결. 개인별 승인 회신·승인 시각은 미확인. |
| [D-NET-01](../tickets/D-NET-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | Index 10 종결 보고서와 Index 09 IP 예외 문서 연결. Index 03~06은 8/28 원본으로 보완 매핑. 8/26 최초 로그·Windows/VMware 캡처 등 미확보 부분은 별도 대기. |
| [D-WBS-01](../tickets/D-WBS-01/README.md) | 2026-08-26 | 새 수신본 독립 승인·편입 완료 | WBS 후보 참조·PR #3 편입 완료 유지. 과거 정본의 WBS v3.1.3 APPROVED 메타데이터 연결. 개인별 승인 회신·승인 시각·바이너리 실제 열람은 미확인. |
| [P1-LNX-01](../tickets/P1-LNX-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | 8/28 6대 precheck/postcheck의 SELinux·Swap·모듈·sysctl 원본 연결. 8/26 Linux Prerequisite 최초 원본으로 소급하지 않음. |
| [P1-NET-01](../tickets/P1-NET-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | 8/28 6대 연결·반환 경로·sshd Source 보존 원본 연결. 8/26 최초 원본과 당시 Reviewer/Approver·승인일시는 별도 미확인. 기존 Done 유지. |
| [P1-ANS-01](../tickets/P1-ANS-01/README.md) | 2026-08-31 | COLLECTED_REMEDIATED_PRIOR_IMPORT_REVIEWED | 기존 불일치 보완(alias·신규 Manifest)와 편입 기술 검토 완료·PR #1 병합. 구 Manifest 불일치 이력 및 Reviewer/Approver 겸임 관찰사항 유지. |
| [DEC-P1-ENTRY-01](../tickets/DEC-P1-ENTRY-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | D18 설계 승인 문서 수신. 실제 Service/접근 제어 Runtime은 후속 구현 티켓 범위. |
| [DEC-P1-TLS-01](../tickets/DEC-P1-TLS-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | D19 설계 승인 문서 수신. Private Key 제외; 인증서 배포·Push/Pull Runtime은 후속 구현 티켓 범위. |
| [DEC-P1-MON-01](../tickets/DEC-P1-MON-01/README.md) | 2026-08-31 | 새 수신본 독립 승인·편입 완료 | 원본 수신·독립 APPROVED·PR #3 편입 완료. FUP-08 수신 보완 종결; 수용된 과거 비교 Hash 부재 한계 유지. |
| [D-SEC-01](../tickets/D-SEC-01/README.md) | 2026-09-01 | 종결·승인 관련 문서 | D34 승인·조치 기록 수신. 보안 설계 정본은 baseline 고정 참조; P1-SEC Runtime 범위와 분리. |
| [MS-G0-01](../tickets/MS-G0-01/README.md) | 2026-09-01 | 종결·승인 관련 문서 | D34 G0 Full PASS 상태 전이 기록 수신. G1/G2 또는 Bootstrap 승인으로 사용하지 않음. |
| [P1-DNS-01](../tickets/P1-DNS-01/README.md) | 2026-09-03 | COLLECTED_VERIFIED | 기존 수신·검증 기록을 포함한 PR #1 편입 기술 검토·병합 완료. 독립 리뷰의 원본 ZIP 외부 대조 NOT VERIFIED 범위 유지. |
| [CR-P1-ANS-01-01](../tickets/CR-P1-ANS-01-01/README.md) | 2026-09-07 | COLLECTED_VERIFIED_PRIOR_IMPORT_REVIEWED | Refinalization·Rollback 원본 보완 및 독립 편입 기술 검토 확인, PR #1 병합 완료. 서버측 보관 메타데이터 등 독립 리뷰의 NOT VERIFIED 유지. |

기존 등록 기록은 [PR #1](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5595784292)에서 독립 기술 검토 후 병합됐다. `MERGED_REGISTERED_RECORDS`는 원본 완비·각 티켓 실제 인수 완료를 뜻하지 않는다. FUP-06/07/08 새 수신본은 PR #3 독립 승인·병합 완료이며, FUP-06/07의 과거 승인 참조·접근 미확인 한계는 최종 수용 후에도 유지한다. 기존 원본 문서 8개는 그대로 보존했다. 사후 작성한 CR 종료 기록을 서버 원본이나 과거 증적으로 간주하지 않는다.

P1-LB-01은 진행 중 티켓이며 Stage A 부분 증적을 별도로 관리한다. [후속 수신·인수 대장](FOLLOWUP_RECEIPTS.md), [관련 결정](RELATED_DECISIONS.md)을 참조한다.

[2026-09-07 ansible01 수신 검토](../receipts/ansible01/20260907T063705Z/FDS_Ansible_Evidence_Receipt_Review_v1.0.md) · [2026-09-08 FUP-02 보완 판정](../receipts/user-upload/20260908T111104Z/P1-ANS-01_FUP-02_REMEDIATION.md)

[2026-09-09 FUP-01 Refinalization 원본 수신 검토](../receipts/ansible01/20260909T003726Z/FDS_FUP01_Refinalization_Receipt_Review_v1.0.md)

[병합 후 후속 실행표](../runbooks/FUP-04-09_POST_MERGE_FOLLOWUP.md) · [신규 원본 수신 검토](../receipts/library/20260909T054024Z/RECEIPT_REVIEW.md)

## 기존 증적 공통 매핑 — 독립 검토 대기

[매핑·검증](../records/followup-mapping-20260909/EXISTING_EVIDENCE_MAP.md) · [잔여 자료 실행표](../runbooks/FUP-04-09_REMAINING_SOURCE_ACTIONS.md). Index 10의 기존 종결 문서, 8/28 보완 원본 5개 및 과거 정본의 승인 메타데이터를 연결했다. 원본 전체 완비·개별 승인 회신·실제 인수 완료를 뜻하지 않는다.
