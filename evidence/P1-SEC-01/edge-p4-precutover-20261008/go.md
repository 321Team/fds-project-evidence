## GWONUK 현재 구성 C0 참고 수집 + P4 출발지 보존 1회 GO

2026-10-08 KST. 사용자 “착수” 지시를 현재 구성의 수집 실행으로 한정합니다.
10/10 Edge upstream 전환 계획(이재환 실행)과 분리하며 전환 후 P4 증적을 미리 만든 것으로 표시하지 않습니다.

- 범위: control01 읽기 전용 pre 수집 → 조건 충족 시 edge01(.50)→Worker3 NodePort30080 /readyz GET과 Pod veth 패킷 헤더 관측 **1회**.
- 실행자: GWONUK, ansible01 기존 server01_ansible→svc_ansible, control01/Worker 기존 sudo.
- 창: **10/8 02:50~03:20 KST**, P4 최종 시작03:10. 자동 재시도 없음.
- C0 source: infra-kubernetes#70 merge `95af5b09e50f31f28101fb6f9840aef42c227a3f`의 control01-cutover-check.sh pre만.
- P4 source: infra-ansible#60 merge `c0d784fa9a1d9dfc57f504ed969c036d0860acef`, 승인HEAD445d1451120c2bc0aeb85c90c3bfe0737022c498의 APPROVED/병합 재확인.
  collector `playbooks/p1-sec-01-b2-collect-58.yml` SHA256 `42fc3ed486b9b16f6be156b2770ada6cf9fa725c9b0a5882473afa0bd7eb9024`.
  기존 clean checkout HEAD/무변경 및 파일 SHA 재확인, Ansible2.16.19(기존 #86 성공 버전) 사용.

시작 조건:6Ready, APP Pod/Endpoint 정상·Worker endpoint1/1/1, ETP Local/30080 및32085없음,
.50/32 허용 GNP, MON23/23/DOWN0, 기존 시험 프로세스·수집 중첩 없음, source 무결성 일치.
같은 알려진 활성 채팅은 Harbor 주소 override 코드 준비 단계로 확인했습니다. 이 확인은 외부 모든 작업 부재를 보장하지 않으며 현장 상태도 별도 확인합니다.

Worker별 최대30초 tcpdump, GET 최대10초. payload 저장 옵션(-A/-X/-w) 없음.
운영 설정·nginx reload/upstream 변경·POST 거래·DB/Secret 변경·보안 완화 없음.
실패/미판정/노드·endpoint변화/상한 도달 시 다음 실행을 중단하고 최초 원본/rc를 남깁니다.
실행은1회, 실패 회차를 자동 재실행하지 않습니다. 수집 파일은 보존하고 자체 임시 PF/캡처 종료 여부를 확인합니다.
합격 관측은 Worker3 각각 source.50→현재 Pod:8000, curl rc0/HTTP200 및 사후 기준선 유지입니다.
기존 source의 고정 /tmp 수집 파일은 이번 실행 전에 기존 파일 보존을 준비하고 회차별 결과를 별도 보관합니다.

**한정 GO: 현재 구성 source-preservation 관측. Edge Cutover GO, 전환 후 C0/C2 인정, AC·Issue·Phase1 Close가 아닙니다.**
증적 독립 리뷰는 별도이며 코드 승인과 실행 결과를 구분합니다. AI 사용: CODEX_ASSISTED.
