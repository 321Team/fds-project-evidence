# P1-HBR-01 — HBR Lead Runtime 증적 2차 편입 (2026-10-04)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 수집·실행: 이하영(HBR Lead). 원본 전사·정리: Claude Code(CLAUDE_ASSISTED). 앞선 1차 편입은 [`../lead-runtime-20260930-20261002/`](../lead-runtime-20260930-20261002/README.md)(PR #106 병합)이며 이 폴더는 그 이후 새 수집회차다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. 이 편입은 AC PASS 선언이 아니다.

| 하위 폴더 | 내용 | 대응 |
|---|---|---|
| [`ac01-tls-negative-20261004/`](ac01-tls-negative-20261004/README.md) | TLS 복구 이후 Runner의 잘못된 CA 거부(curl Exit Code 60) 재실행, 정상 CA health 8개 구성요소 healthy | AC-01, 핵심요구 1·4(복구 후 증적) |
| [`ac04-preapply-20261004/`](ac04-preapply-20261004/README.md) | PR #63 `f222f1f` 정적 검증 11/11과 읽기 전용 사전 점검 `PRECHECK_PASS_RUNTIME_NOT_CHANGED` | AC-04 적용 전 |
| [`ac04-before-reach-20261004/`](ac04-before-reach-20261004/README.md) | 적용 전 도달성: Runner 443 OPEN, ansible01 이미 BLOCKED(관리망 상류 통제로 보이며 호스트 방화벽 증거 아님), harbor01 proxy.log의 same-L2 `.26/.30` HTTP 200 | AC-04 적용 전 기준 |

## 한계와 주의
- **AC-04는 아직 적용 전이다.** 이 폴더는 적용 전 기준선이며 AC-04 PASS가 아니다. 적용 후 증적(허용·비승인 시험, persistence, rollback)은 별도 회차로 편입한다.
- `ac04-before-reach-20261004`의 세 관측은 터미널 출력 전사이며 서버 해시 대조는 없다(소량 텍스트).
- `ac01-tls-negative`의 서버 원본(CR 포함, sha256 `0fcf5fb2…e306`)은 PC에 없고 `tr '\r' '\n'` 정리본만 있다.
- 비밀정보 검색(`password|secret|token|BEGIN … KEY`) 결과 없음.
- 작성자·AI 자체 검수이며 독립 리뷰 완료가 아니다.
