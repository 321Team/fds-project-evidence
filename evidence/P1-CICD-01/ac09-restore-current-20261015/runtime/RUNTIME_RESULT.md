# CICD AC09 실행 결과 — 2026-10-15

**R1 이전 버전 복원과 R2 현행 복귀를 모두 실행했다. 현행 복원 및 두 회차의 HTTP·계수 관측은 충족했으나, AC09 최종 인수는 아직 완료가 아니다.** DB 동일 거래 ID 행 대조와 SEC 시각 증적의 사후 판정이 남아 있다. 이 문서는 실제 실행 결과이며 독립 리뷰·티켓 종결·정본 발행을 대행하지 않는다.

## 승인 및 실제 회차

- 사용자 원문: “제시한 실행·복구 범위 승인”. [중앙 승인 원본](../../phase1-central-control-20261015/AC09_USER_AUTHORIZATION_1535.json), [실제 GO](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186064463).
- 정상 창 15:35–16:20 KST, 별도 수동 현행복구 한도 16:35. 단일 실행 담당은 이 세션이며 Harbor·Ansible 비중첩을 중앙이 관리했다. 별도 수동 복구는 사용하지 않았다.
- 소스 `fddc76e1c261cd938f06211b7ed035fdcb32e606`, source 37개와 native bundle 불변. 새 Runner 등록 0, 정확 4 Jobs/Attempt1, TokenRequest 2, 최소 deposit POST 2, 승인된 추가 Edge GET 4를 사용했다. 재dispatch·재POST·새 권한·수동 PATCH 0.

