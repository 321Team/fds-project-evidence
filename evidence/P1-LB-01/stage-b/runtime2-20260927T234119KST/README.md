# P1-LB-01 Stage B Runtime #2 수신 검토 — 2026-09-27 KST

**판정: Runtime 자동 결과 `PASS_CANDIDATE` / 원본 타임라인 검토 `TECH_PASS` / cleanup·3UP recovery PASS / evidence 독립 편입 리뷰 및 reboot persistence·최종 인수는 PENDING.**

사용자가 `ansible01`에서 실행한 Stage B Runtime #2의 controller archive와 sidecar를 바이트 그대로 보존한다. 검토자가 운영 서버에서 시험을 재실행한 결과가 아니다.

## 원본과 무결성

- 원본: `FDS_P1_LB_01_STAGEB_CONTROLLER_mj1d45e7.tar.gz`
- 크기: 238,269 bytes
- SHA-256: `5672058d58cc1881a887dbe7aeb74dc0ec5de11ad536e833a0cba5d2dbf202bc`
- 외부 sidecar: MATCH
- outer archive 일반 파일: 72개
- outer `SHA256SUMS`: 71/71 MATCH
- unsafe path/symlink/hardlink: 없음
- nested CP archive: SHA-256 `2e3ec6a37faaf34112972f16d8f4cb577ad7ceb9f4c1d58e3b393194e8220e13`, manifest 305/305 MATCH
- nested LB archive: SHA-256 `79f5fde2f947dbad2838d7304657cda2972ee51b75950810a39199eb9ec3a157`, manifest 297/297 MATCH
- 기본 private-key/Bearer/client-key-data 민감정보 패턴 검사: 검출 없음. 이는 독립 리뷰의 민감정보 검사를 대체하지 않는다.

## 실행 바인딩

- controller 시작: `2026-09-27T23:41:19.581879+09:00`
- Runtime run_id: `0c34c0a4abcc4d12a3ce8668545a65d3`
- target: LB `.109` → `10.1.93.104:6443`
- source revision = reviewed revision: `2a7ff5b457e49cf6cfdfbcf3374224f120e735d3`
- source review: `infra-lb#14`, `hayeounglee` exact-HEAD APPROVED (`PRR_kwDOUeQof88AAAABPbQGiw`)
- Lead runtime authorization/OOB/window: controller `INPUTS.json` 및 baseline #9 기록과 연결
- failure budget: 최대 failed samples `12`, 최대 continuous failure `24s`

## Runtime 결과

- controller: `ansible_rc=0`, `archive_integrity=PASS`, 자동 결과 `PASS_CANDIDATE`
- fault apply 완료: `2026-09-27T23:42:02.985575+09:00`
- control03 최초 `DOWN/L4TOUT`: `2026-09-27T23:42:14.812540+09:00` (주입 완료 후 약 11.83초)
- 장애 중 control01/control02: `UP/L4OK` 유지
- drop counter: `178`
- own table 삭제 완료: `2026-09-27T23:42:58.806258+09:00`
- control03 최초 `UP/L4OK` 회복: `2026-09-27T23:43:03.221776+09:00`
- 최종: 3/3 `UP/L4OK`, own `p1lb_<run_id>` table absent
- LB `PASS_CANDIDATE`: `2026-09-27T23:43:34.686098+09:00`

## API observer / failure budget

- sample: 총 70, 성공 67, 실패 3
- 실패 sequence: 18 / 20 / 22
- 실패 사유: 각 `NodeList` 요청 timeout 계열 `COMMAND_FAILED`
- 성공 sample이 각 실패 사이에 존재함
- reviewed algorithm 기준 최대 continuous failed streak: 약 `3.094s`
- 승인 budget `12 samples / 24s` 이내

따라서 이 결과는 **승인된 failure-budget 기준의 API 지속성 PASS 후보**이다. `0 failed sample` 또는 무손실 SLA로 확대하지 않는다.

## Cleanup / 회귀

- HAProxy MainPID: `1267` 유지
- HAProxy cmdline: initial/final byte-identical
- HAProxy config hash output: initial/final byte-identical
- firewalld 상태/룰셋: Runtime 전후 변경 없음으로 수집됨
- Stage B own table: 최종 부재
- backend: 최종 3/3 `UP/L4OK`

동일 fault Runtime 재실행은 이 증적 검토의 선행조건이 아니다.

## 범위와 잔여

- Stage B fault/failover/recovery 기술 검토: `TECH_PASS`
- automated final state: `PASS_CANDIDATE`
- evidence 저장소 독립 리뷰: `PENDING`
- reboot persistence: `NOT_RUN`
- LB-A-01 / P1-K8S 최종 Handoff: `PENDING`
- P1-LB-01 최종 인수/종결: `PENDING`

`RESULT.json`의 `stage_b=NOT_COMPLETED`, `final_acceptance=PENDING`은 위 후속 Gate를 남기는 설계상 상태이며 이번 raw Runtime 결과와 모순되지 않는다.

## 실행 시도 이력 경계

이번 수집회차는 **성공한 attempt3 원본**을 보존한다. 이전 시도는 baseline #9에 별도 이력으로 유지한다.

- attempt1: operator launcher의 Python `-I`로 import 단계 PRE-RUNTIME STOP, controller main 미진입·mutation 없음 — baseline #9 comment `5856743809`
- attempt2: 기존 SSH key binding 누락으로 양 호스트 인증 단계 SAFE STOP, remote Runtime 미진입·mutation 없음 — baseline #9 comment `5856812077`

이 편입이 두 이전 시도의 원본 archive 편입을 의미하지는 않는다.

## 출처

- 책임 티켓: `321Team/fds-project-baseline#9`
- Runtime 기술 판정 기록: baseline #9 comment `5856918773`
- 실행 소스: `321Team/infra-lb@2a7ff5b457e49cf6cfdfbcf3374224f120e735d3`
- merge commit: `1fb1b3fd4abcaa5464943e1df7fb5aff986fafb7` (reviewed HEAD 대비 Stage-B file diff 0 확인 이력)
- 원본 제출: 이권욱, 2026-09-27 KST
