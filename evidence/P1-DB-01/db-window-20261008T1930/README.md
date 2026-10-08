# P1-DB-01 — DB 변경 창 RUN 20261008T1930 실행 증적 (2026-10-08 20:13~20:36 KST)

[#11 창 승인 6058586541](https://github.com/321Team/fds-project-baseline/issues/11#issuecomment-6058586541)(이권욱, 조건부 Runtime/Test GO)에 따라 실행한 1회 창의 원본이다. 실행자는 DB Lead 이재환(supreme33-kr)이다. 해석은 이 README에만 적는다. 위험수용 종료 판단은 이하영이 한다.

**결론: W0~W6 모두 정상 종료, 복구 실행 없음.** T0 20:13:03, 정상 종료 20:36 무렵(23분). 정상 작업 상한 T0+90분(21:43)과 복구 상한 안이다.

| 변경 | 결과 |
|---|---|
| A. edge01 옛 E-K3S 중지 | k3s `inactive`/`disabled`, shim 0, `.50:30080` 응답 000, 수신 포트 없음. nginx `.50:80/readyz` 200 유지. `.50` 출발 DB 세션 0 |
| B. pg_hba `.50` 규칙 제거 | `.50` 줄 1개만 삭제(diff 1줄). `pg_reload_conf=t`, 서버 로그 SIGHUP 20:17:04.331. **edge01 실제 새 SSL 접속이 SQLSTATE 28000 no-entry로 거부**(hba-probe REJECTED rc0) |
| C. db01 5432 출발지 제한 | `ports: 5432/tcp` 제거, Worker `.105/.107/.108`만 rich rule로 허용(runtime·permanent 모두). NM 인터페이스 바인딩 `[ens160 ens192]` 유지. 새 Pod 3개 접속·거래 저장 확인 |
| D. `fds_app` 비밀번호 교체 | 검증자 지문 `2c137c45f1d890f5`→`989c03d351559233`. Secret `DATABASE_URL` 지문 `c6128b8b873eecf8`→`073d25232749095f`, rollout 3/3. 교체 뒤 거래 저장 확인 |

**남은 사항:**
- W5의 `apply.sh check`가 `RUNTIME_PERMANENT_MATCH=NO`를 냈다. runtime과 permanent의 rich rule **순서만** 다르다. 정렬 비교에서 rich rule 집합과 나머지 줄이 모두 같았다(`RICH_RULES_SET_EQUAL`, `OTHER_LINES_EQUAL`). 판정 코드를 순서 무관하게 고치는 후속 PR을 infra-db에 낸다.
- N1(control01)은 변경 전부터 timeout이라 판정 불가다. 차단 근거로 쓰지 않는다.
- W4의 DB 비밀번호 적용(20:26:49)부터 Secret 갱신(20:27:17)·rollout 완료(20:27:52)까지 기존 Pod의 새 DB 연결이 실패할 수 있었다. 이 간격의 5xx 여부는 **측정하지 않았다(NOT MEASURED)**.

## 실행 조건

| 항목 | 기록 |
|---|---|
| 코드 | [infra-db#9](https://github.com/321Team/infra-db/pull/9) 병합 `346725c55c47a99c3ba18c11d4ef8f018192c520`. `control01-secret.sh`는 같은 내용의 이전 병합 `bdcc5613586c011086d13d8d3fa66561ff1e60ba`에서 추출 |
| 배치·해시 대조 | edge01 `~/db-window-346725c5/edge01-k3s.sh` `5f73b153…`, db01 `~/db-window-346725c5/db01.sh` `7d5a203a…`·`apply.sh` `c216f89c…`(20:06 무렵 서버 `sha256sum`), control01 `~/db-window-bdcc5613/control01-secret.sh` `d4e188c3…`(18:44 서버 `sha256sum`). 4개 모두 승인 SHA256과 같다. 대조 출력은 채팅 기록이고 이 폴더에 넣지 않았다 |
| 실행 계정 | edge01·db01 `server08`, control01 `server02`, PC `.29` `soldesk` |
| 단톡 공지·작업창 비중첩(#10/#13/#15/#19) | 실행자 보고: 시작 전 단톡 공지 게시, #13 등 작업창 비중첩은 이권욱 확인. 공지·확인 원문은 단톡에 있고 이 폴더에는 없다 |
| 사전 조회 | 20:06~20:07의 check·probe(`*-200643`·`200645`·`200707`·`200731`, `apply-check-W0.txt`)는 승인 댓글(20:11:25) **전**의 읽기 전용 조회다. W0는 승인 뒤 20:13에 다시 했다 |

## 단계별 결과

| 단계 | 시각(KST) | 결과 | 원본 |
|---|---|---|---|
| W0 | 20:13:03~20:13:40 | edge01: nginx 유효 upstream Worker 3/3, 옛 참조 0, reload 반영 rc0, 옛 NodePort ESTABLISHED 0, hba-probe ALLOWED rc0(TLSv1.3, SCRAM-SHA-256-PLUS·SCRAM-SHA-256). db01: hba_file 일치, 오류 0, `.50` 대상 1줄, `.50` 세션 3, `lc_messages=ko_KR.UTF-8`, 로그 억제 SET rc0, `RUNTIME_PERMANENT_MATCH=YES`(interfaces 줄 제외). control01: Secret 키 `DATABASE_URL` 1개, 소비자 Deployment 1개, replicas 3/3, endpoint 3 | `edge01-check-201303`, `edge01-hba-probe-201304`, `db01-check-201314`, `apply-check-W0b.txt`, `control01-check-201327` |
| W1 | 20:15:01~20:16:05 | `RESULT k3s-stop=OK 20:15:09`. k3s 정지 뒤 iptables k8s 관련 줄 0, 6443·10250·30080 수신 없음. db01 `.50` 세션 0(20:15:24, 20:16:05) | `edge01-stop-201501`, `db01-check-201524`·`201604` |
| W2 | 20:17:03~20:17:30 | pg_hba diff `128d127 < hostssl fdsdb fds_app 10.1.93.50/32 scram-sha-256` 1줄. SHA `e7bd24db…`→`80eb1e51…`. `pg_reload_conf=t`, SIGHUP 로그. 20:17:30 hba-probe REJECTED rc0: `sqlstate=28000`, 메시지 출발지 `10.1.93.50`·`fds_app`·`fdsdb`·SSL 일치 | `db01-hba-apply-201703`, `pg_hba.conf.before/after`, `edge01-hba-probe-201730` |
| W3 | 20:18:03~20:22:32 | `apply.sh apply` rc0, 변경 5건 success. rollout 새 Pod `77bd7c6f64-*` 3개 Ready 20:18:38~20:19:01. 거래 `540d89c3-…`(계정 `SIM_p2hyb_202610081930_W3_1`) curl rc0·HTTP 201, DB 정확히 1행, 값 일치(`f`/`f`, 수신 20:19:15.558) | `apply-apply-W3.txt`, `pc/*W3*`, 전사본 |
| W4 | 20:23:03~20:31:19 | prepare(검증자 지문 `989c03d3…`, 새 URL 지문 `073d2523…`) → db01 pw-apply 20:26:49(`old_fp=2c137c45…` `new_fp=989c03d3…`) → control01 apply: Secret 지문 일치 20:27:18, rollout `54984f6ddd-*` 3/3, `RESULT apply=OK 20:27:52`. 거래 `1a615fca-…`(계정 `…_W4_1`) curl rc0·HTTP 201, DB 1행(수신 20:31:19.385) | `control01-prepare-202303`, `db01-pw-apply-202530`, `control01-apply-202713`, `pc/*W4*`, 전사본 |
| W5 | 20:32:04~20:34 | db01: `.50` 대상 0줄, 세션 `.105/.107/.108` 각 1, 검증자 지문 `989c03d3…`. edge01: k3s inactive/disabled, nginx readyz 200, Worker 3개 200. control01: Secret 지문 `073d2523…`. MON `count(up)=23`, `up==1` 23, `up==0` 없음. P1 `.50/readyz` 200. 방화벽 판정은 위 "남은 사항" | `db01-check-203204`, `edge01-check-203213`, `control01-check-203241`, `apply-check-W5.txt`, 전사본 |
| W6 | 20:35:50~20:36 | control01 `RESULT cleanup=OK`, `secret` 디렉터리 없음. db01 `RESULT cleanup=OK`, 남은 파일 `pg_hba.conf.before/after`만 | 전사본 |

## 음성 시험 (5432 TCP 연결, `timeout 5 bash -c '</dev/tcp/10.1.93.55/5432'`)

| 시험 | 출발지 | 변경 전 W0 | W3 뒤 | W5 | 판정 |
|---|---|---|---|---|---|
| N1 | control01 `.102` | rc124 | rc124 (20:20:53) | rc124 (20:32:41) | **판정 불가** — 변경 전부터 timeout |
| N2 | edge01 `.50` | rc0 | rc1 "호스트로 갈 루트가 없음" (20:21:56) | rc1 (20:32:14) | 차단됨 — 연결 성공 → 거부 응답 |
| N3 | PC `.29` | rc0 (20:13:40) | rc124 (20:22:32) | rc124 (20:33:00) | 차단됨 — 연결 성공 → timeout |
| N4 | fds-engine Pod(control01에서 exec) | 시험 안 함 | — | rc1 `TimeoutError` | 참고만. 변경 전 대조가 없고, 차단 지점이 db01인지 클러스터 정책인지 확인하지 않았다 |

- N2와 N3는 같은 변경 뒤 응답 형태가 다르다(N2 즉시 거부, N3 timeout). 원인은 확인하지 않았다(NOT VERIFIED). 두 출발지 모두 변경 전 연결이 됐고 변경 뒤 안 되므로 전후 대조는 성립한다.
- 승인 Worker 출발 양성은 W3·W4의 새 Pod 접속(db01 세션 `.105/.107/.108` 각 1)과 거래 저장으로 확인했다.

## 비밀정보 처리

- 아카이브에서 `secret` 디렉터리(control01)와 `fds_app.verifier*`(db01)를 제외했다. 서버의 `tar -tzvf` 목록에서 `secret`·`verifier` 0건이었다.
- 수신 뒤 세 아카이브를 풀어 SCRAM 검증자, md5 해시, URL 안 비밀번호, 개인키, JWT 형식을 검색했다. 0건이다. URL은 `fds_app:***`로만 나온다.
- 검증자 한 줄은 control01 출력에서 db01로만 옮겼고 채팅·로그에 남기지 않았다. 이전 검증자 보관본은 W6에서 지웠다.

## 파일

| 경로 | 내용 |
|---|---|
| `edge01/edge01-p2-hyb01-20261008T1930.tgz` | edge01 `~/p2-hyb01-20261008T1930/` 로그 7개. PC로 scp |
| `db01/db01-p2-hyb01-20261008T1930.tgz` | db01 `~/p2-hyb01-20261008T1930/` 로그 11개 + `/var/lib/pgsql/fds-evidence/p2-hyb01-20261008T1930/pg_hba.conf.before/after`. PC로 scp |
| `control01/control01-p2-hyb01-20261008T1930.tgz` | control01 `/root/p2-hyb01-20261008T1930/` 로그 5개. `base64 -w 76` 출력을 PC에서 복원 |
| `*/*.tgz.sha256`, `*/*.tgz.contents.txt` | 서버에서 만든 SHA256과 `tar -tzvf` 목록(control01 둘은 PC에서 같은 명령으로 다시 만들었고 서버 출력과 같다) |
| `pc/p2-SIM_p2hyb_202610081930_W{3,4}_1.json(.code)` | PC 거래 POST 응답 본문과 HTTP 코드(`.code`는 Git Bash가 쓴 CRLF) |
| `transcribed/chat-outputs-20261008T1930.txt` | 서버 파일로 남지 않은 터미널 출력의 **전사본**(N1~N4, P1, P2 DB 행, rollout, MON, 정렬 비교, W6 정리). 서버 SHA 없음 |
| `SHA256SUMS` | 이 폴더 파일의 SHA-256 |

수신 SHA256: edge01 `b244f1430897307be726519b6c3d48b842ac8c979088217bcddca2b1641e1282`, db01 `73407dcacc966973cb00fc6d01ec9c66fc230eea3b6f29e3a00180b46c88fc68`, control01 `bd33f42630df56163544354b386fcfbc853579617a43076f55580b2c2f75d5af`. 셋 다 서버 출력과 같다.

## 한계

- 이 창은 실서버 1회 실행이며, 실행 스크립트 자체를 CI로 시험한 회차가 아니다. 저장소 `check`(evidence-layout)는 이 PR에서 실행됐다: 첫 HEAD `acd71ded`는 대장·archive 목록 미등록으로 FAIL(오류 19건), 등록 커밋 `ff252c48`에서 PASS. (하영 리뷰 지적으로 정정, 이전 문구 "CI NOT RUN"은 사실과 달랐다)
- 복구 절차는 실행하지 않았다(실패 없음). 복구 경로의 실서버 동작은 이 증적으로 확인되지 않는다.
- control01 cleanup 로그(`control01-cleanup-203550.log`, 0바이트)는 아카이브 뒤에 생겨 포함되지 않았다. 결과는 전사본에 있다.
- 옛 E-K3S의 uninstall·데이터 삭제와 `robot$fds-ci` 폐기는 이 창 범위 밖이다(infra-db README 후속 절).

AI 사용: CLAUDE_ASSISTED (명령 준비, 파일 수신·검증, 비밀 패턴 검색, README 작성)
