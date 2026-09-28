# P1-SEC-01 — B2 externalTrafficPolicy: Local 소스 IP 보존 tcpdump 원본 (2026-09-28)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). [evidence PR#58](https://github.com/321Team/fds-project-evidence/pull/58)에 대한 [GWONUK 재검토](https://github.com/321Team/fds-project-evidence/pull/58#issuecomment-5857009999)의 해소 조건 ②("edge01 시험 시간창의 transaction-api Pod access log에서 실제 remote addr `10.1.93.50:*` 확인 원본 보완, 또는 PR 문구를 TCP connectivity 부분 증적으로 명확히 하향") 대응.

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-b2-worker-sourceip-20260928T104719Z.tar.gz` |
| SHA-256 | 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 도구 | [infra-ansible `playbooks/p1-sec-01-b2-collect-58.yml`](https://github.com/321Team/infra-ansible/blob/p1-sec-01-b2-collect-58-20260928/playbooks/p1-sec-01-b2-collect-58.yml) ([infra-ansible PR#58](https://github.com/321Team/infra-ansible/pull/58)) |
| 수집 | ansible01(`server01_ansible`) → k8s-control01/k8s-worker01-03/edge01 대상 read-only 접속 시험, 2026-09-28T10:47:19Z(UTC) / 2026-09-28 19:47 KST, 변경 없음 |
| 전달 경로 | ansible01 `~/evidence-58/20260928T104719Z/` → 사용자가 zip으로 압축해 세션에 업로드 → 세션에서 압축 해제 후 대상 8개 파일만 재구성·SHA-256 재확인 |
| 수집·제공 | 이하영(P1-SEC-01 Lead). 수집 자동화 playbook 작성·실행 보조, 패키징·README 작성은 Claude Code 보조(CLAUDE_ASSISTED). 실제 서버 실행은 이하영이 ansible01에서 직접 수행 |

## 수신 검증

- tar.gz 내부 `SHA256SUMS`(8개 파일 대상) 재계산 일치
- 비밀정보 검색: 해당 없음(kubectl Service/Pod 상태, tcpdump 패킷 헤더, curl 응답 헤더만 포함 — 인증 토큰/비밀번호 없음)

## 내용물 요약 (원본 보존 — 판정 아님)

| 파일 | 내용 |
|---|---|
| `00_cluster-state.txt` | k8s-control01에서 조회한 node 목록, `fds-app` 네임스페이스의 transaction-api Pod, `transaction-api`(ClusterIP)/`transaction-api-nodeport`(NodePort 30080, `externalTrafficPolicy: Local`) Service 원본 JSON, EndpointSlice 원본 JSON |
| `SUMMARY.txt` | k8s-worker01/02/03 3대 각각의 node IP·Pod IP·판정(`PASS`) 요약 |
| `curl_k8s-worker0{1,2,3}.txt` | edge01(10.1.93.50)에서 각 워커 `:30080/readyz`로 보낸 curl 요청의 응답 헤더·`HTTP_CODE`·`CURL_RC` 원본 |
| `tcpdump_k8s-worker0{1,2,3}.txt` | 각 워커의 transaction-api Pod veth(cali\*) 인터페이스에서 캡처한 tcpdump 원본. `10.1.93.50.<port> > <Pod IP>.8000`으로 시작하는 SYN/ACK 패킷이 3대 전부에서 확인됨 |

## 배경과 한계

- [evidence PR#58](https://github.com/321Team/fds-project-evidence/pull/58)은 edge01→워커 `:30080` TCP `CONNECTED` 3건만 보존했고, GWONUK 재검토는 이를 "최종 Positive 전체 인수"로 볼 수 없다며 Pod HTTP access log의 remote_addr 확인을 요구했다.
- 확인 결과 transaction-api Pod의 stdout access log 자체가 비어 있어(원인 미해결, 별도 후속 필요) HTTP 레벨 access log 원본은 이 수집으로도 확보하지 못했다.
- 대신 **Pod veth 인터페이스에서 tcpdump로 L3(IP 패킷) 레벨 소스 주소를 직접 캡처**하는 방식으로 전환해, `externalTrafficPolicy: Local`이 클라이언트 소스 IP(`10.1.93.50`)를 Pod까지 원본 그대로 보존한다는 것을 워커 3대 전부에서 실증했다. 이는 애플리케이션 access log가 아니라 **커널/네트워크 레벨 원본**이며, HTTP access log의 대체 증거로 인정할지, 또는 PR#58 문구를 TCP connectivity 증적으로 하향할지는 이 편입만으로 결정하지 않는다 — Review Owner(GWONUK)/Lead가 baseline #19 및 evidence PR#58에서 별도로 판단한다.
- edge01의 curl 응답은 애플리케이션(`readyz`)이 실제로 200을 반환했음도 함께 보여주지만, 이 역시 access log 자체는 아니다.

이 편입은 원본 보존이다. P1-SEC-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
