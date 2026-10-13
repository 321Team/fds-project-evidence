# PR217 병합 후 새 Push 입력·준비 조회 — 2026-10-13

이권욱 / CODEX_ASSISTED. **TBS 증적 PR217 병합 완료, 새 Push 준비 완료, 실행은 대기**다. 새로 만든 pending 입력과 실제 21:45~21:48 조회 결과를 연결한다. 과거 TBS/Push 승인·Run/claim을 재사용하지 않는다.

- [PR217 독립 승인](https://github.com/321Team/fds-project-evidence/pull/217#pullrequestreview-5503587492): HEAD `47ac79e99ed85e09e0a32fd4db0fd74f97ced920`. 정확 HEAD CI SUCCESS 후21:45:27 일반 병합 `9c10d945f48b59571ae67771f389af9ac4279bb7`.
- [구체적 실행 제안](https://github.com/321Team/fds-project-evidence/pull/217#issuecomment-6145950204): **10/13 22:20~22:30 KST 실제 시작, 10/14 00:30 수집/정리 종료**. 아직 사용자 승인 아님. false 사전검증1회→true Push1회, 자동 재실행 없음, Deploy 제외.
- 기존 코드 main `147f760298dd4a683ea58f2a887483769352b97d`, APP `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, 새 TBS Run38395350748/Attempt1. 코드 변경·기존 코드 전체 재리뷰를 추가하지 않는다. 이번 검토 대상은 **새 Run/이미지/receipt·current 원본·Push 입력·창/Secret 통제·실패 경계**다.

## 실제 확인

| 항목 | 결과와 한계 |
|---|---|
| 원본 재대조 21:45 | 실제 Runner에서 Python77파일 pin, 원본87개 LOCAL_BYTES, BINDING COMPLETE, EVIDENCE_CHECK PASS. 원본 읽기만 수행; 새 앱 기동/Scan 아님 |
| Runner 21:47 | UID1000, HOME/PushInputs/Claims0700, Worker0, Skopeo1.24.0·rpm 검증rc0·필수 TLS/digest 옵션 있음. 기존 claim3개 hash만 읽고 유지 |
| Harbor 21:47 | Runner 기본 trust의 인증서 검증 유지, HTTP200/healthy·8개 component healthy. future 비중첩 확인과 구분 |
| Robot 21:48 | DB READ ONLY transaction, enabled, fds repository Pull/Push, 만료10/18 17:16:55 KST. credential 열 제외, 전후 DB container 동일. 실제 token 인증 아님 |
| Actions Secret | 21:44 저장소에는 source-read 한 개만 있음. Robot 두 이름 없음. 21:19 조직 목록403은 이전 별도 관측이며 조직 Secret 전체 부재를 뜻하지 않음 |
| Harbor 작업 | baseline13의21:41 갱신: PR61 활성화 완료, PR62 H6 복구 helper 검토/병합/실행 준비. H6·사후 관측과 비중첩 미확정 |
| 실행 승인·독립 입력 검토 | 미수신. pending gate는 의도대로 BLOCK이며 활성 입력은 디스크/Runner에 만들지 않음 |

Robot 오전 수집기는 old harbor-db ID 고정 때문에21:47 실패했다. 진단에서 같은 harbor01 UUID, DB 이름/이미지 v2.13.1·healthy, 실제 ID `3fec129340dda3e33be1239925093fec4ac6666f3b01ce19a4ee4ef754ca40c5`, StartedAt12:26:07 KST를 관측했다. 새 수집기는 **ID pin 한 곳만 변경**하고 같은 SQL/읽기전용/제한을 유지했다. 실패·진단·pin 차이·새 성공을 모두 보존하며 이 조회로 과거 컨테이너 교체 원인/승인을 판정하지 않는다.

## 정확 입력과 활성화 조건

`push.pending.json` SHA256 `f20a5f5d7ad031271ccc6ac03456b88b5bb398a3222b426ef13409b99cb5b6ef`.

`ACTIVATION_PLAN.json`의 두 필드만 바꾼 **정적 미리보기 목표**는 `8b7b4f4e64c271b54167bc768e4e3afc1b2326c480683aaaf4aa0ff3e18c2b06`, 파일명 `push-tbs38395350748-window0030.json`이다. `template_only=true→false`, `status→APPROVED_FOR_DELIVERY`는 사용자 새 범위/창 승인·정확 입력 독립 검토 및 시작 조건을 모두 확보한 뒤에만 적용한다. expiry와 reference는 지금 제안값이며 승인 사실이 아니다. 값이 달라지면 해당 차이·해시를 다시 검토한다.

`STATIC_CHECK.json`의 활성화 미리보기 CONDITIONS_MATCH는 구조/선언 값 검사이며 실제 credential, 비중첩, Runtime 또는 승인 증거가 아니다. delivery_gate는 승인 URL의 본문이나 시간창 시작 시각을 검증하지 않으므로 실행자가 실제 승인·리뷰·시간 조건을 별도로 확인한다. 기존 IF09/AC02 인계 PASS와 current TLS/healthy를 구분하며 이번 조회로 AC02를 재실행했다고 하지 않는다.

## 검토 후 실행 순서

1. 로컬에서 사용자 승인과 독립 리뷰의 대상 HEAD·목표 SHA/두 필드 및 `EXECUTION_PROPOSAL.md` 범위를 확인한다. 기존 app-push.yml을 그대로 사용하며 제안 dispatch JSON을 승인 전 실행하지 않는다.
2. 이권욱이 기존 보관 Robot을 Repository Actions Secret 두 이름에 재등록한다. 값은 전달/출력하지 않고 name/updated_at만 인수한다. 해당 창에서 다른 소비/변경 배제와 종료 후 두 이름만 회수 범위를 확인한다. 조직 Secret 존재 여부를 임의 확정하지 않는다.
3. 직전 main/원본·Robot·Secret metadata·Runner online/idle·Harbor TLS/healthy·변경/H6/사후 관측 비중첩을 확인한다. 조건 미충족 또는22:30 시작한도 경과면 실행하지 않는다.
4. 기존 strict SSH `fds-ansible01 → server01_cicd-runner@10.250.10.20`, UID1000의 HOME/PushInputs0700·부모 symlink 부재 확인 후 목표 입력을 O_EXCL/O_NOFOLLOW·0600으로 한 번 배치하고 bytes/hash/uid/mode/nlink를 다시 읽는다. 이전 입력·claim은 유지한다.
5. 고정 main의 `app-push.yml`에 `execute=false` 1회. 실제 새 Run/Attempt·SHA 및 dispatch/record binding·VALIDATION PASS/PUSH NOT_EXECUTED/rc0 확인 후에만 true1회. 실제 RunID는 미리 만들지 않는다. false도 private 출력/lock 생성이 있어 순수 읽기로 표시하지 않는다.
6. true는 claim 소비→fresh DB/Scan→두 새 delivery 태그 전송/원격 digest 확인→임시 인증파일 정리/봉인. HIGH·CRITICAL0, 두 이미지/receipt/hash/Run 연결, credential-cleanup/dispatch-result PASS까지 확인한다.90분 Job 상한과00:30 정리 종료를 추적한다.
7. 종료 후 이번 등록 Secret 두 개의 갱신시각·소비가 변하지 않은 경우에만 회수하고 이름 부재를 확인한다. 변경됐다면 삭제하지 않고 인수한다. Harbor Robot·source-read Secret은 유지한다.

실패/timeout/취소/부분 Push는 증적과 claim·nonce/tag 보존 후 중단한다. 인증 실패를 원격 쓰기0으로 단정하지 않는다. 자동 retry·claim 삭제/재사용·원격 artifact 삭제·기존 앱 Deploy/복귀는 포함하지 않는다. 상세 중단/정리/인수 조건은 `EXECUTION_PROPOSAL.md`에 있다.

## 증적과 검증 범위

수집기는 PURE_READ_PRECHECK / REVIEW=NOT PERFORMED (Pre-check)다. 기존 app_evidence 검증 소스는77개 pins로 검토된 병합본과 대조했다. 원격 명령·수집기 hash·시각·rc·출력 hash는 각 receipt에 있다. `tbs_control.transport-original.py`, `run_harbor_read_probe.original.py`는 기존 전송 경로의 출처 사본이며 증적 폴더에서 재실행하지 않는다.

`NEXT_PUSH_HANDOFF.original.json`은 PR217의 원본 바이트 사본이며 작성 당시 NOT_CREATED 표기를 그대로 보존했다. 현행 입력 생성 상태는 본 문서가 설명한다. 원본 이미지·상세 보고서·Trivy DB·token은 Git에 편입하지 않았다. 새 편입 증적·입력 독립 리뷰/병합은 대기다. Push·Deploy·업무 APP/E2E/DB 인수는 미실행이며 DB는 최종 앱 회귀 후 판단한다.
