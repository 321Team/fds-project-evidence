# 새 Push 이후 Deploy 준비 항목

2026-10-13 KST / 이권욱 / CODEX_ASSISTED. **문서 준비만 수행했다. Deploy 승인·Token 발급·클러스터 변경은 없다.** 현재 승인 범위는 PR218의 Push까지다.

기존 `phase1-deploy-preparation-20261013/deploy-plan.unapproved.json`, `ADDITIONAL_RESULT.md` 및 CICD main147f760의 `docs/deploy-plan-v2.md`를 대조했다. 계획 파일 이름의 unapproved 여부와 실제 template_only=false 값을 구분하며, 기존 계획을 복사해 재실행 가능한 새 승인으로 취급하지 않는다. 초기 설계 문서의 NOT_INTEGRATED는 작성 시점의 경계다. 10/13 실제 실패 Deploy·복귀 기록이 있으므로 현행 Runtime 연결 부재로 해석하지 않는다.

| 항목 | 다음 새 계획에서 필요한 근거 |
|---|---|
| 실행 코드 | 실제 current main SHA·app-deploy.yml/관련 코드·필수 CI 확인. 이전2d8a14c 승인 대신 현147f760과 변경 영향 연결 |
| TBS/Build/Scan | Run38395350748/Attempt1, APP affbc69, 새 archive/manifest/config·Scan/root receipt hash. PR217 원본과 PR218 입력으로 대조 |
| Push | 이번 실제 Push 완료 후 얻는 새 Run/Attempt·workflow SHA·result 원본 SHA·두 원격 digest. 미래 RunID나 PASS를 채우지 않음 |
| 현재 클러스터 | 별도 읽기로 정확 두 Deployment UID·현재 이미지·세대/자원 버전·HPA/replica·Ready·SA UID·CA/API/audience 기준을 다시 수집.16:51 당시값을 현재 상태로 사용하지 않음 |
| 이전 이미지/복귀 | 현행 이미지 두 개의 재Pull·호환성·복귀 영향 확인. 기존 이미지는 업무 포트 /metrics 노출이 다시 생길 수 있음을 새 복귀 결정에 보존 |
| request/plan/approval | 새 실행 의도 UUID, 현재 상태와 새 Push를 포함한 계획 원본, 별도 승인 원본 및 외부 해시. 이전 소비 claim1/checkpoint9는 삭제/재사용하지 않음 |
| CP1 credential | 승인 후에만 기존 TokenRequest900초·fresh TokenReview·audience/SA UID 결속. 이전 token·소켓·수신 파일을 재사용하지 않음 |
| 인수 | 성공 Deploy/원격 이미지와 Pod imageID·준비 상태, 최소 HA/복귀, 최종 APP 저장·조회 회귀 순서로 연결. DB#11은 최종 앱 회귀 후 판단, W4 NOT_MEASURED 유지 |

실행 전에 준비할 검토물은 새 Push 원본과 current 클러스터 baseline에 결속된 plan/approval 후보, 실제 시작·종료창, 두 앱 적용·실패 복귀 범위와 콘솔 대응이다. 코드 리뷰·입력 검토·사용자 실행 허용·Runtime·AC 인수를 분리한다. Push 성공만으로 새 Deploy를 자동 dispatch하지 않는다.
