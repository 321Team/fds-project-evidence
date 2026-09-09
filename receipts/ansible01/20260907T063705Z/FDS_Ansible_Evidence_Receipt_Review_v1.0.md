# Ansible 증적 수신 검토 보고서 v1.0

검토일: 2026-09-07 · 수신회차: ANSIBLE01-20260907T063705Z

## 1. 판정

**전송 무결성 PASS, DNS R2 원본 수신 검증 PASS. CR은 보완 원본 수신 대기, P1-ANS는 기존 Manifest 불일치로 증적 정합성 보완이 필요하다. 전체 증적 편입 최종 승인은 보류한다.**

이 보고서는 제출 바이트와 기존 기록의 대조 결과다. 서버 시험을 재실행한 결과 또는 이하영의 독립 인수 승인이 아니다. 기존 P1-ANS/P1-DNS의 Done·종결일과 CR 승인·병합 결과는 유지한다. Stage A 실제 인수와 `kubeadm init/join` HOLD도 유지한다.

| 범위 | 수신 | 검증 결과 | 증적 편입 상태 |
|---|---:|---|---|
| 전송 묶음 | 62,121 bytes | 외부 Sidecar 일치, COLLECTION_SHA256SUMS 58/58 일치 | 수신 완료 |
| CR-P1-ANS-01-01 | 17개 | 기존 Manifest 16/16, PR 주요 Hash 4/4 일치 | 부분 수신·보완 원본 대기 |
| P1-ANS-01 | 38개 | 기존 Manifest 37개 중 35개 일치, 2개 불일치 | 원본 수신·정합성 보완 필요 |
| P1-DNS-01 | ZIP·Sidecar 2개 | 기록 ZIP Hash 일치, 내부 Manifest 12/12, 개별 Sidecar 11/11 일치 | 원본 수신 검증 완료·독립 편입 검토 대기 |

티켓 파일 57개와 수집 메타데이터 2개로 tar 안에는 일반 파일 59개가 있다. 새 수집 Manifest의 58개 검증 대상은 티켓 파일 57개와 COLLECTION_REPORT.json이며 Manifest 자신은 제외한다.

## 2. 제출 패키지와 검증 범위

- 수집기 기록 시각: 2026-09-07 15:37:05 KST / 06:37:05 UTC.
- 제출 Host·Operator: `ansible01` / `server01_ansible` — 수집 보고서와 사용자 콘솔 근거.
- 외부 파일: `FDS_Evidence_Receipt_v1.0.tar.gz`.
- 외부 SHA-256: `c16bcc02593eca6657420d7026a61b63c24599013d6f846a8c60197b4e7497a0`.
- DNS ZIP: `P1-DNS-01-FRESH-20260902-R2.zip`, 28,138 bytes.
- DNS ZIP SHA-256: `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab`.
- 경로 이탈·중복 경로·링크/특수 파일을 확인한 후 별도 검토 경로에서 읽었다. DNS CRC 오류 없음.
- 수집 보고서의 파일 크기·SHA-256 메타데이터 57/57이 실제 제출 바이트와 일치한다.
- 원본 서버의 무변경 상태는 수집기·사용자 보고이며 서버에 재접속하여 독립 확인한 결과는 아니다.
- 원본 바이트를 변경하지 않았다. ZIP 내부 텍스트 24개는 바이트 그대로 추출해 참조하고 ZIP을 재생성하지 않았다.
- 텍스트와 DNS 내부의 Private Key·주요 공급자 Token·고엔트로피 Credential 할당 패턴 검사에서 일치 없음. 이 검사는 모든 비밀정보의 부재를 보장하는 인증이 아니다.

수집 콘솔의 `issues=0`은 읽기·필터 처리 중 issues 목록이 비어 있다는 뜻이다. `missing_required`, `original_manifest`, `refinalization_hash_matches`를 합산한 숫자가 아니다. 따라서 이번 P1-ANS의 2개 Hash 불일치와 예상 파일명 1건 미수신이 있어도 issues=0으로 출력된다. 상세 COLLECTION_REPORT와 수신 검증 결과를 기준으로 판단해야 한다.

## 3. CR-P1-ANS-01-01

### 확인 사실

- 기존 SHA256SUMS 기재 16개가 모두 일치하며 Index, Manifest, 최종 6대 검증 로그, 최종 무결성 로그의 Hash는 병합 PR의 기록과 4/4 일치한다.
- CP 2대와 Worker 3대 적용 로그는 failed=0/unreachable=0이다. 각각의 멱등성은 changed=0이다.
- 최종 `20260904T180632+0900_verify_all_nodes.txt`는 6대 모두 changed=0, unreachable=0, failed=0이다.
- 최초 Precheck 실패는 해결 이력으로 보존한다. 이 로그를 최종 PASS 근거로 사용하지 않는다.
- Index의 실행 Commit `12412cd6…`와 승인 HEAD `507d8882…`는 역할이 다른 참조다. 수신 검토를 이유로 과거 Index에 병합 Commit을 덮어쓰지 않는다.
- 최종 무결성 로그 자체를 포함하는 수신 Manifest의 16개 대조와, 당시 로그 안에 출력된 15개 성공 결과를 구분한다.

