# P1-MON-01 — Prometheus self job 현장 반영 및 Target 전체 UP (2026-09-27)

MON Lead(이재환)가 k8s-control01(`server02`)에서 실행했다. [infra-monitoring#16](https://github.com/321Team/infra-monitoring/pull/16)(merge 2026-09-26)의 `job_name: 'prometheus'`(`localhost:9090`)를 현장 ConfigMap `prometheus-config`에 반영하고 reload했다. **운영 변경: ConfigMap 1개 수정과 Prometheus `/-/reload` 2회. Pod 재시작은 없다.**

서버 폴더 `~/mon16-apply-20260927T052436`의 파일을 tar.gz(4,632 B, SHA-256 `b49d313d…9dfe`)로 묶어 base64로 받았고, archive 해시와 서버 `sha256sum` 결과(`server-sha256sums.txt`)가 수신본과 일치한다.

## 절차와 파일
| 파일 | 내용 |
|---|---|
| `cm-before.yaml` | 적용 전 현장 ConfigMap 원본(백업) |
| `cm-after.yaml` | self job 3줄만 추가한 적용본. 현장 ConfigMap을 읽어 `scrape_configs:` 바로 아래에 삽입했다 |
| `cm-diff.txt` | `kubectl diff` 결과. 변경은 job 3줄 추가뿐이다 |
| `up-after.json` | 1차 reload 후 `up`: 20/20 UP. `prometheus` job은 아직 없다. ConfigMap 볼륨 반영 전에 reload했기 때문이다 |
| `up-after2.json` | Pod 안 설정 파일 반영을 확인(10초)한 뒤 2차 reload한 결과: **21/21 UP**, `prometheus` 포함 |

## 결과 (판정 아님)
- `up == 1` 21/21: transaction-api 2, fds-engine 2, kube-state-metrics 1, node-exporter 3(`.105/.107/.108`), kubelet 6·kubelet-cadvisor 6(CP `.102~.104` + Worker), prometheus 1.
- 크로스노드 수집 해소는 2026-09-26 SEC/ICR 현장 작업(Worker GNP 9100 현장 패치 [infra-kubernetes#41](https://github.com/321Team/infra-kubernetes/issues/41), CP GNP 10250 Worker source·kubelet `serverTLSBootstrap` 6대 — [#19](https://github.com/321Team/fds-project-baseline/issues/19))에 따른 것이다. 이 현장 상태는 소스 반영 전이다(infra-kubernetes #46·#47·#48, infra-ansible #55 진행 중). 재구성 시 소스가 반영되지 않으면 되돌아갈 수 있다.
- 현장 ConfigMap과 infra-monitoring main의 전체 일치 여부는 대조하지 않았다(이번 변경은 job 추가만).

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
