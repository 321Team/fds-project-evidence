# FUP-06/07/08 원본 수신 검토 v1.0

기준일: 2026-09-09. 상태: 원본 수신·후속 편입 후보 작성 / 독립 검토 PENDING.

| 대상 | 파일 | Bytes | 수신 SHA-256 | Git 등록 |
|---|---|---:|---|---|
| FUP-08 | `DEC-P1-MON-01_Notion_Description_UserStory_v1.0.md` | 11,237 | `c255622b357cfdbdb4dd5880fa12e163ae80f4996a7d14c92c78159024447699` | 원본 텍스트 등록 |
| FUP-06 | `FDS_Phase1_Physical_Architecture_v3.1.2.mmd` | 1,909 | `e90515a94b2a0864ef5b86e47c15565273cf021765cb71225a4bf7e55f7ddef2` | 원본 텍스트 등록 |
| FUP-06 | `FDS_Phase1_Logical_Architecture_v3.1.2.mmd` | 2,640 | `144f747aa7f8cdeb2a9edde4ebb4a4c77e4302fe5756f2567f8ec71c046dc16c` | 원본 텍스트 등록 |
| FUP-07 | `FDS_Remaining_Backlog_WBS_v3.1.3.xlsx` | 34,288 | `07f0dadc85551ec88edafbb16d7a22a1c3b111efd32ceb2612b3f90fb1c557ec` | 별도 보관·참조 등록 |

## 확인 결과

- FUP-08: 과거 다운로드가 실패했던 동일 파일 ID의 Version 1 원본을 정상 수신했다. 11,237 bytes, Revision v1.1, D33 Fixed/Done, 2026-08-31, Approver 이권욱 표기가 기존 수신 대장의 내용 확인과 일치한다. 설계 완료와 P1-MON-01 Runtime을 구분한다.
- FUP-06: 논리·물리 원본 2개에 Release v3.1.2, Freeze Ticket D-ARC-01, Freeze Date 2026-08-26, APPROVED/DONE이 있다. 기존 `records/received-20260907/FDS_Notion_Closed_Descriptions_D-ARC-01_D-NET-01_D-WBS-01_v1.1.md`의 파일명·메타데이터 조건과 일치한다. `D-NET-01_Final_v1.0`의 동명 파일은 Freeze 머리말이 없고 크기도 다르므로 별도 후보로 구분했다. 이번 원본을 현재 아키텍처 정본으로 지정하지 않는다.
- FUP-07: 종결 설명이 지정한 `FDS_Remaining_Backlog_WBS_v3.1.3.xlsx` 원본을 수신하고 ZIP CRC를 검사했다. Library의 Overview/Closed Register 내용 조회에는 2026-08-26 공통 검토와 WBS 관리체계 Freeze 및 v3.1.3 갱신이 있다. 최초 동결 바이트와 동일함을 증명한 것은 아니다. 원본 바이너리는 기존 별도 보관본을 유지하며 Git에는 Hash·식별자를 연결한다.

## 검증 범위와 한계

수신 4개 모두 메타데이터 크기와 실제 바이트 수가 일치하고 SHA-256을 산출했다. Git에 등록할 텍스트 3개는 수신 바이트와 동일하다. 과거 배포 Manifest/승인 Hash는 확보되지 않았으므로 과거 원본 무결성 대조는 NOT VERIFIED다. WBS 전체 셀·수식, 기존 설계의 기술 적합성, 서버 상태를 재시험하지 않았다.

FUP-06/07의 정확한 승인 참조 연결과 새 파일·수신 기록의 독립 편입 검토는 계속 대기한다. FUP-08은 원본 미수신에서 수신 완료·독립 편입 검토 대기로 진전됐다. 이 기록으로 사람의 승인·인수 서명을 생성하지 않는다.

[원본 매핑](SOURCE_FILE_MAP.json) · [이번 등록 체크섬](SHA256SUMS) · [후속 실행표](../../../runbooks/FUP-04-09_POST_MERGE_FOLLOWUP.md)
