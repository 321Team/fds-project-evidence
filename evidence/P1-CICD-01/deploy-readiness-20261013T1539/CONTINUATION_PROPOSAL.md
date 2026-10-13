> 최종 현황: 이후 사용자가 시작 마감16:45/종료17:00을 명시 승인하여 추가 Run38364658401을 실행했다. 새 transaction-api 이미지의 파일 권한 오류로 실패했고 이전 이미지 복귀·두 앱 각Ready3을 확인했다. [추가 회차 결과·원인·수정안](../deploy-additional-20261013T1645/README.md)이 현재 판정이다. 아래 내용은 해당 준비/첫 회차 시점의 이력으로 보존한다.

# 실패 회차 조정 및 추가 Run 제안 — 16:24 KST

CODEX_ASSISTED. **승인된 true Run1회를 사용했고, 앱 배포는 수행되지 않은 상태다. 새 Run은 아직 요청하지 않았다.**

- 사전검사 Run38361678189/Attempt1 SUCCESS, 원본 `PREFLIGHT=SUPPLIED_BYTES_MATCH`, tokenfalse, Deploy NOT_EXECUTED.
- 실제 Run38361855044/Attempt1은16:18:48~16:20:48 KST 인증 전달 대기120초가 끝나 FAILURE. 결과 원문 `MANUAL_RECONCILIATION_REQUIRED`/`DEPLOY_HANDOFF_UNCONFIRMED`, hash `7494b3ffd54085ee0230d371660dd4c9937829740bcc92dc994d60c9c4a33653`를 그대로 보존했다. 임의 PASS 정정하지 않는다.
- 첫 broker16:19:01은 `--authorization-expires 2026-10-13T17:00:00+09:00`를 전달했다. 기존 `native.Window`의 UTC-only 검사에서 CP1/Runner SSH 생성 전에 실패하는 것을 동일 소스로 로컬 재현했다(`UTC_EXPIRY_REQUIRED`). 실행자가 준비한 CLI 표기 오류이며 승인 record의 plan/approval 검증 오류가 아니다.
- 같은 시각의 UTC 표기 `2026-10-13T08:00:00+00:00`로 정정한 호출은16:20:51로 이미 Runner 연결창 종료 뒤였다. 이 호출도 결과는 NOT_CONFIRMED다. 새 Workflow/재발급/claim 삭제는 수행하지 않았다. 두 broker 호출 원문과 실패를 보존한다.
-16:21 사후 조회: Deployment UID/spec/image/RV/generation/각Ready3 및 SA·CA 이전 관측과 동일. Runner socket 부재, 해당 plan claim/checkpoint0, result존재. 승인된 구현상 토큰 issue 요청은 Runner 연결/ready 확인 뒤에만 전송되므로 이번 경로에서 issue 진입이 없었다고 판단한다. 이는 source·실행 시각·잔존 상태 대조에 의한 판단이며 서버 audit 전수 검증은 아니다. 원 broker의 `TOKEN_ISSUANCE=NOT_CONFIRMED` 표기는 변경하지 않는다.
-16:23:49 기존 CP1 staged source7개의 hash를 대조하고, 해당 승인 코드의 NativeAccess 생성·SA·SelfSubjectAccessReview만 조회한 결과 PREISSUE_PREFLIGHT_PASS. TokenRequest/TokenReview를 호출하지 않았고 새 credential을 만들지 않았다.

## 추가 실행안 — 사용자 결정 대기

기존 immutable plan/record/approval과 source·대상·복귀 범위·17:00 종료를 유지하고 **새 true Run/Attempt1을 추가1회만** 요청하는 안이다. record `11c94e5c28e1b22bc8df2d8f686fb61ff2f0c04b7bb9dd810496c4b1f63f0e50`, plan `5c2d8367f5b81875693165055234a30e5c69944e345c8ad8c5277ef30ebd8387`는 독립 승인된 bytes 그대로다. 기존 plan은 claim을 획득하지 않았다. 기존 Run을 rerun하거나 실패 원본/claim을 삭제하지 않는다.

새 Run 실제 binding으로 controller의 **새 binding 파일**을 생성한다. UTC 종료 인자 `2026-10-13T08:00:00+00:00`를 사용하고 현재 Runtime clock에서 Window.remaining≥640초를 사전 검증한다. 기존 false Run의 같은 record 성공을 재사용한다. 실제 true는 새 Run1회, broker의 발급 연결은 추가1회이며 실패하면 이번 창을 종료한다. 16:30까지 새 dispatch할 수 없으면 실행하지 않는다. Harbor Runtime 비중첩 및 main/현재 대상·원 approval 일치를 직전에 확인한다.

원 실행안이 자동 rerun을 금지하고 true Run1회로 제한했으므로 **추가 Run 허용만 사용자에게 확인한다.** 이미 확정된 Source/시간창/콘솔/두 이전 digest 복귀를 다시 승인받는 제안은 아니다. HA/drain/최종 APP·DB 인수는 여전히 제외한다.
