# 최종 시험 준비 입력 — 2026-10-13 05:01 KST

이권욱 / CODEX_ASSISTED. ansible01의 기존 strict SSH→svc_ansible→control01 sudo 경로로11건의 Kubernetes GET을 수행했다. 조회 모두 rc0, Node6 Ready,44 Pod, GNP7·HEP6·FelixConfiguration7·Deployment8·StatefulSet0·PDB1·PV/PVC3을 확인했다. Secret·환경변수 값은 읽기 산출물에 포함하지 않았다. 배치·Token·정책·Pod/Node 변경은 없다.

이 수집기는 새 순수 읽기 준비 도구이며 독립 소스 리뷰 없이 실행한 범위다(`REVIEW=NOT_PERFORMED (Pre-check)`). collector의 명령·코드 SHA·계정/시각·rc와 투영된 출력 원본은 `final-test-inputs-control01/`에 있다. API 응답 전체를 그대로 저장하지 않고 비민감 필드만 투영했으며 API 원 응답 SHA를 함께 기록했다. 원문을 모두 수신했다고 주장하지 않는다.

## 재시험 범위를 좁힌 사실

1. **Worker GNP3개:** 9/27 reboot 회차의 저장 YAML과 현재 spec의 차이는 세 노드 모두 `/tier`: 과거 미기재→현재 `default` 한 항목뿐이었다. ingress/egress/selector/order 등 그 밖의 spec은 같다. [Calico 문서](https://docs.tigera.io/calico/latest/network-policy/policy-tiers/tiered-policy)는 tier를 생략한 정책을 default tier에 둔다고 설명한다. 관측 차이는 그 동작과 정합하지만 이번 대조만으로 HEP/Felix/다른 정책까지의 전체 집행 동일성·AC18 완료를 판정하지 않는다.
2. **노드별 영향:** Worker01/02에는 PVC 참조 Pod가 없고 앱 두 종류가 각1개씩 있다. Worker03에는 같은 앱2개와 Prometheus·Grafana·Alertmanager의 PVC Pod3개가 있다. PV3개는 모두 worker03 nodeAffinity와 local storage이며 Retain이다. 따라서 필요한 단일 Worker 시험 후보는 Worker01/02로 좁히고 Worker03은 모니터링 관측/복구 영향 때문에 우선 대상에서 제외하는 안이 합리적이다. 후보 선정은 아직 실행 허용이 아니다.
3. **control01:** calico-kube-controllers1개·CoreDNS2개가 계속 같은 노드에 있다. OID02 반입 완료로 control01 drain/reboot 금지의 기존 결정을 자동 해제하지 않는다.
4. **앱 형상:** engine/API 모두 replicas3·Ready3·updated3, Worker별1/1/1 배치다. 별도 앱 affinity·nodeSelector와 PVC가 없고 PDB는 Calico 한 개뿐이다. 그 사실만으로 재배치/재부팅 중 가용성을 보장하지 않으며 기존 HA 승인 기준으로 필요한 영향만 확인한다. 새 PDB/배치 정책 개발을 자동 추가하지 않는다.
5. **HTTP Probe 입력:** engine `/readyz`·`/livez`8001, API 동일 경로8000, readiness period10s/failure3, liveness20s/failure3, timeout1s이며 startupProbe는 없다. 이는 설정 읽기이며 실제 실패 전이/회복 시험은 아니다. 없는 startupProbe를 새 필수 AC로 만들지 않는다.

## 권장 실행 순서에 주는 영향

- 기존 9/27 CP/Worker reboot 원본과 수용 이력을 재사용하고 **정책이 모두 바뀌었다는 가정으로 6대를 재부팅하지 않는다**. 현재 관측과 기존 최종 정책 세트/route·HEP·Felix·AC18 차이를 먼저 확정한다. 재부팅 후 정상과 부팅 직후 연속 보호는 별도이며 기존 SEC 잔여 리스크 수용을 유지한다.
- 새로운 앱 이미지가 배포될 예정이므로 HA·최종 E2E/Probe는 최종 digest·배치가 고정된 뒤 필요한 변경 영향만 묶는 편이 중복 시험을 줄인다. Push 대기 중은 준비 입력 수집까지만 진행한다.
- 단일 노드 reboot와 HA drain은 서로 다른 조치다. 하나를 했다고 다른 AC를 자동 완료하지 않는다. 같은 회차로 소비할 수 있는 증거와 별도 필요한 동작/관측을 구분한다.
- OID03은 소비 회차별 공급 경로/복구 범위의 결정 잔여다. 현재 설치 RPM의 재다운로드·새 bootstrap 체계 구축을 모든 회차의 공통 선행조건으로 만들지 않는다. 새 설치/이미지 재생성이 실제 필요한 범위에서 정확 버전·공급원을 연결한다.

## 한계·다음 확인

`FINAL_TEST_INPUTS_ANALYSIS.json`은 실제 투영 출력과 9/27 Worker 정책3개의 비교다. 새 packet·HTTP 요청·fault injection·reboot·drain·CRI 이미지 사용은 수행하지 않았다. NodeReady·PodReady와 현재 설정만으로 업무 E2E·AC/최종 인수 PASS를 선언하지 않는다. 실제 시험 전에 대상 호스트/콘솔·fresh 상태·해당 작업창과 실패 시 복구점/회수 예산을 확정한다. 중첩/드리프트/복구점 부재이면 해당 변경 회차만 보류하고 독립 준비는 계속한다.
