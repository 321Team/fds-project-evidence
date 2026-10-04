# P1-HBR-01 AC-04 — harbor01 방화벽 guard 적용(Runtime) 원본 편입 (2026-10-04)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행: 이하영(HBR Lead), ansible01 `server01_ansible`. 원본 전사·정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다. 적용 전 기준선(사전 점검·도달성)과 TLS 시험은 별도 PR [#108](https://github.com/321Team/fds-project-evidence/pull/108) 회차에 있다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **AC-04는 NOT PASSED**이며 이 편입은 AC PASS 선언이 아니다.

## 시간 순서 (사실 그대로)

| 시각(KST) | 사건 |
|---|---|
| 20:02:28~20:02:44 | 병합 main `09264ae`로 apply 1차 시도 → **`APPLY_RC=2`**(`apply.yml`이 쓰는 `hbr_ac04_filter_save`·`hbr_ac04_nat_save`를 apply 안에서 register하지 않아 `is undefined`). 변경 2건(상태 폴더 생성, `original-public.xml` 복사)뿐이며 방화벽 무변경 |
| ~20:04 | harbor01 읽기 전용 확인: guard 없음, `443/tcp` 유지, rich rule 없음, health 200 |
| 20:09 | 수정 PR infra-ansible#68 올림 → 20:26 이권욱 exact-HEAD `efe82dda` APPROVED → **20:53:55 병합**(`e1c4458`, CI는 queued 상태에서 병합, 21:25:49 CI success는 사후) |
| 21:10 | `e1c4458` 정적 검증(13/13)·사전 점검 PASS(화면 출력) |
| **21:32:34~21:33:20** | **apply 2차 실행, `APPLY_RC=0`(`ok=162 changed=12 failed=0`)** |
| 21:34:05 | verify: `CONFIG_PASS_RUNTIME_TRAFFIC_TESTS_PENDING`(`ok=67 changed=0`) |
| **21:37:00** | 이권욱 `e1c4458` 조건부 GO 코멘트([5979990693](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5979990693)) — **적용(21:32~21:33)보다 늦게 게시**됨. 새 SHA GO를 받지 못한 상태에서 Lead 판단으로 먼저 진행했다 |
| 21:35:32 | Runner positive, 이후 harbor01 서비스·접속 로그 관측(아래) |

## 파일

### `server-originals/` — ansible01 서버 원본 (텍스트 전사, 서버 해시와 **바이트 동일** 확인)
| 파일 | 크기 | 서버 SHA256 | 내용 |
|---|---|---|---|
| `ac04-apply-20261004T200228.txt` | 6,790 | `74f467cec56732fd3c2cb1fa866868baa127d49522c57ed611cadf2378783f3d` | 1차 시도(실패) 전체 출력 |
| `ac04-apply2-20261004T213234.txt` | 18,485 | `0195c4f8dac226389614eda393ffab67375ccfc50f35fae28ec697077f77ffd4` | **2차 적용(성공) 전체 출력** |
| `ac04-verify-20261004T213405.txt` | 8,589 | `6d89c5021eb6346d4ae8d12ca81aaa8077e92ee69f39536f03e537b3f5f0e945` | verify 전체 출력 |
| `ac04-main-static-20261004T195510.txt` | 2,108 | `52bdd24071fd9dafd65d4c1e5da91f25230a05b09615fb8a0112d36cd8f82aa8` | `09264ae` 정적 검증(11/11) |
| `ac04-e1c4458-static-20261004T211015.txt` | 2,475 | `de1df7d3c5ce82d9bf3393005cf1bf5253cd47976ed657e9ff9586065a33d673` | `e1c4458` 정적 검증(13/13, harbor01 `iptables-save` rc0) |

