# P1-MON-01 — 외부 아티팩트 근거(S8-CANON) 수신 검토 (2026-09-24)

판정: **참고 사본으로만 편입. 원본 증적이 아니다.** [baseline #17](https://github.com/321Team/fds-project-baseline/issues/17) AC "Test Alert Firing → Alertmanager 수신 → Resolved 전이가 PASS다"의 근거로 연결된 아티팩트 카드를 발췌하고 확인 가능한 범위만 대조한다. AC 판정·Status는 바꾸지 않는다(Lead 이재환 판단).

## 수신 정보

| 항목 | 값 |
|---|---|
| 출처 | `https://claude.ai/artifact/UCatzSQWiTdLxHXzeABRhe`, Phase E `S8-CANON / TC-TARGET-CANON` 카드 |
| 아티팩트 원본 | 이 저장소의 [`evidence/P1-DB-01/received-20260924T075714Z/artifact/UCatzSQWiTdLxHXzeABRhe.html`](../../P1-DB-01/received-20260924T075714Z/artifact/UCatzSQWiTdLxHXzeABRhe.html) 한 부만 보관한다. SHA-256 `2d16863a590b1236b7fc37d926c1af73b1d1fd6b4366616f2372a70d13dec015`. 수신 경위·작성자 미확인·공개 링크 문제는 그 폴더의 `RECEIPT_REVIEW.md`와 같다 |
| 발췌 | `CARD_EXTRACT_S8-CANON_TC-TARGET-CANON.txt` — 위 HTML의 카드 정의를 글자 그대로 잘라낸 파생 파일 |

## 카드 서술과 대조

| 서술 | 대조 결과 |
|---|---|
| 2026-09-22 정본 클러스터에서 kube-state-metrics replicas 1→0→1 조작 후 Discord에 `TargetDown` FIRING과 RESOLVED 수신 | **확인 불가.** 카드의 `evidence` 목록이 비어 있고 "사용자가 직접 스크린샷으로 확인"이라고만 적혀 있다. 스크린샷·`kubectl scale` 출력·Alertmanager 로그는 수신되지 않았다 |
| Prometheus rule `up{job=~"transaction-api\|fds-engine\|kube-state-metrics"} == 0`, `for: 1m`, `severity: critical` | **정적 일치.** [infra-monitoring `kubernetes/monitoring/alert-rules.yaml`](https://github.com/321Team/infra-monitoring/blob/fe2ad2684bfd3c120369761a5fdb40d1c575c2ec/kubernetes/monitoring/alert-rules.yaml)(SHA-256 `66eee0152435b3c57489e7e7b5b045facac6af60d52ef045569e05fbd4fef0f2`) 52~56행과 같다. 실제 클러스터 적용본과 같은지는 확인하지 않았다 |
| #17 본문의 `FDSMonitoringPipelineTest`(p0-pipeline-test) FIRING→RESOLVED Discord 수신 | **정적 설계만 확인.** [`p0-test-alert.yaml`](https://github.com/321Team/infra-monitoring/blob/fe2ad2684bfd3c120369761a5fdb40d1c575c2ec/kubernetes/monitoring/p0-test-alert.yaml)(SHA-256 `964ba428502efd48b6b08091078b7fb4b505eaac70310f2f104035502805fc01`)은 기본값이 `vector(1) == 0`(비활성)이고, 시연 때 `vector(1) == 1`로 바꿔 발화시키는 설계다. 전환 스크립트는 main에서 `references/e-k3s/scripts/demo/s7b_test_alert.sh`에만 있다. 실제 전환·수신 기록은 없다 |

## 미수신 원본 (Lead 이재환 제출 요청 대상)

1. Discord FIRING·RESOLVED 수신 화면 원본(시각 표시 포함)과 SHA-256
2. `kubectl scale` 실행·복구 출력과 Alertmanager 수신 로그(또는 `/api/v2/alerts` 조회 결과)
3. p0 Test Alert 전환 실행 기록(사용한 스크립트 경로·Commit, 전환 전후 ConfigMap)
4. 같은 AC 절에서 근거 링크 없이 체크된 항목(Grafana Provisioning, Service 유형, Port-forward, RBAC, PVC 유지)의 조회 출력

## 이번에 하지 않은 것

- 클러스터·Discord 조회, AC 체크 변경, baseline #17 본문 수정
