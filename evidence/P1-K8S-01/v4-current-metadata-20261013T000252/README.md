# K8S Phase 1 현행 읽기 — 2026-10-13 KST

이권욱 / CODEX_ASSISTED. 5호스트 45파일 모두 이전 해시와 같다. 교체 17개 / 보존 28개를 유지한다. 승인 source와 현행 main의 각 9개, 총 18개 blob이 고정 계획과 일치한다. 파일·ACL·context 변경, 서버 backup·restore·동시 호출 배제는 미실행이다. control02는 제외한다.

[통합 판단·실행 순서·남은 입력](../../../records/p1-independent-readiness-20261013.md).

## 출처와 검증 범위

사용자 “권장 순서대로 착수”에 따른 기존 정상 접근의 읽기다. 새 정책·서비스·DNS·앱 변경이나 credential 발급은 없다. SSH·sudo·감사 접근 흔적까지 0이라고 주장하지 않는다.

receipts의 collector.py는 실제 stdin 실행 바이트, stdout.json/stderr.txt는 수신 바이트 그대로다. receipt.json에는 호스트 route·명령·시각·종료코드·수신 hash가 있다. RUNNER는 REST 메타데이터 projection으로 기록했다. HA/OID의 응답 원문 전체는 영구 보존하지 않았으며 검증된 projection과 내부 응답 hash만 남는다. 폐기한 원문을 hash로 복원할 수 없다. 비밀키·token·암호·Secret/ConfigMap 객체값은 편입하지 않는다.

OID의 검토된 원 수집기를 제외한 이번 순수 읽기 collector/전달 wrapper는 **REVIEW=NOT PERFORMED (Pre-check)**다. 자체 수신 검수는 독립 리뷰가 아니다. RUNTIME은 명시된 읽기만 실행했고 AC 판정·티켓 상태·기존 완료일은 변경하지 않았다. 증적 편입 REVIEW/MERGE는 이 PR에서 별도로 진행한다.

SHA256SUMS는 이번 폴더의 수신 바이트·새 분석/설명에 대한 무결성 대장이다. 과거 서버 Manifest나 시험 PASS를 대신하지 않는다. 기존 봉인 회차를 수정하지 않았다.
