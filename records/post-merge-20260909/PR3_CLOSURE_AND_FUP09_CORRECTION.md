# PR #3 병합 완료와 FUP-09 인수 기록 정정

기록일: 2026-09-09. 후속 추적: [이슈 #4](https://github.com/321Team/fds-project-evidence/issues/4). 이 문서의 새 정정 편입은 독립 검토 대기다.

## PR #3 병합

- 검토 HEAD: `00d1080a1c8f44b133eef81dd2b58be31bf86d9d`
- 병합 Commit: `39ead0567327cf45ed9f8b81cecdf9848f542d5d` / 2026-09-09 15:36:13 KST
- [독립 APPROVED·사람 확인 CONFIRMED](https://github.com/321Team/fds-project-evidence/pull/3#pullrequestreview-5150486987) 및 [사용자의 후보·대기 편입·출처 한계 수용과 병합 승인](https://github.com/321Team/fds-project-evidence/pull/3#issuecomment-5597170385)
- 병합 Tree `6562dcf582620f8fc49dd1d60e68e5b10d8663b0`가 검토 Tree와 같고 418개 파일이 그대로 보존됐다. main 조회도 병합 Commit과 일치했다.
- FUP-08 원본 수신·독립 검토·편입 완료. FUP-06/07의 후보 편입 수용은 완료됐으나 과거 승인 참조·다른 팀원 원본 접근의 미검증은 유지한다.

## FUP-09 정정

[이하영의 2026-09-08 회신](https://github.com/321Team/fds-project-evidence/pull/1#issuecomment-5582767564)에는 원본 21개와 콘솔 보완 3건 확인 및 **Stage A 증적 조건부 인수**가 명시돼 있다. 이전 관리 문서·안내와 PR #3 검토에 남아 있던 “인수 기록 미확인”은 해당 회신을 반영하지 못한 표기이므로 정정한다. 기존 리뷰 원문과 수신 원본은 수정하지 않는다.

| 항목 | 확인된 원문 또는 검증 |
|---|---|
| 인수자 | 이하영 / hayeounglee |
| 실제 검토 Commit으로 기재된 값 | `7dfec0a042c6f833cb246bb89560ec3eb0af892b` |
| 검토 일시 | 본문은 2026-09-08만 기재. 정확한 시각·시간대는 미기재 |
| GitHub 게시 시각 | 2026-09-08 18:33:45 KST / 09:33:45 UTC. 실제 검토 시각을 대신하지 않음 |
| 인수 범위 | 원본 21개(01~18c) 및 LB-HO-OBS-01/02/03 콘솔 보완 3건 |
| 인수 결과 | 조건부 인수 |
| 미포함·잔여 조건 | LB-A-01 IP 중복검사 원본, firewalld Permanent 출력의 기존 승인 근거 참조 확인 |
| 현재 보존본 연결 | 기재 Commit 대비 병합본 Stage A 경로 28/28 Git blob·mode 동일, 추가·삭제 0 |

회신에 현재 HEAD 재확인 안내 문구가 남아 있으므로 기재된 Commit을 임의로 새 HEAD로 교체하지 않는다. 이번 대조는 그 Commit의 Stage A 자료가 현재 보존본과 동일함을 확인한 것이다. 수신 묶음 Hash 대조 완료는 인수자가 보고한 검토 결과이며 이번에 서버 측 검증을 재수행하지 않았다.

조건부 인수는 무조건 인수 완료가 아니다. 과거 IP 중복검사·Permanent 출력의 참조를 먼저 연결하고, 신규 확인이 필요할 때만 별도 시각의 Supplement로 구분한다. 기존 21개 원본과 콘솔 보완 3건, Stage A PASS는 재제출·재승인 대상이 아니다. OS/Node Gate와 Bootstrap HOLD는 별도다.

## FUP-04 추가 보관본 점검

기존 `D-NET-01_Final_v1.0.zip`을 수신해 ZIP CRC와 전체 멤버 목록을 확인했다. 18,691 bytes, SHA-256 `e121b166c6e3e3c67ac489cd3cb277015a4630aff61ea0e0d070471026b66bfc`. 패키지는 README·설계·기준선·종결·Notion 반영 문서 7개로 구성되며 Index 01~10의 실제 로그·캡처·기존 Manifest는 들어 있지 않다. 종결 보고서의 PASS 요약을 원본 로그로 취급하지 않는다. 실제 원본 보관 위치는 계속 확인 대기다.

이 점검으로 모든 보관소에서 원본이 없다고 단정하지 않는다. 새로 수신한 ZIP은 기존 별도 보관본으로 유지하고 Git에 바이너리를 추가하지 않는다.

[조회 원문·대조 및 압축 목록](FUP09_SOURCE_AND_FUP04_SEARCH.json)
