# P1-APP-01 — Worker 분산 적용 창 원문 보충 (2026-10-07 16:29 KST 수신)

[evidence#136](https://github.com/321Team/fds-project-evidence/pull/136)(`evidence/P1-APP-01/topology-spread-apply-20261007T0540Z/`, 병합 `85e3000d`)에서 **서버에만 둔 20개 파일 중 6개**를 보충합니다. 그 폴더는 병합돼 봉인됐으므로 새 폴더에 둡니다.

근거는 [권욱 #15 최종 재조회 6033027236](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-6033027236)의 "APP Lead는 최종 인수에 필요한 원문 20개 중 관련 항목을 연결"입니다. 고른 기준은 #15 local endpoint 판정과 직접 관련된 파일입니다. **새 시험이나 서버 변경은 없습니다.** 적용 창에서 이미 만든 파일을 그대로 회수했습니다.

실행자는 APP Lead 이재환입니다. 이 보충은 #15 AC·Status·종결 판정이 아닙니다.

## 회수 방법과 대조

| 항목 | 값 |
|---|---|
| 서버 | control01 `10.1.93.102`, `server02`, `~/p65-apply-20261007/` |
| 묶음 | `tar -czf ~/ev-p65-extra.tgz <6개 파일>` 16:29 KST, 6950 bytes, SHA256 `1fbf18077f03baa029a6f5365bb06b029a559508cca12695d0ddc0d63d734da2` |
| 전달 | `base64 -w 76` 터미널 출력을 붙여 넣어 복원. 복원본 SHA256이 서버 출력과 같음 |
| 기존 해시 목록 대조 | 6개 파일의 SHA256이 evidence#136의 `control01/p65-apply-20261007/SHA256SUMS.all`(14:57:08 생성, `021b9582…`)에 적힌 같은 경로의 값과 **6/6 일치**. 적용 창 직후 만든 파일과 같은 바이트임 |
| 비밀값 | 서버에서 `eyJ`·`PRIVATE KEY`·`client-key-data`·`token: `·`password` 파일별 0건(`grep -c`), 복원본도 0건. Secret 객체 조회 없음 |

## 파일

| 경로(`control01/p65-apply-20261007/` 아래) | 크기 | SHA256 | 내용과 판독 |
|---|---|---|---|
| `pre/09-eps.json` | 3514 | `ee3475e9…` | 사전 `transaction-api-nodeport` EndpointSlice. ready endpoint 3개 모두 `k8s-worker02`(`.230`·`.233`·`.234`) |
| `apply/transaction-api-eps.json` | 4166 | `27ee6ba7…` | transaction-api 적용 직후. ready=true는 `k8s-worker01`(`.79.112`)·`k8s-worker03`(`.39.208`)·`k8s-worker02`(`.69.236`) 각 1개, 옛 Pod `.69.230`은 `k8s-worker02` ready=false(종료 중) |
| `apply/fds-engine-ta-eps.json` | 3665 | `80061df4…` | fds-engine 적용 후 같은 Service. ready endpoint `k8s-worker01`·`k8s-worker03`·`k8s-worker02` 각 1개 |
| `pre/pre-deploy.yaml` | 9363 | `5f2f02a4…` | 사전 두 Deployment 전체. `topologySpreadConstraints` 없음 |
| `apply/post-deploy.yaml` | 9999 | `24c3bd4d…` | 사후 두 Deployment 전체. 두 앱 모두 `maxSkew: 1`·`kubernetes.io/hostname`·`DoNotSchedule`·`nodeTaintsPolicy: Honor`·`matchLabelKeys: [pod-template-hash]`, `labelSelector` 앱별 |
| `pre/mon-post-final-pods.json` | 68754 | `4a05f052…` | 최종 MON 판정 시점의 `fds-app` Pod 전체(배치·Ready·IP) |

## 남은 서버 전용 파일 (14개)

server dry-run 전체 JSON 4개(`apply/*-dryrun.json`, `apply/*-unspread-dryrun.json`)와 MON 회차별 Pod JSON 10개(`pre/mon-after-*-pods.json`, `pre/mon-pre-pods.json`)는 서버에만 있습니다. 해시는 evidence#136의 `SHA256SUMS.all`에 있고, 판정 결과는 그 폴더의 `*-dryrun-check.txt`·`*-mon-*.txt`에 있습니다.

## 한계

- 이 보충은 적용 시점의 배치와 endpoint 원문입니다. drain·장애 시 보장, 자동 재분산, #22 HA, 현재 서버 상태는 범위 밖입니다.
- 위 EndpointSlice 3개는 모두 `transaction-api-nodeport`입니다. fds-engine Service의 EndpointSlice는 이번 적용 창에서 수집하지 않았습니다.
- fds-engine MON 61.0초 절차 이탈은 그대로입니다(evidence#136 README "정정 1").

## 파일 무결성

- `SHA256SUMS`: 이 폴더 전체 파일(README 포함, 자기 자신 제외)
- `ARCHIVE_CONTENTS`: `control01/ev-p65-extra.tgz` 내부 목록(크기·경로)
- `registry/ARCHIVE_CONTENTS.json`에 같은 묶음의 내부 해시 목록 등록
