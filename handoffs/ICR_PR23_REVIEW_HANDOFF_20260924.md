# ICR PR23 독립 편입 검토 인계 — 2026-09-24 KST

상태: 원본 5개 전달본 작성·바이트 검증 완료 / 팀 archive 접근 인계 미확인 / 독립 편입 리뷰 대기 / 병합 없음.

현재 대상은5회차72개 증적 파일(그중 original48개)과 원본 archive5개/sidecar5개다. 전달본·AC20개 대조 결과는 문서 끝 최신 추록 및 [AC 대조표](ICR_AC_RECONCILIATION_20260924.md)를 확인한다. 아래 기존3회차·05:20·05:54 절의 수량·검증 수행·PR HEAD는 각각 당시 이력이며 최신 상태를 대신하지 않는다.

이 문서는 누적5회차 증적의 접근 경로와 검토 범위를 모은 인계 기록이다. 새 현장 실행, 원본 수정, 통신 복구, Runtime AC 인수 또는 독립 승인을 기록하지 않는다.

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

## 05:20 후보 메타데이터 회차 추가 — 2026-09-24 KST

- [새 회차 분석](../evidence/ICR-D-NET-01-01/negative-candidates-20260924T052009/README.md), [RECEIPT](../evidence/ICR-D-NET-01-01/negative-candidates-20260924T052009/RECEIPT.json), [후보 대조표](../evidence/ICR-D-NET-01-01/negative-candidates-20260924T052009/CANDIDATE_SUMMARY.json).
- `ICR_Negative_Candidates_tJeRl5.tar.gz`, 4,604 bytes, SHA256 `9f19fd8f06d932f1a3e2c8fe0789414e763bfac9b81c605fb806b83f914c4b30`.
- source `fa33b0dec11d3e02c97739b8a77524c365b939c4` / Pre-check PR33, source REVIEW=NOT PERFORMED (Pre-check).
- 외부·내부7/소스3 해시 대조와 실제 syntax-check·조회3/3 성공. Pod8개 중 일반 후보4개를 확인했다. 원문8개 및 sidecar/분석/receipt/manifest 등 새13파일이다.
- 기존 증적3회차46파일과 원문32파일은 그대로 보존한다. 이 추록까지 ICR 증적은4회차59파일, 그중 original40파일이며 인계 문서는 별도다.
- 권고 후보는 Grafana이나 시험 대상 승인·도구·현재 정책·실제 음성 probe는 미완료다. 과거01:21 정책과05:20 Pod 신원은 서로 다른 시점이다.
- archive 접근 인계 대상은 이제4개 archive와 각 sidecar다. 이번 원본은 사용자 첨부의 파일 식별자로만 연결돼 있고 팀 다운로드 URI/검토자 실제 접근 확인은 아직 없다. 원문을 다시 수집하거나 재압축하지 않는다.
- 이 인계 문서 갱신과 새 회차는 최신 PR HEAD의 독립 편입 검토 범위다. 기존 source/PARTIAL 판정, PR27 운영 리뷰·적용 HOLD, 다른 업무의 AC·담당·일정은 유지한다.

## 05:54 Grafana 정책 입력 회차 추가 — 2026-09-24 KST

- [새 회차 분석](../evidence/ICR-D-NET-01-01/grafana-policy-20260924T055428/README.md), [RECEIPT](../evidence/ICR-D-NET-01-01/grafana-policy-20260924T055428/RECEIPT.json), [정책 대조](../evidence/ICR-D-NET-01-01/grafana-policy-20260924T055428/POLICY_SUMMARY.json).
- `ICR_Grafana_Policy_oBrOMu.tar.gz`, 7,481 bytes, SHA256 `23b3c72d285395c7ad09ad309607d781d542aed892bdc62bc892a75a664547d5`.
- source `bded227a045847059dda657afbd9503ecc5db159` / PR34, merge `479bb55f53dadc7b8625cd037332483a0ed4e470`. REVIEW=NOT PERFORMED (Pre-check).
- 외부·내부7/소스3 해시와 실행 collector hash 일치. 실제 Ansible syntax-check·조회11/11 성공(로컬 API주소1+API GET10), Grafana 전후 투영 신원/RV 동일.
- K8s NP17개 중 Grafana를 선택하는5개의 egress 허용 합집합은 Prometheus TCP9090 및 DNS TCP/UDP53. .105:9100 허용 없음. Calico NP0/GNP7/Tier3/NetworkSet0/GlobalNetworkSet0. 관측 GNP selector는 Grafana Pod labels에 직접 일치하지 않는다. 실제 차단 성공·전체 dataplane 유효 정책 증명은 아님.
- 기존4회차59파일(원문40개)을 보존하고 새13파일(원문8개 포함)을 추가했다. 이제5회차72파일, 그중 original48파일이며 인계 문서는 별도다.
- 사용자는 Grafana 권고안으로 착수를 지시했고 운영 PR27은 `ffbfff8ebcd1ed53ebff7f3e70fb734e93221a0c`에서 신원·도구 확인·bounded 명령을 검토 제안으로 준비했다. 현재 정책 입력 수신은 보완됐으나 도구 확인/실제 probe/운영 실행 수용/독립 리뷰는 미완료다. 같은 후보·정책 조회 반복은 필요하지 않다.
- 원 archive 인계 대상은5개와 각각의 sidecar다. 파일 식별자와 Git 원문은 있으나 팀 archive 접근 URI/검토자 실제 다운로드 확인은 아직 없다. 기존 Draft 유지 이유이며 새로운 공통 Ready 게이트를 만든 것이 아니다.
- 원 API 전체 body는 미보존이며 투영 결과의 hash 검증과 구분한다. 원본·과거 PARTIAL·기존 AC·담당·일정·운영 manifest를 수정하지 않았다. 독립 편입 리뷰는 최신 PR HEAD 전체에 대해 진행한다.

