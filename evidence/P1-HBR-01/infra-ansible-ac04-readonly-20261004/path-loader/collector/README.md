# FDS_HBR_AC04_PR63_Path_Loader_Readonly_v1_0

## 목적과 변경점

Phase1 Harbor AC04의 미확인 IPv6 listener / userland proxy 경로와 nft loader 연결 검토를 위한 추가 읽기 전용 수집입니다.
기존 preapply archive `2a4908f103934e2ed06456c2b2848566a22e0de0c7bf3e38dc8ef0b199051fe2`를 참조합니다.
기존 discovery/precheck/contract runtime를 다시 실행하지 않습니다. 소스·PR·engine·inventory identity gate와 이 supplemental play의 syntax 및 targeted collection만 실행합니다.

## 위치와 전제

ansible01의 기존 계정 server01_ansible, HOME /home/server01_ansible에서 `bash run.sh`로 실행합니다. root 계정 또는 harbor01에서 직접 실행하지 않습니다.
기존 ~/p1-ans-01 저장소와 gh 인증, ~/.config/ansible/p1-ans-01.env, 기존 svc_ansible SSH/sudo 경로를 사용합니다.
Ansible core2.16.19, strict host-key 검증, 인벤토리 harbor01=10.1.93.54/ens160 조건을 유지합니다.
Source HEAD badbe29440916ec3ec79da8fc81722c2e6c4e75b 또는 PR 상태가 달라지면 중단합니다. Git fetch는 워킹트리 전환/수정 없이 수행합니다.

## 수집 범위

- `ss -ltnp`의443 listener PID/프로세스와 실제 docker-proxy의 선택된 network argv. 타 프로세스 argv나 환경변수는 수집하지 않습니다.
- 현재 주소, IPv6 경로, all/default/ens160 disable_ipv6·forwarding 설정.
- nftables.service 시작/reload/stop 명령, 활성/enable 및 dependency/trigger 속성.
- 기존3개 nft 설정 파일 hash와 include/flush/table/define 행. 주석과 활성 행을 구별합니다. include는 실행하거나 재귀 추적하지 않습니다.
- /etc/docker/daemon.json의 ipv6/ip6tables/userland-proxy/bip/fixed-cidr-v6만 수집. 미설정 항목은 기본값을 추정하지 않습니다.
- 정상 Ansible 임시 script 전송 및 계정 HOME의 evidence/source 파일만 생성. 방화벽·서비스·Docker·sysctl 변경, restart/reload/enable, conntrack 설치, token 발급은 수행하지 않습니다.

## 판정 및 후속 검토

정상 수집: STATUS=PATH_LOADER_READONLY_CAPTURED_REVIEW_REQUIRED, PATH_LOADER_EXIT_CODE=0.
이는 collection 성공이며 IPv6 reachability/guard protection/global custom loader 부재/Apply approval/AC04 PASS가 아닙니다.
리스너 PID가 사라지거나 표시되지 않으면 NO_PID/UNAVAILABLE_REVIEW_REQUIRED 기록을 보존하고 검토합니다. 일부 프로세스 관측은 시간차가 있을 수 있습니다.
설정 파일 링크/과대 크기/읽기 실패 또는 필수 명령 실패는 FAIL_OR_INCOMPLETE/rc1로 보존합니다.
HOME_EVIDENCE tar.gz와 같은 위치의 .sha256를 함께 전달합니다.
실패 시 현재 증거를 보존하고 원인을 검토합니다. 운영 상태 변경이 없어 방화벽 rollback은 필요하지 않습니다. 검사 실패를 bypass하기 위한 Apply/reload/restart는 하지 않습니다.
이미 수집한 flush ruleset은 실제 호출 경로/유지보수 정책 검토 대상으로 남깁니다. 설정 삭제·service disable 등으로 임의 해결하지 않습니다.

## 터미널 유지

실행 래퍼는 자식 bash에서만 동작합니다. 부모 shell에 set -e/-u/pipefail를 설정하거나 run.sh를 source하지 않습니다.
기존 운영 env는 검증 후 자식 shell에서 로드합니다. 환경 파일 내용·SSH private key·토큰은 증거에 포함하지 않습니다.

## 사전 검증 범위

첨부 VALIDATION.json에 실제 수행한 STATIC/MOCK 검사를 기록합니다. 실제 Ansible syntax 및 ansible01/harbor01 실행은 운영자 실행 전 NOT_RUN입니다.
독립 reviewer 코드 승인 및 PR63 Draft/merge HOLD는 이 kit로 변경되지 않습니다.
