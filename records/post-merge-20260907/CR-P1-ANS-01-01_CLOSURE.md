# CR-P1-ANS-01-01 승인·병합 인계 기록

작성일: 2026-09-07. 이 문서는 GitHub 승인·병합 메타데이터의 사후 인계 기록이며 원본 서버 시험 로그가 아니다.

| 항목 | 값 |
|---|---|
| 티켓 | CR-P1-ANS-01-01 |
| 승인·병합 Gate | 완료 |
| PR | [infra-ansible #1](https://github.com/321Team/infra-ansible/pull/1) — MERGED / CLOSED |
| Support | 이하영 / hayeounglee — APPROVED |
| Support 승인 | [리뷰 원본](https://github.com/321Team/infra-ansible/pull/1#pullrequestreview-5127492686), 2026-09-07 11:13:58 KST |
| 승인 대상 HEAD | `507d8882a04f53640b07251bcc234b7d6ee81c09` |
| Final Approver | 이권욱 — 2026-09-07 명시적 승인·main 병합 요청 |
| Merge Commit | [`4f9bdb7c08704eebb3d1b294751e51b0721b6af4`](https://github.com/321Team/infra-ansible/commit/4f9bdb7c08704eebb3d1b294751e51b0721b6af4) |
| 병합 일시 | 2026-09-07 15:02:55 KST / 06:02:55 UTC |
| 병합 검증 | 승인 HEAD와 병합 tree 일치; 기존 main·승인 HEAD를 부모로 확인한 PR 종료 기록 참조 |
| 원본 보관 | ansible01 / `/home/server01_ansible/p1-ans-01/docs/evidence/CR-P1-ANS-01-01/` |
| 증적 전용 저장소 원본 수신 | PENDING |
| CI / 이번 서버 시험 | NOT RUN / 재실행 없음 |

기존 P1-ANS-01 Done/2026-08-31과 구분한다. 증적 대장의 완료 항목은 기존 기준선의 12개에 본 CR을 더해 13개로 관리한다. 기준선·WBS·Notion 원본의 상태를 이 작업으로 수정하지 않는다.

## 원본 Hash 참조

| 파일 | 기록된 SHA-256 |
|---|---|
| EVIDENCE_INDEX.md | `6f5568d805a5d7f43130d2fdca2ba631358f4f8be23e1f7d0799ae8243c7db1e` |
| SHA256SUMS | `05de9ba6b22d36ef8fc67bdf3dd8c6629c3e334fbb61620a265a46acdbfd4115` |
| 20260904T180632+0900_verify_all_nodes.txt | `18cbda0fc7d91ebf58c89c230dccabaf9ad8239305856da03067210582194e83` |
| 20260904T182705+0900_integrity_check.txt | `35a320650312e343764a5d7eecfe70c42bafcf43c8043a422d920030a20dee14` |
| Refinalization Record | `db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d` |

위 Hash는 기존 PR에 기록된 값이며 이번 서버 원본 재검증 결과가 아니다. 수신 결과가 다르면 새 값으로 대체하지 않고 원인을 확인한다.

## 후속 연결

- [원본 수집 절차](../../runbooks/ANSIBLE_SOURCE_RECEIPT.md)
- [후속 수신 대장](../../registry/FOLLOWUP_RECEIPTS.md)
- [Stage A 실제 인수 체크리스트](../../handoffs/P1-LB-01_STAGE_A_RECEIVER_CHECKLIST.md)

Stage A 실제 인수와 이권욱의 Stage A 최종 승인은 Pending이다. kubeadm init/join HOLD, OS/Node Gate 및 Stage B 검증은 각 책임 티켓에서 판정한다. 본 CR의 승인·병합이 해당 승인을 대신하지 않는다.
