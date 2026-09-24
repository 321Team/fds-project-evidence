# P1-MON-01 — 직접 재수집 (2026-09-25)

[fds-project-evidence PR #31](https://github.com/321Team/fds-project-evidence/pull/31)에서 지적된 P1-MON-01 AC 근거 공백을 해소하기 위한 자료다. RBAC/PVC/Alert/Discord 관련 원본을 담당 Lead 본인(이재환, supreme33-kr)이 직접 재수집했다.

## 수집 정보

| 항목 | 값 |
|---|---|
| 대상 | k8s-control01 (kubectl), Discord `#채팅-채널` |
| 실행자 | 이재환(supreme33-kr) 본인, control01에 직접 SSH 접속하여 실행 |
| 수집 시각 | 2026-09-25 (KST) |

## 파일 목록

- `rbac.txt` — `prometheus-role`/`prometheus-kubelet-scrape`/`kube-state-metrics-role` 3개 ClusterRole 전문(get/list/watch만, secrets 규칙 0건) + `kubectl auth can-i --list` 결과
- `pvc.txt` — `monitoring-api` 네임스페이스 PVC 3개(Prometheus 20Gi/Grafana 5Gi/Alertmanager 2Gi) 전부 Bound
- `alertmanager-alerts.json` — 수집 시점 Alertmanager 활성 alert 목록. **주의**: 원래 검증했던 Test Alert(FDSMonitoringPipelineTest)는 이미 FIRING→RESOLVED로 지난 시점이라 이 조회에는 안 잡힌다. 이 파일은 "지금도 `discord-notifications` receiver로 alert가 정상 전달되고 있다"는 근거로만 사용.
- `discord-screenshot.png` — Discord `#채팅-채널`에 실제 수신된 alert 캡처. `KubeletScrapeDownK3s`, `FDSDetectionBurst`(R02 관련 이상거래 급증 경고) 등이 Spidey Bot을 통해 정상 전달됨을 보여준다.

## 이번에 하지 않은 것

- 신규 alert 강제 발화(kubectl scale 등)는 수행하지 않음 — 현재 활성 alert와 Discord 캡처로 파이프라인 동작만 확인.
- Grafana 대시보드/데이터소스 재확인은 이번 범위에서 제외(이전 세션 기록 유지).

AI 사용: CLAUDE_ASSISTED (담당자 본인이 직접 명령을 실행하고 Discord를 직접 캡처했으며, Claude는 명령 목록 제공·결과 정리·파일화만 수행)
