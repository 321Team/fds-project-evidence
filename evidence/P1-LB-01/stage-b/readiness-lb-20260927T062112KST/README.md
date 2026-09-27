# P1-LB-01 Stage B LB Readiness 수신 검토 — 2026-09-27 KST

**판정: LB native nft Readiness 원본 증적 PASS / Runtime 장애 주입 NOT RUN / evidence 저장소 독립 편입 리뷰 대기.**

사용자가 `k8s-api-lb01`의 일반 계정 `server01_k8s-api-lb`에서 실행한 원본 archive와 sidecar를 바이트 그대로 보존한다. 검토자가 서버에 접속해 재실행한 결과가 아니다.

## 원본과 무결성

- 원본: `FDS_P1_LB_01_READINESS_LB_je2zvfb0.tar.gz`
- 크기: 20,589 bytes
- SHA-256: `4fb6597fd034a97c638a2255bbc944193bbbcf926f7f9075330306bbab6e951f`
- 외부 sidecar: MATCH
- archive 내부 파일: 21개
- 내부 `SHA256SUMS`: 20/20 MATCH
- 수집 시각: 2026-09-27T06:21:12.747831+09:00 ~ 2026-09-27T06:21:13.192524+09:00
- source revision: `3cb60394241e2eb38e0bd715336816bc06626ea1`

archive에 포함된 `collect_preflight.py`, `collect_stageb_readiness.py`, `stageb_common.py`, `stageb_rules.py`는 infra-lb의 독립 리뷰된 revision `3cb60394241e2eb38e0bd715336816bc06626ea1`과 대조해 동일함을 확인했다.

## 실행 결과

- host/user: `k8s-api-lb01 / server01_k8s-api-lb`
- scope: `READ_ONLY_PRECHECK`
- `STATUS=NFT_CHECK_ONLY_PASS`
- 6개 nft 관련 명령: 모두 rc=0, timeout 없음, stderr 공란
- `nft -c -f -`: rc=0
- nft tables before/after: MATCH
- nft ruleset before/after: MATCH
- candidate table: `ABSENT`
- candidate rules SHA-256: `9efce83d9c39a1a5a3eb341b02c1ec1f313173c927890081ef7daa64580e03aa`

이 결과는 후보 규칙의 **check-only** 문법/권한/비변경 검증이다. 실제 `nft -f -` 장애 주입은 실행하지 않았다.

## 범위와 한계

- Fault injection: **NOT RUN**
- 자동 DOWN 관측: **NOT TESTED**
- expiry/recovery: **NOT TESTED**
- Runtime PASS/최종 인수: **PENDING**
- 증적 저장소 독립 리뷰: **PENDING**

따라서 이 편입으로 P1-LB-01 Stage B 완료, Runtime 승인, 티켓 종결을 선언하지 않는다. 최신 진행 상태와 후속 Gate는 baseline issue #9를 따른다.

## 출처

- 책임 티켓: `321Team/fds-project-baseline#9`
- 실행 소스: `321Team/infra-lb@3cb60394241e2eb38e0bd715336816bc06626ea1`
- review: infra-lb PR #11 / `hayeounglee` APPROVED
- 원본 제출: 이권욱, 2026-09-27 KST
