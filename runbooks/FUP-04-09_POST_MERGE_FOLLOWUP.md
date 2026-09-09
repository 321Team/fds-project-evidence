# FUP-04~09 병합 후 실행표 v1.1

기준일: 2026-09-09. [PR #3 병합·FUP-09 정정 근거](../records/post-merge-20260909/PR3_CLOSURE_AND_FUP09_CORRECTION.md) / [현재 추적 이슈](https://github.com/321Team/fds-project-evidence/issues/4). 목적은 기존 증적의 수신·식별·인수 참조 연결이다. 기존 완료 티켓은 유지한다.

| 항목 | 이번에 수행한 일 | 다음 완료 조건 | 확인 주체 |
|---|---|---|---|
| FUP-04 | 기존 저장소·보관 문서에서 공통 원본 Index 01~10 재확인. 이번 검색에서 실제 로그 묶음 미확보 | 기존 `docs/evidence/D-NET-01/`의 실제 보관 위치 또는 원본 로그·캡처·기존 Manifest 수신 | 이권욱: 보관 위치 확인·수신 조정 |
| FUP-05 | 종결 기록의 Reviewer/Approver 미입력 확인 | 당시 검토자·승인자·일시·범위를 확인할 원본 또는 고정 링크 연결 | 이권욱: 기존 승인 참조 확인·조정. 과거 승인자는 확인 전 미지정 |
| FUP-06 | 후보 원본 수신·독립 APPROVED·사용자 수용·PR #3 병합 | 과거 승인 참조 추후 연결; 후보 편입은 완료 | 이권욱: 출처 확인 / 새 보완분 이재환 검토 |
| FUP-07 | WBS 참조 수신·독립 APPROVED·사용자 수용·PR #3 병합 | 과거 승인 참조·검토자 원본 접근 확인 | 이권욱: 출처·접근 조정 |
| FUP-08 | 원본 수신·독립 APPROVED·PR #3 병합 | 이번 원본 수신·편입 보완 종결 | 추가 리뷰 요청 없음 |
| FUP-09 | [기존 조건부 인수](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5582767564) 확인, 보존본 28/28 동일 | IP 중복검사 원본·Permanent 출력의 기존 승인 근거 참조 | 이하영: 조건 확인 / 이권욱: 자료 연결 |

## FUP-04 제출 대상

기존 기록에 명시된 Index는 다음과 같다. 보관 위치가 확인되면 기존 원본을 보존해 제출한다. 현재 상태로 재실행해 만든 로그를 과거 증적으로 대체하지 않는다.

1. `01_Windows_PostBuild_server01-08`
2. `02_VMware_Virtual_Network_Editor`
3. `03_Linux_Node_Network_Verify`
4. `04_K8s_Linux_Prerequisites`
5. `05_Physical_Return_Route`
6. `06_Source_Preservation_PASS6`
7. `07_Management_VM_Verify`
8. `08_mgmt-gw01_Verify`
9. `09_DO_NOT_USE_IP_Exception`
10. `10_D-NET-01_Closure`

D-NET/P1-NET/P1-LNX 공통 원본은 한 번 수신하고 티켓에서 참조한다. Closure Report의 PASS 요약만으로 실제 로그·캡처를 수신했다고 표시하지 않는다. 보관 위치를 모르면 위치 미확인으로 남긴다.

## 후속 처리 순서

1. [이슈 #4](https://github.com/321Team/fds-project-evidence/issues/4)에서 이번 인수 기록 정정과 남은 원본·참조 수신을 추적한다.
2. FUP-04/05는 기존 원본 또는 승인 링크를 확보한 항목부터 수신한다. 점검한 D-NET Final ZIP은 문서 7개만 포함하며 실제 로그는 없다.
3. FUP-09는 [기존 인수 참조 및 잔여 조건 양식](../handoffs/FUP-09_RECEIPT_REFERENCE_FORM.md)에 미포함 2개 항목의 근거만 연결한다.
4. 이미 APPROVED·병합된 FUP-06/07/08을 같은 범위로 재검토 요청하지 않는다. 새 보완·정정 변경분은 별도 독립 검토한다.

팀원에게 별도 Slack·이메일·개별 인수 요청은 전송하지 않았다. 기존 실제 회신을 연결했으며 인수 서명을 대필하지 않았다. Bootstrap 실행·엔진 변경·서버 apply/rollback은 수행하지 않는다.