### `observations/` — 적용 후 관측 (터미널 출력 전사, 서버 해시 대조 없음)
| 파일 | 내용 |
|---|---|
| `runner-after-20261004T213532.txt` | Runner `10.250.10.20`(허용) 21:35:32 `TCP_443=OPEN`, `health_http=200` |
| `harbor01-service-after.txt` | `harbor_health=200`, `table inet p1_hbr_ac04` 존재, docker·guard `active`(시각 21:3x, 정확한 시각 미기록) |
| `pc-browser-after.txt` | 이하영 PC(비허용) 브라우저 접속 안 됨(구두 보고, 스크린샷·출발지 IP 미기록, 시각 미기록) |
| `harbor01-proxylog-after-20261004T213636.txt` / `…T214505.txt` | `.26/.29/.30` 마지막 기록이 21:31:52(적용 시작 21:32:34 이전)이며 21:45:05에도 새 기록 없음 |
| `harbor01-proxylog-sources-after-20261004T214948.txt` | 21:34~21:49 출처별 응답 집계: 외부 출처는 허용 `10.1.93.50`(200/401/405)과 `10.250.10.20`뿐, 비허용 `.26/.29/.30/.55/.103/.104` 없음, `127.0.0.1`·`172.18.0.1`은 harbor01 자체 |
| `ansible01-output-files-listing-20261004.txt` | ansible01 출력 파일 목록·크기·해시 조회 결과 |

## 확인된 사실과 주의

- **잔존 XML은 덮어쓰이지 않았다.** 2차 적용 원본에서 `Create root-owned state directory`와 `Preserve original public zone XML`이 `changed`가 아니라 `ok`였다. 1차 시도가 남긴 `original-public.xml`이 같은 원본과 내용이 같아 변경이 없었다는 뜻이다. 1차 직후 harbor01에서 `original-public.xml`(392 bytes, 상태 폴더에 이 파일만 존재)을 확인했다. 1차 시도 직후 별도 hash 보존은 하지 않았다.
- **GO 조건 대비 미이행:** (3) 실패 회차 출력·잔존 XML hash를 재시도 **전** 별도 증적으로 보존 — 출력 파일은 보존됐으나 XML hash는 사전 보존하지 못함(위 `ok`로 변경 없음 확인), (2) 적용 직전 NIC/nft 재조회 — 19:57 값에 의존, (#13 시작 기록) 사전 게시 없음(21:12 진행 코멘트로 갈음). 적용 시작이 GO 코멘트보다 앞섰다.
- **이상 파일:** ansible01 `~/ac04-e1c4458-precheck-20261004T211015.txt`는 현재 37 bytes이며 내용이 `[ERROR]: User interrupted execution`(sha256 `640c83b8c065164d54b10ee1850e7a5dc79324cccc9079c2e3370d79dfb29f82`)이다. 그러나 21:10에 같은 명령 실행 직후 화면에는 `PRECHECK_PASS_RUNTIME_NOT_CHANGED`·`ok=47 changed=0`과 이 파일 해시로 `54bb5ffc…`가 표시됐다. 파일이 왜 달라졌는지 확인하지 못했다. 이 파일은 증적으로 첨부하지 않는다. 같은 기준선의 온전한 사전 점검 원본은 `~/ac04-precheck-20261004T174413.txt`와 `~/ac04-main-precheck-20261004T195510.txt`(각 6,191 bytes, 둘 다 sha256 `54bb5ffc1439278166c740c4b5c020d834644612ef8d6ffdbad93105e7049df5`, 17:44 파일은 PR #108에 편입)이다.
- apply 2차는 21:10 점검과 코드가 같은 main(`e1c4458`)에서 실행됐다.

## 한계와 미완 (AC04 = NOT PASSED 유지)

- 비허용 차단의 로그 증거는 해당 PC 브라우저 탭이 15분 주기로 갱신된다는 적용 전 관측에 근거한 추정이며 SYN 드롭 카운터는 수집하지 않았다.
- **미수행:** Worker 3대·edge01의 실제 Harbor pull/Pod start(허용 출처 positive; Worker는 AC-03 시험), 승인된 Docker restart persistence, 모니터링 Target 23/23 회귀(재환 확인 대기), 임시 예외 `.50`/`.102` 제거 추적, 서버 `/var/lib/fds-change/P1-HBR-01-AC04/` 상태 파일 hash 편입.
- `/etc/nftables/main.nft`에 `flush ruleset`이 있다(nftables.service는 disabled/inactive). 수동으로 해당 서비스를 켜면 우리 guard와 Docker 규칙이 지워질 수 있다.
- 작성자·AI 자체 검수이며 독립 리뷰 완료가 아니다.
