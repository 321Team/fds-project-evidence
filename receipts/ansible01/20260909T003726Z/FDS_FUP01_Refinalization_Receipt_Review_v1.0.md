# FUP-01 Refinalization 원본 수신 검토 v1.0

검토일: 2026-09-09. 판정: **PASS — FUP-01 원본 보완·수신 검증 완료 / 독립 편입 검토 대기**.

## 수신 결과

사용자가 ansible01에서 2026-09-09 09:37:26 KST에 수집한 패키지를 대조했다. Refinalization 원본은 2026-09-04 18:32:21 KST 기록이며 이번 수신 시각과 구분한다.

| 항목 | 결과 |
|---|---|
| 외부 패키지 | 1,773 bytes, sidecar SHA-256 일치 |
| 내부 구성 | 검색 보고서·Manifest·Refinalization 원본 3개 |
| 내부 Manifest | 2/2 일치 |
| Refinalization 원본 | 1,181 bytes, 승인 당시 기대 Hash 일치 |
| 원본이 참조하는 Index·Manifest·검증 로그 | 기존 Git 수신본 4/4 일치 |
| 검증 Commit / Tree | GitHub Git 객체와 일치 |
| verify 로그 수 | 기록 2개 / 기존 수신본 2개 일치 |
| 기존 Rollback 5대 | 등록 원본 5/5 Hash 유지 확인 |
| 수집 결과 | MATCH_FOUND_REVIEW_REQUIRED / matches=1 / issues=0 |

원본 SHA-256:

```text
db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d
```

패키지 SHA-256:

```text
6998cbbf93b20def23f235d37af70f916ea045a771b1e61716e831ef14ed6c97
```

첨부명의 `(1)`은 원래 sidecar 파일명과의 이름 차이다. 바이트 Hash를 직접 대조했으며 압축 원본·수신 텍스트를 재작성하지 않았다. 내부 Manifest는 압축 내부 경로 기준으로 보존하고 [원본→Git 매핑](SOURCE_FILE_MAP.json)을 제공한다.

## 출처와 내용 대조

- [수신 원본](../../../evidence/CR-P1-ANS-01-01/received-20260909T003726Z/evidence_refinalization.20260904T183221+0900.txt)
- [수집 보고서 원본](SEARCH_REPORT.json) · [검증 상세](RECEIPT_VERIFICATION.json) · [압축 보관 참조](SOURCE_PACKAGE.json)
- [승인 대상 CR 변경 기록](https://github.com/321Team/infra-ansible/blob/507d8882a04f53640b07251bcc234b7d6ee81c09/docs/change/CR-P1-ANS-01-01.md)
- 검증 Commit: `12412cd6beae7039de74be16258b8fb20c5d64b2`, Tree: `3e41df12845cc79b6f6154554e4d11ec42200508`.
- 원본의 `PASS_READY_FOR_CR_DOCUMENT_UPDATE`, `RESOLVED_AND_REVALIDATED`, `working_tree_state=CLEAN`, `push_performed=NO`를 확인했다. 이 원본은 9월 4일 재최종화 기록이며 9월 7일 사람 승인·병합 기록은 [기존 종료 기록](../../../records/post-merge-20260907/CR-P1-ANS-01-01_CLOSURE.md)으로 별도 추적한다.

당시 서버 보관 경로:

```text
/home/server01_ansible/.local/state/cr-p1-ans-01-01-repository/evidence_refinalization.20260904T183221+0900.txt
```

프로젝트 채팅에서 이 경로를 식별한 뒤 사용자가 정확한 파일을 지정해 수집했다. 이전 홈 검색은 `.local`을 재귀 탐색에서 제외했고, 이번에는 명시한 파일 입력 분기로 직접 읽었다. 따라서 이전 `NOT_FOUND_IN_SCOPE`는 제한된 검색 결과로 보존하며 전체 유실로 해석하지 않는다. 수집 보고서의 일반 `excluded` 설명과 명시 파일 처리 범위는 구분한다.

## 판정 범위

수집 보고서의 before/after dev·inode·size·mode·uid·gid·mtime·ctime은 동일하다. 보고값은 mode 0600 / uid 1000 / gid 1000이며 Codex가 서버에서 독립 측정한 값은 아니다. atime 보존은 주장하지 않는다. 알려진 Private Key·Token·credential 패턴 및 수신 본문 검토에서 비밀정보를 발견하지 못했다.

FUP-01의 미수신 항목은 이번 원본 1개와 앞선 Rollback 5개로 보완됐다. CR 원본은 기존 17개 + Rollback 5개 + Refinalization 1개, 총 23개다. 상태는 `COLLECTED_VERIFIED_REVIEW_PENDING`로 갱신한다. 독립 검토자는 이번 Commit의 원본 Hash·참조 4건·Rollback 연결·이력 보존 범위를 확인한다.

기존 Done/2026-09-07·사람 승인·CR 병합 이력은 보존한다. FUP-02는 기존 정합성 보완 완료·독립 검토 대기 상태를 유지한다. 이번 작업은 수신 검토이며 서버 apply·rollback·finalize 재실행, 다른 Gate 변경, 증적 PR main 병합을 수행하지 않았다.
