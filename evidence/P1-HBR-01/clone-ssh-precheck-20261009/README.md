# 격리 Harbor clone SSH 사전 조회 및 CentOS 파서 검증 증적

CODEX_ASSISTED. 책임 baseline#13. **수집·오프라인 검수 완료, 편입 독립 리뷰 미완료**.
리뷰는 사용자 결정에 따라 **2026-10-09 09:00 KST 이후**에 진행한다.

## 판정과 적용 범위

기존 SSH/NM/firewall 정보를 수집하고, code#21 승인 renderer를 사용한 CentOS의
SSH/nft/NM/firewalld 문법·설정 해석을 확인했다. **파서 범위 PASS**이며 실제 설치,
SSH 인증/권한/패킷 차단/만료/rollback은 NOT_RUN이다. A3 STOP/claim 및 AC/Issue/Phase1
Close 상태를 바꾸지 않는다. 이후 code#22에서 추가한 .link/udev 동작은 이 검증에 없다.

| 회차 (KST) | 보존 원본 | 실제 결과 |
|---|---|---|
| 10/08 23:29:11–12 사전 조회 | inventory, 30항목 | hbrctl 계정 조회 rc2/빈 출력 외 조회 rc0. 기존 운영 NM 자동 연결, wildcard SSH·9090, forwarding 등 연결 전 위험을 확인. 준비 완료/접속 허용을 뜻하지 않음. |
| 10/09 00:35:28 대상 파서 | target-syntax, SUMMARY 1항목 | SSH baseline/후보 결합 -t 및 4문맥, nft --check rc0. NM은 옵션 미확인으로 실행 생략, firewalld rc0이나 stderr544bytes 경고. 최초 상태 유지. |
| 10/09 00:49:10 보충 | syntax-supplement, 2항목 | NM --help-all 지원 확인 후 private --print-config rc0/stderr0, no-auto-default/managed=0 해석 확인. private firewalld.conf를 포함한 검사 rc0/stderr0. ISSUES/WARNINGS 없음. |

대상은 hostname harbor01, BIOS UUID `564d9e38-f024-efe2-b68f-137a5047788a`의
`D:\FDS-Isolated-Lab\harbor01-20261008\harbor01-test.vmx` 작업 복제본이다.
사용자 GWONUK가 server08 VM 콘솔에서 sudo로 stage-local.sh를 실행했고, 공유 경로에서
해시 확인된 local 복사본을 사용했다. 수집기 자체는 순수 조회/사설 작업폴더·결과 쓰기만
수행한다. host HGFS 전달 설정의 열기·닫기는 별도 기록이며 모든 시스템에 쓰기가 없었다는
주장은 아니다. 수집기/전달 helper는 Lead 자체 검수이며 **REVIEW=NOT PERFORMED (Pre-check)**.
code#21 renderer의 독립 승인과 helper의 검토 단계를 구분한다.

## 출처와 바이트 결속

- 승인 renderer source HEAD `69cfb6a684c061dbb78d37f507781a1188a3d3c8`, code#21 merge
  `d960540ee6542e28427880c8f69dd45ed948cf88`. renderer SHA
  `7d488af9114f974186acfe1cf57d9524d859ed56227fac48914f8b9dbe265384`.
- inventory manifest `e588833f9c7dc339c1ef8bb812a4149754887513b5881e60665c13d1291130b6`.
- target-syntax manifest `a190335aa82ea7f4c2bfbbee18a67ed89479ebede7146c6cdd0bb45ca91f8df8`.
- syntax-supplement manifest `42550ee78ec95d8c9755f2bde19d20d1c8b58e5e69abe2fe6dc1e0e26f5d5528`.
- `source/`는 실제 전달 폴더의 collector/renderer/입력/기존 manifest/stage를 원래 바이트로
  복사했다. 각 collector SHA는 회수 JSON 및 전달 기록과 일치한다. **이력 보존용으로 재실행 금지**.
  원본의 `NOT_RUN` 표시는 전달 준비 당시 상태이므로 고치지 않았으며 실행 여부는 회수본으로 판단한다.
