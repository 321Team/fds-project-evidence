# P1-APP-01 — transaction-api NodePort Service·EndpointSlice Worker별 local endpoint 조회 (2026-10-02 16:12 KST)

APP Lead(이재환)가 k8s-control01(`server02`)에서 조회만 했다. 대상은 [#15](https://github.com/321Team/fds-project-baseline/issues/15)의 미체크 두 줄이다.
- 핵심 요구 "`externalTrafficPolicy: Local` 대상 Worker에 local endpoint를 보장한다."
- Runtime AC "승인 Worker backend에 local endpoint 존재"

**운영 변경: 없다.** `kubectl get`(yaml·jsonpath)만 실행했다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/app15-ep-20261002T161253/`(파일 8개) | `app15-ep-20261002T161253.tgz` 1,883 B, SHA-256 `d2ce95f1…5d88f434` | 서버에서 묶어 base64로 받았다. 복원본이 서버 `sha256sum`과 일치했다. 개별 파일 8개도 서버 출력과 일치했다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 개별 파일은 archive를 그대로 푼 것이다. 비밀 정보 검색 0건이다.

## 관측

| 파일 | 내용 |
|---|---|
| `01-nodes.txt` | 노드 6대 Ready. Worker는 `k8s-worker01` `10.1.93.105`, `k8s-worker02` `10.1.93.107`, `k8s-worker03` `10.1.93.108` |
| `02-svc.yaml`, `03-svc-summary.txt` | `fds-app/transaction-api-nodeport`: `NodePort`, `externalTrafficPolicy=Local`, `nodePort=30080`, `targetPort=8000` |
| `04-eps.yaml`, `05-eps-by-node.txt` | EndpointSlice endpoint 3개. Worker마다 1개씩이고 모두 `ready=true serving=true terminating=false`: worker03 `m65z4`(`10.244.39.248`), worker01 `rq9b6`(`10.244.79.100`), worker02 `szcdq`(`10.244.69.221`) |
| `06-pods.txt` | 위 3개 Pod `1/1 Running`. 재시작: `m65z4` 0, `rq9b6` 3(21시간 전), `szcdq` 0(4시간 35분 전 생성 — 10/2 Drain 재시험 뒤 재배치) |
| `07-deploy-topology.txt` | Deployment `replicas=3 ready=3`, **`topologySpreadConstraints` 없음, `affinity` 없음** |

## 판정 범위

| 줄 | 판단 |
|---|---|
| Runtime AC "승인 Worker backend에 local endpoint 존재" | 조회 시점(16:12)에 승인 Worker 3대 모두에 준비된 local endpoint가 1개씩 있다. 단 edge01 nginx upstream은 아직 Worker가 아니라 옛 `10.1.93.50:30080`을 가리킨다(P1-MON-01 `received-20260929T0656Z/edge01`). edge01 upstream 전환은 #19/SEC 범위이며 이 조회로 확인하지 않았다 |
| 핵심 요구 "local endpoint를 **보장**한다" | **미충족 근거.** Worker마다 1개씩 두도록 강제하는 설정(`topologySpreadConstraints`·`podAntiAffinity`)이 없다. 현재 1개씩인 것은 스케줄 결과일 뿐이다. 10/2 Drain 재시험 때 새 Pod가 worker01로 몰렸다가 수동으로 재배치한 사례가 있다(evidence#92) |

- 이 기록으로 #15 AC를 바꾸지 않는다. 체크 여부는 병합 뒤 APP Lead가 판단한다.
- 본문 비고가 가리키는 "P1-LB Stage B"는 API LB(`.109:6443`) 시험이라 이 두 줄의 근거가 아니다.
