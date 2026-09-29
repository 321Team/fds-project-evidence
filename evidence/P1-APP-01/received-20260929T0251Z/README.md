# P1-APP-01 — transaction-api `/readyz` DB 장애 주입 시험 (2026-09-29 11:51~11:58 KST)

APP·DB Lead(이재환)가 정본 클러스터에서 worker01의 transaction-api Pod 1개만 db01에 접속하지 못하게 만든 뒤, Readiness·Endpoint·Liveness 동작을 관측했다. 명령은 담당자가 k8s-control01(`server02`), db01(`server08`), edge01(`server08`)에서 직접 실행했다.

**운영 변경 (모두 원복)**
- db01 firewalld **runtime** rich rule 추가 → 3분 뒤 제거: `rule family="ipv4" source address="10.1.93.105/32" port port="5432" protocol="tcp" reject`. `--permanent`는 사용하지 않았다.
- db01 PostgreSQL에서 `client_addr=10.1.93.105`, `usename=fds_app` 세션 2개(pid 19372, 20250) `pg_terminate_backend`
- 앱·매니페스트·Secret·replica 변경 없음. Pod 재시작·삭제 없음

## 배경 — 9/23 1차 시도와 차이

#15 본문 기록대로 9/23 시도는 worker02→db01:5432 신규 연결만 막아 커넥션 풀의 기존 연결이 계속 쓰였고(readyz 200 유지), Pod 재생성 시 차단하지 않은 Worker로 옮겨 가 재현하지 못했다. 이번에는 ① Worker당 1개 배치(3 replica)를 사전 확인하고 ② 차단 직후 해당 Worker 출발 세션만 종료해 풀이 재연결하도록 했다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-app-readyz-20260929/` (`observe.log`, `events.log`) | 546 B, SHA-256 `ad8f24cc…bf309cc` | 서버 `sha256sum`과 로컬 복원본 일치 |
| `db01/` | `~/p1-app-readyz-20260929/db01.log` | 438 B, SHA-256 `61404a1b…342ab27c` | 서버 `sha256sum`과 로컬 복원본 일치 |
| `edge01/` | `~/p1-app-readyz-20260929-edge01.log` | 269 B, SHA-256 `443eacd3…2d3159ef9` | 서버 `sha256sum`과 로컬 복원본 일치 |
| `console/` | 없음 (사전 확인 콘솔 출력) | — | 담당자 콘솔 제출 원문. 서버 파일·Hash 없음 |

파일별 서버 Hash는 받지 않았다. archive 단위로 대조했다.

## 사전 상태 (`console/precheck-20260929T0249Z.txt`)

- db01 `pg_stat_activity`의 `client_addr`는 Worker 노드 IP(`.105/.107/.108`)와 edge01 E-K3S(`.50`)다. Pod IP가 아니라 노드 IP로 보이므로 Worker IP 단위 차단이 가능하다.
- transaction-api 3 replica가 worker01/02/03에 1개씩, EndpointSlice 3개 모두 `ready=true`
- worker01 Pod `transaction-api-b784c8c5d-rq9b6`의 `restartCount`는 **시험 전부터 1**이다(원인은 이 시험 범위 밖).
- edge01 → Worker 3대 `:30080/readyz` 모두 200

## 절차와 시각 (KST)

| 시각 | 단계 | 근거 |
|---|---|---|
| 11:51:45 | control01 관측 시작(10초 간격, 42회) | `control01/observe.log` |
| 11:53:05 | edge01 관측 시작(10초 간격, `.105` 대상·`.107` 대조) | `edge01/…edge01.log` |
| 11:53:13 | db01 차단 rule 추가, `.105` 세션 2개 종료 | `db01/db01.log` |
| 11:53:18 ~ 11:56:18 | 차단 유지 180초 | `db01/db01.log` |
| 11:56:18 | rule 제거(runtime rich rule 목록에서 사라짐 확인) | `db01/db01.log` |
| 11:56:59 | `.105` 세션 2개 재연결 확인 | `db01/db01.log` |

## 결과

| 관측 | 결과 |
|---|---|
| `/readyz` 응답 (edge01 → `.105:30080`) | 11:53:15~11:53:35 **503**. Readiness 실패 누적 중 해당 Pod가 직접 503을 반환 |
| Readiness 이벤트 | `Unhealthy ×21 — Readiness probe failed: HTTP probe failed with statuscode: 503` (마지막 11:56:18) |
| Endpoint 제외 | 11:53:49~11:56:23 `ready=false`, `ep_ready=false`. edge01 `.105`는 11:53:45~11:56:26 `000`(Local 정책으로 로컬 Endpoint 없음) |
| Liveness | 차단 중(약 2분 45초 NotReady)과 원복 후 모두 **`restarts=1` 유지** — 재시작 루프 없음 |
| 대조군 | `.107` 전 구간 200. 다른 Pod `restarts=0` 유지. `.50`(E-K3S) 세션 3개 변화 없음 |
| 원복 | 11:56:33 `ready=true`·`ep_ready=true`(rule 제거 후 15초 이내), edge01 `.105` 11:56:36부터 200 |

`/livez`는 외부 호출이 없고 Liveness `periodSeconds: 20`(기본 failureThreshold 3)이므로, DB 의존이 있었다면 NotReady 구간 안에 재시작이 발생했어야 한다.

## 한계와 후속

- **FDS 장애는 시험하지 않았다.** transaction-api는 fds-engine 호출을 fail-open(connect 1s/read 2s)으로 처리하고 `/readyz`는 DB `SELECT 1`만 확인한다. AC "DB/FDS 장애 시 `/readyz` 503"의 FDS 부분 해석은 APP Lead 판단으로 남긴다.
- 관측 간격이 10초라 503→Endpoint 제외 전이 시각은 10초 단위로만 특정된다.
- 원인 미상인 기존 `restartCount=1`은 이 시험과 무관하게 남아 있다.
- edge01 nginx(:80) upstream은 아직 E-K3S라 서비스 입구 경로는 이 시험의 영향을 받지 않았고, 이 시험의 대상도 아니다.
- 시험 거래는 발생시키지 않았다(DB 행 추가 없음).

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
