이권욱 / CODEX_ASSISTED — PR217 병합 및 새 Push 실행 제안. **아직 Push 실행 허용을 받은 기록이 아니다.**

[독립 승인](https://github.com/321Team/fds-project-evidence/pull/217#pullrequestreview-5503587492) HEAD `47ac79e99ed85e09e0a32fd4db0fd74f97ced920`와 동일 HEAD CI SUCCESS를 확인하고 2026-10-13 21:45:27 KST에 일반 병합했다. 실제 merge는 `9c10d945f48b59571ae67771f389af9ac4279bb7`이다. 승인 범위는 TBS 증적 편입이며 새 Push 승인으로 확대하지 않는다.

새 대상은 TBS Run38395350748/Attempt1, CICD main `147f760298dd4a683ea58f2a887483769352b97d`, APP `affbc69beef9967f7977d09a6fec14f7fb6c0e94`의 두 이미지다. API manifest `sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0`, engine manifest `sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d`. 21:45 Runner 원본87개 LOCAL_BYTES/BINDING COMPLETE, Python77파일 pin 일치를 다시 확인했다. 원본 이미지·상세 보고서·DB는 Runner에 보존했다.

**제안 범위:** 10/13 **22:20~22:30 KST 실제 Push Job 시작**, 10/14 **00:30 KST까지 결과 수집·정리 종료**. 기존 Job90분+정리30분을 확보한다. 새 입력0600 배치 → 기존 app-push.yml `execute=false` 사전검증 1회 → 통과 후 `execute=true` 새 Run1회 순서다. 실패·timeout 시 자동 재실행하지 않는다. 22:30까지 시작 조건이 안 되면 실행하지 않으며, 대기열의 실제 Push Job은 취소한다. 입력 만료가 실행 중 명령을 자동으로 중단시키는 것은 아니므로 진행 상태와 정리를 끝까지 추적한다.

실제 쓰기는 `10.1.93.54/fds/transaction-api`, `10.1.93.54/fds/fds-engine`에 새 `delivery-<uuid>` 태그 각1개다. 매 Run fresh 취약점 DB/Scan, HIGH·CRITICAL 각각0, TLS 검증 유지·digest 보존 전송·원격 tag/digest manifest 일치·임시 인증 파일 정리·봉인을 성공 조건으로 한다. Deploy, 기존 태그 덮어쓰기·artifact 삭제, Harbor manager/H6, 새 Robot·권한 확대·회전은 포함하지 않는다.

**시작 조건:** 이번 pending 입력의 정확한 해시·활성화 두 필드에 대한 독립 검토, 사용자 새 회차/창 허용, current main/Runner idle/원본 불변, Robot 및 두 Actions Secret 메타데이터, Harbor 변경·H6·사후 관측과의 비중첩을 모두 확인한다. H6 완료를 새 보편 Gate로 추가하지 않지만 겹치는 실행은 하지 않는다. 사용자와 별도 작업의 일정 확인 없이 현재 healthy만으로 향후 비중첩을 단정하지 않는다.

21:47 읽기에서 Skopeo1.24.0/패키지 무결성·필수 옵션·HOME/PushInputs/Claims0700·Worker0, Runner의 검증된 TLS/HTTP200·Harbor healthy를 확인했다. Robot은 21:48 현재 enabled, fds repository Pull/Push, 만료 **2026-10-18 17:16:55 KST**다. 오전 수집기의 예전 harbor-db ID가 현재 ID와 달라 첫 조회가 차단됐다. 실제 hostname/UUID·DB 이름/버전/healthy/StartedAt를 읽고 현 ID만 고정한 새 순수 조회로 확인했으며 원래 실패 기록을 보존했다. token/secret/salt 열은 조회하지 않았다. 이는 토큰 실제 인증 성공의 증거는 아니다.

이전 Push 후 회수한 Repository Actions Secret `HARBOR_CI_ROBOT_USERNAME`, `HARBOR_CI_ROBOT_TOKEN`은 현재 목록에 없다. 이권욱이 기존 보관 경로의 동일 Robot을 이 두 이름으로 다시 등록한 뒤 이름/갱신시각만 인수한다. 비밀값을 채팅·파일·Git에 전달하지 않는다. 다른 Workflow/branch의 소비·Secret 변경을 실행/정리 동안 배제하는 기존 회차 통제를 이번 창에도 적용하는 안이다. 종료 후 이번에 등록한 두 Secret의 갱신시각·소비 여부가 그대로인 경우에만 두 개를 회수하고 부재를 확인한다. 변경이 있으면 자동 삭제하지 않고 인수한다. Harbor Robot과 source-read Secret은 유지한다.

**실패 처리:** 사전검증/fresh Scan 실패는 실제 전송 중단. 인증·copy·inspect 실패/timeout은 원격 쓰기0으로 단정하지 않으며, 새 claim·nonce/tag·영수증을 보존하고 원격 상태를 조회한다. claim 삭제/재사용·자동 retry·원격 태그 삭제 없음. 부분 Push나 인증 파일 정리 미확인은 완료로 표시하지 않는다. 기존 앱은 배포하지 않아 그대로이며 새 Push 성공 후에도 Deploy 입력·승인·실행은 별도다.

현재 이 제안에 대한 USER_AUTHORIZATION/INPUT_REVIEW/Secret 재등록/비중첩 확정은 대기다. 새 Runtime Run·fresh Scan·Push·Deploy는 미실행이다. 기존 TBS1회 승인과 오전 Push 승인/claim은 재사용하지 않는다. 이후 순서는 새 Push → Deploy → 최소 HA/복귀 → 최종 앱 회귀 → DB 판단을 유지한다.
