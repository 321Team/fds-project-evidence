# 이미지 전환 후 축약 부하 회귀 — RUN 202610141415

**판정: 승인된 §8 Runtime gate 자체 대조 PASS / 증적 독립 검토 대기.**
2026-10-14 14:16:12.031~14:22:12.036 KST에 기존 두 앱으로 1회 실행했다.
계획/실제 8,400건이 모두 HTTP 201이고, 사용자 DB 사후 8,400행 및 저장·평가 카운터 +8,400과 일치한다.
두 앱 Q3=0%, restart 변화 0·OOM 0, Resource 경보 산식이 현재 값 이내다.
이권욱 / CODEX_ASSISTED. 작성·실행자의 검증은 독립 리뷰가 아니며 APP/E2E 인수·Critical 0·Phase 1 Close는 미판정이다.

## 적용 기준과 실행 결속

- [APP 결정안 v2 §4/§6/§8](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5885861552), [G3 확인](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-5886568007).
- 생성기/실행 카드: [fds-msa PR33](https://github.com/321Team/fds-msa/pull/33), 독립 리뷰 이재환(`supreme33-kr`)의 [정확 HEAD 승인](https://github.com/321Team/fds-msa/pull/33#pullrequestreview-5512546052).
  HEAD `f9f981ba8f87aa6f876f5dc6da7e2f9f774d09ba`, merge `654d7762c3e6f4cc195c4628b42d0b47c3f8e17e`.
- [실행안](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6161231492)과 [사용자 확인](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6161260119): 14:15~14:25 실제 시작, 15:00 정리 종료 상한, 1회, 콘솔·db01 사전/사후·Harbor/H6/H3 및 APP/DB/MON/노드/다른 writer 비중첩.
- RUN 식별자 `202610141415`는 준비 때 고정한 prefix이며 실제 시작은 **14:16:12.031**이다. 시작창을 임의 연장하지 않았다.
- 앱 source `affbc69beef9967f7977d09a6fec14f7fb6c0e94`; 공급 경로 [TBS217](https://github.com/321Team/fds-project-evidence/pull/217) → [Push218](https://github.com/321Team/fds-project-evidence/pull/218) → [Deploy219](https://github.com/321Team/fds-project-evidence/pull/219) → [기능회귀224](https://github.com/321Team/fds-project-evidence/pull/224).
- 실제 API digest `338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0`, engine digest `8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d`.
- gen3 SHA256 `e5942646ba2544275b7664bbbc296d841920a0d1dac23421f96f1cc20e766b29`; q_range `5b59d0d5d8205154b350377599645734f801154f1532681453a8cf27b65cfd85`; promql `deccc54929862a137de59ae8f4d32b62b23a4461a2de77249381eb19863d91a1`.
- 각 3 Ready, Worker별 1/1/1. requests 250m/256Mi, limits 500m/512Mi를 유지했다.

## 실제 결과

| 항목 | 결과 | 근거 |
|---|---|---|
| 20 rps 기준 구간 | 14:16:12.031~14:18:12.031, 2,400건 / 201 2,400 | stages/requests 원본 |
| 50 rps 피크 구간 | 14:18:12.033~14:20:12.033, 6,000건 / 201 6,000 | stages/requests 원본 |
| 무부하 관찰 | 14:20:12.036~14:22:12.036, 120초 | IDLE END / DONE outstanding 0 |
| 생성기·오류 | rc0, timeout·연결 오류·201 외 0, 자동 재시도 0 | completion.json / requests.log |
| DB 사전 | 14:12:09.067179, fdsdb/postgres/Asia-Seoul, prefix 0행, rc0 | 사용자 콘솔 제출 |
| DB 사후 | 14:20:54.434941, 저장·고유계정·고유거래ID 모두 8,400; skipped/detected 각 0; rc0 | 사용자 콘솔 제출 |
| 유형 대조 | deposit 4,962 / transfer 1,693 / withdrawal 1,745, 생성기 로그와 동일 | requests.log ↔ DB 집계 |
| Metrics | save_success 23→8,423, evaluated 23→8,423, save_failure 0→0 | before/after MON 원본 |
| 관측·형상 | MON 23/23 up, 앱 6 targets, Pod UID/image/spec 유지, restart Δ0, OOM 0 | 사전/중간 8회/사후 |
| 정리 | 생성기 PID17794 reaped·14:22:41 부재; 이번 range PF 종료·listener 없음 | completion/progress-9/range receipt |

기존 engine Pod 1개 restartCount=1(앞선 Probe 이력), 나머지 0이며 이번 변화는 모두 0이다.
이번 DB 사후는 P 구간 drain 뒤, 무부하 관측 중 조회했다. 그 뒤 추가 전송이 없고 DONE/사후 metric도 같은 총수다.
HTTP 응답의 transaction_id를 부하 도구가 저장하지 않으므로 이 자료는 **집계 대조**다. PR224의 응답ID↔DB 1:1 대조와 구분한다.

### §8 gate와 Resource 경보선

| 워크로드 | CPU B/P 최대(m) | 메모리 최대(MiB) | Q3 B/P | CPU 경보 request/limit | 메모리 경보 request/limit |
|---|---:|---:|---:|---:|---:|
| transaction-api | 80.394 / 169.957 | 82.871 | 0% / 0% | 150m / 400m | 128Mi / 256Mi |
| fds-engine | 9.196 / 16.564 | 41.875 | 0% / 0% | 100m / 100m | 64Mi / 128Mi |

201 외 0, Q3<25%, restart Δ0/OOM0, 각 경보선 ≤ 현재 250m/500m·256Mi/512Mi이므로 §8 네 조건을 자체 대조 통과했다.
산식은 CPU B×1.5를 50m 올림(최소100m), CPU P×2를100m 올림, 전체 memory×1.2를64Mi 올림 및 그 두 배다.
**새 sizing·Resource 확정/축소는 수행하지 않았다. 2분 profile은 10분 메모리 추세를 증명하지 않는다.**

| 참고값(합격 SLO 아님) | B | P |
|---|---:|---:|
| 달성 요청 시작 rps / 98% 참고값 | 20.0 / 19.6 | 50.0 / 49.0 |
| p50 / p95 / p99 / max(ms) | 19.8 / 26.5 / 32.8 / 72.2 | 18.1 / 24.6 / 31.4 / 55.9 |
| 최대 1초 시작 건수 / 최대 시작 지연(ms) | 20 / 22.0 | 50 / 21.0 |

### 시계열 판정 범위

고정 Q1~Q3의 query_range 원본만 수치 판정에 사용했다. start=1791954912.031(B−60초), end=1791955332.036(idle end), step=15초.
쿼리마다 현재 Pod6·각29점(174점), 누락0·invalid0·NaN→0 치환0이다.
CPU/Q3는 [각 구간 시작+60,구간 끝], memory는 [B시작,idle끝]을 적용했다. Pod당 유효점은 B5/P4, memory25다.
P 시작이 B grid보다 0.002초 뒤여서 P의 경계점이 제외되는 것은 누락이 아니다. 워크로드별 Pod3 최대를 썼다.
중간 instant 조회는 감시·대응 목적이며 range 수치 판정을 대체하지 않는다.

## 원본·수신 검증·재현

- [판정 JSON](execution/phase1-short-load-window-20261014-1415/RUNTIME_ANALYSIS.json), [실행 종료 요약](execution/phase1-short-load-window-20261014-1415/RUNTIME_CLOSURE.json).
- [edge stages](execution/phase1-short-load-window-20261014-1415/edge-originals/results/stages.log), [요청 8,400행](execution/phase1-short-load-window-20261014-1415/edge-originals/results/requests.log), [완료 원본](execution/phase1-short-load-window-20261014-1415/edge-originals/results/completion.json).
- [Q1](execution/phase1-short-load-window-20261014-1415/control-originals/q1.json), [Q2](execution/phase1-short-load-window-20261014-1415/control-originals/q2.json), [Q3](execution/phase1-short-load-window-20261014-1415/control-originals/q3.json), [조회·정리 receipt](execution/phase1-short-load-window-20261014-1415/control-originals/range-receipt.json).
- [DB 사전 사용자 제출](execution/phase1-short-load-window-20261014-1415/db-before-user-transcript.txt), [DB 사후 사용자 제출](execution/phase1-short-load-window-20261014-1415/db-after-user-transcript.txt).
- `execution/phase1-short-load-window-20261014-1415/before-*`, `during1-*`~`during8-*`, `after-*`: 수집 코드·원본 stdout·stderr·SSH receipt·해시. SSH strict host-key 확인을 유지했다.
- edge01 svc_ansible(uid1003), control01 svc_ansible→sudo(uid0) 실행. 서버 원본 경로는 `/home/svc_ansible/p1-short-load-202610141415/` 및 `/var/tmp/p1-short-load-202610141415/`이며 소유 결과·수집기 경로만 사용했다.
- `edge-results/stdout.json`과 `control-range/stdout.json`은 서버 파일 byte/hash/base64 봉투다. 해제한 `*-originals`와 수신 후 SHA256을 대조했다. DB는 사용자 텍스트를 보존한 것으로 서버 .txt/.sha256 원본 Hash 검증을 주장하지 않는다.
- [SOURCE_INDEX.json](SOURCE_INDEX.json)은 로컬 수신 바이트→편입 파일 복사 대장이다. [SHA256SUMS](SHA256SUMS)는 이 회차 무결성만 나타내며 Runtime PASS·사람 승인과 구분한다.
- `CANDIDATE_BINDING`/`CONFIRMED_WINDOW`/`PREPARED_COMMANDS_MANIFEST` 및 preparation/stage 자료는 **실행 전 시점** 기록이다. 그 안의 NOT_RUN·load_runs0 등은 현행 상태가 아니며, 현행은 RUNTIME_ANALYSIS/CLOSURE를 따른다.
- 실제 gen3/q_range는 PR33 원본 그대로다. local wrapper·순수 조회/집계 수집기는 실행자 보조 도구이며 독립 리뷰된 앱 코드라고 표시하지 않는다. `during8` 허용은 같은 읽기 관측의 로컬 phase 이름 확장으로 Runtime 대상·명령·부하를 바꾸지 않았다. DB 유형/스킵 추가 대조는 로컬 분석 보강이다.
- 재계산은 별도 임시 복사본에서 `python -B execution/analyze_short_load_result_1415.py`로 가능하다. at_kst는 새로 계산되므로 수치/검사값을 비교한다. 실행·수집 스크립트는 과거 원본 보존용이며 새 승인 없이 다시 실행하지 않는다.

## 보존하는 한계·다음 단계

1. 준비 단계의 Kubernetes API service-proxy 8개 조회 timeout은 `preflight-api-proxy-timeout/`에 보존한다. 승인된 전용 PF의 사전·중간·사후·range는 성공했으며, 대체 경로 timeout을 MON 전체 장애 또는 이번 부하 실패로 확대하지 않는다.
2. 부하 경로는 edge01→Worker NodePort다. 새로운 Client→edge ingress POST 증명이 아니며, [evidence169](https://github.com/321Team/fds-project-evidence/pull/169)의10/8 경로 증거와 PR224 기능 증거를 별도 연결한다.
3. D-02 외부 MON/IF24, D-03 read timeout·engine error·DB save failure의 새 Runtime 공백, I01 INFO, W4 NOT_MEASURED 및 기존 접근통제 검증 한계를 이 실행으로 지우지 않는다. DB11 최종 인수는 기존 별도 결정이며 자동 재개하지 않는다.
4. 시험 8,400행과 원본을 보존했다. 삭제·Deploy·보안 변경·Harbor 변경·full profile·자동 재실행은 없었다. 이번 1회 허용은 소진됐다.
5. 독립 리뷰어가 원본·입력/판정·누락/한계·해시를 검토한 뒤 증적 편입을 판단한다. APP/E2E Lead가 남은 Defect와 전체 AC를 별도로 판정한다. 본 PR을 병합했다고 최종 인수·티켓 종결하지 않는다.

STATIC/자체 집계: 완료. RUNTIME: 위 범위 실제 완료. REVIEW: 독립 편입 검토 대기. MERGE/PUBLICATION/APP·E2E 최종 인수: 미수행.
