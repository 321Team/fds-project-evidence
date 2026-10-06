# P1-MON-01 — 승인 단말 port-forward 2회차 + `.108` IF-06B canary 원본 (2026-10-06 16:22~16:48 KST)

#17 [시작 기록 6011489994](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6011489994)·[연장 승인 6011332756](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6011332756)·[오늘 GO 6008238972](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6008238972) 범위에서 실행한 PF 2회차와 `.108` canary의 원본입니다. 결과 보고는 [#17 6011861893](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6011861893)이고, Close 분류는 [#17 6011892873](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6011892873)입니다. 실행자는 MON Lead 이재환(supreme33-kr)입니다. 해석은 이 README에만 적습니다.

**결과 요약**
- **PF 2회차:** 토큰 발급까지는 정상이었습니다. 실행자가 kubeconfig를 붙여넣지 않아 배치 검사가 FAIL했고, verify·pftest는 실행되지 않았습니다. 이후 삭제·정리·Restore Gate는 PASS이고 runner는 online으로 복구됐습니다. **port-forward AC는 NOT VERIFIED입니다.**
- **canary:**
  - `.108` 출발지에서 잘못된 인증으로 보낸 요청이 **401**을 받았습니다.
  - monitor01 캡처에 출발지 `10.1.93.108`이 그대로 남았습니다.
  - `.108 → .30:8443` 직접 연결은 curl timeout이었지만 **monitor01에 SYN이 0개**였습니다. 그래서 어디서 막혔는지(차단 지점 귀속)는 NOT VERIFIED입니다.
  - 임시 GNP는 삭제됐고, 방화벽 diff는 0, MON은 23/23으로 회복됐습니다.

## 실행 소스

- PF 도구: infra-monitoring merge `d9bc0c8d9d8cb68b07fffa6221e6f059c3ff6f0e`(승인 HEAD `6262eb0e`). 전달본 SHA-256은 시작 직전에 대조해 일치했습니다([시작 기록](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6011489994) §2).
  - `pf_cp.sh` `cbe25e84…`
  - `pf_runner.sh` `22566e14…`
  - `pf_gh.sh` `8243b103…`
- canary manifest: infra-kubernetes merge `b4303f2d`. `control01/canary-20261006/canary.yaml`의 SHA-256 `b4edfca8421615b765415f6bef7ff6509e7436fdec76c241567721ce0952c660`이 승인값과 같습니다.

## 수집 정보

| 위치 | 계정 | 서버 폴더 | 이 PR의 파일 |
|---|---|---|---|
| control01 `10.1.93.102` | `server02` | `~/pf-retest-d9bc0c8/{run-20261006T1625, canary-20261006, mon-gate-20261006T1615.txt}` | `control01/ev-control01-20261006.tgz` + `.sha256` + 풀어낸 파일 |
| cicd-runner01 `10.250.10.20` | `server01_cicd-runner` | `~/pf-retest-d9bc0c8/run-20261006T1625` | `runner/ev-runner-20261006.tgz` + `.sha256` + 풀어낸 파일(빈 `bin/`은 Git에 담기지 않음) |
| k8s-worker03 `10.1.93.108` | `server07` | `~/canary-20261006` | `worker03/ev-worker03-20261006.tgz` + `.sha256` + 풀어낸 파일 |
| monitor01 `10.250.10.30` | `server01_monitor` | `~/canary-20261006` | `monitor01/ev-monitor01-20261006.tgz` + `.sha256` + 풀어낸 파일 |
| PC `10.1.93.29` | `soldesk`(Git Bash, `gh`) | `C:\Users\soldesk\pf-run-20261005\gh-20261006` | `pc/gh-20261006/`(pre·after_stop·post_restore raw JSON·meta·verdict) |

