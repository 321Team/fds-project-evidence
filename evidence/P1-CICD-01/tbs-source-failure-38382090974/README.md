# 새 TBS 1회 — Source 수신 실패, 2026-10-13

이권욱 / CODEX_ASSISTED. **Run38382090974/Attempt1 FAILURE, `SOURCE_PRIVATE_FETCH_FAILED`(Git exit128). Test/Build/이미지 기동/Scan·Push·Deploy는 미실행이다.** 새 수정 이미지의 성공 여부나 앱·DB·전체 Delivery 인수를 판단한 결과가 아니다.

## 승인·버전·실행

- 사용자 결정: [19:15~22:40 KST TBS 1회 승인](https://github.com/321Team/fds-project-baseline/pull/168#issuecomment-6143263724). 실제 Job 시작 마감19:25, 자동 재실행 금지, Push·Deploy 제외. 이 회차 허용은 소진했다.
- [Run](https://github.com/321Team/infra-cicd/actions/runs/38382090974), [Job115244770236](https://github.com/321Team/infra-cicd/actions/runs/38382090974/job/115244770236), `cicd-runner01/server01_cicd-runner` UID1000. GitHub Job19:15:23~19:15:34 KST, workflow receipt19:15:27.791~19:15:28.114. 각 호스트·API 시각을 단일 정밀 시계로 간주하지 않는다.
- CICD `fadc07f18b5bf7febc8cf601fa138d8f35e9ccb4`; [PR76](https://github.com/321Team/infra-cicd/pull/76)·[PR77](https://github.com/321Team/infra-cicd/pull/77) 독립 승인·병합 후 [결합 CI](https://github.com/321Team/infra-cicd/actions/runs/38376834597) SUCCESS.
- APP 입력 `321Team/fds-msa@affbc69beef9967f7977d09a6fec14f7fb6c0e94`, 기존 두 앱. config SHA256 `72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3`, workflow SHA256 `40a5dcd56b0bb6feb816bb297eb27bb747524181e914dcf514d614492ace2982`.
- 19:14 실제 사전검사: home/공급 디렉터리 UID1000·0700, 약48GiB 가용, Runner.Worker0, Podman6.1.0, 공급 manifest `6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4` 일치. GitHub main·6파일·Runner idle·Secret 등록 존재 재조회.
- Secret 존재 확인은 실제 인증 성공을 입증하지 않는다. TBS workflow 자체의 첫 Private fetch가 실제 인증 시도였다.

## 원본 결과와 한계

`run-38382090974/`는 서버의 `result.json`, `SHA256SUMS`, 세 단계 로그를 원래 바이트 그대로 수신한 자료와 GitHub Run/Job/로그다. 서버 원본은 `/home/server01_cicd-runner/FDS_CICD_AppWorkflow.4_alowtt`에 보존했다.

| 확인 단계 | 실제 결과 |
|---|---|
| Workflow/checkout | 새 회차·승인 main 결속 성공 |
| Source init/origin | 각각 exit0 |
| Private source fetch | exit128, `SOURCE_PRIVATE_FETCH_FAILED` |
| Handoff/Test/Build/기동/Scan | NOT_EXECUTED, handoff와 build-scan 디렉터리 없음 |
| Push/Deploy/DB/Harbor 변경 | NOT_EXECUTED |
| 사후 원본/정리 | result·각 단계 log 해시 일치, Worker0. 이미지 기동 CID 생성 단계에 도달하지 않아 컨테이너 정리 NOT_APPLICABLE |

result SHA256 `f8a129fe694bca53a1e27a961e093c7b18068b1b6aba1030cb0d255e97a56d96`. 무결성 확인을 시험 PASS로 바꾸지 않는다. 기존 Deploy claim1/checkpoint9는 재사용·삭제하지 않았다. 이번 조회는 운영 앱 Ready/업무 회귀 재검증이 아니다.

`source-fetch.log`는 종료 코드와 `RAW_OUTPUT=DISCARDED`만 기록한다. [검토된 인증 처리](https://github.com/321Team/infra-cicd/blob/fadc07f18b5bf7febc8cf601fa138d8f35e9ccb4/tools/delivery/source_auth.py)가 토큰 노출 방지를 위해 Git stdout/stderr를 폐기하므로 이 결과만으로 만료/권한/SSO/401/403/404/TLS 원인을 특정할 수 없다. 토큰 값·hash·인증 헤더를 수집하지 않았다.

19:16 실패 후 순수 읽기 통신 확인은 DNS 해결, 검증된 TLS의 github.com HTTP200, **익명** Private Git endpoint HTTP401이다. 이401은 실패한 **인증 fetch의 응답 코드가 아니다**. 별도 워크스테이션 인증 경로에서 승인 APP Commit 존재도 재확인했다. Actions Secret metadata의 created/updated는9/18로 같지만 만료일·권한·조직 승인·유효성을 뜻하지 않는다. SSH 조회 환경과 Actions Job 환경이 같다고 단정하지 않는다.

## 후속 조치

1. 기존 발급 담당 경로에서 `CICD_APP_SOURCE_READ_TOKEN`의 실제 만료·대상321Team/fds-msa·Contents Read-only/Metadata Read-only·조직 승인 상태를 확인한다. 값/스크린샷/토큰 hash를 댓글·Git에 넣지 않는다. 일반 사용자 gh 자격증명이나 classic repo 권한으로 자동 대체하지 않는다.
2. 필요한 회수/재발급은 기존 승인된 최소 권한 경로로 별도 처리하고 비밀 외 확인 근거를 남긴다. 이번 회차에서 자격증명 변경·Token 발급은 수행하지 않았다.
3. 정상 접근 준비 후 새 회차 수·시간창을 확정한다. 이번 창의 남은 시간이 추가 Run 허가는 아니다. 기존 실패 디렉터리·Run·claim을 재사용하지 않는다.
4. 새 Test/Build/두 이미지 비루트 기동/Scan 성공 후 새 Push 입력을 만들고, 이후 Deploy→최소 HA/복귀→최종 앱 회귀→DB 인수 판단 순서를 유지한다. W4 NOT_MEASURED는 보존한다.

## 수집·검증 경계

collector는 기존 strict SSH 경로를 사용한 **PURE_READ_PRECHECK, REVIEW=NOT PERFORMED (Pre-check)**다. Python 표준 라이브러리로 정해진 metadata/원본만 읽었고, 호스트 설정·권한 변경·설치·Secret 조회·부하/장애 주입은 하지 않았다. 수집 명령·시간·계정·collector SHA256·출력 hash는 각 receipt에 남겼다. `tbs_control.py`는 로컬 실행 기록 사본이며 서버에 설치하거나 새 runtime workflow로 반영하지 않았다. 원문에서 당시 cwd를 기준으로 사용한 코드이므로 증적 폴더에서 재실행하지 않는다.

`SHA256SUMS`는 이번 편입 파일 무결성용 manifest이며 서버 원본 manifest와 구분한다. STATIC/layout 검사와 실제 Source fetch FAILURE를 구분한다. 증적 독립 REVIEW/MERGE와 Phase1 최종 인수는 미완료다.
