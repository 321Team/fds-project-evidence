# AC09 APP 업무 증적 대조 — R1·R2 HTTP/계측 확인, DB 사후행 대기

2026-10-15 16:03 KST · 실행자는 CICD 단일 담당, 이 APP 세션은 기존 로컬 원문의 독립 분석만 수행했다. **R1·R2 각각 HTTP/FDS·같은 Pod 계측은 기준과 일치한다. 두 Transaction ID의 실제 DB행 대조는 미확인이다. AC09 완료·전체 인수는 선언하지 않는다.**

기준은 기존 실행 카드의 상태별 P01·동일 ID DB·같은 Pod 전후 counter 요구다. 원본 위치는 `deliverables/p1-cicd-ac09-preparation-20261015/runtime-1535/`. 복사한 60파일의 SHA256 및 receipt의 stdout/stderr/collector SHA·rc를 대조했다. [SOURCE_INDEX.json](SOURCE_INDEX.json), [독립 산출값](APP_RUNTIME_COMPARISON.json), [대조 코드](compare_app_evidence.py). 복사본에 실행용 collector가 있어도 import/실행하지 않았다.

## 단계별 대조표

| 항목 | R1 이전 이미지 | R2 현행 복원 |
|---|---|---|
| Actions 실제 회차 | [38693979785](https://github.com/321Team/infra-cicd/actions/runs/38693979785), Attempt1 completed/success | [38694721511](https://github.com/321Team/infra-cicd/actions/runs/38694721511), Attempt1 completed/success 로컬 결과 수신 |
| 배포 관측 | 15:44:35와15:49:07 두 관측에서 이전 digest·앱별Ready3·PodUID6 동일·restart0→0 | 15:58:07 최종 상태에서 현행digest·앱별Ready3·Pod6, 이전Pod 없음. before inventory와 같은UID6·restart0→0 |
| Health | engine3Pod 직접8001 및 API3Worker NodePort30080의 livez/readyz 모두200 | 같은 경로 livez/readyz 모두200, 업무metrics404. 전용9090/9091 모두200·up6 |
| 실제 POST | edge01→`http://10.1.93.50/api/v1/transactions`,15:48:19.494~.538,1건·retry=false·HTTP201 | 같은 경로15:56:29.930~.971,1건·retry=false·HTTP201 |
| FDS 응답 | detected=false, skipped=false, R01/R02/R04/R07 모두 triggered=false/detail=null | 동일 정상 결과 확인 |
| 같은 Pod 계측 | 전15:47:27 / 후15:48:20. PodUID/IP6 동일, process_start 및 counter_created 동일. 저장성공+1·평가+1·오류증가0 | before15:51:37와after 원문에서 같은6Pod·process_start/counter_created 동일. 저장성공+1·평가+1·오류증가0. R1과 R2는 서로 차감하지 않음 |
| 실제 DB 사후행 | NOT_COLLECTED. HTTP201·계수+1을 DB11열 실측으로 대체하지 않음 | NOT_COLLECTED |
| DB 사전0행 | 원 실행 `r1-post-attempt.json`에 NOT_COLLECTED_NORMAL_DB_CONSOLE_ONLY | `r2-post-attempt.json`도 같은 NOT_COLLECTED 기록 |
| catalog 기준 | 13:54:33 사용자 READ ONLY rc0, 파일6개 해시 일치·11열/인덱스/권한 대조 유지 | 동일 기준 재사용. 새 catalog 조회 없음 |

R2 신규 원문을 받아 해당 열을 갱신했다. 현행 상태·업무metrics404·전용200/target6 관측은 위에 연결했으나 자격증명/Job/Runner 회수·노출시간의 최종 판단은 CICD/SEC 단일 담당 결과와 연결한다. 이 APP 분석으로 실행·회수 완료를 대신 선언하지 않는다.

## R1 실제 업무 입력·응답

- account_id: `SIM_ac09_cd01e613d57641eb83548e9283d0f60d_P01`
- transaction_id: `22b7c46c-cd07-4539-a7fc-8890b67b12ee`
- deposit10000 KRW, source_ip=`198.51.100.10`
- occurred_at=`2026-10-15T06:48:17.993816+00:00` (=15:48:17.993816+09)
- 정상 응답 body323바이트 SHA256=`1a324c28ed3ec55bbc9761e692799c78e0fca8be8d8850143bcf08116aad1e4b`; decode·길이·SHA·4 Rule 중복/누락 없음을 확인했다.

[POST 원문](references/r1-post-one/stdout.json)은 실제 POST 1건이다. 같은 폴더 transport receipt의 `classification=PURE_READ_PRECHECK`는 공통 래퍼 메타데이터와 실제 동작이 맞지 않는다. **이 대조표는 실제 collector·method·payload·응답을 기준으로 POST/거래쓰기1건으로 분류**한다. 원본 메타데이터를 고치거나 조회0건으로 숨기지 않았다.

이 경로는 edge01 호스트에서 자체 nginx 주소로 요청한 것이다. 외부 Client가 실제 요청했다는 새 D04 증적은 아니다. 정상 입금1건은 출금·이체 이력 SELECT 또는 전체 Rule 경계 검증도 아니다. 기존 최소 표본 범위를 유지한다.

## R1 동일 Pod 전후 증가분

| Pod | 계측 변화 | 연속성 |
|---|---|---|
| transaction-api-54984f6ddd-vrdgh | 저장성공0→1, 저장실패/누락IP/FDS호출오류0→0 | UID `aa9a8926-af6b-49f6-b356-bb653f319906`, process_start 동일 |
| transaction-api-54984f6ddd-6nxts | 저장성공/저장실패/누락IP/FDS호출오류 모두0→0 | 동일 UID·process_start |
| transaction-api-54984f6ddd-ml225 | 위 네 계수 모두0→0 | 동일 UID·process_start |
| fds-engine-66b8c565c4-pr6rv | 평가0→1 | UID `195a4721-e44b-44d2-b252-842e838725e2`, process_start 동일 |
| fds-engine-66b8c565c4-flzbg | 평가0→0 | 동일 UID·process_start |
| fds-engine-66b8c565c4-nfssw | 평가0→0 | 동일 UID·process_start |

전후 각각 정확6개 target의 `up=1`도 확인했다. 해당 서비스가 실제 노출한 counter만 사용했으며 없는 metric을0으로 채우지 않았다. 양측 process_start/counter_created와 바깥 Pod 상태 관측을 함께 확인했다. 이 +1 계측은 정상1건과 일치하지만 Transaction ID label이 없으므로 특정 DB행의 내용 일치 증명은 아니다. 다양한 호스트의 시계를 하나의 정밀 latency로 합성하지 않으며 시각 계약 판단은 기존 CICD/SEC 증적을 소비한다.

## R2 실제 입력·계측 보충

- account_id=`SIM_ac09_3451e56c57bc490e8d156cede958229f_P01`, transaction_id=`1827bd8a-a921-49f9-83f7-22529e903451`
- deposit10000 KRW, source_ip=`198.51.100.10`, occurred_at=`2026-10-15T15:56:28.439537+09:00`
- 응답 body SHA256=`4edd368d5ef9a29bcdbefc04cf5817463665763c471dc85ed287fc3714417504`. [실제 POST 원문](references/r2-post-one/stdout.json)의 HTTP201·네 Rule false/detail null·detected/skipped=false를 직접 검증했다.
- transaction-api-666c98b5f5-xvqp2(UID `d448512c-6e60-49c4-b78f-f1b7ddb17088`) 저장성공0→1. engine-65479b5bf-qjqms(UID `d338c785-a352-4086-a8b0-2e9c0d128acf`) 평가0→1. 나머지 네 Pod의 해당 계수 변화0, API3개의 저장실패/누락IP/FDS호출오류 모두0→0.
- before inventory와 최종 상태에서6PodUID·imageID·ready/restart를 대조했다. metric process_start/counter_created도 전후 동일하다. 최종 상태의 두Deployment updated/ready/available/replicas가 모두3이고 old imageID는 없다.

## DB 사후 원본의 최소 보충 — 실행하지 않은 준비안

[DB_POST_READONLY_PREPARED.md](DB_POST_READONLY_PREPARED.md)의 정상 `server08@db01` 콘솔용 단일 블록을 준비했다. 기존11열과 정확 AC09 계정2개/확보 ID만 READ ONLY로 조회하며 statement3초·lock1초·외부45초, 원본/rc/시각/해시를 보존한다. 새 SSH·권한·업무쓰기를 포함하지 않는다. 중앙이 R2 실제 결과와 시점을 확정한 뒤 필요할 때 사용한다.

**R1·R2의 계정과 거래ID 모두 실제 POST 원문으로 결속했다.** 준비 SQL SHA256=`8bb9b1c3d32fea5c821064547341b369aebae6a0b8b3de6606a743dd8ff3694c`이며 콘솔 블록은 이 해시를 검증한 뒤에만 조회한다. 새 사용자 질문/DB 실행은 하지 않았다. 로컬 셸 문법 검사만 통과했으며 SQL 실제 실행 검증은 아니다. [입력 결속 기록](DB_READ_PREPARATION.json).

최소 반환은 DB 식별·읽기전용·rc와 두 phase의 계정별 행수 및11열이다. R1 exact ID와 입력값·FDS 결과를 대조하고 R2 수신 후 같은 방식으로 비교한다. **사후 SELECT로 사전0행을 소급 증명하지 않는다.** 기존 누락은 보존하며 DB11 인수를 다시 열거나 새 업무 표본/POST를 추가하지 않는다.

## 실제 수행 경계

이번 APP 세션은 로컬 파일 읽기·원문 복사/해시 대조·base64/JSON/계측 분석·SQL 초안과 문서 작성만 했다. 서버 관측0·POST0·DB연결0·Token/배포0. CICD의 실제 R1 거래와 APP 분석 세션의 실행 수량을 구분한다. R2 현행 복원·회수 우선순위에 개입하지 않았고 중앙/실행자/공통 대장/#30 파일을 수정하지 않았다.
