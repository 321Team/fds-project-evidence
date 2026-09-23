# 기존 증적 매핑 — FUP-04/05/06/07/09

기준 main: `493c09e728b643d620debe29738f1b47b3cafa8a`. 사용자의 결과서 반영·후속 착수 지시에 따라 기존 파일을 고정 참조로 연결한다. 이번 변경의 독립 검토는 대기다.

## 연결 결과

| Index | 대상 | 상태 | 원본 고정 참조 | 범위·잔여 |
|---|---|---|---|---|
| 01 | Windows PostBuild server01~08 | SUMMARY_ONLY | [D-NET-01_Closure_Report_v1.0.md](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/records/received-20260907/D-NET-01_Closure_Report_v1.0.md) | 원래 Windows 실행 로그·캡처 미확보 |
| 02 | VMware Virtual Network Editor | GUIDE_AND_SUMMARY_ONLY | [D-NET-01_Closure_Report_v1.0.md](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/records/received-20260907/D-NET-01_Closure_Report_v1.0.md) | 실제 VMnet0/1/8 화면 캡처 미확보 |
| 03 | Linux Node Network Verify | LATER_EVIDENCE_LINKED | [01_network_precheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/01_network_precheck.txt) · [05b_node_precheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/05b_node_precheck.txt) · [06g_full_postcheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/06g_full_postcheck.txt) | 8/28 연결·노드 상태 보완 근거. 8/26 fds-node-verify 전문 아님 |
| 04 | K8s Linux Prerequisites | LATER_EVIDENCE_LINKED | [05b_node_precheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/05b_node_precheck.txt) · [06d_canary_postcheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/06d_canary_postcheck.txt) · [06g_full_postcheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/06g_full_postcheck.txt) | 8/28 6대 사전·사후 점검. canary는 control01 1대 |
| 05 | Physical Return Route | LATER_EVIDENCE_LINKED | [05b_node_precheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/05b_node_precheck.txt) · [06g_full_postcheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/06g_full_postcheck.txt) | 8/28 management_route .58 경유. 8/26 최초 원본·영구 프로필 전체는 미확보 |
| 06 | Source Preservation PASS6 | LATER_EVIDENCE_LINKED | [05c_source_preservation.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/05c_source_preservation.txt) | 8/28 6대 sshd 실제 Source .10. 8/26 배치 결과와 별도 |
| 07 | Management VM Verify | PARTIAL_LATER_EVIDENCE | [D-NET-01_Closure_Report_v1.0.md](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/records/received-20260907/D-NET-01_Closure_Report_v1.0.md) · [01_network_precheck.txt](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/01_network_precheck.txt) | ansible 일부 출력만 연결. 관리 VM 3대 전체 Verify 전문 미확보 |
| 08 | mgmt-gw01 Verify | SUMMARY_ONLY | [D-NET-01_Closure_Report_v1.0.md](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/records/received-20260907/D-NET-01_Closure_Report_v1.0.md) | gateway 자체 전체 Verify 원문 미확보 |
| 09 | DO_NOT_USE_IP Exception | DECISION_DOCUMENT_LINKED | [D-NET-01_Closure_Report_v1.0.md](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/records/received-20260907/D-NET-01_Closure_Report_v1.0.md) | §3·§5 IP 예외 문서. 당시 응답 장비 조사 원문 미확보 |
| 10 | D-NET-01 Closure | EXISTING_DOCUMENT_LINKED | [D-NET-01_Closure_Report_v1.0.md](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/records/received-20260907/D-NET-01_Closure_Report_v1.0.md) | 기존 main의 종결 보고서. 01~09 원본 완비를 뜻하지 않음 |

Index 10 종결 보고서는 이미 수신·병합돼 있다. Index 03~06은 2026-08-28 Ansible 보완 원본을 연결한다. 2026-08-26 최초 종결 원본이나 그 시점의 상태로 소급하지 않는다. Source 보존은 05c의 6대 sshd 실제 관찰값으로 판단하며 01의 연결 성공만으로 대체하지 않는다. 06d canary는 control01 한 대다.

## 선택한 5개 원본의 무결성

기존 Git blob·당시 Manifest·수신 SOURCE_FILE_MAP을 각각 대조했다. 아래는 5개 파일의 결과이며 전체 저장소를 새로 재검증한 결과가 아니다. 기존 원본 경로·바이트는 변경하지 않는다.

| 파일 | SHA-256 | 3종 대조 |
|---|---|---|
| 01_network_precheck.txt | `b770f87cb71b25a992bbd9f9825814de704f2664137450c6b6d043d653b87364` | 일치 |
| 05c_source_preservation.txt | `8bb453665f2d6d17411a767ec50a5801d4f45a6c3665592d31c88280974a89ed` | 일치 |
| 05b_node_precheck.txt | `1fa33b73d7364532fff25c56447d237d9d09d8384df28b81b7b6419023ecea30` | 일치 |
| 06d_canary_postcheck.txt | `8a4fd2170e2a79d59de9cc51b60ed69b67710e5b60e008a4973e13aedbb81deb` | 일치 |
| 06g_full_postcheck.txt | `16d9198a9215f8f1248aa5b32bd13ce7e2dd7d47310e9908123a7d53fae8f4d3` | 일치 |

[당시 Manifest](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/99_SHA256SUMS.txt) · [수신 SOURCE_FILE_MAP](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/receipts/ansible01/20260907T063705Z/SOURCE_FILE_MAP.json) · [P1-ANS-01 완료일·범위 Index](https://github.com/321Team/fds-project-evidence/blob/493c09e728b643d620debe29738f1b47b3cafa8a/evidence/P1-ANS-01/received-20260907T063705Z/P1-ANS-01_Evidence_Index.md)

## 승인 참조와 잔여 조건

- FUP-05: 사용자의 기존 P1-NET 종결 언급은 Done 상태의 근거이며 개별 Reviewer/Approver·승인일시의 증거가 아니다. 해당 값은 미확인이다.
- FUP-06/07: [과거 v3.1.3 정본의 승인 메타데이터 발췌](HISTORICAL_APPROVAL_METADATA.json)를 연결했다. Architecture v3.1.2 및 WBS v3.1.3 APPROVED 표기와 8/26 종결을 확인한다. 파일 읽기 응답에서 만든 참조 발췌이며 원본 바이너리나 과거 서명으로 표시하지 않는다. 개인별 승인 회신·승인 시각·WBS 실제 열람은 미확인이다. 이전 후보 편입의 수용·병합을 되돌리지 않는다.
- FUP-09: [PR #6](https://github.com/321Team/fds-project-evidence/pull/6)의 새 Permanent 수신분은 독립 APPROVED·CONFIRMED 후 main 편입 완료다. 이하영의 새 인수 판단과 IP 중복검사 전문·고정 참조는 대기다.
- 채팅은 20개 조건 검색으로 조사했으나 전체 목록·전문 열람이 제공되지 않았고 일부 오류·생략이 있었다. 채팅 회수 요약을 원본 로그나 타인의 승인으로 등록하지 않는다.

[구조화된 매핑](EXISTING_EVIDENCE_MAP.json) · [잔여 자료 실행표](../../runbooks/FUP-04-09_REMAINING_SOURCE_ACTIONS.md) · [이슈 #4](https://github.com/321Team/fds-project-evidence/issues/4)

기존 13개 완료 티켓의 Done·종결일·원 승인 정보, Stage A PASS·조건부 인수·Bootstrap HOLD를 유지한다. 이 매핑은 인프라 변경·시험 재실행 또는 미확인 인수의 대필을 포함하지 않는다.
