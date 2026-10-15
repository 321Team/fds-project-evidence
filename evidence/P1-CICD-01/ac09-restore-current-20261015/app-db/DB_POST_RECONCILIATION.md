# AC09 APP DB 사후 대조 보완

2026-10-15 16:30 KST · CODEX_ASSISTED · 새16:22:17 DB 원문과 이미 확보한 실제 R1/R2 API 입력·응답만 대조했다.

**R1 이전 이미지와 R2 현행 이미지에서 보낸 정상 입금 각1건의 동일 Transaction ID DB 저장 내용이 모두 일치한다. 기존 APP 대조표의 DB 사후행 미확인2건은 해소됐다.** 이전에 확인한 HTTP/FDS·같은 Pod 계측 결과는 그대로 재사용한다. 전체 Rule/이력 쿼리·외부 Client 경로·SEC 시한·AC09 최종 인수를 새로 완료 선언하지 않는다.

## 1. 이번 원본과 무결성

중앙이 보존한 사용자 콘솔 [전체 원문](references/USER_CONSOLE_OUTPUT.txt)을 별도 경로에 그대로 복사했다. provenance는 **사용자 제공 db01 정상 콘솔 텍스트**이며 APP가 새로 DB에 접속한 결과가 아니다.

- 콘솔: db01 / server08. DB: fdsdb / postgres, TimeZone Asia/Seoul, transaction_read_only=on.
- DB 시각: `2026-10-15T16:22:17.634935+09:00`. start/end 파일 모두16:22:17, rc0, stderr0바이트.
- 텍스트에서 literal 파일6개를 분리했고, 재결합 시 원문 데이터 구간과 정확히 같다. 공백·줄바꿈·JSON 직렬화는 변경하지 않았다.
- **host/start/db-after JSONL/stderr/rc/end 6개와 고정SQL1개, 총7개 SHA256 모두 보고값과 일치.** DB JSONL SHA256=`993b2e9588945e1e31551e61c94788756b7356670a475cca7cb88acf22d83a4f`.
- SQL SHA256=`8bb9b1c3d32fea5c821064547341b369aebae6a0b8b3de6606a743dd8ff3694c`. 전체 콘솔 원문 SHA256=`272dc9b5eb08fc581822369eebd95932bd70bd195432d8109d964a716b0bdd83`.

파일별 실제값과 비교 결과는 [DB_APP_COMPARISON.json](DB_APP_COMPARISON.json), [출처 목록](SOURCE_INDEX.json), [분리한 원문](references/literal-files/)에 있다. 중앙의 판정 JSON을 그대로 결론으로 복제하지 않고 새 콘솔 원문과 실제 API body를 독립 파싱·대조했다. 해시 일치는 전달 무결성이며 업무 값 대조 결과와 구분한다.

## 2. 실제 API → DB 값 대조

| 항목 | R1 이전 이미지 | R2 현행 복원 |
|---|---|---|
| transaction_id | `22b7c46c-cd07-4539-a7fc-8890b67b12ee` | `1827bd8a-a921-49f9-83f7-22529e903451` |
| 계정·ID 조건으로 찾은 행수 | 1 | 1 |
| 계정·금액·통화·유형·IP | 실제 payload와 모두 일치 | 실제 payload와 모두 일치 |
| occurred_at | UTC입력06:48:17.993816 = DB15:48:17.993816+09 | 입력·DB15:56:28.439537+09 동일 |
| transaction_id·detected·skipped·rules | 응답과 모두 일치 | 응답과 모두 일치 |
| received_at | 15:48:19.508568+09 관측 | 15:56:29.942495+09 관측 |

각 account는 각각 `SIM_ac09_cd01e613d57641eb83548e9283d0f60d_P01`, `SIM_ac09_3451e56c57bc490e8d156cede958229f_P01`이다. amount10000/currencyKRW/deposit/source_ip198.51.100.10, detected=false, skipped=false, R01/R02/R04/R07 네 Rule의 triggered=false/detail=null을 확인했다. JSONB 객체의 키 출력 순서는 의미가 같으면 차이로 만들지 않았다.

기존11열 중 **입력/응답에 대응하는10필드는 직접 비교**했고, `received_at`은 DB만의 필드로 분리했다. 두 값은 기록된 HTTP 시작~종료 범위 안에 있지만 이는 관측 사실이다. 새로운 clock/latency 합격기준이나 호스트 시계 정확성 증명으로 사용하지 않는다.

정확 계정 OR 실제 Transaction ID로 조회했으므로 같은 계정의 복수행이나 잘못 저장된 계정 값을 숨기는 필터가 아니다. 조회 시점에는 각1행이다. 이것으로 과거 사전0행까지 소급 증명하지 않는다.

