# P1-MON-01 — node-exporter livenessProbe 현장 반영 (2026-09-27 16:44 KST)

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

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
