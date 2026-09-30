# P1-MON-01 — NetworkPolicy 정리 현장 적용과 양성·음성 재시험 (2026-09-30 15:21~15:30 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 [infra-monitoring#25](https://github.com/321Team/infra-monitoring/pull/25)(GWONUK APPROVED [5351074972](https://github.com/321Team/infra-monitoring/pull/25#pullrequestreview-5351074972), merge `c5e5076`)의 NetworkPolicy 정리를 현장에 적용하고, 적용 전후에 같은 확인을 돌렸다. #25 승인 경계("현장 object 삭제/apply, 양성·음성 재시험은 RUNTIME NOT RUN이며 별도 Gate")에 따라 이 증적으로 Runtime 결과를 따로 검토받는다.

**운영 변경:** `monitoring-api` NetworkPolicy 2개 갱신, 2개 삭제(`monitoring-api/allow-monitoring-egress-dns`, `fds-app/allow-monitoring-scrape`). Pod 재시작·이미지·Resource·다른 객체 변경은 없다.

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/` | `~/p1-mon-np-20260930T152145/` (파일 50개) | `p1-mon-np-20260930T152145.tar.xz` 17,216 B, SHA-256 `bf3fd433…0206059e` | base64로 받아 복원. 서버 `sha256sum`과 일치. 개별 파일은 archive를 그대로 푼 것이다 |

archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다.

## 적용 기록 (REVIEW_AUTHORITY_POLICY §4 — 운영 Runtime)

| 항목 | 내용 |
|---|---|
| 적용 소스 | infra-monitoring main `d71d00c`의 `kubernetes/monitoring/networkpolicy.yaml`(git blob `13aed0b`, SHA-256 `31362617…290128`). #25 병합(`c5e5076`) 뒤 이 파일은 바뀌지 않았다. 같은 main의 #26(Request/Limit)은 적용하지 않았다(digest 고정 조건) |
| 전달 | PC에서 `networkpolicy.yaml`·`np-check.sh`를 tar.gz→base64로 만들어 붙여넣고 복원, SHA-256 대조 `성공`(`npkit.tgz.b64` 보존) |
| 선행조건 | 적용 전 수집 대상 23/23 UP, Grafana Datasource OK, Alertmanager 연결, `kube-dns` 라벨 CoreDNS 2개, `kubectl diff`·server dry-run = 변경 2 / 무변경 4 |
| 성공 기준 | 적용 75초 뒤 수집 대상 전부 UP·DNS 탐색 실패 증가 0·탐색 대상 수 불변, Datasource OK, Alertmanager 연결·전송 오류 0, Pod 재시작 없음, 필요 경로 양성 유지, 지운 경로 차단, 적용 뒤 `kubectl diff` rc=0 |
| 복구 방법 | `backup/`의 4개 원본으로 삭제 2개 `create`, 갱신 2개 `replace`(명령은 실행 전 제시). 성공 기준을 모두 충족해 실행하지 않았다 |
| 실행 | 15:25:30~15:25:31 `kubectl apply -f networkpolicy.yaml`(2 configured / 4 unchanged) → 두 객체 `delete`(`chg/`) |

## 확인 스크립트 `np-check.sh` (SHA-256 `b53f7b3b…bba82a3`) — 순수 검증기 분류

REVIEW_AUTHORITY_POLICY §3.2 4-1에 따라 담당 Lead가 순수 검증기로 판단해 적용 전(`pre`)·후(`post`)에 같은 파일로 실행했다.

- 조회(`kubectl get`, Prometheus·Alertmanager·Grafana 읽기 API)와 5초 연결 시도만 한다. 객체 생성·변경·삭제, 재시작·reload, 설치·상주가 없다(조건 1·2).
- 결과는 실행 폴더의 `pre/`·`post/`에만 남기고 운영 설정 입력으로 쓰지 않는다(조건 3).
- 기존 계정(`server02` + admin kubeconfig)과 Grafana Pod 안의 기존 관리자 환경 변수만 쓰고 값을 출력하지 않는다(조건 4).
- 부하·장애 주입·대량 스캔이 없다. 연결 시도는 회차당 30건 이하다(조건 5).
- 실행 기록: 대상 k8s-control01, 계정 `server02`, `pre` 15:21:52 · `post` 15:26:46 KST, 결과 `pre/`·`post/`, 명령은 `pre/console.txt`·`post/console.txt` 첫 줄 전후와 이 README.

## 결과

**수집·경로 (`pre/summary.txt` → `post/summary.txt`)**

| 확인 | 적용 전 | 적용 후 |
|---|---|---|
| 수집 대상 health | up 23 / 23 | up 23 / 23, lastError 없음 |
| DNS 탐색 | 실패 0 / 조회 16,518 | 실패 0 / 조회 16,538(계속 성공) |
| 탐색 대상 수(scrape pool 7개 + notify) | fds-engine 3, KSM 1, kubelet 6, cadvisor 6, node-exporter 3, prometheus 1, transaction-api 3 | 같음 |
| Alertmanager | active 1, dropped 0, 전송 오류 0 | 같음 |
| Grafana Datasource health | `OK` | `OK` |
| monitoring-api Pod | 재시작 0/0/2/0(KSM 2는 기존) | 같음 |
| NetworkPolicy 수 | monitoring-api 17, fds-app 4 | monitoring-api 16, fds-app 3 |
| 소스 ↔ 현장 | `kubectl diff` rc=1(변경 2개) | `kubectl diff` rc=0 |

**연결 시험 (`pre/np-matrix.txt` → `post/np-matrix.txt`)**

| 구분 | 시험 | 적용 전 | 적용 후 |
|---|---|---|---|
| 9/27 방식(호스트 방화벽) | control01 → Worker `:9100`·`:9101` / `:10250` | BLOCKED 6 / OPEN 3 | 같음 |
| 9/27 방식(NetworkPolicy) | fds-engine → Prometheus·Worker 9100, Grafana → 9100·KSM, Prometheus → 9101 | 모두 차단 | 같음 |
| 9/27 방식(양성) | Grafana → Prometheus 9090, Prometheus → Worker 9100 | 연결 | 같음 |
| 필요 경로(이름 해석 포함) | Prometheus → Alertmanager 9093, KSM 8080, transaction-api 9091, fds-engine 9090 / Grafana → Prometheus / Alertmanager → egress-proxy01 3128 | 모두 연결(프록시는 HTTP 400 응답 = 연결됨) | 같음 |
| **지운 경로** | Prometheus → kube-system 비DNS Pod(`10.244.246.113`) `:53` | `Connection refused`(정책 허용) | **`timed out`(차단)** |
| 좁힌 경로 | Prometheus → CP `.102:9100` | timed out | timed out |
| 교차 포트 | Prometheus → transaction-api `:9090`, fds-engine `:9091` | timed out | timed out |
| 옛 namespace | `fds` | 없음(NotFound) | 없음, `allow-prometheus-egress-scrape`는 `fds-app` 앱별 포트로 교체 |

- CP `.102:9100`은 적용 전에도 호스트 방화벽에서 막혀 있어, 이 항목의 변화는 객체 내용(`kubectl diff`: CP 3개 ipBlock 제거)으로 확인한다.
- 연결 시간(ms)으로 거부(즉시)와 차단(5초 timeout)을 구분했다.
- `post/prometheus-buildinfo.json`: 운영 Prometheus `3.14.0`(revision `d7598b7`, go1.26.6).

## 판정 범위

- 이 증적이 보여 주는 것: #25의 소스 정리가 현장에 그대로 반영됐고(적용 뒤 `kubectl diff` rc=0), 넓은 DNS 허용·옛 `fds` 규칙·CP 9100 egress·fds-app 교차 포트 ingress가 사라졌으며, 그 뒤에도 Scrape·Datasource·Alert 필요 경로와 이름 해석이 유지된다.
- 판단 대상: #17 핵심 요구 "Default Deny 이후 필요한 Scrape, Datasource, Alert, Remote Write 경로만 허용한다". 체크 여부는 이 PR 독립 리뷰 뒤 MON Lead가 판단한다.
- 한계: Remote Write(Prometheus → monitor01 `.30:443`) 규칙은 바꾸지 않았고, 수신 측(monitor01)이 HOLD라 동작 시험은 IF-06B 인수 때 한다. 9100/10250 호스트 경로(Calico HEP/GNP)는 별도 요구다. infra-kubernetes 03과의 중복 정의 정리(2단계)는 SEC Lead 확인 뒤 별도 변경이다(현장 `prometheus-allow`·`alertmanager-allow`·`grafana-allow`는 그대로).
- 적용 전후 조회본 `pre/np-*.yaml`·`post/np-*.yaml`은 현장 객체 전체 목록이다(`kubectl.kubernetes.io/last-applied-configuration` 포함).

AI 사용: CLAUDE_ASSISTED (명령·확인 스크립트·전달 묶음 준비, 수신 대조·판정·문서화, 실행은 담당자 본인)
