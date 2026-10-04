# Phase1 Harbor AC04 IPv6 persistent configuration read-only v1.0

## 실행 환경

ansible01 / server01_ansible / HOME /home/server01_ansible. 기존 gh·git 저장소 ~/p1-ans-01, Ansible2.16.19, ~/.config/ansible/p1-ans-01.env와 기존 SSH key/svc_ansible sudo 경로를 사용합니다.
`bash run.sh`로 자식 shell에서 실행합니다. 부모 터미널에 strict flags를 설정하거나 source하지 않습니다.
exact PR63 source badbe29440916ec3ec79da8fc81722c2e6c4e75b 및 inventory harbor01=10.1.93.54 gate를 유지합니다. source/PR 변경 시 중단합니다.

## 추가 수집만 수행

기존 discovery/precheck, proxy/listener/nft ruleset 검사를 반복하지 않습니다.
필수 identity/source/engine/inventory gate와 supplemental syntax 이후:
- ens160 활성 NetworkManager connection UUID를 가져와 그 연결의 UUID/interface/autoconnect/ipv6.method만 조회합니다.
- NetworkManager 및 systemd-sysctl의 상태/loader 속성만 조회합니다.
- /etc,/run,/usr/lib NetworkManager profile에서 동일 UUID의 파일 backing/hash 및 선택4개 필드만 기록합니다. 프로필 전체·credential·private-key 내용은 증거에 넣지 않습니다.
- /etc/sysctl.conf와 표준 sysctl.d4개 경로의 hash 및 all/default/ens160 disable_ipv6 행만 기록합니다. 다른 설정·credential 본문은 출력하지 않습니다.
- 심볼릭 링크는 따라가지 않고 review-required로 기록합니다. include/load/설정 변경을 하지 않습니다. 특수/custom loader와 sysctl precedence는 수동 검토 범위입니다.

NetworkManager 연결이 없거나 uuid 조회 실패/잘못된 uuid는 STOP. 다른 네트워크 관리 도구로 추정해 계속하지 않습니다.
프로필 파일이 없거나 여러 개면 해당 count와 실제 원본을 검토합니다. 수집 성공이 영구 설정 입증을 의미하지 않습니다.
`nmcli connection show`만 사용하고 modify/up/down/reload/reapply를 사용하지 않습니다. sysctl -w/--system, service restart/reload, 재부팅/네트워크 재연결도 실행하지 않습니다.

## 정상·실패 판정

정상 수집 STATUS=IPV6_CONFIG_READONLY_CAPTURED_REVIEW_REQUIRED / IPV6_CONFIG_EXIT_CODE=0.
설정 근거를 읽었다는 뜻이며 reboot/reconnect persistence 실제 시험·Apply approval·AC04 PASS가 아닙니다.
재부팅/재연결 시험은 비충돌 변경창과 별도 승인된 검증 계획에서 수행합니다. 이 패키지에서 미확인을 PASS로 채우지 않습니다.
실패는 FAIL_OR_INCOMPLETE와 rc1로 기록하며 HOME_EVIDENCE를 보존합니다. 현재 터미널은 자식실행 래퍼로 유지합니다. 구성 변경이 없어 rollback은 필요하지 않습니다.
결과 tar.gz 및 같은 위치 .sha256를 함께 전달합니다. 실패를 우회하기 위한 네트워크/IPv6/서비스 변경을 하지 않습니다.

## 승인 조건

이 패키지로 실제 client·임시 .50/.102·UI fallback·변경창·loader 운영 계획·Lead 승인 값은 확정되지 않습니다.
기존 검토 worksheet commit227faee8d188ed29d02cf851ba51a2abd090b6d8와 앞선 capture archive dc7a6842f372c04a94ccb2054a8274a5e1233b91051e7233fd53e4331f29f218에 연결되는 추가 증거입니다.
이번 실제 호스트 실행 전 STATIC/MOCK8 및 AST/YAML/Bash/parent-retention만 확인했습니다. actual Ansible syntax/host execution NOT_RUN.
