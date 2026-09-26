# P1-MON-01 — 보완 증적 수집 (2026-09-26)

[baseline#17 증적 대응표](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5843098390) 2번(근거 표기 없이 체크된 AC)의 읽기 전용 보완분과, 미체크 AC "거래 호출 후 API/FDS/DB 저장 Metric과 Kubernetes/Node Metric 조회가 성공한다"의 실측이다. MON Lead(이재환)가 k8s-control01에서 직접 실행했다.

`mon01-20260926T051616Z/`의 파일은 서버에서 만든 archive를 풀어낸 **서버 생성 원본 그대로**다. 그 폴더의 `SHA256SUMS`도 서버에서 만들었다.

## 실행 정보

| 항목 | 값 |
|---|---|
| 대상·계정 | k8s-control01, `server02`. kubectl은 `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf` |
| 시각 | 2026-09-26 05:16:16–05:24 UTC (14:16–14:24 KST) |
| 명령 | `commands.txt`(수신 측 작성, 실행한 명령을 그대로 옮김). 별도 스크립트 파일 없이 콘솔에서 실행 |
| archive | `mon01-20260926T051616Z.tar.gz` 2,821 bytes, SHA-256 `027e50383a40a192f67b69aa4231f46491dde7df73620a42b5fa36655866a791` |
| 전달 | 서버에서 `base64 -w0`로 출력해 채팅으로 받았다. 복원한 archive의 SHA-256이 서버 출력과 같고, 내부 `SHA256SUMS` 9/9가 일치한다. archive 자체는 편입하지 않고 풀어낸 파일을 편입한다. `archive.sha256.txt`는 서버 출력을 옮겨 적은 것이다 |
| 클러스터 변경 | 없음. 다만 `31`에서 합성 거래 1건을 POST해 DB `transactions`에 시험 행 1개(`account_id=SIM_mon_ac2_20260926T051949Z`)가 생겼다 |

`22-grafana-provisioning.txt`는 두 번 추출했다. 첫 추출(`provisioning|datasource|dashboard` 60줄)이 대시보드 검색 인덱스 로그로 채워져, `logger=provisioning`으로 다시 추출해 덮어썼다. 그 뒤 `SHA256SUMS`와 archive를 다시 만들었다. 첫 archive(SHA-256 `dfb94750…b9fc3a`)는 폐기했다.

## 결과 요약 (판정 아님)

| 파일 | 대상 AC | 결과 |
|---|---|---|
| `10`·`11`·`12` | Grafana `ClusterIP`, Ingress·NodePort·LB 0건 | monitoring-api Service 4개(alertmanager·grafana·kube-state-metrics·prometheus) 모두 ClusterIP. `nodeport_or_lb: 0`, `ingress: 0`. 클러스터 전체 Ingress 조회 결과 없음 |
| `20` | 승인 관리 단말 port-forward 성공 | control01에서 `port-forward svc/grafana` → `/api/health` `{"database":"ok","version":"13.2.2"}`, HTTP 200 |
| `21` | 비승인 외부 접근 실패 | 노드 6대 IP × 3000/9090/9093, 18건 모두 `http_code=000` |
| `22` | Dashboard Provisioning | Pod 시작(2026-09-25 04:42:28Z)에 `provisioning.alerting`·`provisioning.dashboard` 각각 starting → finished, 오류 없음 |
| `30`·`31`·`32` | 거래 호출 후 Metric 조회 | 아래 표 |

### 거래 호출 전후 (`30` 05:19:49Z → `31` 거래 → `32` 05:20:34Z)

- `31`: HTTP 201, `transaction_id=b1dcaf7d-6560-4b7b-b109-24b6311c15af`, `fds_detected=true`, R02만 triggered(3,500,000원, threshold 3,000,000원).

| Metric | 전 | 후 | 차이 |
|---|---|---|---|
| `sum(transaction_save_success_total)` (API → DB 저장) | 1 | 2 | +1 |
| `sum(fds_evaluated_total)` | 2 | 3 | +1 |
| `sum by (rule_id)(fds_detected_total)` R02 | 1 | 2 | +1 |
| `kube_deployment_status_replicas_available{namespace="fds-app"}` | fds-engine 2, transaction-api 2 | 같음 | 조회 성공 |
| `node_uname_info` | k8s-worker03 1건 | 같음 | 조회 성공, 1대만 |
| `up{job=~"transaction-api\|fds-engine"}` | 4/4 up | 4/4 up | — |

카운터 절댓값이 작은 것은 앱 Pod가 약 15시간 전에 재시작되어 메모리 카운터가 초기화됐기 때문이다. 판정에는 증가분만 쓴다. 카운터는 rule_id 단위라 transaction_id로 직접 조인되지 않는다. 같은 거래를 가리킨다는 근거는 전후 +1과 응답의 R02다(9/25 #20 기록과 같은 방식).

## 한계

- **Node Metric은 worker03 1대만 수집된다.** 전체 `up` 20개 중 up은 6개다(app 4, kube-state-metrics 1, node-exporter 1). kubelet·kubelet-cadvisor 12개와 node-exporter 2개는 down이다. GNP 크로스노드 known issue(#14, infra-kubernetes#39)와 같다.
- **`up` 목록에 Prometheus self Target이 없다.** AC "모든 Target UP"의 대상인 Prometheus self Target은 scrape job이 설정되지 않은 것으로 보인다. 별도로 확인해야 한다(NOT VERIFIED).
- `21`의 출발지는 control01 1곳이다. 외부 PC 출발지는 대표하지 않는다.
- Grafana Datasource Health와 Dashboard 목록은 로그인이 필요해 이번 수집에 없다.
- DB 행 직접 조회(psql)는 하지 않았다. DB 저장 근거는 `transaction_save_success_total` 증가와 HTTP 201 응답이다.

이 편입은 증적 보존이며 AC 체크·Gate·티켓 상태를 바꾸지 않는다. AC 판정은 #17에서 Lead가 기록한다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
