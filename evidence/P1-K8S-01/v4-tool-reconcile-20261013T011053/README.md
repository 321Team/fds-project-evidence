# P1-K8S-01 — K8S17 실제 파일 교체 증적

2026-10-13 KST / 이권욱 / CODEX_ASSISTED. 교체17·보존28·5대. [결과·검증 한계·다음 순서](../../../records/p1-k8s17-reconcile-20261013.md).

`*-prepare`, `*-apply`, `*-independent` 각5개와 control01-runtime-sanity1개, 총16개 영수증을 바이트 그대로 보존했다. 실행 source·SSH 명령·rc·수신 시각·서버 시각·원본 출력의 SHA가 연결된다. 별도 읽기는 독립 사람 리뷰가 아니다. INPUT은 앞선 공급 준비 입력의 바이트 사본이다.

이번 helper는 별도 독립 코드 리뷰를 받지 않았다. 운영 도구 호출·정책 Runtime·AC 인수 미실행. 서버 임시 복원 대조는 실제 수행했고 실패 복귀는 미발생. REVIEW/MERGE는 PR208을 따른다. 실행 collector와 dispatcher는 기록이므로 재실행하지 않는다. dispatch.py의 이전 공급 디렉터리 참조는 당시 로컬 환경이며 배포 패키지가 아니다.

읽기 전용 로컬 검증: `python3 verify_results.py <수집회차 경로>` (명시적 경로 인자를 주면 결과 파일을 다시 쓰지 않음). SHA256SUMS는 이 폴더 전체 편입 무결성 기준이다. API 수집은 전체 응답이 아닌 선택 필드·응답 SHA를 보존한다. credential 내용은 포함하지 않는다. 서명이나 신뢰된 시각 증명으로 확대하지 않는다.
