# 완료 티켓 증적 편입 대장 v1.6

기존 기준선의 완료 티켓 12개와 2026-09-07 승인·병합 완료된 CR-P1-ANS-01-01을 포함해 13개를 관리한다. 기존 12개는 v3.1.16 Closed/Project Status Register 및 v3.1.17 WBS 대조 기록, 추가 CR은 infra-ansible PR #1의 실제 승인·병합 기록을 근거로 한다. 기준선·WBS 원본은 이 작업에서 변경하지 않는다.

| 티켓 | 종결일 | 이번 수신 | 추가 확인 |
|---|---|---|---|
| [D-ARC-01](../tickets/D-ARC-01/README.md) | 2026-08-26 | 새 원본 수신 / 독립 편입 검토 대기 | Freeze 메타데이터가 종결 설명과 일치하는 논리·물리 원본 2개 수신·Hash 기록. 당시 승인 참조 최종 연결 및 새 편입 독립 검토 대기. |
| [D-NET-01](../tickets/D-NET-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | Closure Report 수신. docs/evidence/D-NET-01/의 01~10 원본 로그·캡처 및 기존 Manifest 미수신. |
| [D-WBS-01](../tickets/D-WBS-01/README.md) | 2026-08-26 | 새 원본 수신 / 독립 편입 검토 대기 | 종결 설명 지정 WBS v3.1.3 원본 수신·Hash·CRC 확인, 별도 보관 참조 등록. 동결/갱신 승인 참조 연결 및 원본 접근·독립 검토 대기. |
| [P1-LNX-01](../tickets/P1-LNX-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | D-NET 공통 Closure Report만 수신. 04_K8s_Linux_Prerequisites 등 실제 원본 미수신. |
| [P1-NET-01](../tickets/P1-NET-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | D-NET 공통 증적을 참조. 원본 로그·캡처 미수신; 종결 문서의 Reviewer/Approver는 미입력이므로 임의 지정하지 않음. |
| [P1-ANS-01](../tickets/P1-ANS-01/README.md) | 2026-08-31 | COLLECTED_REMEDIATED_PRIOR_IMPORT_REVIEWED | 기존 불일치 보완(alias·신규 Manifest)와 편입 기술 검토 완료·PR #1 병합. 구 Manifest 불일치 이력 및 Reviewer/Approver 겸임 관찰사항 유지. |
| [DEC-P1-ENTRY-01](../tickets/DEC-P1-ENTRY-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | D18 설계 승인 문서 수신. 실제 Service/접근 제어 Runtime은 후속 구현 티켓 범위. |
| [DEC-P1-TLS-01](../tickets/DEC-P1-TLS-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | D19 설계 승인 문서 수신. Private Key 제외; 인증서 배포·Push/Pull Runtime은 후속 구현 티켓 범위. |
| [DEC-P1-MON-01](../tickets/DEC-P1-MON-01/README.md) | 2026-08-31 | 새 원본 수신 / 독립 편입 검토 대기 | 동일 파일 Version 1 원본 11,237 bytes 수신·Revision v1.1·D33 승인 내용·Hash 확인. 새 원본 편입 독립 검토 대기. 과거 HTTP 502 이력 보존. |
| [D-SEC-01](../tickets/D-SEC-01/README.md) | 2026-09-01 | 종결·승인 관련 문서 | D34 승인·조치 기록 수신. 보안 설계 정본은 baseline 고정 참조; P1-SEC Runtime 범위와 분리. |
| [MS-G0-01](../tickets/MS-G0-01/README.md) | 2026-09-01 | 종결·승인 관련 문서 | D34 G0 Full PASS 상태 전이 기록 수신. G1/G2 또는 Bootstrap 승인으로 사용하지 않음. |
| [P1-DNS-01](../tickets/P1-DNS-01/README.md) | 2026-09-03 | COLLECTED_VERIFIED | 기존 수신·검증 기록을 포함한 PR #1 편입 기술 검토·병합 완료. 독립 리뷰의 원본 ZIP 외부 대조 NOT VERIFIED 범위 유지. |
| [CR-P1-ANS-01-01](../tickets/CR-P1-ANS-01-01/README.md) | 2026-09-07 | COLLECTED_VERIFIED_PRIOR_IMPORT_REVIEWED | Refinalization·Rollback 원본 보완 및 독립 편입 기술 검토 확인, PR #1 병합 완료. 서버측 보관 메타데이터 등 독립 리뷰의 NOT VERIFIED 유지. |

기존 등록 기록은 [PR #1](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5595784292)에서 독립 기술 검토 후 병합됐다. `MERGED_REGISTERED_RECORDS`는 원본 완비·각 티켓 실제 인수 완료를 뜻하지 않는다. 새 FUP-06/07/08 수신본은 별도 독립 검토 대기다. 기존 원본 문서 8개는 그대로 보존했다. 사후 작성한 CR 종료 기록을 서버 원본이나 과거 증적으로 간주하지 않는다.

P1-LB-01은 진행 중 티켓이며 Stage A 부분 증적을 별도로 관리한다. [후속 수신·인수 대장](FOLLOWUP_RECEIPTS.md), [관련 결정](RELATED_DECISIONS.md)을 참조한다.

[2026-09-07 ansible01 수신 검토](../receipts/ansible01/20260907T063705Z/FDS_Ansible_Evidence_Receipt_Review_v1.0.md) · [2026-09-08 FUP-02 보완 판정](../receipts/user-upload/20260908T111104Z/P1-ANS-01_FUP-02_REMEDIATION.md)

[2026-09-09 FUP-01 Refinalization 원본 수신 검토](../receipts/ansible01/20260909T003726Z/FDS_FUP01_Refinalization_Receipt_Review_v1.0.md)

[병합 후 후속 실행표](../runbooks/FUP-04-09_POST_MERGE_FOLLOWUP.md) · [신규 원본 수신 검토](../receipts/library/20260909T054024Z/RECEIPT_REVIEW.md)
