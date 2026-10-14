# 최종 APP 회귀 실제 실행 — RUN 202610141025

이권욱 / CODEX_ASSISTED. 2026-10-14 KST. API·metrics/형상 검증과 DB 실조회·최종 인수 단계를 구분한다.

## 허용·입력·실행

- 사용자 기존 승인: PR86 실행 카드의 APP 10:25~10:35 실제 시작,11:15 수집 종료, 기존 두 앱/도구 1회, 자동 재실행 없음. 콘솔 대기·Harbor/H6/APP/DB/MON 변경 및 다른 거래 writer 비중첩·DB 콘솔 조회 가능을11:15까지 확인했다.
- 선행: evidence#221 HA 증적 병합851c3827, infra-kubernetes#86 실행기 병합e60e0223. 09:50 engine HTTP Probe1회 후 서비스·MON 회복은 PR223(e2d6d5aa) 원본으로 확인했다. 해당 증적은 supreme33-kr가 정확한 HEAD를10:24:43에 독립 승인했고10:25:58에 ddd1e38c1c07d7d0dd99281df8e619c317db764b로 병합됐다. 편입 병합 시각은 이번 APP 요청 종료 후이며, 당시 진입 근거인 기존 코드 승인·실제 회복 관측과 구분한다.
- APP 도구: fds-msa#30의 이하영 독립 승인 SHA61fbf0bf1ace1fa3a5eb983c002de2a0ddac856a, mergec2372da3. rg.py SHA256 f5dee1069ab96838355cf6269dd6cdff2a08107e880594c5dad98d20424594ed를 Git/기존 공급본/edge공급본/수신본과 대조했다. 도구를 변경하지 않았다.
- 사용자 DB 사전 콘솔:10:20:30.353457, db01/server08→postgres/fdsdb, READ ONLY·5초 statement timeout, 정확한 RUN 범위202610141025~202610141035 count0, DB_BEFORE_RC0. 앞선10:09 결과와 echo 겹침도 별도 보존한다. DB 자료는 사용자 제출 텍스트이며 직접 SQL 실행/서버 파일 해시 검증이 아니다.
- 10:24 사전 GET: 두 Deployment image/spec/generation, Pod6 UID·배치·restart(Probe 대상1/기타0), API Local endpoint Worker별1, Node 정상, MON23/앱6, 거래/평가/실패/IP누락 counter0. 미생성 Rule series는 이전 metric 정의·target 정상·평가0 근거로0 해석하고 empty vector를 보존했다.
- edge01 uid1003 기존 strict SSH 경로에서 `/home/svc_ansible/p1-app-20261014-1025/supply/rg.py run /home/svc_ansible/p1-app-20261014-1025/results` **1회**. root권한/새 Secret/권한·보안설정 변경 없음. 디렉터리0700·파일0600. 자동 재실행0.
- 기준/meta가 첫 요청 전에 기록됐다. criteria SHA256 `5fce797a0e10b8c68feda908cbc4573b9dda9bc2b8e621b4ebd6e04ed1ca8e7d`. 실제 RUN202610141025는 사전0행 범위 안이다.

## 확인된 결과

| 항목 | 실제 결과 |
|---|---|
| 실제 POST |10:25:10.907~10:25:11.403,25요청, 재시도0 |
| API |24PASS/0FAIL/1INFO, run rc0 |
| HTTP |201×23(고유 Transaction ID23), N06/N07 422×2, 5xx/연결실패0 |
| 정상 평가 |201응답의 skipped=false, Rule/boolean 계약 대조 |
| metrics |save_success+23, evaluated+23, save_failure0, missing_client_ip0 |
| 탐지 |R01/R02/R04/R07각+1; I01은201·탐지false,INFO유지 |
| 사후 상태 |Pod UID/restart/image·Deployment generation/spec·Service불변, API3/engine3 Ready, 각 Worker1/1, MON23/앱6정상 |
| 업무 경계 |edge→Worker3 ready200·업무 metrics404, edge localhost80 ready200 |
| N08 |10:13 control01→Worker3 NodePort GET각000(URLError), 특정 규칙 귀속/경로 전체 deny 증거로 확대하지 않음 |

API·metrics/형상 및 DB 사후 대조까지 통과했다. `verify_runtime.py`는 네트워크 요청 없이 수신 원본에서 기존 rg.py의 판정/결속 검사를 재사용하고 metric delta·Pod/설정 동일성과 DB23행을 대조한다. 기존 `judge.txt`를 덮어쓰지 않는다.

## DB·한계·후속

- 사용자 db01 사후 콘솔(10:30:13.242908, fdsdb/postgres, DB_AFTER_RC0)에서 실제 RUN의8열23행을 수신했다. 기존 승인 rg.py crosscheck rc0: **DB23행/HTTP201응답23건/불일치0**. 거래ID·계정·유형·금액·탐지·Rule·skipped가 일치하고 201인데 미저장/응답 밖 추가행/중복ID0이다. 자료 출처는 사용자 제출 콘솔이며 직접 DB접속이나 서버 원본 해시 대조로 표시하지 않는다.
- I01의 timezone 없는02:30 입력은 INFO다. 이번 API201/탐지false/skippedfalse이며, DB occurred_at은 `2026-10-14 11:30:00+09`로 표시됐다. 명시적 offset 사례 P05/N03은02:30+09, N02는05:00+09와 일치한다. 이 관측을 새로운 timezone 정책이나 I01 자동 인수 기준으로 바꾸지 않는다.
- 직접 시험 경로는 edge01→WorkerNodePort다. Client→LB전체 E2E·DB 장애·누락 패킷·모든 Namespace 보안 검증을 이 결과로 확대하지 않는다.
- 실제 기능 시험 데이터는 기존 보존 결정에 따라 남긴다. DELETE/rollback/Deploy/추가 장애 주입0.
- 새 증적 독립 검토/병합, APP/E2E 최종 인수·DB#11 판단은 별개다. DB#11의 사용자 결정 `최종 앱 회귀 후 판단`과 W4전체HTTP5xx NOT_MEASURED를 유지한다. 관련 티켓을 자동 종결하지 않는다.

## 원본 재현과 보존

`remote-originals`는 edge 서버31파일을 byte그대로 수신했으며 `remote-results-receipt`의 Base64·원격SHA·mode/uid와 대조한다. `before-*`/`after-*`의 collector·strict SSH argv·시각·rc·stdout/stderr hash가 수집 범위를 고정한다. 사용자 DB 콘솔 텍스트는 별도 출처로 보존한다. 원격 경로·claim/거래를 삭제하거나 같은 RUN으로 다시 요청하지 않는다.

재현은 `python -I -B verify_runtime.py <이 수집회차 경로>`만 사용한다. `invoke_once.py`/`prepare_source.py` 등은 당시 수행 기록이며 재실행하지 않는다. 순수 GET/검증기 코드의 자체 검토는 독립 코드 리뷰가 아니며 `REVIEW=NOT PERFORMED (pure validator)`로 구분한다.
