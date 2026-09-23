# ICR PR23 독립 편입 검토 인계 — 2026-09-24 KST

상태: 검토 자료 정리 완료 / 원 archive 접근 인계 미확인 / 독립 편입 리뷰 대기 / 병합 없음.

이 문서는 기존 3회차 증적의 접근 경로와 검토 범위를 모은 인계 기록이다. 새 현장 실행, 원본 수정, 통신 복구, Runtime AC 인수 또는 독립 승인을 기록하지 않는다.

## 검토 대상

- PR: https://github.com/321Team/fds-project-evidence/pull/23
- 기존 증적 기준 commit: `2f8a238142ad669a35800bb3e8ecc6d372354d60`
- 해당 commit의 3회차 46파일을 보존한다. 그중 `original/` 원문은 8 + 13 + 11 = 32파일이다.
- 본 문서 추가 후 최종 검토 SHA는 PR 본문 및 게시 검증 댓글에서 확인한다. 기준 commit의 원본 blob과 최종 검토 commit의 원본 blob이 같은지 확인한다.
- 현재 GitHub 요청 Reviewer: `hayeounglee`. 요청 상태는 승인 완료가 아니다.
- 기준: [EVIDENCE_POLICY](https://github.com/321Team/fds-project-evidence/blob/2f8a238142ad669a35800bb3e8ecc6d372354d60/governance/EVIDENCE_POLICY.md), [중앙 리뷰 정책](https://github.com/321Team/fds-project-baseline/blob/e491eb8363533828fe00aab103c369c6626edd2e/governance/REVIEW_AUTHORITY_POLICY.md).

## 3회차 열람 순서와 한계

| 회차 | Git의 검토 자료 | 유지할 판정 |
|---|---|---|
| 01:21 MON 사전점검 | [README](../evidence/ICR-D-NET-01-01/monitoring-precheck-20260924T012110/README.md), [RECEIPT](../evidence/ICR-D-NET-01-01/monitoring-precheck-20260924T012110/RECEIPT.json), [원문](../evidence/ICR-D-NET-01-01/monitoring-precheck-20260924T012110/original/) | 실제 조회 17/17 성공. Sender·HEP/GNP·관련 NP snapshot이며 당시 실제 packet Source는 미관측. |
| 02:05 Source | [README](../evidence/ICR-D-NET-01-01/scrape-source-20260924T020500/README.md), [RECEIPT](../evidence/ICR-D-NET-01-01/scrape-source-20260924T020500/RECEIPT.json), [원문](../evidence/ICR-D-NET-01-01/scrape-source-20260924T020500/original/), [대응표](../evidence/ICR-D-NET-01-01/scrape-source-20260924T020500/FLOW_CORRELATION.json) | 3지점의 SYN 64개 / 19개 연결 대응 및 Pod→node SNAT·출발 포트 변환. counter 조회 8건 오류로 PARTIAL 유지. |
| 02:40 counter 보완 | [README](../evidence/ICR-D-NET-01-01/scrape-counters-20260924T024027/README.md), [RECEIPT](../evidence/ICR-D-NET-01-01/scrape-counters-20260924T024027/RECEIPT.json), [원문](../evidence/ICR-D-NET-01-01/scrape-counters-20260924T024027/original/), [증가량](../evidence/ICR-D-NET-01-01/scrape-counters-20260924T024027/COUNTER_DELTA_SUMMARY.json) | 조회 9/9 성공. Worker01 named host-GNP 최종 DROP +46 packets / 2,760 bytes. 집계 counter이며 per-flow/PID 귀속·통신 복구 증거는 아님. |

각 회차의 상위 `SHA256SUMS`는 편입 자료, `original/SHA256SUMS`는 수신 원문 내부의 manifest다. 검증 위치와 대상을 구분한다. 기존 수신 기록의 외부/내부/소스 해시 일치 결과를 재사용하며, 이번 인계 작업에서 원 archive 바이트를 다시 읽고 검증한 것으로 표시하지 않는다.

앞선 64 SYN과 나중의 46 DROP은 서로 다른 관측 창이다. 02:40 성공으로 02:05의 오류 원본이나 PARTIAL 판정을 수정하지 않는다. 세 수집 source는 모두 `REVIEW=NOT PERFORMED (Pre-check)`이며 소스의 예외 병합을 독립 증적 편입 승인으로 해석하지 않는다.

## 원 archive 접근 인계 — 실제 남은 입력

| 원본 파일 | bytes | SHA-256 |
|---|---:|---|
| ICR_MON_Precheck_N11a7g.tar.gz | 9443 | `c7ef76c9e7a4b314df96e946ee4db5d7b71e96bb22224903b713cace31a2b724` |
| ICR_Scrape_Source_Q9M3kW.tar.gz | 10233 | `2d4014cd30af788438a62a3d166bec372b7ac4919c9ae6527ea6a1427cb6c9f3` |
| ICR_Scrape_Counters_cXoiN1.tar.gz | 60846 | `85e57eb5ab91562209538677fe1658fa4e3c6e6bc4810371a93d0d19f550ef47` |

확인된 보관 근거는 사용자 원 첨부와 각 RECEIPT의 식별자다. **첨부 식별자·대화 내부 file ID는 팀 검토자가 열 수 있는 URI가 아니다.** 검토자의 실제 다운로드 가능 여부는 미확인이다. 원 archive 및 sidecar를 기존 승인된 팀 전용 보관 위치에 원래 바이트로 전달하고, 이 PR에 접근 경로와 수신 확인을 연결하면 된다. 별도 양식이나 신규 계정은 필요하지 않다.

현재 값을 미리 채우지 않는다:
- archive/sidecar 접근 URI: UNCONFIRMED
- 검토자 실제 다운로드 및 outer hash 대조: NOT CONFIRMED
- 원본 수령/접근 인계 완료: NOT DONE

재압축, 수정된 manifest로 원본 대체, Git binary 편입, Public 링크, 임의 Release Asset 업로드는 이번 인계에서 하지 않았다. 새 수집 실행도 필요하지 않다. 보관 경로만 부족한 상황을 서버 시험 실패로 표시하지 않는다.

## 독립 검토에서 확인할 범위

1. 최종 검토 SHA와 원본 blob 보존 여부, 원본 출처 및 수신 바이트·외부/내부 manifest·실행 source 연결.
2. 실제 rc/stdout/stderr와 회차별 판정 일치. controller rc0만으로 하위 조회 전체 성공을 인정하지 않는다.
3. Source 대응과 counter 집계의 관측 한계, 02:05 오류 및 보완 회차 보존.
4. 민감정보·누락·오표기 및 실제 원 archive 접근 확인. 필요한 원본을 못 열면 그 항목을 미검토로 남긴다.
5. 증적 편입 판정과 별도 운영 변경·AC 판정 분리.

Ready 전환은 독립 승인 완료가 아니다. 본 건은 아직 원 archive 접근 인계가 확인되지 않아 Draft를 유지한다. 접근 인계를 보완한 뒤 Ready 전환과 독립 리뷰를 진행하고, 최소 1인의 독립 검토 후 기존 병합 담당 이권욱이 정확한 SHA와 잔여 차단을 확인한다. 이 문서는 새로운 팀 공통 Ready 정책을 만들지 않는다.

## 운영 후속과의 연결

- [PR27](https://github.com/321Team/infra-kubernetes/pull/27), `4f0f0903d36742c80e0cc298e579ea2d163ea449`: Ready / 독립 리뷰 대기 / APPLY HOLD. .108/32→.105/32 TCP9100 임시 후보이며 source 노드 IP를 Prometheus 전용 identity로 보지 않는다.
- 01:21 원문에서 worker03에 확인된 것은 Prometheus, hostNetwork node-exporter, hostNetwork calico-node다. 이 조회는 일반 workload 전체 목록이 아니므로 적합한 음성 시험 Pod가 없다고 단정하지 않는다. hostNetwork 또는 CNI 관리 Pod를 일반 비인가 workload 시험으로 자동 대체하지 않는다.
- PR27의 실제 잔여 입력은 worker03의 기존 승인된 일반 workload, 시험 가능한 기존 컨테이너, 정확한 .105:9100 명령 및 적용 egress 정책이다. 기존 17조회는 이 입력을 수집하지 않았다. 새 현장 조회는 이 메타데이터 누락에 한정한다.
- [PR31](https://github.com/321Team/infra-kubernetes/pull/31), `eb8bd864c6f016f3d599c658cac5397365c53f6f`: 별도 TLS 후보. 04:11 TLS 자료는 이 PR23의 위 3회차에 포함됐다고 주장하지 않으며 별도 MON/TLS 작업을 재수집하거나 수정하지 않는다.
- 증적 PR23 편입만으로 PR27/PR31 운영 변경이 승인되거나 ICR 전체가 종결되지 않는다.

## 이번 인계 검증 수준

GitHub 최신 PR·정책·RECEIPT 및 01:21 원문을 읽고 경로/해시/회차/원문 수를 대조했다. 새 문서 링크와 게시 diff/blob 보존 여부는 게시 검증 댓글에 기록한다. 원 archive 재다운로드, 새 서버 실행, 음성 probe, 독립 승인, 병합은 수행하지 않았다. CI는 최종 HEAD의 실제 상태를 별도 기록하며 0건이면 NOT RUN이다.

AI assistance: CODEX_ASSISTED.
