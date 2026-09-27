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

## `control01-mon11-ksm/` — KSM 공식 Probe 현장 반영 (2026-09-27 15:32 KST)
[infra-monitoring#11](https://github.com/321Team/infra-monitoring/pull/11)(merge 2026-09-26)의 KSM Probe를 현장 Deployment에 `kubectl patch`로 반영했다. **운영 변경: KSM Pod 1회 교체.** 서버 폴더 `~/mon11-ksm-20260927T063238`, archive `06d856cf…76f76822`(수신 대조 일치).
- 적용 전 포트 이름 확인 `http-metrics:8080 telemetry:8081` → readiness `/readyz`(telemetry)·liveness `/livez`(http-metrics), `initialDelaySeconds 5`·`timeoutSeconds 5`(`ksm-before/after.yaml`, `ksm-probes.txt`)
- rollout 후 120초 관찰: `ready=true restarts=0`, Probe 실패 이벤트 0(`ksm-pod.txt`, `ksm-probe-events.txt`)
- 전체 모니터링 Pod(`all-pods.txt`, `all-probes.txt`, `unhealthy-events.txt`, `restart-reasons.txt`): 7개 모두 Ready, Unhealthy 이벤트 0. 재시작 1~2회는 모두 `Unknown/255`, 2026-09-27 04:35~04:50Z(Worker 재부팅 시험 시간대, evidence#52)이다.
- **확인된 공백:** node-exporter DaemonSet에 **livenessProbe가 없다**(readiness `/metrics`만). 현장 startupProbe `timeoutSeconds`는 1로, infra-monitoring main(`ee4f93f` 이후 3)과 다르다.

## `monitor01-lb-probe/` — monitor01 receiver·Blackbox 기동과 API LB Probe 실패·복구 (2026-09-27 15:47~16:06 KST)
MON Lead(이재환)가 monitor01(`server01_monitor`)에서 실행했다. [infra-monitoring#19](https://github.com/321Team/infra-monitoring/pull/19) `monitor01/DEPLOY_PLAN_20260929.md`의 9/29 항목을 앞당겨 수행했다. 서버 폴더 `~/mon01-images-20260927T154710/evidence-*`를 tar.gz(4,520 B, SHA-256 `3b606025…50202e`)로 받았고, archive와 서버 `sha256sum`(`server-sha256sums.txt`)이 수신본과 일치한다. **운영 변경: monitor01에 컨테이너 2개(`fds-blackbox`, `fds-receiver`, 모두 127.0.0.1 전용) 기동, 설정 파일 3개(`/etc/fds/monitor01/...`) 생성, 시험 중 3분간 monitor01 런타임 방화벽 direct rule 1개(시험 후 제거, 잔존 0).**

**이미지 반입 방식 (계획과 다른 점)**
- 원격 작업이라 계획의 ansible01 → monitor01 파일 전달이 어려웠다. monitor01에서 인터넷 레지스트리 도달을 확인(`registry-1.docker.io`·`quay.io` `/v2/` HTTP 401)하고 **monitor01에서 직접 pull**했다. digest는 pull 결과로 고정했고, 같은 monitor01에서 Trivy `0.74.0`(`docker.io/aquasec/trivy:0.74.0`) 컨테이너로 HIGH/CRITICAL을 검사했다(`--ignore-unfixed=false`, `--scanners vuln`). Harbor `fds/` 사본은 만들지 않았다.
- 검사 결과(`trivy-summary.txt`, 원본 JSON은 monitor01 보관·SHA-256만 기록):
  - #17에서 정한 nginx `1.30.5`(debian) HIGH 66/CRITICAL 1, blackbox-exporter `v0.28.0` HIGH 39/CRITICAL 2 → **BLOCK**. 비교한 nginx `1.30.5-alpine`도 HIGH 1로 BLOCK.
  - **PASS(0/0)로 채택:** nginx `cgr.dev/chainguard/nginx@sha256:1cb61392…` (wolfi), Prometheus `docker.io/prom/prometheus:v3.15.0@sha256:86b17a25…`, blackbox **직접 빌드** `localhost/fds/blackbox-exporter:0.28.0-master.065fc18`(image ID `8d75253e…`).
  - blackbox 직접 빌드 이유: 공식 최신 릴리스 v0.28.0에 수정된 의존성이 없다(upstream issue #1668 open). Chainguard blackbox·prometheus는 무료 제공이 아니다(403). 빌드 입력은 소스 `prometheus/blackbox_exporter@065fc188bd76…`(tar SHA-256 `952651a8…`, `bb-src.sha256`), `golang:1.25@sha256:54b6b88d…`(go1.25.14), base `cgr.dev/chainguard/static@sha256:c5fed92d…`, `Containerfile.blackbox`, `build.log`(`--version` 출력 포함)다.
- 이 방식은 [#17 ICR 결정](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5846829418)(Harbor digest·Trivy 후 파일 전달)과 다르다. 이미지 변경은 HBR 확인 대상이다. monitor01의 인터넷 egress는 SEC 확인 대상이다.

**기동 확인**: `promtool check config` SUCCESS(rule 1개 포함). `containers.txt`에 두 컨테이너 Up. `listeners.txt`에 `127.0.0.1:9115`·`127.0.0.1:19090`만 있다. `probe-direct.txt`·`probe-receiver.json`은 `probe_success{instance="10.1.93.109:6443"}` = 1.

**API LB TCP Probe 실패·복구** (`lb-fault-timeline.txt`, `probe-range.json`)
- 16:00:50 정상(1) → 16:00:51 monitor01 OUTPUT에 `.109:6443` REJECT(runtime direct rule) → 16:01:21~16:03:51 **0**(30초 간격 6회) → 16:03:51 규칙 제거 → 16:04:21~16:05:51 **1**. query_range(step 15s) 25점 `1111100000000000011111111`. 시험 후 direct rule 0개.
- 이 시험은 **monitor01 관점의 Probe 실패 유도**다. LB 자체 장애 시험은 P1-LB-01 범위다.

**미포함·후속**: NGINX(443)·sender `remote_write`·heartbeat 단절 시험은 9/30~10/1 예정이다. 컨테이너 재부팅 자동 기동(`--restart=unless-stopped` 외 systemd 연계)은 확인하지 않았다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·문서화, 실행은 담당자 본인)
