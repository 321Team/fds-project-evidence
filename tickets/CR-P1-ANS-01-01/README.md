# CR-P1-ANS-01-01 — 완료 CR 증적 편입

- 티켓 승인·병합 완료: 2026-09-07
- 상태 근거: [infra-ansible PR #1](https://github.com/321Team/infra-ansible/pull/1)
- [종료 기록](../../records/post-merge-20260907/CR-P1-ANS-01-01_CLOSURE.md)
- [원본 수집 절차](../../runbooks/ANSIBLE_SOURCE_RECEIPT.md)
- 원본 수신: ROLLBACK_RECEIPT_VERIFIED_REFINALIZATION_PENDING — 기존 17개 + Rollback 상태 5개 수신, Refinalization 원본 대기
- 증적 저장소 편입 검토: PENDING

기존 P1-ANS-01 Done/2026-08-31과 분리한다. 이 CR 승인은 Stage A 인수나 Bootstrap 승인을 대신하지 않는다.

## 2026-09-07 원본 수신

17개 수신·Manifest 16/16 및 주요 Hash 4/4 일치. Refinalization 원본·Rollback 상태자료 보완 대기.

[수신 검토 보고서](../../receipts/ansible01/20260907T063705Z/FDS_Ansible_Evidence_Receipt_Review_v1.0.md)

## 2026-09-08 Rollback 보완 수신

새 수집회차의 외부 sidecar와 내부 6/6 해시가 일치한다. 변경 노드 5대의 원본 JSON을 바이트 그대로 수령했다. 수집 보고서상 원본은 root:root/0600이며, 권한·읽기 전후 불변성의 원시 stat 증적은 패키지에 없다. 따라서 보고 기반 보관 정보와 직접 재계산한 원본 해시를 구분한다.

Refinalization 원본은 미수신이다. 다음 제출은 당시 원본 또는 고정 참조로 한정하며, 5대 재수집·rollback·finalize 재실행은 불필요하다.

[보완 수신 검토](../../receipts/ansible01/20260908T115139Z/FDS_FUP01_Rollback_Receipt_Review_v1.0.md)
