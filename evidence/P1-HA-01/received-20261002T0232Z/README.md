# P1-HA-01 — Worker Drain 가용성 재시험 (2026-10-02 11:32~11:36 KST, worker02)

HA Lead(이재환)가 결정안 [#22 5887966702](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5887966702)의 측정 방식·허용 기준으로 worker02 1대를 Drain하고 가용성 구간만 다시 측정했다. 명령은 담당자가 k8s-control01(`server02`)과 edge01(`server08`)에서 직접 실행했다(`commands.txt`). 9/27 시험(evidence#57)은 NOT VERIFIED로 두며 이 판정에 합산하지 않는다.

이 문서는 작성·자체점검 결과이며, 독립 Reviewer(#22 Support) 승인 전에는 AC 체크 근거로 확정하지 않는다.

## 요약

| 항목 | 값 |
|---|---|
| 도구 판정(`judge.py`, edge01 실행) | **PASS** (종료 코드 0) |
| 로컬 재판정 | 수신한 `probe.log`·`timeline.txt`로 PC에서 같은 `judge.py`를 다시 실행, 출력 7줄 일치(rc 0) |
| A 정상 Worker(.105·.108) 실패 요청 | **0건** (기준 0) |
| B 성공 응답 최대 간격 | **0.510초** (기준 ≤1.0초) |
| 측정 무결성 | 구간 전체 측정, 누락 tick 0, 발사 지연 최대 0.012초(기준 0.2), 기준선 비200 0건 |
| 판정 구간 | 11:32:38.981 ~ 11:35:56.286 KST (197.3초), tick 394개, 요청 1,182건 |
| 생성기 종료 | `END ticks 961 outstanding 0 saturated False` |

사람 판정(승인·보류)은 이 문서에 없다. Reviewer가 `commands.txt`·원본 로그·`judge.out`으로 결정한다.

## 기준·도구 근거

| 항목 | 값 |
|---|---|
| 결정안 | #22 [5887966702](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5887966702) (1~6절 그대로, 시험 뒤 변경 없음) |
| G3 수용 권고 | 권욱 [5922780836](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5922780836) (10/1) |
| Support(하영) 승인 | **시험 시작 전 #22 조회 기준 결정안에 대한 명시적 승인 댓글을 확인하지 못했다.** 하영 [5944159371](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5944159371)은 시간표 조율이다. 재환 [5943868410](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5943868410)이 "이견이 없으면 이 기준으로 판정"한다고 공지하고 진행했다 |
| 일정 조율 | 11:00~12:00 worker02 Drain 우선(권욱 [5943906763](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5943906763) 수용, 하영 5944159371 동의). 시험 중 다른 클러스터 변경 없음 |
| 도구 | infra-kubernetes#50 병합 `c55bad3`의 `ops/p1-ha-01-availability/` — `probe.py` `e2603769…9804`, `judge.py` `79f54c95…6aad`(결정안·`SHA256SUMS`와 일치, edge01에서 `sha256sum`으로 재확인) |
| 도구 검증 범위 | 도구 PR의 selftest 15/15(로컬 모의)와 권욱 독립 승인이 있다. 이 시험이 도구의 첫 운영 실행이다 |

## 사전 조건 (결정안 5절)

| 조건 | 결과 | 원본 |
|---|---|---|
| 노드 | control 3·worker 3 모두 Ready, worker02 SchedulingDisabled 아님 | 11:29 control01 출력(`commands.txt` 첫 명령) — **서버 원본 파일로는 저장하지 않았고 사용자 붙여넣기 출력 기준** |
| 배치 | transaction-api·fds-engine 각 3 Pod, Worker 3대에 1개씩 | `control01/ha22-20261002/pre-pods.txt` |
| NodePort | `transaction-api-nodeport` 30080, `externalTrafficPolicy: Local`, EndpointSlice 3개 | 11:29 control01 출력(붙여넣기) |
| 기준선 `/readyz` | edge01에서 3대 모두 200 (약 10ms, 11:29:55) | 11:29 edge01 출력(붙여넣기). 판정 구간 내 기준선 비200 0건은 `judge.out` |
| 시간 | edge01 System time 0.000168초 slow(11:31:45), control01 0.001359초 slow(11:32:17). 둘 다 한도 0.25초 이내 | `edge01/…/chrony-edge01-pre.txt`, `control01/…/chrony-control01-pre.txt` |
| 이미지 digest | fds-engine `5e2a081c…7369`, transaction-api `a7093136…cc33` (10/5 전환 전 이미지) | `control01/…/pre-images.txt` |
| 사전 재시작 횟수 | fds-engine bp6t6(worker01) 2, transaction-api rq9b6(worker01) 3 — 16시간 전 값이며 시험 중 증가 없음 | `pre-images.txt`, `post-images.txt` |

## 절차와 시각 (`timeline.txt`, control01 epoch)

| 단계 | KST | UTC |
|---|---|---|
| probe 시작(첫 tick) | 11:32:26 | 02:32:26Z |
| `baseline_start` | 11:32:38.981 | 02:32:38Z |
| `drain_start` | 11:33:40.985 | 02:33:40Z |
| `rescheduled_ready` | 11:33:52.024 (drain 시작 후 **11.0초**) | 02:33:52Z |
| `uncordon` | 11:34:54.283 | 02:34:54Z |
| `end` | 11:35:56.286 | 02:35:56Z |
| probe 종료 | 11:40:26 | 02:40:26Z |

- Drain 명령(결정안과 동일): `kubectl drain k8s-worker02 --pod-selector='app in (transaction-api,fds-engine)' --ignore-daemonsets --delete-emptydir-data --timeout=180s`. `drain.out`: transaction-api-b784c8c5d-75ws7·fds-engine-5699669f6f-d2vwq 퇴거, `drain rc=0`. `--timeout=180s`는 결정안에 없던 안전장치다(180초 안에 끝나 판정에 영향 없음).
- 재배치 Ready 판정: 두 Deployment `readyReplicas`가 모두 3이고 worker02에 해당 Pod가 0개(2초 간격 폴링).
- 관찰 구간: 기준선 62.0초, 재배치 Ready 뒤 62.3초, uncordon 뒤 62.0초(모두 60초 이상).
- 재배치 결과: 두 서비스의 새 Pod 2개가 worker01에 생성됐다(`ffhtr`·`hpwdv`, 각 서비스 worker01에 2개).

## 구간별 응답 (edge01 → Worker:30080 `/readyz`, 0.5초 tick, 구간은 tick 예정시각 기준)

| 구간 | .105 w01 | .107 w02(Drain 대상) | .108 w03 |
|---|---|---|---|
| 기준선 | 200×124 | 200×124 | 200×124 |
| drain → 재배치 Ready | 200×22 | 200×1, 000×21 | 200×22 |
| Ready 뒤 | 200×124 | 000×124 | 200×124 |
| uncordon 뒤 | 200×124 | 000×124 | 200×124 |

- .105·.108은 판정 구간 전 요청이 200이다. 응답시간은 최대 19.2ms.
- .107은 Drain 시작 뒤 Pod가 없어 `000`(Local 정책의 즉시 거부)이고, 결정안 3절에 따라 허용·판정 제외다(비200 269건 기록). uncordon만으로는 Pod가 돌아오지 않아 `000`이 이어졌다.

## 배치 복구 (판정 구간 밖)

- worker01의 새 Pod 2개(`fds-engine-5699669f6f-ffhtr`, `transaction-api-b784c8c5d-hpwdv`)를 삭제해 worker02에 재생성했다(`restore.out`). 삭제 명령 시각은 기록하지 않았다(NOT RECORDED). probe 로그상 .107의 첫 200은 11:37:17이다.
- 복구 후 Worker마다 두 서비스 1개씩, 이미지 digest 시험 전과 동일, 노드 6대 Ready(`post-pods.txt`, `post-images.txt`, `post-nodes.txt`).
- 판정 구간 종료 이후 로그(11:35:56~11:40:26): .105·.108은 541건 모두 200이다. 판정에는 쓰지 않는다.
- 복구는 probe가 끝나기 전에 실행했다. 판정 구간이 끝난 뒤이므로 판정에 영향이 없다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `edge01/` | edge01 `~/ha22-20261002` | `ha22-edge01-20261002.tgz`, SHA-256 `bfb657cd…64d3` | 서버 `.sha256` sidecar·PC 수신 `Get-FileHash`·저장 파일 일치. 풀린 폴더와 archive 내용 일치 |
| `control01/` | control01 `~/ha22-20261002` | `ha22-control01-20261002.tgz`, SHA-256 `7209701e…2465` | 서버 `sha256sum` 출력값과 PC에서 base64 복원한 파일 일치. **서버 `.sha256` 파일 자체는 수신하지 않아 sidecar는 서버 출력값으로 로컬에서 만들었다.** 풀린 폴더와 archive 내용 일치 |

- `timeline.txt`는 control01 원본과 edge01 사본이 같다(SHA-256 `a1f99fe4…25c7`). edge01 사본은 control01 출력 5줄을 옮겨 적은 것이다.
- Windows 로컬 재판정 시 한글 출력은 개행만 `\r\n`으로 달라진다(내용 동일).

## 한계·미검증

- **업무 거래(POST)·DB 저장 경로는 이 시험에서 보내지 않았다**(결정안 1절, `/readyz`만). Final E2E는 이미 체크된 AC라 반복하지 않았다.
- 사전 조건 중 노드·배치 일부와 `/readyz` 사전 응답, EndpointSlice는 서버 파일이 아니라 11:29 출력이다. 배치는 `pre-pods.txt`로 확인할 수 있다.
- Support(하영) 결정안 승인 댓글은 위 표와 같이 미확인이다.
- worker02만 커널이 `6.12.0-267`이고 나머지는 `-266`이다(11:29 `get nodes -o wide`). 어제 worker02 VM 정지·재기동 영향으로 추정되나 확인하지 않았다(NOT VERIFIED). 이 시험의 판정에는 쓰이지 않는다.
- 실행한 control01 시퀀스는 사전 코드 리뷰를 받은 파일이 아니라 담당자가 붙여넣은 일회성 명령이다. 판정 도구(`probe.py`·`judge.py`)는 병합된 `c55bad3` 그대로이고, Drain·uncordon 명령은 결정안과 같다.
- 시험은 worker02 1대, 1회만 수행했다. 반복 재현성은 이 증적으로 확인되지 않는다.
- 이 시험 중 다른 클러스터 시험·변경은 없었다(권욱 시간표 5943906763). 이를 서버에서 따로 검증하지는 않았다.

## 파일

| 경로 | 내용 |
|---|---|
| `commands.txt` | 실제 실행한 명령과 시각 |
| `edge01/ha22-edge01-20261002.tgz`(+`.sha256`) | edge01 원본 묶음 |
| `edge01/ha22-20261002/` | 위 묶음을 푼 사본: `probe.py`, `judge.py`, `probe.log`(2,883줄), `probe.stdout`, `timeline.txt`, `judge.out`, `chrony-edge01-pre.txt` |
| `control01/ha22-control01-20261002.tgz`(+`.sha256`) | control01 원본 묶음 |
| `control01/ha22-20261002/` | 위 묶음을 푼 사본: `timeline.txt`, `drain.out`, `restore.out`, `pre-pods.txt`·`post-pods.txt`, `pre-images.txt`·`post-images.txt`, `post-nodes.txt`, `chrony-control01-pre.txt` |
| `SHA256SUMS` | 이 폴더 파일의 SHA-256 |
