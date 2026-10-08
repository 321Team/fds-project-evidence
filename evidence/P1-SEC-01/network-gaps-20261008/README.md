# SEC IF-03 / IF-13A 빈 행 보완 — 2026-10-08 GWONUK 실제 관측

책임: [baseline #19](https://github.com/321Team/fds-project-baseline/issues/19).
기존 빈 행: [SEC Lead 행별 정정](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6039967923).
사용자 지시: SEC의 NOT_VERIFIED/PARTIAL 재수집 착수, 타 세션 비어 있음 확인.
이 회차는 과거 원본을 고치지 않는 새 관측이다. AC 승격·위험 수용·Issue 종결은 하지 않는다.

## 결과와 범위

실제 통신 관측: **2026-10-08 03:51:40~03:53:57 KST**, 총 **34건**.
사전 API: 03:44:15 KST부터, 사후 API: 03:54:22 KST 종료.
실행자 GWONUK / CODEX_ASSISTED. 독립 소스/증적 REVIEW=PENDING, MERGE=NOT_RUN.

| 행 | 새 관측 | 판정 한계 |
|---|---|---|
| IF-03 허용 | Worker03 transaction-api 네트워크에서 engine Pod IP 3개:8001 TCP 연결 3/3 | HTTP·업무 응답 시험 아님 |
| IF-03 비허용 | 기존 CoreDNS 네트워크에서 같은 3개 목적지 TIMEOUT 3/3 | 해당 출발지/목적지 표본의 결과. 과거 MON·KSM 회차를 소급 PASS 처리하지 않음 |
| IF-03 목적지 연결 | Worker 각각에 정확한 출발지/출발 포트/목적지 SYN 3개 도착, 대상 cali-tw 체인의 정책 미허용 DROP 각각 +3 | 패킷 헤더·route·집계 카운터 상관 검증이며 패킷별 kernel trace는 아님. source egress만으로 생긴 TIMEOUT이라는 설명은 이번 표본에서 배제 |
| IF-13A 허용 UDP DNS | APP 6개 + monitoring-api 4개에서 CoreDNS ClusterIP UDP/53 질의 10/10 응답(rcode=0) | TCP 시험을 UDP로 확대하지 않고 실제 UDP 질의 수행 |
| IF-13A 외부 UDP DNS | 같은 10개 출발지→8.8.8.8 UDP/53 TIMEOUT 10/10 | 별도 CoreDNS 출발 대조는 실제 응답 1/1. 외부 DNS 전체/전 시간대의 보장 아님 |
| IF-13A 일반 egress | transaction-api 3개 + monitoring-api 4개→1.1.1.1 TCP/443 TIMEOUT 7/7 | 목적지 서비스 건강을 확인한 시험은 아님. 출발지 정책 DROP 카운터로 보강 |
| IF-13A 출발지 연결 | 각 대상 cali-fw 체인의 정책 미허용 DROP: engine 각 +1, 나머지 각 +4, 합계31 | UDP 1개 + TCP SYN 3개 관측 예상량과 동일. 카운터는 관측 구간의 집계 |

monitoring-api 4개는 Prometheus, Alertmanager, Grafana, kube-state-metrics다.
**hostNetwork node-exporter/HEP egress, IF-05C Firing→Resolved, Probe 장애 주입은 NOT_RUN**이다.
따라서 IF-13A 전체 완료나 SEC 전체 인수로 올리지 않는다.

## 실행 방식·추적성

- PC→기존 fds-ansible01→svc_ansible@control01/worker01/02/03, 기존 sudo -n 사용.
  호스트 키 검증 유지. SSH/sudo 권한이나 토큰·계정 변경 없음.
- 기존 containerd의 sandbox ID·Pod UID·PID·starttime·cgroup·network namespace inode를 결속했다.
  Pod가 Running/Ready인지, hostNetwork가 아닌지 확인한 뒤 namespace FD를 고정하고 각 시험 전후 재검사했다.
- **호스트 Python 프로세스가 해당 Pod의 network namespace만 사용**했다. Pod 안의 앱 실행 파일·UID·사용자/PID/mount namespace를 사용한 시험이 아니다.
  실제 Pod IP에 socket을 bind했으며 NetworkPolicy의 L3/L4 경로만 관측한다. 새로운 Pod/Namespace/정책을 만들지 않았다.
- TCP는 연결 후 종료하며 업무 payload 없음. UDP는 공개 example.com 또는 클러스터 서비스명 DNS 질의 1개만 전송한다.
  소켓 제한3초, 개별 프로세스7초, 노드 collector100초 예산이며 예상과 다르면 해당 collector 중단.
- IF-03 tcpdump는 source IP와 source port55801~55803, dst8001로 제한했다. 헤더 텍스트만 수집, payload 표시 옵션 없음.
  각 capture는 24초 상한 뒤 종료하고 wait했다. 임시 workload나 서비스 변경이 없어 서비스 복구 작업은 없다.
- 각 *-invocation.json에 실제 SSH 명령·시각·RC·원격 실행 source SHA가 있다.
  원격 결과 JSON에는 소스 SHA, 대상 pin, 실제 명령·stdout/stderr/RC, 전후 규칙이 있다.
  collect.py/API 결과는 비밀정보를 제외한 **선별 필드**이며 전체 API 원본의 해시만 추가 기록했다.
- original-collect-ac02-residual-v3.sh는 evidence#110의 과거 참고 원본이다. 이번 실행 코드는 새 수집기이며
  과거 스크립트를 그대로 실행했거나 독립 리뷰를 마친 코드라고 표시하지 않는다.

## 실패와 정정도 보존

1. 첫 cp-inventory.json은 0바이트다. crictl 미설치로 rc1 종료했으며 stderr와 실행 소스 node-inspect.py를 보존했다.
   기존 ctr로 조회하는 node-inspect-v2.py가 4노드에서 성공했다. 새 도구는 설치하지 않았다.
2. policy-post.json의 기존 9개 API 조회는 모두 rc0이나, 추가 WEP CRD 조회는 지원되지 않아 rc1, 전체 collector rc2다.
   이 실패를 PASS로 덮지 않았다. 목적지 Pod IP→호스트 route→cali interface→kernel chain으로 별도 연결했다.
3. analysis-initial.json은 88/89다. Worker03의 ctr 반환 순서만 바뀐 것을 동일성 실패로 센 분석기 오류다.
   sandbox ID 정렬 후 모든 pin 필드가 같음을 확인했으며 현재 analysis.json은 **89/89**다. 원격 재시험은 하지 않았다.

## 사후 확인과 무결성

- 44개 Pod UID·IP·label·phase 동일, 6개 Node Ready.
- Namespace, NetworkPolicy 23개, GNP7개, Calico namespaced policy0개, HEP6개,
  Service/EndpointSlice의 수집 필드 동일. ResourceVersion만 비교에서 제외했다.
- 조회한 sandbox ID/PID/starttime/netns/cgroup 동일. filter table 구조는 카운터·생성시각을 제외하면 전후 동일.
- node-post/route 수집까지 끝났으며 원격 collector·probe·capture 프로세스는 종료했다.
- 기존 Failed icr39-probe Pod는 변경하지 않았다. Secret·환경변수·개인키·인증 입력은 수집하지 않았다.
- SHA256SUMS는 이 회차 파일 바이트를 고정한다. 해시·89개 대조 통과는 독립 리뷰나 AC 인수의 대체물이 아니다.

## 재검산과 다음 작업

이 폴더에서 `python3 analyze.py`는 **보존된 JSON만** 재분석한다. 서버 접근·패킷 전송 없음.
실행용 파일은 이번 PID/IP/UID와 묶인 이력용이며 새 창에서 재사용하지 않는다. 재시험은 fresh inventory로 별도 회차를 만든다.

1. SEC/Review Owner가 이번 IF-03 목적지 보강과 IF-13A 표본을 독립 검토한다.
2. IF-13A hostNetwork는 현재 HEP/GNP 계약을 대조해 별도 시험 행을 확정한다. 일반 Pod 결과를 대입하지 않는다.
3. IF-05C는 MON의 전용 테스트 알림·외부 수신 Firing/Resolved 원본을 수집한다. 룰 변경·외부 알림 발송은 이번 창에 넣지 않았다.
4. Probe는 기존 고정 번들·별도 시험창의 장애 주입/정리 조건을 유지한다. 이번 네트워크 관측으로 대체하지 않는다.

관련 증적 대기: [#152 Backup](https://github.com/321Team/fds-project-evidence/pull/152),
[#155 정책/MON 읽기 수집](https://github.com/321Team/fds-project-evidence/pull/155).
