# P1-MON-01 — 10/4 worker03 장애 중 monitor01 heartbeat 단절 감지 기록 (수집 2026-10-04 22:36 KST)

10/4 worker03 장애(01:47~16:15 KST) 동안 monitor01 외부 수신 측이 heartbeat 단절을 감지·해소했는지 확인한 원본이다. #17 [5980607431](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5980607431)에 적은 관측의 근거 파일이다. 수집자는 MON Lead 이재환(supreme33-kr)이다. 해석은 이 README에만 적는다.

## 수집 정보

| 항목 | 값 |
|---|---|
| 호스트·계정 | monitor01 `10.250.10.30`, `server01_monitor` |
| 수집 시각 | `ts.txt` = 2026-10-04T22:36:15+09:00 |
| 방법 | monitor01 receiver Prometheus `127.0.0.1:19090` `query_range` 읽기 전용 조회 2건, 01:30~16:45 KST, step 60s. 명령 전문은 `collect-command.sh` |
| 조회 식 | `ALERTS{alertname="FDSMonitoringHeartbeatMissing"}` → `alerts.json`, `count_over_time(fds_monitoring_heartbeat[1m])` → `hb.json`. `summary.txt`는 두 파일을 요약한 출력 |
| 서버 해시 | `monitor01/server-SHA256SUMS` — 10/5 01:0x KST monitor01에서 다시 계산한 값 |
| 전달 | 10/5 monitor01 화면 출력으로 옮겼다. `alerts.json`은 `gzip -9cn | base64` 38줄(줄마다 `cksum` 대조 38/38), 나머지 3개는 `cat` 출력. 복원한 4개 파일 모두 서버 SHA-256과 일치한다. 첫 시도(tar.gz)는 옮기는 과정의 오류로 CRC가 맞지 않아 버렸다 |

## 확인된 사실

| 항목 | 값 |
|---|---|
| 경보 | `FDSMonitoringHeartbeatMissing`(severity `critical`) 시계열 1개, `alertstate=firing`. 01:48:00 ~ 16:16:00 KST, 60초 간격 869점, 중간 공백 없음 |
| heartbeat 수신 | 1분당 4개(15초 간격) 정상 수신 → 마지막 01:43:00 구간 → 다음 16:17:00 구간(1개) → 16:18부터 다시 4개 |
| 단절 구간 | 01:43 → 16:17 KST(52,440초) |

**해석:** 클러스터 Prometheus가 worker03 장애로 멈춘 동안 monitor01의 heartbeat 단절 경보가 firing 상태가 됐고, heartbeat가 다시 들어오자 해소됐다. 외부 Watchdog의 감지·해소 동작이 실제 장애에서 관측된 것이다.

## 한계

- **통보는 확인 대상이 아니다.** monitor01 receiver에는 Alertmanager가 없고 IF-24는 설계상 미구성이라, 이 firing은 외부로 통보되지 않았다. 이 자료는 규칙 상태까지만 보여 준다.
- **시간 해상도는 60초다.** `hb.json`은 1분 창 집계이고 `alerts.json`도 60초 간격이라, 마지막 heartbeat 시각과 firing 시각의 차이를 초 단위로 판정할 수 없다. "5분 이내(평가 간격 포함 5분 15초)" 판정은 evidence#91의 통제 시험(5분 11초)을 따르며, 이 자료로 대체하거나 다시 판정하지 않는다.
- worker03 장애 원인과 클러스터 쪽 Prometheus 공백 자체는 이 수집 범위 밖이다.
- 명령 실행 화면은 보존하지 않았다(`collect-command.sh` 머리말 참조).

## 파일

| 경로 | 내용 |
|---|---|
| `monitor01/alerts.json` | 경보 `query_range` 응답 원본 |
| `monitor01/hb.json` | heartbeat 수신 수 `query_range` 응답 원본 |
| `monitor01/summary.txt` | 위 두 파일 요약 출력 |
| `monitor01/ts.txt` | 수집 시각 |
| `monitor01/server-SHA256SUMS` | monitor01에서 계산한 4개 파일 SHA-256 |
| `collect-command.sh` | 전달한 조회 명령 전문 |
| `SHA256SUMS` | 이 폴더 파일의 SHA-256 |

AI 사용: CLAUDE_ASSISTED (명령 작성, 전달 복원·대조, README 작성)
