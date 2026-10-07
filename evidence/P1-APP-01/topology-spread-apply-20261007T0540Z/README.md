# P1-APP-01 — fds-app 두 Deployment Worker 분산(topologySpreadConstraints) 적용 원본 (2026-10-07 14:40~14:55 KST)

#15 local endpoint 보장 요구에 대한 적용 창 원본입니다. 근거는 다음과 같습니다.
- [조건부 GO 6030134751](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-6030134751)
- source [infra-kubernetes#65](https://github.com/321Team/infra-kubernetes/pull/65) HEAD `a1e19ea82a5cb151104b26ddfcb04195114ce758`(이하영 [APPROVED 5437120027](https://github.com/321Team/infra-kubernetes/pull/65#pullrequestreview-5437120027), 같은 HEAD)

실행자는 APP Lead 이재환입니다. 해석은 이 README에만 적습니다. **이 원본은 #15 AC 충족·#22 HA 인수·티켓 종결의 판정이 아닙니다.**

## 실행 정보

| 위치 | 계정 | 서버 경로 | 이 PR의 파일 |
|---|---|---|---|
| control01 `10.1.93.102` | `server02`·sudo, 단일 쓰기 세션 | `~/p65-apply-20261007/` | `control01/ev-p65-small.tgz` + `.sha256` + 풀어낸 `p65-apply-20261007/` |
| edge01 `10.1.93.50` | `server08` | `~/p65-edge-ta-20261007T145148.txt`, `~/p65-edge-post-20261007T145446.txt` | `edge01/` 두 파일 |

- **적용 파일 전달(PC → control01):** 검토 HEAD의 git blob으로 만든 묶음(sha256 `12b226f76d5dcd32531cf35ff5c1e7dbb4e4967642f8d13a92c4d5cfcc2f41b2`)을 base64로 붙여 넣었습니다. 서버에서 같은 해시를 확인했고 `sha256sum -c SHA256SUMS`가 5/5였습니다(`pre/00-sha-check.txt`, `sha_check_rc=0`). 서버의 `p1-app01-topology-spread/`는 그 묶음을 풀어낸 사본입니다.
- **결과 원본 회수(control01 → PC):** 서버 폴더 전체 130개 파일의 해시 목록 `SHA256SUMS.all`(sha256 `021b9582…`)을 만들었습니다. 큰 원본 20개(아래 "서버에만 둔 파일")를 뺀 묶음 `ev-p65-small.tgz`(20286 bytes, sha256 `f72b89f5…`)를 base64로 받았습니다. 복원본 해시가 서버 출력과 같고, `SHA256SUMS.all` 대조는 110개 OK, 나머지 20개는 묶음에 넣지 않은 파일입니다.
- **edge01 파일:** 터미널 `tee` 출력으로 복원했고, 서버 `sha256sum` 출력(`e8afa2b9…`, `5b8da845…`)과 같습니다.
- **비밀값:** `eyJ`·`PRIVATE KEY`·`client-key-data`·`token: `·`password` 패턴이 복원본에서 0건입니다. Secret 객체는 조회하지 않았습니다.

## 시각

| 시각(KST) | 사건 | 파일 |
|---|---|---|
| 14:40:29~14:40:33 | 사전 단계(읽기 전용) | `pre/00-start.txt`~`pre/10-mon-pre.txt` |
| 14:42:22 | transaction-api server dry-run과 대조 | `apply/transaction-api-dryrun.rc`, `-dryrun-check.txt` |
| **14:50:02** | transaction-api T0(patch). 시작 한계는 14:55 | `apply/transaction-api-T0.txt`, `-patch.out` |
| 14:50:41 | transaction-api `rollout status` 성공 | `apply/transaction-api-rollout*.txt` |
| 14:51:48 | edge01 → Worker 3대 `/readyz` | `edge01/p65-edge-ta-20261007T145148.txt` |
| 14:52:59 | fds-engine dry-run 대조 → T0(patch) | `apply/fds-engine-*` |
| 14:53:33 | fds-engine `rollout status` 성공 | `apply/fds-engine-rollout*.txt` |
| 14:54:46 | edge01 → Worker 3대 `/readyz`(사후) | `edge01/p65-edge-post-20261007T145446.txt` |
| 14:55:51 | 사후 확정, port-forward 종료 | `apply/80`~`99-*.txt` |

## 1. 사전 단계 (읽기 전용)

| 확인 | 결과 | 파일 |
|---|---|---|
| server 버전 | `v1.36.4`, rc=0 | `pre/01-version.yaml` |
| transaction-api 기준선 | uid `8a2af808-ec33-41f2-80b5-addde4e28910`, RV `4346963`, generation 6, replicas 3, `transaction-api@sha256:a7093136…`, strategy RollingUpdate 25%/25%, 현재 revision 5 | `pre/02-baseline.txt`, `pre/03-history.txt` |
| fds-engine 기준선 | uid `bf825dec-465b-4603-8b71-f768d195531c`, RV `4346977`, generation 4, replicas 3, `fds-engine@sha256:5e2a081c…`, strategy 25%/25%, revision 1 | 같음 |
| template 원본 | `tmpl-transaction-api.json`(`366307…`), `tmpl-fds-engine.json`(`5e3736…`), 전체 Deployment `pre-deploy.yaml`(`5f2f02…`, 서버에만 둠) | `pre/tmpl-*.json` |
| 기존 분산·toleration | 두 앱 모두 비어 있음 | `pre/04-spread-tol.txt` |
| 노드 | 6대 Ready. control 3대는 `control-plane:NoSchedule`, worker 3대는 taint 없음·schedulable | `pre/05-nodes.txt` |
| 자원 요청 | worker01 CPU 3%, worker02 25%, worker03 11% | `pre/06-alloc.txt` |
| 이미지 보유 | worker 3대 모두 두 앱 digest를 이미 보유(Harbor pull 불필요, `IfNotPresent`) | `pre/07-node-images.txt` |
| 배치 | Pod 6개 모두 `k8s-worker02`, `transaction-api-nodeport` ready endpoint `{'k8s-worker02': 3}` | `pre/08-pods.txt`, `pre/09-eps-summary.txt` |
| MON | `count=23 ok=23 down=0 set_match=True` → `MON_23_23=PASS` | `pre/10-mon-pre.txt`, `pre/mon-pre-{count,ok,down,up}.json` |

## 2. 변경

각 앱 모두 아래 순서로 진행했습니다.
1. server dry-run(`-o json`)을 실행해 결과를 저장했습니다.
2. 대조 스크립트로 두 가지를 확인했습니다.
   - dry-run이 돌려준 `topologySpreadConstraints`가 `unspread-<앱>.json`의 `test` 값과 같은지
   - 분산 설정을 뺀 나머지 template이 사전 `tmpl-<앱>.json`과 같은지
3. 둘 다 PASS이고 시각 조건을 만족할 때만 patch를 실행했습니다.

| 확인 | transaction-api | fds-engine |
|---|---|---|
| dry-run | rc=0, 분산 설정이 test 값과 같음 True, 나머지 template이 기준선과 같음 True | 같음 |
| patch / rollout | `patch_rc=0`, `rollout_rc=0`(39초) | `patch_rc=0`, `rollout_rc=0`(34초) |
| 적용 중 가용 Pod(2초 간격 110회) | AVAILABLE 110/110이 3, READY 3/3 | 같음 |
| 새 배치 | worker01·02·03 각 1 | worker01·02·03 각 1 |
| Pending | 0 | 0 |
| endpoint(`transaction-api-nodeport`) | `{'k8s-worker01': 1, 'k8s-worker02': 1, 'k8s-worker03': 1}` | 같음(fds-engine 적용 후 재확인) |
| MON(rollout 후 15초 간격 재조회) | 4회차 PASS, rollout 완료 뒤 **45.8초** | 5회차 PASS, rollout 완료 뒤 **61.0초**(아래 이탈) |
| 사후 uid / generation / image | uid 같음, 6→7, digest 같음 | uid 같음, 4→5, digest 같음 |
| 되돌림 patch server dry-run | `unspread_dryrun_rc=0` | `unspread_dryrun_rc=0` |

MON 회차별 실패 내용은 `apply/<앱>-mon-*.txt`에 있습니다. 실패 target은 모두 옛 Pod IP였고(`up==0` 또는 집합에 남음), 새 Pod IP가 아직 target에 없었습니다. 시각은 `apply/80-mon-timing.txt`(각 회차 `up` 조회 파일의 기록 시각)에 있습니다.

## 3. 사후

| 확인 | 결과 | 파일 |
|---|---|---|
| Deployment | transaction-api `gen=7 obs=7 ready=3 avail=3 upd=3`, fds-engine `gen=5 obs=5 ready=3 avail=3 upd=3` | `apply/92-deploy-post.txt` |
| revision | transaction-api 6, fds-engine 2 | `apply/93-history-post.txt` |
| 배치 | 두 앱 모두 worker01·02·03 각 1, Terminating 없음 | `apply/91-pods-post.txt` |
| MON | `MON_23_23=PASS` | `apply/90-mon-post-final.txt` |
| edge01 → `.105`·`.107`·`.108:30080/readyz` | 14:51:48, 14:54:46 모두 `rc=0 http=200` | `edge01/` |
| port-forward 19095 | 이 세션 것만 종료, 잔여 0(`pf19095_remaining_check_rc=1`) | 터미널 출력 |
| 전체 Deployment 사후 원본 | `post-deploy.yaml`(`24c3bd…`, 서버에만 둠) | `SHA256SUMS.all` |

## 이탈 (숨기지 않음)

- **fds-engine MON 재조회 61.0초:** README·GO의 "rollout 성공 뒤 최대 60초, 15초 간격 재조회"를 약 1초 넘겼습니다(rollout 완료 14:53:33.146, 5회차 `up` 조회 기록 14:54:34.111). 계획한 5회차(0·15·30·45·60초)에 조회 자체의 소요 시간이 더해졌습니다. 그동안 두 앱은 READY 3/3·AVAILABLE 3을 유지했습니다. 5회차가 PASS였기 때문에 **되돌리지 않았고**, 이후 최종 MON도 PASS였습니다. 기준상으로는 60초 시점에 중단에 해당할 수 있으므로 판단은 Review Owner·PMO에 맡깁니다.
- 사전 단계의 `kubectl version` 확인 줄은 grep 패턴이 맞지 않아 화면에 나오지 않았습니다. 원본 파일(`pre/01-version.yaml`)에는 `gitVersion: v1.36.4`가 있습니다.
- 붙여 넣기 중 터미널 화면에 명령 줄이 겹쳐 보였습니다. 실행 결과·rc·해시는 위와 같고, 전달 묶음 해시로 입력 무결성을 확인했습니다.

## 정정 1 — 종료·관측·봉인 시각 구분 (2026-10-07, 권욱 리뷰 반영)

[권욱 리뷰](https://github.com/321Team/fds-project-evidence/pull/136)의 지적대로 `apply/99-end.txt`(14:55:51) 뒤에도 fds-engine 관측이 이어졌습니다. 원본은 바꾸지 않고, 시각의 의미만 아래처럼 구분합니다. 근거는 각 파일의 내용과 `control01/ev-p65-small.tgz` 안 tar 헤더의 파일 기록 시각(mtime)입니다.

| 구분 | 시각(KST) | 근거 |
|---|---|---|
| (1) 마지막 변경(쓰기) | **14:53:33** fds-engine rollout 완료. 이후 쓰기는 없음(되돌림은 `--dry-run=server`만) | `apply/fds-engine-rollout-end.txt` |
| (1') 주 실행 순서 종료 | 14:55:51 사후 확정·port-forward 19095 종료 | `apply/99-end.txt` |
| (2) 읽기 관측 종료 | transaction-api watch 마지막 행 14:53:51(110행), **fds-engine watch 마지막 행 14:56:46(110행)**. 두 watch는 `kubectl get deploy` 읽기만 하는 110회 고정 반복이고, 마지막 행 뒤 `sleep 2`로 끝나므로 fds-engine 쪽은 약 14:56:48에 끝남 | `apply/*-watch.txt` 마지막 행, tar mtime 14:53:51·14:56:46 |
| (3) 해시 목록 생성·묶음 봉인 | `SHA256SUMS.all` 14:57:08(묶음 안 최신 파일), 그 직후 `ev-p65-small.tgz` 생성(서버 `ls -l` 14:57) | tar mtime, 터미널 출력 |
| (4) 관측 프로세스 종료·잔존 | 두 watch 모두 110행으로 반복이 끝까지 돌았음(transaction-api 쪽은 터미널에 `[3]- 완료` 표시). `SHA256SUMS.all`(14:57:08)이 fds-engine watch 110행 완성본의 해시를 담고 있음. **watch 프로세스 잔존을 `pgrep`으로 직접 확인하지는 않았음(NOT VERIFIED)**. port-forward 19095는 잔존 0 확인 | `SHA256SUMS.all`, 터미널 출력 |

- `apply/81-fds-engine-watch-min.txt`(`lines=82`)는 14:55:48에 집계한 **중간값**입니다. 최종 110행 기준으로도 AVAILABLE은 110/110이 3입니다(위 "2. 변경" 표의 값이 최종값).
- 따라서 이 창의 **실제 전체 종료는 읽기 관측까지 포함해 약 14:56:48**이고, 마지막 쓰기는 14:53:33입니다.
- **MON 61.0초는 승인된 최대 60초를 벗어난 절차 이탈로 기록합니다**(권욱 판정). 최종 MON 회복과 절차 준수는 구분하며, 이 회차를 PASS로 소급하지 않습니다.

## 서버에만 둔 파일 (해시는 `control01/p65-apply-20261007/SHA256SUMS.all`)

전체 Deployment(`pre/pre-deploy.yaml`, `apply/post-deploy.yaml`), server dry-run 전체 JSON 4개(`apply/*-dryrun.json`, `apply/*-unspread-dryrun.json`), MON 회차별 Pod 목록 JSON 11개(`pre/mon-*-pods.json`), EndpointSlice JSON 3개(`pre/09-eps.json`, `apply/transaction-api-eps.json`, `apply/fds-engine-ta-eps.json`). 이 20개 파일을 판정한 결과는 각각 `*-dryrun-check.txt`, `*-eps-summary.txt`, `mon-*` 결과 줄로 이 PR에 있습니다.

## 한계

- 이 적용은 **Worker 3대가 모두 스케줄 가능할 때의 1·1·1 배치**를 만든 것입니다. drain·장애로 Worker가 줄면 노드별 endpoint 보장은 유지되지 않고, 노드가 복귀해도 자동 재분산은 없습니다(#65 README). `externalTrafficPolicy: Local`은 그대로입니다.
- edge01 `/readyz` 원본은 #19 AC-04 edge 행의 전제(Worker 3대 local endpoint) 대조에 재사용할 수 있지만, **AC-04 edge 6행 재수집은 별도 GO**입니다.
- 업무 장애 시험과 HA 인수(#22)는 이 범위가 아닙니다.
- 원본은 서버 쪽 봉인 없이 터미널·파일 출력이고, 서버 `SHA256SUMS.all`과 대조했습니다.

## 파일 무결성

- `SHA256SUMS`: 이 폴더 전체 파일(README·하위 `SHA256SUMS`·`SHA256SUMS.all` 포함, 자기 자신 제외)
- `ARCHIVE_CONTENTS`: `control01/ev-p65-small.tgz` 내부 목록(크기·경로)
- `registry/ARCHIVE_CONTENTS.json`에 같은 묶음의 내부 해시 목록을 등록