## 원본 전달본 및 AC20개 대조 — 2026-09-24 KST

원본 보관 근거와 사용자 첨부를 다시 대조하여, 아래 archive5개 및 각각의 원본 sidecar를 묶었다. 이번에는 로컬에서 제공된 원본 바이트를 직접 읽어 outer SHA256·sidecar와 확인하고 ZIP 안에서도10파일 전부 바이트 동일성을 확인했다. 앞선 인계 작성 단계의 “원 archive 재검증 없음”은 그 당시 수행 범위이며 이번 검증과 구분한다.

| 원본 파일 | bytes | SHA256 |
|---|---:|---|
| ICR_MON_Precheck_N11a7g.tar.gz | 9,443 | `c7ef76c9e7a4b314df96e946ee4db5d7b71e96bb22224903b713cace31a2b724` |
| ICR_Scrape_Source_Q9M3kW.tar.gz | 10,233 | `2d4014cd30af788438a62a3d166bec372b7ac4919c9ae6527ea6a1427cb6c9f3` |
| ICR_Scrape_Counters_cXoiN1.tar.gz | 60,846 | `85e57eb5ab91562209538677fe1658fa4e3c6e6bc4810371a93d0d19f550ef47` |
| ICR_Negative_Candidates_tJeRl5.tar.gz | 4,604 | `9f19fd8f06d932f1a3e2c8fe0789414e763bfac9b81c605fb806b83f914c4b30` |
| ICR_Grafana_Policy_oBrOMu.tar.gz | 7,481 | `23b3c72d285395c7ad09ad309607d781d542aed892bdc62bc892a75a664547d5` |

전달본:

- 파일: `FDS_ICR_PR23_Original_Handoff_20260924_v1.0.zip`
- 크기: **101,021 bytes**
- SHA256: `119c0edc2d89ddf30ab95aa7ffe4a99b35b4b449b75965235043db3419b4b08d`
- 외부 해시 파일: `FDS_ICR_PR23_Original_Handoff_20260924_v1.0.zip.sha256`
- 구성: 원본 archive5개 + 원본 sidecar5개 + README.md + INDEX.json + SHA256SUMS =13개 항목. wrapper manifest는 자신을 제외한12항목을 검증한다.
- 검증: 원본 archive5/5 외부 hash 일치, 원본 sidecar5/5 Git 편입본 일치, ZIP에서 꺼낸 원본10/10 바이트 동일, wrapper manifest12/12 일치, ZIP CRC 이상 없음.
- ZIP_STORED 전달용 외피다. 원본 tar.gz를 풀거나 재압축하지 않았고, archive 내부 manifest도 수정하지 않았다. Git binary/Release Asset 업로드는 없다.
- README에는 사용자 다운로드 후 외부 hash·wrapper manifest·원본 sidecar를 확인하는 절차와 추출 폴더를 기록했다. 이 ZIP은 서버 실행 키트가 아니다.

사용자에게 전달본과 외부 해시 파일을 다운로드 제공한다. **이 제공은 팀 검토자의 접근 확인을 의미하지 않는다.** Git에 대화 내부 file ID나 사용자 전용 링크를 팀 접근 URI처럼 기록하지 않는다. 기존 승인된 팀 전용 보관 위치에 두 파일을 전달하고 기존 PR23에 URI와 실제 수신 결과를 연결한다. 새 공유 권한·계정·별도 승인 양식은 만들지 않는다.

- 전달본 준비·로컬 바이트 검증: COMPLETE
- 팀 archive 접근 URI: UNCONFIRMED
- 검토자의 실제 다운로드·outer hash 확인: NOT CONFIRMED
- 독립 편입 리뷰: PENDING / MERGE: NOT DONE
- Draft 유지: 원본 접근 인계 미확인 사유 유지. 준비 완료를 독립 승인으로 처리하지 않는다.

[AC20개 대조표](ICR_AC_RECONCILIATION_20260924.md)는 기존3 PASS/8 PARTIAL/2 FAIL(보고)/6 NOT_VERIFIED/1 BLOCKED를 유지하며 과거 원본 연결과 실제 잔여 시험을 구분한다. CP 변경 전 route와 Gate2·지정 Worker pull의 당시 원본은 이번5archive에 포함됐다고 주장하지 않는다. 기존08/13/14 PASS는 재사용하며 완료 작업을 다시 시작하지 않는다.

MON05:59 K8s 수집 완료와 monitor01 콘솔 준비는 [MON PR9](https://github.com/321Team/infra-monitoring/pull/9), source `efcbed006d9e777a23ae145bfb425c33a4c742b5`에 연결한다. monitor01 실제 결과는 미수신이고 CM에는 remote_write가 없어 IF-06B 송신/수신 인수는 남는다. 별도 TLS PR31·MON·LB 작업을 이 PR에서 중복 실행하지 않는다.

이번 Git 변경은 이 인계 문서와 AC 대조표뿐이다. 기존72증적/48original 파일의 보존과 최종HEAD의 CI·리뷰 상태는 게시 검증 댓글로 연결한다. 서버 조회·active probe·운영 manifest 변경·AC 상태 변경은 수행하지 않았다.
