# 검토 후 실행 카드

대상은 EXECUTION_SCOPE.md와 ACTIVATION_PLAN.json으로 고정한다. 이 문서 자체는 독립 입력 검토 회신이 아니다. 비밀번호·token을 입력표/명령 인수/공개 로그에 넣지 않는다.

1. **로컬 / 입력 검토:** PR208 리뷰·댓글 원문에서 검토자, 대상 커밋, `13b50485c6d3fe7bbb155561f88a22c6f06aab6dc73e9f14fb0e8f02696c2d89` 및 ACTIVATION_PLAN 두 필드 변환 수용을 확인한다. 작성자의 USER 결정 댓글을 독립 리뷰로 사용하지 않는다. 원본 hash/유효창/main이 바뀌면 해당 차이만 재검토한다.
2. **로컬 / 변환:** verify_revision.py의 읽기 검증을 통과한 pending JSON에 ACTIVATION_PLAN의 두 필드만 적용하고 정의된 UTF-8/LF 직렬화로 `push-20261013-window1200.json`을 새 파일로 저장한다. 파일 SHA256이 목표와 다르면 배치하지 않는다. 임의 reference·시각·PASS를 추가하지 않는다.
3. **회차 시작 / 읽기:** infra-cicd actual main SHA, Runner online/idle·queued/in_progress, 두 Secret 이름/created_at/updated_at, Harbor 변경·사후 관측 비중첩을 확인한다. 기존 신뢰를 사용하는 정상 Runner에서 Harbor TLS/health를 확인한다. 새 CA 설치·보안 예외로 우회하지 않는다. 종료12:00, 실제 Push Job 시작10:00 한도를 확인한다.
4. **Runner / 사용자 파일:** 기존 SSH 경로 `fds-ansible01 → server01_cicd-runner@10.250.10.20`을 사용한다. 정상 hostname/UID1000/HOME0700/PushInputs0700·소유자·상위 symlink 부재를 확인하고 `FDS_CICD_PushInputs/push-20261013-window1200.json`을 O_EXCL/O_NOFOLLOW·0600으로 새로 만든다. 쓰기 후 bytes/hash/owner/mode/nlink를 다시 읽어 확인한다. 기존 입력·claim·HOME 설정을 바꾸지 않는다. 부분 실패는 새 파일 상태를 기록하고 덮어쓰지 않는다.
5. **GitHub / 사전검증:** `DISPATCH.validate.json`의 ref=main, exact name/hash, execute=false로 기존 app-push.yml을 수동 dispatch한다. 실제 새 Run/Attempt와 SHA를 응답/조회로 결속하고 해당 실행 로그의 EVIDENCE_DIR만 읽는다. 원격 result.json `VALIDATION=PASS`, `PUSH=NOT_EXECUTED`, rc0 및 dispatch.json record/context 일치를 확인한다. false 경로에는 credential-cleanup/dispatch-result 봉인이 생성되지 않으므로 실제 Push 경로의 산출물을 요구하지 않는다.
6. **GitHub / 실제1회:** 위 성공 후 시작 조건을 재확인하고 `DISPATCH.execute.json`으로 dispatch한다. 10:00 전 실행이 시작되지 않으면 취소하고 실행하지 않는다. 새로운 실제 Run/Attempt·SHA를 기록한다. Workflow가 새 claim을 소비하며 fresh Scan을 수행한다. 토큰 인증은 그 뒤 실제 Skopeo 전송에서 확인되므로 조회 메타데이터만으로 성공을 예상 판정하지 않는다.
7. **결과:** 해당 새 private EVIDENCE_DIR만 읽어 두 서비스 PASS/digest, fresh-scan receipt, credential-cleanup PASS, dispatch-result PASS/PUSH PASS, dispatch-SHA256SUMS를 대조한다. 전체 Scan 원문과 auth 원문은 공개하지 않는다. 코드/Run/해시/rc·시각·오류 코드와 선택한 결과를 증적으로 봉인한다.
8. **정리:** 실행이 종결되고 같은 Secret의 다른 소비가 없는지 확인한다. GitHub Secret 이름/갱신시각이 승인 대상과 같을 때 두 이름만 DELETE하고 이후 이름 부재를 조회한다. 변경됐다면 삭제하지 않고 인수한다. `CICD_APP_SOURCE_READ_TOKEN` 및 Harbor Robot은 유지한다. 임시 auth 잔여가 있으면 해당 회차 소유 경로만 확인해 정리한다.

## 실패 시

- 입력·사전검증 실패: 실제 Push 중단, 기존 파일/claim 보존. 별도 동일 실패 재시도 없음.
- fresh Scan 실패: 현재 HIGH/CRITICAL 또는 DB/정합성 원인을 기록, 예외 Push 없음.
- 인증·copy·inspect 실패/timeout/취소: 원격 쓰기0으로 단정하지 않음. claim·nonce/tag·영수증을 보존하고 원격 readback으로 판단한다. 자동 재시도·claim 삭제·원격 tag 삭제는 범위 밖이다.
- host/SIGKILL 장애: 임시 auth 정리·봉인이 확인될 때까지 완료 아님. 기존 콘솔/운영 인수 경로로 전달한다.
- 유효창 종료 전 검토를 못 받으면 실행하지 않는다. 새 시간은 승인 없이 대입하지 않는다.
