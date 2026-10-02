# P1-MON-01 — monitor01 밤사이 수신 확인, heartbeat 5분 단절·복구, API-LB Probe 실패·복구 (2026-10-02 09:40~10:16 KST)

MON Lead(이재환)가 monitor01(`server01_monitor`)과 k8s-control01(`server02`)에서 실행했다. 전날 기동 기록은 [`received-20261001T1405Z`](../received-20261001T1405Z/README.md)이다.

**운영 변경:** 클러스터 `monitoring-api` Deployment `prometheus`를 09:43:02 replicas 1→0, 09:50:04 0→1로 바꿨다(Pod `prometheus-d8949bd64-tvptk` → `-cb7hx`, 같은 이미지 `2c28708b…`, worker03). monitor01 firewalld direct OUTPUT REJECT rule 1줄을 10:10:56~10:13:56(180초) 동안 두었다가 제거했다. 그 밖의 변경은 없다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `monitor01/` | `~/p1-mon-g8-morning-20261002T094013/`, `~/p1-mon-hb-cut-20261002T094143/`, `~/p1-mon-lb-fault-20261002T100845/`의 결과 2개(파일 5개) | `monitor01-g8-20261002.tgz` 3,470 B, SHA-256 `7c37a7a0…f9e594e7` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일 5개도 작업 중 서버가 출력한 SHA-256과 일치했다 |
| `control01/` | `~/p1-mon-hb-cut-20261002T094250/`(파일 4개) | `control01-g8-20261002.tgz` 1,288 B, SHA-256 `57447d23…e0c4701a` | 같은 방식. `run.log`·`post-check.txt`는 작업 중 출력과 일치(`run.sh`·`pf.log`는 비교할 이전 출력 없음) |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다. 비밀 정보 검색 0건.

## 1. 밤사이 수신 (`monitor01/p1-mon-g8-morning-20261002T094013/morning.txt`, 09:40)

컨테이너 3개 Up·재시작 0. 최근 10시간 `count_over_time(fds_monitoring_heartbeat[10h])` = **2400**(15초 간격 기대값), 최대 공백 12.8초, Watchdog firing 0회, `min_over_time(probe_success[10h])` = 1, nginx `10.1.93.108 204` 3000건·오류 0, receiver·blackbox error/warn 0. firewalld 조회는 `sudo -n` 비밀번호 요구로 빠졌다.

## 2. heartbeat 5분 단절·복구 (#17 4절 "`absent_over_time(fds_monitoring_heartbeat[5m])`로 단절을 탐지하고 복구 전이를 기록한다")

- 실행: control01 `run.sh`(root 백그라운드. replicas≠1이면 중단, 7분 뒤 자동 원복) → `run.log`
- 관찰: monitor01 `watch.log`(15초 간격 64회). 열 `age`는 `time() - timestamp(fds_monitoring_heartbeat)`, `alert`는 receiver `/api/v1/alerts`의 `FDSMonitoringHeartbeatMissing`. **열 `last_ts`는 조회식 오류로 평가 시각이 찍혀 판단에 쓰지 않는다.**

| 시각(KST) | 사건 | 근거 |
|---|---|---|
| 09:43:02 | `T_SCALE0`, Pod 제거 09:43:04 | `run.log` |
| 09:43:01.9 | 마지막 heartbeat(09:43:58 `age` 56.08초에서 역산) | `watch.log` |
| 09:43:13~09:47:58 | `age` 11→296초 증가 | `watch.log` |
| **09:48:12.9** | **firing**(`activeAt` `2026-10-02T00:48:12.902794128Z`, pending 없음). 마지막 샘플 뒤 **5분 11초** | `watch.log` |
| 09:50:04 / 09:50:15 | `T_SCALE1` / `T_READY rc=0`(새 Pod `cb7hx`) | `run.log` |
| 09:50:16.8 | 첫 heartbeat 재수신(09:50:28 `age` 11.16초에서 역산) | `watch.log` |
| **09:50:13 → 09:50:28** | **firing → none(해소)** | `watch.log` |

- 감지 시점은 `absent_over_time(…[5m])` 정의(마지막 샘플 + 5분)와 rule 평가 간격(15초) 안의 대기로 설명된다.
- 시험 뒤(10:03) 클러스터 Prometheus: `count(up)` 23 / `up==1` 23, rules 8 bad 0, config reload 1, 최근 10분 remote write 40건·실패 0(`control01/…/post-check.txt`). monitor01 nginx 최근 20분 `.108 204` 68건, 400 없음, receiver error/warn 없음(`nginx-after.txt`).
- receiver에는 Alertmanager가 없다. 상태 전이는 receiver API로만 확인했고 외부 알림 발송은 없다.

## 3. API-LB TCP Probe 실패·복구 (#17 4절 "API LB TCP Probe의 실패·복구를 외부 관점에서 기록한다")

- 실행기: infra-monitoring `monitor01/runtime_fault_api_lb.py`(main `1e33a0b`, SHA-256 `8b557628…`, 커밋 `7829473`), `sudo … --ack-hostwide --duration 180` → `fault-api-lb.jsonl`
- 관찰: `probe-watch.log`(15초 간격 32회, `probe_success{instance="10.1.93.109:6443"}`)

| 시각(KST) | 사건 | 근거 |
|---|---|---|
| 10:08:45~10:11:00 | `probe_success` 1 × 10회 | `probe-watch.log` |
| 10:10:55.6 | `impact_boundary` — `.109:6443` 연결 **없음**, direct rule 0줄 | `fault-api-lb.jsonl` |
| 10:10:55.8 | 자동 회수 timer arm(180초) | `auto_recovery_armed` |
| **10:10:56** | **fault rule 추가·확인** `FDS_MON19_1790903455_25738` | `fault_active` |
| **10:11:15~10:14:00** | **`probe_success` 0 × 12회** | `probe-watch.log` |
| 10:13:55.8 | timer가 rule 제거(스크립트의 제거는 `NOT_ENABLED`, timer unit은 이미 종료되어 `not loaded`) | `fault-api-lb.jsonl` |
| **10:13:56** | direct rule 0줄 재확인, `fault_recovered`, rc 0 | `fault-api-lb.jsonl` |
| **10:14:15~10:16:30** | **`probe_success` 1 × 10회** | `probe-watch.log` |

edge01 HTTPS Probe는 edge01에 443 서비스가 없어 9/26 기록대로 범위 밖이다.

## 판정 범위

- 이 기록은 #17 4절 heartbeat 단절·복구 전이와 API LB TCP Probe 실패·복구의 근거다. **AC 체크는 이 증적 병합 뒤 따로 판단한다.**
- **NOT RUN:** `.108` 출발지의 잘못된 인증 401·`.108 → .30:8443` 직접 차단·tcpdump(ICR 경로 필요), 재부팅 자동 기동, Gate-F 임시 키 정리.
