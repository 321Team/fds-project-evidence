# Phase 1 앱 분산 복구 — 실행 범위 r1

이권욱 / CODEX_ASSISTED · 2026-10-13 KST. 준비 완료와 실제 변경을 구분한다. 실제 Eviction은 아직 0회다.

## 목적과 선택

현재 worker02에 모인 fds-engine 3개와 transaction-api 3개를 기존 Worker 3대에 앱별 1개씩 배치한다. 기존 Deployment·ReplicaSet·이미지·분산 정책은 유지하고, worker02의 기존 Pod만 **한 번에 1개, 앱당 최대 2개, 합계 최대 4개** 정상 종료(Eviction)한다. engine 완료 뒤 API를 진행한다. 다음 Pod는 앞선 대체 Pod가 Ready가 되고 관측이 회복된 뒤에만 선택한다.

기존 분산 규칙은 신규 Pod의 배치에 사용된다. 0/3/0에서 두 번의 정상 재생성으로 1/1/1이 되는 것은 예상 결과이며 현장 검증 전 성공으로 간주하지 않는다. 전체 rollout restart는 모든 Pod를 교체하고 템플릿 변경도 남기므로 이번 최소 범위에서 제외한다. 1개 종료 중에는 해당 앱의 Ready가 2개로 줄 수 있고 진행 중 요청에 영향이 있을 수 있다. `/readyz` 정상은 업무 요청 무손실의 증명이 아니다.

## 이미 확보한 근거

- `control01-binding/`: 00:34 KST, API GET 8종. 앱별 Ready3, 같은 기존 ReplicaSet, HPA/PDB0, Worker3 Ready/uncordoned/taint 없음. 정확한 UID·spec/template SHA와 Pod UID는 `APP_BINDING.json`에 고정한다.
- `k8s-worker01-cache/`, `k8s-worker03-cache/`: 00:32, 해당 이미지 2개씩 content complete/unpacked true, kubelet/containerd active, SELinux enforcing. 이는 관측 시점의 로컬 cache 준비이며 향후 pull·인증이 절대로 발생하지 않는다는 보장은 아니다.
- `edge-current-unprivileged/`: 00:33, Edge `/readyz`와 worker02 NodePort200; worker01/03 NodePort 연결 거부. root 시도는 sudo 암호 요구로 실행 전 실패했고 별도 영수증에 보존했다.
- `control01-mon-target-labels/`: 00:35, up 23개 모두1, 앱 각3개. 실제 app job 라벨은 `fds-engine`·`transaction-api`이며 namespace 라벨은 없다. 앞선 namespace 조회의 빈 벡터를 앱 장애 또는 PASS로 쓰지 않는다. 임시 loopback port-forward는 종료했다.

## 실행 직전에만 확인할 사항

1. Harbor 변경·사후 관측 및 다른 앱/노드 변경과 겹치지 않는 실제 회차. 타세션이 대기 중이라는 과거 조회만으로 확보했다고 하지 않는다.
2. 이권욱의 control01 콘솔 로그인·sudo·기존 관리자 인증 사용 가능 및 회차 동안 인수 대기. 과거 MON 1회 콘솔 확인을 이번 시각의 가용성으로 대신하지 않는다.
3. 이 범위의 앱 Pod 정상 종료·재생성 허용. 앞선 권장안의 읽기·구체화 단계 및 MON 1회 허용을 이 변경으로 확대하지 않는다. 새 Lead 설계 승인이나 기존 코드의 재리뷰를 요구하는 것은 아니다.

## 한 단계의 명령과 순서

실행 위치는 control01, 기존 svc_ansible → sudo, 기존 `/etc/kubernetes/admin.conf` 인증이다. 비밀번호·키·token을 새로 발급하거나 복사하지 않는다. 실행자는 각 단계의 명령·시각·rc·응답과 관측을 새 로컬 receipt에 기록한다.

1. 저장된 수집기와 같은 읽기 방식으로 cluster UID, Deployment UID/spec SHA, RS 소유 관계, Pod6개/Ready, 노드, PDB/HPA, EndpointSlice를 새로 확인한다. 시작 직전 두 앱 각3 Ready, 종료 중 Pod0, 예상 외 Pod/RS 변경0이어야 한다. 각 노드의 Ready/pressure/cordon/taint와 분산 라벨도 확인한다. 형상 변경·수집 실패·새 PDB/HPA가 보이면 중단한다.
2. worker02에 2개 이상 남은 **해당 기존 RS의 기존 Pod** 1개만 고른다. 새 GET에서 이름·UID·resourceVersion·Ready·grace30을 확인한다. 저장된 과거 resourceVersion을 재사용하지 않는다. UID가 기존 허용 집합에 없으면 선택하지 않는다.
3. 아래 JSON의 값은 그 GET 결과로 채운다. 예시/placeholder를 그대로 실행하지 않는다. 요청은 1회이며 자동 재시도하지 않는다.

