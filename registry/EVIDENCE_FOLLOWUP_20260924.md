# Evidence 잔여 작업 — 2026-09-24 착수 결과

## 현재 상태 — 2026-09-25 갱신 (main `4d2db33` 기준)

이 절이 최신이다. 아래 "2026-09-24 착수 결과" 이하는 2026-09-24 04:33 KST 기준 기록이며 당시 표현을 보존한다.

### 증적 정책·점검 도구

- [#30](https://github.com/321Team/fds-project-evidence/pull/30) 병합(`b676375`, 09-25 10:48 KST): 중앙 정책 반영, `evidence/<Record ID>/` 경로 통일, 파생 이슈 경로, 해시 대장 범위, 압축 파일 조건(1MB 이하·sidecar·`registry/ARCHIVE_CONTENTS.json`), 예외 목록, 병합된 수집회차 보호(SEALED), PR 자동 점검(`evidence-layout`).
- 리뷰 후속 [#39](https://github.com/321Team/fds-project-evidence/pull/39)(Manifest 폴더 밖 항목·빈 Manifest 경고)는 재확인 대기다.

### 2026-09-24~25 병합된 증적 PR

| PR | 내용 | merge | 독립 검토 |
|---|---|---|---|
| [#22](https://github.com/321Team/fds-project-evidence/pull/22) | P1-CICD-01 Run35683010080/1 BLOCK 수신·원본 압축 2개 | `4b78bd2` | 이하영, 이재환(사람 확인) |
| [#23](https://github.com/321Team/fds-project-evidence/pull/23) | ICR-D-NET-01-01 5개 수집회차·원본 압축 5개 | `87c70e4` | 이하영 |
| [#24](https://github.com/321Team/fds-project-evidence/pull/24) | P1-CICD-01 Ansible PR47 readiness·구문 46/46 | `67addd8` | 이하영(재확인 포함) |
| [#26](https://github.com/321Team/fds-project-evidence/pull/26) | P1-CICD-01 앱 후보 Build/Scan BLOCK, 278MB 원본 팀 공유 디렉터리 보관 | `6cb2a4f` | 이하영, 이재환(사람 확인) |
| [#27](https://github.com/321Team/fds-project-evidence/pull/27) | P1-ANS-01 infra-ansible #9 호출 경로 | `7f96c59` | 이하영(재확인 포함) |
| [#31](https://github.com/321Team/fds-project-evidence/pull/31) | P1-DB-01·MON-01·E2E-01 외부 아티팩트 참고 사본 | `5535c9f` | 이하영 |
| [#32](https://github.com/321Team/fds-project-evidence/pull/32) | P1-LB-01 DAD·Stage B 원본 86개·원본 압축 2개 | `fb41ffe` | 이하영 |
| [#33](https://github.com/321Team/fds-project-evidence/pull/33) | P1-SEC-01 Gate 2 실행 기록 참고 사본 | `455d1c1` | 이재환 |
| [#35](https://github.com/321Team/fds-project-evidence/pull/35) | P1-K8S-01 CR-P1-NTP-01-01 읽기 전용 재수집 | `b803b9b` | 이재환(사람 확인) |
| [#36](https://github.com/321Team/fds-project-evidence/pull/36) | P1-K8S-01 CR-P1-NTP-01-01 이전 실행 원본 7개 | `4d2db33` | 이하영 |
| [#38](https://github.com/321Team/fds-project-evidence/pull/38) | P1-DNS-01 PR #16 후속 정정 기록(squash) | `c99de09` | 이하영 |

- 병합은 증적 보존이다. 각 티켓의 AC·Status·Runtime 판정은 바꾸지 않았다. 특히 P1-CICD-01의 CVE BLOCK(HIGH 44)은 예외 없이 해소해야 하며([infra-cicd #11](https://github.com/321Team/infra-cicd/issues/11#issuecomment-5817229485)), 해소 결과는 새 Build/Scan 회차로 제출한다.
- #26은 병합 전 PR CI가 실행되지 않았다. 병합 커밋 메시지의 "CI success"는 오기이며 [정정 댓글](https://github.com/321Team/fds-project-evidence/pull/26#issuecomment-5826837827)을 남겼다. 병합 전후 로컬 점검은 PASS다.
- #36의 원본 3건은 ansible01에서 다른 출처로 해시를 대조해 모두 일치했다: [교차 대조 기록](../records/post-merge-20260925/P1-K8S-01_NTP_ORIGINALS_HASH_CROSSCHECK.md).

### 열린 PR과 남은 입력

| 항목 | 상태 | 다음 |
|---|---|---|
| [#37](https://github.com/321Team/fds-project-evidence/pull/37) P1-DB-01·MON-01·E2E-01 Lead 직접 재수집 | 이하영 [수정 요청](https://github.com/321Team/fds-project-evidence/pull/37#pullrequestreview-5313449647)(`0110c05`): 정리본을 원본으로 표기, PR 코멘트 참조, 미수신 항목 미기재. main 충돌 해소(`ede08d6`) 후 작성자가 서버 원본 출력으로 교체(`d2096ab`) | 이하영 재검토 |
| [#39](https://github.com/321Team/fds-project-evidence/pull/39) 점검 도구 후속 | 정정 반영, 재확인 대기 | 이하영 재확인 |
| 이 PR(#25) | 이 절로 갱신 | 이하영 독립 리뷰 |
| [evidence #34](https://github.com/321Team/fds-project-evidence/issues/34) P1-SEC-01 원본·보안 후속 | 미제출 | 이하영 |
| baseline #10·#11·#17·#19·#20·#21 증적 보완 요청 | 담당자 회신 대기 | 각 Lead(#37이 #11·#17·#20 일부 대응) |

### 현재 main 점검

`check-evidence-layout.py`: PASS(추적 파일 3,135개, 오류 0건). `sha256sum -c REGISTRY_SHA256SUMS` OK. `registry/ARCHIVE_CONTENTS.json` 압축 파일 39개.

---

조회·검증 기준: 2026-09-24 04:33 KST (2026-09-23 19:33 UTC). main 기준 `9a3d03341d8878f43e97d5ab9fc040b0037c9250`. 진행 중 새로 확인한 PR24까지 반영했다.
사용자 요청: “evidence 잔여 작업 착수”. 수행: GWONUK 계정의 CODEX_ASSISTED 정리·검증·병합. 이번 자체 점검은 독립 사람 리뷰가 아니다.

## 완료한 편입

| PR | 독립 검토 근거와 범위 | 실제 결과 |
|---|---|---|
| [#17](https://github.com/321Team/fds-project-evidence/pull/17) 종결 티켓 증적 공백 | 이하영의 [정식 APPROVED](https://github.com/321Team/fds-project-evidence/pull/17#pullrequestreview-5289484157)는 `e9cae7a` 기준. 이후 오타·해시 정정 HEAD `c9f61aa074611608ae4259f980842dbaea1aeaee`에 대한 [재승인 댓글](https://github.com/321Team/fds-project-evidence/pull/17#issuecomment-5793175657)을 별도로 확인 | 04:24:41 KST 병합, [`9cb70bda262ecff22c519d8b7ed6102b8d8bd587`](https://github.com/321Team/fds-project-evidence/commit/9cb70bda262ecff22c519d8b7ed6102b8d8bd587) |
| [#21](https://github.com/321Team/fds-project-evidence/pull/21) Squid 설명 정정 | 이하영의 [정식 APPROVED](https://github.com/321Team/fds-project-evidence/pull/21#pullrequestreview-5292027346), 정확한 HEAD `a7346935bd901e7e5489d888a7f7a2f155ad3a04` | 04:25:13 KST 병합, [`9a3d03341d8878f43e97d5ab9fc040b0037c9250`](https://github.com/321Team/fds-project-evidence/commit/9a3d03341d8878f43e97d5ab9fc040b0037c9250) |

PR17은 기록 4파일 범위다. 변경한 대장 2개의 SHA-256을 다시 계산해 일치시켰으며, 병합 후 현재 루트 Manifest의 기존 2,187항목이 모두 남고 해당 해시 2줄만 바뀐 것을 확인했다. 신규 공백 문서는 해당 PR의 검토 범위대로 루트 Manifest에 포함하지 않았다. 전체 2,187파일을 이번에 다시 해시 계산한 결과로 표기하지 않는다.

PR21은 README 1파일 범위다. 원본 precheck의 `tree=dirty`, 후속 4단계의 `tree=clean`, 5단계의 `rc=0`을 직접 대조했다. 로그 6개·원본 Index·원본 Manifest의 Git blob 8/8 보존과 내부 SHA-256 7/7 일치를 확인했다. Worker 후보 주소 3개를 proxy가 모두 실측한 post-SNAT 주소로 확대하지 않는다.

각 병합 후 main 전체 Git tree를 직전 main과 대조했다. PR17의 4파일과 PR21의 1파일 외 변경·삭제는 없으며 최종 main은 2,530개 blob이다. 두 PR의 GitHub check-runs/statuses는 각각 0건으로 **CI NOT RUN**이다. 기존 리뷰어·작성자의 과거 시험 기록과 이번 자체 검증은 구분한다.

## 열려 있는 증적 PR과 다음 입력

아래 무결성 수치는 각 PR의 수신 검토 기록에 보고된 값이다. 이번 관리 정리에서 전체 원본을 다시 수집·검증한 값은 아니다.

| PR·검토 HEAD | 확보된 근거 | 남은 작업·완료 기준 |
|---|---|---|
| [#22 CICD](https://github.com/321Team/fds-project-evidence/pull/22), `a6aa1d86723051fcb30196d7f26223b8d1cf7683` | Run35683010080/Attempt1 수신 18파일, 내부 Manifest17/17; receipt 검증 PASS. 원 실행 APP_WORKFLOW=BLOCK, HIGH57/CRITICAL3, fds-engine NOT_SCANNED, Runtime AC1/10 | GWONUK: 기존 collect stdout/rc·종료 화면·서버 수집 시각을 기존 출력 폴더에서 확보하고 archive 접근을 인계. 요청된 Reviewer 이하영: 정확한 HEAD의 원본 출처·누락·판정 범위 독립 검토. 이후 증적 병합 판단 |
| [#23 ICR MON](https://github.com/321Team/fds-project-evidence/pull/23), `2f8a238142ad669a35800bb3e8ecc6d372354d60` | 01:21·02:05·02:40 KST의 세 회차 46파일. counter 보완 수집 완료, worker01 host GNP source .108 매칭 및 DROP46 packets/2,760 bytes 증가 | GWONUK: 세 archive의 독립 검토자 접근 경로 인계 및 적격 Reviewer 연결. 정확한 HEAD의 3회차 원본·수집 source·분석 한계 독립 검토 후 병합 판단 |
| [#24 Ansible PR47](https://github.com/321Team/fds-project-evidence/pull/24), `1eaa62b6ce96f4e7090da6201e2a6dd56d25648d` | 02:00:56~58 KST cicd-runner01의 기존 PREPARED·rootless image 수신, 11파일 추가·내부 Manifest6/6. PASS_PREPARED_IMAGE_READINESS | GWONUK: 적격 Reviewer 연결. 원본 무결성·source·검사기 보고 한계·과거 완료 범위 보존을 독립 검토한 뒤 편입 판단 |

- PR22는 reviewer 요청이 있지만 실제 제출된 독립 리뷰는 0건이다. raw payload는 포함되지 않았다. 수신 검증 성공은 원 Workflow 성공이나 Push/Deploy 완료를 뜻하지 않는다. 서버 수집 시각은 원 Actions 실행 시각으로 대체하지 않는다.
- PR22 원 archive: 7,367 bytes, SHA-256 `11578ae33211f569df91830a2b26314c01ffcaea70a67dc7165f9e3dad4b1c79`. 파일 식별자·기존 보관 경로는 [수신 README](https://github.com/321Team/fds-project-evidence/blob/a6aa1d86723051fcb30196d7f26223b8d1cf7683/evidence/P1-CICD-01/run-35683010080-attempt-1/received-20260924/README.md)에 있다. 식별자 기재만으로 Reviewer 접근 확인을 완료 처리하지 않는다.
- PR23은 실제 독립 리뷰 0건, 요청된 Reviewer 0명이다. 새 수집 source `91b9792e0e276c0f97c36a0124fda14cf56a6b3b`의 query9/9 성공과 counter 보완을 기존 02:05 PARTIAL과 분리한다. 같은 수집을 반복할 필요가 없다.
- PR23 counter archive: 60,846 bytes, SHA-256 `85e57eb5ab91562209538677fe1658fa4e3c6e6bc4810371a93d0d19f550ef47`. [수신 README](https://github.com/321Team/fds-project-evidence/blob/2f8a238142ad669a35800bb3e8ecc6d372354d60/evidence/ICR-D-NET-01-01/scrape-counters-20260924T024027/README.md). 02:05의 64패킷과 02:40의 DROP46을 동일 모집단으로 합치지 않는다.
- PR23의 세 source는 `REVIEW=NOT PERFORMED (Pre-check)`다. 이 증적 PR의 독립 리뷰는 별도 필수다. host-policy DROP 관측을 통신 복구, target API/TLS/Auth, 음성 workload, IF-06B 또는 AC07 인수로 확대하지 않는다. 운영 후보 [infra-kubernetes PR27](https://github.com/321Team/infra-kubernetes/pull/27)의 검토·적용 판단은 해당 Lead 범위다.
- PR24는 실제 독립 리뷰 0건, 요청된 Reviewer 0명이다. 원 archive 1,361 bytes, SHA-256 `d58c76fa3818c30f273115d4f18b515aeb8ed079b6e6ab712ba7fa7d598f1153`. source `c6ba5f87711acc3eeeba12c13c72cedd09d178f8`은 현재 독립 APPROVED가 없고 Run35889332032/1은 skipped다. PREPARED/image inspect 원문 미포함 한계가 있으므로 검사기 보고를 일반 CI PASS·격리/IPC·새 Runner 등록·infra-ansible #5 완료로 확대하지 않는다. 새 prepare·이미지 build·기존 격리 Actions 반복은 필요하지 않다.
- 현재 세 PR은 Draft다. 이 기록 정리는 세 브랜치의 원본·본문·수신 분석을 변경하지 않는다.

## 공통 FUP — 이미 완료된 항목 반영

[추적 이슈 #4](https://github.com/321Team/fds-project-evidence/issues/4)의 기존 담당·미확보 범위를 유지한다.

| 항목 | 확인된 상태 | 다음 입력·처리 기준 |
|---|---|---|
| 기존 매핑 PR7 | 2026-09-23 18:53:28 KST main 병합, [`d1c8e1a7b10568fb00ff8dd573d0d7972f784dab`](https://github.com/321Team/fds-project-evidence/commit/d1c8e1a7b10568fb00ff8dd573d0d7972f784dab) | Index10 종결 문서·09 IP 예외·03~06의 8/28 보완 원본 매핑은 편입 완료. 같은 매핑 재승인·재제출 불필요 |
| FUP-04 | 8/26 최초 로그·Windows/VMware 캡처·관리 VM/gateway 전문 일부 미확보 | GWONUK/자료 보유자: 당시 파일 또는 정확한 기존 보관 위치 제공. [탐색 후보](../runbooks/FUP-04-09_REMAINING_SOURCE_ACTIONS.md)는 실제 저장 위치 확인과 구분 |
| FUP-05 | 과거 개별 승인 근거 미확인 | GWONUK: 당시 Reviewer/Approver·일시·범위가 보이는 기존 회신 또는 고정 참조 연결. 승인 시각·서명을 새로 만들지 않음 |
| FUP-06/07 | 후보 편입·한계 수용 완료, 정본 APPROVED 메타데이터 연결 완료 | GWONUK: 개인별 회신·정확한 시각과 WBS 실제 열람 근거 확인. 기존 편입 재승인 요구 없음 |
| FUP-08 | 원본 수신·편입 완료 | 추가 재검토·재수집 대상 없음 |
| FUP-09 Permanent | [9/16 인수 회신](https://github.com/321Team/fds-project-evidence/issues/4#issuecomment-5697474151)에 따라 수용 범위의 조건 해소 | 해소 범위 유지 |
| FUP-09 DAD | 현재 시점 보완 원본 확보. [infra-lb PR2](https://github.com/321Team/infra-lb/pull/2)는 9/21 병합, `134dfbd643b143a6d639bbc33b32b7cee2555f7f` | [독립 리뷰](https://github.com/321Team/infra-lb/pull/2#issuecomment-5757405743)는 증적 편입만 승인했고 LB-A-01 잔여 인수 조건 해소는 범위 밖이라고 명시. 해당 Lead의 현재 보완 결과 수용 범위·남은 조건을 이슈에 기록 |

infra-lb PR3도 9/21 `1f7c13f2d339b98aad36a245c6f765fb97e7219c`로 병합됐다. 이를 PRECHECK_NOT_READY 해소나 Stage B 완료로 해석하지 않는다. 8/31 역사 원본 미복구와 현재 시점 DAD 보완 원본 확보는 별개의 사실이다.

## DB 증적 이슈 #8

[evidence PR2](https://github.com/321Team/fds-project-evidence/pull/2)는 2026-09-09 12:44:16 KST [`36a65c64763077eabe680b81827b1c4dc6ad3fc5`](https://github.com/321Team/fds-project-evidence/commit/36a65c64763077eabe680b81827b1c4dc6ad3fc5)로 병합됐다. 따라서 [이슈 #8](https://github.com/321Team/fds-project-evidence/issues/8)의 과거 “PR 병합 미완”은 현재 상태가 아니다.

증적 편입 완료와 운영 db01 schema/revision·0002 적용 방식, 정본 Source 거부 시험·IF-04, 백업 무결성·Restore 후 Final E2E는 분리해 추적한다. 잔여 실행·인수의 정본은 [DB #11](https://github.com/321Team/fds-project-baseline/issues/11) 및 [DR #21](https://github.com/321Team/fds-project-baseline/issues/21)이다. 이번 정리는 DB 서버 재검증이나 잔여 AC 전수 재판정이 아니며 기존 체크를 일괄 완료 처리하지 않는다.

## 관리 문서 정정과 경계

README·수신 대장·FUP 실행표·완료 티켓 대장에 이 기록으로 연결되는 현재 상태 안내를 추가한다. 기존 날짜별 수신 원문·승인·종결 이력은 보존한다. 기존 완료 티켓 편입 대장 13개와 PR17의 2026-09-19 CLOSED 18건 조회 범위는 다른 집계이므로 합치지 않는다.

이번 관리 문서 PR도 [EVIDENCE_POLICY](../governance/EVIDENCE_POLICY.md)의 독립 검토를 마친 뒤 병합한다. 이는 main 직접 갱신이 아니며 새 원본 수신·Runtime 실행·AC 인수·정본 발행을 완료한 기록이 아니다. 새 사람 확인 서명이나 과거 승인자는 생성하지 않는다.
