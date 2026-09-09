# P1-DNS-01 R2 Evidence Index

- Generated: 2026-09-03T11:09:36+09:00
- Baseline: FDS Project Implementation Baseline v3.1.14
- Ticket Status: In Review — Support Review pending

| Test ID | Acceptance Criterion | Result | Evidence Relative Path / SHA-256 |
|---|---|---:|---|
| DNS-PT-01 | dns01 내부 A/SOA 및 승인 Record 13개 | PASS | `dns01/20260902T184229+0900_dns01_evidence.txt`<br>`4c9776bf619e18fc58952e11bee35f92f3b2737e2e9575ba47f9ad871077f932`<br>`inventory/20260902T212724+0900_dns_record_inventory_evidence.txt`<br>`db3b16e8290908437f3153afe6978eca8ba54d4041671e2a8d4c59e1a79dbe9d` |
| DNS-PT-02 | dns02 내부 A/SOA 및 승인 Record 13개 | PASS | `dns02/20260902T184239+0900_dns02_evidence.txt`<br>`097dff21ebda5e75825f9b81145dbecb0116149a4a9c0e86c6460459af509fc2`<br>`inventory/20260902T212724+0900_dns_record_inventory_evidence.txt`<br>`db3b16e8290908437f3153afe6978eca8ba54d4041671e2a8d4c59e1a79dbe9d` |
| DNS-PT-03 | dns01/dns02 External Forwarding | PASS | `dns01/20260902T184229+0900_dns01_evidence.txt`<br>`4c9776bf619e18fc58952e11bee35f92f3b2737e2e9575ba47f9ad871077f932`<br>`dns02/20260902T184239+0900_dns02_evidence.txt`<br>`097dff21ebda5e75825f9b81145dbecb0116149a4a9c0e86c6460459af509fc2` |
| DNS-PT-04 | Fresh HMAC-SHA256 TSIG Zone Transfer | PASS | `tsig/20260902T212908+0900_dns02_fresh_tsig_evidence.txt`<br>`147722d9b7c84b680678248aa062ba28f546fa8b8b42e6c9680335908340c745` |
| DNS-PT-05 | Primary 장애 중 Secondary 서비스 및 복구 | PASS | `failover/20260902T184138+0900_k8s_control01_failover_evidence.txt`<br>`51e8bcd810fdf6a03e12f8f0e7dc261d8b17a9dbaa0320bcbbab2b4bcace60c2`<br>`failover/20260902T184144+0900_k8s_api_lb01_failover_evidence.txt`<br>`d3fd6d82986e6ef8b4ca5250d533df0ea9b9796e9a3ab6308f808c048f69de9f`<br>`recovery/20260902T184205+0900_dns01_recovery_evidence.txt`<br>`e5c84fe232075d13e6840acd23ea89e99d10f6e0eda68a4ee67fa04ae4c80ecb` |
| DNS-NT-01 | 비승인 Source 내부 Query 차단 | PASS | `monitor01/20260902T184303+0900_monitor01_negative.txt`<br>`76c8c52c7ebc4761115180bc1e270ec1e60ba0d3069ea9459c1f489f1beb4f6e` |
| DNS-NT-02 | 미인증 AXFR 거부 | PASS | `dns01/20260902T184229+0900_dns01_evidence.txt`<br>`4c9776bf619e18fc58952e11bee35f92f3b2737e2e9575ba47f9ad871077f932`<br>`dns02/20260902T184239+0900_dns02_evidence.txt`<br>`097dff21ebda5e75825f9b81145dbecb0116149a4a9c0e86c6460459af509fc2` |
| DNS-NT-03 | 비승인 Source 재귀 Query 차단 | PASS | `monitor01/20260902T184303+0900_monitor01_negative.txt`<br>`76c8c52c7ebc4761115180bc1e270ec1e60ba0d3069ea9459c1f489f1beb4f6e` |
| DNS-NT-04 | Reverse/PTR | N/A | Phase 1 Out of Scope — Ticket Description v1.2 |
| DNS-CR-01 | k8s-control01 Resolver Canary | PASS | `client/20260902T184246+0900_k8s_control01_evidence.txt`<br>`ab5a9540e71bdfefaafc0cc0d0a49debd016dae905810eb7c74adc181026a0ea` |
| DNS-CR-02 | Public Resolver Rollback | PASS | `rollback/20260902T184517+0900_k8s_control01_rollback_evidence.txt`<br>`c09fcd36a656014fe546ba05ee7192fced985870c522057d8bc03f26a42e917d` |
| DNS-CR-03 | 승인 Resolver 재적용 | PASS | `rollback/20260902T184517+0900_k8s_control01_rollback_evidence.txt`<br>`c09fcd36a656014fe546ba05ee7192fced985870c522057d8bc03f26a42e917d`<br>`client/20260902T184246+0900_k8s_control01_evidence.txt`<br>`ab5a9540e71bdfefaafc0cc0d0a49debd016dae905810eb7c74adc181026a0ea` |
| DNS-CR-04 | k8s-control01 `.52→.53` 자동 Failover | PASS | `failover/20260902T184138+0900_k8s_control01_failover_evidence.txt`<br>`51e8bcd810fdf6a03e12f8f0e7dc261d8b17a9dbaa0320bcbbab2b4bcace60c2` |
| DNS-CR-05 | k8s-api-lb01 `.109` Resolver/ACL/IPSet/Failover | PASS | `lb/20260902T184256+0900_k8s_api_lb01_evidence.txt`<br>`cfdcdd61425a522f8bad07715f9c5a8311602b2a2f4835a2c9cff3c6787481ea`<br>`failover/20260902T184144+0900_k8s_api_lb01_failover_evidence.txt`<br>`d3fd6d82986e6ef8b4ca5250d533df0ea9b9796e9a3ab6308f808c048f69de9f`<br>`dns01/20260902T184229+0900_dns01_evidence.txt`<br>`4c9776bf619e18fc58952e11bee35f92f3b2737e2e9575ba47f9ad871077f932`<br>`dns02/20260902T184239+0900_dns02_evidence.txt`<br>`097dff21ebda5e75825f9b81145dbecb0116149a4a9c0e86c6460459af509fc2` |
| DNS-EV-01 | dns01 원본·Sidecar 및 Record Inventory | PASS | `dns01/20260902T184229+0900_dns01_evidence.txt`<br>`4c9776bf619e18fc58952e11bee35f92f3b2737e2e9575ba47f9ad871077f932`<br>`inventory/20260902T212724+0900_dns_record_inventory_evidence.txt`<br>`db3b16e8290908437f3153afe6978eca8ba54d4041671e2a8d4c59e1a79dbe9d` |
| DNS-EV-02 | dns02 원본·Sidecar 및 Fresh TSIG | PASS | `dns02/20260902T184239+0900_dns02_evidence.txt`<br>`097dff21ebda5e75825f9b81145dbecb0116149a4a9c0e86c6460459af509fc2`<br>`tsig/20260902T212908+0900_dns02_fresh_tsig_evidence.txt`<br>`147722d9b7c84b680678248aa062ba28f546fa8b8b42e6c9680335908340c745` |
| DNS-EV-03 | 중앙 무결성 | PASS | 본 인덱스 생성 후 `generate_checksums_r2.sh`와 ZIP Sidecar 검증을 통과한 패키지만 정본 반영 |

## 보안 확인

- TSIG Secret content: EXCLUDED
- TSIG key file hash: EXCLUDED
- Authenticated AXFR TSIG MAC/record: EXCLUDED
- Reverse/PTR: N/A — Phase 1 Out of Scope
