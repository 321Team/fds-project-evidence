# P1-MON-01 — node-exporter DaemonSet 이미지 교체 `56566542…` → `4d5c92fc…` (2026-10-01 15:46~15:49 KST)

MON Lead(이재환)가 k8s-control01(`server02`, `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf`)에서 실행했다.
- 적용 소스: [infra-monitoring#32](https://github.com/321Team/infra-monitoring/pull/32)(hayeounglee APPROVED, GWONUK 병합 `f289f0f`) `kubernetes/monitoring/node-exporter.yaml`
- 이미지 승인: HBR Lead 확정 [#13 5925883099](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5925883099)(`fds/node-exporter@sha256:4d5c92fc…`, `1.12.1-fds.1`). 빌드·push·Trivy 증적 [evidence#88](https://github.com/321Team/fds-project-evidence/pull/88)
- 원복 기준: 이미지 줄을 `56566542…`로 되돌려 apply(Harbor에 원복 전용으로 보존). 실행하지 않았다.

**운영 변경:** `monitoring-node` DaemonSet `node-exporter`의 이미지 한 줄(generation 8→9). args(Collector 8개)·securityContext·probe·Service 변경 없음. RollingUpdate(maxUnavailable 1, maxSurge 0)로 Pod 3개가 노드별로 1회씩 교체됐다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/p1-mon-ne-apply-20261001T154610/` | control01 `~/p1-mon-ne-apply-20261001T154610/`(파일 21개 + `SHA256SUMS`) | `p1-mon-ne-apply-20261001.tar.xz` 5,180 B, SHA-256 `0ee28a22…820acd410` | base64로 받아 복원, 서버 `sha256sum`과 일치. 서버 `SHA256SUMS` 21줄 모두 OK. 개별 파일은 archive를 그대로 푼 것이다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. Secret·token·cookie 값은 없다(`pre/ds.yaml`은 DaemonSet 객체이며 `last-applied-configuration` 주석은 매니페스트 사본이다).

## 적용 전 (`pre/`, 15:46:18)

| 확인 | 근거 파일 | 결과 |
|---|---|---|
| 적용 파일 | `node-exporter.yaml` | SHA-256 `efe14761…501cf985` = #32 병합본(main `f289f0f`) |
| DaemonSet | `ds.yaml`, `ds-status.txt` | updateStrategy RollingUpdate maxUnavailable 1·maxSurge 0, desired 3 / ready 3 / updated 3 |
| Pod | `pods.txt` | `bbp2t`(worker01)·`qtvk2`(worker02)·`kwd76`(worker03) Ready, restarts 0, imageID `56566542…` |
| diff | `diff.txt`, `diff-rc.txt` | rc=1, 차이는 image 한 줄과 generation 8→9뿐 |
| dry-run | `dryrun.txt` | `daemonset.apps/node-exporter configured (server dry run)`, `service/node-exporter unchanged`. PodSecurity `warn=restricted` 경고는 namespace가 `enforce=privileged`인 기존 통제 예외에서 늘 나오는 것이다(차단 아님) |
| Prometheus | `prom.txt`, `pf.log` | `up{job="node-exporter"}` 3/3 = 1, collector 8, job별 Target 수(kubelet 6·node-exporter 3·kubelet-cadvisor 6·kube-state-metrics 1·transaction-api 3·fds-engine 3·prometheus 1) |

## 적용 (`chg-*`)

15:47:38 `kubectl apply -f node-exporter.yaml`(DaemonSet configured, Service unchanged) → 15:47:53 `rollout status` 성공(15초), `rollout rc=0`.

## 적용 후 (`post/`, 15:48~15:49)

| 확인 | 근거 파일 | 결과 |
|---|---|---|
| DaemonSet | `ds-status.txt` | desired 3 / ready 3 / updated 3 / available 3 |
| Pod | `pods.txt` | `4gtms`(worker01)·`thcn5`(worker02)·`zdhnv`(worker03) Ready, restarts 0, **imageID `4d5c92fcbea9fd5f2769a13192885366f6d348443ea6b48783590c9d9be43318`** |
| Pull | `pulled.txt` | 3개 모두 Harbor에서 `Successfully pulled`(255~268ms, 13,107,169 B) |
| 버전 | `version.txt` | 3개 Pod `kubectl exec … /bin/node_exporter --version`: `1.12.1-fds.1`, revision `6044da78…`, go1.26.8 |
| Prometheus | `prom.txt` | `up{job="node-exporter"}` 3/3 = 1, collector 8, `node_exporter_build_info` 3개 모두 version `1.12.1-fds.1`·goversion go1.26.8, job별 Target 수 적용 전과 같음 |
| 소스 ↔ 현장 | `diff.txt`, `diff-rc.txt` | **rc=0, 0 B** |

- port-forward(`19094`)는 조회 뒤 종료했다. port-forward는 kubelet 경유라 NetworkPolicy 경로 증명이 아니며, 여기서는 Prometheus API 조회에만 썼다.

## 판정 범위

- 이 증적이 보여 주는 것: HBR 확정 digest `4d5c92fc…`(Trivy Critical 0 / High 0)가 monitoring-node DaemonSet에 그대로 반영됐고, 3개 노드 수집·Collector 8개 구성이 유지됐다.
- 판단 대상: #17 "`monitoring-api` PSA Restricted와 `monitoring-node` 통제 예외를 적용한다"의 node-exporter 이미지 부분(Trivy·HBR 승인). 이 줄의 다른 조건(monitoring-node 임의 Workload 생성 제한 등)과 "모든 Image … Digest 고정·Trivy"(Alertmanager·Grafana `:latest`)는 이 증적만으로 체크하지 않는다.

AI 사용: CLAUDE_ASSISTED (명령 준비, 수신 대조·문서화, 실행은 담당자 본인)
