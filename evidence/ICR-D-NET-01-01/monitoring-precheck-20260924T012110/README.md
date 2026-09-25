# ICR MON 사전점검 수신·정책 대조 — 2026-09-24 KST

책임: ICR-D-NET-01-01 Lead 이권욱. 연계: [ICR #14](https://github.com/321Team/fds-project-baseline/issues/14), [MON #17](https://github.com/321Team/fds-project-baseline/issues/17), [SEC #19](https://github.com/321Team/fds-project-baseline/issues/19).

**수신 무결성 확인 및 실제 조회 완료 / 실제 packet Source·통신 AC는 미검증.**
독립 증적 편입 리뷰와 main 병합은 PENDING이다.

## 출처와 검증

- 원 첨부: `ICR_MON_Precheck_N11a7g.tar.gz`, 9,443 bytes.
- SHA256: `c7ef76c9e7a4b314df96e946ee4db5d7b71e96bb22224903b713cace31a2b724`.
- 사용자 첨부 archive와 sidecar 일치, 내부 Manifest 7/7 및 실행 소스 3/3 해시 일치.
- `original/`의 8개 텍스트 파일은 archive 내부 바이트 그대로다. 서버 `SHA256SUMS`는 변경하지 않았다. 이 경로의 별도 `SHA256SUMS`는 수신 후 편입 파일 검증용이다.
- 원 archive/sidecar 첨부 식별자는 `RECEIPT.json`에 기록했다. 원 archive는 기존 첨부 보관을 유지하며 재압축·Git binary/Release Asset 업로드는 하지 않았다. 독립 검토자의 원 archive 접근 인계는 미확인이다.
- 소스: [infra-kubernetes PR25](https://github.com/321Team/infra-kubernetes/pull/25), `722e58638dad565949220cc1bbdbbafca15b5a92`, merge `78d86b5aafd9d87997b4e4c7e336994a20b28743`.
- 코드 `REVIEW=NOT PERFORMED (Pre-check)`. 작성자 자체 검사·소스 병합을 독립 코드 승인으로 표시하지 않는다.

## 실제 실행

| 항목 | 관측 |
|---|---|
| 시각 | controller 2026-09-24 01:21:09 KST, remote 01:21:10–11 KST |
| 경로 | ansible01/server01_ansible → k8s-control01/10.1.93.102, svc_ansible |
| infra-ansible | `da7f2ccd52ee407e61376d11375a1361f076f112`, tracked_changes=false |
| inventory SHA256 | `0e7e66c6b182c95d9bff4502e02de7c8669a781296b7ff45965a8b2defb4f565` |
| 실행 | 현장 Ansible syntax-check 성공, controller/remote rc=0, 17개 조회 모두 rc=0 |
| Ansible recap | ok=4, changed=1, unreachable=0, failed=0. changed=1은 localhost 증적 파일 저장 작업 |
| API·노드 | API LB https://10.1.93.109:6443, 정본 6개 노드 Ready |

결과 JSON은 선택 필드의 투영이다. `stdout_sha256`는 수신 API 응답 해시이며 전체 API 응답 원문은 archive에 없다. 응답 해시를 투영 JSON 바이트의 해시로 재검증했다고 표시하지 않는다. 수신 파일·코드 해시 일치는 원격 실행 진위의 독립 증명이나 Runtime AC PASS가 아니다.

## 식별된 송신·수신 대상

| 항목 | 관측 |
|---|---|
| Prometheus | monitoring-api/prometheus-58c848c688-kzvhp, Running/Ready |
| UID | `46c00f91-2073-440a-800c-6cedba89d291` |
| 배치·IP·SA | worker03 / Pod 10.244.39.219 / host 10.1.93.108 / SA prometheus |
| imageID | `10.1.93.54/fds/prometheus@sha256:b77f9cee82fd1c61521634d2d6b192fc526ffd938e904b8e6836b6c0cf8d875a` |
| node-exporter | Worker3개 모두 Running/Ready, hostNetwork=true; Ready가 scrape Target UP을 뜻하지 않음 |
| Calico | 6/6 Running/Ready, node digest `c061070a27292f8152ae6a0582078eb9059d1b6ed5e57c2052e5c22534734240`. digest만으로 semantic version을 확정하지 않음 |

Pod/host IP는 패킷 Source 후보이며 monitor01에서 관측한 Source가 아니다. 현재 Prometheus의 Remote Write 설정·실제 송신 여부·monitor01 서비스 상태는 이번 수집 범위 밖이다.

## 정책 대조와 제한

1. **HEP 6개:** ens160, 노드별 expectedIPs, `fds.example/bootstrap=p1-k8s-01-v4`. Worker3개의 `fds.example/role=worker`가 실제 존재한다. 운영 `nodeport-30080-allow` selector는 이 Worker HEP3개를 선택한다. order50/preDNAT/applyOnForward 및 .50/32 Allow/나머지 TCP30080 Deny도 관측했다. 이는 [PR21](https://github.com/321Team/infra-kubernetes/pull/21)의 v4 운영 경로 설명을 뒷받침하며 독립 리뷰·NodePort 양성/음성 시험·복구를 대신하지 않는다.
2. **호스트 GNP 6개:** default tier/order100/applyOnForward=false, ingress 최종 Deny. TCP9100 허용 규칙이 없으며 TCP10250은 CP3개 .102/.103/.104 /32만 허용한다. 관측 PodIP 및 worker03 hostIP 어느 쪽도 이 10250 source 목록에 없다. 정책 누락은 확인됐지만 실제 packet Source·hit counter·drop 지점은 미수집이다. 전체 timeout의 원인 확정으로 확대하지 않는다.
3. **native NetworkPolicy:** monitoring-api 17개, monitoring-node 2개, 해당 namespace의 Calico NP는 0개. `allow-prometheus-egress-kubelet`/`...node-exporter`는 6개 NodeIP에 TCP10250/9100 egress를 허용한다. `prometheus-remote-write-allow`는 10.250.10.30/32:443을 허용한다. Pod egress 허용이 수신 호스트 허용이나 TLS/Auth 성공을 대신하지 않는다.
4. **잔여 namespace 문구:** `allow-prometheus-egress-scrape`는 여전히 `fds`를 지정한다. 동시에 `prometheus-allow`에는 fds-app transaction-api:9091/fds-engine:9090 허용이 존재한다. native 정책은 허용 합집합이므로 옛 규칙 하나만으로 앱 scrape 전체가 차단됐다고 판단하지 않는다. MON PR7 병합은 이 live 객체의 수정/삭제 증거가 아니다.
5. **IPPool:** 10.244.0.0/16 단일 pool, natOutgoing=true, ipipMode=Never, vxlanMode=CrossSubnet. 모든 흐름을 VXLAN 캡슐화로 가정하지 않는다. Calico 문서상 pool 밖 목적지에는 SNAT가 예상되지만 실제 노드 dataplane·예외·wire Source를 수집하지 않아 이번 실제 SNAT 발생 여부는 미검증이다. IF-06B Source 및 내부 SNAT 금지 AC는 별도 대조한다.

동일 노드 worker03 TLS IP SAN 오류는 기존 MON 보고의 독립 후속이다. 이번 수집은 Prometheus `/api/v1/targets`를 조회하지 않았으므로 Target UP/DOWN 수치의 새 실측으로 표시하지 않는다. 함께 확인한 01:20:05 MON 콘솔 자료는 별도 제출 자료이며 이 archive에 포함되지 않는다.

공식 의미 참고: [Calico outgoing NAT](https://docs.tigera.io/calico/latest/networking/configuring/workloads-outside-cluster), [HostEndpoint](https://docs.tigera.io/calico/latest/reference/resources/hostendpoint), [forwarded traffic](https://docs.tigera.io/calico/latest/reference/host-endpoints/forwarded), [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/). 이는 API 필드 해석 참고이며 설치된 digest의 동작을 실측한 근거가 아니다.

## 다음 작업·인수 상태

- ICR: 현재 sender identity를 재확인하고 worker03 송신/worker01 수신 ens160에서 기존 15초 scrape의 TCP9100/10250 SYN 헤더를 제한 관측한다. 패킷·리스너·정책 counter/경로를 대조한 뒤 source 최소 범위를 결정한다. 수집 도구가 없거나 기존 권한이 부족하면 오류를 반환하며 설치·권한 변경으로 진행하지 않는다.
- K8S/SEC: source 관측을 받아 필요한 최소 허용 정책과 kubelet serving 인증서 보완. 새 정책은 독립 코드 리뷰 후 적용한다. PodCIDR 전체 또는 worker IP 전체를 승인 Prometheus 신원과 동일하게 취급하지 않는다.
- MON: monitor01 receiver/TLS/Auth/Payload와 실제 Remote Write 송신 입력 통합. ICR은 실제 IF-06B 수신 Source/return route를 별도로 연결한다. scrape Source 관측을 IF-06B Source 검증으로 대체하지 않는다.
- 기존 ICR AC 집계(3 PASS / 8 PARTIAL / 2 FAIL 보고 / 6 NOT_VERIFIED / 1 BLOCKED), 담당·계획·open 상태는 유지한다. 정책 적용, TLS 우회, 장애 주입, 서비스 재시작 또는 새 Runtime AC 인수는 수행하지 않았다.

이 PR은 [EVIDENCE_POLICY](../../../governance/EVIDENCE_POLICY.md)에 따라 독립 편입 검토가 필요하다. 이번 수신 검증과 후속 순수 사전점검은 해당 편입 승인을 기다리는 단계가 아니다.
