# IF06B 회차 입력표

CLAUDE_ASSISTED · 2026-10-12 KST · **r5**. 한 회차의 입력을 한 장에 모은다. 항목마다 따로 승인받는 표가 아니며, 수집 결과와 선택을 채운 뒤 한 번에 확정한다. 근거는 `MON_IF06B_FIELD_PREP.md`(r6), **실행 명령은 `RUNBOOK_DRAFT.md`(r3)에만** 있다.

**r4(일괄 반영 R1~R5):** 시간 후보를 한 표로 모았다(원안 · 후보 X · 후보 Y). 자격증명 칸을 "자동 회수는 token, 수동 인수는 기존 관리 인증"으로 통일했다. 전달물·경로·결과 위치, 네 캡처 지점, HEP·GNP 전후 기록, MON·gateway 기준선의 명령 위치 칸을 넣었다. 회차 순서의 명령은 지우고 실행안 위치를 가리킨다. r3는 SHA256 `15534719…33b2`.

**r5(D1·D2):** 시간 후보 표에서 캡처 창의 기준점을 고치고 X의 "권장" 표시를 뗐다. X는 만료 회수와 post-deny까지 덮는다는 보장이 없는 후보다. 재부팅 뒤 수동 회수에 쓰는 호스트 식별 칸을 넣었다. r4는 SHA256 `4da2695d…60af`.

**상태 표기:** `확정` 이미 확보 · `실측` 18:33:48 읽기로 관측, 현장 검증 전 · `후보` 계산·제안했으나 채택 전 · `현장` 그 위치에서 채움 · `선택` 회차에서 고름

**핵심 미확정 2개:** ① 사용할 자격증명(기존 것 또는 신규 SA 범위) ② 콘솔 인수가 실제로 가능한지. **이 둘만 남았다는 뜻은 아니다:** C의 경로와 검증, D의 현장 입력, E의 역할, 아래 시간 후보의 채택, F의 비중첩 구간도 비어 있다. 값을 채우는 것과 승인이 필요한 것을 섞지 않는다: 새 승인 범위가 필요한 것은 **신규 SA·RBAC·token 생성**과 **control01 파일 배치**, **실제 canary** 뿐이고, 나머지는 값 수집이다.

회차 식별자 `S`: `__________` · 계획 구간: `__________` ~ `__________` KST · 공급 기준: `92c182fc58de999536e56d90012bb2686d9f07cf`

실측 근거: control01 `k8s-control01`, product UUID `80724d56-7c17-f8a0-b2ea-ece7a154e24b`, boot `2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360`, 명령 18개 rc0, 원본 `control01-C1-C7.json` SHA256 `e1bbfe0e9a8a99ba2d458c3bb507a2b378cb57a918abc9dee510da957c253b4b`. 회차 전에 reboot나 관련 변경이 있었으면 해당 항목만 다시 읽는다.

이 hostname과 product UUID는 재부팅 뒤 수동 회수(실행안 8.2a)에서 "같은 호스트"를 확인하는 기준이기도 하다. 회차 직전에 값이 다르면 조사한다.

## A. 실행기 입력 (`input.json`)

| 항목 | 값 | 상태 | 비고 |
|---|---|---|---|
| `session_id` | | 선택 | `S`와 같게 |
| `expected_cluster_uid` | `e1669cff-1435-423f-a6c4-28bc44f488de` | 확정(10/12 오전 읽기) | `run`이 매번 재확인 |
| `api.connect_ip` / `port` | `10.1.93.109` / `6443` | 실측 C1 | 기존 관리 endpoint 유지. `.102` 직접 접속으로 바꾸지 않음 |
| `api.tls_server_name` | `10.1.93.109` | 실측 C1 | 실제 TLS 상대의 검증은 `preflight` |
| `api.ca_file` / `ca_sha256` | `/etc/kubernetes/pki/ca.crt` / `5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c` | 실측 C2 | MON 목적지용 Root CA와 다름 |
| `credential` | | **선택 ①** | 아래 B |
| `manifest_file` | `/var/lib/fds-change/if06b-<S>/supply/canary-manifest.json` | 후보 | SHA-256 `48f44146…f90a` |
| `reviewed_manifest_sha256` | `0602b0001405a9929f3b8d91dc6a2b9175c5811531a6eab930e50520b2f6d37f` | 후보 | `validate`가 재계산 |
| `reviewed_spec_sha256` | `4b5599c45f99528dc1e0f02216bd220afd3789af39db38159e718488d53b8146` | 후보 | `preflight` dry-run이 재확인 |
| `journal_dir` / `evidence_dir` | `/var/lib/fds-change/if06b-<S>/journal` / `…/evidence` | 후보 경로 | 회차마다 새 디렉터리. 결과 파일은 여기에 두지 않는다 |
| `budgets` 5개 | 아래 시간 후보 | 선택 | |

