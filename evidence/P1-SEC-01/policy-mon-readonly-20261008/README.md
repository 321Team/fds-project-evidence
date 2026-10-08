# SEC 정책·MON 구성 순차 수집 — 2026-10-08 KST

책임: baseline #19 / P1-SEC-01. 연계 #17 / P1-MON-01.
실행·작성: GWONUK / CODEX_ASSISTED. 사용자 “순차적으로 수집하자” 지시에 따른 읽기 전용 수집.
요구 기준: docs-v3.1.21 `979facb98de8ca1f1e2ce22f38b27ac3366f3fc3`, IF-03/IF-13A/IF-05C.
기존 판단: #19 comment6040616297. Backup#152·IF06B#151 재실행 없음.

## 수집 출처·방법

- PC → fds-ansible01/server01_ansible → control01(10.1.93.102)/svc_ansible → 기존 sudo/root.
- policy: 02:14:14 KST, API get 9/9 rc0. K8s NetworkPolicy23, Calico GNP7,
  Calico namespaced policy0, HEP6, Node6, Namespace9, Pod44, Service12, EndpointSlice12.
- MON inventory: ConfigMap get rc0; PrometheusRule/ServiceMonitor/PodMonitor 3조회 rc1.
  오류는 해당 리소스 유형 미설치다. 전체 PASS로 숨기지 않고 `mon.json`, `mon.rc=2`에 보존했다.
- MON config: 02:15:39 KST, ConfigMap5개 및 Pod mount 조회 6/6 rc0.
- MON loaded API: 02:18:39 KST, 실제 Prometheus config/rules/query 4/4 성공.
  control01 loopback 임시 자동 포트의 기존 kubectl port-forward 사용, 자신이 생성한 PID만
  종료·wait로 회수(`forward_reaped=true`). HTTP GET만 수행했다.
- Edge/Worker 접근·도구 사전 확인: 02:20~02:21 KST (정확한 시각은 JSON).
  Worker3 sudo/root 및 tcpdump/nsenter/crictl/python3 있음.
  edge01 일반 svc_ansible SSH/python3/curl 있음. edge01 sudo -n은 암호 필요로 rc1,
  원본 보존. 권한 변경이나 비밀번호 우회 없음.

서버 설정·Pod·서비스·정책·패키지 변경, 재시작/reload, 장애 유발, 통신 허용/차단 시험 없음.
코드는 stdin으로 1회 실행한 순수 조회기이며 서버에 설치하지 않았다.
REVIEW=NOT PERFORMED (Pre-check / 중앙 정책 §3.2 4-1), 증적 독립 리뷰는 별도.
소스 Git 배포 SHA 대신 실행 입력 bytes SHA256을 각 서버 JSON에 결속한다:

| 실행 입력 | SHA256 |
|---|---|
| collect.py (policy/mon) | 63d35599adfcc392626175908cbea0b2eb9d50e259ad98cc50fb2a947b626be8 |
| collect-mon.py | 0626340e612c370d66b99985df10861f9f25ff74c70c689f3a85634ea3d1f1e4 |
| collect-mon-live.py | 76df5716b16da62036b821aae6c9c14fa8e4c5ebf8ee25b96dc93004033d6123 |

JSON은 **선별 필드 투영 결과**이며 kubectl 전체 원문 사본이 아니다.
명령·시각·rc·stderr와 전체 응답의 SHA256을 서버에서 계산해 함께 남겼다.
Policy spec/label/UID/resourceVersion은 보존하며 annotations/managedFields, Pod env,
Secret 값, webhook URL/인증정보는 내보내지 않았다. MON은 allowlist 필드만 보존한다.
수신 SHA와 서버 JSON의 실행 소스 SHA를 별도로 검증했다. 원문 전체를 저장하지 않았으므로
raw_stdout_sha256을 로컬 원문과 다시 대조했다고 주장하지 않는다.
반복 재수집은 불필요하다. 후속 실행은 이 수집 결과를 운영 입력으로 사용하지 않는다.
재수집이 필요하면 기존 계정/권한·호스트와 읽기 전용 명령을 확인하고 새 회차에 보존하며,
조회 실패/시간초과는 미확인으로 종료하고 설정을 변경해 통과시키지 않는다.

## IF-03 / IF-13A 결과

**현재 설정·대상 매칭 공백 해소 / 실제 차단 Runtime 판정은 유지.**

- fds-app transaction-api3·fds-engine3의 실제 app label과 정책 selector가 맞고 hostNetwork=false.
- fds-app default-deny-all은 ingress/egress 모두 적용 대상.
- fds-engine:8001 ingress 허용은 동일 namespace의 app=transaction-api다.
  Prometheus 허용은 monitoring-api namespace + app=prometheus, TCP9090 별도 규칙이다.
  현재 수집한 정책에서 monitoring Pod→engine:8001 허용 규칙은 발견하지 않았다.
  기존 monitoring source TIMEOUT은 source egress와 destination ingress를 분리 입증하지 못한다.
- transaction-api egress는 engine8001, DB10.1.93.55:5432, CoreDNS UDP/TCP53을 허용한다.
  engine egress는 CoreDNS UDP/TCP53만 허용한다. CoreDNS selector는 kube-system + k8s-app=kube-dns.
- monitoring-api에도 CoreDNS 한정 DNS 정책과 기본 차단이 있다.
  monitoring-node의 node-exporter3는 hostNetwork=true이며, 이들의 적용·차단 여부를
  일반 Pod NetworkPolicy 존재만으로 인정하지 않는다. 수집된 HEP/GNP와 별도 대조 대상으로 유지한다.