### 잔여 항목

| ID | 발견 사항 | 필요한 자료·조치 |
|---|---|---|
| RCV-CR-01 | Refinalization Record의 기록 Hash와 일치하는 수신 파일 없음 | 기존 원본 또는 고정 원본 참조를 제출. 기대 SHA-256은 `db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d`. 새 문서를 같은 원본으로 재생성하지 않는다. |
| RCV-CR-02 | Rollback 상태자료 원본 미수신 | 변경 Node 5대의 당시 보존 상태자료 또는 위치·Hash·권한을 확인하는 기존 수신 가능한 기록을 연결한다. 적용 로그의 보존 Task 성공과 실제 상태파일 바이트 검증을 구분한다. |

Rollback 상태자료는 수집기의 ansible01 티켓 폴더 범위 밖에 있을 수 있다. 이번 미수신은 Rollback 기능 실패나 당시 파일 부재를 뜻하지 않는다. 검증만을 위해 Resolver Rollback을 실행하지 않는다. 정보가 부족하므로 실제 상태파일의 존재·보관 위치·완비는 미확인으로 남긴다.

## 4. P1-ANS-01

### 확인 사실

- 수신 승인문서 05h/05j 본문에 2026-08-31 이하영 PASS/APPROVED와 HO-ANS-08·09 종결 기록이 있다. 05j 승인이 전혀 없다고 판정하지 않는다.
- v1.3 Primary Closure Evidence 31개 중 지정 파일명 기준 30개가 존재한다. 나머지 05j는 아래의 다른 파일명으로 승인 내용이 수신됐다.
- `06g_full_postcheck`, `06h_full_idempotency`, `08_final_check_diff_no_drift`는 모두 6대 failed=0/unreachable=0, 멱등성·최종 Check/Diff는 changed=0이다. `05g6` SSH 제한 멱등성도 동일하다.
- 기존 Index는 초기 종결 당시 상태를 포함한다. 후속 SSH 승인 기록은 별도로 연결한다.

### RCV-ANS-01 — 기존 Manifest 2개 불일치

| 파일 | 기존 99_SHA256SUMS.txt 기재 Hash | 수신 실제 Hash |
|---|---|---|
| 05h_ssh_key_lifecycle_record.md | `7ab0ad3c1b1610009dfc5c777f17f1bbb74f3a8d172b696ddb22a56d37763752` | `9f5b8c1b24dc9e44109d57205ca3c13bf54e3b0e05ee53615371f2604065ad95` |
| 05j_review_approval_record.md | `e64c466161f441b7007e6dfb7bb2dbe1046cf7a74a68653731e66c69f20e826c` | `944d3e74cfc72e9ed0ce56a5914a16fcba7ae35f2145cd243f2e2a5ef172006d` |

불일치는 사실이다. 기존 v1.3 종결문서와 수신 승인문서는 승인본 배치 및 Manifest 재생성·검증을 배포 후속 조치로 명시한다. 따라서 승인문서 갱신 후 Manifest 미갱신 가능성이 있으나 **실제 변경 이력·이전 바이트가 없어 원인은 확정할 수 없다.** 전송 오류로도 단정할 수 없다. 새 수집 Manifest가 일치한다는 사실은 과거 Manifest 불일치를 해소하지 않는다.

### RCV-ANS-02 — 05j 파일명·본문 참조 불일치

| 구분 | 파일명 |
|---|---|
| 승인문서·종결목록·수집기 지정 | `05j_reviewer_approver_record.md` |
| 실제 수신 파일·기존 Manifest 기재 | `05j_review_approval_record.md` |

수신 파일 본문 자체도 지정 경로를 reviewer_approver로 표기한다. 기존 파일을 임의로 이름 변경해 원본인 것처럼 편입하지 않는다. 승인 정본과 변경 이력을 대조한 후 정규 파일명 또는 승인된 별칭 매핑을 문서화하고, 실제 배포 후의 별도 Manifest·검증 로그를 제출한다.

### 보완 순서

1. 현재 수신본과 기존 Manifest를 그대로 보존한다.
2. 05h/05j의 이전 파일·변경 내역 또는 승인 배포 기록으로 불일치 원인을 확인한다. 이전 파일이 없으면 확인 불가 범위를 명시한다.
3. 지정 승인본과 파일명 정합성을 확인한 뒤 새 배포회차로 반영한다. 이 작업에서 원본·승인 내용·Manifest를 소급 수정하지 않았다.
4. 기존 Manifest를 보존한 상태에서 새로운 배포회차 Manifest와 전체 검증 결과를 남기고 변경자·시각·사유·전후 Hash를 연결한다.
5. 보완본을 별도 수신회차로 제출한다. 단순 Hash 재생성만으로 기존 불일치를 종결하지 않는다.

