# 완료 티켓 증적 공백 기록 — 2026-09-19

조회: 2026-09-19 KST. baseline CLOSED 18건, 증적 대장 v1.7 13건, evidence HEAD `90093f88167055f81e8789d2a848f44ead0ee9ce`.

이 기록은 종결 재오픈·Runtime 재시험·원본 합성 수집이 아니다. 기존 대장의 미수신·NOT VERIFIED 표시를 정리하고, 대장에 없는 CLOSED Decision 위치를 고정한다.

## 1. Decision 5건 — Issue 본문을 결정 증적으로 본다

`tickets/` 사본을 이번에 만들지 않는다. Decision Exit Criteria가 결정 기록이면 baseline Issue 본문·댓글이 증적 위치다. Runtime/Gate 완료로 확대하지 않는다.

| Record ID | Issue | 증적 위치 | `tickets/` 편입 | 비고 |
|---|---|---|---|---|
| DEC-P1-FDS-01 | [baseline#4](https://github.com/321Team/fds-project-baseline/issues/4) | Issue 본문 | 미편입 | 결정 기록 |
| DEC-P1-TXN-01 | [baseline#5](https://github.com/321Team/fds-project-baseline/issues/5) | Issue 본문 | 미편입 | 결정 기록 |
| DEC-P1-ADMIN-01 | [baseline#6](https://github.com/321Team/fds-project-baseline/issues/6) | Issue 본문 | 미편입 | 결정 기록 |
| DEC-CAL-P1-01 | [baseline#28](https://github.com/321Team/fds-project-baseline/issues/28) | Issue 본문 | 미편입 | 주말 작업 결정 |
| DEC-P1-EGRESS-01 | [baseline#78](https://github.com/321Team/fds-project-baseline/issues/78) | Issue 본문·댓글 실측 | 미편입 | Decision Done. #74/#75 Runtime은 별도 |

후속에 Issue 본문을 `tickets/<ID>/`로 복사할지는 별도 편입 PR에서 정한다. 이 기록만으로 13건 대장을 18건 완료 편입으로 바꾸지 않는다.

## 2. 구현 Task — 원본 미수신 (대장 기존 표시 유지)

원본을 이번 수집하지 않았다. 한계를 재확인할 뿐이다.

| 티켓 | Issue | 있는 것 | 없는 것 |
|---|---|---|---|
| D-NET-01 | [baseline#60](https://github.com/321Team/fds-project-baseline/issues/60) | Closure Report | 01~10 원본 로그·캡처, 기존 Manifest |
| P1-LNX-01 | [baseline#66](https://github.com/321Team/fds-project-baseline/issues/66) | D-NET 공통 Closure | Linux Prerequisites 등 실제 원본 |
| P1-NET-01 | [baseline#67](https://github.com/321Team/fds-project-baseline/issues/67) | D-NET 공통 참조 | 원본 로그·캡처. Reviewer/승인자 미입력 |

원본이 없으면 다음은 별도 수집 작업이다. 확보되지 않으면 한계 수용을 별도 편입 PR에서 적는다. 이 기록으로 한계 수용을 선언하지 않는다.

## 3. NOT VERIFIED 유지 (재검사 안 함)

| 티켓 | 유지 항목 |
|---|---|
| P1-DNS-01 | 동립 리뷰의 원본 ZIP 외부 대조 |
| P1-ANS-01 | 구 Manifest 불일치 이력, Reviewer/Approver 겸임 관찰 |
| CR-P1-ANS-01-01 | 서버 보관 메타데이터 등 동립 리뷰 NOT VERIFIED |

## 4. 완료가 아닌 항목 (혼동 방지)

- [evidence#8](https://github.com/321Team/fds-project-evidence/issues/8) P1-DB-01 — OPEN
- [evidence#4](https://github.com/321Team/fds-project-evidence/issues/4) FUP-04/05/09 — OPEN
- baseline #74/#75 — OPEN. #78 Done과 분리
