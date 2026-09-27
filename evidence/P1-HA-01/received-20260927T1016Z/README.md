# P1-HA-01 — Worker Drain Continuity 시험 (2026-09-27 19:04~19:13 KST)

HA Lead(이재환)가 정본 클러스터에서 fds-app을 3 replica로 분산한 뒤, worker02를 drain하는 동안 edge01에서 반복 요청을 보냈다. 이어서 uncordon, 배치 복구, Final E2E를 수행했다. 명령은 담당자가 k8s-control01(`server02`)과 edge01(`server08`)에서 직접 실행했다.

**운영 변경:**
- transaction-api·fds-engine replicas 2 → 3. infra-kubernetes main `manifests/02-securitycontext.yaml`의 `replicas: 3`과 일치시켰다.
- worker02 cordon/drain/uncordon
- 앱 Pod 퇴거·재생성

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01-drain/` | `~/ha22-drain-20260927` | 2,827 B, SHA-256 `05b44f8b…573a1d` | archive 해시 일치, 서버 `sha256sum`(`server-sha256sums.txt`, 9개) 전부 일치 |
| `edge01-client/` | `~/ha22-edge-20260927.log`·`ha22-e2e-20260927.txt`·`ha22-edge-summary.txt` | 8,568 B, SHA-256 `b08caae5…667c1f` | archive 해시 일치(파일별 서버 Hash 없음) |

`edge01-client/analysis-recomputed.txt`는 수신한 로그를 로컬에서 다시 집계한 결과다(아래 "요약 파일 결함" 참고).

## 절차와 시각 (`control01-drain/timeline.txt`, epoch)

| 단계 | 시각 |
|---|---|
| 3 replica 분산 | 19:04. 3번째 Pod를 원하는 Worker로 보내려고 다른 Worker 2대를 잠시 cordon했다가 해제했다(`pre-scale.txt` → `post-scale.txt`) |
| 기준 기록 | `criteria_recorded` 1790503628.831(19:07:08). `criteria.txt` SHA-256 `032f020d…fc40d1` |
| 기준선 | `baseline_start` 1790503629.084 (60초) |
| Drain | `drain_start` 1790503689.087 → `drain_end` 1790503691.401. `drain k8s-worker02 --pod-selector='app in (transaction-api,fds-engine)' --ignore-daemonsets --delete-emptydir-data` |
| 재배치 Ready | `rescheduled_ready` 1790503701.823 (drain 시작 후 12.7초) |
| Uncordon | `uncordon` 1790503761.999, `end` 1790503822.224 |
| 배치 복구 | `restore_start` 1790503948.986 → `restore_end` 1790503961.548. worker01/03을 잠시 cordon하고 worker01의 새 Pod 2개를 삭제해 worker02에 재생성 |
| Final E2E | 19:13:01 (edge01) |

## 결과

**배치**
- 시험 전 2 replica: transaction-api는 w01·w02, fds-engine은 w02·w03
- 3 replica 분산 후: 두 서비스 모두 **w01·w02·w03에 1개씩**. NodePort `transaction-api-nodeport` local endpoint 3개 모두 `ready=true`
- drain 중: worker02의 Pod 2개가 퇴거돼 worker01에서 Ready. endpoint는 w01·w03 두 곳
- 배치 복구 후: 다시 Worker마다 1개씩(`restored.txt`)

**요청 (edge01 → Worker:30080 `/readyz`, Worker별 약 1초 간격, 로그 1,147줄)**

| 구간 | `.105` w01 | `.107` w02(drain 대상) | `.108` w03 |
|---|---|---|---|
| 기준선 60초 | 200×59 | 200×59 | 200×59 |
| drain → 재배치 Ready | 200×12 | 000×11 | 200×12 |
| drain 상태 60초 | 200×59 | 000×60 | 200×59 |
| uncordon 60초 | 200×60 | 000×60 | 200×60 |
| 복구 전까지 | 200×124 | 000×125 | 200×124 |
| 배치 복구 중 | 200×13 | 000×13 | 200×13 |
| 복구 후 | 200×22 | 000×1, 200×21 | 200×22 |

- `.105`와 `.108`은 전체 382건 모두 200이고, 응답시간은 최대 0.042초다.
- `.107`은 drain 시작 0.93초 뒤부터 000을 냈다. Local Service에서 Pod가 없는 노드는 즉시 거부하기 때문이며(최대 0.001~1.014초), 기준에서 허용한 동작이다. 배치 복구가 끝나고 1.6초 뒤 200으로 돌아왔다.
- **기준 "매 1초 구간에 200이 1건 이상" 대조 결과, 355초 중 1초 구간(epoch 1790503754, 19:09:14 KST)에 200이 없다.** 그 앞뒤 200은 `…753.996`(w01)·`…753.998`(w03)과 `…755.012`(w01)·`…755.015`(w03)이다. 요청 루프가 `sleep 1`에 응답시간만큼 밀리면서 두 정상 Worker가 같은 1초 경계를 동시에 건너뛴 **측정 공백**이다. 그 구간에 실패한 요청은 없다. 200과 200 사이 최대 간격은 1.028초다. 기준 문언은 시험 후에 바꾸지 않았다. 이 1건을 어떻게 판정할지는 Lead/Support 판단으로 남긴다.

**Final E2E** (`edge01-client/ha22-e2e-20260927.txt`)
- `.105`·`.107`·`.108` `/readyz` 모두 200
- `POST /api/v1/transactions`(`account_id=SIM_ha22_20260927`, 3,500,000 KRW, transfer) → **HTTP 201**, `fds_detected=true`, R02 `triggered=true`, `fds_evaluation_skipped=false`, `transaction_id=09fc1a3b-d24f-48b4-a87c-2bffa11a84ce`
- DB 행 직접 조회는 NOT RUN이다. 저장 실패 시 API가 500을 반환하는 코드 경로(`transaction-api/app/main.py`)로 저장 성공을 판단한다. 이 시험 거래 1건은 DB에 남아 있다.

**복구** (`after.txt`, `restored.txt`)
- 노드 6대 Ready, SchedulingDisabled 없음
- monitoring-api Pod 재시작 없음
- `icr39-probe` Pod 4개(w01/w02/w03/cp01)는 `--pod-selector`로 퇴거 대상에서 빠져 계속 Running

## 요약 파일 결함

edge01에서 만든 `ha22-edge-summary.txt`는 복구 구간 시각(`R1`/`R2`)이 비어 있는 채로 실행됐다. 그래서 `5gap` 구간에 복구 이후가 섞였고, `window … no200_secs 0` 줄은 **계산되지 않은 값**이다(구간 길이가 음수). 수신 원문이라 그대로 두고, 판정에는 `analysis-recomputed.txt`를 쓴다.

## 한계와 후속

- 요청 대상은 `/readyz`(DB ping)다. 업무 API 연속 요청은 하지 않았다(시험 행이 DB에 쌓이는 것을 피하려고).
- edge01 nginx upstream은 바꾸지 않았다. 요청은 edge01에서 각 Worker로 curl을 직접 보냈다. 판정은 "edge가 Worker별 `/readyz`로 정상 Worker를 고른다"(D18, `transaction-api-nodeport.yaml` 주석)는 가정의 모사다.
- 소스에 `topologySpreadConstraints`나 PDB가 없어서, 분산 배치는 cordon으로 맞췄다. 재시작하면 한 Worker로 몰릴 수 있으므로 infra-kubernetes 후속 PR이 필요하다.
- 합격 기준 값은 시험 전에 서버 파일로 기록했다. Support(이하영) 검증과 G3 대조(이권욱)는 아직 받지 않았다.

AI 사용: CLAUDE_ASSISTED (명령 준비·수신 대조·재집계·문서화, 실행은 담당자 본인)
