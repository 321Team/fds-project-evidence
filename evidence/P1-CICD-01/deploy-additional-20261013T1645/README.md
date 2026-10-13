# 추가 Deploy 1회 결과 — 2026-10-13 KST

AI 사용: CODEX_ASSISTED · 이권욱 승인 범위 실행.

**판정: Run38364658401/Attempt1 FAILURE(`READINESS_TIMEOUT`), transaction-api 이전 이미지 복귀 `READY_HEALTH_NOT_VERIFIED`. fds-engine 배포 미실행. 전체 Delivery·APP 인수는 미완료다.**

## 범위와 실제 결과

[사용자 결정 기록](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6140849866)에 따라 추가 true Run 1회와 시작 마감16:45/종료17:00을 적용했다. 원 승인 JSON·plan·record bytes, 두 앱과 복귀 범위는 동일하다. 로컬 dispatch 진입은16:44:57.717이고 POST 직전16:45 미만 조건을 확인했다. GitHub가 기록한 Run 생성은16:45:01이다. 로컬 요청 시작·서버 Run 생성·Job 시작을 같은 시각으로 표시하지 않는다. 이 추가 Run은 소진했고 자동 재실행은 하지 않았다.

| 단계 | 결과 |
|---|---|
| 입력·Harbor 재조회 | 16:42 앱/SA/CA·main2d8a14c·원 approval 일치, 기존 claim 부재, Harbor TLS health200/healthy. 별도 Harbor 작업은 PR60 코드 병합만 완료·설치/H6 미실행으로 확인 |
| [추가 Run](https://github.com/321Team/infra-cicd/actions/runs/38364658401) | Source `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`, Attempt1, Job115186791665,16:45:09~16:50:34 배포 step failure; 정확 Job/step 시각은 `dispatch-true-additional/jobs-final.json` 참조 |
| broker execute | 16:45:27~28 로컬 시각,1회, rc0·`HANDOFF=REVIEW_RESPONSE_RECEIVED`. 원 종료와 동치인 UTC `2026-10-13T08:00:00+00:00` 사용 |
| Token 관측 | CP1 발급16:45:29→만료17:00:29, TTL900초, SA UID·audience 결속, fresh TokenReview 응답 수신. 각 호스트 시각은 미세 차이가 있으며 로컬 수신 시각과 발급 시각을 단일 정밀 시계로 간주하지 않음 |
| transaction-api | 새 digest `ef0afe42…5dc39` 적용(gen9→10), 새 Pod가 `/app/run.py` Permission denied·exit2·CrashLoopBackOff.300초 준비 대기 후 `READINESS_TIMEOUT`. 이전 digest `a7093136…cc33`로 복귀(gen11)·READY |
| fds-engine | 새 digest 적용·복귀 모두 `NOT_EXECUTED`. 이전 digest `5e2a081c…67369` 유지 |
| 사후 확인 | 16:51:27 조회에서 이전 이미지의 Pod6개 Running/Ready, 각 Deployment updated/available/ready3. UID/spec은 원래 값과 일치하나 transaction-api generation/RV는 실행·복귀로 증가. socket 부재, claim1·checkpoint9 보존 |

원 result SHA256은 `113fd691d883339bdbc936a401b3fa35d25fb04554e077c73598dc8d1d622b67`이다. `selected-original-receipts`에 dispatch/result/claim/checkpoint bytes를 base64에서 그대로 추출하고 해시를 대조했다. 원본의 `DELIVERY_GATE=NOT_VERIFIED`, `HEALTH_E2E=NOT_VERIFIED`, `POD_IMAGE_ID=NOT_VERIFIED`, `SOURCE_APPROVAL=NOT_INDEPENDENTLY_VERIFIED`, credential `runner_token_authentication=NOT_VERIFIED`는 그대로 보존한다. 별도 사후 Pod 이미지 조회·입력 독립 승인·실제 API 갱신 결과를 연결하되 원본 판정을 다시 쓰지 않는다.

서버 강제 token 회수는 `NOT_PERFORMED`다. 실행 권한 종료는17:00이며 발급 token의 명목 만료는17:00:29로29초 늦다. 발급 token 원문을 보관·재사용하지 않았다. 명목 만료와 실제 서버 만료 거부 시험은 구분하며 후자는 미실행이다. claim은 삭제하지 않고 이후 계획의 재사용 금지를 유지한다.

## 원인: 빌드 파일 권한과 비루트 실행 계정 불일치

16:48 로그는 원문 전체를 외부로 내보내지 않고 hash와 고정 오류/경로만 수집했다. current/previous 로그 모두115B·SHA `1bd2a009e19cb566d2c38a5d02d06f445b970295c9c43dde9d4626f7270f3177`, 선택 필드는 `can't open file`, `/app/run.py`, `Permission denied`였다.

16:52:25~26 Runner의 기존 TBS OCI archive를 읽기만 했다. archive 해시는 증적에 기록된 값과 일치하고 manifest/config digest도 Push digest와 결속된다. **두 후보 모두 최종 layer의 `/app/run.py`는 UID0/GID0/mode0600**, 이미지 User는10001:999, Entrypoint `/venv/bin/python3`, CMD `run.py`다.16:55 조회한 실제 Deployment도 runAsUser10001/runAsGroup999/runAsNonRoot true, readOnlyRootFilesystem true, allowPrivilegeEscalation false이며 volumeMount는 없다. 이 권한 조합은 실행 계정의 run.py 읽기를 막는다. engine은 같은 결함이 archive에서 확인됐지만 실제 engine crash 시험은 하지 않았다.

생성 경로도 [TBS source c9eff5f의 build_scan.py](https://github.com/321Team/infra-cicd/blob/c9eff5fb2e50a690818a3e67347ab4a1bfc88f51/tools/delivery/build_scan.py#L172)에서 확인했다. `unpack_source`는 소스를0600/0700으로 만들며 같은 함수를 테스트 사본과 이미지 build context에 모두 쓴다. [앱 source affbc69 Dockerfile](https://github.com/321Team/fds-msa/blob/affbc69beef9967f7977d09a6fec14f7fb6c0e94/transaction-api/Dockerfile#L18)은 root 소유 COPY 후 USER10001로 실행한다. Build/Scan 성공이 실제 비루트 이미지 기동을 입증하지 못한 공백이다. build_scan.py는 TBS source c9eff5f와 현재 CICD source2d8a14c 간 차이0이었다.

## 수정안과 재검증 조건 — 미적용

`FIX_PROPOSAL.patch`는 현재 CICD main2d8a14c에 맞춘 최소 코드 제안이다. private evidence/source 루트0700과 테스트 사본0600/0700은 유지하고 **이미지 build context 내부의 일반 소스만 Git 실행 비트에 따라0644/0755로 정규화**한다. 앱 파일을 일반 사용자 쓰기 가능으로 만들거나 Runtime root 실행·SELinux/권한 통제 해제로 우회하지 않는다. 이 패치는 저장소/서버에 적용하지 않았고 실제 수정 후 검증을 아직 수행하지 않았다.

수정 완료조건은 다음과 같다.

1. CICD 빌드 소스 수정·독립 리뷰. umask077에서도 이미지 context의 파일/하위 디렉터리가0644/0755이고 private 루트/테스트 사본은 기존 권한을 유지하는 POSIX 회귀검증.
2. 두 이미지의 `/app/run.py` 및 import 대상 파일/디렉터리에 대한 최종 OCI 권한 검사. 별도 staging 사본의 권한 변경이 원본 증적이나 비밀 파일에 미치지 않음 확인.
3. 실제 UID10001/GID999·읽기 전용 파일시스템 조건으로 **두 최종 이미지의 기동·업무/metrics 포트 분리** 검증. 테스트 컨테이너 통과만으로 대신하지 않음.
4. 새 TBS/Scan/Push와 새 digest/plan/approval/record로 결속. 현재 claim은 보존하고 같은 plan을 다시 실행하지 않음. 실제 서버 재배포는 새 구체 입력·시간창의 승인 범위에서만 수행.
5. 성공 Deploy 후 최종 형상→별도 HA/복구→최종 APP 회귀→DB#11 인수 판단. 이번 기록은 DB 종결이나 W4 NOT_MEASURED 해소가 아님.

## 증적 범위

이 폴더는 추가 회차와 그 직전/직후 읽기 수집만 묶었다. 첫 실패 Run과16:30 마감 보류는 [이전 회차](../deploy-attempt-20261013T1615/README.md)에 보존한다. `START_CUTOFF_AUTHORIZED.json`과 사용자 결정 댓글이 이후 시간 조정이다. SHA·layout 검사는 무결성/형식 검사이며 Runtime 성공이나 최종 인수를 대신하지 않는다. 순수 읽기 collector는 `REVIEW=NOT PERFORMED (Pre-check)`이고 증적 편입 최신 HEAD의 독립 REVIEW/MERGE는 별도다.