### 시간 후보 — 여기 한 곳에서 채택한다

원안은 [MON 최소 관측안](https://github.com/321Team/infra-monitoring/blob/0dd0235b07d44ba7965490e3808e0a67a3bd903b/docs/IF06B_REMAINING_TEST_INPUTS_20261009.md)의 **제안**이다. 120초·180초는 승인값이 아니므로 후보를 고르는 것이 새 AC 변경은 아니다. 기준점이 서로 다르다는 점을 같이 본다.

| 항목 | 기준점 | 원안(제안) | 후보 X | 후보 Y (r1 실행안) | 채택 |
|---|---|---|---|---|---|
| 캡처 창 | **지점마다 그 캡처의 `timeout` 시작 시각**(t0가 아님) | 최대 120초 | 120초 | 200초 초과 | |
| 공통 유효 관측 구간 | 가장 늦게 준비된 캡처 ~ 가장 먼저 끝난 캡처 | — | 120초보다 짧다 | 캡처 창보다 짧다 | 회차 뒤 시각으로 판단 |
| (만료 회수·post-deny까지 관측할 때) 캡처 창에 넣을 것 | 위와 같음 | — | 시작 시각 차이 + 사전 GET 2건(최대 20) + lease 90 + 회수 window 60 + post-deny 8 + 전달 여유 → **178초 + 여유, 원안 120초 초과** | 같은 식에 lease 120 → 208초 + 여유 | |
| 무시험 배경 | t0 | 20초 | 20초 | 20초 | |
| 두 요청(443 + 8443) | 첫 요청 시작 | 20초 이내 | 20초 | 30초 | |
| 후관측 | 마지막 요청 뒤 | 20초 | 20초 | 20초 | |
| `lease_seconds` | `ARMING` 직전 | — | 90 | 120 | |
| `cleanup_window_seconds` | 만료 시각 | — | 60 | 60 | |
| lease + 회수 window | `ARMING` 직전 | canary 180초 | 150초 | 180초 | |
| 요청 시작 최종 시점 | 만료 시각에서 거꾸로 | — | 만료 − 40초 | 만료 − 50초 | |
| `request_timeout_seconds` | 요청 1건 | (카드의 kubectl 10초) | 10 | 10 | |
| `observation_max_age_seconds` | 삭제 직전 GET | — | 10 | 10 | |
| `readback_delay_seconds` | DELETE 뒤 | — | 2 | 2 | |
| watch `poll` / `window` | `watch`를 띄운 시각 | — | 2 / 200 | 2 / 200 | |
| token 요청 TTL / 허용 실제 상한 | 발급 시각 | — | 900 / 900 | 900 / — | |
| token `run` 직전 남은 시간 | 7-0 확인 시각 | — | lease + 회수 window + 인수 여유 이상 | 같음 | |
| survival-check 길이 / 간격 | 시작 | — | 300 / 5 | 300 / 5 | |

- **기준점:** 각 캡처의 창은 **그 캡처의 `timeout`이 시작된 순간부터** 센다. t0는 네 지점의 준비를 서로 확인한 시각일 뿐, 타이머를 다시 시작하는 시각이 아니다. 먼저 켠 캡처는 t0 전에 이미 시간이 줄어든다. 네 캡처에 공통으로 유효한 관측 구간은 **가장 늦게 준비된 시각부터 가장 먼저 끝난 시각까지**다. `run`의 사전 GET 2건은 lease가 시작되기 전에 일어난다.
- **X와 Y 중 고르는 기준:** X는 원안의 캡처·요청·후관측 숫자를 유지한다. 대신 만료에 의한 회수와 post-deny까지 캡처 안에 든다는 보장이 없고, **관측 범위가 제한될 수 있음을 받아들일 때** 고른다. 만료 회수와 post-deny까지 관측하려면 위 표의 셋째 줄처럼 캡처 창을 길게 잡아야 하며, 그러면 원안의 캡처 상한 제안과 다른 숫자가 된다. 사람 사이의 전달 시간을 0으로 잡지 않는다. 어느 쪽도 권장으로 정해 두지 않았다.
- 두 후보 모두 실행기의 제약(`lease > request_timeout`, `cleanup_window > 3 × request_timeout + readback_delay`)을 만족한다.
- lease + 회수 window는 **API 처리 예산**이지 그 시간 안에 삭제나 인수가 끝난다는 보장이 아니다.
- 900초는 **MON의 현재 후보**다. 다른 업무에서 정한 값을 가져온 것이 아니다.
- 어느 후보든 지연으로 캡처 창을 벗어난 부분은 `NOT_VERIFIED`이고 추가 시험 없이 회수한다. lease와 캡처 창을 현장에서 늘리지 않는다.

## B. 자격증명 — 핵심 미확정 ①

비밀값은 적지 않는다. 경로와 속성만 적는다. **역할 분리: 임시 credential은 감독의 자동 회수에만 쓰고, 콘솔 수동 인수는 기존 관리 인증으로 한다.**

| 항목 | 값 |
|---|---|
| 방식 | 용도·권한·수명이 확인된 기존 guardian용 credential이 있으면 그것. 없으면 **신규 기본 후보: 회차용 ServiceAccount + RBAC + 단기 token**(실행안 2절, `rbac/`). 채택 제안이며 생성 허용이 아님 |
| 종류 (`bearer_token_file` / `client_cert_files`) · 파일 경로 | 신규 후보: `bearer_token_file` · `/run/fds-if06b-<S>/token` (새 디렉터리, 덮어쓰기 없음) |
| 발급 주체 · 용도 | |
| (신규일 때) 생성 영수증의 UID 3개 — SA / ClusterRole / ClusterRoleBinding | 실행안 2.3의 `…-receipt.out`에서 |
| (신규일 때) 준비 중 실패·UNKNOWN 객체가 있었는가, 지금 남은 객체 | 실행안 2.6의 보고 |
| token: 요청 TTL · 실제 `lifetime_s` · `run` 직전 `left_s` | 요청 후보 900 · `tokeninfo` 출력 · 7-0 출력 |
| token: 허용 실제 상한을 넘거나 자동 회수 예산에 못 미치면 | **시작하지 않는다** |
| 실행에 필요한 create/get/delete 허용 확인 | `preflight` 접근 검토 3건. 이 통과가 다른 권한이 없다거나 최소 권한이라는 증명은 아니다 |
| credential의 출처와 역할 범위의 근거 | 위와 별도로 연결(영수증, manifest 해시, `can-i` 11건) |
| 남는 권한 | create는 이름 제한이 안 된다: 유효한 동안 어떤 GlobalNetworkPolicy든 생성 가능. "이 canary 전용"이라고 적지 않는다 |
| 임시 credential이 만료·소실될 때의 회수 경로 | 콘솔 인수자의 **기존 관리 인증**(실행안 8절). 자동 회수 예산만 임시 credential이 덮으면 된다 |
| 새 사본/RBAC 생성 범위의 허용 근거 | |
| swap 상태 | 실측 C7(18:33:48): 활성 swap 없음, `/run`은 tmpfs. 그 시점의 사실일 뿐이다 |

C3 실측: `/etc/kubernetes/` 바로 아래에는 관리·시스템 구성요소용 kubeconfig 5개(모두 root 0600)만 있었다. guardian 전용 파일은 그 위치에서 보이지 않았다. 이것으로 한정 자격증명의 부재를 확정하지 않으며, 그것들을 쓰자는 뜻도 아니다.

## C. control01 — 전달물, 경로, 실행 환경, 준비 검증

| 항목 | 값 | 상태 |
|---|---|---|
| 호스트 · OS | k8s-control01 `10.1.93.102`, EL10, SELinux Enforcing | 확정(10/12 오전 읽기) |
| Python · OpenSSL · 시계 | 3.12.14 · OpenSSL 3.5.8 · `CLOCK_BOOTTIME` 있음 | 실측 C6 |
| 세션 종료 정책 | `KillUserProcesses=false`, `svc_ansible` Linger=no | 실측 C4 |
| 보호 경로 부모 | `/var/lib/fds-change` root:root 0700, `var_lib_t`, local XFS. 기존 자식 `CR-P1-NTP-01-01`·`ssh-pr4` | 실측 C5 |
| 전달물 1 | `supply-92c182f.tar` 81,920 B, SHA-256 `8d1630c872eb9a88cecc3f5dec3cc6e2316f87ec6dacea420777967b5795fc20` | 확정(로컬) |
| 전달물 2 | `if06b-aux-r1.tar` 20,480 B, SHA-256 `fd5bb7c43fa8cf166f074eb78afb98bf4e552cfdc6f4762adac9eda1bab9d7ad` (`rbac/` + `tools/`) | 확정(로컬) |
| 받는 위치 `<IN>` (절대경로, 기존 승인 전송 경로) | | 현장 |
| 회차 경로 `SES` | `/var/lib/fds-change/if06b-<S>/` 아래 `supply/` `aux/` `journal/` `evidence/` `results/` | 후보. 새로 만들어지는지 확인하고, 기존 것을 지우거나 다시 쓰지 않음 |
| 생존 시험 경로 `SURV` | `/var/lib/fds-change/if06b-survival-<S>/` | 후보. `SES`와 다른 경로 |
| token 경로 `TOK` | `/run/fds-if06b-<S>/` | 후보 |
| 실행 구조 (A 세션 이탈 / B 콘솔 / C transient unit) | | 선택. A는 후보 유지 |
| 1절 배치 결과 (`mkdir_rc`·`supply_rc`·`aux_rc`, `1-4-layout`) | | 현장 — `NOT RUN` |
| 3절 `validate` (`3-1-validate.rc`·`.out`) | | 현장 — `NOT RUN` |
| 4절 `survival-check` (세션 S의 ID, 닫은 시각, `BEAT`·`FINAL`) | | 현장 — `NOT RUN` |
| 5절 `preflight` (`5-1-preflight.rc`·`.out`) | | 현장 — `NOT RUN` |
| 위 검증 뒤 바뀐 입력이 있는가 | | 회차 직전 |

## D. control01 밖의 입력과 기준 기록

| 위치 | 항목 | 값 | 상태 |
|---|---|---|---|
| worker03 `.108` | 접근 경로 | 기존 `server07` | 확정(기존 경로), 회차 인증은 현장 |
| | `route get 10.250.10.30`의 src · 인터페이스(= `worker-out` 캡처 IF) | | 현장 (10/6: `src 10.1.93.108`, HEP 인터페이스 `ens160`) |
| | 고정 출발 포트 2개 (443용 / 8443용) | | 선택 |
| | 승인 CA 파일의 절대경로 · SHA-256 | Root `20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f` | 확정(카드), 파일 대조는 현장 |
| | 443 검증 이름 · `GET /` 기대값 | IP SAN `.30` · 404(승인 소스 기준) | 후보, live 확인은 현장 |
| | 8443 연결 상한 · 재시도 | 5초 · 0 | 확정(MON 최소 관측안) |
| mgmt-gw01 `.58` | `gateway-in`(physical) · `gateway-out`(management) 인터페이스 | | 현장 |
| | 정책·zone·route·NAT 전후 | 기존 수집기 `ops/if06b-policy-readonly/`(`92c182f`, `collect.py` `d8c6fdef…0f4b`), ansible01에서 `run-interactive.sh`. 회차 전 1회 · 뒤 1회 | 명령 위치 확정, 실행은 현장 |
| | 관측 계정 · sudo/콘솔 | | 현장 (10/8 인증 재사용 안 함) |
| monitor01 `.30` | `monitor-in` 인터페이스 | `ens160`(카드) | 후보, 현장 확인 |
| | listener 443 · 8443 전후, firewalld runtime/permanent 전후 | | 현장 |
| | 관측 계정 | | 현장 |
| 네 캡처 지점 | 결과 디렉터리 | 각 호스트 `~/if06b-<S>/worker-out/` · `gateway-in/` · `gateway-out/` · `monitor-in/` | 후보. 지점마다 터미널 하나 |
| | 필터 · 헤더 전용 · 종료 코드 보존 | 카드 3절 필터 재사용 | 확정(카드) |
| control01 | worker03 HEP · host GNP의 raw·UID/RV/spec 해시, GNP 목록 전후 | 실행안 6.1 · 6.4 (`6-pre-*`, `6-post-*`, `6-diff-*`) | 명령 확정, 실행은 현장 |
| MON | targets 수와 up 수, remote write 실패 증가(15분), heartbeat 나이 — **읽는 명령과 위치** | 10/6 `mon-gate-…txt`·`hb-after.txt`를 만든 기존 명령. 저장소에서 위치를 찾지 못함 | **현장 입력** |
| | 기대값 | 23 / 23 / 0 / 정상 | 확정(10/6 형식) |

## E. 역할 — 핵심 미확정 ②는 "회수 인수"

겸임할 수 있다. 다만 **네 지점의 동시 캡처**(터미널 4개)와 장애 시 콘솔 인수가 실제로 가능해야 한다.

| 역할 | 실행자 | 대체 연락 | 경로 |
|---|---|---|---|
| control01 실행 (`run`, 시작 판정, 감독 식별 뒤 신호, 중단 전달) | | | |
| **회수 인수** (`ARMED` 직후 `watch`, 콘솔에서 **기존 관리 인증**으로 수동 조건부 회수, 만료·회수 기한 시각 인지) | 후보: 이권욱 — control01 콘솔 로그인·sudo·기존 관리 인증의 실제 가용성은 **미확인** | | |
| MON 관측 (기준선 전후, abort 판단) | | | |
| worker03 요청 (시작 통보 뒤에만, 8443 전 "계속" 통보 뒤에만) | | | |
| gateway 관측 (캡처 2개 + 정책 수집 2회) | | | |
| monitor01 관측 | | | |

abort 기준: `__________` (MON Lead 제안: `count(up==1)` 기준선 감소 / heartbeat 60초 이상 단절 / remote write 실패 증가). abort를 보낸 뒤에는 그 행이 증적에 보이기 전이라도 새 요청을 보내지 않는다.

## F. 시작 조건 점검 (회차 직전)

| 조건 | 확인 |
|---|---|
| T19 보호 복원과 후속 원복·최종 기준선 검수의 기존 근거 연결, 그 뒤 변경 없음 또는 영향 확인 | |
| 현재 기준선 안정(D의 MON 기대값) | |
| Harbor의 앱 변경·복구·worker 검증·사후 관측이 끝났고 다음 변경과 겹치지 않음. Harbor가 대기 중이라는 것만으로 구간이 비었다고 보지 않는다. **이 문서 작성이 그 구간의 확보는 아니다** | |
| 다른 K8S·네트워크·APP 작업 없음 | |
| control01 boot가 실측 때와 같음(`2a889fe4-…`) 또는 바뀐 항목 재확인 | |
| worker03 HEP · host GNP 기록(`6-pre-*`), 같은 selector·order 90의 다른 GNP 없음 | |
| credential 수명 재확인(실행안 7-0) | |
| A의 시간 후보 채택, B·E의 핵심 미확정 2개, C의 준비 검증, D의 현장 입력이 채워짐 | |
| 네 캡처의 준비 통보 | |

## G. 회차 중 순서

명령·출력·판정표는 `RUNBOOK_DRAFT.md` 7절(회차), 6절(관측), 8절(인수)에 있다. 여기에는 순서만 둔다.

1. 네 캡처 준비 통보 → token 수명·boot 확인(7-0) → `run`(7-1) → `ARMED`. `ARMED`와 launcher rc 0은 생성도 회수도 아니다.
2. 인수자가 `watch`를 바로 띄운다(7-2).
3. 시작 판정(7-3). `SNAPSHOT_ELIGIBLE`이 나올 때까지 로컬 증적만 다시 읽는다. POST를 다시 보내지 않는다. `STOP_…`이면 새 요청 금지.
4. 시작 전달 조건 네 가지를 모두 볼 때만 요청자에게 시작 전달. `watch` 결과와 abort는 요청자에게 바로 넘긴다.
5. 443 양성 대조 1회 → 8443 직전 재판정 → 8443 새 연결 1회 → 후관측(6.3).
6. 감독 식별 뒤 완료 신호(7-4) → 자동 회수 → `watch` 종료 코드.
7. post-deny와 전후 비교(6.4) → 임시 권한 정리(9.1) → 증적 모으기(9.2).

만료 시각: `__________` · 회수 기한 시각: `__________` (인수자가 알고 있을 것) · 요청 시작 최종 시점: `__________`

네 캡처의 시작·종료 시각: worker-out `____`~`____` · gateway-in `____`~`____` · gateway-out `____`~`____` · monitor-in `____`~`____` → 공통 유효 관측 구간 `____`~`____`

도중에 control01이 재부팅됐으면: 신호·재실행 없이 실행안 8.2a의 다섯 확인(같은 호스트 · boot 변경 · 같은 회차 · 같은 cluster · 락 해제)을 기록한다. 이전 boot의 만료 시각을 현재 시계와 비교하지 않는다.

실제로 보낸 요청 수: 443 `__` 회 · 8443 `__` 회 · post-deny `__` 회 (중단 전에 나간 것도 그대로 적는다)