- `analysis/receipt-verification.json`은 10/09 01:27 KST 오프라인 대조 기록이며 guest가 생성한
  실행 결과가 아니다. `analysis/verify.py`로 원manifest/수집기/선별 stdout 결속을 재검사한다.
- fixture ens160/MAC/공개키는 합성이며 실제 할당·배포·인증 증적이 아니다. 신규 실제 관리
  개인키·공개키 설치 후보 및 code#22 실행 후보는 이 PR에 포함하지 않는다.

## 원문 미수신과 해석 한계

원본 private는 `/root/hbr-ssh-precheck-mtx_g6am`, `/root/hbr-ssh-target-syntax-i7ref62c`,
`/root/hbr-ssh-supplement-o1kjeto8`이다. SSH 전체 유효 설정, 복사한 설정 원문,
firewalld raw stderr 등은 guest private에 유지했다. 파서 SUMMARY의 원문 SHA/크기/rc 및
선별값을 검토한 것이며 반출하지 않은 전체 원문을 직접 확인했다고 주장하지 않는다.

NM 보충의 `match-device=interface-name:nbft*` 줄은 기존 다른 섹션에서 추출된 값이다.
`[device-hbr-mgmt] match-device=type:ethernet managed=0` 결속과 구별한다. 실제 NIC의
unmanaged 여부 및 자동 연결 차단은 아직 실측하지 않았다. firewalld 원경고는 private
main config 누락 경로 언급을 기존 stderr SHA에 결속해 확인했고, 보충 검사 결과로만 해소한다.

## 공유 폐쇄 및 이후 호스트 상태

host/에는 23:30:03, 00:36:56, 00:50:42 KST의 공유 제거/HGFS disable 성공과
NIC FALSE/공유0 기록을 보존했다. guest 마지막 mount 해제는 별도 로그가 없어 미확인이다.
screenshots/는 사용자 콘솔 제출 자료이며 서버 원문 대신 사용하지 않는다.

`host/ssh-vmnet2-applied-check.json`은 **그 이후 01:08:16 KST**의 Windows 조회다.
VMnet2 Up/192.168.253.1/24, IPv4 DHCP off, IPv4/IPv6 forwarding Disabled, 기본경로 없음,
IPv4 DNS 없음, ICS/RemoteAccess Stopped, IPEnableRouter0, clone NIC FALSE를 확인했다.
IPv6 기본 DNS·링크 로컬 주소 등은 남아 있으며 전체 IPv6 패킷 차단 성공을 뜻하지 않는다.
이 파일의 Get-NetNat 빈 결과만으로 VMware NAT 부재 전체를 증명하지 않는다. 별도 사용자가
제시한 편집기 설정과 함께 해석하며 당시 화면은 이 PR의 새 서버 원본으로 만들지 않았다.

## 검토 연결과 다음 단계

- [파서 결과 종합](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6063745150)
- [VMnet 반영 및 code#22 준비](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6064198596)
- [09시 이후 리뷰 결정](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6064331892)
- [code#22](https://github.com/321Team/infra-harbor-trivy/pull/22): MAC/이름 결속 변경의 별도 리뷰.

증적 편입 승인과 소스 승인·실제 설치 GO는 각각 구분한다. 오전 실행에는 05:14:33 KST
만료의 기존 후보를 재사용하지 않고, 당시 승인 소스/실행 창에 맞춰 재생성·봉인한다.
CentOS udev/설정 경로/선행 규칙, hotplug 후 정확한 이름·MAC, 실제 인증/차단/만료/복구는
후속 단계로 남긴다. 이 증적 준비 중 서버 명령·NIC·설치·A3 재시험을 실행하지 않았다.
