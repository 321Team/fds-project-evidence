# P1-MON-01 — 모니터링 이미지 digest 근거·Harbor Trivy 결과, Alertmanager·Grafana digest 고정 현장 반영 (2026-10-02 10:34~11:54 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 실행했다. 코드 변경은 [infra-monitoring#37](https://github.com/321Team/infra-monitoring/pull/37)(merge `4cf6c41`), 현장 반영 보고는 [fds-project-baseline#17 5944766163](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-5944766163)이다.

**운영 변경:** 11:53:37 `kubectl apply`로 `monitoring-api` Deployment `alertmanager`·`grafana`, ConfigMap `grafana-datasources`를 바꿨다(Pod `alertmanager-774f8866d-ppgqn` → `-6bf6dc555-nhtnn`, `grafana-559b978c69-k2ws6` → `-f65457bfd-p4j4t`). **kube-state-metrics는 반영하지 않았다**(HBR Lead 최종 확인 전 HOLD). Harbor에서 세 artifact에 Trivy 스캔을 요청했다(10:37). 그 밖의 변경은 없다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` (digest 근거) | `~/p1-mon-digest-pre-20261002T103421/`, `~/p1-mon-digest-trivy-20261002T103638/`, `~/p1-mon-pin-20261002T104441/`(파일 17개) | `control01-digest-pin-20261002.tgz` 14,042 B, SHA-256 `ba53008b…8f24be74e5` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일도 서버 `digest-pin-SHA256SUMS`와 일치했다 |
| `control01/` (적용 기록) | `~/p1-mon-pin-20261002T104441/apply-20261002T115040/`(파일 6개) | `control01-pin-apply-20261002.tgz` 4,282 B, SHA-256 `9ab60e54…8f9f730b` | 같은 방식. 개별 파일 6개가 작업 중 서버가 출력한 SHA-256과 일치했다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다. 비밀 정보 검색 0건(`ca.crt`는 Harbor 접속용 공개 CA 인증서, YAML의 `secretName`·`secretKeyRef`는 이름 참조뿐이다). Harbor 취약점 상세 JSON(`/additions/vulnerabilities`)은 크기 때문에 묶지 않았다. CVE 목록은 `summary.txt`에 있다.

## 1. 현장 digest 확인 (`p1-mon-digest-pre-20261002T103421/digest-pre.txt`, 10:34)

| Deployment | spec 이미지 | 실행 Pod imageID |
|---|---|---|
| alertmanager | `fds/alertmanager:latest`, `Always` | `@sha256:babefaac…ab67` |
| grafana | `fds/grafana:latest`, `Always` | `@sha256:7a1ff544…7d5b` |
| kube-state-metrics | `fds/kube-state-metrics:v2.13.0`, `IfNotPresent` | `@sha256:8ca59a98…22a1` |
| prometheus(참고) | `fds/prometheus@sha256:2c28708b…` | 같음 |

고정할 digest는 이 실행 중 imageID를 그대로 쓴다. 그래서 고정 자체로는 이미지가 바뀌지 않는다.

## 2. Harbor artifact·Trivy (`p1-mon-digest-trivy-20261002T103638/`)

- `art-*-pre.json`(10:37): Harbor `fds` 프로젝트 artifact 조회. 세 digest 모두 Harbor에 있고 `scan_overview`가 없다(스캔 이력 없음).
- 10:37 Harbor admin으로 스캔을 요청했다(`robot$push`는 스캔 API 403).
- `art-*.json`(10:39): 스캔 결과. Scanner Trivy `v0.62.1`, 세 개 모두 `Success`(01:37:42Z 시작).

| artifact | digest | tag | push | Trivy 요약 |
|---|---|---|---|---|
| alertmanager | `babefaac…ab67` | `latest` | 2026-09-22 06:25Z | High 1, Medium 2, Low 4, Unknown 1 |
| grafana | `7a1ff544…7d5b` | `latest` | 2026-09-22 06:25Z | High 72, Medium 30, Low 25, Unknown 3 |
| kube-state-metrics | `8ca59a98…22a1` | `v2.13.0` | 2026-09-22 06:25Z | **Critical 1**, High 44, Medium 47, Low 4, Unknown 3 |

- `summary.txt`: 위 요약과 High·Critical CVE·패키지·수정 버전 목록(grafana 72건 중 40건, KSM 45건 중 40건 표시).
- 처분은 HBR이 했다: [#13 5944401484](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5944401484), 예외 기록 [5944486155](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5944486155), 만료 보정 [5944712059](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5944712059)(2026-10-26 23:59 KST), QA STOP 해제 [5944664142](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5944664142). **이 고정은 취약점 해소가 아니다.** Phase 2에서 0/0 대체 digest로 바꿔야 한다.

## 3. 반영 전 diff·백업 (`p1-mon-pin-20261002T104441/`, 10:46)

- `alertmanager-deploy.yaml`·`grafana.yaml`·`kube-state-metrics.yaml`: #37 병합본. SHA-256 `57bc3112…`·`e14956e9…`·`9a6a68c5…`가 저장소 main 파일과 같다.
- `diff.txt`(`kubectl diff`): 이미지 3줄(tag → digest), Alertmanager `resources: {}` → 명시(requests 200m/256Mi, limits 500m/512Mi), Grafana memory requests 256Mi → 1152Mi·limits 1Gi → 2304Mi, `grafana-datasources` URL 줄 주석 1개.
- `node-w3.txt`: k8s-worker03 `describe node`(10:51). Alertmanager는 그때 이미 LimitRange 기본값(200m/500m, 256Mi/512Mi)으로 실행 중이었다. 명시해도 값은 같다. Grafana 메모리 증가분을 더해도 worker03 memory requests는 1536Mi + 896Mi로 할당 가능량 약 23Gi 안이다.
- `pre-*.yaml`: 반영 전 현장 YAML 백업(되돌리기용).

## 4. 현장 반영 (`apply-20261002T115040/`, 11:50~11:54)

worker02 Drain 재시험 종료(노드 6대 Ready, SchedulingDisabled 없음)를 확인한 뒤 진행했다.

| 단계 | 결과 | 근거 |
|---|---|---|
| 사전 11:50:40 | 두 파일 `diff` 내용이 10:46과 같다. 백업 `pre-alertmanager.yaml`·`pre-grafana.yaml` SHA가 10:46 백업과 같다(그사이 현장 변경 없음) | `pre.txt`, `pre-*.yaml` |
| 적용 11:53:37 | `deployment.apps/alertmanager`·`grafana` configured, `configmap/grafana-datasources` configured, Service 2개 unchanged. rollout `am_rc=0`·`gf_rc=0`, 11:53:44 종료 | `apply.txt` |
| 사후 11:54:02 | spec 이미지 = digest(alertmanager·grafana), 새 Pod imageID = **적용 전과 같은 digest**, 재시작 0 | `post.txt` |
| | Grafana `/api/health` database ok, v13.2.2. 대시보드 provisioning 시작·완료 | `post.txt` |
| | Alertmanager `/-/ready` 200, Prometheus `alertmanagers_discovered` 1, `count(up)` 23 / `up==1` 23 | `post.txt` |
| | 사후 `kubectl diff` 두 파일 rc=0 | `post.txt` |

## 판정 범위

- 이 기록은 #17 "모든 Image는 Harbor 승인 Repository의 Digest로 고정하고 Trivy 결과를 연결한다"의 Alertmanager·Grafana 부분과 "PVC와 Resource Request/Limit을 정의한다"의 근거다. **AC 체크는 이 증적 병합 뒤 따로 판단한다.** 이미지 AC는 KSM 반영 뒤에 판단한다.
- **NOT RUN:** kube-state-metrics 현장 반영(HOLD), Phase 2 0/0 대체 digest 교체.
