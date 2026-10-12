# P1-MON-01 — IF06B 단회 canary·만료 자동 회수 (2026-10-12 KST)

**승인된 canary 1회와 만료 회수·임시 권한 정리를 완료했다. 이번 관측 범위의 RUNTIME PASS를 증적으로 제출하며, 독립 편입 리뷰·병합·티켓 전체 AC 인수는 별도다.** 실행자는 이권욱(GWONUK), 명령·수집·분석은 CODEX_ASSISTED다. Phase 1 잔여 IF06B 범위이며 Phase 2 또는 영구 설정 변경은 포함하지 않는다.

회차는 `20261012T2220-mon02`. 제품 코드는 [infra-kubernetes#85](https://github.com/321Team/infra-kubernetes/pull/85) 병합본 `92c182fc58de999536e56d90012bb2686d9f07cf`의 실행기다. [MON 승인](https://github.com/321Team/infra-kubernetes/pull/85#pullrequestreview-5488184132)은 코드/문서 리뷰이고 이번 실제 증적의 독립 승인은 아니다. 제품 코드·AC 문구를 이 PR에서 변경하지 않는다.

## 검토 순서와 원본

1. 아래 결과·H04 대응·한계를 확인한다.
2. [journal](excerpts/control01/journal/journal.jsonl), [supervisor](excerpts/control01/evidence/supervisor.jsonl), [watch](excerpts/control01/results/7-2-watch.out)로 생성→만료→조건부 회수→부재를 대조한다.
3. [기계 판독 결과](raw/RUNTIME_RESULT.json)와 세 원본 압축본, worker 원본을 대조한다. [오프라인 검증기](verify_runtime.py)는 원본을 읽고 저장된 결과와 비교하며 네트워크 접근·파일 쓰기를 하지 않는다.
4. `execution/`은 당시 실행 명령·전달 소스의 사본이다. 검토를 위해 보존했으며 **재실행 카드가 아니다**. `provenance/`의 준비 문서·초기 회차 상태는 각 작성 시점의 이력이다.

| 자료 | 내용·수신 방식 |
|---|---|
| [control01-evidence.tar.gz](raw/control01-evidence.tar.gz) | control01에서 만든 227개 일반 원본과 `EXPORT_SHA256SUMS`. 기존 SSH 경로의 전송 출력에서 복원; 원 바이트 유지 |
| [gateway-fetch.tar.gz](raw/gateway-fetch.tar.gz) | gateway 사전/사후 조회 압축본, 양쪽 캡처·시각·rc·통계, 실행/인증 흐름의 영수증 |
| [monitor-fetch.tar.gz](raw/monitor-fetch.tar.gz) | monitor01 사전/사후 조회 압축본, 캡처·heartbeat·alert·시각·rc·통계 |
| [worker03-export.json](raw/worker03-export.json) | SSH 수신한 worker 명령·캡처·시각 원문과 파일별 SHA256. 해석은 결과 JSON/이 문서에 분리 |
| [worker03-route-post.json](raw/worker03-route-post.json) | 마지막 사후 경로 조회, 22:30:56.841 KST 종료 |
| [ORIGIN.json](ORIGIN.json) | 복사 출처, 수신 바이트 수·SHA256, 압축본 내부 발췌 위치. 공개된 사본은 원본과 바이트 동일 |
| [SHA256SUMS](SHA256SUMS) | **이번 편입 폴더** 무결성 목록. 루트 대장에서 이 파일로 연결 |

세 현장 압축본의 SHA256은 각각 `3472837608b92afdd0171893707538bd433eb2050fe745a17e8176260bbca1d7`, `faaf0598996338c030a47f2f6be506053008181031bba209696a6f979c62858d`, `39dfd226108d499ddb1220845c00ac767218777362f1a63f9c57e8166efd2f13`다. 같은 이름의 `.sha256`과 저장소 `registry/ARCHIVE_CONTENTS.json`에 내부 목록을 연결했다. 재압축하지 않았다.

`raw/RUNTIME_RESULT.*`의 `NOT_PUBLISHED`/리뷰 대기는 22:32 최초 정리 시점의 상태다. 원문을 사후 수정하지 않는다. 실제 제출·리뷰·병합 상태는 이 편입 PR 이력으로 확인한다. `provenance/ORIGINAL_LOCAL_SHA256SUMS`는 최초 로컬 100개 산출물의 이력이며 이번 선별 편입 목록이 아니다. 중복 base64 압축본 출력, 최종 묶음 안에 포함된 별도 사전 압축본, 로컬 창 바로가기는 중복 편입하지 않았다.

## 승인·대상·실행 입력

사용자가 [실제 적용 범위](provenance/EXECUTION_SCOPE.md)에 대해 “일괄 허용 — 검증·비중첩 충족 후 1회 실행”으로 승인했다([동일 대화 승인 수신 기록](provenance/RUNTIME_AUTHORIZATION.json)). 사용자에게 control01 VMware 콘솔 로그인·sudo·기존 관리 인증과 회차 대기가 가능함을 확인했고, gateway·monitor01은 사용자 직접 인증으로 진행했다. 이 기록은 타인의 독립 승인이나 새 권한 위임이 아니다.

| 항목 | 이번 실제 값 |
|---|---|
| control01 | `k8s-control01` / `10.1.93.102`; `fds-ansible01 → svc_ansible → sudo`, UUID `80724d56-7c17-f8a0-b2ea-ece7a154e24b`, boot `2a889fe4-51fe-43fe-bcd7-5a0f9b8ff360` |
| API / cluster | `10.1.93.109:6443`, TLS 검증 이름 `10.1.93.109`, cluster UID `e1669cff-1435-423f-a6c4-28bc44f488de` |
| worker03 | `10.1.93.108`, `svc_ansible → sudo`, host-origin `ens160`, `.30 via 10.1.93.58`; boot `f0c48106-f753-4ab7-bacd-660c126fca2f` |
| gateway / monitor | gateway `ens160` 입구·`ens224` 출구; monitor01 `.30`의 `ens160`. 기존 계정 직접 인증·sudo. 각 수집 원본의 `receipt.json`에 명령·시각·rc |
| 공급·보호 경로 | `/home/svc_ansible/if06b-in-20261012T2220-mon02`, `/var/lib/fds-change/if06b-20261012T2220-mon02`, token은 `/run/fds-if06b-20261012T2220-mon02/token` |
| 입력 SHA256 | `ac489bef85948b4a8a425e1aeb96cdabe328827152264246cae98135618cbfce`; [배치 입력 원본](excerpts/control01/input.json) |
| manifest / spec | `0602b0001405a9929f3b8d91dc6a2b9175c5811531a6eab930e50520b2f6d37f` / `4b5599c45f99528dc1e0f02216bd220afd3789af39db38159e718488d53b8146`; 실제 dry-run에서 대조 |
| 예산 | lease90 / cleanup60 / API request10 / max-age10 / readback2초; 캡처300초, background20 / 요청20 / 후관측20초, watch poll2/window200 |
| 자격증명 | 임시 SA·ClusterRole·Binding 각1, token 실제 TTL900초. GNP create는 이름 제한 불가, get/delete는 canary 이름 제한. 최소 권한 전체를 증명한 것으로 확대하지 않음 |

이전 준비 회차(mon01)는 canary0·시험0으로 정리됐다([당시 종료 기록](provenance/PREPARATION_CLOSEOUT.md)). [입력 차이](raw/PREPARATION_DELTA.json)는 회차ID 및 그에 종속된 경로, JSON pointer 5개뿐이며 코드·정책·예산은 그대로다. 공급15개 해시, 새 경로·권한, 11개 허용/금지 검사, `validate`와 `preflight`를 실제 확인했다([배치](raw/control01-supply-placed.json), [검증](raw/control01-credential-preflight.json)).

`survival-check`는 **동일 boot·동일 공급**에서 21:23:00.987~21:28:00.989 실행한 300초·BEAT60·FINAL과 시작 SSH 세션24 소실 증거를 재사용했다([시작](provenance/control01-survival-start-2.json), [최종](provenance/control01-survival-final-2.json)). mon02에서 재실행한 것으로 세지 않는다. 실제 재부팅/SIGKILL 복구 시험은 이번 범위가 아니다.

Harbor와는 사용자 MON 우선 지시 및 [22:18 작업창 조정 기록](provenance/HARBOR_WINDOW_RECORD.json)으로 현장 비중첩을 확인했다. Harbor는 로컬 코드 작업만 병행했고 MON 마지막 사후 조회는 22:30:56.841 종료했다. 이후 Harbor 실행 허용 여부는 해당 작업의 별도 승인 범위로 판단한다.

## 실제 결과와 H04 대응

공통 유효 캡처 구간은 **22:23:26.463401~22:28:25 KST**. 네 지점 모두 준비 확인, rc0, kernel drop0이며 아래 요청·만료 회수는 구간 안에 있다. 이는 해당 시점 기록의 대조이며 지속적인 무손실 보장은 아니다.

| 단계 (KST) | 실제 관측 | 근거 |
|---|---|---|
| 생성 22:24:11.058 | persisted CREATE1, `OWNED`, UID `1aea5509-d0ff-4c8c-a217-61a534d57601`, RV `5192531` | journal, supervisor, `raw/control01-canary-run-watch.json` |
| 443 22:24:39.763 | 1회 curl rc0, HTTP404, TLS검증0, `.108:45143→.30:443`, 네 지점 양방향 | `raw/worker03-443.json`, 네 캡처 |
| 8443 22:24:59경 | 직전 gate 재확인, 1회 curl rc28; `.108:45843→.30:8443` SYN worker5 / gateway-in5 / gateway-out0 / monitor0 | `raw/worker03-8443.json`, gate8443 영수증, 네 캡처 |
| 만료 22:25:41.047 | expiry trigger → UID/RV 조건부 DELETE1 → 22:25:43.094 readback404; 만료 후2.054초, 22:26:41 회수 기한 내 | journal DELETE_INTENT·DELETE_ACK·ABSENT, supervisor |
| 회수 후 22:26:01.943 | 새443 연결1회 rc28. TLS/CA/bind 오류 없음. worker NIC 새 SYN 미관측, 정확한 차단 hook 미확인 | `raw/worker03-post-deny.json`, worker 캡처 |
| 정책·MON 복귀 | HEP/hostGNP UID·RV·spec 및 GNP 목록 동일, gateway/monitor 설정 동일(nft counter 제외), worker 경로 동일 | policy pre/post, host별 pre/post, worker route-post |
| MON 시점별 확인 | 전·중·후23/23, remote-write 실패 15분 증가0; 사후heartbeat4.564초, 활성alert0 | `raw/control01-mon-portforward-*-remaining-read.json`, monitor post |
| 임시 정리 | Binding→Role→SA 생성UID 조건부 삭제 및 각 NotFound, token 파일 제거; 캡처 정상 종료 | `raw/control01-credential-cleanup.json`, control archive cleanup 원본 |

`ARMED`만으로 요청을 시작하지 않았다. watch를 먼저 시작하고 CREATE `OWNED`·UID/RV 확인 및 요청별 gate 통과 뒤 각각 한 번 요청했다. SYN5개는 같은 연결의 TCP 재전송이며 요청5회가 아니다. post-deny는 회수 뒤 별도 새 연결이다. 원래 background `.108:41308→.30:443`은 시험 연결에서 제외했다.

[H04 결정 원문](https://github.com/321Team/fds-project-baseline/pull/160#issuecomment-6083293377)은 **gateway 구간 귀속**을 요구하고 특정 nft rule counter/log/nftrace 추가를 요구하지 않는다. 해당 흐름에는 과거 “monitor01 SYN 도착 후 미응답” 조건을 적용하지 않는다는 결정이다. 그 대응은 다음과 같다.

| 요구/기존 증거 | 이번 보완 | 판정 경계 |
|---|---|---|
| 비승인8443 차단의 gateway 구간 귀속 | worker와 gateway 입구에서 같은 출발지/포트 SYN, gateway 출구와 monitor에서0; 같은 창443은 네 지점 양방향, drop0, 정책·경로 전후 동일 | **H04 gateway 구간 귀속 근거 확보**. 특정 nft rule 귀속은 주장하지 않음 |
| 기존 Source·wrong-auth401 | [증적#122](https://github.com/321Team/fds-project-evidence/pull/122)와 [재사용 결정](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6072071555) 유지 | 이번404 양성 대조를401 인증 시험으로 바꾸지 않음 |
| gateway 정책 구조 | [증적#151](https://github.com/321Team/fds-project-evidence/pull/151)과 이번 pre/post 원본 연결 | 설정만으로 패킷 차단을 입증했다고 하지 않음 |
| 만료·원복 | 조건부 자동회수·명시적 부재, post-deny 새연결 실패, 정책/MON 별도 비교 | 정상 만료 경로1회. 모든 실패/재부팅 경로 PASS 아님 |
| #14 ICR-AC12/15~17·#17 잔여 | 위 하위 항목을 원본에 연결 | **전체 AC/티켓 Done 미판정**. 원래 AC 문구는 유지하며 형식 변경 필요 시 해당 변경 절차로 분리 |

## 해석·검증 한계와 정정

- `ABSENT_BASELINE_UNVERIFIED`는 자동 실행기의 원문 상태로 보존한다. 자동회수는 canary 부재까지만 판정하며 기준 복귀는 별도 정책·MON·요청 증거로 확인했다. FINAL 줄과 `evidence_complete_before_write=true`만으로 FINAL의 fsync 성공을 증명하지 않는다.
- MON 수치/heartbeat는 시점별 표본이다. loopback port-forward는 기준선 API 읽기용이며 IF06B 통신 경로 증거는 네 캡처다. 캡처는 텍스트 헤더 출력이고 payload 출력/pcap 저장 옵션은 없었다. 실제 snaplen262144를96으로 표시하지 않는다.
- 로컬 최초 검증기가 실행안6.4에 없는 “post-deny SYN 반드시 관측” 조건으로 중단한 이력을 [정정 기록](raw/VERIFICATION_CORRECTION.json)과 `verification-history/`에 보존했다. 새 연결 rc28·관측되지 않은 SYN·미확정 차단 hook을 그대로 보고하며 서버 요청 재실행은0이다.
- 준비 전달 보조의 문자열 치환 오류1건은 원격 Python 파싱 단계에서 중단됐다([실패 영수증](raw/field-pre-helper-failed.json)). 그 호출의 현장 명령/RBAC/canary는0. 수정 후 정확한 전송 소스 구문을 확인했고 제품 실행기는 변경하지 않았다.
- [민감정보 검사](SENSITIVE_SCAN.json)는 편입 파일과 중첩 압축 내부를 검사했다. private key/JWT/client-key-data/literal bearer 패턴0. 공개 CA·token claim·계정/내부IP/credential 경로는 추적 목적으로 남긴다. 패턴 검사를 모든 비밀정보 부재의 완전한 증명으로 확대하지 않는다.
- `verify_runtime.py`는 최초 검증기에서 입력 루트와 출력 동작만 바꾼 읽기 전용 편입용이다. 원 검증 결과를 덮어쓰지 않고 시각 필드 외 결과 일치를 검사한다. 최초 검증기 사본은 `verification-history/verify_runtime.py`다.

## 오프라인 재확인 및 남은 단계

서버 접근 없이 이 폴더에서 수행한다(Python3 표준 라이브러리, `-O` 사용 금지).

```sh
sha256sum -c SHA256SUMS
python3 -B verify_runtime.py
```

저장소 루트에서는 `python3 tools/check-evidence-layout.py --base origin/main`으로 경로·봉인된 기존 회차·대장·압축본 목록을 확인한다. 현재 파일 무결성 확인은 실제 시험/독립 리뷰/AC 인수를 대체하지 않는다.

| 단계 | 상태 |
|---|---|
| 제품 STATIC/MOCK/CI | 기존 PR85의147 PASS/0 SKIP을 참조. 이번에 제품 시험을 다시 실행하지 않음 |
| RUNTIME | 이 문서의 단회 생성·만료 회수·정리·관측 범위 완료 |
| 편입 로컬 검증 | 오프라인 원본 재판독·복사 무결성·압축 목록·민감 패턴 확인. 실제 로그는 PR 본문/검증 결과 연결 |
| REVIEW / MERGE | 이번 증적의 독립 리뷰·병합 대기. 이재환(MON 인수·MON 영향), 이하영(H04·정책 경계·권한/회수)에게 한 PR로 요청 |
| PUBLICATION / AC | PR 제출은 검토용 발행; main 편입·최종 인수와 구분. #17/#14는 Open 유지 |

남은 것은 이번 증적 편입 검토와 해당 하위 결과의 인수 기록이다. Grafana 관리 principal/감사, 다른 Probe 행, ICR 부팅 연속 보호/OID 등 이 회차 범위 밖 잔여를 완료로 올리지 않는다. 한 번 허용된 canary는 소진됐으므로 자동 재실행하지 않는다. 서버 보안 통제 완화·서비스 재시작·새 permanent 정책·Phase 2 작업은 수행하지 않았다.
