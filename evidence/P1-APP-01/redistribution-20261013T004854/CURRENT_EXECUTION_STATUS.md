# APP 분산 복구·사후 관측 종료 — 2026-10-13 00:57:20 KST

**실제 앱 변경·사후 관측 회차 종료. 진행 중 변경/관측 및 잔여 port-forward 없음.** 기존 Pod4개만 engine→API 한 개씩 정상 종료·재생성했다. 최종 앱별 Worker3대 1/1/1, Ready6/6, Node6 Ready, 서비스 Ready endpoint와 Edge→세 Worker NodePort200, MON23/23 및 remote write failure0. Deployment UID/spec/template SHA·기존 이미지 보존, 기존 Pod2개 보존. 변경4구간 각90회+최종60회 GET420/420 HTTP200, 최대19ms. 이 GET 관측을 업무 무손실·Drain/최종 HA 인수로 확대하지 않는다.

Runtime receipt44개 수신 hash를 대조했고 실제 Eviction command4개 rc0/Status Success를 확인했다. 중간 MON 교체 대기는 보존했고 다음 변경은 안정화 후에만 진행했다. 강제삭제·Drain·reboot·정책/DNS/credential 변경0. 증적 PR208 보완/독립 리뷰는 별도이며 AC/Exit/티켓 종결0.

K8S17은 공급4파일·17교체/28보존 입력의 로컬 준비만 완료, 서버 backup/restore/apply0. OID15개 layer84,341,850bytes 실제 읽기/hash 일치, export/import/reboot0. 후속 준비는 별도이며 이 파일의 종료 이후 자동 추가 Runtime 실행은 없다.

## 회차 시작 당시 기록

CODEX_ASSISTED. 사용자 앱별 최대2개/합계4개 한 개씩 Eviction 허용과 control01 콘솔 대기를 받았다. Harbor 세션 CURRENT_EXECUTION_STATUS의 00:41:57 기록에서 실제 변경·사후 관측 00:40:39 종료 및 진행 중 작업0을 확인했다. 이전 변경과 겹쳐 실행하지 않는다.

이쪽 fresh guard/Edge/MON 확인 후 APP 실행 및 사후 관측 구간을 시작한다. 이 파일에 종료 결과를 남길 때까지 Harbor/Registry/다른 앱·노드 변경과 겹치지 않는다. 현재 Eviction0이며 시작 확인과 실제 접수는 각 영수증으로 구분한다. 실제 실행자는 이권욱, 보조는 Codex, 콘솔 인수는 사용자 확인을 따른다.