- **전달 방식:** 서버에서 `tar --sort=name -czf`로 압축본을 만들었습니다. 이를 `base64 -w 76`으로 화면에 출력하되 줄마다 `cksum`을 붙여 받았습니다.
  - 줄 검사합 일치: control01 133/133, runner 21/21, worker03 41/41, monitor01 94/94.
  - 복원한 압축본의 SHA-256이 서버 출력과 같습니다(각 `.sha256` sidecar).
  - 서버 압축본은 서버 홈 디렉터리에 남아 있습니다.
- **압축본 목록:** `ARCHIVE_CONTENTS`(압축본별 크기·경로).
- **비밀값:** 네 서버 모두 회차 폴더에서 `eyJ`(JWT 접두)·`PRIVATE KEY`·`client-key-data`·`token: ` 패턴이 0건이었습니다(서버에서 검사). 복원본도 0건입니다.
  - 토큰은 control01 화면에만 출력됐고, 파일에는 클레임만 있습니다(`15-token-claims.txt`).
  - runner에는 kubeconfig가 배치되지 않았습니다(빈 입력 → 제거).
  - `worker03/canary-20261006/fds-root-ca.crt`는 공개 CA 인증서입니다.
- **PC 시각 표기:** PC Git Bash에 시간대 데이터가 없어 meta 시각이 UTC인데 "GMT"로 표기됐습니다. 예를 들어 `07:22:49 GMT`는 16:22:49 KST입니다.

## PF 2회차 단계별 결과 (KST, 회차 `run-20261006T1625`)

| 단계 | 시각 | 결과 | 근거 파일 |
|---|---|---|---|
| A1 GitHub pre | 16:22:49 | online · busy=false · queued 0 · in_progress 0 — PASS | `pc/gh-20261006/verdict.txt`, `pre-*` |
| A2 control01 pre | 16:26:25 | PRE=PASS, context `kubernetes-admin@kubernetes`, Grafana `grafana-f65457bfd-ckjgj`(UID `916b8c8a…`, ready), 비교 Pod `prometheus-d8949bd64-2zc4m`, 임시 객체 명시적 NotFound | `control01/run-20261006T1625/00~07*`, `pinned.env` |
| A3 runner pre / stop | 16:26:48 | PRE=PASS / RUNNER_STOPPED_LOCAL=PASS(`stop_rc=0 is-active=inactive`) | `runner/run-20261006T1625/00~03*`, `ss.log` |
| A4 GitHub after_stop | 16:27:21 | offline · busy=false — PASS | `pc/gh-20261006/after_stop-*` |
| A5 kubectl 설치 | 16:28:27 | 체크섬 OK, v1.36.4 — PASS | `runner/…/04-kubectl-sha.txt` |
| A6 임시 RBAC | 16:28:43 | server dry-run PASS, 생성 UID 3개(SA `81085622…`, Role `5735f3f2…`, RB `4193cfd6…`) | `08-*.yaml`, `09-dryrun.txt`, `10-create.txt`, `created.env` |
| A7 토큰 | iat 16:29:41 | 소유 UID 재대조 PASS, 호출자 kubernetes-admin, sub `system:serviceaccount:monitoring-api:p1-mon-pf-verify`, aud `https://kubernetes.default.svc.cluster.local`, exp 16:39:41, TTL 600초 | `12-owned-before-token.txt`, `13-tokenrequest-caller.txt`, `15-token-claims.txt` |
| A8 배치 | 16:30:46 | 화면 출력: 시작 표식 0개로 `MARKER_CHECK=FAIL` → `KUBECONFIG_PLACED=FAIL_INVALID_REMOVED` | `runner/…/status.txt`, `05-kubeconfig-place-fail.txt` |
| 파싱 검사 | 16:31:42 | `parse_rc=1`(`current-context must exist`) → verify·recheck·pftest **미실행**(절차대로 건너뜀) | `runner/…/05c-parse-check.txt` |
| A12 임시 객체 삭제 | 16:32:41 | 소유 UID precondition 삭제 3건, 사후 absent 3건 — TEMP_OBJECTS_REMOVED=PASS(토큰 만료 전) | `17-*`, `18-delete-*.txt`, `19-*` |
| A13 runner 정리 | 16:32:53 | PF_PROCESS_STOPPED=NOT_STARTED, OLD_TOKEN_AUTH_AFTER_SA_DELETE=`PLACE_FAILED_FILE_REMOVED`, KUBECONFIG_REMOVED=PASS, TEST_KUBECTL_REMOVED=PASS, TEMP_OBJECTS_REMOVED_CP=PASS → **RESTORE_GATE=PASS** | `runner/…/status.txt` |
| A14 runner 복구 | 16:33:52 | `start_rc=0 is-active=active`. 다만 확인 시점에 Listener가 아직 뜨지 않아 `RUNNER_RESTORED_LOCAL=FAIL`이 기록됐습니다. 재시작은 하지 않았습니다 | `runner/…/13-runner-restore.txt`, `status.txt` |
| A14 재확인(읽기 전용) | 16:48:14 | `actions.runner.321Team-infra-cicd.cicd-runner01.service` active running, `Runner.Listener` PID 6852 1개, `/dev/shm` kube 0 | `runner/…/13b-post-restore-check.txt` |
| A15 GitHub online | 16:34:31 | online · busy=false — PASS | `pc/gh-20261006/post_restore-*` |