0-byte `04a_ansible_ping_inventory_missing.txt`와 Index의 과거 `04_ansible_ping.txt` 참조 차이는 초기 Troubleshooting 자료의 문서 품질 항목이다. 최종 Ping 원본은 별도로 수신됐으므로 이를 최종 기술 실패 또는 필수 시험 재실행 사유로 사용하지 않는다.

## 5. P1-DNS-01

- 기록된 R2 ZIP Hash와 제출 Sidecar가 일치한다.
- ZIP 내 일반 파일 24개: 실행 로그 11개, 로그 Sidecar 11개, Index 1개, SHA256SUMS 1개.
- 기존 내부 Manifest의 Index 및 실행 로그 12/12 일치. 로그 Sidecar 11/11 일치. Manifest 자기 자신과 Sidecar는 내부 중앙 Manifest의 대상이 아니며 전체 ZIP Hash로 추가 보호된다.
- Index의 17개 테스트 행은 PASS 16개, N/A 1개(Reverse/PTR)로 기재돼 있다. 원본 로그에서 Record Inventory 26/26, Fresh TSIG 성공, DNS Failover·복구, Resolver Rollback·재적용 결과를 확인했다.
- monitor01 Negative 로그는 허용 DNS 응답을 얻지 못한 결과를 보여준다. `host unreachable`만으로 특정 방화벽 규칙이 차단 원인이라고 확대 판정하지 않는다.
- Index의 `In Review — Support Review pending`은 패키지 작성 시점 상태다. 기존 v1.3-R5 종결문서의 완료 기록과 연결하며 ZIP 내부를 현재 Done으로 다시 쓰지 않는다.

**FUP-03의 원본 수신·무결성 검증을 완료로 갱신한다.** 저장소 독립 편입 검토·최종 승인·병합은 별도로 남는다.

## 6. 후속 항목

| 대상 | 현재 상태 | 다음 조치 |
|---|---|---|
| FUP-01 CR | 17개 수신·수신 파일 무결성 PASS | Refinalization 및 Rollback 상태자료 보완 |
| FUP-02 P1-ANS | 38개 수신·2개 Hash 불일치 | 승인본 변경 이력·05j 명칭 정합성·배포 후 검증 |
| FUP-03 DNS R2 | 원본 수신 검증 완료 | 증적 PR 독립 검토 |
| FUP-04 D-NET/P1-NET/P1-LNX | 공통 원본 수신 대기 | 01~10 인덱스의 실제 로그·캡처·기존 Manifest와 보관 위치 |
| FUP-05 P1-NET | 승인 참조 확인 대기 | 실제 Reviewer/Approver·승인 일시 원본 또는 고정 참조 |
| FUP-06 D-ARC | 승인본 식별 대기 | 동결 당시 Architecture v3.1.2와 승인 참조 |
| FUP-07 D-WBS | 참조 확인 대기 | 동결 당시 WBS 및 승인 기록 고정 참조 |
| FUP-08 D33 | 내용 확인·원본 바이트 대기 | 기존 개별 승인문서 원본 수신·Hash 확인 |
| FUP-09 LB Stage A | 실제 인수 대기 | 이하영 실제 인수, 검토 Commit·범위·일시 및 이권욱 Stage A 최종 승인 |

LB 원본 21개·콘솔 보완 3건의 기존 수용 결과는 유지한다. 보완 3건을 필수 재제출 항목으로 되돌리지 않는다.

## 7. 개선 권고와 Gate

수집기 콘솔은 `collection_issues`, `missing_required`, `manifest_mismatches`, `missing_references`를 각각 출력하도록 개선하는 것이 적절하다. 이번 검토에서는 원 수집기 v1.0과 수집 보고서를 변경하지 않았으며 전체 원본을 다시 수집할 필요도 없다. 보완할 항목만 새 회차로 수신하면 된다.

- 본 검토 판정: **RECEIVED / PARTIAL_VERIFIED / REMEDIATION_REQUIRED**.
- 증적 PR: Draft 및 독립 검토 대기. 최종 승인·main 병합 미수행.
- 기존 P1-ANS/P1-DNS Done 및 CR MERGED: 유지.
- Stage A 실제 인수·최종 승인: Pending.
- Kubernetes Bootstrap: HOLD. 인수 및 필수 OS/Node Gate는 해당 담당자의 증적·승인으로 별도 판단한다.

## 8. 근거

