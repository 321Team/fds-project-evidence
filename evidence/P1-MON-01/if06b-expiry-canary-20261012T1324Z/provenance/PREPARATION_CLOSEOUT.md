# MON IF06B 준비 회차·사후 인증 재시도 결과

CODEX_ASSISTED · 정리 시각 2026-10-12T21:56:33.395310+09:00

**사후 조회 재시도 완료. 준비 검증은 통과했으나 canary와 자동 회수의 실제 시험은 미실행이다.**

| 항목 | 실제 확인 결과 |
|---|---|
| gateway 사후 조회 | 2026-10-12 21:50:45~48 KST, 22개 명령 rc0. 수집한 정책·zone·인터페이스·라우팅·IP forwarding 및 카운터를 제외한 nft 설정 전후 동일 |
| monitor 사후 조회 | 21:50:53~54 KST, 11개 명령 rc0. 수집한 주소·경로·listener·runtime/permanent zone 전후 동일 |
| monitor 상태 | heartbeat 약 6.895초, 활성 alert 0건 |
| control01 사후 확인 | 21:41경 수집한 HEP·host GNP·GNP 목록/spec 전후 동일. MON targets 23/23, remote-write 실패 증가 0 |
| 실행 준비 | 실제 validate·preflight 통과, SSH 종료 후 300초 생존 시험 60 BEAT와 FINAL 확인 |
| 실제 통신·자동 회수 | canary 생성 0회, 시험 요청 0회. 미검증 |
| 임시 권한·관측 정리 | Binding→Role→SA 생성 UID별 삭제 후 각각 NotFound. token 파일 제거. 캡처 5개(네 지점·worker 추가 1개) 모두 종료 rc0/drop0 |

## 중단 원인과 재시도 범위

인증과 준비 조회를 마치기 전에 시간 제한 캡처를 시작한 실행 순서 때문에 공통 관측 구간의 여유를 소진했다. 캡처를 연장하거나 기준을 낮추지 않고 canary를 시작하지 않았다. 이 시간 배분 문제는 Codex 실행 순서의 문제이며 사용자 암호 입력 오류와 구분한다.

최초 사후 수집은 300초 캡처 뒤 sudo 인증이 만료되어 실패했다. 첫 별도 사후 조회는 SSH rc255였고 사용자가 암호 오류였다고 확인했다. 두 번째 별도 사후 조회는 두 호스트 모두 정상 완료했다. 실패 원본과 성공 원본을 각각 보존했다. 사후 조회 재시도에서는 canary·RBAC·token을 만들지 않았다.

사후 설정은 캡처 종료 약 10분 뒤의 지연된 스냅샷이다. 전후 일치는 그 두 시점의 비교이며 사이 모든 순간의 무변경이나 시험 성공을 증명하지 않는다. 수동 재부팅·강제 종료 복구 시험과 AC 판정도 수행하지 않았다.

## 다음 실제 시험의 순서

1. Harbor의 실제 변경·사후 관측 종료를 확인한다. 21:51 공유 상태와 이번 조회의 세션 진행 내용은 Harbor 작업이 진행 중임을 나타낸다. 예상 경과시간으로 비중첩을 간주하지 않는다.
2. 이번 증적·실패 기록·생성 UID·해시를 보존한다. 실제 적용한 공급 코드·도구·RBAC·입력이 같고 환경이 유지되면 검증된 STATIC/MOCK/CI 및 survival 결과를 반복하지 않는다. 새 실행 입력의 변경 부분만 대조한다.
3. 실행 명령과 판정을 먼저 준비하고 gateway·monitor 인증, 콘솔 인수 대기, 현장 값과 기준선을 확인한다. 수명이 있는 token을 발급한 채 승인·입력 수집을 기다리지 않는다.
4. 권한·token 및 fresh preflight 준비가 완료된 뒤 네 지점 캡처를 맞춰 시작한다. 공통 유효 구간의 남은 시간이 고정 회차 예산을 충족해야 run을 시작한다. 부족하면 생성·시험 요청 0건으로 중단한다. 기존 회차를 덮어쓰거나 연장하지 않는다.
5. 기존 실행안의 ARMED→watch→CREATE OWNED UID/RV→시간 판정→443→재판정→8443→회수→post-deny 순서를 유지한다. 사후 읽기 전에 해당 터미널에서 sudo 인증을 다시 확인한다. 인증 정책·시간 제한을 완화하지 않는다.
6. 회수 NotFound·정책/관측 전후 대조·UID 기반 임시 권한 정리까지 실제 확인한 뒤 시험 결과를 판단한다.

새 Lead GO나 동일 범위 승인 재요청은 추가하지 않는다. 기존 사용자 허용의 canary 1회는 아직 사용하지 않았으며 Phase 2·영구 변경·티켓 종결을 포함하지 않는다. 이번 문서는 다음 회차가 이미 시작됐다는 기록이 아니다.

## 원본 연결

- `PREPARATION_CLOSEOUT.json`, `READINESS_STATUS.json`: 단계별 결과·해시·잔여 작업.
- `gateway-post2-receipt/`, `monitor-post2-receipt/`: 성공한 사후 수집 원본·해시·명령·종료 코드·시각.
- `gateway-field-receipt/`, `monitor-field-receipt/`: 캡처와 최초 sudo 실패 원본.
- `post-current-status.json`, `gateway-post-receipt/`, `monitor-post-receipt/`: 암호 오류로 끝난 첫 별도 조회 기록.
- `control01-credential-cleanup.json`: 임시 객체 3개 UID 조건부 정리와 token 제거.
- `control01-survival-final-2.json`, `control01-credential-preflight.json`: 실행 준비 검증.