| 단계 | 실제 Run | 결과 |
|---|---|---|
| R1 execute=false | [38693789875](https://github.com/321Team/infra-cicd/actions/runs/38693789875) | success, 서버 변경 없는 검증 |
| R2 execute=false | [38693851363](https://github.com/321Team/infra-cicd/actions/runs/38693851363) | success, 서버 변경 없는 검증 |
| R1 execute=true | [38693979785](https://github.com/321Team/infra-cicd/actions/runs/38693979785) | success, ROLLOUT=READY, error NONE |
| R2 execute=true | [38694721511](https://github.com/321Team/infra-cicd/actions/runs/38694721511) | success, ROLLOUT=READY, error NONE |

[4개 Run/Jobs/로그 원본 인덱스](github-final/RUN_SUMMARY.json). R1/R2 최종 claim과 checkpoint 각각 8개는 Run·Attempt·plan·approval·UID 및 sequence/previous hash 결속을 확인했다. 원 서버 metadata와 원 bytes를 함께 보존했다. [R1 journal](r1-journal-final/r1/stdout.json), [R2 journal](r2-journal-final/r2/stdout.json). 실행 종료 판정은 journal 조회만으로 하지 않고 완료된 GitHub Job, Worker 0, 해당 소켓 부재를 결합했다.

## 현행 복원과 최소 업무 관측

- R1: 이전 두 digest 각 Ready 3, Pod 6개. 입금 1회 HTTP 201, 탐지 false·평가 skip false·R01/R02/R04/R07 모두 false. 저장 성공/평가 계수 각각 +1, 저장 실패·missing IP·평가 오류 증가 0. [R1 결과](R1_MINIMUM_HTTP_METRICS.json).
- R2: 현행 API digest `338b8a28…`, engine digest `8b257adb…`, 각 Ready 3. 최초 이전 Pod 전체 부재 관측은 15:51:34.973 KST. 직접 업무 포트의 `/metrics`는 API 3개·engine 3개 모두 404, `/livez`·`/readyz`는 모두 200, 전용 metrics 6개 200 및 Prometheus up 6은 15:51:37.318까지 확인했다. [복원 HTTP 판정](RECOVERY_HTTP_CONFIRMED.json).
- R2 입금 1회도 HTTP 201·동일 정상 판정 및 저장/평가 각각 +1·오류 증가 0. 조회 전후 같은 Pod UID 집합, restart 0, Deployment UID와 비이미지 사양 불변을 확인했다. [R2 업무 결과](R2_MINIMUM_HTTP_METRICS.json), [안정 상태](R2_STABLE_FINAL.json).
- 추가 Edge 관측: 이전 버전 노출 전 `/metrics`와 `/metrics/` 모두 404. 이전 버전 동안 `/metrics` 404, `/metrics/` 307(Location `http://10.1.93.50/metrics`), redirect를 따라가지 않았다. 직접 업무 metrics 노출과 Edge 경로는 별도로 판정했다. 원본은 상위 `round4/edge-pre`, `round4/edge-during`에 있다.
- R1 거래 ID `22b7c46c-cd07-4539-a7fc-8890b67b12ee`, R2 `1827bd8a-a921-49f9-83f7-22529e903451`. **DB 동일 ID 행/내용은 미수집이며, HTTP 201·계수 증가를 DB 행 대조로 확대하지 않았다.** 재POST나 거래 삭제는 하지 않았다.

## 시간 판정

[수용된 방식](../round5/TIMING_CONTRACT.md)과 [계산 원본](TIMING_ASSESSMENT.json)을 적용했다.

- R1 첫 PATCH_PENDING 원mtime: 15:43:16.828114. 실제 PATCH 송신시각 자체는 NOT_MEASURED.
- R2 첫 APPLIED 원mtime 상한: 15:49:27.941749. 보정 전 차이 371.114초(6분 11초).
- 복원 조건 관측 상한: 15:51:37.318038. 보정 전 차이 500.490초(8분 20초).
- 이전 Pod의 정확 terminated 시각을 확보하지 못해 마지막 존재 관측부터 첫 전부 부재 관측까지의 구간으로 보존했다.
- 실제 회차 전·후 정상계정 6대의 시계 원본을 각각 1회 수집했다. 각 시점의 추정 오차는 약 0.0027–0.0721초이고 Leap Normal, boot 및 chrony 서비스 상태 등을 비교했다. 그러나 두 스냅샷만으로 회차 전체의 엄격한 오차 상한을 입증할 수 없어 `E_interval=UNPROVEN`을 유지했다.
- **TIMING_PROOF = 시한 미입증 / SEC 사후 검토.** 관측 벽시계상 15/30분 초과나 W+45 잔여 노출은 발견하지 않았다. 이 사실을 엄격한 시한 입증 또는 자동 사고 판정과 혼동하지 않는다.

## 정리와 보존

- [정확 경로 정리 영수증](EXACT_CLEANUP_RECEIPT.json): Runner 입력 2파일, control01 미사용 복구 공급 경로 1개(파일 3개), ansible01 이번 공급 경로 1개(파일 41개)를 로컬 원본·원 SHA 및 inode/소유권/모드와 대조한 뒤 정리했다. 다른 회차·공용 디렉터리·claim/checkpoint는 삭제하지 않았다.
- 원 서버의 claim/checkpoint, Workflow 결과, GitHub 로그 및 공개 소스만 들어 있는 native bootstrap 디렉터리는 증적으로 보존했다. 공급 제거를 증적 삭제로 확대하지 않았다.
- 토큰 2건은 메모리 참조 종료 영수증을 보존했다. 명시된 만료는 15:58:14 / 16:04:25 KST. 서버 강제 폐기와 만료 후 인증 실패 시험은 수행하지 않았다. 실제 창 반환은 별도 `WINDOW_RETURN.json`의 최종 조회·시각을 따른다.
- R1 시작 시 로컬 Windows의 `BINDING.json`/`binding.json` 충돌로 Token 발급 전 중단됐다. 덮인 바이트를 보존하고 정본에서 메타데이터를 복구했으며 기존 Job에 최초 broker 연결을 수행했다. 원격 plan/approval·생산 코드는 불변이고 추가 dispatch/Token은 없었다. 정리 준비에서도 보존 파일 경로 오참조를 로컬 검증이 차단했고 원격 변경 전에 수정했다.

## 남은 인수

1. SEC: 실제 시각 원본·보수적 구간 및 엄격 오차 미입증을 판정. 반복 Runtime 시험을 임의로 시작하지 않는다.
2. APP/DB 정상 담당 경로: 위 두 ID의 승인된 읽기 전용 DB 행 대조. 이번 창의 추가 인증·POST는 요청하지 않는다.
3. 중앙: 결과와 증적 리뷰 후 AC09 및 Phase 1 티켓 상태 결정, 다음 실행창 순서 배정. 본 실행 결과만으로 전체 AC 완료를 선언하지 않는다.
