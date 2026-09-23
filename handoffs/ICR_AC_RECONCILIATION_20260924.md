# ICR-D-NET-01-01 AC 20개 증적 대조 — 2026-09-24 KST

기존 증적 재사용, 과거 원본 연결, 실제 잔여 시험을 구분한 후속 작업표다. 신규 서버 실행이나 AC 판정 변경은 없다. 책임·담당·일정·종결 조건은 [기존 ICR #14](https://github.com/321Team/fds-project-baseline/issues/14)를 유지한다. Lead 이권욱 / Support 이하영·이재환 / In Progress / End TBD.

판정 기준은 #14의 “Acceptance Criteria — 2026-09-23 전수 대조 반영” 절과 [기존 대조 기록](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5794357232)이다. **RUNTIME_PASS 3 / PARTIAL 8 / FAIL 2(담당자 Runtime 보고) / NOT_VERIFIED 6 / BLOCKED 1**을 그대로 유지한다. 이는 전체 구축 공수의 진행률이 아니다. 이번 5회차 수집 성공을 통신 복구·독립 인수로 승격하지 않는다.

## 근거와 최신 입력

| 자료 | 실제 확인 범위 | 이번 대조에서의 용도 |
|---|---|---|
| [01:21 사전점검](../evidence/ICR-D-NET-01-01/monitoring-precheck-20260924T012110/README.md) | 조회17/17, sender·HEP/GNP/NP snapshot | AC03의 실제 정책 입력 및 AC05/06 진단 기준 |
| [02:05 Source](../evidence/ICR-D-NET-01-01/scrape-source-20260924T020500/README.md) | 3지점64 SYN/19연결, Pod→worker03 SNAT. counter8건 오류/PARTIAL 보존 | scrape 경로 원인 분석. IF-06B Source 증거로 전용 불가 |
| [02:40 Counters](../evidence/ICR-D-NET-01-01/scrape-counters-20260924T024027/README.md) | 조회9/9, worker01 named host-GNP DROP +46 packets/2,760 bytes | AC05/06 네트워크 진단. per-flow/PID 귀속이나 Target UP 증거 아님 |
| [05:20 후보](../evidence/ICR-D-NET-01-01/negative-candidates-20260924T052009/README.md) | 조회3/3, worker03 Pod8개/일반 후보4개 | AC07 음성 시험 준비 입력 |
| [05:54 Grafana 정책](../evidence/ICR-D-NET-01-01/grafana-policy-20260924T055428/README.md) | 조회11/11, Grafana 신원 전후 동일, 선택 K8s NP5개에 TCP9100 허용 없음 | AC07 준비 입력. 실제 DENY/전체 effective policy 검증 아님 |
| [9/22 Gate2 실행 보고](https://github.com/321Team/infra-kubernetes/blob/2d35809313c70731c58d210b37ef29ed0a300883/docs/evidence/P1-SEC-01/GATE2_RUNTIME_EXECUTION_20260922.md) | 6대 firewalld 비활성·HEP/GNP6개, NodePort 적용, Harbor/앱 배포 보고. 원본 로그는 서버 보관 경로·해시로 기재 | AC02/03/04/09 및 AC20 원본 연결. 보고와 원본 직접 검수를 구분 |
| [MON 05:59 수신](https://github.com/321Team/infra-monitoring/blob/0b04ff5c34b45f07037551234b08e53bd7b4665d/docs/MON_FOLLOWUP_RECEIPT_20260924T055938.md) | control01 조회11/11·48객체, Pod7 Ready/PVC3 Bound. CM hash 대조상 remote_write 없음. monitor01 결과 없음 | AC09/12/16/17 의존성 최신화. Ready를 새 pull·scrape UP·TLS PASS로 확대하지 않음 |

5회차 Git 증적 기준은 `05d5ba3dc17ecc1e832840df7dfd5e716d24b484`, 증적72파일/그중 original48파일이다. MON 별도 archive와 TLS 자료는 이 5회차 전달본에 포함하지 않았다. 이 표는 위 자료 및 기존 #14 기록의 대조이며, 과거 모든 호스트 원본을 이번에 다시 수신·재실행했다는 뜻이 아니다.

## AC별 후속

작업 구분: **원본 연결**은 이미 수행한 작업의 당시 자료를 확보하는 일, **대조·인수**는 관측 자료와 승인 범위의 정합성을 검토하는 일, **실측 잔여**는 조건을 입증하는 시험이 남은 상태다. 한 AC에 여러 구분이 겹칠 수 있다.

| AC·현행 판정 | 재사용할 증거 | 남은 절차와 완료 근거 |
|---|---|---|
| **01 PARTIAL** — 변경 전 firewall/listener/route·SHA | #14의 6대 방화벽·리스너와 Worker3 route 자료 | **원본 연결:** CP2/3 최초 변경 전 route 원본 위치·당시 해시를 연결한다. resume/Join 자료에 route가 없음을 유지한다. 지금 새로 조회한 경로를 과거 baseline으로 대체하지 않는다. 원본 미발견은 미확보로 기록한다. |
| **02 PARTIAL** — firewalld 비활성·Calico 통신 | Gate2의 disabled/inactive6대 및 HEP/GNP 존재 보고, #14에 연결된 네트워크9/9 보고 | **원본 연결 + 대조·인수/실측 잔여:** 기존 네트워크 결과의 범위·원본을 연결하고, 빠진 Calico Pod/Node 통신과 현재 보호 범위를 확정한다. 이미 성공한 동일 조건은 재사용하고 변경 영향만 회귀한다. |
| **03 PARTIAL** — HEP/expectedIPs/Bootstrap Allow | Gate2 HEP6/GNP6 보고와 01:21 실제 HEP/GNP snapshot | **대조·인수:** named HEP·interface·actual expectedIPs·selector를 실제 v4 승인 manifest/Bootstrap Allow와 대응한다. 저장소의 별도 calico 예시를 승인 v4 적용본으로 간주하지 않는다. 승인 기준본 및 차이 판단 연결이 필요하다. |
| **04 PARTIAL** — .50→Worker:30080 허용·비승인 차단 | Gate2 적용 보고, [PR21](https://github.com/321Team/infra-kubernetes/pull/21)의 worker selector/order50, 01:21 정책 snapshot | **실측 잔여 + 인수:** .50 양성 및 승인된 비승인 Source 음성을 실제 서비스 조건에서 기록한다. 정상 양성 대조군과 정책 차단 근거를 함께 보존한다. 정책 존재만으로 PASS 처리하지 않는다. |
| **05 FAIL (보고)** — Worker3 node-exporter UP | 기존1/3 UP·2 timeout 보고, 02:05 SNAT 및 02:40 host-policy DROP | **실측 잔여:** [운영 PR27](https://github.com/321Team/infra-kubernetes/pull/27)의 제한 진단 후 정식 수정 범위와 Worker3 Target 결과를 연결한다. canary 1경로 성공만으로 3대 UP·영구 복구를 인정하지 않는다. |
| **06 FAIL (보고)** — Worker3 kubelet CA+SA | kubelet/cadvisor6 DOWN 보고. worker03 IP SAN 오류와 다른5 timeout을 구분 | **실측 잔여:** 네트워크는 PR27 진단과 연결하고 serving TLS는 [PR31](https://github.com/321Team/infra-kubernetes/pull/31)에서 처리한다. 이후 Worker3 CA+SA 결과를 확인한다. TCP 도달성·Pod Ready를 인증 성공으로 대체하지 않는다. |
| **07 NOT_VERIFIED** — 비승인 workload 9100/10250 차단 | 05:20 일반 후보, 05:54 Grafana UID/이미지/정책 입력 | **실측 잔여:** 승인된 일반 workload와 기존 도구로 실제 음성을 수행하고, 정상 양성 대조군 및 정책 귀속을 남긴다. Grafana의 .105:9100 준비는 10250과 전체 범위를 충족하지 않는다. timeout/refused/도구 없음/exec 실패만으로 DENY PASS 불가. |
| **08 RUNTIME_PASS** — CP logs/exec/port-forward | [9/21 원본·검증](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5755742235), 9고유조합×3기능=27/27 | **기존 PASS 유지:** 당시 구성에서의 유효한 증거를 재사용한다. 이후 HEP/GNP 변경 영향에 대한 관리 회귀는 별도 기록한다. 현재 작업의 API는 기존 LB .109:6443 경로를 사용하고 CP 직접 fallback을 추가하지 않는다. |
| **09 PARTIAL** — Harbor pull·Pod 시작 | Gate2 worker01 pull/앱 Running 보고 및 MON05:59 imageID·Pod7 Ready | **원본 연결 + 부족 범위 실측:** 지정 Worker별 실제 pull·Pod 시작의 원 실행 자료를 먼저 연결한다. Running/imageID만으로 각 Worker에서 새 pull 시험이 수행됐다고 주장하지 않는다. 승인 digest/이미지 보안 인수는 MON/HBR에 연결한다. |
| **10 PARTIAL** — Cockpit9090 비노출 | 기존 Worker3 masked/inactive·리스너 부재, #14의9/22 미청취6/6 보고 | **원본 연결 + 대조·인수:** 대상6대의 실제 서비스/리스너 결과와 보호 정책을 연결하고 전체 범위 비노출을 인수한다. 이미 확인한 상태를 새 미실행 항목으로 되돌리지 않는다. |
| **11 NOT_VERIFIED** — monitor01 신규 ingress 차단 | 기존 경로 설계 및 monitor01 콘솔 점검 준비 | **실측 잔여:** monitor01 서비스 입력을 확인한 뒤 승인 범위에서 Cluster workload로의 신규 ingress 음성 시험을 기록한다. 콘솔의 host/port 조회는 이 차단 시험을 대신하지 않는다. |
| **12 BLOCKED** — IF-06B TLS/Auth/Payload·비승인 egress | sender Pod 기동은 완료. MON05:59 NP에 .30/32:443 허용 선언, CM에는 remote_write 없음 | **차단 해소 → 실측:** MON Lead의 receiver 실행 모델·TLS/Auth/allowlist와 실제 sender 구성을 연결한 뒤 정상 Remote Write 및 비승인 egress를 검증한다. 예전 “sender 미배포”를 재차단 조건으로 사용하지 않는다. |
| **13 RUNTIME_PASS** — edge/harbor/db .30 via .58 | #14의9/18 원본·해시 및 .50/.54/.55 source route-get3/3 | **기존 PASS 유지:** 정상 기존 경로 관측을 재사용한다. 새 route 적용 영수증을 요구하지 않는다. Forward/NAT·실제 packet source·재부팅은 각각 AC15/17/18에 남긴다. |
| **14 RUNTIME_PASS** — Worker3 route 회귀 | [9/18 13:04](https://github.com/321Team/infra-kubernetes/blob/22673b0ba5ee188a514c5643bc3df8e7999a2d5a/ops/icr-followup-20260918/results/20260918T040403Z_zgby6ckp/README.md), [15:56 후속](https://github.com/321Team/infra-kubernetes/blob/ea4aef3c960fd79377225f7f037bc39cd04df469/ops/icr-followup-20260918/results/20260918T065614Z_zzi65aal/README.md), .105/.107/.108 via .58 | **기존 PASS 유지:** 당시 route-get3/3 원본을 재사용한다. 기존 원문에 없는 “최종 보호 전환 이후만 인정” 조건을 추가하지 않는다. 이후 관련 변경의 회귀는 별도로 판단한다. |
| **15 NOT_VERIFIED** — mgmt-gw Forward/Zone/Policy/NAT·내부 SNAT 없음 | route PASS 및 승인 경로 설계 | **대조·인수 + 실측 잔여:** mgmt-gw 실제 forwarding/zone/policy/NAT를 승인안에 대응하고 IF-06B 양방향 source 보존을 확인한다. Worker route-get이나 scrape의 Pod→node SNAT 관찰만으로 이 조건을 판정하지 않는다. |
| **16 NOT_VERIFIED** — monitor01 .30:443 Receiver/Protocol/TLS/Auth | 기존 PKI/구성 후보 및 MON05:59 수신 기록 | **입력 수집 → 실측:** [MON PR9 콘솔 절차](https://github.com/321Team/infra-monitoring/blob/efcbed006d9e777a23ae145bfb425c33a4c742b5/ops/mon-followup/MONITOR01_CONSOLE.md)의 기존16고정 조회를 연결한다. 현재 실제 monitor01 실행은 NOT RUN. 조회 후 MON Lead가 receiver/TLS/Auth 입력을 확정하고 통합 검증한다. |
| **17 NOT_VERIFIED** — 실제 Source·양방향 Return | sender Pod 신원 및 경로 준비 자료 | **실측 잔여:** IF-06B가 준비된 뒤 실제 monitor01 수신 패킷 Source와 양방향 Return Path를 관측한다. 02:05의 worker03→worker01 scrape는 다른 목적지/경로이므로 대체 증거가 아니다. |
| **18 NOT_VERIFIED** — Reboot 지속성·재시험 | 기존 route/보호 관련 자료 | **실측 잔여:** 최종 보호·경로 구성과 변경 범위를 확정한 뒤 승인된 작업 창에서 재부팅 지속성과 필요한 회귀를 기록한다. 과거 백업 준비 중 재기동이나 현재 Running으로 대체하지 않는다. 이 문서는 재부팅 실행 승인이 아니다. |
| **19 PARTIAL** — Rollback 재현성 | [CP1 실제 Runtime rollback·baseline 복구](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5662361174) | **기존 증거 재사용 + 잔여 복구 검증:** 최신 전체 ICR 변경에 대응하는 복구 범위·원본·재현성을 연결한다. Join 성공을 rollback 실행으로 세지 않는다. PR27 canary 제거는 그 자원 복구이며 전체 ICR rollback을 대신하지 않는다. AC에 없는90분 제한을 추가하지 않는다. |
| **20 PARTIAL** — Evidence 평문 비밀정보 없음 | 제출본별 SHA/마스킹/검사 이력, 이번5원본+5sidecar 바이트 검증 | **원본 연결 + 최종 검토:** Gate2 미수신 원문 및 최종 증적을 기존 전용 경로로 연결하여 검사·누락 판정을 완료한다. 해시 일치만으로 비밀정보 없음/독립 승인을 인정하지 않는다. 별도 SEC 노출 대응은 기존 담당 기록으로 추적한다. |

## 진행 순서와 작업 경계

1. **지금 인계:** [기존 PR23 인계 문서](ICR_PR23_REVIEW_HANDOFF_20260924.md)의 5개 원본·sidecar 전달본을 기존 승인 팀 전용 위치에 놓고, PR23에 접근 URI와 검토자의 실제 다운로드/해시 확인을 연결한다. 원본 연결 부족은 서버 실패가 아니다. 과거 CP route·Gate2·지정 Worker pull 로그는 보관 담당자의 당시 파일을 먼저 연결한다.
2. **독립 검토:** PR23은 최신 HEAD 전체의 편입 리뷰가 남는다. 운영 PR27은 `ffbfff8ebcd1ed53ebff7f3e70fb734e93221a0c` 기준 Ready/미병합/리뷰0건을 확인했다. 실제 실행은 정확한 리뷰 SHA, 기존 K8S/SEC Lead 기록의 실행자·창·rollback·음성 시험 수용을 확인한 뒤 진행한다. 원본 전달본 작성은 이 조건을 해제하지 않는다.
3. **제한 진단:** PR27의 실행 직전 신원/정책 재확인과 명시적 NotFound, create-only, 서로 다른 두 post-create scrape, 정상 양성 대조군을 둔 음성, 관리 회귀, UID/RV를 확인한 회수·최종 NotFound를 하나의 진단 기록으로 남긴다. 이 절차는 제안 상태이며 이번 작업에서 실행하지 않았다. .108 노드 IP는 Prometheus 전용 identity가 아니다.
4. **별도 MON/IF-06B 연결:** MON PR9 HEAD `efcbed006d9e777a23ae145bfb425c33a4c742b5`의 콘솔 절차와 기존05:59 K8s 수신 기록을 사용한다. 새 collector·새 계정·동일 K8s 재수집을 만들지 않는다. TLS PR31·MON 설정/이미지·알림·LB 장애/복구 작업은 각 기존 PR/티켓에서 진행한다.
5. **잔여 조건 종결:** 원본 대조 후 실제 빠진 AC04/07/11/12/15/16/17 범위를 기존 담당 기록에 확정하고, 최종 구성에 대한 AC18/19 및 AC20 증적 검토로 연결한다. PASS3건을 불필요하게 다시 시작하거나 본 표만으로 나머지 AC를 완료 처리하지 않는다.

## 검증 수준

- 이번 수행: GitHub 최신 PR/정책/기존 AC·보고 대조, 기존5개 archive 및5개 sidecar의 바이트 검증, 전달용 ZIP과 목록 작성, 문서 편입.
- 이번 미수행: 서버 명령·active probe·정책/서비스 변경·도구 설치·권한 변경·독립 사람 리뷰·병합·새 Runtime 인수.
- [EVIDENCE_POLICY](../governance/EVIDENCE_POLICY.md) 및 [중앙 리뷰 정책](https://github.com/321Team/fds-project-baseline/blob/main/governance/REVIEW_AUTHORITY_POLICY.md)을 따른다. 이번 자체 대조는 독립 리뷰가 아니다. 새 승인 양식이나 공통 Ready 규칙을 만들지 않는다.

AI assistance: CODEX_ASSISTED.
