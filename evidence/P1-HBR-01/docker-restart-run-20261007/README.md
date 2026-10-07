# P1-HBR-01 AC-04 — harbor01 Docker restart persistence 시험 실행 원본 (2026-10-07 23:12 1회)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행: 이하영(HBR Lead), ansible01 `server01_ansible` → harbor01 `svc_ansible`, 비승인 source `10.1.93.23`(server01). 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-04 인수, Docker 자동기동(automatic restart persistence) PASS, #13 종결을 뜻하지 않는다.** 자동기동은 FAIL이고 수동 복구 B를 사용했다.

## 근거
- GO: [긴급 새 1회 GO 6039725493](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6039725493) (+ [6037611737](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6037611737), [6035912853](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6035912853), A′ 6032930550, A″ 6033171191, `.23` 대체 [6039592528](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6039592528), 실행안 v2 6030202914)
- 시작 기록 [6039790104](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6039790104), 결과 기록 [6040127247](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6040127247)

## 파일 (해시는 폴더 `SHA256SUMS` 참조)
| 경로 | 시각(KST) | 내용 |
|---|---|---|
| ★ `server-originals/docker-go4-pre-20261007T231004.txt` | 23:10:05 | 시험 전 fresh START Gate(PRESTATE 5/5, A″ 대조, guard counter before, 컨테이너 10개 상세, 443, `tcp_rc=0`) |
| `server-originals/docker-go4-runner-20261007T231056.txt` | 23:12:14 | Runner `.20` TLS 시험 전 확인 `http=200 verify=0 curl_rc=0` (아래 한계 1) |
| ★ `server-originals/docker-go4-run-20261007T231221.txt` | 23:12:21~34 | **T0** `systemctl restart docker` 1회, `restart_rc=0` |
| ★ `server-originals/docker-go4-post1-20261007T231335.txt` | 23:13:35 | 앱 컨테이너 9개 `Exited (128)`, `harbor-log`만 healthy, guard·docker active, counter 이어짐 |
| ★ `server-originals/docker-go4-recoverB-20261007T231421.txt` | 23:17:21~23:21:59 | **복구 B** 시작 Gate(`getent ahosts localhost`, `tcp_1514_rc=0`)와 9개 객체 순차 시작(각 rc=0, healthy) |
| ★ `server-originals/docker-go4-pre-20261007T232344.txt` | 23:23:44 | 사후 대조(파일명은 pre지만 사후 수집): A″ PASS, 컨테이너 10개 사전과 동일 ID, healthy |
| ★ `server-originals/docker-go4-post2-20261007T232538.txt` | 23:25:38 | Runner TLS 사후 `http=200 verify=0 curl_rc=0` + guard counter before(drop 50 / 2600 B) |
| ★ `server-originals/docker-go4-post3-20261007T232653.txt` | 23:26:54 | guard counter after (drop **53 / 2756 B**) |
| ★ `server-originals/docker-go4-verify-20261007T232731.txt` | 23:27:31 | 원 verifier `rc=2` (DOCKER-FORWARD 마지막 ACCEPT 2줄 순서), 15:53 회차와 같은 파일 해시 |
| `server-originals/docker-go3-pre-20261007T224937.txt` | 22:49:38 | 이전 창(23:00) 준비 Gate. 23:00 창은 미실행으로 종료, 참고용 |
| `observations/docker-go3-pre-20261007T224842.txt` | 22:48:43 | **1차 시도 실패.** ssh 키 미지정으로 harbor01 `UNREACHABLE`, harbor01에 명령 미전달. Runner TLS 줄만 있음 |
| `observations/ansible01-hash-list.local.txt` | 23:3x | ansible01에서 파일을 한 폴더로 복사한 뒤 만든 해시 목록 |
| `scripts/ac04-gate-v2.py`, `scripts/ac04-recoverB.sh` | | 실행한 Gate 수집·복구 B 스크립트 |

## 결과 (원본 기준, 항목별 분리)
- **T0 23:12:21** 재시작 1회, `restart_rc=0`. T0+1(23:13:35): 앱 컨테이너 9개 `Exited (128)`, `harbor-log`만 healthy, 443 listener 없음. T0+5(23:17:21)까지 그대로 → **자동기동 FAIL, 복구 B 진입.**
- **복구 B:** harbor-db → redis → registry → registryctl → harbor-core → harbor-portal → harbor-jobservice → trivy-adapter → nginx 순서, 각 `rc=0`·healthy(약 31초), **23:21:59 완료.** 컨테이너 10개가 시험 전과 같은 ID·image·mount·port로 `running/healthy`. daemon 재restart·guard unit restart·컨테이너 재생성 없음. **수동 복구를 사용했으므로 automatic restart persistence PASS가 아니다.**
- **guard 유지 PASS:** 재시작 중 counter가 초기화되지 않고 이어짐(승인 accept 62909→63171→63285, 비승인 drop 50 유지), guard 기동 시각 10/6 10:04:40 그대로, A″ 대조 PASS, FORWARD·DOCKER-USER·NAT exact.
- **서비스·TLS:** 443 listener 복구, Runner TLS 사후 `200/verify0/rc0`(23:25:38).
- **fresh deny PASS:** `.23` 23:25:50 `curl.exe --connect-timeout 5` → rc=28, 비승인 IPv4 drop **50→53 packets(+3), 2600→2756 B(+156)**.
- **원 verifier:** `rc=2` FAIL(order) 이력 유지. A″ 대조는 별도 PASS. 전체 정렬 비교로 PASS를 만들지 않았다.
- 원인 가설(미확정): 앱 컨테이너의 syslog 드라이버가 `tcp://localhost:1514`에 접속하려는데 `harbor-log`가 늦게 올라와 exit 128. 이 시험으로 확정하지 않았다.

## 한계 (숨기지 않음)
1. **Runner 시험 전 TLS 원본 불일치.** 시작 기록에는 23:10:56 수집분(sha256 `871c505fcb2f5b30c2d9ccc214fd31ec506ef353fef0d42048e7f26d0985d8d3`)을 적었으나, 같은 파일명(`…T231056.txt`)의 현재 내용은 **23:12:14**의 재확인 결과(51바이트, `200/verify0/rc0`)이고 해시가 다르다. 즉 같은 이름의 파일이 덮어써졌고 **23:10:56 수집 원본은 보존되지 않았다.** 23:10:56 값은 실행자 터미널에서 본 출력(`http=200 verify=0 curl_rc=0`)으로만 남아 있다. 두 확인 모두 T0(23:12:21) 이전이다.
2. 원본은 터미널·ansible 출력이며 서버 측 봉인이 없다. ansible01에서 한 폴더로 복사·압축 후 공유 폴더를 거쳐 받았고 압축 안 13개 해시가 사본과 13/13 일치했다. 터미널에서 직접 본 해시와는 위 1번 파일만 다르다.
3. 공지 전송 시각·연락 경로·#19/APP 실제 종료 시각의 숫자는 이 폴더에 원본이 없다(실행자 구두 확인).
4. 원인 분석, 로깅 의존 순서 개선, 영구 verifier 변경은 이 폴더 범위가 아니다.
5. `docker-go4-pre-…T232344.txt`는 파일명이 pre이지만 사후 수집이다(사전 Gate 스크립트를 다시 실행한 것).