```json
{"apiVersion":"policy/v1","kind":"Eviction","metadata":{"name":"<fresh pod name>","namespace":"fds-app"},"deleteOptions":{"preconditions":{"uid":"<fresh uid>","resourceVersion":"<fresh resourceVersion>"},"gracePeriodSeconds":30}}
```

```bash
# 위에서 검증한 JSON을 stdin으로 1회 전달한다. 같은 명령을 반복 붙여 넣지 않는다.
sudo /usr/bin/kubectl --kubeconfig=/etc/kubernetes/admin.conf --request-timeout=10s \
  create --raw '/api/v1/namespaces/fds-app/pods/<fresh pod name>/eviction' -f -
```

4. 요청 전부터 Edge의 기존 `/readyz` GET을 관측한다. 요청 후 120초 한도로 Pod/EndpointSlice/Ready를 읽는다. 이 수치는 제안한 **다음 변경 중단 한도**이며 서버의 reconciliation을 강제 종료하는 값이 아니다. 남은 기존 Pod 최소2개가 Ready이고 새 Pod가 빈 Worker에 배치돼 Ready가 되어야 한다. 종료 Pod도 사라지고 앱별 총3 Ready 및 서비스의 Ready endpoint3이 확인돼야 다음 관측으로 간다.
5. MON은 최대90초까지 기존 수집 주기를 기다린다. app job별 현재 Pod에 해당하는3개 target up=1, 오래된 target 소멸, 기타17개 target 정상 및 Edge200 회복을 확인한다. Pod IP/metrics port와 현재 EndpointSlice를 대조하며 단순 target 총수만 판정하지 않는다. 새 Ready 이후 최소30초 안정 관측 뒤 다음 Pod를 고른다. HTTP/Ready 악화가 발생하면 기한까지 기다려 다음 변경을 밀어붙이지 않고 중단한다.
6. engine 1/1/1 완료 후 API에 같은 순서를 적용한다. 최종 두 앱 1/1/1, Ready6/6, service endpoint, Edge→세 Worker NodePort200, app up6/6와 기존17개, Deployment spec SHA·UID/RS 동일성을 보존한다. 후관측60초. 실제 HTTP/Rule/DB Final E2E와 HA Drain 판정은 별도다.

## 중단과 복구

- API 409/429/5xx·timeout·SSH 단절은 재전송하지 않는다. 정확한 Pod UID/삭제 시각 및 RS/대체 Pod를 읽어 요청 반영 여부를 먼저 구분한다. 불확실한 동안 다음 Pod 종료0회.
- Ready2 미만·노드/Endpoint 이상·Pending/ImagePull/CrashLoop·Edge 실패·MON 복구 한도 초과·다른 작성자 발견이면 다음 변경을 중단한다. 남아 있는 정상 Pod를 보존하고 콘솔에서 기존 관리 인증으로 상태를 인수한다.
- 정상 종료가 승인된 Pod UID는 되살릴 수 없다. 기존 RS가 같은 이미지·템플릿으로 재생성하도록 둔다. 실행 도구 종료나 SSH 단절이 이미 접수된 요청을 되돌리지는 않는다.
- 강제 삭제, 전체 Drain, 정책/SELinux/TLS 완화, 이미지 변경·추가 pull, replica 조정, 임의 rollout undo는 자동 복구에 포함하지 않는다. 재생성 실패의 원인을 확인한 뒤 필요한 최소 별도 조치를 제시한다.
- 성공한 부분 배치는 유지하고 실제 변경한 Pod UID와 미완료 수를 인계한다. 기존 worker02 집중으로 일부러 되돌리거나 실패를 성공으로 표기하지 않는다.

## 검증 구분과 근거

현재 RUNTIME은 읽기 수집만 완료. 실제 앱 변경·새 HA 시험·AC/Exit 판정은 미실행이다. 이 카드는 새 오케스트레이터·서비스를 만들지 않으며 Kubernetes 기본 Eviction API를 사용한다.

[공식 Eviction 설명](https://kubernetes.io/docs/concepts/scheduling-eviction/api-eviction/)의 graceful 종료·PDB 처리를 따른다. PDB0에서는 이 API 자체가 최소 Ready2를 보장하지 않으므로 각 단계 관측이 필요하다. [분산 제약 설명](https://v1-36.docs.kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)과 기존 PR65의 자동 재분산 한계를 유지한다.
