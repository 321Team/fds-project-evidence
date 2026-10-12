# HA Phase 1 현행 읽기 — 2026-10-13 KST

이권욱 / CODEX_ASSISTED. control01 API GET 9종이 rc0으로 끝났다. 두 앱 Pod 6개와 ready endpoint는 모두 worker02에 있다. 10/7 서버 YAML의 선택된 spec 필드와 차이는 0이다. 집중 원인·현재 HTTP/Drain 결과는 미확인이다. 현재 전체 HA/Exit 인수를 하지 않으며 10/2 제한 수용을 보존한다.

[통합 판단·실행 순서·남은 입력](../../../records/p1-independent-readiness-20261013.md).

## 출처와 검증 범위

사용자 “권장 순서대로 착수”에 따른 기존 정상 접근의 읽기다. 새 정책·서비스·DNS·앱 변경이나 credential 발급은 없다. SSH·sudo·감사 접근 흔적까지 0이라고 주장하지 않는다.

receipts의 collector.py는 실제 stdin 실행 바이트, stdout.json/stderr.txt는 수신 바이트 그대로다. receipt.json에는 호스트 route·명령·시각·종료코드·수신 hash가 있다. RUNNER는 REST 메타데이터 projection으로 기록했다. HA/OID의 응답 원문 전체는 영구 보존하지 않았으며 검증된 projection과 내부 응답 hash만 남는다. 폐기한 원문을 hash로 복원할 수 없다. 비밀키·token·암호·Secret/ConfigMap 객체값은 편입하지 않는다.

OID의 검토된 원 수집기를 제외한 이번 순수 읽기 collector/전달 wrapper는 **REVIEW=NOT PERFORMED (Pre-check)**다. 자체 수신 검수는 독립 리뷰가 아니다. RUNTIME은 명시된 읽기만 실행했고 AC 판정·티켓 상태·기존 완료일은 변경하지 않았다. 증적 편입 REVIEW/MERGE는 이 PR에서 별도로 진행한다.

SHA256SUMS는 이번 폴더의 수신 바이트·새 분석/설명에 대한 무결성 대장이다. 과거 서버 Manifest나 시험 PASS를 대신하지 않는다. 기존 봉인 회차를 수정하지 않았다.
