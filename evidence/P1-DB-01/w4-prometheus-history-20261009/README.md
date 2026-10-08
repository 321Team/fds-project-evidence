# P1-DB-01 — W4 과거 Prometheus 관측 보완

CODEX_ASSISTED · 실행자 이권욱(GWONUK). 2026-10-09 07:22~07:24 KST, 사용자 00~09시 단독 창에서 기존 경로로 읽기 전용 조회했다. **과거 앱 카운터 시계열은 회수했으나 W4 전체 HTTP 5xx 여부는 여전히 `NOT_MEASURED`다.**

## 대상과 실제 결과

기준은 [원 실행 #172](https://github.com/321Team/fds-project-evidence/pull/172)의 **10/8 20:26:49~20:27:52 KST**다. 앞선 [#181](https://github.com/321Team/fds-project-evidence/pull/181)의 Worker CRI 로그 0바이트 확인에 이어 Edge 로그 접근 및 Prometheus 과거 보존 자료를 확인했다. 기존 증적 폴더는 수정하지 않았다.

| 조회 | 시각 KST | 실제 결과 |
|---|---|---|
| Edge `/var/log/nginx` 목록 | 07:22:44 | 기존 `svc_ansible`, euid1003: errno13 접근 거부. 로그 내용·보존 여부 미확인. 설정 파일 2개에서 조회한 명시 logging directive는 없었지만, 이것을 logging OFF로 해석하지 않음 |
| control01 서비스·Pod 조회 | 07:22:45 | monitoring-api/prometheus, ClusterIP10.100.128.161:9090, worker03의 Pod UID `265ca811-873c-45e1-8c46-6c1ce034e596` 확인 |
| Kubernetes Service proxy 경유 | 07:23:34~44 | 첫 과거 조회가 10초 timeout, 내부 명령 rc1. SSH/수집기 rc0와 구분. 다음 3개 proxy 조회는 미실행 |
| 기존 Prometheus loopback | 07:24:24경 | worker03에서 현재 컨테이너 UID/PID/netns 전후 일치 확인 후 기존 netns의 127.0.0.1:9090에 HTTP GET 4건, 모두 200/status success/rc0 |

Service proxy timeout 원인은 이 회차에서 진단하지 않았다. 운영 권한·정책을 바꾸지 않고, 이전 수집에서도 사용한 정상 관리 경로로 동일 Prometheus 프로세스의 loopback을 읽었다. 호스트 Python의 network namespace만 전환했으며 Pod 파일·명령·설정은 변경하지 않았다.

## 회수한 자료의 의미

`time=2026-10-08T11:30:00Z`에서 원시 range vector `[5m]`를 조회해 **20:25~20:30 KST** 보존 표본을 받았다. query_range의 반복 평가·보간 표본으로 바꾸지 않았다.

- `transaction_save_failure_total`, `fds_evaluation_error_total`, `transaction_save_success_total`: 각각 6개 instance 시계열, 합계 18개. 각 지표 57개, 합계 171개 보존 표본. **저장 실패·평가 오류의 조회 표본은 모두 0**이다. 저장 성공은 `10.244.39.202:9091`에서 1로 일정하고 나머지 시계열은 0으로 일정하다. 이 기간의 새 거래 유무와 HTTP 응답 전수는 확정할 수 없다.
- `up`: transaction-api 6개 시계열의 보존 표본을 연결했다. `10.244.69.238:9091`에 **20:27:42.943 `up=0`**가 있어 W4 안의 scrape 실패가 확인된다. 같은 대상의 20:27:57.943 및 `10.244.39.202:9091`의 20:28:03.103에도 0이 있으나 두 표본은 W4 종료 뒤다. 나머지 조회 시계열의 관측값 1은 연속 가용성의 보장이 아니다.
- 수집 표본 간격은 각 시계열에서 15초다. 시계열 종료/새 instance 시작 구간을 하나의 연속 프로세스로 합쳐 counter reset을 판정하지 않았다. 과거 IP의 Pod UID 매핑도 이 회차에서는 별도 검증하지 않았다.
- W4 시작/종료 두 시점에서 이름에 `http` 또는 `request`가 포함된 지표는 각각 55개다. 이 조회에는 앱 거래 HTTP 응답 전체를 나타내는 상태 코드별 지표를 식별하지 못했다. Prometheus/스크레이프 핸들러/API server의 HTTP 지표를 앱 5xx로 대체하지 않는다. 이 제한된 검색으로 모든 중앙 로그 시스템의 부재를 주장하지 않는다.

Prometheus 공식 문서의 [up 정의](https://prometheus.io/docs/concepts/jobs_instances/#automatically-generated-labels-and-time-series)에 따라 0은 **스크레이프 실패**다. 이를 앱의 HTTP 5xx 발생, DB 장애 원인 또는 사용자 요청 실패로 단정하지 않는다. 반대로 일부 오류 카운터 0도 전환 시각 사이의 요청·최종 scrape 뒤·프로세스 교체 전 손실을 배제하지 못한다.

## 파일과 검증

- `receipt/` 4개: 전송 collector, 수신 stdout JSON, stderr, 명령·KST·rc·collector/stdout SHA256. 접근 거부와 proxy timeout도 보존했다.
- API 본문 전체는 보존하지 않고 호스트에서 필요한 필드만 추출한 JSON을 수신했다. 원 API 응답 SHA256과 수신 projection SHA256은 구분한다. 토큰·Secret·환경 변수·앱 요청 본문/주소를 수집하지 않았다.
- `analyze_w4_history.py`와 `analysis.json`: 원본 수신 projection으로 분석을 다시 실행해 동일 바이트임을 확인했다. 실행 예: `python -I -X utf8 analyze_w4_history.py receipt/prometheus-loopback/stdout.json`. Windows 생성 stdout의 줄바꿈도 원본 그대로 보존했다.
- 4회 수신의 collector/stdout 해시 8/8 일치, 새 manifest 및 루트 레지스트리 연결. 해시·layout 검증은 HTTP 성공/가용성/AC 인수와 별개다.

## 남은 수집과 경계

Edge의 기존 정상 운영 계정으로 당시 access log 및 log_format·rotation/보존 범위를 확인해야 한다. 이 세션의 `svc_ansible`에 새 권한을 부여하거나 ACL을 변경하지 않는다. 사용자에게 기존 server08 콘솔에서 직접 sudo 입력이 가능한지 확인 요청했으며, **인증 또는 로그 수신 완료로 기록하지 않는다**. 확인 가능한 과거 자료가 없으면 W4 미측정을 유지하고 담당자가 한계를 인수한다.

DB/Secret 변경, 앱 트래픽 생성, rollout, 서비스 재시작, Harbor 접근은 없었다. 원복할 운영 변경도 없다. 독립 리뷰는 작업창 종료 후 이재환님께 회수하며, 기존 DB 위험수용 종료·N1 판정 불가·AC 상태는 변경하지 않는다.