- 사용자 제출 `FDS_Evidence_Receipt_v1.0.tar.gz`와 `.sha256`, 패키지 내 COLLECTION_REPORT/각 원본 Manifest·Index·실행 로그.
- [승인·병합된 Ansible CR PR #1](https://github.com/321Team/infra-ansible/pull/1).
- [병합 Commit의 CR 변경 기록](https://github.com/321Team/infra-ansible/blob/4f9bdb7c08704eebb3d1b294751e51b0721b6af4/docs/change/CR-P1-ANS-01-01.md).
- [기존 P1-ANS 종결·승인 문서 v1.3](https://github.com/321Team/fds-project-evidence/blob/cfd848615fb5cde387f2f58838f0a5d2535f0930/records/received-20260907/FDS_Notion_Technical_PASS_P1-ANS-01_v1.3.md).
- [기존 DNS 종결 문서 v1.3-R5](https://github.com/321Team/fds-project-evidence/blob/cfd848615fb5cde387f2f58838f0a5d2535f0930/records/received-20260907/P1-DNS-01_Notion_Description_v1.3_Review.md).
- [기존 수집기 v1.0](https://github.com/321Team/fds-project-evidence/blob/cfd848615fb5cde387f2f58838f0a5d2535f0930/tools/collect-ansible-evidence.py).
- 새 회차의 파일별 대조: RECEIPT_VERIFICATION.json, 원본→저장소 경로·Hash 연결: SOURCE_FILE_MAP.json.

## 9. 최초 등록 준비 기록 — 추가 명시적 승인 전

- 원격 기준 HEAD: `cfd848615fb5cde387f2f58838f0a5d2535f0930`.
- 준비 시작 전 원격 71개 파일과 로컬 Git blob Hash 71/71 일치를 확인했다.
- CR/P1-ANS 원본 55개, DNS ZIP 추출 원본 24개, 총 79개의 원본→준비본 바이트 일치를 확인했다.
- 기존 LB 증적, 종결·승인 원본 8개와 CR 병합 기록은 그대로 보존했다.
- 갱신 대장과 신규 수신회차를 포함한 준비본은 총 158개 파일이며 REGISTRY_SHA256SUMS 157개 항목이 일치한다.
- **최초 등록 시도 미수행:** 자동 승인 검토가 이번 내부 인프라 상세 원본의 대상 저장소 업로드 승인이 명확하지 않다고 판단하여 Git tree 생성을 거부했다. 이번 변경의 Commit 생성·브랜치 이동·PR 갱신은 수행하지 않았다.
- 위 차단 시점에는 대장 갱신이 로컬 준비본에만 반영됐다. 당시 배포 패키지와 원격 상태를 구분하는 이력이다. 이후 등록 승인과 현재 상태는 아래 후속 기록 및 PR 본문을 참조한다.
- 요청하는 등록 범위: `321Team/fds-project-evidence` Private 저장소의 기존 `evidence/initial-import-20260907` 브랜치와 Draft PR #1에 텍스트 원본·수신 메타데이터·검토 보고서·대장 갱신본 추가. 내부 IP/Host/권한 메타데이터 포함. 원본 tar/ZIP은 제출 파일로 보존하며 Git에는 바이너리를 추가하지 않는다.
- 최종 증적 승인, main 병합, Stage A 실제 인수, Kubernetes Bootstrap 해제는 이 등록 범위에 포함하지 않는다.

## 10. 원본 등록에 대한 추가 명시적 승인

- 승인일: 2026-09-07.
- 승인자: 이권욱 — 현재 사용자 대화의 명시적 요청.
- 사용자 승인 원문: “자동 승인 검토에서 차단된이유가 뭐지? 일단 권고한 브랜치와 Draft PR #1에 등록하는것을 승인”.
- 직전 요청에서 명시한 대상: `321Team/fds-project-evidence` Private 저장소, `evidence/initial-import-20260907` 브랜치 및 Draft PR #1.
- 승인 대상: 직전 제공 패키지에 포함한 CR/P1-ANS 텍스트 원본 55개, DNS ZIP 내부 텍스트 원본 24개, 수집 메타데이터·검토문서·대장 갱신본. 내부 IP·호스트·권한 메타데이터 포함 사실을 안내한 후 승인받았다.
- 원본 등록 승인: APPROVED. 이는 과거 Hash 불일치를 해소하거나 증적 편입 최종 승인을 부여하는 기록이 아니다.
- 원본 tar/ZIP은 제출 파일에서 그대로 보존하며 Git에는 텍스트 원본과 보관 참조를 기록한다.
- 실제 게시 Commit·원격 파일 대조 및 Draft 유지 여부: [증적 PR #1](https://github.com/321Team/fds-project-evidence/pull/1)의 등록 결과를 참조한다.
- main 병합·최종 증적 승인·Stage A 실제 인수·Kubernetes Bootstrap 해제는 별도 Gate로 유지한다.
