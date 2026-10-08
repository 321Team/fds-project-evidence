# IF-05C 다음 1회 시험안 — PREPARED / NOT_EXECUTED

2026-10-08 08:30~08:32 KST 조회. 실행 승인이나 예약된 창이 아니다.
대상: control01 기존 svc_ansible/sudo, monitoring-api의 전용 규칙 FDSMonitoringPipelineTest.

## 현재 확인

- ConfigMap `prometheus-p0-test-alert`, UID `fc3593b2-2937-49e0-acc9-8709dd1139a3`, resourceVersion1181424.
- 원본 data SHA256 `c97c60256c4caa64cd9699539eccbb5d60f18907b1c8190cea280e0d7e8fb22c`.
- 실제 Prometheus rule: `vector(1) == 0`, inactive/health ok. `web.enable-lifecycle=true`.
- 실제 Alertmanager status: 기본 receiver `discord-notifications`, group_wait10s/group_interval30s/repeat_interval1h,
  Discord send_resolved=true. Secret URL/credential은 저장하지 않았다.
- 현재 up23, up==0 빈 배열. 12일 전용 Firing sample 조회 및9/26 13:00~16:00 KST 범위 조회는 성공·빈 결과.
  빈 결과만으로 과거 시험 미실행을 확정하지 않는다. 조회 가능한 자료에서 원본 재구성은 못했다.

## 구체 변경과 예상 영향

전용 규칙의 **한 줄** `expr: vector(1) == 0`을 `expr: vector(1) == 1`로 잠시 변경하고 원복한다.
apply-candidate.json/restore-candidate.json은 현행 UID/data에 대한 JSON Patch test를 포함한다.
apply는 현재 resourceVersion도 검증하므로 stale 입력이면 중단한다. 새 창에서 다시 조회·대조해야 한다.
이는 실제 Discord 수신 경로로 Firing/Resolved 알림을 보내는 시험이다. 정상 목표는 각1회이며 전송 재시도·중복 가능성은 별도 기록한다.
APP 장애, Pod 재시작·스케일 변경, 기존 알림 silence, receiver/Secret/라우팅 변경은 포함하지 않는다.

## 실행 위치·순서·완료와 복구

1. control01에서 fresh 비중첩 창, Pod UID/Ready, up23/다운0, 원본 data hash·UID·RV와 실제 inactive/health를 다시 확인한다.
   일치하지 않으면 중단. 현재 live 파일 `/etc/prometheus/rules-p0/p0-test-alert.yml` 읽기와 hash 확인 경로를 먼저 검증한다.
2. 원본 byte/metadata·현재 API 상태를 새 회차에 저장한다. 실행자는 중간 오류에도 조건부 원복을 수행할 수 있어야 한다.
3. JSON Patch CAS로 expr만1로 바꾼다. Pod에 투영된 파일 hash가 후보와 일치한 뒤 loopback PF의 POST /-/reload를 사용한다.
   ConfigMap 반영 응답만으로 로드를 가정하지 않는다. 투영/로드 확인3분 상한, 반복 재배포는 하지 않는다.
4. 실제 rules/ALERTS Firing, Alertmanager 활성 항목, notification 지표 변화와 기존 Discord 채널 수신 원본을 시각·alertname으로 연결한다.
   Firing 관측 후 최대2분만 기다리고, 수신 실패여도 원복 단계로 진행한다. 외부 수신 열람이 없으면 delivery는 NOT_VERIFIED다.
5. UID와 후보 data 일치 조건으로 원본을 복구한다. 다른 작성자의 변경이 보이면 덮어쓰지 않고 즉시 인계한다.
   투영된 원본 hash 확인→reload→rule inactive/health ok→Alertmanager 해소→Discord Resolved 원본 순서로 확인한다.
6. 전체 창10분을 상한으로 사용한다. 오류/상한/사용자 중단이면 원복이 우선이다. 원복 확인 실패 시 완료 선언 금지,
   현재 CM/투영 파일/API 차이와 원본을 보존해 MON Lead에 전달한다. 서비스 재시작이나 임의 규칙 삭제로 해결하지 않는다.
7. PF와 관측 프로세스를 종료·회수하고, 원본 hash·up23/다운0·다른 규칙 불변을 확인한다.

**필요한 추가 사용자 확인:** 전용 규칙의 일시 변경과 기존 Discord 채널로의 실제 시험 알림 발송.
기존 “착수”를 외부 메시지 발송 지시로 확대하지 않았다. 독립 리뷰·AC 인수·티켓 종결은 별도다.
