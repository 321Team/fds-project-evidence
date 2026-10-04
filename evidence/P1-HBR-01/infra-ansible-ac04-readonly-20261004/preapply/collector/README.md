# FDS HBR AC04 PR63 Preapply Readonly v1.0

목적: 승인된 badbe29440916ec3ec79da8fc81722c2e6c4e75b의 기존 discovery/precheck를 실행하고 supplemental NIC/주소/경로/443 연결/nft loader 정보를 읽기 수집한다. Phase1만 대상으로 한다.

## 실행 전제

- ansible01의 server01_ansible 일반계정, HOME=/home/server01_ansible.
- 기존 ~/p1-ans-01의 승인된 origin, gh 인증, operational Ansible2.16.19.
- 기존 ~/.config/ansible/p1-ans-01.env 및 기존 SSH key/known_hosts/harbor01 svc_ansible 연결.
- 기존 inventory/hbr.yml, strict host checking 유지, harbor01 정확 hostname/IP 확인.
- harbor01의 기존 Ansible become 권한 사용. 새 계정/권한/SSH key/known_hosts 등록 없음.
- 워킹트리 checkout/switch/merge 없음. 기존 repo에 git fetch만 하고 새 private stage로 git archive 추출.
- 코드 HEAD가 바뀌면 STOP; 새 source 검증/독립 리뷰 범위 확인 후 재패키징.
- 패키지를 WinSCP 등 기존 경로로 ansible01 홈에 반입하고 외부 ZIP SHA256을 확인한 뒤 child Bash로 bash run.sh 실행. source run.sh 금지.
- 부모 터미널에 set -e/-u/pipefail을 설정하지 않는다. 기존 env는 child Bash 안에서만 source한다.

## 수집 범위

기존 discovery/precheck + 모든 NIC/IP(v4/v6)/라우트, listener/현재443 연결, 전체 nft numeric ruleset, iptables NAT, nftables unit의 상태·경로·순서·시작 명령, Docker 컨테이너의 name/ID/Ports/Networks만 조회한다. Docker Config/Env와 secret/key 내용을 수집하지 않는다.

고정 nft 설정 경로의 hash와 include/flush/table 지시행을 수집한다. 임의 include를 실행하거나 전체 unit/config 내용을 공개하지 않는다. include closure/custom unit/drop-in/경쟁 loader는 원본 수신 후 별도 검토가 필요하다. conntrack와 ip6tables가 없으면 optional_unavailable로 남긴다.

Ansible 실행에는 통상 임시 파일이 필요하다. firewall/service/컨테이너/호스트 설정 적용, nft -f, reload/restart, credential/token 발급, traffic probe/packet capture, system engine 전환은 수행하지 않는다.

## 정상·실패 판정

- 정상 수집: STATUS=PREAPPLY_READONLY_CAPTURED_REVIEW_REQUIRED / PREAPPLY_EXIT_CODE=0.
- 이는 APPLIED/READY/AC04 PASS가 아니다. 현재 연결 한 번의 관측으로 모든 실제 client 또는 모든 ingress 경로 부재를 증명하지 않는다.
- essential command/identity/HEAD/engine/contract/precheck 실패: STOP 및 FAIL_OR_INCOMPLETE, nonzero rc. optional unavailable 항목과 manual review 항목은 숨기지 않는다.
- 실패하면 apply/서비스 restart/권한 확장/증적 삭제로 우회하지 말고 생성된 RESULT/log/archive를 보존하여 전달한다. 운영 변경이 없어 rollback 적용 명령을 실행하지 않는다.
- HOME_EVIDENCE와 같은 경로의 .sha256 두 파일을 반출. 환경파일·개인 SSH key·source working directory 전체는 반출하지 않는다.
- 자동 정리하지 않고 생성 stage/증적 보존. 검수 후 폐기 여부는 별도 운영 절차로 처리한다.

## 후속 필수 수동 확인

1. ens160/10.1.93.54 외 NIC/address/VIP/IPv6 proxy/published443 우회 경로 검토. 추가경로는 scope/design STOP.
2. 실제 client 목록(현재 idle consumer 포함)과 .50/.102 예외 필요성·제거 추적 reconfirm.
3. nftables/service/include/경쟁 loader flush 또는 guard wipe 가능성 검토.
4. control01 실제 UI login/fallback 증적.
5. P1-HA Drain/Harbor 재생성/monitoring 변경과 비충돌 change window 및 impact notice.
6. reviewer가 유지한 Draft/merge HOLD와 명시적 Runtime attestations. read-only 수집으로 승인값을 자동 주입하지 않는다.
7. 승인된 Apply 이후에 positive/negative/pull/persistence와 Lead 인수.

## 검증 수준

동봉 VALIDATION.json은 assistant static/mock 확인 결과다. 실제 Ansible syntax-check·ansible01/harbor01 실행은 사용자 현장 실행 전 NOT_RUN. 모의 수집 성공을 실제 read-only 확인으로 승격하지 않는다.

