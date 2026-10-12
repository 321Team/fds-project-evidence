# Phase 1 앱 분산 복구와 후속 준비 — 2026-10-13

이권욱 / CODEX_ASSISTED. 최종 서버 조회 **00:57:19 KST**, 변경·사후 관측 종료00:57:20. 사용자 “권장 순서대로 착수” 및 정확 범위에 대한 “허용 — Harbor 종료 후 콘솔 대기 가능”에 따라 수행했다. Harbor 세션의00:41:57 상태 기록에서 변경/사후 관측00:40:39 종료·진행중0을 확인한 후 별도 APP 구간으로 통보했다.

## 실제 결과

| 작업 | 결과 | 완료로 확대하지 않는 범위 |
|---|---|---|
| 앱 분산 복구 | engine→API, 앱당 기존 Pod2개씩 총4개 Eviction command 성공. 각 단계 후 복구 확인. 최종 앱별 worker01/02/03에1개씩, Ready6/6 | Final E2E·HTTP POST/Rule/DB·새 Drain/HA AC·지속적인 자동 재분산 |
| 형상·공급 보존 | 같은 Deployment UID/spec/template SHA·같은 RS·기존 이미지 유지. worker02 기존 Pod2개 보존. 후보 이미지 배포0 | 이미지 후보/rollback 승인·보안/서비스 전수 검증 |
| 접속·MON | Edge와3개 Worker NodePort200. MON app6개 포함23/23 up, remote write failure15m 값0. 임시 loopback forwarder 모두 종료 | 모든 사용자 요청 무손실, 외부 구간/전 트래픽 성공 |
| GET 관측 | 변경4구간 각90회+마지막60회, **420/420 HTTP200**, 관측 최대19ms | 연속 전 구간의 무장애나 기존 HA AC 측정 조건과 동등하다는 주장 |
| K8S17 준비 | 승인 source4개 바이트·SHA·구문 대조, 교체17/보존28/호스트 순서 입력 고정 | 서버 backup·복원시험·설치·도구 실제 호출 |
| OID 보완 | control01 고정15개 layer **84,341,850bytes** 직접 읽기, 각 descriptor size/SHA 일치 | 원 공급 provenance·archive 생성/크기·export/import·타 노드 cache·reboot |

기존 API image a7093136…/engine5e2a081c…를 유지했다. 승인된 Delivery 후보 ef0afe42…/de34afb7…로 배포한 회차가 아니다. worker01/03에서 같은 이미지 complete/unpacked를 먼저 확인했고 실제 새 Pod의 event를 별도로 보존했다. cache 관측만으로 모든 향후 Registry 접근이 없다고 보장하지 않는다.

## 단계와 추적

`EXECUTION_SCOPE.md`는 사용자에게 제시한 실행 범위 원본 r1이다. `USER_AUTHORIZATION.json`, `APP_BINDING.json`, 변경 전 읽기, 단계별 target UID/resourceVersion·grace30·API 응답·원본 script SHA·사후 분석을 연결한다. 같은 요청 자동 재전송·강제삭제·전체 rollout/Drain/reboot0. 각 단계는 기본 kubectl 명령1회 호출로 기록하며 HTTP wire 전송 횟수를 packet capture로 센 것은 아니다.

native Eviction은 같은 Pod UID를 복원하는 기능이 아니다. 기존 RS의 새 Pod 재생성이 실제로 성공했으며 네 기존 UID 소멸·두 기존 UID 보존을 확인했다. Deployment/RS·이미지·정책을 바꾸어 복구하지 않았다.

중간 `engine-2-post1`과 `api-2-post1`에는 MON 이전 주소가 남아 있어 NOT_STABLE로 기록했다. 후속 읽기에서 현재 Pod IP와 app job target을 직접 대조했고, Ready30초·MON 안정 뒤에 다음 변경 또는 최종 관측으로 갔다. 초기 `up{namespace="fds-app"}`의 빈 벡터는 해당 namespace 라벨 부재였으며 `up` 원본에서 실제 job 라벨을 확인해 정정했다. 빈 결과를 성공이나 장애로 계산하지 않았다.

Edge 최초 sudo 시도는 암호가 필요해 HTTP 실행 전에 실패했고 정상 기존 계정의 비권한 GET으로 수집했다. 실패 영수증도 보존했다. `eviction-guard-readonly`의 rc2/STOP은 실제 요청 직전에 의도적으로 중단한 guard 검증이며 Eviction0이다. 이들을 실제 복구 실패로 합산하거나 삭제하지 않는다.

원본 수신44개 receipt의 source/stdout/stderr SHA 일치, API 요청4개의 rc0/Status Success, 최종 분산·UID·spec·420개 GET·15개 layer·공급4개 SHA를 로컬 검증기로 대조했다. 자기 검증은 독립 REVIEW가 아니다. 실제 순수 읽기 collector와 단회 기본명령 전달 보조는 별도 독립 코드 리뷰를 받지 않았으며 source/명령/영수증을 그대로 공개한다. 기존 PR65·PR85 승인 코드를 그대로 실행했다고 주장하지 않는다.

## 다음 순서

1. **K8S17**: 실제 도구 호출 배제·해당 호스트 콘솔·새0700 백업 위치를 확정하고 backup→임시 복원/metadata 확인→control01의1파일→검수→나머지4대 각4파일. [준비 자료](../evidence/P1-K8S-01/v4-supply-prep-20261013/K8S_OID_NEXT.md). worker01 비대상5파일 relabel은 포함하지 않는다.
2. **OID02**: 현 control01 cache를 복구 공급원으로 채택하는 범위와 실제 대상 고정 후 export·archive closure/해시·필요 대상 반입 검증. [보완 입력](../evidence/ICR-D-NET-01-01/oid02-layer-read-20261013/OID_INPUT_SUPPLEMENT_VERIFIED.json). 원 공급 경로를 소급 생성하거나 CP→Harbor를 열지 않는다.
3. **worker02 DNS 한정 회차**: 앱 집중 선행 위험은 해소됐다. 실행 시점 재점검·콘솔·다른 작성자 배제를 거쳐 기존 prepare/apply/reapply/rollback 범위로 진행한다. 현재 목표 DNS와 같으므로 고의 drift를 만들지 않는다.
4. **Delivery/Runner/최종 인수**: fresh 공급 입력과 실제 필요한 Job이 생길 때 두 번째 운영자 인수, 후보 배포 뒤 해당 HA·Final E2E를 연결한다. PR164/207 대기 리뷰를 재요청하거나 기존 AC를 넓히지 않는다.

Phase2 작업·새 descheduler/PDB 정책 도입·추가 자격증명·새 티켓 종결 없음. 현 APP 작업창은 종료됐고 Harbor에 완료 상태를 인계한다. 증적은 기존 PR208에 한 번 보완하여 독립 검토를 받으며 새 중복 PR을 만들지 않는다.

실제 수신 자료: [APP 회차](../evidence/P1-APP-01/redistribution-20261013T004854/README.md), [K8S 준비](../evidence/P1-K8S-01/v4-supply-prep-20261013/README.md), [OID layer 읽기](../evidence/ICR-D-NET-01-01/oid02-layer-read-20261013/README.md).
