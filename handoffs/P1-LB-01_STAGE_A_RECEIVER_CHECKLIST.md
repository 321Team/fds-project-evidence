# P1-LB-01 Stage A 증적 인수 확인 체크리스트

상태: 기존 Stage A Technical/Evidence PASS 유지 / 증적 제출 완료 / 조건부 인수 기록 확인 / 미포함 2개 항목 참조 확인 대기. D36 승인정본과 CR 리뷰에 반영된 Stage A PASS는 재승인 대상이 아니다. [승인 범위 정정](../registry/STAGE_A_APPROVAL_SCOPE_CORRECTION.md)을 따른다. 이 체크리스트는 실제 인수 서명을 대신하지 않는다.

- 인계자: 이권욱
- 인수자: 이하영
- 검토 PR: [fds-project-evidence #1](https://github.com/321Team/fds-project-evidence/pull/1)
- 검토 Commit: 리뷰 시 PR의 현재 HEAD를 실제 승인 기록에 기입
- [기술·무결성 검토 기록](../evidence/P1-LB-01/stage-a/received-20260907/19_stage_a_handoff_review.md)
- [원본/보완 Index](../evidence/P1-LB-01/stage-a/received-20260907/EVIDENCE_INDEX.md)
- [Ansible CR 승인·병합 기록](../records/post-merge-20260907/CR-P1-ANS-01-01_CLOSURE.md)

## 기존 조건부 인수 회신 연결

[실제 회신](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5582767564)과 [정정 근거](../records/post-merge-20260909/PR3_CLOSURE_AND_FUP09_CORRECTION.md)를 연결한다. 아래 체크박스는 요구항목 목록으로 유지하며, 원문이 명시하지 않은 세부 항목을 임의로 체크하지 않는다.

## 인수자가 확인할 내용

- [ ] PR의 검토 HEAD와 수신 묶음 SHA-256 `62c64dfbd0cc672c96e4b1fbfa0c71a406e0c86d991b663c0ee02a47b82236a3`를 기록한다.
- [ ] 원본 21개, 기존 PACKAGE_SHA256SUMS, 신규 99_SHA256SUMS의 검증 범위를 구분해 확인한다.
- [ ] .109:6443 Listener, Node 6대·Runner Positive 및 비승인 Source Negative 결과를 확인한다.
- [ ] SELinux 및 임시 키 폐기 보완 3건은 이미 수용된 사용자 콘솔 증적임을 확인한다. 동일 파일 재제출이나 시험 재실행을 요구하지 않는다.
- [ ] 기술 원본이 Bootstrap 전 시점의 기록임을 확인한다. 당시 Backend DOWN을 Stage B 완료로 해석하지 않는다.
- [ ] 수신 묶음에 없는 LB-A-01 IP 중복검사와 firewalld Permanent 출력은 기존 Stage A 승인 근거의 참조를 확인한다. 신규 확인이 필요하면 별도 시각의 Supplement로 남긴다.
- [ ] P1-ANS 원본 인계와 후속 OS/Node·Runtime Gate의 완료 근거를 별도로 확인한다.
- [ ] 인수 결과, 인수 범위, 인수일시, 미해결 조건 및 검토 Commit을 실제 기록한다.

## 실제 기록 양식

실제 인수 여부는 인수자의 기존 기록 또는 인수 결과로 확인한다. 기존 기록이 있으면 참조를 연결한다. Codex가 인수 서명을 대신 작성하지 않는다.

| 필드 | 실제 입력 |
|---|---|
| 검토 Commit | `7dfec0a042c6f833cb246bb89560ec3eb0af892b` — 실제 회신 기재값 |
| 인수자 | 이하영 |
| 인수 결과 | 조건부 인수 — 실제 회신 연결 |
| 인수 일시 | 본문 2026-09-08; 정확한 시각·시간대 미기재. 게시 시각은 18:33:45 KST |
| 원본·Hash 대조 결과 | 원본 21개·콘솔 보완 3건 확인 및 수신 묶음 Hash·HEAD 대조 완료를 인수자가 보고 |
| 미해결 조건 / 인수 범위 | LB-A-01 IP 중복검사 원본·firewalld Permanent 출력의 기존 승인 근거 참조 대기 |
| 인수 리뷰 URL | [이하영 조건부 인수 회신](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5582767564) |
| 기존 Stage A 판정 | Technical/Evidence PASS — D36 승인정본 반영 |
| CR 재확인 | 이하영 2026-09-07 리뷰: Listener Ready PASS |
| Stage A PASS 재승인 | 요구하지 않음 |
| OS/Node Gate 참조 | 미입력 |
| Bootstrap Gate | HOLD |

GitHub에서 리뷰를 제출할 때 실제 검토한 HEAD와 위 인수 범위를 본문에 기록한다. 증적 편입 PR 승인이 Stage A 실제 인수를 포함하는지는 리뷰 문구에 명시해야 한다. infra-ansible의 완료된 리뷰는 기존 Listener Ready PASS의 재확인 근거로 재사용한다. 해당 리뷰에 명시되지 않은 실제 증적 인수까지 완료됐다고 확대하지 않는다.

## 인수 후 후속 조건

Stage A 실제 인수 및 필수 OS/Node Gate 확인 후 P1-K8S-01의 Bootstrap 승인 범위를 판정한다. Control Plane API 기동 후 P1-LB-01 Stage B의 Backend 3대 UP·인증 API·Failover를 수행한다. 전체 P1-LB-01은 Stage B가 남아 있으므로 In Progress다.
