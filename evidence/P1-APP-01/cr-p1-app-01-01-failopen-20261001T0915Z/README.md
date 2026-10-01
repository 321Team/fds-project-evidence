# CR-P1-APP-01-01 — fds-engine 장애 시 transaction-api fail-open Runtime 시험 (2026-10-01 18:15~18:21 KST)

APP Lead(이재환)가 정본 클러스터에서 `fds-engine`을 `replicas=0`으로 내려, #15 새 AC ② "fds-engine 장애 시 transaction-api는 Ready를 유지하고 거래를 fail-open(`fds_evaluation_skipped=true`, HTTP 201)으로 저장"을 시험했다. 명령은 담당자가 k8s-control01(`server02`, `sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf`), edge01(`server08`), db01(`server08`)에서 직접 실행했다.

- 변경 요청: [CR #119](https://github.com/321Team/fds-project-baseline/issues/119)(APP Lead 승인 [5928210700](https://github.com/321Team/fds-project-baseline/issues/119#issuecomment-5928210700), G3 수용 권고 [5922785388](https://github.com/321Team/fds-project-baseline/issues/119#issuecomment-5922785388))
- 검증 계획: CR 본문 "② 검증 계획". 실행 전 G3 권고(실행 전 상태 기록, 단독 변경창, Worker 3대 `/readyz` 유지, 거래 1건 201+DB 행+`skipped=true`/null, 오류 카운터 +1, restartCount 변화 0, 복구 후 3 replica·정상 거래 `skipped=false`, 원본 증적 편입)를 따랐다.
- 이 증적은 **② 줄(fds-engine 장애)만** 다룬다. ① 외부 DB 장애 `/readyz` 503은 [evidence#66](https://github.com/321Team/fds-project-evidence/pull/66)의 몫이며 여기서 판정하지 않는다.

**운영 변경 (모두 원복)**
1. 18:13:01 worker01의 `fds-engine-5699669f6f-hcmxb`·`transaction-api-b784c8c5d-2nqhq` Pod 삭제(재배치, 아래 "시험 전 사건").
2. 18:15:48 `kubectl -n fds-app scale deploy/fds-engine --replicas=0` → 18:17:01 `--replicas=3`.
3. 시험 거래 2건(`SIM_fo15_202610011815_1`, `_2`)이 운영 `fdsdb`에 남아 있다. #11 보존 기준(기능 시험 거래 보존, 범주 `SIM_fo15`)에 따라 삭제하지 않는다.
앱·매니페스트·Secret·transaction-api replica 변경은 없다. 코드·스크립트는 새로 만들지 않았고, 모두 `kubectl`·`curl`·`psql` 명령과 조회 함수(`control01/…/p1-app-fo-fn.sh`, 읽기 전용 Prometheus 질의)만 썼다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | control01 `~/p1-app-fo-202610011805/`(파일 11개) | `p1-app-fo-control01-202610011805.tgz` 5,328 B, SHA-256 `adea630f…71660082b` | base64로 받아 복원, 서버 `sha256sum`과 일치. 개별 파일은 archive를 그대로 푼 것 |
| `edge01/` | edge01 `~/p1-app-fo-202610011815/`(파일 3개) | `p1-app-fo-edge01-202610011815.tgz` 1,428 B, SHA-256 `52b33705…adbf2ea9d8a` | base64로 받아 복원, 서버 `sha256sum`과 일치 |
| `db01/` | db01 `~/p1-app-fo-db01.log` | archive 없음. 로그 파일 4줄, SHA-256 `a702ea09…e067c68` | 담당자가 db01 콘솔 출력(psql 결과)을 제출했고, 같은 4줄로 로컬에서 만든 파일의 SHA가 서버 `sha256sum` 출력과 일치 |

- archive 2개를 **바이트 그대로** 보존했고 같은 이름의 `.sha256` sidecar를 두었다. 내부 목록은 `registry/ARCHIVE_CONTENTS.json`에 등록했다.
- 파일별 서버 Hash는 받지 않았다. 서버 측 대조는 archive 단위(db01은 파일 단위)다.
- 폴더 이름 두 개의 시각이 다르다: control01 `…1805`는 사전 기록을 시작한 시각(18:05), edge01 `…1815`와 계정 `SIM_fo15_<RUN>`의 RUN은 시험 실행 시각(18:15)이다.
- Secret·token·cookie 값은 없다. 수집한 명령은 `kubectl get`/`logs`, Prometheus 질의, `curl`, `psql` 조회뿐이다.

## 시험 전 사건 — Worker02 VM 정지와 재배치 (시험 결과와 별개)

- 18:05 사전 기록 시점에 `k8s-worker02`가 17:45:46부터 kubelet 상태를 보고하지 않아 `NotReady`였고(`control01/…/diag-worker02.txt`), 같은 노드 `.107`에 ping·SSH·NodePort가 닿지 않았다. 담당자가 확인해 보니 **Worker02 VM이 꺼져 있었고**, 18:08 이후 담당자가 다시 켰다(복구 확인은 18:12). 원인은 이 증적의 범위 밖이다.
- 18:12 `k8s-worker02` `Ready`로 복구(`diag-worker02-after.txt`). 장애 중 쿠버네티스가 worker02 Pod를 worker01에 다시 만들어 worker01에 fds-engine·transaction-api가 2개씩 몰려 있었고, worker02에는 앱 Pod가 없었다.
- 그래서 시험 전에 worker01의 20분 된 Pod 2개를 삭제해 **Worker당 1개 배치**로 되돌렸다(`rebalance.txt`, 18:13:01). 삭제한 Pod가 아닌 다른 transaction-api 2개는 계속 Ready라 서비스는 끊기지 않았다.
- `env-before.txt`(18:05:55)는 이 Worker02 정지 중의 기록이다. **시험 직전 상태는 `metrics.log`의 `[BASE2]`(18:15:48)와 `rebalance.txt`**다.
- 18:14:16 edge01 → Worker 3대 `/readyz` 모두 200을 직접 확인한 뒤 시험을 시작했다(`edge01` 루프 첫 줄 18:15:38부터 3대 200).

## 시험 전 상태 (`metrics.log [BASE2]`, 18:15:48)

| 항목 | 값 |
|---|---|
| fds-engine | 3 Pod — worker02 `bgtm2`, worker03 `5rxbt`, worker01 `c5jw6`, 모두 Ready, restarts 0·2·0 |
| transaction-api | 3 Pod — worker02 `75ws7`, worker03 `m65z4`, worker01 `rq9b6`, 모두 Ready, restarts 0·0·1(`rq9b6`의 1은 시험 전부터 있던 값) |
| 이미지 | fds-engine `10.1.93.54/fds/fds-engine@sha256:5e2a081c…f67369`, transaction-api `@sha256:a7093136…45cc33`(`env-before.txt`, 두 Deployment 모두 시험 전후 불변) |
| `fds_evaluation_error_total` | 3개 Pod 모두 0 |
| `transaction_save_success_total` | `10.244.79.84`(worker01 `rq9b6`) 16,263 · `.39.248`(worker03) 16,257 · `.69.218`(worker02 새 Pod) 0 |
| `transaction_save_failure_total` | 모두 0 |
| ALERTS | 없음 |

## 절차와 시각 (KST)

| 시각 | 단계 | 근거 |
|---|---|---|
| 18:15:38 | edge01 `/readyz` 1초 루프 시작(Worker `.105/.107/.108`, 300회) | `edge01/…/readyz-loop.log` |
| 18:15:48 | control01 `replicas=0`(`scale0 rc=0`) | `control01/…/outage-run.txt` |
| 18:15:51 | fds-engine Pod 0개, EndpointSlice 비어 있음(`<unset>`) | 같은 파일 |
| 18:16:12 | **POST1** `SIM_fo15_202610011815_1` → `.105:30080` | `edge01/…/post1-outage.txt` |
| 18:17:01 | 장애 중 metric·로그 기록(`[OUTAGE]`) 후 `replicas=3`(`scale3 rc=0`) | `outage-run.txt`, `metrics.log` |
| 18:17:13 | `rollout status` 성공(`rollout rc=0`), 3 Pod가 worker01·02·03에 1개씩 | `outage-run.txt` |
| 18:17:31 | **POST2** `SIM_fo15_202610011815_2`(복구 후) | `edge01/…/post2-recovered.txt` |
| 18:19:16 | 복구 후 metric(`[AFTER]`) | `metrics.log` |
| 18:20:03 | db01 행 조회 | `db01/p1-app-fo-db01.log` |
| 18:20:51 | edge01 루프 종료(데이터 300줄) | `readyz-loop.log` |

장애 구간(`replicas=0` 18:15:48 → `replicas=3` 18:17:01)은 **73초**다. CR 계획의 "약 2분"보다 짧게 진행했다.

## 결과 — CR "② 검증 계획"의 합격 항목 대조

| 합격 항목 | 관측 | 근거 |
|---|---|---|
| fds-engine 장애 구간 | Pod 0개, EndpointSlice 비어 있음, `up{job="fds-engine"}` 대상 사라짐, `fds_evaluated_total` 결과 없음 | `outage-run.txt`, `metrics.log [OUTAGE]` |
| Worker 3대 `/readyz` 200 유지 | 장애 구간(18:15:51~18:17:01) 샘플 68개 전부 `.105=200 .107=200 .108=200`. 전체 데이터 300줄 중 300줄이 3대 모두 200 | `readyz-loop.log` |
| transaction-api Ready 유지 | `[OUTAGE]` 시점 3개 Pod `READY true`, `up{job="transaction-api"}` 3개 모두 1 | `metrics.log` |
| 거래 1건 201·`skipped=true`·`fds_detected=null` | POST1: `HTTP=201`, `fds_detected:null`, `fds_rules:null`, `fds_evaluation_skipped:true`, 응답 1.02초(connect timeout 1초와 일치) | `post1-outage.txt` |
| DB 행 | `SIM_fo15_202610011815_1`, `transaction_id 76cdb194-6a3c-46e3-803a-088fa69ba81f`, deposit 10000, `fds_detected` null, `fds_evaluation_skipped=t`, `fds_rules` null, `received_at 18:16:12.973719+09` | `db01/p1-app-fo-db01.log` |
| `fds_evaluation_error_total` +1 | `.79.84`(POST1을 받은 worker01 Pod) 0 → **1**, 나머지 0 유지. 복구 후에도 1 | `metrics.log` |
| 저장 성공 | `.79.84`의 `transaction_save_success_total` 16,263 → 16,264(POST1) → 16,265(POST2), `save_failure` 전 구간 0 | `metrics.log` |
| transaction-api restartCount 변화 0 | 전·장애 중·후 모두 0·0·1(기존 값) | `metrics.log` Pod 표 |
| 복구 3 replica·Worker당 1개 | fds-engine `bp6t6`(worker01)·`d2vwq`(worker02)·`lt9hb`(worker03) Ready, EndpointSlice 3개 | `outage-run.txt` |
| 복구 후 정상 거래 `skipped=false` | POST2: `HTTP=201`, `fds_detected:false`, R01·R02·R04·R07 평가됨, `fds_evaluation_skipped:false`, DB 행 `SIM_fo15_202610011815_2`(`9ba0560f-d915-48c0-95b6-a785ed95fe30`, `fds_detected=f`, `skipped=f`) | `post2-recovered.txt`, db01 로그 |
| 복구 후 fds-engine 평가 | `fds_evaluated_total`이 새 Pod `10.244.39.251`에서 1 | `metrics.log [AFTER]` |
| 서비스 영향 | `save_failure` 0, POST 두 건 모두 201, `/readyz` 200 유지. 거래 접수 중단 없음 | 위 근거 |

DB 조회 결과 `SIM_fo15_%` 행은 정확히 2건이다(`count 2`).

## 관측 — 알람 (이 증적의 합격 항목 아님)

- `ALERTS` 범위 조회(`alerts-range.json`, 18:14~18:19 KST, 15초 간격)는 **시리즈 0개**다. fds-engine 장애 구간에 firing·pending 알람이 모두 없었다.
- 장애 중 `up{job="fds-engine"}`가 `0`이 아니라 **대상 목록에서 사라졌다**(Pod가 없어 dns_sd 대상이 비었다). `up == 0` 형태의 조건은 이 장애를 못 잡는다는 뜻일 수 있으나, 이 증적은 알람 규칙을 점검하지 않았으므로 **가설일 뿐**이며 #17 검토 입력으로만 남긴다.

## 한계와 후속

- 거래는 장애 중 1건, 복구 후 1건이다. 장애 중 요청은 edge01 → worker01 NodePort(`.105:30080`, `externalTrafficPolicy Local`)의 transaction-api Pod 1개(`rq9b6`)가 처리했다. 다른 두 Pod는 직접 요청하지 않았다(같은 이미지·코드).
- 경로는 edge01 → Worker NodePort 직접이다. edge01 nginx(:80) upstream은 아직 E-K3S라 Client → edge(:80) 경로는 이 시험 대상이 아니다.
- 장애 시간 73초는 CR 계획(약 2분)보다 짧다. fail-open 동작 자체는 connect timeout(1초) 안에서 관측됐다.
- 장애 중 transaction-api EndpointSlice 자체는 따로 조회하지 않았다. 대신 NodePort `Local` 정책에서 Worker 3대 `/readyz` 200이 유지된 것(로컬 Endpoint 존재)과 Pod Ready 유지로 갈음했다.
- Prometheus 조회는 control01의 `kubectl port-forward`(`19093`, 이 시험 전용)로 했다. port-forward는 kubelet 경유라 NetworkPolicy 경로 증명이 아니며 조회에만 썼고 시험 뒤 종료했다(`pf.log`).
- 이 증적은 AC 판정을 하지 않는다. #15 새 AC ② 체크 여부는 독립 리뷰·병합 뒤 Lead가 판단한다. #20 A04 "엔진 실패 fail-open 대조"에는 같은 증적을 연결할 수 있다.
- Worker02 VM 정지(17:45~18:10)와 그 원인은 별도 사건이며 이 시험의 결과로 해석하지 않는다.

AI 사용: CLAUDE_ASSISTED (명령 준비, 수신 대조·문서화, 실행은 담당자 본인)
