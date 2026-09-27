# P1-SEC-01 — B1(CP GNP 10250)·B2(transaction-api NodePort) 조치 후 상태 수집본 (2026-09-27)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). GWONUK Review Owner 판정의 B1/B2 대응. 관련 코멘트: [B1/B2 종합 정리](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5853684178), [B2 조치](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5853570610).

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-b1b2-20260927-20260927T074845Z.tar.gz` |
| SHA-256 | 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 | k8s-control01, `server02`, 2026-09-27 (kubectl get 조회, 변경 없음 — read-only) |
| 전달 경로 | control01 → ansible01(`scp`, sha256 재계산 일치 확인) → 사용자가 zip으로 압축해 세션에 업로드 → 세션에서 압축 해제 후 SHA-256 재확인 |
| 수집·제공 | 이하영(P1-SEC-01 Lead). 수집·편입 정리는 Claude Code 보조 |

## 수신 검증

- tar.gz 내부 `SHA256SUMS`(6개 파일 대상) 전부 재계산 일치 확인
- 비밀정보 검색: `password|secret.{0,20}=|token.{0,20}=|BEGIN (RSA|EC|PRIVATE) KEY|postgresql://|ENC_KEY=` 패턴 0건
- 압축을 다시 하거나 내용을 고치지 않음

## 내용물 요약 (원본 보존 — 판정 아님)

| 파일 | 내용 | 관련 blocker |
|---|---|---|
| `b1-gnp-k8s-control01-after.yaml`, `...control02...`, `...control03...` | CP 3대 GlobalNetworkPolicy 현재(조치 후) 상태. `10250` ingress source가 6개 노드(CP3+Worker3) 전체, `2379/2380`(etcd) source는 CP 3대만으로 유지됨을 확인. [infra-kubernetes PR#48](https://github.com/321Team/infra-kubernetes/pull/48) 병합 source와 일치 | B1 |
| `b2-svc-after.yaml` | `transaction-api`(ClusterIP, nodePort 없음) / `transaction-api-nodeport`(NodePort, `80:30080/TCP`만, metrics 미노출) Service 현재 상태 | B2 |
| `b2-endpoints-after.txt` | 두 Service의 Endpoints. `transaction-api`는 9091+8000 유지(Prometheus 내부 스크레이프 영향 없음), `transaction-api-nodeport`는 8000만 | B2 |
| `00-environment.txt` | `kubectl version` (Client/Server v1.36.4), 수집 시각(UTC) | — |

## 세션 중 조치 요약

- **B1**: 현장에 이미 반영돼 있던 CP 3대 GNP의 10250 6-node 허용을, 병합된 git source([PR#48](https://github.com/321Team/infra-kubernetes/pull/48))와 대조해 3대 전부 일치함을 확인. 신규 Runtime 변경 없음(이미 일치 상태였음을 확인만 함).
- **B2**: `transaction-api` Service가 승인 source와 다르게 `type: NodePort`로 변경되어 metrics(9091)에도 `nodePort: 32085`가 자동 할당돼 있던 것을 확인. `transaction-api`를 ClusterIP로 복구하고 별도 `transaction-api-nodeport`(HTTP 30080 only) Service를 신규 생성해 승인 source([PR#36](https://github.com/321Team/infra-kubernetes/pull/36)) 형태로 정합화. 조치 전/후 기능 회귀 없음(Endpoints 정상, 30080 접근성 유지, 32085 노출 제거).

## 한계·미수신 (이번 회차에서 하지 않은 것)

- **B2 조치 전(before) 상태의 raw 파일**: `transaction-api` Service의 조치 전 yaml은 대화 세션에 붙여넣기(paste)로만 남아있고, 이번 tar.gz에는 조치 후(after) 상태만 원본 파일로 포함됨. 조치 전 상태는 baseline #19 코멘트 텍스트로만 존재.
- **32085 외부 접근 테스트 raw 로그**: ansible01에서 수행한 30080/32085 connectivity probe(`/dev/tcp`)의 원본 출력은 이번 tar.gz에 포함하지 않음(대화 세션 paste로만 존재). 후속 수집 필요.
- **edge01(승인 source)에서의 30080 연결 확인**: 이번 세션에서 edge01 접근 경로 자체가 확인되지 않아 미실행.
- **B3(kubelet serverTLSBootstrap 6-node)**: 이 편입 범위 밖. [infra-ansible PR#55](https://github.com/321Team/infra-ansible/pull/55) 리뷰 승인 완료했으나 CI(`ansible-isolated` 러너) 미가동으로 병합·Runtime 적용 보류 중.
- **AC 최종 충족 판정**: 이 편입은 원본 보존이며, SEC-AC-01/03/04/06의 baseline AC 체크·Status 변경은 하지 않음. AC 판정은 P1-SEC-01 Lead(이하영)가 baseline #19에서 별도로 함.

이 편입은 원본 보존이다. P1-SEC-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
