# 완료 티켓 증적 편입 대장 v1.1

기존 기준선의 완료 티켓 12개와 2026-09-07 승인·병합 완료된 CR-P1-ANS-01-01을 포함해 13개를 관리한다. 기존 12개는 v3.1.16 Closed/Project Status Register 및 v3.1.17 WBS 대조 기록, 추가 CR은 infra-ansible PR #1의 실제 승인·병합 기록을 근거로 한다. 기준선·WBS 원본은 이 작업에서 변경하지 않는다.

| 티켓 | 종결일 | 이번 수신 | 추가 확인 |
|---|---|---|---|
| [D-ARC-01](../tickets/D-ARC-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | 종결 설명 수신. 동결 당시 Architecture 승인본·승인 참조 확인 필요. Runtime 시험 대상 아님. |
| [D-NET-01](../tickets/D-NET-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | Closure Report 수신. docs/evidence/D-NET-01/의 01~10 원본 로그·캡처 및 기존 Manifest 미수신. |
| [D-WBS-01](../tickets/D-WBS-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | 종결 설명 수신. 동결 당시 WBS 및 승인 기록의 고정 참조 확인 필요. 현 WBS를 과거 증적으로 대체하지 않음. |
| [P1-LNX-01](../tickets/P1-LNX-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | D-NET 공통 Closure Report만 수신. 04_K8s_Linux_Prerequisites 등 실제 원본 미수신. |
| [P1-NET-01](../tickets/P1-NET-01/README.md) | 2026-08-26 | 종결·승인 관련 문서 | D-NET 공통 증적을 참조. 원본 로그·캡처 미수신; 종결 문서의 Reviewer/Approver는 미입력이므로 임의 지정하지 않음. |
| [P1-ANS-01](../tickets/P1-ANS-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | v1.3 종결·승인 문서 수신. 원본 로그와 05h/05j 반영 후 99_SHA256SUMS 검증 자료 미수신. 원래 티켓 Done 유지. |
| [DEC-P1-ENTRY-01](../tickets/DEC-P1-ENTRY-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | D18 설계 승인 문서 수신. 실제 Service/접근 제어 Runtime은 후속 구현 티켓 범위. |
| [DEC-P1-TLS-01](../tickets/DEC-P1-TLS-01/README.md) | 2026-08-31 | 종결·승인 관련 문서 | D19 설계 승인 문서 수신. Private Key 제외; 인증서 배포·Push/Pull Runtime은 후속 구현 티켓 범위. |
| [DEC-P1-MON-01](../tickets/DEC-P1-MON-01/README.md) | 2026-08-31 | 개별 승인 내용 확인 / 바이트 대기 | 개별 문서 본문 Revision v1.1의 Done/APPROVED/D33 Fixed/2026-08-31을 확인했다. 다운로드 HTTP 502로 원본 바이트·Hash 수신은 대기. FOLLOWUP_RECEIPTS.md 참조. |
| [D-SEC-01](../tickets/D-SEC-01/README.md) | 2026-09-01 | 종결·승인 관련 문서 | D34 승인·조치 기록 수신. 보안 설계 정본은 baseline 고정 참조; P1-SEC Runtime 범위와 분리. |
| [MS-G0-01](../tickets/MS-G0-01/README.md) | 2026-09-01 | 종결·승인 관련 문서 | D34 G0 Full PASS 상태 전이 기록 수신. G1/G2 또는 Bootstrap 승인으로 사용하지 않음. |
| [P1-DNS-01](../tickets/P1-DNS-01/README.md) | 2026-09-03 | 종결·승인 관련 문서 | v1.3-R5 종결 설명 수신. R2 ZIP·sidecar·내부 Manifest 원본 미수신. 기록된 Hash만 확보했으므로 이번 원본 검증 PASS를 선언하지 않음. |
| [CR-P1-ANS-01-01](../tickets/CR-P1-ANS-01-01/README.md) | 2026-09-07 | GitHub 승인·병합 기록 / 서버 원본 대기 | 승인·병합 종료 기록은 확보. ansible01의 CR 원본 Index·SHA256SUMS·실행/무결성/복구 자료 수신 대기. runbooks/ANSIBLE_SOURCE_RECEIPT.md에 따라 수집. |

저장소 편입은 모든 행에서 CANDIDATE_REVIEW_PENDING이다. 기존 원본 문서 8개는 그대로 보존했다. 사후 작성한 CR 종료 기록을 서버 원본이나 과거 증적으로 간주하지 않는다.

P1-LB-01은 진행 중 티켓이며 Stage A 부분 증적을 별도로 관리한다. [후속 수신·인수 대장](FOLLOWUP_RECEIPTS.md), [관련 결정](RELATED_DECISIONS.md)을 참조한다.
