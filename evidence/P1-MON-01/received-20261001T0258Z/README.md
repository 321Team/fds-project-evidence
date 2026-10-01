# P1-MON-01 — 클러스터 Prometheus v3.15.0 적용과 Harbor read-only 확인 (2026-10-01 11:36~11:56 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 실행했다.
1. Harbor read-only 조회(11:36~11:47): #13 HBR 요청 확인 항목, #17 적용 전 필수 Gate ①②
2. [infra-monitoring#29](https://github.com/321Team/infra-monitoring/pull/29)(GWONUK APPROVED, merge `588bc7c`)의 `prometheus.yaml` 클러스터 적용(11:49~11:56)

**운영 변경:** `monitoring-api` ConfigMap `prometheus-config`(주석만), Deployment `prometheus`(이미지 `:latest`(=v3.14.0 `b77f9cee…`) → `@sha256:2c28708b…`(v3.15.0), resources `{}` → requests 200m/448Mi · limits 500m/896Mi). Recreate로 Pod 1회 교체. Service·PVC·RBAC·NetworkPolicy·Secret 변경 없음. Grafana·Alertmanager 재시작 없음.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-mon-harbor-ro-20261001T113657/`, `~/p1-mon-prom315-apply-20261001T114946/`(파일 46개) | 원본 `p1-mon-prom315-20261001.tar.xz` 14,440 B, SHA-256 `3f8cbd6e…6d595d126e` → **Git에는 파생본 `p1-mon-prom315-20261001-sanitized.tar.xz`만 둔다** | 원본은 base64로 받아 복원했고 서버 `sha256sum`과 일치했다. 파생본은 응답 헤더 2개의 `Set-Cookie: sid=` 값만 `<REDACTED>`로 바꾼 것이다(`control01/SANITIZED_FILES.txt`에 두 파일의 원본·파생본 SHA-256). 개별 파일은 파생본을 그대로 푼 것이다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 원본 archive(`sid` 값 포함)는 Git에 넣지 않고 control01 `~/p1-mon-prom315-20261001.tar.xz`에만 둔다. 그래서 서버에서 만든 `p1-mon-harbor-ro-20261001T113657/SHA256SUMS`의 `hdr-*.txt` 두 줄은 원본 바이트 기준이라 파생본과 다르다(나머지 줄은 같다). 이 폴더 전체는 수집회차 `SHA256SUMS`가 파생본 기준으로 확인한다.

## 1. Harbor read-only 조회 (`p1-mon-harbor-ro-20261001T113657/`)

- 근거: [#13 HBR 5923320268](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5923320268)(조회만 허용), 회의(2026-10-01) HBR Lead 구두 승인으로 `robot$push` 사용. TLS 검증 유지(`--cacert ca.pem`, 현장 ConfigMap `monitor01-root-ca` Root PEM SHA-256 `20ddfa5e…053f`). 자격증명은 실행 중 입력하고 파일·명령줄에 남기지 않았다.
- 1차 시도(`fds_app`)는 Harbor 인증 실패(401)였다. `me.json`·`proj.json`이 그때 진단 응답(401)이다. 이후 `robot$push`로 다시 실행해 manifest·artifact·summary 파일을 덮어썼다. `SHA256SUMS`는 2차 결과 기준이다.

| 대상 | 결과 | 판단 |
|---|---|---|
| `fds/prometheus@sha256:2c28708bb561e4ceadac83bd2b60054a1a5381426a13f7b12bbd1bf2a8dd2d19` raw manifest | HTTP 200, 내용 SHA-256 = digest, docker v2, layers 9, **`config.digest` = `sha256:66416213a3b43651d3521acc3987277b4f97ad0ae29acc581f910ef9bd3959bd`** Gate ② **authenticated manifest read·identity PASS**. monitor01 docker-archive config(`66416213…`)와 일치 — #17 Gate B 판단 입력. 이 조회 자체는 layer blob까지 받는 full pull이 아니다. 같은 digest의 실제 pull은 아래 2절 적용(Pod가 `2c28708b…`로 Running, `post/imageid.txt`)과 evidence#85 시험 Pod(worker02, 새로 받음)로 따로 확인된다 |
| `fds/prometheus@sha256:b77f9cee82fd1c61521634d2d6b192fc526ffd938e904b8e6836b6c0cf8d875a` raw manifest | HTTP 200, 내용 SHA-256 = digest, config `sha256:31c1e0aa…45bd` Gate ① **artifact presence·authenticated manifest read PASS / full image pull NOT VERIFIED**(이번에 pull하지 않았다. worker03 노드 이미지 목록에 같은 digest가 있음은 아래 보조 관측) |
| artifact API 3건(scan overview, node-exporter `56566542…` 포함) | HTTP 403(`robot$push` 권한 밖) | **NOT VERIFIED** — node-exporter Trivy 결과는 HBR 확인 대상으로 남는다 |

- 보조: worker03 Node 이미지 목록에 `fds/prometheus@sha256:b77f9cee…`(111,939,124 B)가 있다(작업 화면 조회, 파일 미저장).
- `ca.pem`(공개 Root, SHA-256 `20ddfa5e…053f`)은 저장소 `.gitignore`의 `*.pem` 규칙에 따라 풀어 둔 파일로는 편입하지 않았다. 원본은 archive 안에 그대로 있고, 내용은 infra-monitoring `monitor01-remote-write.yaml`의 Root PEM과 같다. 서버 쪽 `SHA256SUMS`에는 이 줄이 남아 있다.
- `hdr-*.txt`는 응답 헤더다. Harbor가 응답마다 붙이는 `Set-Cookie: sid=` 값은 **`<REDACTED>`로 가린 파생본**만 편입했다(만료 여부와 관계없이 세션 식별자는 Git에 두지 않는다). 다른 헤더 줄은 원본 그대로다. 요청 헤더(Authorization·token)는 처음부터 저장하지 않았다.

## 2. Prometheus v3.15.0 적용 (`p1-mon-prom315-apply-20261001T114946/`)

| 항목 | 내용 |
|---|---|
| 적용 소스 | infra-monitoring main `588bc7c`의 `kubernetes/monitoring/prometheus.yaml` — 현장 파일 `prometheus.yaml` SHA-256 `19ef7e89…94c3929`, git blob `021b3e04ffeee8ff1580c3d8ad64b351844c38bd`(main과 일치, Gate ③) |
| 적용 전 기록(Gate ④) | `pre/`: Deployment YAML 전체, RS·Pod, imageID `b77f9cee…`, buildinfo 3.14.0, TSDB, Rule, Alertmanager, `count(up)`, remote_write 실패 카운터, diff(rc=1, 이미지·resources·주석·generation), server dry-run(rc=0) |
| 원복 기준 | [5922395260](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5922395260)·[5922778973](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5922778973): 1차 `set image …@sha256:b77f9cee…`, 2차 `pre/deploy.yaml` 기준 전체 복구. 실행하지 않았다 |
| 실행 | 11:52:25 `kubectl apply -f prometheus.yaml`(ConfigMap·Deployment configured, Service unchanged) → 11:53:06 `rollout status` 성공(41초) — `chg/` |

**적용 전 → 적용 후 (`pre/` → `post/`)**

| 확인 | 적용 전 | 적용 후 |
|---|---|---|
| imageID / 버전 | `b77f9cee…` / 3.14.0 (`d7598b7`) | **`2c28708b…` / 3.15.0 (`5241a27`, go1.27.1)** |
| Pod | `prometheus-5c6cd4bc84-b2zpq` | `prometheus-d8949bd64-tvptk`, worker03, restarts 0, lastState 없음(OOM 없음) |
| resources | `{}`(LimitRange 기본 512Mi, 9/30 조회 `GOMEMLIMIT` 483,183,820) | 200m/448Mi · 500m/896Mi(`GOMEMLIMIT` 845,571,686 = 896Mi×0.9) |
| 설정 | — | `promtool check config` rc=0(Rule 파일 포함), reload 정상 |
| Rule | 8개, bad 0 | 8개, bad 0 |
| Target | `count(up)` 23 / `up==1` 23 | 23 / 23 |
| TSDB | numSeries 29,990, minTime 1790812800000 | 30,284, minTime **같음**(PVC 데이터 유지) |
| 연속성 | — | 적용 전 30분~적용 후 `count(up)` query_range 141점, 15초 간격 공백 없음 |
| Alertmanager / Grafana Datasource | 1개 연결 | 1개 연결 / `OK` |
| 소스 ↔ 현장 | diff rc=1 | **사후 diff rc=0, 0 B** |

- Deployment `imagePullPolicy`는 기존 값 `Always`가 유지된다(digest 참조라 같은 이미지만 받음).

## 판정 범위

- 이 증적이 보여 주는 것: Harbor digest `2c28708b…`로 고정한 v3.15.0이 클러스터에 그대로 반영됐고, 수집·Rule·Alert·Datasource·PVC 데이터가 유지됐다. 원복 대상 v3.14.0 digest는 Harbor에 manifest로 남아 있다(full pull NOT VERIFIED).
- Trivy: 이 수집의 artifact API는 403이라 **Trivy를 재검증하지 않았다**. `2c28708b…` Trivy 0/0은 기존 HBR 기록 참조다(9/30 스캔, #13). 10/1 `admin` 재조회 결과는 [evidence#85](https://github.com/321Team/fds-project-evidence/pull/85) `art-prometheus-2c28708bb561.json`(Critical·High 없음, Unknown 1)이다.
- 판단 대상: #17 핵심 요구 "모든 Image는 Harbor 승인 Repository의 Digest로 고정하고 Trivy 결과를 연결한다"(Prometheus 부분), "Prometheus·Grafana·Alertmanager PVC와 Resource Request/Limit을 정의한다"(Prometheus 부분). Alertmanager·Grafana는 아직 `:latest`라 두 줄 모두 이 증적만으로 체크하지 않는다.
- 범위 밖: monitor01 receiver(Gate B 판정·기동), remote_write Positive(monitor01 HOLD), node-exporter Trivy 결과(403, HBR 확인 대상).

AI 사용: CLAUDE_ASSISTED (명령 준비, 수신 대조·판정·문서화, 실행은 담당자 본인)
