# P1-SEC-01 — B2 clean immutable Runtime source-IP preservation (2026-10-01)

Record ID: **P1-SEC-01**

이번 수집은 기존 evidence PR #63의 실행-source exact binding 부족을 소급 보정하지 않고,
infra-ansible #60 병합 후 clean immutable main에서 새로 실행한 독립 수집회차이다.

| 항목 | 값 |
|---|---|
| Source merge | `c0d784fa9a1d9dfc57f504ed969c036d0860acef` |
| Collector SHA256 | `42fc3ed486b9b16f6be156b2770ada6cf9fa725c9b0a5882473afa0bd7eb9024` |
| Runtime | 2026-10-01 12:45:06 KST |
| Controller | ansible01 / server01_ansible |
| Ansible | core 2.16.19 |
| SSH source | 10.250.10.10 |
| P1 key fingerprint | `SHA256:VPGV/RGA8TrwO/3FC4YPxGzRNhBWuB+9hCzPV5plkws` |
| SSH preflight | 7/7 PASS |
| become preflight | 6/6 PASS |
| PLAY_RC / TEE_RC | 0 / 0 |
| Runtime raw files | 8 |
| Worker result | 3 PASS / 0 CHECK |
| Archive | `p1-sec01-b2-clean-runtime-20261001T034506Z.tar.gz` |

## Runtime result

edge01 `10.1.93.50`에서 worker01/02/03의 NodePort 30080 /readyz를 호출했다.
각 worker의 transaction-api Pod veth tcpdump에서 source `10.1.93.50`이 Pod까지
원본 보존됨을 확인했고 curl rc=0 및 HTTP 200을 함께 확인했다.

이 수집은 Pod-observed source-IP preservation과 해당 Positive HTTP path의 Runtime 증적이다.
전체 P1-SEC-01 완료, Negative path 전체 인수, Edge Cutover 완료를 단독으로 의미하지 않는다.

## Known follow-up

Ansible core 2.16.19 실행 중 non-boolean conditional 관련 deprecation warning 2건이 관찰됐다.
이번 worker별 실제 판정은 모두 PASS했으므로 본 실행 결과는 유지하되,
2.19+ 호환성 수정은 infra-ansible #9에서 별도 추적한다.

기존 evidence PR #63의 2026-09-28 실행은 본 수집으로 소급 승인하지 않는다.
