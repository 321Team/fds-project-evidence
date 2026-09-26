# P1-MON-01 — Lead 직접 재수집 원본 (2026-09-25)

[PR #31](https://github.com/321Team/fds-project-evidence/pull/31)이 지적한 P1-MON-01 AC 근거 공백 중 조회로 확보할 수 있는 항목을 담당 Lead(이재환, supreme33-kr)가 k8s-control01에서 **명령 출력 파일 그대로** 편입한다. 손으로 고치지 않았다. 이 PR의 이전 커밋(`0110c05`)에 있던 정리본(`rbac.txt`, `alertmanager-alerts.json` 등)은 이번 커밋에서 이 원본으로 교체했다([하영님 리뷰](https://github.com/321Team/fds-project-evidence/pull/37#pullrequestreview-5313449647)).

## 수집 정보

| 항목 | 값 |
|---|---|
| 실행자 | 이재환(supreme33-kr) 본인, k8s-control01 계정 `server02` |
| 시각 | 2026-09-25T04:47Z (13:47 KST). Alertmanager 재조회는 04:57Z |
| 명령 | `commands.log`에 명령 전문·시작/종료 시각·종료코드 기록 |
| 검증 | 서버가 수집 직후 계산한 `server-SHA256SUMS.pre`와 복원한 파일이 일치. 추가분 압축본 SHA-256 `45c4aadac381cac17a06fe5c332ca62aa1079bf77c3c915c88c26eb06a0697cd` 일치 |
| 빈 파일 | 내용이 비어 있는 `*.stderr`는 생략(서버 해시에는 빈 파일 해시로 기록) |

`commands.log`는 Alertmanager 재조회까지 포함한 최종본이라 서버 해시의 `commands.log` 항목과 다르다(이후 줄 추가).

## 파일 목록

- `rbac-clusterroles.yaml`: `kubectl get clusterrole prometheus-role prometheus-kubelet-scrape kube-state-metrics-role -o yaml` 원본.
- `rbac-can-i-list.txt`: `kubectl auth can-i --list --as=system:serviceaccount:monitoring-api:prometheus` 전체 출력.
- `monitoring-api-pvc.txt`, `monitoring-api-workloads.txt`: PVC, Service·Pod 조회.
- `alertmanager-alerts-pf.json`: Alertmanager `/api/v2/alerts` 원본 응답(`port-forward` 경유, 14건, `pf.log` 포함).
- `alertmanager-alerts.json`(0바이트) + `.stderr`: 먼저 시도한 apiserver 프록시 조회의 실패 기록(`10.244.39.221:9093: i/o timeout`). control01에서 다른 노드 파드로 가는 경로가 막혀 있는 알려진 교차 노드 문제와 같은 계열이며 결과 파일로 쓰지 않는다.
- `discord-screenshot.png`: Discord `#채팅-채널` 화면 캡처(휴대폰). 날짜가 화면에 없고 시각 표시는 10:20 전후(`FDSDetectionBurst`, `KubeletScrapeDownK3s` 등)다. 수집 일시를 특정하지 못하므로 참고용이다.

## 확인된 사실

- ClusterRole 3종은 get/list/watch(및 `nodes/metrics` get, `/metrics` get)만 부여하고 `secrets` 규칙이 없다. Prometheus SA의 `can-i --list`도 같다.
- PVC 3개(Prometheus 20Gi, Grafana 5Gi, Alertmanager 2Gi)가 Bound다.
- Alertmanager는 수집 시점 활성 alert 14건을 갖고 있고 모두 `suppressed` 상태다(`KubeletScrapeDown` 6노드, `NodeExporterDown` 2개 등). 시작 시각은 9/25 04:23~04:24Z다. 이 조회 결과만으로는 Discord 전달 여부를 증명하지 못한다(스크린샷은 다른 시각의 별도 자료).

## 미수신·미확인 (이번에 확보하지 못한 것)

- **Test Alert(FDSMonitoringPipelineTest)의 FIRING→RESOLVED 전이 기록.** 이 티켓 AC의 핵심이다. 스크린샷은 다른 alert이고 날짜가 없다. 필요하면 별도 승인 하에 발화 시험 후 원본을 추가해야 한다.
- `kubectl scale` 시험과 p0 alert 전환 기록.
- Grafana 대시보드·데이터소스, Service·Port-forward 승인/비승인 조회의 원본.
- Discord 수신 화면의 날짜·시각이 보이는 원본 캡처.

AI 사용: CLAUDE_ASSISTED (실행은 담당자 본인, Claude는 명령 작성·복원·검증·문서화)