- **원인:** 토큰 만료값을 입력한 뒤 화면이 kubeconfig 입력을 기다리는 상태였습니다. 실행자가 붙여넣을 위치를 몰라 아무것도 넣지 않았습니다. 도구는 빈 입력을 거부했고, 이후 정리는 승인 절차대로 진행됐습니다. 도구 결함 근거는 없습니다.
- 이 회차는 port-forward 성공·비승인 접근 실패 AC의 근거가 되지 않습니다.

## canary 단계별 결과 (KST)

| 단계 | 시각 | 결과 | 근거 파일 |
|---|---|---|---|
| MON 사전 Gate | 16:17:03 | `targets 23 up 23`, remote_write 실패 15분 0 | `control01/mon-gate-20261006T1615.txt` |
| 사전 목록 | 16:36:27 | worker03 HEP UID `76f476c5…` RV 997111(`ens160`, `10.1.93.108`). GNP 7개(host GNP 6개 order 100, `nodeport-30080-allow` order 50 Ingress). order 90 충돌 없음 | `control01/canary-20261006/00-time.txt`, `01-*` |
| 후보 부재·dry-run | 16:3x | 후보 NotFound, server dry-run OK | `02-candidate-absent.txt`, `03-dryrun.txt` |
| 출발지·방화벽 사전 | 16:38 | worker03 경로 `10.250.10.30 via 10.1.93.58 src 10.1.93.108`, CA SHA 기록. monitor01 firewalld runtime=permanent, rich rule 1개(`.108` → `.30:443` → 8443) | `worker03/canary-20261006/t0-route.txt`, `ca.sha`, `monitor01/canary-20261006/fw-pre.txt` |
| GNP 생성(T0′) | 16:39:19 | `create_rc=0`, UID `9cfdccea-b371-403f-8724-49779ed4e7c9`, RV 4149284 | `04-create-time.txt`, `04-create.json`, `04-created.txt` |
| 캡처 | 16:39:41~16:42:41 | monitor01 `ens160`, rc=0, 220 captured / 220 received / 0 dropped | `monitor01/canary-20261006/cap-*.txt`, `cap.txt` |
| T1 첫 실행 | 16:40:10.98 | 잘못된 자격으로 POST → `http=401`, `ssl_verify=0`, local_ip `.108`(화면 출력). 캡처 `.108:44400 → .30:443` `[S]`(16:40:10.979777)·`[S.]`(16:40:10.979837). nginx `*991 user "fds-heartbeat": password mismatch, client: 10.1.93.108` → 401 | `cap.txt`, `nginx-1639.txt`, `nginx-non204.txt` |
| T2 첫 실행 | 16:40:11.00 | curl rc 28(연결 timeout 5초)(화면 출력) | — |
| T1 두 번째 실행 | 16:40:13.84 | 실행자가 **새 터미널 탭에서 같은 시험 명령을 한 번 더 실행**했습니다(실행자 보고). `http=401`. 캡처 `.108:47936 → .30:443` `[S]`(16:40:13.831368)·`[S.]`. nginx `*992` 같은 형태 → 401 | `worker03/canary-20261006/t1.*`, `cap.txt`, `nginx-*` |
| T2 두 번째 실행 | 16:40:13.85 | curl rc 28(연결 timeout 5초) | `worker03/canary-20261006/t2.*` |
| T2 판정 | — | 캡처 전체에서 `.8443` 패킷 **0줄**. runbook 기준("monitor01에 SYN 도착 후 미응답")을 충족하지 못해 **차단 지점 귀속 NOT VERIFIED** | `cap.txt` |
| GNP 삭제 | 16:42:20 | UID 일치 확인 후 UID+RV precondition 삭제 `Success`, 사후 NotFound. GNP 7개 UID·RV와 HEP RV 997111이 생성 전과 같음 | `05-pre-delete.txt`, `06-delete.txt`, `07-post-delete.txt`, `08-*` |
| 방화벽 사후 | 16:4x | `fw-pre.txt`와 `fw-post.txt` 동일(SHA `6b65076d…`) | `monitor01/canary-20261006/fw-*.txt` |
| 차단 복귀 | 16:44:13 | worker03 `.30:443` 새 연결 rc 28(timeout) | `worker03/canary-20261006/post-deny.*` |
| MON 회복 | 16:44:28 | `up` 23/23, remote_write 실패 15분 0 | `control01/canary-20261006/09-mon-after.txt` |
| 수신 회복 | 16:48:02 | heartbeat 나이 0.57초, `FDSMonitoringHeartbeatMissing` inactive·ok | `monitor01/canary-20261006/hb-after.txt` |

