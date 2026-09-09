# 후속 증적 수신·인수 대장 v1.8

기준일: 2026-09-09. infra-ansible PR #1은 최종 승인·병합 완료다. 아래 항목은 기존 완료 티켓의 재구현이 아닌 증적 수신·편입 및 실제 인수 절차로 관리한다.

| ID | 대상 | 이번 조치 | 다음 수신·확인 항목 | 상태 |
|---|---|---|---|---|
| FUP-01 | CR-P1-ANS-01-01 | 원본 23개 보완·독립 편입 기술 검토 확인·PR #1 병합 | 기존 독립 리뷰의 NOT VERIFIED 범위 유지 | 기존 편입 기록 병합 완료 |
| FUP-02 | P1-ANS-01 | 05h/05j 보완·alias·신규 Manifest 독립 편입 검토 확인·PR #1 병합 | 구 Manifest 불일치 이력·겸임 관찰사항 유지 | 기존 편입 기록 병합 완료 |
| FUP-03 | P1-DNS-01 | 기존 원본 수신 검증 기록을 포함한 PR #1 편입·병합 완료 | 독립 리뷰의 원본 ZIP 외부 대조 NOT VERIFIED 유지 | 기존 편입 기록 병합 완료 |
| FUP-04 | D-NET-01/P1-NET-01/P1-LNX-01 | 공통 원본은 한 번 수집하도록 유지 | 인덱스 01~10 중 미수신 Windows/VMware/Linux/Return Route/Source Preservation 로그·캡처·기존 Manifest. 실제 보관 위치 확인 필요 | 원본 수신 대기 |
| FUP-05 | P1-NET-01 | Reviewer/Approver 미입력 상태 유지 | 실제 검토자·승인자·일시를 확인할 원본 또는 고정 참조 | 참조 확인 대기 |
| FUP-06 | D-ARC-01 | 종결 설명의 Freeze 메타데이터가 있는 논리·물리 원본 2개 수신·Hash 기록 | 당시 승인 참조 최종 연결 및 새 편입 독립 검토 | 원본 수신 / 승인 참조·독립 검토 대기 |
| FUP-07 | D-WBS-01 | 종결 설명 지정 WBS v3.1.3 원본·Hash·CRC 확인, 별도 보관 참조 등록 | 동결/갱신 승인 참조 연결·검토자 원본 접근·독립 편입 검토 | 후보 원본 수신 / 승인 참조·독립 검토 대기 |
| FUP-08 | DEC-P1-MON-01/D33 | 동일 파일 Version 1 원본 11,237 bytes 정상 수신·Revision/승인 내용·Hash 확인 | 새 원본의 독립 편입 검토 | 원본 수신 완료 / 독립 검토 대기 |
| FUP-09 | P1-LB-01 Stage A | D36 승인정본과 CR 리뷰의 Stage A PASS 유지·증적 제출 완료 | 이하영 증적 인수 여부를 확인할 범위·일시·참조 연결. Stage A PASS 재승인 요구 없음 | 인수 기록 확인 대기 |

FUP는 증적 수집용 관리 ID이며 WBS 티켓이나 별도 Change Request를 발행한 것이 아니다.

## 다음 보완 항목

FUP-01은 2026-09-09 Refinalization 원본 수신으로 Rollback 5대와 함께 원본 보완·해시 검증을 완료했다. FUP-02는 2026-09-08 정합성 보완 완료 상태다. 두 항목의 독립 기술 검토와 PR #1 병합은 완료됐다. 새 수신본은 별도 후속 검토로 관리한다. 기존 원본·Manifest와 각 수신회차의 당시 판정은 보존한다.

FUP-04의 원본 보관 위치는 현재 확보 자료만으로 확정할 수 없다. Closure Report만 다시 제출하는 대신 실제 로그·캡처의 보관 위치 또는 파일을 연결한다.

FUP-09는 [Stage A 승인 범위 정정](STAGE_A_APPROVAL_SCOPE_CORRECTION.md)과 [인수 확인 체크리스트](../handoffs/P1-LB-01_STAGE_A_RECEIVER_CHECKLIST.md)를 사용한다. Stage A 기존 PASS와 증적 제출 완료는 유지하며, 인수 기록 확인만 남긴다. 인수자에게 리뷰 요청 메시지를 보내거나 인수 서명을 대신 작성하지 않았다. 기존 SELinux·임시 키 폐기 콘솔 보완은 재제출 요구 대상이 아니다.

