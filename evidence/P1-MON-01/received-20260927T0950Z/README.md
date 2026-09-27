# P1-MON-01 — Prometheus SA 전환·IF-06B remote_write 현장 반영과 경로 차단 진단 (2026-09-27)

MON Lead(이재환)가 k8s-control01(`server02`)에서 [infra-monitoring#20](https://github.com/321Team/infra-monitoring/pull/20)(SA 전환, merge `fbeeaea`)과 [infra-monitoring#22](https://github.com/321Team/infra-monitoring/pull/22)(IF-06B 송신, merge `ace1e3f`)을 현장에 반영했다. **운영 변경: monitoring-api의 prometheus·alertmanager·grafana Pod 교체, RBAC 교체.** 서버 폴더 `~/ifo6b-apply-20260927T182247`의 archive(14,501 B, SHA-256 `3df54e42…746978`)를 base64로 받았다. archive와 서버 `sha256sum`(`server-sha256sums.txt`, 23개 파일)이 수신본과 일치한다.

## 결과 요약

| 항목 | 결과 |
|---|---|
| SA 전환 | prometheus → `prometheus-sa`, alertmanager → `alertmanager-sa`, grafana → `grafana-sa`. 3개 모두 Ready |
| RBAC | ClusterRole·CRB `prometheus-sa-kubelet-metrics`(`nodes/metrics` `get`만) 생성. 구 CRB `prometheus-binding`(18:26)·`prometheus-kubelet-scrape`(18:48)와 구 SA `prometheus`(18:48)는 백업 후 삭제 |
| Target | 적용 후 `count(up==1)`=21, `up==0` 없음(18:33, 18:50 두 번) |
| heartbeat | `fds_monitoring_heartbeat`=1(recording rule `vector(1)`, 15s) |
| remote_write | **실패(재시도 중).** 09:33Z부터 약 70초마다 `context deadline exceeded`, `samples_pending`=71, `samples_failed_total`=0 |
| 경로 | Pod 위치 `k8s-worker03`(`10.1.93.108`). control01 경로는 `10.250.10.30 via 10.1.93.58`(mgmt-gw01). monitor01에서 60초 tcpdump 결과 SYN **0건** |

## `control01-ifo6b-apply/`

| 파일 | 내용 |
|---|---|
| `sa-before.txt`·`cr-before.txt`·`crb-before.txt`·`deploy-before.txt` | 적용 전 SA·RBAC·Deploy SA 목록 |
| `deploy-{prometheus,alertmanager,grafana}-before.yaml` | 적용 전 Deployment(원복용) |
| `cm-before.yaml`·`cm-after.yaml`·`cm-diff.txt` | prometheus-config에 `remote_write`, prometheus-alert-rules에 `fds-monitoring-heartbeat` 그룹 추가 |
| `np-rw-before.yaml` | NetworkPolicy `prometheus-remote-write-allow`(app=prometheus → `10.250.10.30/32` TCP 443) |
| `rbac-new.yaml`·`can-i-prometheus-sa.txt` | 새 ClusterRole과 `auth can-i --list` 결과(`nodes/metrics` `[get]`만) |
| `root-ca.crt` | ConfigMap `monitor01-root-ca`에 넣은 공개 Root CA. DER SHA-256 `6a75baf4…ac06b10` |
| `crb-prometheus-binding-deleted.yaml`·`crb-prometheus-kubelet-scrape-deleted.yaml`·`sa-prometheus-deleted.yaml` | 삭제 직전 백업 |
| `checks.txt`·`deploy-after.txt`·`prom-log-tail.txt` | 적용 직후(18:33) Target·heartbeat·Deploy·로그 |
| `post-state.txt`·`post-remote-write.txt`·`path-diagnosis.txt` | 구 SA 삭제 후(18:50) 상태·remote_write 지표와 로그·NetworkPolicy·경로·GNP |

- Secret `monitor01-remote-write-auth`는 비밀번호를 담당자가 `read -s`로 직접 입력해 만들었다. 값과 Secret YAML은 이 폴더에 없다. 수집 전에 `kind: Secret`·`password:`·개인키 패턴을 검사해 0건임을 확인했다.
- `post-state.txt`의 `auth can-i get nodes/metrics … no`는 **명령 문법 오류**다. `nodes/metrics`가 subresource가 아니라 이름이 `metrics`인 node로 해석됐다(`--subresource=metrics`가 필요). 실제 권한은 `can-i-prometheus-sa.txt`와 kubelet Target UP으로 확인한다.
- 이제 참조가 없는 ClusterRole `prometheus-kubelet-scrape`는 남겨 두었다(`post-state.txt`에 참조 0 기록).

## `monitor01-console/` — 수신 측 SYN 관측

**콘솔 제출 자료**다(채팅 붙여넣기 원문, 서버 Hash 없음, 명령은 `commands.txt`). remote_write가 실패하는 중에 monitor01 `ens160`에서 TCP 443 SYN을 60초 동안 관측했고 결과는 0건이다.

## 판단과 후속

- Worker Calico GNP는 모두 `applyOnForward: false`(`path-diagnosis.txt`)라 Pod가 보내는 전달 트래픽에는 적용되지 않는다. K8s NetworkPolicy는 `10.250.10.30/32:443`을 허용한다. 따라서 차단 위치는 클러스터 밖, 즉 mgmt-gw01(`10.1.93.58`)의 서비스망 → 관리망 전달이나 반환 경로로 **추정**한다(미검증).
- ICR 요청: [#14 comment](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5854763610). Worker `.105/.107/.108` → `10.250.10.30` TCP 443 전달·반환 허용.
- 경로가 열린 뒤: 출발지 실측 → NGINX 443 기동 → 인수 시험 → heartbeat 5분 단절 시험(#17). 이 폴더는 #17 AC의 PASS 근거가 아니며, 반영 이력과 경로 진단 기록이다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
