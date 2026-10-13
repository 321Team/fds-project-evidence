# 토큰 교체 후 TBS — 기동 전 inspect 실패, 2026-10-13

이권욱 / CODEX_ASSISTED. **Run38388390767/Attempt1은 소스 인증·handoff·앱 시험51개·API Build/save를 통과했지만 첫 inspect가 exit125로 실패했다. 컨테이너 start/probe·engine Build·Scan은 미실행이며 Push·Deploy도 하지 않았다.** 전체 TBS 성공·APP/E2E/DB 인수 결과가 아니다.

## 승인과 실행 식별

- [새 실행안](https://github.com/321Team/fds-project-baseline/pull/168#issuecomment-6144160243), [사용자 승인 기록](https://github.com/321Team/fds-project-baseline/pull/168#issuecomment-6144183623): 2026-10-13 20:10~23:35 KST, 실제 시작 마감20:20, 새 Run1회, 자동 재실행 금지, Push·Deploy 제외. **이번1회는 소진했다.** 남은 시간은 추가 실행 허가가 아니다.
- [Run38388390767](https://github.com/321Team/infra-cicd/actions/runs/38388390767), [Job115265751500](https://github.com/321Team/infra-cicd/actions/runs/38388390767/job/115265751500): 20:10:32~20:11:19 KST. 서버 workflow receipt20:10:36.749~20:11:15.069. 서로 다른 호스트·API의 시각을 하나의 정밀 시계로 간주하지 않는다.
- `cicd-runner01/server01_cicd-runner`, UID1000, Podman6.1.0. 20:09 사전 읽기에서 home/공급 디렉터리0700·UID1000, 약48GiB 가용, Worker0, 공급 manifest 일치를 확인했다.
- 실행 CICD `fadc07f18b5bf7febc8cf601fa138d8f35e9ccb4`, APP `affbc69beef9967f7977d09a6fec14f7fb6c0e94`. PR76/77 독립 승인·병합 및 [결합 CI](https://github.com/321Team/infra-cicd/actions/runs/38376834597)를 재사용했다. 수정 PR78 코드를 이 Run에서 실행한 것은 아니다.
- config SHA256 `72eb52594048aa713ade12621f4545def0395f3f1603adec7bab3385b24f13e3`, workflow SHA256 `40a5dcd56b0bb6feb816bb297eb27bb747524181e914dcf514d614492ace2982`.
- 공급 경로 `/home/server01_cicd-runner/FDS_CICD_Runtime/FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a`, manifest SHA256 `6ab02000437a7b5f7d3c99e5202d40b663056a998018a1894360c58de68b73d4`.

## 자격증명 확인 범위

사용자가 토큰 교체 완료와 만료일2026-11-12를 확인했다. 정확한 만료 시각·시간대는 받지 않았다. GitHub Secret metadata의 updated_at은20:03:38 KST다. **새 Run의 전용 소스 인증 fetch exit0**을 실제 확인했으므로 직전 인증 차단은 이번 소스 수신 범위에서 해소됐다. 권한 전체·조직 설정 전수나 다음 실행의 유효성을 보증하지 않는다. 토큰 값·hash·인증 원문을 조회하지 않았다.

`TOKEN_REPLACEMENT_READBACK.json`의 인증 미검증·새 승인 전 표기는20:05 당시 기록이고, `USER_AUTHORIZATION.json`의 실행 전 표기도 당시 기록이다. 사후 문구로 원본을 덮어쓰지 않는다. 기존 실패 Run38382090974/증적 PR215도 그대로 보존한다.

## 실제 결과

| 단계 | 관측 결과 |
|---|---|
| Private Source/handoff | exit0 / PASS, 승인 APP Commit 일치 |
| 앱 시험 | engine Unit16 + API Contract20 + engine Contract15 = 51 PASS. API Unit은 기존 APP Source별 승인에 따른 NOT_APPLICABLE |
| API Build/save | exit0, API archive/config/manifest identity 생성 |
| API 격리 컨테이너 | create exit0 → 첫 inspect exit125. start/probe 미도달, 기동 PASS 아님 |
| engine Build/기동·Scan | NOT_RUN |
| Push/Deploy·업무 DB 변경 | NOT_EXECUTED |
| 소유 자원 정리 | 동일 CID remove exit0, 후속 ps 출력 없음, receipt cleanup=REMOVED, 수집 시 Worker0 |

오류는 `COMMAND_FAILED:transaction-api-image-smoke-created`이며 원본은 `run-38388390767/build-scan/transaction-api-image-smoke-created.log`다. 로그 SHA256 `cf200a6df8556ac535debc805bb135c599c88ca936159984c132e111aa487ad9`.

검사 template의 `.Id`는 Podman6.1.0 Go 구조체의 필드명이 아니다. [원본 타입](https://github.com/containers/podman/blob/v6.1.0/libpod/define/container_inspect.go#L741)의 exported 필드는 `ID`, JSON tag만 `Id`다. [코드 PR78](https://github.com/321Team/infra-cicd/pull/78), HEAD `7ebf101b88814498f7390a2c7afb2a5b9fd9c96e`에서 `.ID`로 최소 수정했다. 정적 타입 경로12개 대조·기존 MOCK9개·[CI](https://github.com/321Team/infra-cicd/actions/runs/38389073992) PASS. MOCK는 준비된 JSON을 반환하므로 실제 Go template 평가를 검증하지 않았다. 독립 코드 REVIEW/MERGE와 수정 후 Runtime은 미완료다.

## 원본과 무결성

서버 원본 `/home/server01_cicd-runner/FDS_CICD_AppWorkflow.lnz0tdq8`를 보존했다. `run-38388390767/`에는 서버 result/handoff/manifest/각 단계 로그의 수신 원본 및 GitHub Run/Job/로그가 있다. 수신 bytes와 원본 SHA256, receipt→handoff/build, 각 단계 log hash 및 기존 서버 manifest를 대조했다. 결과는 `VALIDATION.json`에 기록했다.

API archive SHA256 `9aeb2531ecd9e0bb0e7013c0e8c7f41ab9de9c0c2e9bf82df9e632edf2635fd7`, config/image `sha256:fd7d427c3b89f62c959988d73727dc94afaffe64e2652477a0830444e57b9868`, manifest `sha256:68e5211992cb7507b338e7bb364d4a991398f9f3e4b53123771a89f03ec7d756`. 48,930,816바이트 archive는 Runner에서 사후 hash만 확인했으며 워크스테이션/Git으로 복사하지 않았다. 기동·Scan 실패/미실행 회차 이미지를 다음 Push 성공 입력으로 넘기지 않는다.

CID `de9727f0cd7c097cf9880ee61337352b67ec28441aad76f6598995325b1d2538`은 result·create/remove 원본에 남아 있다. 사후 cidfile은 없었다. Podman rm은 연결된 cidfile도 지울 수 있으므로 파일 부재만으로 정리 실패나 수집 손실이라고 판단하지 않는다. Scan receipt2개도 미실행으로 부재다. 기존 Deploy claim1/checkpoint9는 변경하지 않았다.

수집기는 기존 strict SSH 경로로 정해진 원본·메타데이터·archive hash만 읽은 **PURE_READ_PRECHECK, REVIEW=NOT PERFORMED (Pre-check)**다. 실행 argv·계정·시각·rc·collector SHA256·출력 hash는 `runner-preflight-final/receipt.json`, `result-collection/receipt.json`에 있다. 호스트 설정·보안 통제·인증 값은 변경/조회하지 않았다. collector 사본은 수집 코드 증적이며 코드 독립 리뷰나 앱 시험을 대신하지 않는다.

`tbs_control.py`는 당시 로컬 실행 기록의 사본이다. 역사적인 이전 창을 담은 미사용 authorize 분기도 있으므로 재실행용 문서가 아니다. 실제 승인값은 `USER_AUTHORIZATION.json`, dispatch는 `DISPATCH_PRECHECK.json`/`DISPATCH_INTENT_NO_RETRY.json`/원 Run과 결속한다. 이 증적 폴더에서 어느 실행 코드도 재실행하지 않는다.

## 잔여 조건

수정 코드 독립 리뷰·병합 → 정확한 새 source/config/Runner·공급·시간창·Run수 결정 → 새 TBS로 두 이미지 실제 기동/Scan 검증 → 새 Push/Deploy → 최소 HA/복귀 → 최종 앱 회귀 → DB 판단 순서다. 자동 재실행하지 않는다. 이전 Run·출력·claim 재사용, 보안 통제 완화, Push/Deploy 범위 확대를 하지 않았다.

이번 자체 manifest와 layout 검사는 수신 바이트·경로 검증이며 Runtime 성공·인수의 증거가 아니다. 증적 독립 REVIEW/MERGE, Phase1 인수/종결은 미완료다. W4 NOT_MEASURED·C01 기술 ACL 미검증·DR 종결 한계·DB 최종 앱 회귀 후 판단을 유지한다.