## 2026-09-09 병합 후 후속 착수

[PR #1 병합 기록](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5595784292) · [FUP-06/07/08 신규 수신 검토](../receipts/library/20260909T054024Z/RECEIPT_REVIEW.md) · [담당별 실행표](../runbooks/FUP-04-09_POST_MERGE_FOLLOWUP.md). FUP-04/05 및 FUP-09 실제 인수 참조는 이번 조회에서도 미확인이다.

이하 날짜별 수신 기록은 당시 이력이다. 현 상태는 위 표와 신규 수신 검토를 적용한다.

## 2026-09-08 FUP-01/02 우선 보완

- [사용자 제출 기존 종결 증적 수신](../receipts/user-upload/20260908T111104Z/README.md): 원본 `evidence.zip` SHA-256 `915be6e1df8c3718a344b0e07dd69a3e57362684749495f246e964391206e1da`, ZIP CRC·경로 안전성 PASS.
- FUP-02: 제출 ZIP의 P1-ANS 파일 46개 중 기존 Git 수신본 38개가 38/38 동일하다. 05h/05j 승인본 반영 후 구 매니페스트 재생성·검증이 누락된 원인을 확인하고, 구 매니페스트 보존·05j [파일명 Alias](../evidence/P1-ANS-01/remediation-20260908/FILENAME_ALIAS.json)·[신규 수신회차 매니페스트](../evidence/P1-ANS-01/remediation-20260908/DISTRIBUTION_SHA256SUMS)를 등록했다. 과거 서버 검증 완료를 소급 주장하지 않는다.
- FUP-01: Role 정의에서 변경 노드 5대의 원본 경로를 `/var/lib/fds-change/CR-P1-ANS-01-01/original-resolver.json`으로 확정했다. [전용 수집기](../tools/collect-fup-01-02-remediation.py)는 stat/slurp만 사용하며 rollback이나 Runtime 변경을 수행하지 않는다. 첨부 ZIP에는 기대 Refinalization 원본과 Rollback 상태자료가 없어 실제 수령은 계속 대기한다.
- 검증: 로컬 fixture 단위시험 3/3 PASS. 실제 운영 노드 수집은 미실행이다.

## D33 문서 확인 근거

- 파일명: `DEC-P1-MON-01_Notion_Description_UserStory_v1.0.md`
- 문서 내부 Revision: v1.1 / 기준선 v3.1.13
- 저장된 파일 ID: `libfile_bd4195787cbc8191a4ec670936aefa25`, Version 1
- 파일 메타데이터 크기: 11,237 bytes
- 본문 확인: Result PASS, Status Done, Decision APPROVED/D33 Fixed, Completed Date 2026-08-31, Approver 이권욱
- 과거 검증 범위: 전체 본문 193줄 확인 / 당시 원본 미수신. 2026-09-09 후속에서 동일 원본 수신·SHA-256 산출 완료. 신규 원본 편입 독립 검토는 대기.

다운로드 실패는 승인 부재를 뜻하지 않는다. 원본을 다시 생성하거나 읽기 응답을 원본 바이트로 간주하지 않는다.

## 별도 Gate

증적 PR #1은 병합 완료다. 이번 새 수신·관리 변경분은 별도 Draft PR 개설과 독립 검토를 위한 준비본이다. Stage A 실제 인수, OS/Node Gate 및 kubeadm Bootstrap 해제는 자동 완료 처리하지 않는다. 기존 완료 티켓의 Done·종결일은 유지한다.

[이번 수신 검토 상세](../receipts/ansible01/20260907T063705Z/FDS_Ansible_Evidence_Receipt_Review_v1.0.md)

현재 Stage A 판정은 [승인 범위 정정](STAGE_A_APPROVAL_SCOPE_CORRECTION.md)을 따른다. 과거 보고서의 별도 Stage A 최종 승인 대기 표시는 중복 요구로 정정됐다.


## 2026-09-08 PR #4 운영 적용 결과 수신

[운영 적용 원본·검토 시작점](../evidence/P1-ANS-01/pr4-runtime-apply-20260908/README.md) · [운영 이슈 #10](https://github.com/321Team/infra-ansible/issues/10).

- 실행 Run ID: `20260908T102238Z-7dcfedd0`, 종료 2026-09-08 19:26:18 KST.
- 기술 결과: 승인 main을 기존 `~/p1-ans-01`에 동기화, 28개 소스 일치, 기존 증적 등 59개 보존, 6/6 실제 apply·멱등성·신규 SSH 및 OS/DNS 전후 검사 PASS.
- 원본 수신: 외부 sidecar 일치, 내부 55/55 일치, 원본 텍스트 56개 바이트 보존. 원본 압축 패키지는 별도 수신 첨부로 보존.
- 첫 실행의 HTTPS 인증 입력 불가 문제는 이번 실제 fetch 성공으로 해소.
- 비차단 특이사항: SFTP 경고 36건. 실제 작업은 성공했지만 실패 원인과 성공한 전송 방식은 현재 로그로 확정하지 않음. 이슈 #10에서 후속 확인.
- 운영 적용 기술 검토 완료, 이슈의 독립 운영 증적 검토 대기. 기존 PR #4 코드 승인·병합 유지, 본 증적 편입 PR Draft 유지.
- 운영 엔진 2.16.19 유지, Bootstrap HOLD. FUP-01/02의 과거 원본·Manifest 보완을 이번 실행으로 해소 처리하지 않음.



## 2026-09-08 SFTP 후속 수신

[수신 검토와 키트 전송 수정](../evidence/P1-ANS-01/pr4-sftp-followup-20260908/README.md).

- 사용자 실행 20:30:07–20:30:13 KST, 직접 SFTP get 6/6 PASS, 외부 sidecar 일치·내부 25/25·원본 26개 보존.
- 6대 공개키 인증·subsystem 수락·rc=0·다운로드 Hash·키 상태 보존을 원본으로 대조. PR4 최종 키 상태와도 일치.
- 적용 키트 v1.2가 SSH 전용 -T를 SFTP 공통 인자에 전달하는 결함을 로컬 재현하고 v1.3에서 분리 수정. 승인 main 코드 28개는 동일.
- 직접 SFTP 성공과 수정 후 Ansible 업로드 검증은 구분. 당시 대기였던 후자는 아래 21:25 KST 수신에서 6/6 PASS·경고 0건으로 완료했다. 기존 6대 apply 재실행 불필요.
- 이번 수신은 FUP-01/02 보완 상태와 기존 독립 승인·인수·엔진 전환·Bootstrap을 자동 변경하지 않음.

## 2026-09-08 20:51 KST FUP-01 Rollback 원본 수신

- [보완 수신 검토](../receipts/ansible01/20260908T115139Z/FDS_FUP01_Rollback_Receipt_Review_v1.0.md): 외부 sidecar 일치, 내부 6/6, Rollback 상태 5/5 원본 바이트 보존. 원본 CR 파일은 기존 17개에서 상태자료 5개가 추가됐다.
- JSON은 2026-09-04 변경 전 8.8.8.8 상태를 보존한다. 현재 DNS drift나 실제 rollback 실행의 증거로 해석하지 않는다.
- 원격 root:root/0600 및 읽기 전후 불변성은 수집기 보고 기반이다. stat-before/after 원시 출력은 미첨부여서 독립 서버 측정으로 주장하지 않는다.
- Refinalization은 MISSING/matches=0이며 수신 멤버에서도 기대 해시 일치 파일이 없다. 검색 범위 밖 원본의 부재까지 입증한 것은 아니다.
- FUP-01 전체 완료 및 새 Commit의 독립 편입 승인은 계속 대기. FUP-02와 SFTP 등 다른 후속 항목, 기존 Done·승인·Bootstrap 상태는 변경하지 않는다.

## 2026-09-08 21:25 KST Ansible SFTP 수정 후 서버 검증 수신

[검토서·원본 시작점](../evidence/P1-ANS-01/pr4-ansible-sftp-verify-20260908/README.md).

- 원본 SHA-256 `70c16442626426f0c57ab55d402c53fd62799df9cf44621b4831c1f1627d2e30`, 6,335 bytes. 외부 sidecar 일치, 내부 22/22, 원본 23개 보존.
- 수정된 옵션의 실제 SFTP put 6/6 rc=0, ping pong/changed=false 6/6, 임시 모듈 정리 6/6 rc=0, 이번 Ansible 경고 0건. 노드별 SSH 5회·SFTP 1회 전송 명령 모두 rc=0.
- -T 음성 대조는 예상대로 rc=1이며, 실제 SFTP 명령에는 -T가 없다. 이번 성공을 다른 전송 방식 fallback으로 처리하지 않는다.
- 12개 원시 snapshot 대조 및 이전 직접 SFTP 수신 최종 키 상태와 일치. 승인 main/28개 소스·known_hosts 보존은 수집기 검사 성공 보고 기반이며 별도 원시 측정값은 미첨부다.
- SFTP 기술 후속 완료. 운영 이슈 #10의 독립 운영 증적 검토는 대기이며, 기존 전체 apply 재실행·main 코드 수정은 필요하지 않다. 과거 36건 fallback 재구성은 미완료 이력으로 보존한다.
- 이번 수신은 다른 FUP 보완 상태·기존 승인·엔진 전환·Bootstrap을 변경하지 않는다.

## 2026-09-08 Refinalization 전용 후속 준비

- [Refinalization 원본 전용 수집 절차](../runbooks/FUP-01_REFINALIZATION_ONLY.md)와 로컬 Python 수집기를 준비했다. 기존 5대 Rollback 수집기 재실행 없이 명시한 로컬 보관 경로와 압축 내부에서 기대 SHA-256 바이트만 찾는다.
- 승인 대상 Commit의 기대 해시를 재확인했다. 기존 보관 문서 검색에서는 참조 기록만 확인됐고 Refinalization 원본은 확보하지 못했다. 모든 보관소에서 유실됐다는 판정은 아니다.
- 로컬 fixture 10/10 PASS. 원본 바이트·출처·전후 메타데이터·무결성을 보존하며 미발견 시 진단 자료만 생성한다. 서버 실행·원본 수신은 대기다.
- FUP-01/02 상태, 기존 종결·승인·SFTP·Bootstrap 및 증적 PR Draft/미병합 상태는 유지한다.

## 2026-09-08 21:45 KST Refinalization 전용 검색 결과 수신

- [한국어 수신 검토](../receipts/ansible01/20260908T124550Z/FDS_FUP01_Refinalization_Search_Review_v1.0.md): 외부 sidecar 일치, 내부 1/1, 검색 보고서·Manifest 원본 2개 보존. Refinalization 원본은 포함되지 않았다.
- 보고서 상태는 NOT_FOUND_IN_SCOPE, matches=0, issues=0. /home/server01_ansible 및 압축 내부를 지정 필터로 검색했고 숨김·링크 24개, 비대상 62개를 제외했다. 모든 보관소의 유실을 입증하지 않는다.
- 이름 후보 2건은 배포 수집기와 수집기 해시 목록이며 Refinalization 원본이 아니다. 수집기 보고 해시는 배포본과 일치하나 서버 직접 독립 측정 결과로 주장하지 않는다.
- 같은 범위의 재검색·Rollback 재수집은 요구하지 않는다. 당시 작성·다운로드한 원본의 다른 보관 위치 또는 조회 가능한 고정 참조를 먼저 확인한다. 기존 해시 인용문만으로 원본 수신을 대체하지 않는다.
- FUP-01 원본 수신은 계속 대기. FUP-02·기존 종결·승인·SFTP·Bootstrap 및 증적 PR Draft/미병합 상태 유지.


## 2026-09-09 FUP-01 Refinalization 원본 수신 — PASS

[수신 검토](../receipts/ansible01/20260909T003726Z/FDS_FUP01_Refinalization_Receipt_Review_v1.0.md) · [원본](../evidence/CR-P1-ANS-01-01/received-20260909T003726Z/evidence_refinalization.20260904T183221+0900.txt) · [검증 상세](../receipts/ansible01/20260909T003726Z/RECEIPT_VERIFICATION.json).

- 수집 09:37:26 KST, 원본 기록 2026-09-04 18:32:21 KST. 외부 1,773 bytes·sidecar 일치, 내부 2/2, 원본 1,181 bytes의 승인 Hash 일치.
- Index·Manifest·검증 로그 4/4 및 검증 Commit/Tree 일치. 기존 Rollback 5/5 원본 Hash 유지 확인. CR 원본은 총 23개다.
- 이전 홈 검색에서 제외된 `.local/state`의 정확한 파일을 지정해 수신했다. 기존 미발견 기록은 당시 검색 범위의 결과로 보존한다.
- FUP-01: `COLLECTED_VERIFIED_REVIEW_PENDING`. 원본 보완 완료·독립 편입 검토 대기. 기존 Done·승인·FUP-02·다른 Gate는 유지한다.
