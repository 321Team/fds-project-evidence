# 시작 마감만 조정하는 실행안 — 2026-10-13 16:41 KST

사용자의 추가 true Run 1회 허용은 확정했다. 이 문서는 기존 16:30 시작 마감을 16:45로 조정하는 결정만 요청하며 승인 전에는 실행하지 않는다.

- 종료는 기존 17:00 KST 그대로. `--authorization-expires 2026-10-13T08:00:00+00:00`에 대한 기존 source Window 로컬 검증 PASS, 현재 잔여900초 이상.
- 원 plan/approval/record/source/대상 두 앱/지정 이전 image 복귀는 동일하다. 16:45까지 새 dispatch하지 못하면 보류한다. 추가 true Run은 1회, 새 binding 사용, broker execute 1회. 자동 재실행 없음.
- 기존 false 사전검사의 exact record 일치 결과를 소비한다. 새 dispatch 전에 main/원 approval/현재 앱·SA·CA/plan claim 부재/Harbor 비중첩을 재확인한다. Harbor 별도 작업은 16:36 PR60 코드 병합만 완료, 설치·H6 미실행으로 조회했다.
- broker UTC 검증은 dispatch 전에 끝낸다. 실제 Run/Attempt1/binding/socket을 읽고 해당 binding을 보호된 새 파일로 저장한 뒤 기존 source broker를 연결한다. 실패 시 재실행하지 않고 원본과 현재 앱 상태를 수집한다.
- 정상 판정은 broker 결과만으로 하지 않으며 Workflow 결과·claim/checkpoint·두 이미지/Pod 준비상태를 함께 확인한다. rollback 시 이전 업무 포트 /metrics 노출 복원이라는 기존 영향은 유지한다.
- HA/drain/reboot/최종 APP 회귀 및 DB 인수는 포함하지 않는다.

질문이 필요한 이유: 원 PR213 사용자 승인과 독립 입력 검토는 시작 마감을16:30으로 명시했다. 추가 실행 횟수 승인을 임의의 시작 마감 연장으로 바꾸지 않는다.
