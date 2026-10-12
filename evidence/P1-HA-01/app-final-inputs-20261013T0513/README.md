# Phase 1 APP·HA 입력 보완 — 2026-10-13 05:13 KST

이권욱 / CODEX_ASSISTED. control01의 순수 Kubernetes API GET6건만 수행했다.05:01의11GET 수집에서 빠진 topologySpreadConstraints·Service·EndpointSlice·HPA를 보완한 새 회차다. 두 Deployment의 spec·template는00:34 분산복구 사전 관측과 동일하고 Ready3/3이다. 변경 명령·능동 HTTP·거래 POST·Token·Deploy·drain·reboot·Probe 장애는0회다.

## 원본과 검증 범위

- `app-ha-delta-control01/`: 실행 collector bytes, SSH 명령/route·계정/StrictHostKey/시각/rc receipt, stdout 투영 JSON, 비어 있는 stderr. 기존 ansible01→svc_ansible→sudo 경로이며 새 인증이나 서버 파일 배치를 만들지 않았다.
- `read_app_ha_delta.py`의 출력은 비민감 필드만 보존한다. env·Secret·토큰·kubeconfig 내용을 출력하지 않는다. 원 API 응답 전체는 보관하지 않고 각각 hash를 기록했다.
- 원격 rc0, GET6건 모두rc0, receipt source/stdout/stderr SHA 일치, 분석의source SHA 일치. source 독립 REVIEW=NOT_PERFORMED (Pre-check). 새 수집기 결과의 증적 편입 독립 리뷰는 별도다.
- 분석은 `APP_HA_DELTA_ANALYSIS.json`에 보존했다.00:34 비교 근거는 `evidence/P1-APP-01/redistribution-20261013T0034`로 추측 연결하지 않고, 기존 PR208의 앱 분산복구 기록/APP_BINDING 원본을 소비한다. 정확한 비교 원본은 `prior-APP_BINDING.json` 사본과 해시로 함께 고정한다.

## 관측과 해석

| 항목 | 관측 | 해석의 범위 |
|---|---|---|
| 두 Deployment | spec·template hash 및 spread가00:34와 동일, Ready/updated/available3 | 현재 구 digest 형상. 이후 새 Deploy의 결과가 아님 |
| 분산 조건 | DoNotSchedule/maxSkew1/nodeTaintsPolicy Honor/matchLabelKeys pod-template-hash |05:01의 affinity 부재는 이 규칙의 부재를 뜻하지 않음 |
| NodePort | transaction-api-nodeport30080, externalTrafficPolicy Local | 실제 요청 성공·edge nginx upstream 동일성은 별도 |
| EndpointSlice | Worker3대 각1, ready=true/serving=true/terminating=false | API 메타데이터, 능동 HTTP 성공 증거가 아님 |
| HPA | fds-app0개 | 새 HPA 채택/필수화 근거가 아님 |

10/2 HA 증적92는 구 image·worker02 Drain·GET 범위의 유효한 과거 결과로 보존한다. 이후 K8S PR65에서 추가한 spread의 drain 중 스케줄링 영향은 그 시험에 들어 있지 않다. 최종 image 뒤 단일Worker 영향 확인을 준비하되 전체6대 반복·새 부팅 방화벽·Phase2를 추가하지 않는다. uncordon이 기존 Pod를 자동1/1/1로 옮긴다고 가정하지 않는다.

실행/중단/조건부 배치복구/DB 회귀 카드는 baseline PR165 `APP_HA_EXECUTION_CARD_20261013.md`에 있다. 아직 새 runtime 허용·실행·인수 완료가 아니다. Push13b50485 입력과10:00/12:00 별도 허용창은 그대로다.
