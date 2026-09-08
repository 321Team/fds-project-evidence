# 후속 증적 수신·인수 대장 v1.2

기준일: 2026-09-07. infra-ansible PR #1은 최종 승인·병합 완료다. 아래 항목은 기존 완료 티켓의 재구현이 아닌 증적 수신·편입 및 실제 인수 절차로 관리한다.

| ID | 대상 | 이번 조치 | 다음 수신·확인 항목 | 상태 |
|---|---|---|---|---|
| FUP-01 | CR-P1-ANS-01-01 | 17개 수신·기존 Manifest 16/16·주요 Hash 4/4 일치 | Refinalization 원본 및 변경 Node 5대 Rollback 상태자료·보관 증명 | 부분 수신·보완 대기 |
| FUP-02 | P1-ANS-01 | 38개 원본 수신, 35/37 일치 | 05h/05j Hash 불일치 원인·승인본 이력, 05j 파일명 정합성, 새 배포회차 검증 | 수신 완료·정합성 보완 |
| FUP-03 | P1-DNS-01 | ZIP·Sidecar 수신, 기록 Hash·내부 12/12·개별 Sidecar 11/11 일치 | 독립 편입 검토. 원본 재제출·ZIP 재생성 불필요 | 원본 수신 검증 완료 |
| FUP-04 | D-NET-01/P1-NET-01/P1-LNX-01 | 공통 원본은 한 번 수집하도록 유지 | 인덱스 01~10 중 미수신 Windows/VMware/Linux/Return Route/Source Preservation 로그·캡처·기존 Manifest. 실제 보관 위치 확인 필요 | 원본 수신 대기 |
| FUP-05 | P1-NET-01 | Reviewer/Approver 미입력 상태 유지 | 실제 검토자·승인자·일시를 확인할 원본 또는 고정 참조 | 참조 확인 대기 |
| FUP-06 | D-ARC-01 | v3.1.2 논리·물리 도면 후보를 찾음 | 같은 이름의 원본·Final 패키지 후보가 있어 동결 당시 승인 대상과 참조를 먼저 확정 | 승인본 식별 대기 |
| FUP-07 | D-WBS-01 | 종결 설명 v1.1 및 후속 v1.2 후보 확인 | 동결 당시 WBS와 승인 기록의 고정 참조. 최신 WBS를 과거 승인본으로 대체하지 않음 | 참조 확인 대기 |
| FUP-08 | DEC-P1-MON-01/D33 | 개별 문서 본문에서 승인·완료 기록 확인 | 원본 바이트 다운로드가 HTTP 502로 실패해 원본 수신·Hash 확인은 미완료 | 내용 확인 / 원본 수신 대기 |
| FUP-09 | P1-LB-01 Stage A | D36 승인정본과 CR 리뷰의 Stage A PASS 유지·증적 제출 완료 | 이하영 증적 인수 여부를 확인할 범위·일시·참조 연결. Stage A PASS 재승인 요구 없음 | 인수 기록 확인 대기 |

FUP는 증적 수집용 관리 ID이며 WBS 티켓이나 별도 Change Request를 발행한 것이 아니다.

## 다음 보완 항목

FUP-01~03 수집은 실행·수신됐다. 전체 수집기를 재실행할 필요는 없으며 FUP-01/02의 확인·보완 자료만 새 수신회차로 제출한다. 기존 원본·Manifest를 보존하고 불일치 원인을 먼저 확인한다. 원본 수신 검증과 독립 인수 승인은 분리한다.

FUP-04의 원본 보관 위치는 현재 확보 자료만으로 확정할 수 없다. Closure Report만 다시 제출하는 대신 실제 로그·캡처의 보관 위치 또는 파일을 연결한다.

FUP-09는 [Stage A 승인 범위 정정](STAGE_A_APPROVAL_SCOPE_CORRECTION.md)과 [인수 확인 체크리스트](../handoffs/P1-LB-01_STAGE_A_RECEIVER_CHECKLIST.md)를 사용한다. Stage A 기존 PASS와 증적 제출 완료는 유지하며, 인수 기록 확인만 남긴다. 인수자에게 리뷰 요청 메시지를 보내거나 인수 서명을 대신 작성하지 않았다. 기존 SELinux·임시 키 폐기 콘솔 보완은 재제출 요구 대상이 아니다.

## D33 문서 확인 근거

- 파일명: `DEC-P1-MON-01_Notion_Description_UserStory_v1.0.md`
- 문서 내부 Revision: v1.1 / 기준선 v3.1.13
- 저장된 파일 ID: `libfile_bd4195787cbc8191a4ec670936aefa25`, Version 1
- 파일 메타데이터 크기: 11,237 bytes
- 본문 확인: Result PASS, Status Done, Decision APPROVED/D33 Fixed, Completed Date 2026-08-31, Approver 이권욱
- 검증 범위: 전체 본문 193줄 확인. 원본 바이트 수신·Hash 검증·저장소 원본 편입은 아직 수행하지 않음

다운로드 실패는 승인 부재를 뜻하지 않는다. 원본을 다시 생성하거나 읽기 응답을 원본 바이트로 간주하지 않는다.

## 별도 Gate

증적 PR은 Draft / 독립 검토 대기다. 증적 편입 main 병합, Stage A 실제 인수, OS/Node Gate 및 kubeadm Bootstrap 해제는 자동 완료 처리하지 않는다. 기존 완료 티켓의 Done·종결일은 유지한다.

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
