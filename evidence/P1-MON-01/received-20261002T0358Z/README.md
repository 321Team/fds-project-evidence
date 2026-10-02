# P1-MON-01 — kube-state-metrics digest 고정 현장 반영 (2026-10-02 12:56~12:58 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 실행했다. 앞선 수집회차 [`received-20261002T0302Z`](../received-20261002T0302Z/README.md)의 "KSM HOLD / NOT RUN"은 11:54 수집 당시의 사실이므로 고치지 않았다. 이 수집회차가 그 뒤의 반영 기록이다.

- 반영 근거:
  - HBR Lead 최종 처분 [#13 5945021427](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5945021427): Critical `CVE-2025-68121` 조사 결과 수용, Phase 1 조건부 예외, 만료 2026-10-26 23:59 KST, Phase 2 0/0 대체 필수
  - QA Gate OPEN [#17 5945086485](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5945086485)
- **운영 변경:** 12:57:01 `kubectl apply -f kube-state-metrics.yaml`([infra-monitoring#37](https://github.com/321Team/infra-monitoring/pull/37) 병합본, SHA-256 `9a6a68c5…`). Deployment `kube-state-metrics`가 configured됐고 Service는 unchanged다. Pod가 `kube-state-metrics-f88b9c457-n5n7x`(worker01)에서 `-77796bd485-7rq4h`(worker02)로 바뀌었다(RollingUpdate). 그 밖의 변경은 없다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-mon-pin-20261002T104441/apply-ksm-20261002T125613/`(파일 5개) | `control01-ksm-apply-20261002.tgz` 2,945 B, SHA-256 `2d811302…4de58f0a` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일 5개도 작업 중 서버가 출력한 SHA-256과 일치했다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다. 비밀 정보 검색 0건.

## #37 Gate (QA 필수 증적 1~6)

| # | 항목 | 결과 | 근거 |
|---|---|---|---|
| 1 | 적용 직전 `kubectl diff`·현장 YAML 백업 | 12:56:15 파일 SHA 확인 성공. diff는 `image` 한 줄(`:v2.13.0` → `@sha256:8ca59a98…`), `rc=1`로 10:46 diff와 같다. 백업 `pre-kube-state-metrics.yaml` `53bf940f…`가 10:46 백업과 같다(그사이 현장 변경 없음). Service 백업도 남겼다 | `pre.txt`, `pre-*.yaml` |
| 2 | apply/rollout rc | 12:57:01 configured, rollout `ksm_rc=0`, 12:57:08 종료 | `apply.txt` |
| 3 | 새 Pod imageID exact digest | spec `@sha256:8ca59a98…`, 새 Pod imageID `@sha256:8ca59a98…`(적용 전과 같은 digest = 이미지 불변), 재시작 0 | `post.txt` |
| 4 | Target·관련 metrics 회귀 | 12:58:10 `up{job="kube-state-metrics"}` 1, `count(up)` 23 / `up==1` 23, `count(kube_pod_info)` 44, `count(kube_deployment_status_replicas)` 8, firing 알림 없음 | `post.txt` |
| 5 | 사후 `kubectl diff` 0 | `rc=0` | `post.txt` |
| 6 | 원본 로그 + SHA | 이 폴더(`SHA256SUMS`, archive sidecar) | — |

- Alertmanager·Grafana·Prometheus Pod는 변하지 않았다(재시작 0).
- KSM 로그에 `validatingwebhookconfigurations`·`certificatesigningrequests`·`storageclasses` 조회 forbidden 오류가 있다(`post.txt`).
  - 이 세 리소스는 D33 최소 권한 RBAC(`rbac-kube-state-metrics.yaml`)가 일부러 주지 않는 것이다. 이번 변경은 이미지 줄뿐이고 인자와 RBAC는 그대로다.
  - 그래서 이번 반영 때문에 생긴 회귀가 아니라 기존 현상으로 판단한다. 이전 Pod 로그는 확인하지 않았다(NOT VERIFIED).
  - 쓰는 지표(`kube_pod_info` 등)는 정상이다. 수집 대상을 `--resources=`로 줄이는 것은 Phase 2 후속 후보다.

## 판정 범위

- 이로써 Alertmanager·Grafana(`received-20261002T0302Z`)와 KSM(이 수집회차)의 현장 이미지가 모두 #37 digest로 고정됐다. **AC 체크는 이 증적 병합 뒤 따로 판단한다.**
- 이 반영은 취약점 해소가 아니다. Phase 1 조건부 예외(만료 2026-10-26 23:59 KST)이며 Phase 2에서 0/0 대체 digest로 바꿔야 한다.
