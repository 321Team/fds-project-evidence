# IF-13A hostNetwork/HEP 보완 및 IF-05C 원본 조회 — 2026-10-08

연계: [baseline #19](https://github.com/321Team/fds-project-baseline/issues/19),
[앞선 일반 Pod 회차](../network-gaps-20261008/README.md), [증적 PR157](https://github.com/321Team/fds-project-evidence/pull/157).
사용자의 후속 착수 지시에 따라 GWONUK/CODEX_ASSISTED로 수행했다. 이전 회차 원본은 변경하지 않는다.

## 실제 수행

08:25 KST부터 fresh API/런타임 조회, 08:27~08:29 hostNetwork 관측, 08:30~08:32 MON 읽기 조회.
정확한 시작/종료 시각·명령·source SHA·RC는 각 invocation 및 결과 JSON에 있다.

| 대상 | 실제 결과 |
|---|---|
| 외부 대조, 기존 CoreDNS 네트워크 | 8.8.8.8 UDP DNS 응답, 1.1.1.1 TCP443 연결 — 2건 |
| Worker01/02/03→내부 DNS .52/.53 | UDP 질의 응답6건(rcode0), TCP53 연결6건 — 12건 |
| Worker01/02/03→외부8.8.8.8 UDP53 | EPERM 즉시 거절3건, 각 노드의 HEP egress DROP +1 |
| Worker01/02/03→외부1.1.1.1 TCP443 | TIMEOUT3건, HEP egress DROP 각각 +3/+3/+10 |

hostNetwork 18건 + 대조2건을 보존했다. Worker03 +10은 동시 호스트 트래픽을 포함할 수 있으므로
시험 SYN3개 전부와 1:1로 일치한다고 주장하지 않는다. 집계 counter를 packet trace로 확대하지 않는다.

기존 node-exporter 3개 sandbox의 Pod UID/PID/starttime/cgroup/network namespace를 결속했다.
namespace inode가 host와 같고 API hostNetwork=true이며 IP가 해당 Node IP임을 확인했다.
호스트 Python이 고정 namespace FD에서 해당 Node IP에 bind한 L3/L4 관측이다.
**node-exporter 바이너리·프로세스 UID·애플리케이션 기능 시험은 아니다.**
기존 정상 계정 경유 SSH/sudo -n을 사용했고 설정/방화벽/Pod/네임스페이스 변경은 없다.

## 첫 중단과 판정 보완

host105.json의 첫 실행은 허용4건 뒤 외부 UDP에서 `PermissionError:[Errno 1] Operation not permitted`를 만나
child rc3/collector rc2로 중단했다. TIMEOUT만 기대한 도구의 제한이며 원본 ERROR/RC를 그대로 보존했다.
같은 시점 HEP egress chain의 DROP이 +1이었다. 이 첫 실행은 개별 syscall 단계가 기록되지 않아
후속 v2와 구분한다. `EPERM이면 무조건 PASS`로 바꾸지 않았다.

v2는 bind/connect/send/recv 단계와 errno를 기록하고 **고정 출발지 + send/connect EPERM 또는
connect/recv TIMEOUT + 같은 HEP chain의 DROP 증가**를 모두 요구한다.
bind 오류, errno13, 잘못된 출발지, 연결 성공, DROP 증가 없음, 규칙 구조 변경은 거절한다.
10개 MOCK 사례 통과. Worker01은 미실행 TCP443 한 건만 이어갔고, 최초 UDP를 반복하지 않았다.
Worker02/03 UDP는 send 단계 errno1, DROP+1로 확인했다.

[Linux upstream netfilter nf_hook_slow](https://github.com/torvalds/linux/blob/master/net/netfilter/core.c)의
NF_DROP→EPERM 반환 경로는 이러한 해석을 뒷받침한다(2026-10-08 조회).
이 문서와 counter만으로 실행 커널의 개별 call stack을 입증했다고 표시하지 않는다.

## 사후 검증·재현

- 44 Pod UID/IP/label/phase 동일, 6 Node Ready.
- 수집한 Namespace/NetworkPolicy/GNP/HEP/Service/EndpointSlice 필드 동일(ResourceVersion 비교 제외).
- 4노드 조회 sandbox pin 및 filter 구조 동일(카운터·생성시각 제외).
- `python3 analyze.py`: 보존 파일만 대조하며 64/64. 실제 시험 성공/독립 승인/AC 인수를 뜻하지 않는다.
- `python3 -B test-guard.py`: MOCK10/10, 서버 접근 없음.
- 실행 source SHA18건 연결. SHA256SUMS에 모든 회차 파일을 포함한다.
- 실행 수집기는 이번 UID/PID/IP에 고정된 이력이다. 새 승인·fresh 조건 없이 재실행하지 않는다.
- build.py는 앞선 회차 build-probes.py에서 기존 socket 로직을 읽는 의존성이 있다. 생성된 probe*.py에 실행 로직 전체가 고정돼 있다.

## IF-05C 조회 결과와 남은 경계

현재 실제 Prometheus의 전용 규칙은 inactive/health ok, expr `vector(1)==0`이다.
12일 Firing sample 집계 및9/26 13:00~16:00 KST 조회 모두 success·빈 결과였다.
storageRetention은 `15d or 16GiB`; TSDB 최소 시각 metric도 원문 보존했다.
**조회된 자료로 원본을 복원하지 못했으며, 과거 시험 자체가 없었다고 단정하지 않는다.**

현재 Alertmanager `/api/v2/status`에서 기본 discord-notifications 수신 경로와 send_resolved=true를
직접 확인했다. Secret URL/credential을 제외한 투영본과 원 응답 SHA만 보존했다.
이는 실제 Firing/Resolved 수신 증거가 아니다. 현재 up23/다운0, loopback PF는 모두 종료·회수했다.

[다음 시험안](IF05C_NEXT_WINDOW.md)과 정확한 apply/restore JSON Patch 후보를 준비했다.
실제 규칙 일시 변경과 Discord 시험 알림 발송은 사용자 확인 대기이며 **미실행**이다.
Probe 장애 주입도 별도 고정 번들·창을 유지하며 이번 회차에 포함하지 않았다.

RUNTIME=상기 관측 / STATIC=64대조·MOCK10 / REVIEW=PENDING / MERGE=NOT_RUN.
AC·기존 PARTIAL·Issue Status·Close는 변경하지 않았다.
