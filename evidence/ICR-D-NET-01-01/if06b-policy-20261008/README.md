# IF-06B gateway 정책 원본 — 2026-10-08 KST

책임 baseline #14/GWONUK 생산 → #17/MON 소비·재판정, #19 공백 보완.
사용자가 기존 비밀번호 SSH/sudo로 인증하고 고정 wrapper를 실행했다.
CODEX_ASSISTED가 코드 준비·ansible01 원본 수신·검증·정책 검토를 수행했다.

## 실행과 출처

- 실행 코드 infra-kubernetes #72 `eabf69948badf051bb290dda57eb0b1898c96041`.
  collector SHA `d8c6fdeffbf2bf9585306b7f20118277bc99f757d31e139e7e8b9e9bb7440f4b`.
- 기존 경로 PC → ansible01/server01_ansible → server01_mgmt-gw@10.1.93.58 + sudo/root.
  계정·키·권한·SSH/방화벽 설정 변경 없음. 암호는 사용자 TTY 입력이며 증적에 없다.
- `receipt.json` 명령 시각 **00:54:41~43 KST**, 호스트 mgmt-gw01/uid0.
- 원본 `/root/if06b-policy-1x2k0nr2`.
  사용자 회수 `/home/server01_ansible/if06b-receipt.s9JlV4yW`.
  22개 조회 rc0, collector rc0/remote wrapper rc0, 전후 설정 원문 동일.
- capture.tar.gz SHA `01760bbd0ac821d9ea422fdb105964640ebefb4209fbbdd6d0509489ea1d7296`.
  gateway에서 생성된 sidecar → ansible01 수신 확인 → PC 수신 bytes 일치.
  내부 SHA256SUMS **67/67** 일치. 수신 collector bytes와 receipt의 source SHA 일치.
- executed-*는 실제 실행한 구버전 source/transport wrapper이다. 수정 후보로 바꿔치기하지 않았다.
  remote-command.sh는 실행 중 생성된 실제 gateway 실행/회수 명령이다.

## 현재 설정 검토

1. runtime/permanent `if06b-p2m`: priority -1, target DROP, physical→management,
   masquerade no, rich rule는 `.108/32 → 10.250.10.30/32 tcp443 accept` 1개다.
2. active interface는 physical=ens160, management=ens224. nft forward jump handle619가
   해당 인터페이스 쌍을 if06b chain으로 보내며 allow handle618, terminal DROP handle606이 있다.
3. 현재 일반 신규 non-DNAT flow의 tcp8443은 해당 allow에 매칭되지 않아 위 DROP 경로다.
   상위 established/related 및 DNAT 예외가 있으므로 모든 상태의 flow를 일반화하지 않는다.
4. nft 전체는 inet firewalld table1개. IF06B NAT subchain은 비어 있고, 관측된 masquerade
   handle423은 management source10.250.10.0/24의 내부대역 외 목적지에 한정된다.
   `.108 → .30`에 적용되는 SNAT/masquerade 규칙은 관측되지 않았다.
   gateway 전체 NAT가 없다는 뜻은 아니다. 내부대역 set 정의도 원본에 포함된다.
5. ip_forward=1, 두 연결 대역과 기본 route가 기록됐다.

**정책 원본 부재 공백은 해소**, 현재 gateway 설정 범위의 technical review는 수용 가능하다.
이번 수집은 패킷을 발생시키지 않았고 과거10/6 8443 시험 시점의 drop counter/pcap을
생성하지 않았다. 따라서 과거 8443 차단 귀속, 당시 시작 gate·추가 실행 이력, source
preservation/IF-06B 전체 AC는 자동 PASS가 아니다. 기존 evidence#122와 함께 #17에서 재판정한다.

## 전송 도구 결함과 수정 경계

사용자 콘솔에서 `Master refused session request` 후 별도 인증이 반복됐다.
초기 wrapper의 `ControlMaster=yes`와 `-M` 중복 지정이 원인이다.
실제 ansible01의 ssh -G 진단: 기존 `ask`, -M 제거본 `true`.
새 수정본은 중복 -M 제거 및 후속 BatchMode=yes로 재사용 실패 때 반복 prompt 대신 STOP한다.
소스 PR72에 반영했으나 이번 증적의 executed wrapper는 초기본 그대로 보존한다.
수집 재실행 없음. 전체 수정 wrapper Runtime은 NOT_RUN이다.

기존 master의 -O exit도 confirmation 거부로 실패했다. 완료된 수집 전용 PID15180의
소유자/정확한 socket argv를 확인하고 pidfd로 해당 프로세스만 TERM했다.
이후 PID와 socket 부재 확인. 서버 SSH 설정이나 다른 연결을 변경하지 않았다.
원본·receipt 디렉터리는 보존한다. 진단 stdout/stderr/rc를 함께 편입한다.

## 상태

LIVE_READONLY_CAPTURE=COMPLETE / HASH=VERIFIED / CURRENT_POLICY_TECHNICAL_REVIEW=ACCEPT_WITH_SCOPE.
INDEPENDENT_EVIDENCE_REVIEW=PENDING / HISTORICAL_8443_ATTRIBUTION=NOT_ESTABLISHED.
Backup/Probe RUN·AC 인수·Issue/Phase1 Close 승인이 아니다.
