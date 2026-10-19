# ICR — 공개 CA 결속 후 Worker03→관리 Harbor 단회 관측

**판정: 공개 CA 파일 결속은 해소됐다. 허용된 GET 명령1회는 접속 시간 초과로 끝났고, TCP/TLS/HTTP 정상 도달을 확인하지 못했다. 재시도0이다.**

## 실제 결과

| 항목 | 관측 |
|---|---|
| 실행 시각(KST) | 2026-10-19 12:38:49.400909~12:38:54.408646 |
| 관리 접근 | 기존 `svc_ansible` SSH→`sudo -n python`, uid/euid0·root·SUDO_USER=svc_ansible. 새 권한 부여 없음 |
| 대상 신원 | k8s-worker03 / machine0bb03794b5b04dc4bded6bd75d63f701 / boot2e3c5d9a-b386-4c20-8c0b-f5f7f0e10b0c. 전·GET 직전·사후 일치 |
| 출발지 준비 | ens160에10.1.93.108 할당, `.30 via .58 dev ens160 prefsrc .108` rc0. curl은 `--interface 10.1.93.108`로 고정 |
| 서버identity / 네트워크 목적지 | `https://10.1.93.54/` 검증identity, `--connect-to 10.1.93.54:443:10.250.10.30:443`로 실제 목적지.30:443 지정 |
| curl 실제 결과 | **rc28**, `Connection timed out after 5002 milliseconds`, HTTP000, num_connects0 |
| 실제 socket 메타데이터 | local_ip/remote_ip 빈 값, local_port/remote_port -1. 요청한 source/destination을 실제 연결 관측값으로 채우지 않음 |
| 시간 | time_connect0 / time_appconnect0 / time_total5.002362초 |
| TLS 해석 | ssl_verify_result0은 기록됐지만 연결·TLS handshake가 성립하지 않았으므로 **인증서/서버이름 검증 성공이 아님** |
| 수집기/접근 결과 | outer/bridge rc0 = 결과 기록·프로세스 회수 완료. curl28과 구분하며 전체 성공으로 쓰지 않음 |

curl GET 명령은1회 실행했으나 TCP 연결이 성립하지 않아 **실제 HTTP 요청 수신/본문 전달은 입증되지 않았다**. 본문은 `/dev/null`, 인증·리다이렉트·proxy·curlrc 사용 없이 수행했다. `-k`/검증 해제·CA trust import·CA 파일 수정·임시 신뢰 파일 생성·자동 retry는 없다.

## CA 접근 공백의 해소

기존 NTP_TRANSPORT_BINDING의 정확 Worker03 sudo-n 읽기 argv를 재사용했다. 공개 CA 후보는 총11개(지정 registry5개×파일2개 + 공개 anchors1개), 각 최대128KiB·전체64개 상한 안에서 확인했다. 파일유형/정확 경로/성공/오류 종류를 원본에 분리했다.

- registry CA 후보10개: **FileNotFound**. 이 root 조회에서의 정확 후보 결과이며 다른 이름/경로 전체의 부재로 확대하지 않는다.
- `/etc/pki/ca-trust/source/anchors/fds-root-ca.crt`: 정규 공개 인증서 파일1개·2004bytes·uid0·mode0600. DER SHA256 `6a75baf4dbe03ef24cce944e616384d318f7ca919cd7bd914624b4cebac06b10`이 기존 고정값과 일치했다. PEM SHA256 `20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f`이며 GET 전후 동일하다.
- PermissionError0, CA 본문 전송/출력0, `.key`/개인키·authconfig·hosts.toml·인증자료 조회0. 파일0600은 비root가 CA 내용을 읽을 수 없음을 보여 주지만 상위 디렉터리의 정확 권한까지 새로 읽어 증명한 것은 아니다. 이전 비root 후보0을 CA 부재로 소급 단정하지 않는다.

## GW·관리 접근·전송 증거의 구분

GW 신원은 **사용자12:30:58 콘솔**(mgmt-gw01 / machine6720cbd7c6494f48b7991d25f2fc1a2a / boot7144f978-8f70-43ac-98bc-6502885ee47b)이다. 이전09:41/09:43 설정 원본과 같은 boot로 연결한다. GW SSH 인증 거부는 유지하며 이번 GW 재접속0이다. GET 당시까지 GW boot가 연속 불변임을 별도 실측한 자료는 없다.

이 원본은 해당 GW 콘솔 기록 이후의 **source108로 bind한 관리 Harbor 목적지 접속 시도 결과**다. 성공한 GW 통과나 특정 방화벽 규칙 귀속, 실제 `.108→.30` 패킷 캡처를 입증하지 않는다. 시간 초과의 위치/원인(GW, 중간 경로, 목적지 ingress/서비스 등)은 이번 단일 클라이언트 결과로 확정할 수 없다. 현재 CA/실행 자료 공백은 해소했지만 **정상 흐름은 충족 증적을 얻지 못했다.**

APP/MON 건강·기존 인수 결과를 반복 시험하거나 변경하지 않았다. 서비스/방화벽/경로/프로필·패키지/신뢰 설정 변경0, Robot/Secret/API/healthz·자격증명 본문 조회0, GitHub/공통 상태 변경0이다. 전체 AC18/19 인수·업무 정상·Owner 승인으로 확대하지 않는다. 이 회차의 GET1회는 소진했으며 추가 실행을 예약하지 않았다. 중앙이 원본과 기존 네트워크 통제를 대조해 후속 판단할 자료로 반환한다.
