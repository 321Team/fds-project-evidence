# P1-MON-01 — 소스·현장 정합(infra-monitoring#28) 현장 반영과 사후 확인 (2026-09-30 17:32~17:41 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 [infra-monitoring#28](https://github.com/321Team/infra-monitoring/pull/28)(GWONUK APPROVED [5363524502](https://github.com/321Team/infra-monitoring/pull/28#pullrequestreview-5363524502), merge `fa208c7`)의 세 파일을 현장에 반영하고, 반영 전·후에 같은 확인을 돌렸다. #28 승인 경계("RUNTIME NOT RUN — 병합 후 MON Lead 적용 Gate에서 별도 확인")와 리뷰의 "Runtime 필수 확인" 6개에 대한 결과를 이 증적으로 따로 검토받는다.

**운영 변경:** `monitoring-api` ConfigMap 3개(`prometheus-alert-rules`, `grafana-dashboards-provider`, `grafana-dashboards`) 갱신, `monitoring-node` DaemonSet `node-exporter` 실행 인자 변경(Pod 3개 순차 교체). Prometheus·Grafana·Alertmanager는 재시작하지 않았다(설정 다시 읽기만). `grafana.yaml`(Deployment 포함)은 적용하지 않았다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/src-check/` | `~/p1-mon-src-20260930T164408/` (파일 27개) — 반영 전 소스 대조(#28 작성 근거) | `p1-mon-src-20260930T164408.tar.xz` 19,824 B, SHA-256 `1f710689…61fd63fd` | base64로 받아 복원, 서버 `sha256sum`과 일치. 개별 파일은 archive를 그대로 푼 것이다 |
| `control01/sync/` | `~/p1-mon-sync-20260930T173234/` (파일 83개, 전달 묶음 `applykit.tgz`는 제외하고 묶음) — 반영 전 확인·반영·사후 확인 | `p1-mon-sync-20260930T173234.tar.xz` 30,040 B, SHA-256 `e7405e3a…89a359c8` | 같음 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. `control01/sync/applykit.tgz.b64`는 서버에 붙여 넣은 전달 묶음 원문이다(`applykit.tgz` SHA-256 `eaf88f78…9d787050`, 서버 `sha256sum -c` 성공).

## 적용 기록 (REVIEW_AUTHORITY_POLICY §4 — 운영 Runtime)

| 항목 | 내용 |
|---|---|
| 적용 소스 | infra-monitoring main `e4acbdc`의 `kubernetes/monitoring/` `alert-rules.yaml`(blob `0a64b7a`, SHA-256 `f0b3717e…7be0d0d3`), `grafana-dashboards.yaml`(blob `c5037d4`, `bde06eef…ddecd5df`), `node-exporter.yaml`(blob `efde5c9`, `848dbba6…43885c6e`). #28 병합(`fa208c7`) 뒤 main에 들어온 #27은 `monitor01/` 문서만 바꿔 세 파일은 #28 승인본과 같다 |
| 전달 | PC에서 세 파일·확인 스크립트·기준값을 tar.gz→base64로 붙여 넣고 복원, 서버 `sha256sum -c` 성공, 파일 5개의 SHA-256 출력이 main 원본과 일치(작업 화면 출력이며, `sync/`에 보존된 파일로 재계산할 수 있다) |
| 선행조건 | 반영 전 확인(`sync/out-pre/`)에서 Prometheus `--web.enable-lifecycle` 있음, node_exporter 1.12.1 ×3·Target 3/3 UP, DaemonSet RollingUpdate(`maxUnavailable: 1`)·3/3 Ready, `node_exporter --help`에 사용할 옵션 9개 존재(`sync/pre-diff/node-exporter-help.txt`), `kubectl diff` 대상은 ConfigMap 3개·DaemonSet 1개뿐, server dry-run rc=0(PVC `grafana-data`·Service `unchanged`) |
| 성공 기준 | Rule 파일 반영 후 Prometheus reload 성공·두 Alert `known_issue` 없음·health ok, Grafana 대시보드 4개 `provisioned=True`, node-exporter 순차 교체 완료·Target 3/3 UP·Collector 8개, ConfigMap 소스 대조 SAME, 사후 `kubectl diff` 차이 없음, 전체 수집 대상 23/23 UP 유지, Prometheus·Grafana 재시작 없음 |
| 복구 방법 | `sync/backup/`의 반영 전 객체 4개(ConfigMap 3개·DaemonSet)로 원복, node-exporter는 `kubectl rollout undo`. 성공 기준을 모두 충족해 실행하지 않았다 |
| 실행 | `sync/chg/rc.txt`(각 단계 종료 코드·시각), `sync/chg/apply-*.txt`, `sync/chg/rollout.txt`, `sync/chg/*-reload.txt` |

실행 순서(KST):

1. 17:32:34 반영 전 확인(`mon-src-check.sh pre`), `kubectl diff` 3개(rc=1 ×3, `sync/pre-diff/`), server dry-run(rc=0)
2. 17:35 반영 전 객체 백업 4개(`sync/backup/`)
3. 17:35:11 `kubectl apply -f alert-rules.yaml`(ConfigMap 1 configured), `kubectl apply -f grafana-dashboards.yaml`(ConfigMap 2 configured, PVC unchanged)
4. 17:36:22 Pod 안 파일 3개가 새 SHA로 바뀐 것을 확인(14번째 시도) → Prometheus `POST /-/reload` rc=0, Grafana `POST /api/admin/provisioning/dashboards/reload` rc=0(`{"message":"Dashboards config reloaded"}`)
5. 17:37:39 `kubectl apply -f node-exporter.yaml`(DaemonSet configured, Service unchanged) → 17:37:56 `rollout status` 성공(Pod 3개 한 대씩, generation 7→8)
6. 17:38:56 사후 확인(`mon-src-check.sh post`), 사후 `kubectl diff` 3개(rc=0 ×3, 출력 0 B — `sync/post-diff-*.txt`, rc는 `sync/chg/rc.txt`)
7. 17:40:46 전체 수집 대상 수(`sync/chg/targets-all.txt`)

- dry-run·apply 때 나온 PodSecurity `Warning`은 `monitoring-node`의 `warn=restricted` 라벨에 따른 경고다. 강제 기준은 `enforce=privileged`(정본 통제 예외)이고, 경고 항목(hostNetwork·hostPID·hostPort·hostPath·runAsNonRoot)은 반영 전 현장과 같다. 이번 변경은 실행 인자만 바꿨다.

## 확인 스크립트 `mon-src-check.sh` — 순수 검증기 분류

REVIEW_AUTHORITY_POLICY §3.2 4-1에 따라 담당 Lead가 순수 검증기로 판단해 실행했다. 반영 전 기록은 첫 판(`src-check/mon-src-check.sh`, SHA-256 `7dee4d7a…16dfdfdd`, 기준값 main `d71d00c`), 반영 전·후 확인은 조회 항목을 늘린 판(`sync/mon-src-check.sh`, `08f6405e…7cf519fd`, 기준값 main `e4acbdc`)이다.

- `kubectl get`, Prometheus·Grafana 읽기 API, Pod 안 `sha256sum` 조회만 한다. 객체 생성·변경·삭제, 재시작·reload, 설치·상주가 없다(조건 1·2). reload·apply는 스크립트 밖에서 위 실행 순서대로 따로 했다.
- 결과는 실행 폴더의 `out/`·`out-pre/`·`out-post/`에만 남기고 운영 설정 입력으로 쓰지 않는다(조건 3).
- 기존 계정(`server02` + admin kubeconfig)과 Grafana Pod 안의 기존 관리자 환경 변수만 쓰고 값을 출력하지 않는다(조건 4).
- 부하·장애 주입·대량 스캔이 없다(조건 5).
- `node_exporter --help`·`--version`은 실행 중인 Pod 안에서 출력만 하는 조회다.

## 결과

**#28 리뷰 "Runtime 필수 확인"과 대조**

| 리뷰 확인 항목 | 반영 전 (`sync/out-pre/`) | 반영 후 (`sync/out-post/`) |
|---|---|---|
| 1. node_exporter build/version·옵션 지원 | 1.12.1(revision `6044da7`) ×3, `--collector.disable-defaults`와 8개 옵션 모두 `--help`에 있음 | 같은 버전(이미지 digest 고정) |
| 2. DaemonSet RollingUpdate 3/3 Ready | desired 3 / updated 3 / ready 3, generation 7 | desired 3 / updated 3 / ready 3, generation 8(observed 8) |
| 3. Target 3/3 UP, Collector 8개 | UP 3/3, Collector 49개(기본값) | UP 3/3, Collector **8개**(cpu·diskstats·filesystem·loadavg·meminfo·netdev·time·timex) 모두 success=1 |
| 4. Grafana 대시보드 4개 로드, UI 저장 차단 | 4개, 모두 `provisioned=False`(provider `allowUiUpdates: true`) | 4개, 모두 `provisioned=True`. `fds-overview`는 소스 판으로 갱신(version 2→3) |
| 5. Rule reload 성공, `known_issue` 제거 | `NodeExporterDown`·`KubeletScrapeDown` `known_issue=gnp-crossnode-pod-cidr` | reload 성공(`last_reload_successful`=1, 성공 시각 17:36:22), 두 Alert `known_issue=-`, health ok, severity 그대로(warning/info) |
| 6. 실패 시 원복 | 백업 4개 준비 | 실행 안 함(성공 기준 충족) |

**소스 ↔ 현장 (`cm-compare.txt`, 키별 SHA-256)**

| 대상 | 반영 전 | 반영 후 |
|---|---|---|
| `prometheus-alert-rules` `alert-rules.yml` | DIFF(`bca9426a`) | SAME(`2ffbb777`) |
| `grafana-dashboards-provider` `provider.yaml` | DIFF(`e23193cc`) | SAME(`077da836`) |
| `grafana-dashboards` `fds-overview.json`(P0 아님) | DIFF(`ff150e57`, 8패널) | SAME(`2b6c20b0`) |
| P0 대시보드 3개, 선택 Alert, P0 시험 Alert | SAME | SAME |
| `grafana-datasources` `datasource.yaml` | DIFF(주석만) | DIFF(주석만) — #28 범위 밖, `grafana.yaml` 미적용 |
| 사후 `kubectl diff` 3개 | — | rc=0, 출력 0 B |

**영향 없음 확인**

- 전체 수집 대상 `count(up)`=23, `count(up==1)`=23(17:40:46).
- Pod 안 파일: Rule `2ffbb777…`, provider `077da836…`로 반영(`apply-state.txt`).
- `monitoring-api` Pod 재시작 없음: Prometheus·Grafana·Alertmanager restart 0, 시작 시각 9/27 그대로(KSM restart 2는 기존 값).
- `monitoring-node` PSA 라벨(enforce=privileged, audit/warn=restricted)과 node-exporter 보안 설정(privileged=false, HostPath read-only 등)은 반영 전후 같다(`node-summary.txt`).

## 판정 범위

- 이 증적이 보여 주는 것: #28의 소스 정리가 현장에 그대로 반영됐고(사후 diff 출력 없음, ConfigMap SHA 일치), 해소된 `known_issue` 라벨 제거·대시보드 화면 저장 차단(`provisioned=True`)·node-exporter Collector 8개 축소가 재시작 없이(node-exporter는 순차 교체) 이뤄졌으며, 그 뒤에도 수집 대상 23/23과 Alert Rule health가 유지된다.
- 판단 대상: #17 핵심 요구 "P0 기본 Dashboard 3종과 기본 Alert Rule을 Source 관리한다", "`monitoring-api` PSA Restricted와 `monitoring-node` 통제 예외를 적용한다"(정본 monitoring-node 행 "불필요 Collector 비활성"). 체크 여부는 이 PR 독립 리뷰 뒤 MON Lead가 판단한다.
- 한계: 화면 저장 차단은 `provisioned=True` 표시로 확인했고 실제 저장 시도는 하지 않았다(변경 행위). `grafana-datasources`의 주석 차이와 `grafana.yaml`(Deployment)은 이번 범위 밖이다. Prometheus는 여전히 `3.14.0`이며 v3.15.0 교체는 infra-monitoring#27 Gate로 따로 진행한다.
- `sync/out-*/cm-*.json`·`sync/backup/*.yaml`은 현장 객체 조회본이다(`kubectl.kubernetes.io/last-applied-configuration` 포함). Secret 값은 없다(`harbor-pull-secret` 등 이름만 있음).

AI 사용: CLAUDE_ASSISTED (명령·확인 스크립트·전달 묶음 준비, 수신 대조·판정·문서화, 실행은 담당자 본인)
