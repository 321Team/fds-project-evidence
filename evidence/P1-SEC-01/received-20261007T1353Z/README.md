# P1-SEC-01 — IF-12B(CP02·CP03 → Worker:10250) 6경로 관측과 AC-04 edge 12행 수집 원본, 2026-10-07 22시 창

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 2026-10-07 22:13~22:15 KST에 승인된 한 회차로 실행한 ① IF-12B 접속 관측(2곳)과 ② AC-04 방식 B 수집기(edge01) 원본이다. **이 폴더는 AC-04·IF-12B의 충족·PASS를 주장하지 않는다.** 판정은 Review Owner 몫이다. 모든 시험은 읽기 전용 접속 시도이며 서버 설정·정책·Pod는 바꾸지 않았다.

## 출처와 수신
| 항목 | 값 |
|---|---|
| 승인 | Review Owner 판정 [6035749738](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6035749738)(①② GO), 재확인 [6035875369](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6035875369), 창 경계 [6037581049](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6037581049)(종료 상한 22:25). 이 승인은 **한 회차**다 |
| ① 스크립트 | `scripts/if12b-cp-to-worker-10250-v1.sh` rev `v1.1-20261007`, SHA-256 `55eb49109019d5b86072910bd31806ed2bba0da07e4d00c4c6948acf5703613b`(승인값과 일치, 두 아카이브의 `00-environment.txt` `script_sha256`과 같음). 본문은 [#19 6035403083](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6035403083)에 게시했다. 이 스크립트는 저장소 PR이 아니라 #19 코멘트로 검토·승인된 파일이다 |
| ② 수집기 | `scripts/collect-ac04-extra-negative.sh` rev `v3-20261005`, SHA-256 `4ba0ac9ad98c9a1dce7b4cf94ec7632ac0408aafbf6a7a934534cc142da699d0`(`infra-kubernetes` main의 같은 blob, 두 아카이브의 `script_sha256`과 같음). 10/6 [evidence#119](https://github.com/321Team/fds-project-evidence/pull/119)와 같은 파일 |
| 실행 | 이하영(P1-SEC-01 Lead). ansible01에서 `scp`로 ①을 control02(`server03`)·control03(`server04`)에 보내 `ssh`로 각 1회 실행, ②는 edge01(`server08`)의 기존 `~/p1-sec01-ac04-extra-negative/`에서 실행. 명령 안내·수신 검증·편입 정리는 Claude Code 보조 |
| 전달 경로 | 각 서버 홈 → ansible01 `scp` → 사용자가 zip으로 공유 폴더에 올려 세션에 전달 → 압축 해제 후 해시 재확인. 첫 zip(`187fb300…`)에는 ② 1차 실행이 빠져 있어 다시 가져온 두 번째 zip(`p1-sec01-1007-evidence-v2.zip`, SHA-256 `92b51223dc1c13b4efbdae961e809da087a88abcd202cf9b660fcda53b270153`)으로 4개 묶음을 모두 확인했다 |
| 수신 시각 | 2026-10-07 22:5x KST |

| 묶음 | 아카이브 SHA-256 | 수집(UTC) | 결과 |
|---|---|---|---|
| ① control02 | `e18e6828de380617f577bbda46c6b622e5ea2b5a36f8803b3ebc97c519c5d06a` | 13:13:01Z (22:13:01 KST) | `COLLECTOR_STATUS=COMPLETE EXIT_CODE=0` |
| ① control03 | `15cd0703f06ca4663c1ca800be72b84477bc59df71ceab33a408e054b0a4bb41` | 13:13:58Z (22:13:58 KST) | `COMPLETE EXIT_CODE=0` |
| ② edge01 **1차** `…T131445Z.ey8HjG` | `885be51dd9b2c161b44d38f6036d4fca045bb3dd7c1fcca16ced470f45b7190c` | 13:14:45Z (22:14:45 KST) | `COMPLETE`, `AC_VERDICT=BLOCKED_VALID`, `EXIT_CODE=0` |
| ② edge01 **2차** `…T131507Z.NXE3sE` | `ff643c30e423d4ed3cd4cae386509536bf3faeb44aeff068f932773baded7d60` | 13:15:07Z (22:15:07 KST) | `COMPLETE`, `AC_VERDICT=BLOCKED_VALID`, `EXIT_CODE=0` |

## 수신 검증
- 아카이브 4개의 바이트 SHA-256 = 서버 sidecar의 값(4/4 일치). sidecar는 상대 파일명만 적고 있어 `sha256sum -c`로 검증할 수 있다.
- 각 아카이브 안 폴더의 `SHA256SUMS`를 풀어서 검증한 결과 모든 항목 OK(4/4 폴더, 불일치 0).
- 비밀정보 패턴 검색(`password|secret=|token=|BEGIN … KEY|bearer|authorization:`) 일치 0건(폴더·아카이브 내용 모두). Secret·토큰·키 자료는 증적에 없다.
- 서버 설정 사본·snapshot·개인키는 이 시험에 없다.

## 관측값 (원본 보존 — 판정 아님)
### ① IF-12B — 각 CP에서 Worker 3대 `:10250`, 행당 1회, 재시도 없음
| 출발 | 대상 | route src | TCP(`/dev/tcp`, 5초) | TLS(`openssl s_client -brief`, 8초) |
|---|---|---|---|---|
| control02 | .105 / .107 / .108 | 모두 `10.1.93.103` | 3행 모두 rc0 `TCP_CONNECTED` | 3행 모두 rc0, `Protocol version: TLSv1.3` 관측 |
| control03 | .105 / .107 / .108 | 모두 `10.1.93.104` | 3행 모두 rc0 `TCP_CONNECTED` | 3행 모두 rc0, `Protocol version: TLSv1.3` 관측 |

- 각 행 폴더에 `cmd.txt`(실행한 route·tcp·tls 명령 문자열), `route.*`, `tcp.*`, `tls.*`, `times.txt`가 있다. TCP와 TLS는 별도 명령·별도 원본이다.
- TLS 출력에 상대가 낸 인증서의 주체(`depth=0 O=system:nodes, CN=system:node:k8s-worker01/02/03`, .105/.107/.108 순)가 나온다. 이 시험은 CA 번들을 주지 않아 `verify error:num=20/21`(발급자를 찾지 못함)이 모든 행에 출력되었다. 즉 **인증서 검증·kubelet 인증·API 호출은 하지 않았고, TLS 핸드셰이크(프로토콜 버전)가 시작·진행되었음만 관측했다.** peer 신원 검증으로 표현하지 않는다.

### ② AC-04 방식 B — edge01 `10.1.93.50` → Worker 3대, 12행
두 실행의 `results.tsv`가 같은 형태다.
| 행 | 기대 | 1차 | 2차 |
|---|---|---|---|
| 대조 `:30080` × 3 (.105/.107/.108) | CONNECTED | CONNECTED ×3 | CONNECTED ×3 |
| 차단 기대 `:9100`·`:9101`·`:10250` × 3 Worker = 9행 | TIMEOUT | TIMEOUT ×9 (약 3.0초) | TIMEOUT ×9 (약 3.0초) |
| 수집기 요약 | | `rows=12/12 incomplete_reasons=0`, `BLOCKED_VALID valid_block=9 fail=0 inconclusive=0` | 동일 |
- 10/6 [evidence#119](https://github.com/321Team/fds-project-evidence/pull/119)에서 worker01(.105)·worker03(.108) 대조(`:30080`)가 즉시 거부되어 해당 6행이 `INCONCLUSIVE`였던 것과 달리, 이번에는 세 Worker 모두 대조가 CONNECTED였다. 이재환 님의 APP 분산 적용(10/7 14:50~14:53, [evidence#136](https://github.com/321Team/fds-project-evidence/pull/136)·[#138](https://github.com/321Team/fds-project-evidence/pull/138))이 앞서 있었고, 이번 시험 전 EndpointSlice ready=true가 worker01·02·03에 각 1개였다(아래 한계의 콘솔 확인).
- `AC_VERDICT=BLOCKED_VALID`는 수집기 입력일 뿐 AC 판정이 아니다.

## 기록상 편차와 한계 (은닉 아님)
1. **② 중복 실행 2회(승인은 1회):** edge01에서 같은 수집기가 22초 간격으로 2번 실행되었다(22:14:45, 22:15:07 KST). 실행자가 ssh 응답이 느려 연결이 안 된 줄 알고 같은 명령을 한 번 더 입력했는데, 첫 입력도 실행 중이었다고 설명했다(첫 입력 때는 암호 입력 뒤 출력이 화면에 보이지 않았음). 의도한 재시도가 아니다. 서버 변경은 없다(읽기 전용 접속 시도). **두 결과가 같으며(12/12, `BLOCKED_VALID`, FAIL 0, INCONCLUSIVE 0), 둘 다 삭제하지 않고 편입했다.** 어느 실행을 인용할지, 승인 범위 초과를 어떻게 처리할지는 Review Owner 판단이다. [#19 6038826789](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6038826789) §4에 같은 내용을 먼저 알렸다.
2. **파일이 아닌 콘솔 확인:** 시작 전 ① 노드 6/6 `Ready`·Worker별 ready endpoint 1·1·1(`ready=true`), ② 각 CP의 `ip -4 route get` 3행(출발 주소 `.103`/`.104`, rc0)과 스크립트 해시 대조는 **콘솔 출력**으로만 확인했고 별도 파일 원본은 없다. route 조회는 아카이브의 `route.stdout`에 실행 시점 값이 있고, 스크립트 해시는 `00-environment.txt`의 `script_sha256`에 있다. 노드·endpoint 확인 화면은 편입하지 않았다.
3. **TIMEOUT은 차단 주체를 구분하지 않는다.** Calico 정책과 상위 방화벽 중 무엇이 막았는지 이 수집기는 가르지 못한다(수집기 README 한계). 규칙 대응은 [evidence#122](https://github.com/321Team/fds-project-evidence/pull/122)·[#131](https://github.com/321Team/fds-project-evidence/pull/131)의 몫이다.
4. **TCP 성공은 TCP 연결만 뜻한다.** TLS는 핸드셰이크 시작 관측까지이며 인증서 검증·kubelet 인증·실제 `logs/exec` 경로는 확인하지 않았다. CP→control 노드 `:10250`과 `:9100` 대조는 이번 범위가 아니다(Review Owner가 범위에서 제외).
5. **시점 한 번의 관측**이다. ①은 이번 실행 전에 `bash -n`과 PATH 스텁 시험만 거쳤고 실제 서버에서 실행한 적이 없었다. 그 사실은 [#19 6035267679](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6035267679)에 알렸다.
6. edge01 `source_ips`에 `10.42.0.0`·`10.42.0.1`이 함께 기록된다. 시험에 쓴 출발 주소는 `10.1.93.50`이다(10/6 증적과 같은 현상으로 edge01의 기존 k3s 인터페이스 주소로 보이며 이 수집에서는 확인하지 않았다).

## AC와의 대응 (판정이 아니라 연결)
| #19 항목 | 관련 파일 |
|---|---|
| IF-12B CP02·CP03 출발 미시험 행 | ① 두 아카이브의 `99-summary-provisional.txt`, 행별 `tcp.*`·`tls.*`·`route.*`·`cmd.txt`·`times.txt` |
| AC-04 edge→worker01·03 부족 6행(10/6 INCONCLUSIVE) | ② 두 아카이브의 `results.tsv`, `verdict-rows.tsv`, `99-summary-provisional.txt`, `route-*.{stdout,stderr,rc}` |
| ② 중복 실행 | `…T131445Z.ey8HjG`(1차)와 `…T131507Z.NXE3sE`(2차)의 `.completion.txt` 두 개 |

AI usage: CLAUDE_ASSISTED (수신 검증·정리 보조). 판단은 이하영.