## 해석과 한계

- **worker03 `t1`·`t2` 파일:** 두 번째 실행 결과로 덮어써졌습니다(16:40:13.8x). 첫 실행(16:40:10.98) 값은 화면 출력에만 있고, 캡처·nginx 기록과 시각이 맞습니다.
- **두 번 실행한 것:** GO 범위는 canary 1회였는데, 같은 GNP 창 안에서 시험 명령이 2번 실행됐습니다. 추가 GNP 생성이나 시간 연장은 없었고, 두 요청 모두 401로 거부됐습니다.
- **401 관측의 범위:** "`.108` 출발지 + 잘못된 인증 → TLS 종료 후 거부"까지만 확인됩니다. 정상 송신 204는 같은 시간대 remote_write 기록(`nginx-1639.txt`의 204 26줄)으로 확인됩니다.
- **T2(8443 직접):** 연결은 실패했습니다. 그러나 SYN이 monitor01 `ens160`에 오지 않았으므로 monitor01 방화벽이 막았다는 근거는 아닙니다. 경로(`via 10.1.93.58`) 중간에서 막혔는지는 확인하지 않았습니다.
- **기존 흐름:** `.108:18577 → .30:443`은 기존 remote_write 연결이며 시험 대상이 아닙니다.
- **`09-mon-after.txt`:** 파일 안에 시각이 없습니다. 시각(16:44:28)은 실행 화면 출력 기준입니다.

## 파일 무결성

- `SHA256SUMS`: 이 폴더 전체 파일의 SHA-256(README 포함, 자기 자신 제외)
- `*/ev-*-20261006.tgz.sha256`: 압축본 sidecar(서버 출력값과 같음)
- `ARCHIVE_CONTENTS`: 압축본별 파일 목록. 풀어낸 파일은 압축본에서 꺼낸 그대로입니다.

AI 사용: CLAUDE_ASSISTED (명령 작성, 전달 복원·대조, README 작성)
