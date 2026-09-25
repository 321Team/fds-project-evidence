# Grafana 정책 입력 수신·분석 — 2026-09-24 05:54 KST

판정: **실제 순수 조회11/11 성공 / 수집된 Grafana 선택 Kubernetes 정책에 TCP9100 허용 없음 / 실제 음성 시험 미실행**.

## 원본과 실행 검증

- 원본 `ICR_Grafana_Policy_oBrOMu.tar.gz`: 7,481 bytes, SHA256 `23b3c72d285395c7ad09ad309607d781d542aed892bdc62bc892a75a664547d5`.
- 외부 sidecar 일치, 내부 manifest7/7, 고정 Git 소스3/3 및 실행 collector hash 일치. 원문8파일을 바이트 그대로 보존했다.
- source `bded227a045847059dda657afbd9503ecc5db159`, [순수 Pre-check PR34](https://github.com/321Team/infra-kubernetes/pull/34), merge `479bb55f53dadc7b8625cd037332483a0ed4e470`.
- controller 시작05:54:28.714882 KST, control01 실제 명령05:54:29–30. 계정svc_ansible, become:false, 기존 admin.conf의 LB API `https://10.1.93.109:6443`.
- 실제 Ansible syntax-check 성공, controller/envelope rc0, 모든11명령 rc0/status COLLECTED/stderr bytes0. API 주소 로컬 조회1회와 API GET10회다.
- recap ok4/changed1/unreachable0/failed0. changed1은 ansible01 증적 파일 저장이며 운영 설정 변경이 아니다.
- 결과는 `COLLECTED_PENDING_POLICY_REVIEW`. 수집기 자체의 policy_verdict는 NOT_ASSESSED이고 아래 내용은 수신 후 작성한 정적 분석이다.

이번 확인은 사용자가 실제 실행해 제출한 원본 분석이다. 작성자가 VM에 접속해 실행한 것이 아니다. Source는 REVIEW=NOT PERFORMED (Pre-check)이며 이 예외를 운영 PR27 또는 증적 PR23의 독립 리뷰에 적용하지 않는다.

## 고정 신원

| 항목 | 관측값 |
|---|---|
| Namespace/Pod | monitoring-api/grafana-7dc57885d4-sk8h2 |
| UID / resourceVersion | 00396c87-640c-4704-ac6c-dcbacf6fbc90 / 1429982 |
| Node / hostIP / PodIP | k8s-worker03 / 10.1.93.108 / 10.244.39.217 |
| SA / container | default / grafana |
| Pod labels | app=grafana, pod-template-hash=7dc57885d4 |
| imageID | 10.1.93.54/fds/grafana@sha256:7a1ff54408c90357ff1c76189e5bbc24f898531cb771fbbfe6a477f00de37d5b |

수집 전후 투영 필드와 resourceVersion이 동일하다. Running/Ready, hostNetwork/hostPID/hostIPC=false, 수집기 검사 범위에서 privileged container 없음. Namespace/SA labels도 원문과 POLICY_SUMMARY에 보존했다. default SA의 labels는 비어 있으며 SA 이름만으로 Alertmanager와 구분하지 않는다.

## 현재 Kubernetes 정책 분석

monitoring-api NetworkPolicy17개를 모두 대조했다. 모든 최상위 podSelector가 빈 selector 또는 matchLabels 형태이며, 실제 Grafana labels로 선택되는 Egress 정책은 아래5개다. 다른12개 정책은 최상위 selector가 다른 app을 지정한다. 이름이 Grafana를 포함하는 `allow-grafana-ingress-from-prometheus-ns`도 최상위 app=prometheus이므로 Grafana의 egress 허용으로 계산하지 않았다.

| 선택 정책 | 관측된 Egress 허용 |
|---|---|
| default-deny-all | 허용 규칙 없음, Egress 격리 대상 |
| grafana-allow | 같은 monitoring-api의 app=prometheus에 TCP9090 |
| allow-grafana-to-prometheus | 같은 monitoring-api의 app=prometheus에 TCP9090 |
| allow-monitoring-egress-dns | kube-system Namespace의 Pod에 TCP/UDP53; Pod label 제한은 없음 |
| monitoring-api-dns-allow | kube-system의 k8s-app=kube-dns Pod에 TCP/UDP53 |

Kubernetes NetworkPolicy는 선택되는 Egress 허용들의 합집합을 적용하므로 default-deny만 보고 결론 내리지 않았다. 위5개 전체를 합해도 허용 port는 TCP9090, TCP53, UDP53이며, **10.1.93.105:9100/TCP를 허용하는 규칙은 없다**. 이는 수집된 Kubernetes 정책 설정 범위의 판단이다. 이 자료로 실제 dataplane 차단을 PASS 처리하지 않는다.

공식 의미 참고: https://kubernetes.io/docs/concepts/services-networking/network-policies/ . 공식 문서의 현재 버전은 현장 설치 버전·구현 동작의 증거가 아니다.

## Calico 입력과 관측 한계

- monitoring-api Calico NetworkPolicy0, namespaced NetworkSet0, GlobalNetworkSet0.
- GlobalNetworkPolicy7개: v4 host GNP6개(default tier/order100)와 nodeport-30080-allow(default/order50, preDNAT=true, applyOnForward=true, Ingress만).
- host GNP는 fds.example/bootstrap과 fds.example/node를, NodePort GNP는 fds.example/role=worker를 선택한다. 관측한 Grafana Pod labels에는 이 값이 없어 직접 일치하지 않는다. NodePort 규칙 대상도 TCP30080이다. 이는 host endpoint 경유 영향 전체가 없다는 뜻이 아니다.
- Tier3개: kube-admin order1000/defaultAction Pass, default order1000000/Deny, kube-baseline order10000000/Pass. 조회된 GNP는 전부 default에 속한다. native admin-policy API와 Calico endpoint/profile 세부는 이 회차에서 수집하지 않았다. Tier 이름·빈 namespaced list만으로 미수집 경로까지 허용/차단을 단정하지 않는다.
- worker01 host GNP의 ingress는22/10250/UDP4789 허용 후 terminal Deny이며 TCP9100 허용은 없다. 기존02:40의 named DROP 증거는 별도 관측 창으로 보존한다.
- 완전한 GNP7개 목록에 `icr-mon-worker03-to-worker01-9100-canary`는 없다. 이 목록 관측은 실행 창 직전의 명시적 NotFound 확인을 대신하지 않는다.
- 과거01:21와 대조한 K8s NP17개/GNP7개/Tier3개는 이름 집합 및 각 UID/resourceVersion/spec이 모두 동일하다. 중간 기간 내내 변경이 없었다는 실시간 관측이나 과거 packet 수집의 재실행을 뜻하지 않는다.

Tier 평가 의미 참고: https://docs.tigera.io/calico/latest/reference/resources/tier . 각 request의 시각/resourceVersion은 원문에 있으며, 순차 조회를 원자적 snapshot이라고 주장하지 않는다. 실제 Pod 시작/끝 일치 역시 중간 정책 변화를 증명하지 않는다.

## 다음 단계와 판정 경계

1. Grafana 신원과 현재 수집 범위의 정책 입력은 확보됐다. 동일 후보 목록·동일 정책 수집을 다시 요청하지 않는다. 실행 창 직전 필요한 신원·정책 갱신은 승인된 운영 절차에 한정한다.
2. [PR27 고정 실행계획](https://github.com/321Team/infra-kubernetes/blob/ffbfff8ebcd1ed53ebff7f3e70fb734e93221a0c/docs/change/ICR-D-NET-01-01/MON_SCRAPE_CANARY_20260924.md)의 독립 리뷰와 기존 K8S/SEC Lead 실행 수용이 남는다. 신원·정책의 필요한 추가 의존성이 검토 중 식별되면 그 범위만 보완한다.
3. 기존 컨테이너의 shell/curl 존재·옵션 지원은 아직 미확인이다. 계획에 있는 도구 확인 exec 및 정확한 bounded probe를 검토 후 수행한다. 새 Pod/도구 설치·label 변경·권한 확대는 하지 않는다.
4. 전후 음성 시험은 정상 positive endpoint, 실제 차단 enforcement point에 귀속되는 결과와 짝지어 판정한다. generic timeout/refusal/exec 실패/도구 부재만으로 PASS를 부여하지 않는다. Positive/Negative/Regression/Recovery 전 단계와 종료 시 canary 회수 조건을 유지한다.

원 API 전체 body는 저장되지 않았고 투영 데이터와 hash만 있다. 따라서 원 응답 전체 hash의 재생산·재검증을 주장하지 않는다. 이번 원본은 사용자 첨부 바이트를 보존하며 재압축·Git binary·Release 업로드 없음. 첨부 file ID는 팀 접근 URI가 아니며5개 archive와 sidecar의 검토자 실제 다운로드 인계는 미확인이다.

STATIC/LOCAL18/소스 병합은 이전 준비 단계다. 이번에 추가 확인한 단계는 실제 Ansible syntax-check와 순수 조회11/11 성공이다. CI·독립 증적 리뷰·운영 리뷰·실제 probe·운영 적용·AC 인수는 별도로 판정한다. 증적 PR23은 독립 편입 리뷰 대기이며 기존 AC 집계와 담당·일정·티켓 상태는 유지한다.

책임: ICR #14 / SEC #19 / K8S #10 / MON #17. AI assistance: CODEX_ASSISTED.
