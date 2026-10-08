# Edge 전환 전 현재 구성 — C0 참고 수집 + P4 source preservation

책임 baseline#19/P1-SEC-01. 실행·작성 GWONUK / CODEX_ASSISTED.
사용자 “착수”에 따라 [한정 GO6043603789](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6043603789)를 남기고 수행했다.
창 2026-10-08 02:50~03:20 KST, P4 latest start03:10, 현재 구성 1회/자동 재시도 없음.
**Edge upstream 전환·전환 후 검증·AC 인수의 증거가 아니다.**

## 실행 원본·환경

- control01 pre: infra-kubernetes#70 merge `95af5b09e50f31f28101fb6f9840aef42c227a3f`의
  `ops/edge01-cutover/control01-cutover-check.sh`, GitHub blob bytes로 전달하고 서버에서 SHA 확인.
  02:51:51~54 KST, rc0. RUN `20261008T0255`는 회차 식별자이며 실제 실행 시각은 원본을 따른다.
  `/root/sec19-edge-c0.Ky13JT1l`, 스크립트 자체 로그 `/root/edge-cutover-20261008T0255/`.
  회수 archive에는 동일한 pre stdout/stderr와 실행 소스, nodes-before 및 시작/끝 시각을 보존했다.
- P4 source: infra-ansible#60 merge `c0d784fa9a1d9dfc57f504ed969c036d0860acef`.
  PR HEAD `445d1451120c2bc0aeb85c90c3bfe0737022c498` 독립 APPROVED/병합을 재확인했다.
  collector `playbooks/p1-sec-01-b2-collect-58.yml` SHA256
  `42fc3ed486b9b16f6be156b2770ada6cf9fa725c9b0a5882473afa0bd7eb9024` 일치.
- 기존 clean checkout `/home/server01_ansible/p1-sec-b2-runtime-20261001T115520`, HEAD/무변경 재확인.
  Ansible core2.16.19, 기존 server01_ansible→svc_ansible + control01/Worker sudo.
  edge01 curl은 sudo 없이 기존 계정을 사용했다. 새 키/계정/권한·보안 설정 변경 없음.
- 실제 P4 **02:55:17~29 KST**, 실행1회/rc0, 사후 확인02:55:30 완료.
  Controller 작업 `/home/server01_ansible/sec19-edge-p4.jhwyv1bh`, raw 회차 `20261007T175517Z`.
  명령/추가변수/Ansible 버전/소스상태/수집기 bytes/stdout/stderr/rc 보존.
- 승인 collector의 기존 변수로 out_root/out/td_file/curl_file만 회차별 경로로 지정했다.
  실제 내용은 archive의 extra-vars.json/command.json에 있다. source 수정 없음.
  고정 `/tmp/00_cluster-state.txt` 이전 파일은 실행 전 bytes/hash를 prior-control-temp.stdout에
  base64 보존했다. 기존 출력 삭제·과거 증적 교체 없음. 새 수집용 임시 파일은 원본 보존 상태다.

## 현재 구성 결과

control01 pre 결과(실제 전환 직전 C0 전체 완료와 구분):

| 항목 | 관측 |
|---|---|
| Node | 6/6 Ready |
| Service | NodePort80→8000:30080 / externalTrafficPolicy Local |
| local endpoint | Worker01/02/03 각1, ready=true/terminating=false |
| GNP | order50/preDNAT/applyOnForward true, .50/32 TCP30080 Allow 뒤 해당 포트 Deny |
| metrics NodePort32085 | 없음 |
| MON | count(up)=23 / up==1=23 / up==0=EMPTY(성공·빈 결과) |
| 조회 오류 | 0 |

P4 원본 수신 후 별도 재대조:

| 대상 | 현재 transaction-api Pod IP | 관측 source | curl/HTTP |
|---|---|---|---|
| worker01 .105 | 10.244.79.112 | 10.1.93.50→Pod:8000 일치3행 | rc0 / 200 |
| worker02 .107 | 10.244.69.236 | 10.1.93.50→Pod:8000 일치3행 | rc0 / 200 |
| worker03 .108 | 10.244.39.208 | 10.1.93.50→Pod:8000 일치3행 | rc0 / 200 |

각 worker SUMMARY=PASS, play recap failed/unreachable/rescued/ignored 모두0.
Ansible의 changed는 수집 출력·async capture 작업을 포함하며 운영 설정 변경을 뜻하지 않는다.
패킷은 기존 collector의 숫자 IP/포트·헤더 출력이고 payload(-A/-X/-w)는 저장하지 않았다.
worker-verification.json은 로컬 파생 검증이며 서버 raw와 구분한다.

## 비중첩·사후 상태·무결성

- 시작 전 controller/대상4대에서 ansible-playbook/tcpdump/backup.sh/probe.sh/edge01-cutover.sh
  이름으로 식별되는 실행 프로세스 없음. 전용 controller flock 사용. 모든 외부 작업을 잠그거나
  모든 실행 형태의 부재를 증명하는 방식은 아니므로 알려진 채팅/이슈 상태도 별도 대조했다.
- P4 전후 Node6 Ready·APP Pod UID/배치/Ready/restarts·Endpoint UID/IP/conditions 투영값 동일.
  Worker3의 캡처/관련 시험 프로세스 사후 부재 확인. control01 pre의 임시 PF는 자체 PID 종료/wait.
- P4 archive64파일 / 내부 SHA256SUMS63항목 모두 일치. C0 archive7파일에는 내부 manifest 없음.
  C0는 전달 source의 서버 SHA확인, SSH수신 bytes hash와 outer manifest로 결속했다.
- 두 tar는 SSH stream으로 수신한 원본 bytes이며 sidecar SHA는 **로컬 수신 bytes** 기준이다.
  서버에 저장된 outer tar와 비교한 것으로 표현하지 않는다. 기존 과거 증적을 수정하지 않았다.
- 기존 #86에도 있던 non-boolean conditional deprecation2건을 원문 보존했다.
  이번2.16.19 실행은 성공했지만 2.19+ 호환성까지 검증한 것은 아니다(기존 infra-ansible#9 후속).

## 범위·다음 단계

**PRE_COLLECTION=PASS_WITH_SCOPE / P4_CURRENT_TOPOLOGY_RUNTIME=PASS(3/3) /
POST_BASELINE=UNCHANGED / CAPTURE_PROCESSES=ABSENT.**

이번 흐름은 edge01에서 Worker NodePort로 직접 GET한 것이다. edge01 nginx upstream 경유·전환,
비승인 source 차단, POST/DB 업무 smoke, 전체 AC-04 또는 전체 SEC 인수를 입증하지 않는다.
nginx reload/upstream 변경·Secret/DB 변경·재시작·장애주입·보안완화는 하지 않았다.
10/10 전환 계획은 여전히 별도이며 실제 전환창의 fresh C0, edge01/Worker 표식 TRACE_READY,
apply→trace, C2/P4·C3 관찰과 #47 인계는 남는다. 이번 결과를 전환 후 증적으로 사용하지 않는다.
독립 증적 리뷰·편입/병합·AC·Issue/Phase1 Close는 별도다.
