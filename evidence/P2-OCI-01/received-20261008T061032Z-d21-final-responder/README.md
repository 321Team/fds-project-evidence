# P2-OCI-01 / D21 — final responder raw 수신

CODEX_ASSISTED. 이번 수신 시각: 2026-10-08T15:10:32+09:00.

수신 범위는 **2026-10-03 최종 responder 로그 1개**다. RAW_INTAKE=RECEIVED_HASH_MATCH / 독립 REVIEW·MERGE=PENDING. D21 전체 증적 완비·publication·#36 Close는 미완료다. 새로운 Runtime 시험은 수행하지 않았다.

## 원본·출처·무결성

- 원본: [d21-ike-observer-20261003T042646Z.log](d21-ike-observer-20261003T042646Z.log), **8706 bytes**, SHA256 `e5f754a3d66c6fe452605ff914a6294e87aa85bf6a345ec0fadb981f18745cb0`.
- source-reported host/path: `fds-p2-oci-relay01:/home/opc/d21-ike-observer-20261003T042646Z.log`. [당시 실행 기록](https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5965536893).
- 수집 종료 후 OCI Cloud Shell SCP 수신·최종 해시는 [최종 정정 기록](https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5965598580)에 있다. 이전 `bdcd9564...`는 수집 중간 값으로 최종 기준에 사용하지 않는다.
- 이번에는 사용자가 제공한 Windows Downloads 파일을 직접 읽고 크기/SHA256을 계산했다. 기존 최종값과 일치하며 새 수집회차에 **바이트 그대로 복사**했다. Relay/Cloud Shell을 새로 조회하거나 중간 전송 경로를 다시 검증한 것은 아니다.
- 원본의 줄바꿈·checksum 경고·footer 모두 보존했다. [receipt.json](receipt.json)은 이번 수신 메타데이터이고 [SHA256SUMS](SHA256SUMS)는 이번 편입용 manifest다. 둘 다 과거 서버 생성 파일로 표시하지 않는다.
- 원본 명령 전체·명령 RC·실행 tool 버전/번들 SHA는 이번 파일에 없으므로 미확인이다. tcpdump footer가 있다는 이유로 command RC0을 추정하지 않는다. 파일명의 Z 표식과 packet timestamp를 구분하며 packet 줄 자체에는 timezone 표기가 없다.

## 원문에서 직접 확인한 범위

| 구간 | 원문 관측 | 판단 한계 |
|---|---|---|
| 첫 IKE_SA_INIT | `121.160.42.93:1011 → 10.30.10.10:isakmp` 요청과 응답, NAT detection payload 표시 | 원문 decoded label 기준. 최종 인증 성공을 뜻하지 않음 |
| 같은 교환의 IKE_AUTH | 동일 cookie pair `092c36f302eb6062→45d7762eadab794e`, `180.80.107.14:64916`와 UDP4500 NONESP-encap 요청/응답 | 공개 출발지 변경과 왕복은 관측. 암호화 payload 결과는 이 파일로 복호화/판정하지 않음 |
| 두 번째 교환 | 별도 cookie pair의 INIT 요청/응답 2개 | 이 파일에는 두 번째 AUTH 결과 없음 |
| capture footer | 6 captured / 6 received by filter / 0 dropped by kernel | 해당 capture의 카운터이며 경로 전체 무손실·명령 RC0의 증명이 아님 |

packet header 원문 행: 4, 74, 87, 90, 93, 163. `child_sa ikev2_auth`라는 tcpdump label만으로 Child SA 수립을 판정하지 않는다. 원문 outbound `bad udp cksum` 표기는 그대로 보존했으며 원인·실제 wire checksum 정상 여부는 이번 자료만으로 단정하지 않는다.

의도적인 PSK 불일치 및 `AUTHENTICATION_FAILED`, Child/IPsec SA 없음, cleanup PASS는 [당시 실행자 기록](https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5965536893)과 [cleanup 기록](https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5965598580)에 근거한 기존 보고다. 이번 responder raw 하나가 initiator 로그·cleanup 명령 원본을 대신하지 않는다.

## 결정·관련 증적과 잔여

- [D21 FINAL 결정](https://github.com/321Team/fds-project-baseline/issues/36#issuecomment-5965637169): OCI Primary NO-GO(프로젝트 적합성), AWS EC2+EIP Libreswan Relay 채택. 결정은 재심사하지 않으며 당시 AMI/설정을 현행 실행값으로 자동 소비하지 않는다.
- [PR95](https://github.com/321Team/fds-project-evidence/pull/95)는 OCI Relay 로컬 prerequisite/reboot persistence, [PR104](https://github.com/321Team/fds-project-evidence/pull/104)는 vpn-gw01 pre-VPN baseline이다. 기존 수집회차는 수정하지 않았다.
- 이번 파일로 final responder 원본 미수신 항목은 해소된다. **Phase-A UDP·initiator·cleanup 원본과 수집 provenance 보완은 별도 잔여**다. 전체 D21 publication이나 #34/#35/#37 handoff 완료를 선언하지 않는다.
- 원본 출처/범위/해시·민감정보·누락을 독립 Reviewer가 확인한 뒤 이 한정 편입의 병합 여부를 판단한다. #37 authenticated tunnel/업무 경로·G4 인수는 별도다.

## 보안·검증 경계

원문 전체를 확인하고 private-key header, GitHub/AWS token, credential assignment, Authorization header 패턴을 검사했다. 탐지0건. IKE nonce/SPI·공개/사설 주소는 패킷 관측 데이터이며 실제 PSK/private key/token 원문은 관측되지 않았다. 기존 Private 저장소 접근 범위를 유지하고 새 권한은 부여하지 않는다.

SHA256 일치는 수신 무결성 확인이며 Runtime 재시험·독립 승인·AC 충족 판정이 아니다. 원본과 과거 증적은 보존한다.