- 외부 UDP53, transaction-api 일반 egress, 비승인 source→8001의 실제 차단은 이번에 시험하지 않았다.
  현재 설정과 과거 시험시점 설정의 동일성·과거 패킷 차단 귀속을 소급 증명하지 않는다.

## IF-05C / MON 대조

1. **기존 “전용 시험 규칙 원본 부재”를 정정한다.**
   `received-20260926T0445Z/run1-20260926T0419Z/p0-test-alert-cm.yaml`에 원본이 있다.
   해당 data `p0-test-alert.yml`은 현재 ConfigMap과 SHA256
   `c97c60256c4caa64cd9699539eccbb5d60f18907b1c8190cea280e0d7e8fb22c` 일치.
   현재 실제 rules API에도 FDSMonitoringPipelineTest, `vector(1)==0`, inactive/health=ok가 있다.
   **규칙 원본·로드 확인이며 그 전용 규칙의 과거 Firing→Resolved 실행 증거는 아니다.**
   run4는 KSM 장애로 TargetDown을 관측한 기존 시험이다.
2. 현재 alert-rules data는 9/30 `control01/sync/alert-rules.yaml`과 bytes SHA 동일.
   9/27 사본과 bytes는 다르지만 핵심 alert/expr/for는 동일하다(전체 동등성으로 확대하지 않음).
   현재 TargetDown은 transaction-api|fds-engine|kube-state-metrics의 up==0, for1m이며 실제 로드됨.
3. 현재 prometheus.yml은 10/1 `p1-mon-prom315-apply-20261001T114946/prometheus.yaml`의 data와 bytes SHA 동일.
   실제 loaded config는 APP DNS SD(9091/9090), KSM8080, Alertmanager9093을 참조한다.
   9/27의 prometheus.yml과는 SHA가 달라 **9/26 시험 전체와 현재 구성의 동등성을 일괄 승인하지 않는다.**
4. 10/2 `alertmanager-config.masked.yml`과 현재 ConfigMap의 수신·route·proxy·send_resolved
   선별 필드가 동일하다. 인증정보/미수집 필드·Alertmanager 실제 로드 상태·외부 Discord 도달은 미입증.
5. 현재 monitoring-api의 Prometheus→Alertmanager TCP9093 egress/ingress 허용과 default-deny 원본 확보.
   9/30 networkpolicy.yaml의 6개 객체는 현재 spec과 동일하다. 이 6개 대조를 9093 정책의
   9/26 당시 형상 증명으로 확대하지 않는다.
6. 실제 Prometheus 시점 조회: up 시계열23개(6+6+1+3+1+3+3), up==0 결과는 성공·빈 배열.
   조회 실패를 0으로 바꾸지 않았다. 장애주입/알림 전송/회복 시험은 실행하지 않았다.

비차단 후속: 로드된 optional `UnexpectedPodInFdsNs` 규칙이 namespace="fds"를 참조한다.
현행 앱 namespace=fds-app과 달라 감시 대상 대조가 필요하다. 이번 수집에서 수정하지 않았으며
IF-05C 필수 시험을 이 optional 규칙 문제로 새로 차단하지 않는다.

## Edge C0/P4 준비와 남은 조건

- infra-kubernetes#70: HEAD258c1dbec77d1fcb7a8c078047e2db90b451213f, merge
  95af5b09e50f31f28101fb6f9840aef42c227a3f, 10/8 01:41:39 KST 병합 확인.
- README의 창은 **10/10 오전 제안**이며 별도 GO 전이다. 실행 이재환, P4 지원 이권욱 유지.
- 현재 참고 상태: 6/6 Ready, Worker별 Ready non-terminating endpoint1/1/1,
  NodePort80→8000:30080/ETP Local, NodePort32085 Service0, .50/32 허용 GNP 있음.
  이 관측은 실제 전환 직전 C0나 edge01 표식 TRACE_READY를 대신하지 않는다.
- P4 고정 collector: infra-ansible c0d784fa9a1d9dfc57f504ed969c036d0860acef /
  playbooks/p1-sec-01-b2-collect-58.yml, SHA25642fc3ed486b9b16f6be156b2770ada6cf9fa725c9b0a5882473afa0bd7eb9024.
  evidence#86의 기존 성공 회차를 참조했다. Worker 캡처는 become, edge curl은 일반 계정이다.
  이번 접근 확인에서 edge sudo 불가가 P4 전체 접근 불가를 뜻하지 않는다.
- **현재 P4 packet capture/curl 및 Edge check/apply/trace는 NOT_RUN.** 실제 창의 RUN·최신 Pod와
  형상·소스 무결성·비중첩·C0·중단조건을 확인하고 P4 한 회차를 별도 보존한다.
  재시작/reload/upstream 변경·시험 거래 생성·DB 변경은 이번 수집 지시에 포함하지 않았다.

## 편입·후속 판정

이 폴더 SHA256SUMS는 파일 무결성 검증이다. `historical-comparison.json`, `analysis.json`은
로컬 파생 분석이며 서버 원문과 구분한다. 참조 증적 기준은 evidence main
`b1328ea3efd5cfb1ce966fd0285d99bd7a4d28eb` (기존 사본 조회 시작은 d034e60).
과거 파일은 변경하지 않았다. 독립 편입 리뷰·AC 인수·#19/Phase1 Close·새 Runtime GO는 별도다.
