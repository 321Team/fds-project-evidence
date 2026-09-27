# P1-MON-01 — node-exporter livenessProbe 현장 반영·NetworkPolicy/9100 양성·음성 시험 (2026-09-27)

MON Lead(이재환)가 k8s-control01(`server02`)에서 [infra-monitoring#21](https://github.com/321Team/infra-monitoring/pull/21)(이권욱 APPROVE, merge `8107b25`)의 livenessProbe를 현장 DaemonSet에 `kubectl patch`로 반영했다. **운영 변경: node-exporter Pod 3개 순차 교체.** 서버 폴더 `~/mon21-ne-20260927T074437`, archive(2,323 B, SHA-256 `bae00ae1…155508`)를 base64로 받았고, archive와 서버 `sha256sum`(`server-sha256sums.txt`)이 수신본과 일치한다.

| 파일 | 내용 |
|---|---|
| `ds-before.yaml` / `ds-after.yaml` | 적용 전·후 DaemonSet |
| `ne-liveness.txt` | liveness `GET / :9100`, initialDelay 10, period 20, timeout 5, failureThreshold 3 |
| `ne-pods.txt` | rollout 후 90초: worker01/02/03 Pod 모두 `ready=true restarts=0` |
| `unhealthy.txt` | Unhealthy 이벤트 3건. 모두 **readiness** `connection refused`이며 새 Pod 기동 직후(readiness에 initialDelay 없음) 1회다. liveness 실패와 재시작은 없다 |
| `ne-up.json` | `up{job="node-exporter"}` 3/3 = 1 |

- patch 시 PodSecurity `warn=restricted` 경고가 출력됐다. monitoring-node는 `enforce=privileged`·`audit/warn=restricted`인 의도된 통제 예외(DEC-P1-MON-01)다.
- 같은 날 KSM Probe 반영과 Prometheus·Grafana·Alertmanager Probe 상태는 [evidence#51](https://github.com/321Team/fds-project-evidence/pull/51) `control01-mon11-ksm/`에 있다. 이 둘을 합쳐 #17 보조통제 "KSM `/livez:8080`·`/readyz:8081`과 각 Monitoring Component 공식 Probe PASS"의 근거로 쓴다.

## `control01-np-matrix/`·`ansible01-console/` — NetworkPolicy·TCP 9100 Host Firewall 양성/음성 (16:50~17:00 KST)
**읽기·연결 시험만 했다. 객체 생성·변경은 없다.** control01은 호스트 `/dev/tcp`와 기존 Pod(`kubectl exec`)에서 5초 connect를 시도했다. 서버 폴더 `~/mon17-np-20260927T075050`, archive(1,116 B, SHA-256 `be8b564a…5a7da7`)를 수신 대조해 일치했다. ansible01 출력은 **콘솔 제출 자료**다(채팅 붙여넣기 원문, 서버 Hash 없음, 명령은 `commands.txt`).

| 구분 | 시험 | 결과 |
|---|---|---|
| Host FW 음성 | CP `.102` → Worker `.105/.107/.108` `:9100`·`:9101` | 6/6 BLOCKED |
| Host FW 양성(대조) | CP `.102` → Worker `:10250` | 3/3 OPEN |
| Host FW 음성 | 관리 `.10` → Worker `:9100`·`:10250` | 6/6 TIMEOUT(DROP) |
| Host FW 대조 | 관리 `.10` → Worker `:22` | 3/3 OPEN |
| NP 음성 | fds-engine → `prometheus.monitoring-api.svc:9090`, → `.105:9100` | TIMEOUT |
| NP 양성 | Grafana → prometheus `:9090` | rc=0 |
| NP 음성 | Grafana → `.105:9100`, → kube-state-metrics `:8080` | rc=1(실패) |
| NP 양성 | Prometheus → `.107:9100` | rc=0 |
| NP 음성(약함) | Prometheus → `.107:9101` | rc=1 — 9101에 listener가 없어 거부와 정책 차단을 구분할 수 없다 |

`np-list.txt`(NetworkPolicy 26줄)·`gnp-list.txt`(GNP 7개)는 시험 시점 목록이다. 호스트 `/dev/tcp` 결과 BLOCKED는 timeout과 refused를 구분하지 않는다. 대상 9100은 node-exporter가 hostNetwork로 listen하므로 차단은 방화벽에 의한 것이다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
