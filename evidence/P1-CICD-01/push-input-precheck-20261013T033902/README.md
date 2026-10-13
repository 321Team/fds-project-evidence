# Phase 1 Push 입력·원본 사전점검

2026-10-13 / CODEX_ASSISTED / 이권욱.
[결과·검증 한계·다음 단계](../../../records/p1-push-input-precheck-20261013.md).
push.draft.json은 실행 불가 초안이다. 원본 영수증3개·OCI2개·기존 보고서2개를 Runner에서 읽어 대조했으며, 새 Scan/Push/Deploy와 구분한다.
GitHub Secret 이름·등록시각만 포함하며 비밀값은 없다. 원 Scan 보고서 전체는 반출하지 않았다.
source는 고정 main 바이트이며 실행기 변경이 아니다. runtime-read는 실제 읽기 원본이고, prepare/collect/runner_read/build_input은 작업 추적용으로 무조건 재실행하는 카드가 아니다.
읽기 전용 재검증: `python -B verify_package.py <이 폴더>`.
