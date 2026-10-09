# P1-DB-01 — W4 과거 로그 보존 여부 확인

CODEX_ASSISTED · 실행자 이권욱(GWONUK). **2026-10-09 01:58:39~01:58:53 KST**, 기존 SSH 경로의 `svc_ansible` → `sudo -n python3 -`로 Worker 3대를 순차 조회했다. 사용자가 확보한 00~09시 단독 창의 읽기 전용 증적 수집이다.

**판정: 조회한 CRI 로그에서는 W4 구간을 복원할 수 없다. HTTP 5xx 상태는 `NOT_MEASURED`로 유지한다.** 파일 0바이트는 5xx 0건, 서비스 무중단 또는 AC 충족의 증거가 아니다.

## 기준과 결과

기존 [증적 PR #172](https://github.com/321Team/fds-project-evidence/pull/172), 병합 `008eb7e48d52308375481c58a1e22ab38a6ddad9`의 `db-window-20261008T1930/README.md`가 미측정으로 남긴 **10/8 20:26:49~20:27:52 KST**를 대상으로 했다. 이는 비밀번호 적용에서 새 Pod rollout 완료까지의 구간이다. 기존 원본·판정은 수정하지 않는다.

| 대상 | 조회 시각 KST | 남아 있는 transaction-api Pod | CRI 파일 | 결과 |
|---|---|---|---|---|
| worker01 / 10.1.93.105 | 01:58:39 | `54984f6ddd-lrpp4` | `0.log` 1개 | 0바이트, rc0 |
| worker02 / 10.1.93.107 | 01:58:45 | `54984f6ddd-brmwj` | `0.log` 1개 | 0바이트, rc0 |
| worker03 / 10.1.93.108 | 01:58:53 | `54984f6ddd-h2tvv` | `0.log` 1개 | 0바이트, rc0 |

각 `/var/log/pods/fds-app_transaction-api-*` 아래 일반 파일을 확인했다. 세 파일은 읽기 전후 크기·mtime·ctime이 같고, 3/3 빈 파일의 SHA256은 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`다. 해당 경로에서 전환 전 `77bd7c6f64-*` Pod의 디렉터리는 발견되지 않았다. 다른 백업·중앙 로그까지 부재임을 뜻하지 않는다.

## 증적과 재현 범위

- `receipt/worker*/`: 각 실행에 실제 전송한 collector, stdout JSON 원본, stderr, SSH 명령·시각·종료 코드·collector/stdout 해시가 있는 invocation JSON. 수신본 바이트를 보존했다.
- `w4-log-availability.py`: 대상 호스트·root·작업창 검사, 일반 파일만 읽기, symlink 거부, 최대 파일 64개/파일당 8MiB/호스트당 32MiB/60초. gzip은 미열람으로 표시하며 잘린/변경 파일은 COMPLETE로 판정하지 않는다. payload는 출력하지 않고 CRI 시간대와 메타데이터만 남긴다.
- `run_readonly.py`: 기존 SSH 경유 경로·키 파일 참조 사용. 키 내용은 수집하지 않는다. 서버에 수집기 파일을 쓰지 않는다.
- `test_w4_log_availability.py`: 경계 시각 포함, 본문 미출력, 용량 상한, 압축 미열람, 시각 상한을 4개 로컬 fixture로 검증. Windows에서는 Linux 전용 open 플래그만 mock했다. 이는 Linux symlink 경쟁 방어의 시험 결과가 아니다. 서버 3회 실제 읽기와 구분한다.
- 로컬 fixture 실행: `python -I -X utf8 test_w4_log_availability.py` → 4 tests OK. 최초 Windows 실행은 Linux 전용 플래그 부재로 오류 3건이었고 fixture에 플랫폼 mock을 적용해 재실행했다. 실서버 collector의 플래그는 완화하지 않았다.
- 동일 실행의 재검산: invocation의 collector/stdout SHA256, 폴더 SHA256SUMS와 루트 레지스트리 연결을 확인한다. 나중에 재조회한 현재 로그로 과거 상태를 덮어쓰지 않는다.

## 남은 작업과 인수 경계

1. 기존에 승인된 정상 Edge 운영 계정 경로로 당시 Nginx access log·rotation/보존 기간 및 실제 log_format을 확인할 수 있다면, 위 구간의 **시간대·요청 경로·HTTP 상태 집계**를 추가 수집한다. 인증 우회·새 키 발급 없이 진행하며 URL query/body/Authorization는 반출하지 않는다. 현 세션은 Edge 로그를 확인하지 않았고 그 존재 여부는 미확인이다.
2. 중앙 로그 또는 같은 구간의 과거 HTTP 상태별 시계열이 있다면 보존 범위·scrape 공백·counter reset을 함께 확인한다. 자료가 없으면 역사적 W4 판정은 그대로 유지하고 담당자가 한계를 인수한다. 새 시험 결과로 과거 미측정을 PASS로 바꾸지 않는다.
3. 향후 별도 승인된 변경 창에서는 변경 전부터 연속 HTTP 관측을 준비한다. 이번 수집에서는 요청 전송, DB 접속/비밀번호 교체, rollout, 서비스 재시작, 정책 변경, Harbor 작업을 수행하지 않았다. 원복할 운영 변경은 없다.

[SEC의 DB 위험수용 종료 확인](https://github.com/321Team/fds-project-baseline/issues/11#issuecomment-6063472395)은 별도 결정이다. 이 수집은 그 결정을 번복하거나 N1 차단 귀속·W4 미측정·전체 AC를 완료 처리하지 않는다. 독립 리뷰는 작업창 종료 후 회수하며 리뷰/병합은 아직 미완료다.