## 3. 사전0행 미수집의 분류

**이번에 고정 승인된 최종 카드 기준으로는 새 차단사항이 아니라 보존할 이력상 한계다.** 다음 문서·승인 바이트를 대조한 한정 판단이며, 프로젝트 전체의 다른 기준을 바꾸는 결정이 아니다.

| 근거 | 실제 문구·적용 범위 |
|---|---|
| 초기 미승인 [EXECUTION_CARD](references/EARLIER_UNAPPROVED_EXECUTION_CARD.md) §3·§5 | `PREPARED / INPUT_REVIEW_PENDING / RUNTIME_NOT_AUTHORIZED` 후보에서 “DB catalog/시험 계정0행”, “이전0행·이후1행”을 제안했다. 이 문구의 존재와 실제 미수집을 숨기지 않는다 |
| 실제 사용자 [승인 기록](references/AC09_USER_AUTHORIZATION_1535.json) | “제시한 실행·복구 범위 승인”. 최종 결정 카드 SHA `7bdad3c96100c578ac80ba7ab450dcfa971b37ca719003fbea4bd5cc43222a34`와 상세 카드 SHA `cda3353af5f5894f6c9a01b1094f79d534f4f71cf2d48ee2773492c4a2986786`를 고정했다. 두 파일의 현재 바이트가 이 값과 일치함을 확인했다 |
| 승인된 [최종 상세 카드](references/FINAL_OPERATOR_CARD.md) §1 | “APP14:00 DB 정적 진입조건 충족 유지. 추가SQL·migration·DB재인수 요청 없음.” |
| 같은 카드 §3의 3번·5번 | R1은 “P01deposit1건·동일ID DB/동일Pod계측 대조”, R2는 “현행P01deposit1건/동일ID DB·계측 대조”를 요구한다. 사전0행 재조회를 필수 진입조건으로 채택하지 않았다 |
| 승인된 [최종 결정 카드](references/FINAL_DECISION_CARD.md)의 정상 범위 | 단계별 입금 POST1, 합계최대2이며 timeout/응답 유실 시 재POST 없이 동일ID 결과를 기존 읽기 경로로 판정한다. 추가 사전0행 Gate는 없다 |
| 실제 실행 기록 | R1/R2 `post-attempt.json` 모두 `db_before=NOT_COLLECTED_NORMAL_DB_CONSOLE_ONLY`. [R1](references/r1-post-attempt.json), [R2](references/r2-post-attempt.json) |

따라서 **초기 준비안의 미채택 사전0행 절차를 이번 최종 승인 카드의 미충족 필수조건으로 재도입하지 않는다.** 사전0행이 성공했다거나 면제 승인을 새로 받았다고 표시하지도 않는다. 해당 과거 증적은 지금 다시 읽어 재현할 수 없으므로 “미수집·소급 미입증”으로 남긴다. 별도 DB 재시험·추가 POST·기존 DB #11 재인수는 필요하지 않다.

이번에 채택된 동일ID DB 사후 대조는 두 단계 모두 충족했다. 실제 Runtime 표본은 여전히 정상 deposit 각1건으로 한정되며, deposit이 실행하지 않는 withdrawal/transfer 이력 SELECT·모든 Rule 경계까지 검증했다고 하지 않는다.

## 4. 인계와 변경 경계

- 보완 판정: **두 단계의 최소 정상 거래에 대해 HTTP/FDS → 실제 DB 저장 연결 확인 완료**. 기존 metrics 분석을 반복하지 않고 연결한다.
- 16:22:17은 후속 DB 읽기/증적 보완 시각이며 실제 POST 시각이나 Deploy/노출 시한을 바꾸지 않는다. 시한 증거와 SEC 사후 판단은 기존 별도 결과를 유지한다.
- 중앙은 이 보완 결과를 기존 허용 범위의 infra-cicd #11 기록에 연결한다. APP는 외부 댓글·원격 상태/인수/종결을 수행하지 않았다.
- 봉인된 CICD runtime-1535의 EVIDENCE_MANIFEST 및446파일과 기존 APP 대조표/원문은 변경하지 않았다. 이 별도 후속 경로와 APP_E2E_STATUS만 갱신한다.
- 새 SQL/POST/서버 관측·연결0. 기존 전체 catalog·계측 검사를 반복하지 않았다. 새 사용자 질문도 없다.

이 보완으로 DB 행 미확인 항목은 닫을 수 있으나, AC09 전체 완료·독립 리뷰·최종 인수와 SEC 판단을 대신하지 않는다.
